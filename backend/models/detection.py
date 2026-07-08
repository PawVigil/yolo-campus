"""Detection / AnimalResult / Box 模型 —— 参考 SDS  5.2.1"""

import json
from datetime import datetime
from pydantic import BaseModel


class Box(BaseModel):
    """边界框坐标（值对象）"""
    x1: float
    y1: float
    x2: float
    y2: float

    def to_dict(self) -> dict:
        return self.model_dump()


class AnimalResult(BaseModel):
    """YOLO 检测结果中的单只动物（值对象，不独立存表）"""
    breed_en: str
    breed_cn: str
    confidence: float
    box: Box

    def to_dict(self) -> dict:
        return {
            "breed_en": self.breed_en,
            "breed_cn": self.breed_cn,
            "confidence": self.confidence,
            "box": self.box.to_dict(),
        }


class Detection(BaseModel):
    """检测记录"""
    id: int
    location_id: int
    user_id: int
    image_path: str
    detect_time: str              # ISO 8601
    result_json: str              # JSON 字符串，内含 [{breed, confidence, box}]
    total_animals: int = 0
    created_at: datetime | None = None

    def get_animals(self) -> list[AnimalResult]:
        """解析 result_json → AnimalResult 列表"""
        raw_list = json.loads(self.result_json)
        return [
            AnimalResult(
                breed_en=item["breed_en"],
                breed_cn=item["breed_cn"],
                confidence=item["confidence"],
                box=Box(**item["box"]),
            )
            for item in raw_list
        ]

    def to_dict(self, location_name: str | None = None) -> dict:
        """转字典，可选附加 location_name（JOIN 查询时填充）"""
        d = {
            "id": self.id,
            "location_id": self.location_id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "detect_time": self.detect_time,
            "result_json": self.result_json,
            "total_animals": self.total_animals,
            "animals": [a.to_dict() for a in self.get_animals()],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if location_name:
            d["location_name"] = location_name
        return d
