"""分享卡片服务 —— 参考 SDS 5.2.2 ShareCardService"""

import json
from pathlib import Path

from db import get_db


class ShareCardService:
    """生成分享卡片 HTML"""

    _template: str | None = None

    @classmethod
    def _load_template(cls) -> str:
        if cls._template is None:
            tmpl_path = Path(__file__).resolve().parent.parent / "templates" / "share_card.html"
            if tmpl_path.exists():
                cls._template = tmpl_path.read_text(encoding="utf-8")
            else:
                cls._template = cls._default_template()
        return cls._template

    @staticmethod
    def _default_template() -> str:
        return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PawVigil 动物分享卡片</title>
<style>
  body {
    margin: 0; padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh; display: flex; justify-content: center; align-items: center;
  }
  .card {
    background: #fff; border-radius: 16px; padding: 24px;
    max-width: 400px; width: 100%; box-shadow: 0 12px 40px rgba(0,0,0,.2);
    text-align: center;
  }
  .card h2 { margin: 0 0 4px; color: #333; }
  .card .time { color: #999; font-size: 13px; margin-bottom: 12px; }
  .card .breed {
    display: inline-block; background: #f0f0ff; color: #667eea;
    padding: 6px 14px; border-radius: 20px; margin: 4px;
    font-size: 15px; font-weight: 600;
  }
  .card .location { color: #666; margin: 12px 0 4px; font-size: 14px; }
  .card .footer {
    margin-top: 16px; padding-top: 12px; border-top: 1px solid #eee;
    color: #bbb; font-size: 12px;
  }
</style>
</head>
<body>
<div class="card">
  <h2>🐾 发现动物！</h2>
  <p class="time">{{detect_time}}</p>
  <div>{{breeds}}</div>
  <p class="location">📍 {{location_name}}</p>
  <p class="footer">PawVigil · 校园流浪动物观测关爱系统</p>
</div>
</body>
</html>"""

    @classmethod
    def generate(cls, detection_id: int) -> str:
        """根据检测记录生成分享卡片 HTML"""
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
                raise ValueError(f"检测记录不存在: {detection_id}")

            animals = json.loads(row["result_json"])
            breeds_html = "".join(
                f'<span class="breed">{a.get("breed_cn", "未知")}</span>'
                for a in animals
            )

            template = cls._load_template()
            html = template \
                .replace("{{detect_time}}", row["detect_time"]) \
                .replace("{{breeds}}", breeds_html or '<span class="breed">未识别</span>') \
                .replace("{{location_name}}", row["location_name"])

            return html
        finally:
            conn.close()
