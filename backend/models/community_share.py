"""CommunityShare 实体模型 —— 参考 SDS 5.2.1"""

from datetime import datetime
from pydantic import BaseModel


class CommunityShare(BaseModel):
    """社区分享（独立于 detection 数据线）"""
    id: int
    location_id: int | None = None   # 可选
    image_path: str
    description: str | None = None
    nickname: str | None = None
    breed: str | None = None         # YOLO 识别品种名（可选）
    created_at: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "location_id": self.location_id,
            "image_path": self.image_path,
            "description": self.description,
            "nickname": self.nickname,
            "breed": self.breed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
