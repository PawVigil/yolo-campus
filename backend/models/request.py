"""请求体 Pydantic 模型 —— 参考 SDS 5.3 + 第6章接口契约"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 鉴权
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    """A1. POST /api/auth/login"""
    username: str
    password: str


# ---------------------------------------------------------------------------
# 检测
# ---------------------------------------------------------------------------
class SaveDetectionRequest(BaseModel):
    """B2. POST /api/detections"""
    location_id: int
    image_path: str
    detect_time: str          # ISO 8601
    result_json: str          # JSON.stringify(animals)
    total_animals: int = 0


class DetectionFilter(BaseModel):
    """B3. GET /api/detections 查询参数"""
    location_id: int | None = None
    breed: str | None = None
    date_from: str | None = None    # "2026-07-01"
    date_to: str | None = None
    page: int = 1
    page_size: int = 15


# ---------------------------------------------------------------------------
# 地点
# ---------------------------------------------------------------------------
class LocationCreate(BaseModel):
    """B7. POST /api/locations"""
    name: str
    description: str | None = None


class LocationUpdate(BaseModel):
    """B8. PUT /api/locations/{id}（至少传一个字段）"""
    name: str | None = None
    description: str | None = None


# ---------------------------------------------------------------------------
# 安全提醒
# ---------------------------------------------------------------------------
class SafetyTipCreate(BaseModel):
    """B11. POST /api/safety-tips"""
    location_id: int
    title: str
    content: str
    status: str = "draft"


class SafetyTipUpdate(BaseModel):
    """B12. PUT /api/safety-tips/{id}"""
    title: str | None = None
    content: str | None = None


class SafetyTipStatusUpdate(BaseModel):
    """B13. PUT /api/safety-tips/{id}/status"""
    status: str                 # "published" | "archived"


# ---------------------------------------------------------------------------
# 社区分享
# ---------------------------------------------------------------------------
class CommunityUploadRequest(BaseModel):
    """C8. POST /api/public/community（除图片外的表单字段）"""
    location_id: int | None = None
    description: str | None = None
    nickname: str | None = None
    auto_detect: bool = False   # 是否启用 YOLO 自动识别
