"""社区分享服务 —— 参考 SDS 5.2.2 CommunityService"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from config import COMMUNITY_DIR
from db import get_db
from models.community_share import CommunityShare
from models.response import CommunityShareResponse, PaginatedResult
from yolo_engine import engine

# 品种知识库缓存
_breed_info: dict | None = None


def _load_breed_info() -> dict:
    global _breed_info
    if _breed_info is None:
        from config import BREED_INFO_PATH
        if BREED_INFO_PATH.exists():
            _breed_info = json.loads(BREED_INFO_PATH.read_text(encoding="utf-8"))
        else:
            _breed_info = {}
    return _breed_info


def _parse_comments(comments_json: str | None) -> list[dict]:
    """解析评论JSON字符串，容错处理"""
    if not comments_json:
        return []
    try:
        return json.loads(comments_json)
    except (json.JSONDecodeError, TypeError):
        return []


def _build_response(row) -> CommunityShareResponse:
    """根据数据库行构建CommunityShareResponse（兼容dict和sqlite3.Row）"""
    # 统一转为dict
    d = dict(row) if not isinstance(row, dict) else row
    bi = _load_breed_info().get(d.get("breed") or "", None)
    # 处理路径：将绝对路径转为相对URL
    raw_path = d['image_path']
    if 'uploads' in raw_path:
        img_url = "/" + raw_path.split("uploads", 1)[1].replace("\\", "/")
        img_url = img_url.lstrip("/")  # 确保不会出现 //
        img_url = "/uploads/" + img_url
    else:
        img_url = f"/{raw_path}"
    comments = _parse_comments(d.get("comments_json"))
    return CommunityShareResponse(
        id=d["id"],
        location_id=d.get("location_id"),
        location_name=d.get("location_name"),
        image_url=img_url,
        images=[img_url],
        comments=comments,
        description=d.get("description"),
        nickname=d.get("nickname"),
        breed=d.get("breed"),
        breed_info=bi,
        created_at=d["created_at"],
    )


class CommunityService:
    """社区分享业务逻辑"""

    @staticmethod
    def save_upload_file(file_data: bytes, filename: str) -> str:
        """保存社区分享图片到 uploads/community/"""
        ext = Path(filename).suffix.lower()
        save_name = f"{uuid.uuid4().hex}{ext}"
        save_path = COMMUNITY_DIR / save_name
        COMMUNITY_DIR.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(file_data)
        return str(save_path)

    @staticmethod
    def create(
        image_path: str,
        location_id: int | None = None,
        description: str | None = None,
        nickname: str | None = None,
        auto_detect: bool = False,
    ) -> CommunityShare:
        """创建社区分享记录"""
        breed: str | None = None
        if auto_detect:
            try:
                animals = engine.detect(image_path)
                if animals:
                    breed = animals[0].breed_cn  # 取置信度最高的
            except Exception:
                pass  # YOLO 识别失败不影响上传

        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO community_share
                   (location_id, image_path, description, nickname, breed)
                   VALUES (?, ?, ?, ?, ?)""",
                (location_id, image_path, description, nickname, breed),
            )
            conn.commit()

            row = conn.execute(
                "SELECT * FROM community_share WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return CommunityShare(
                id=row["id"], location_id=row["location_id"],
                image_path=row["image_path"], description=row["description"],
                nickname=row["nickname"], breed=row["breed"],
                created_at=row["created_at"],
            )
        finally:
            conn.close()

    @staticmethod
    def get_list(page: int = 1, page_size: int = 15) -> PaginatedResult:
        """分页查询社区分享列表"""
        conn = get_db()
        try:
            total = conn.execute(
                "SELECT COUNT(*) as c FROM community_share"
            ).fetchone()["c"]

            page = max(1, page)
            page_size = min(max(1, page_size), 50)
            offset = (page - 1) * page_size

            rows = conn.execute(
                """SELECT cs.*, l.name as location_name
                   FROM community_share cs
                   LEFT JOIN location l ON cs.location_id = l.id
                   ORDER BY cs.created_at DESC
                   LIMIT ? OFFSET ?""",
                (page_size, offset),
            ).fetchall()

            items: list[CommunityShareResponse] = []
            for r in rows:
                items.append(_build_response(r))

            return PaginatedResult(
                items=items, total=total, page=page, page_size=page_size,
            )
        finally:
            conn.close()

    @staticmethod
    def get_by_id(share_id: int) -> CommunityShareResponse | None:
        """单条查询"""
        conn = get_db()
        try:
            row = conn.execute(
                """SELECT cs.*, l.name as location_name
                   FROM community_share cs
                   LEFT JOIN location l ON cs.location_id = l.id
                   WHERE cs.id = ?""",
                (share_id,),
            ).fetchone()
            if row is None:
                return None
            return _build_response(row)
        finally:
            conn.close()

    @staticmethod
    def add_comment(share_id: int, nickname: str, text: str) -> list[dict] | None:
        """添加评论到社区分享（方案A：存JSON字段）"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT comments_json FROM community_share WHERE id = ?",
                (share_id,),
            ).fetchone()
            if row is None:
                return None

            comments = _parse_comments(row["comments_json"])
            comment = {
                "id": len(comments) + 1,
                "nickname": nickname or "匿名",
                "text": text.strip(),
                "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            }
            comments.append(comment)
            conn.execute(
                "UPDATE community_share SET comments_json = ? WHERE id = ?",
                (json.dumps(comments, ensure_ascii=False), share_id),
            )
            conn.commit()
            return comments
        finally:
            conn.close()
