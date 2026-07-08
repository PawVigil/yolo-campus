"""报表服务 —— 参考 SDS 5.2.2 ReportService"""

import csv
import io
import json
from collections import Counter

from db import get_db
from models.response import ReportData, ReportMetric


class ReportService:
    """周报/月报生成 + 导出"""

    @staticmethod
    def generate_weekly(start: str, end: str) -> ReportData:
        """生成周报（start/end: YYYY-MM-DD）"""
        data = ReportService._aggregate(start, end)
        return ReportData(
            type="weekly",
            period={"start": start, "end": end},
            data=data,
        )

    @staticmethod
    def generate_monthly(year: int, month: int) -> ReportData:
        """生成月报"""
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{last_day:02d}"
        data = ReportService._aggregate(start, end)
        return ReportData(
            type="monthly",
            period={"year": year, "month": month},
            data=data,
        )

    @staticmethod
    def _aggregate(start: str, end: str) -> list[ReportMetric]:
        """日期范围内的统计数据"""
        conn = get_db()
        try:
            total = conn.execute(
                """SELECT COUNT(*) as c FROM detection
                   WHERE date(detect_time) BETWEEN ? AND ?""",
                (start, end),
            ).fetchone()["c"]

            with_animals = conn.execute(
                """SELECT COUNT(*) as c FROM detection
                   WHERE date(detect_time) BETWEEN ? AND ?
                     AND total_animals > 0""",
                (start, end),
            ).fetchone()["c"]

            locations_covered = conn.execute(
                """SELECT COUNT(DISTINCT location_id) as c FROM detection
                   WHERE date(detect_time) BETWEEN ? AND ?""",
                (start, end),
            ).fetchone()["c"]

            # 最常见品种
            rows = conn.execute(
                """SELECT result_json FROM detection
                   WHERE date(detect_time) BETWEEN ? AND ?
                     AND total_animals > 0""",
                (start, end),
            ).fetchall()
            breed_counter: Counter = Counter()
            for r in rows:
                try:
                    for a in json.loads(r["result_json"]):
                        breed_counter[a.get("breed_cn", "未知")] += 1
                except (json.JSONDecodeError, KeyError):
                    pass
            top_breed = breed_counter.most_common(1)
            top_breed_str = f"{top_breed[0][0]}({top_breed[0][1]}次)" if top_breed else "无"

            # 最活跃地点
            loc_rows = conn.execute(
                """SELECT l.name, COUNT(*) as cnt
                   FROM detection d
                   JOIN location l ON d.location_id = l.id
                   WHERE date(d.detect_time) BETWEEN ? AND ?
                   GROUP BY d.location_id ORDER BY cnt DESC LIMIT 1""",
                (start, end),
            ).fetchone()
            top_loc_str = f"{loc_rows['name']}({loc_rows['cnt']}次)" if loc_rows else "无"

            return [
                ReportMetric(metric="总检测数", value=total),
                ReportMetric(metric="有动物记录数", value=with_animals),
                ReportMetric(metric="覆盖地点数", value=locations_covered),
                ReportMetric(metric="最常见品种", value=top_breed_str),
                ReportMetric(metric="最活跃地点", value=top_loc_str),
            ]
        finally:
            conn.close()

    @staticmethod
    def export_csv(data: ReportData) -> str:
        """ReportData → CSV 字符串"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["指标", "数值"])
        for m in data.data:
            writer.writerow([m.metric, m.value])
        return output.getvalue()

    @staticmethod
    def export_json(data: ReportData) -> str:
        """ReportData → JSON 字符串"""
        return json.dumps(data.model_dump(), ensure_ascii=False, indent=2)
