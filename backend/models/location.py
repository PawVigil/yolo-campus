"""Location 实体模型 —— 参考 SDS 5.2.1"""

from datetime import datetime
from pydantic import BaseModel


class Location(BaseModel):
    """校园地点"""
    id: int
    name: str
    description: str | None = None
    safety_tip: str | None = None   # 当前生效安全提醒（冗余缓存）
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "safety_tip": self.safety_tip,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
