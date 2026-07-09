"""看板数据服务 —— 参考 SDS 5.2.2 DashboardService"""

import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

def _load_breed_info():
    """加载 breed_info.json"""
    path = Path(__file__).parent.parent / "breed_info.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def get_breed_count() -> dict[str, int]:
    """品种出现次数统计（供 dashboard 和 breed-stats 共用，仅统计 breed_info.json 中已知品种）"""
    breed_info = _load_breed_info()
    known_breeds = {v.get("name_cn", "") for v in breed_info.values()}
    from db import get_db
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT result_json FROM detection WHERE total_animals > 0"
        ).fetchall()
        counter: Counter = Counter()
        for r in rows:
            try:
                for a in json.loads(r["result_json"]):
                    cn = a.get("breed_cn", "")
                    if cn and cn in known_breeds:
                        counter[cn] += 1
            except (json.JSONDecodeError, KeyError):
                pass
        return dict(counter)
    finally:
        conn.close()

from db import get_db
from models.response import (
    AdminDashboard, BreedRank, LocationRank, LocationStatus,
    PublicDashboard, PublicStats, SafetyTipBrief, Stats, TrendPoint,
)


class DashboardService:
    """管理端 + 公共端看板数据聚合"""

    # ------------------------------------------------------------------
    # 管理端看板
    # ------------------------------------------------------------------

    @staticmethod
    def get_admin_dashboard() -> AdminDashboard:
        conn = get_db()
        try:
            # --- stats ---
            total = conn.execute("SELECT COUNT(*) as c FROM detection").fetchone()["c"]
            with_animals = conn.execute(
                "SELECT COUNT(*) as c FROM detection WHERE total_animals > 0"
            ).fetchone()["c"]
            locations_covered = conn.execute(
                "SELECT COUNT(DISTINCT location_id) as c FROM detection"
            ).fetchone()["c"]
            published_tips = conn.execute(
                "SELECT COUNT(*) as c FROM safety_tip WHERE status = 'published'"
            ).fetchone()["c"]

            stats = Stats(
                total_detections=total,
                with_animals=with_animals,
                locations_covered=locations_covered,
                published_tips=published_tips,
            )

            # --- location_ranking ---
            loc_rows = conn.execute(
                """SELECT l.name, COUNT(*) as cnt
                   FROM detection d
                   JOIN location l ON d.location_id = l.id
                   GROUP BY d.location_id
                   ORDER BY cnt DESC"""
            ).fetchall()
            location_ranking = [LocationRank(name=r["name"], count=r["cnt"]) for r in loc_rows]

            # --- breed_top5 ---
            det_rows = conn.execute(
                "SELECT result_json FROM detection WHERE total_animals > 0"
            ).fetchall()
            breed_counter: Counter = Counter()
            for r in det_rows:
                try:
                    animals = json.loads(r["result_json"])
                    for a in animals:
                        breed_counter[a.get("breed_cn", "未知")] += 1
                except (json.JSONDecodeError, KeyError):
                    pass
            breed_top5 = [
                BreedRank(breed=b, count=c)
                for b, c in breed_counter.most_common(5)
            ]

            # --- trend_14d ---
            trend_14d = DashboardService._trend_14d(conn)

            return AdminDashboard(
                stats=stats,
                location_ranking=location_ranking,
                breed_top5=breed_top5,
                trend_14d=trend_14d,
            )
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # 公共端看板
    # ------------------------------------------------------------------

    @staticmethod
    def get_public_dashboard() -> PublicDashboard:
        conn = get_db()
        try:
            # --- stats ---
            total = conn.execute("SELECT COUNT(*) as c FROM detection").fetchone()["c"]
            with_animals = conn.execute(
                "SELECT COUNT(*) as c FROM detection WHERE total_animals > 0"
            ).fetchone()["c"]
            locations_covered = conn.execute(
                "SELECT COUNT(DISTINCT location_id) as c FROM detection"
            ).fetchone()["c"]

            # 出现过的品种数（与 breed-stats 共用同一逻辑）
            breed_count = get_breed_count()
            breed_set = {b for b, c in breed_count.items() if c > 0}

            stats = PublicStats(
                total_detections=total,
                with_animals=with_animals,
                locations_covered=locations_covered,
                breed_count=len(breed_set),
            )

            # --- location_status ---
            now = datetime.now()
            locations = conn.execute("SELECT * FROM location ORDER BY id").fetchall()
            location_status: list[LocationStatus] = []

            for loc in locations:
                last_det = conn.execute(
                    """SELECT detect_time, result_json FROM detection
                       WHERE location_id = ? AND total_animals > 0
                       ORDER BY detect_time DESC LIMIT 1""",
                    (loc["id"],),
                ).fetchone()

                if last_det is None:
                    location_status.append(LocationStatus(
                        id=loc["id"], name=loc["name"], emoji="📍",
                        status="no_record", recent_breeds=[],
                        last_detect_time=None,
                    ))
                else:
                    try:
                        ts = last_det["detect_time"][:19]
                        # 兼容空格和 T 两种分隔符
                        last_time = datetime.strptime(ts.replace("T", " "), "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        last_time = now

                    hours_ago = (now - last_time).total_seconds() / 3600
                    if hours_ago <= 2:
                        status = "active"
                    elif hours_ago <= 24:
                        status = "resting"
                    else:
                        status = "no_record"

                    try:
                        animals = json.loads(last_det["result_json"])
                        recent = list(dict.fromkeys(
                            a.get("breed_cn", "") for a in animals
                        ))
                    except (json.JSONDecodeError, KeyError):
                        recent = []

                    location_status.append(LocationStatus(
                        id=loc["id"], name=loc["name"], emoji="📍",
                        status=status,
                        recent_breeds=recent,
                        last_detect_time=last_det["detect_time"],
                    ))

            # --- trend_14d ---
            trend_14d = DashboardService._trend_14d(conn)

            # --- safety_tips ---
            tip_rows = conn.execute(
                """SELECT st.content, l.name as location_name
                   FROM safety_tip st
                   JOIN location l ON st.location_id = l.id
                   WHERE st.status = 'published'
                   ORDER BY st.published_at DESC"""
            ).fetchall()
            safety_tips = [
                SafetyTipBrief(location_name=r["location_name"], content=r["content"])
                for r in tip_rows
            ]

            return PublicDashboard(
                stats=stats,
                location_status=location_status,
                trend_14d=trend_14d,
                safety_tips=safety_tips,
            )
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _trend_14d(conn) -> list[TrendPoint]:
        """近14天每日检测量"""
        today = datetime.now().date()
        days = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]

        rows = conn.execute(
            """SELECT date(detect_time) as day, COUNT(*) as cnt
               FROM detection
               WHERE date(detect_time) >= ?
               GROUP BY date(detect_time)""",
            (days[0],),
        ).fetchall()
        day_count = {r["day"]: r["cnt"] for r in rows}

        return [TrendPoint(day=d, count=day_count.get(d, 0)) for d in days]
