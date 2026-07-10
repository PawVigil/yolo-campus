"""检测记录服务 —— 参考 SDS 5.2.2 DetectionService"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, UPLOAD_DIR
from db import get_db
from models.detection import AnimalResult, Detection
from models.request import DetectionFilter
from models.response import PaginatedResult
from yolo_engine import engine


class DetectionService:
    """检测记录业务逻辑"""

    # ------------------------------------------------------------------
    # SDS: upload(file, location_id, user_id) → Detection
    # 完整流程：校验文件 + 保存图片 + YOLO检测 + 标注 + 存库
    # ------------------------------------------------------------------

    @staticmethod
    def validate_file(filename: str, file_size: int) -> None:
        """校验文件类型和大小，不通过抛 ValueError"""
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError("仅支持 JPG/PNG 格式")
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(f"文件大小超过 {MAX_FILE_SIZE_BYTES // 1024 // 1024}MB 限制")

    @staticmethod
    def save_upload_file(file_data: bytes, filename: str) -> str:
        """保存上传文件到 uploads/，返回相对路径"""
        ext = Path(filename).suffix.lower()
        save_name = f"{uuid.uuid4().hex}{ext}"
        save_path = UPLOAD_DIR / save_name
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(file_data)
        return str(save_path)

    @staticmethod
    def detect(image_path: str) -> list[AnimalResult]:
        """仅调用 YOLO，不存库"""
        return engine.detect(image_path)

    @staticmethod
    def annotate(image_path: str, animals: list[AnimalResult]) -> str:
        """在图片上画框+标签，返回标注图路径"""
        return engine.annotate(image_path, animals)

    @staticmethod
    def save(
        location_id: int,
        user_id: int,
        image_path: str,
        detect_time: str,
        animals: list[AnimalResult],
        annotated_path: str = "",
    ) -> Detection:
        """仅存库，不调 YOLO"""
        result_json = json.dumps(
            [a.to_dict() for a in animals], ensure_ascii=False
        )
        total = len(animals)

        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO detection (location_id, user_id, image_path,
                   detect_time, result_json, total_animals, annotated_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (location_id, user_id, image_path, detect_time,
                 result_json, total, annotated_path),
            )
            conn.commit()
            det_id = cursor.lastrowid

            row = conn.execute(
                "SELECT * FROM detection WHERE id = ?", (det_id,)
            ).fetchone()
            return Detection(
                id=row["id"],
                location_id=row["location_id"],
                user_id=row["user_id"],
                image_path=row["image_path"],
                detect_time=row["detect_time"],
                result_json=row["result_json"],
                total_animals=row["total_animals"],
                created_at=row["created_at"],
            )
        finally:
            conn.close()

    @staticmethod
    def get_list(filters: DetectionFilter) -> PaginatedResult:
        """分页+筛选查询"""
        conn = get_db()
        try:
            where_clauses: list[str] = []
            params: list = []

            if filters.location_id:
                where_clauses.append("d.location_id = ?")
                params.append(filters.location_id)
            if filters.date_from:
                where_clauses.append("d.detect_time >= ?")
                params.append(filters.date_from)
            if filters.date_to:
                where_clauses.append("d.detect_time <= ?")
                params.append(filters.date_to + " 23:59:59")
            if filters.breed:
                where_clauses.append("d.result_json LIKE ?")
                params.append(f"%{filters.breed}%")

            where_sql = (" AND ".join(where_clauses)) if where_clauses else "1=1"

            # 总数
            count_row = conn.execute(
                f"SELECT COUNT(*) as cnt FROM detection d WHERE {where_sql}",
                params,
            ).fetchone()
            total = count_row["cnt"]

            # 分页
            page = max(1, filters.page)
            page_size = min(max(1, filters.page_size), 50)
            offset = (page - 1) * page_size

            sql = f"""SELECT d.*, l.name as location_name
                    FROM detection d
                    JOIN location l ON d.location_id = l.id
                    WHERE {where_sql}
                    ORDER BY d.detect_time DESC
                    LIMIT ? OFFSET ?"""
            print(f'[DEBUG] page={page} offset={offset} sql={sql} params={params + [page_size, offset]}')
            rows = conn.execute(sql, params + [page_size, offset]).fetchall()

            items = []
            for r in rows:
                det = Detection(
                    id=r["id"], location_id=r["location_id"], user_id=r["user_id"],
                    image_path=r["image_path"], detect_time=r["detect_time"],
                    result_json=r["result_json"], total_animals=r["total_animals"],
                    created_at=r["created_at"],
                )
                animals = det.get_animals()
                breeds = list(dict.fromkeys(a.breed_cn for a in animals))  # 去重保序
                items.append({
                    "id": det.id,
                    "location_name": r["location_name"],
                    "image_url": f"/{det.image_path}",
                    "detect_time": det.detect_time,
                    "total_animals": det.total_animals,
                    "breed_summary": ", ".join(breeds) if breeds else "未识别",
                })

            return PaginatedResult(items=items, total=total, page=page, page_size=page_size)
        finally:
            conn.close()

    @staticmethod
    def get_by_id(detection_id: int) -> Detection | None:
        """单条查询（含 JOIN location）"""
        conn = get_db()
        try:
            row = conn.execute(
                """SELECT d.*, l.name as location_name
                   FROM detection d
                   JOIN location l ON d.location_id = l.id
                   WHERE d.id = ?""",
                (detection_id,),
            ).fetchone()
            if row is None:
                return None
            return Detection(
                id=row["id"], location_id=row["location_id"], user_id=row["user_id"],
                image_path=row["image_path"], detect_time=row["detect_time"],
                result_json=row["result_json"], total_animals=row["total_animals"],
                created_at=row["created_at"],
            ), row["location_name"], row["annotated_path"] if "annotated_path" in row.keys() else ""
        finally:
            conn.close()

    @staticmethod
    def delete(detection_id: int) -> bool:
        """删除数据库记录 + 删除图片文件"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT image_path FROM detection WHERE id = ?", (detection_id,)
            ).fetchone()
            if row is None:
                return False

            # 删除原始图片
            image_path = Path(row["image_path"])
            if image_path.exists():
                image_path.unlink()
            # 删除标注图（命名规则：annotated_{原始文件名stem}.jpg）
            from config import ANNOTATED_DIR
            annotated_name = f"annotated_{image_path.stem}.jpg"
            annotated_path = ANNOTATED_DIR / annotated_name
            if annotated_path.exists():
                annotated_path.unlink()

            conn.execute("DELETE FROM detection WHERE id = ?", (detection_id,))
            conn.commit()
            return True
        finally:
            conn.close()
