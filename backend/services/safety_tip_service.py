"""安全提醒服务 —— 参考 SDS 5.2.2 SafetyTipService"""

from datetime import datetime

from db import get_db
from models.response import Suggestion


class SafetyTipService:
    """安全提醒 CRUD + 发布/下架 + 自动建议"""

    @staticmethod
    def get_all() -> list[dict]:
        """返回全部提醒（含 location_name），所有状态"""
        conn = get_db()
        try:
            rows = conn.execute(
                """SELECT st.*, l.name as location_name
                   FROM safety_tip st
                   JOIN location l ON st.location_id = l.id
                   ORDER BY st.created_at DESC"""
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def get_published() -> list[dict]:
        """仅返回已发布的提醒"""
        conn = get_db()
        try:
            rows = conn.execute(
                """SELECT st.*, l.name as location_name
                   FROM safety_tip st
                   JOIN location l ON st.location_id = l.id
                   WHERE st.status = 'published'
                   ORDER BY st.published_at DESC"""
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    @staticmethod
    def create(location_id: int, title: str, content: str, status: str = "draft") -> dict:
        conn = get_db()
        try:
            cursor = conn.execute(
                """INSERT INTO safety_tip (location_id, title, content, status)
                   VALUES (?, ?, ?, ?)""",
                (location_id, title, content, status),
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)
        finally:
            conn.close()

    @staticmethod
    def update(tip_id: int, title: str | None, content: str | None, status: str | None = None, location_id: int | None = None) -> dict | None:
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            if row is None:
                return None

            new_title = title if title is not None else row["title"]
            new_content = content if content is not None else row["content"]
            new_status = status if status is not None else row["status"]
            new_location_id = location_id if location_id is not None else row["location_id"]

            conn.execute(
                "UPDATE safety_tip SET title = ?, content = ?, status = ?, location_id = ? WHERE id = ?",
                (new_title, new_content, new_status, new_location_id, tip_id),
            )
            conn.commit()

            updated = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            return dict(updated)
        finally:
            conn.close()

    @staticmethod
    def delete(tip_id: int) -> bool:
        conn = get_db()
        try:
            row = conn.execute("SELECT id FROM safety_tip WHERE id = ?", (tip_id,)).fetchone()
            if row is None:
                return False
            conn.execute("DELETE FROM safety_tip WHERE id = ?", (tip_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    @staticmethod
    def publish(tip_id: int) -> dict | None:
        """发布提醒：更新 status + published_at + 同步 location.safety_tip"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            if row is None:
                return None

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                """UPDATE safety_tip
                   SET status = 'published', published_at = ?
                   WHERE id = ?""",
                (now, tip_id),
            )
            # 同步冗余缓存到 location
            conn.execute(
                "UPDATE location SET safety_tip = ? WHERE id = ?",
                (row["content"], row["location_id"]),
            )
            conn.commit()

            updated = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            return dict(updated)
        finally:
            conn.close()

    @staticmethod
    def archive(tip_id: int) -> dict | None:
        """下架提醒：更新 status + 清 location.safety_tip"""
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            if row is None:
                return None

            conn.execute(
                "UPDATE safety_tip SET status = 'archived' WHERE id = ?",
                (tip_id,),
            )
            # 清除 location 冗余缓存
            conn.execute(
                "UPDATE location SET safety_tip = NULL WHERE id = ?",
                (row["location_id"],),
            )
            conn.commit()

            updated = conn.execute(
                "SELECT * FROM safety_tip WHERE id = ?", (tip_id,)
            ).fetchone()
            return dict(updated)
        finally:
            conn.close()

    @staticmethod
    def auto_generate() -> list[Suggestion]:
        """基于近7天各地点检测量生成建议（仅返回 count ≥ 5 的）"""
        conn = get_db()
        try:
            rows = conn.execute(
                """SELECT d.location_id, l.name as location_name,
                          COUNT(*) as cnt
                   FROM detection d
                   JOIN location l ON d.location_id = l.id
                   WHERE d.detect_time >= datetime('now', '-7 days', 'localtime')
                     AND d.total_animals > 0
                   GROUP BY d.location_id
                   HAVING cnt >= 5
                   ORDER BY cnt DESC"""
            ).fetchall()

            suggestions: list[Suggestion] = []
            for r in rows:
                suggestions.append(Suggestion(
                    location_id=r["location_id"],
                    location_name=r["location_name"],
                    count=r["cnt"],
                    suggestion_text=(
                        f"「{r['location_name']}」近7天检测到{r['cnt']}次动物出没，"
                        f"建议发布安全提醒"
                    ),
                    data_basis=f"近7天检测{r['cnt']}次",
                ))
            return suggestions
        finally:
            conn.close()
