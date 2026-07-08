"""SafetyTip 实体模型 —— 参考 SDS 5.2.1"""

from datetime import datetime
from pydantic import BaseModel


class SafetyTip(BaseModel):
    """安全提醒"""
    id: int
    location_id: int
    title: str
    content: str
    status: str = "draft"          # "draft" | "published" | "archived"
    created_at: datetime | None = None
    published_at: datetime | None = None

    def is_published(self) -> bool:
        return self.status == "published"

    def to_dict(self, location_name: str | None = None) -> dict:
        d = {
            "id": self.id,
            "location_id": self.location_id,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
        if location_name:
            d["location_name"] = location_name
        return d
