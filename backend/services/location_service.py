"""地点管理服务 —— 参考 SDS 5.2.2 LocationService"""

from db import get_db
from models.location import Location
from models.request import LocationUpdate


class LocationService:
    """地点 CRUD"""

    @staticmethod
    def get_all() -> list[Location]:
        conn = get_db()
        try:
            rows = conn.execute("SELECT * FROM location ORDER BY id").fetchall()
            return [
                Location(
                    id=r["id"], name=r["name"], description=r["description"],
                    safety_tip=r["safety_tip"], created_at=r["created_at"],
                )
                for r in rows
            ]
        finally:
            conn.close()

    @staticmethod
    def get_by_id(location_id: int) -> Location | None:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM location WHERE id = ?", (location_id,)
            ).fetchone()
            if row is None:
                return None
            return Location(
                id=row["id"], name=row["name"], description=row["description"],
                safety_tip=row["safety_tip"], created_at=row["created_at"],
            )
        finally:
            conn.close()

    @staticmethod
    def create(name: str, description: str | None = None) -> Location:
        conn = get_db()
        try:
            # 检查重名
            exist = conn.execute(
                "SELECT id FROM location WHERE name = ?", (name,)
            ).fetchone()
            if exist:
                raise ValueError("地点名称已存在")

            cursor = conn.execute(
                "INSERT INTO location (name, description) VALUES (?, ?)",
                (name, description),
            )
            conn.commit()
            return Location(
                id=cursor.lastrowid, name=name, description=description,
                safety_tip=None, created_at=None,
            )
        finally:
            conn.close()

    @staticmethod
    def update(location_id: int, data: LocationUpdate) -> Location | None:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM location WHERE id = ?", (location_id,)
            ).fetchone()
            if row is None:
                return None

            new_name = data.name if data.name is not None else row["name"]
            new_desc = data.description if data.description is not None else row["description"]

            conn.execute(
                "UPDATE location SET name = ?, description = ? WHERE id = ?",
                (new_name, new_desc, location_id),
            )
            conn.commit()
            return Location(
                id=location_id, name=new_name, description=new_desc,
                safety_tip=row["safety_tip"], created_at=row["created_at"],
            )
        finally:
            conn.close()

    @staticmethod
    def delete(location_id: int) -> bool:
        """删除地点。有关联检测记录时返回 False（外层抛 409）"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id FROM location WHERE id = ?", (location_id,)
            ).fetchone()
            if row is None:
                return False

            # 检查是否有关联检测记录
            ref = conn.execute(
                "SELECT COUNT(*) as cnt FROM detection WHERE location_id = ?",
                (location_id,),
            ).fetchone()
            if ref["cnt"] > 0:
                raise RuntimeError("该地点有关联的检测记录，无法删除")

            conn.execute("DELETE FROM location WHERE id = ?", (location_id,))
            conn.commit()
            return True
        finally:
            conn.close()
