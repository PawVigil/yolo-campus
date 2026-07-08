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
    # 处理路径：兼容旧格式（单路径）和新格式（JSON数组）
    raw_path = d['image_path']
    paths: list[str] = []
    try:
        parsed = json.loads(raw_path)
        if isinstance(parsed, list):
            paths = parsed
        else:
            paths = [str(parsed)]
    except (json.JSONDecodeError, TypeError):
        paths = [raw_path]

    def _path_to_url(p: str) -> str:
        if 'uploads' in p:
            u = "/" + p.split("uploads", 1)[1].replace("\\", "/")
            u = u.lstrip("/")
            return "/uploads/" + u
        return f"/{p}"

    img_urls = [_path_to_url(p) for p in paths]
    comments = _parse_comments(d.get("comments_json"))
    return CommunityShareResponse(
        id=d["id"],
        location_id=d.get("location_id"),
        location_name=d.get("location_name"),
        image_url=img_urls[0],
        images=img_urls,
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
        image_paths: list[str],
        location_id: int | None = None,
        description: str | None = None,
        nickname: str | None = None,
        auto_detect: bool = False,
    ) -> CommunityShare:
        """创建社区分享记录（支持多图）"""
        breed: str | None = None
        if auto_detect:
            try:
                # 用第一张图做品种识别
                animals = engine.detect(image_paths[0])
                if animals:
                    breed = animals[0].breed_cn
            except Exception:
                pass

        # 将路径列表存为JSON数组
        paths_json = json.dumps(image_paths, ensure_ascii=False)

        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO community_share
                   (location_id, image_path, description, nickname, breed)
                   VALUES (?, ?, ?, ?, ?)""",
                (location_id, paths_json, description, nickname, breed),
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
    def create_from_detection(
        image_url: str,
        location_id: int | None = None,
        description: str | None = None,
        nickname: str | None = None,
        auto_detect: bool = False,
    ) -> CommunityShare:
        """从检测记录分享到社区（使用已有图片URL）"""
        from config import UPLOAD_DIR

        # 将 URL 转为本地路径: /uploads/xxx.jpg → d:\train2\backend\uploads\xxx.jpg
        clean = image_url.lstrip("/")
        if "uploads/" in clean:
            # 提取 uploads 之后的路径，拼接 UPLOAD_DIR 的父目录
            idx = clean.index("uploads/")
            local = str(UPLOAD_DIR.parent) + "\\" + clean[idx:].replace("/", "\\")
        else:
            local = str(UPLOAD_DIR) + "\\" + Path(clean).name

        # 用本地路径列表创建，走 create 的逻辑（YOLO检测也在里面）
        return CommunityService.create(
            image_paths=[str(local)],
            location_id=location_id,
            description=description,
            nickname=nickname,
            auto_detect=auto_detect,
        )

    @staticmethod
    def get_list(page: int = 1, page_size: int = 15, date: str | None = None) -> PaginatedResult:
        """分页查询社区分享列表（支持按日期筛选）"""
        conn = get_db()
        try:
            where_clause = "1=1"
            params: list = []

            if date:
                where_clause = "date(cs.created_at) = ?"
                params.append(date)

            total = conn.execute(
                f"SELECT COUNT(*) as c FROM community_share cs WHERE {where_clause}",
                params,
            ).fetchone()["c"]

            page = max(1, page)
            page_size = min(max(1, page_size), 50)
            offset = (page - 1) * page_size

            rows = conn.execute(
                f"""SELECT cs.*, l.name as location_name
                   FROM community_share cs
                   LEFT JOIN location l ON cs.location_id = l.id
                   WHERE {where_clause}
                   ORDER BY cs.created_at DESC
                   LIMIT ? OFFSET ?""",
                params + [page_size, offset],
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

    @staticmethod
    def delete(share_id: int) -> bool:
        """删除社区分享（含图片文件清理）"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT image_path FROM community_share WHERE id = ?", (share_id,)
            ).fetchone()
            if row is None:
                return False

            # 删除图片文件
            import json as _json
            try:
                paths = _json.loads(row["image_path"])
                if not isinstance(paths, list):
                    paths = [str(paths)]
            except (_json.JSONDecodeError, TypeError):
                paths = [row["image_path"]]
            for p in paths:
                try:
                    # 将 URL 转为本地路径
                    local = Path(p.replace("/uploads/", str(COMMUNITY_DIR.parent) + "/"))
                    if local.exists():
                        local.unlink()
                except Exception:
                    pass

            conn.execute("DELETE FROM community_share WHERE id = ?", (share_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def delete_comment(share_id: int, comment_id: int) -> list[dict] | None:
        """删除社区分享的某条评论"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT comments_json FROM community_share WHERE id = ?", (share_id,)
            ).fetchone()
            if row is None:
                return None
            comments = _parse_comments(row["comments_json"])
            comments = [c for c in comments if c.get("id") != comment_id]
            conn.execute(
                "UPDATE community_share SET comments_json = ? WHERE id = ?",
                (json.dumps(comments, ensure_ascii=False), share_id),
            )
            conn.commit()
            return comments
        finally:
            conn.close()
