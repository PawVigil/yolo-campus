"""响应体 Pydantic 模型 —— 参考 SDS 5.3 + 第6章接口契约"""

from datetime import datetime
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 通用
# ---------------------------------------------------------------------------
class PaginatedResult(BaseModel):
    """分页结果包装"""
    items: list
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# 鉴权
# ---------------------------------------------------------------------------
class TokenResponse(BaseModel):
    """A1. POST /api/auth/login"""
    token: str
    username: str
    role: str = "admin"


# ---------------------------------------------------------------------------
# 检测（管理端）
# ---------------------------------------------------------------------------
class DetectionPreviewResponse(BaseModel):
    """B1. POST /api/upload — 预览结果（不存库）"""
    image_url: str
    annotated_url: str
    animals: list[dict]
    total: int


class DetectionListItem(BaseModel):
    """B3. GET /api/detections — 列表项"""
    id: int
    location_name: str
    image_url: str
    detect_time: str
    total_animals: int
    breed_summary: str         # 品种摘要（去重拼接）


class DetectionListResponse(BaseModel):
    """B3. GET /api/detections — 分页列表"""
    items: list[DetectionListItem]
    total: int
    page: int
    page_size: int


class DetectionDetailResponse(BaseModel):
    """B4. GET /api/detections/{id}"""
    id: int
    location_name: str
    image_url: str
    annotated_url: str | None = None
    detect_time: str
    result_json: str
    total_animals: int
    animals: list[dict]         # 解析好的 [{breed_cn, breed_en, confidence, box}]
    created_at: str


# ---------------------------------------------------------------------------
# 地点（管理端）
# ---------------------------------------------------------------------------
class LocationResponse(BaseModel):
    """B6/B7/B8. 地点响应"""
    id: int
    name: str
    description: str | None = None
    safety_tip: str | None = None
    created_at: str


class LocationListResponse(BaseModel):
    """B6. GET /api/locations"""
    items: list[LocationResponse]


# ---------------------------------------------------------------------------
# 安全提醒（管理端）
# ---------------------------------------------------------------------------
class SafetyTipResponse(BaseModel):
    """B10/B11/B12. 安全提醒响应"""
    id: int
    location_id: int
    location_name: str | None = None   # JOIN location
    title: str
    content: str
    status: str
    created_at: str
    published_at: str | None = None


class SafetyTipListResponse(BaseModel):
    """B10. GET /api/safety-tips"""
    items: list[SafetyTipResponse]


class SafetyTipStatusResponse(BaseModel):
    """B13. PUT /api/safety-tips/{id}/status"""
    id: int
    status: str
    published_at: str | None = None


class Suggestion(BaseModel):
    """B14. 自动生成建议"""
    location_id: int
    location_name: str
    count: int
    suggestion_text: str
    data_basis: str             # "近7天检测23次"


class SuggestionListResponse(BaseModel):
    """B14. GET /api/safety-tips/suggestions"""
    suggestions: list[Suggestion]


# ---------------------------------------------------------------------------
# 管理端看板
# ---------------------------------------------------------------------------
class Stats(BaseModel):
    """管理端统计"""
    total_detections: int
    with_animals: int
    locations_covered: int
    published_tips: int


class LocationRank(BaseModel):
    """地点排行"""
    name: str
    count: int


class BreedRank(BaseModel):
    """品种排行"""
    breed: str
    count: int


class TrendPoint(BaseModel):
    """趋势数据点"""
    day: str                    # "2026-07-01"
    count: int


class AdminDashboard(BaseModel):
    """B15. GET /api/dashboard"""
    stats: Stats
    location_ranking: list[LocationRank]
    breed_top5: list[BreedRank]
    trend_14d: list[TrendPoint]


# ---------------------------------------------------------------------------
# 公共端看板
# ---------------------------------------------------------------------------
class PublicStats(BaseModel):
    """公共端统计"""
    total_detections: int
    with_animals: int
    locations_covered: int
    breed_count: int


class LocationStatus(BaseModel):
    """C1. 地点状态"""
    id: int
    name: str
    emoji: str = "📍"
    status: str                 # "active" | "resting" | "no_record"
    recent_breeds: list[str]
    last_detect_time: str | None = None


class SafetyTipBrief(BaseModel):
    """C1. 安全提醒摘要"""
    location_name: str
    content: str


class PublicDashboard(BaseModel):
    """C1. GET /api/public/dashboard"""
    stats: PublicStats
    location_status: list[LocationStatus]
    trend_14d: list[TrendPoint]
    safety_tips: list[SafetyTipBrief]


# ---------------------------------------------------------------------------
# 公共端 - 日历
# ---------------------------------------------------------------------------
class CalendarDayLocation(BaseModel):
    """C2. 日历某天某地点"""
    name: str
    breeds: list[str]


class CalendarDay(BaseModel):
    """C2. 日历某天"""
    date: str                   # "2026-07-01"
    has_animals: bool
    locations: list[CalendarDayLocation]


class CalendarResponse(BaseModel):
    """C2. GET /api/public/calendar"""
    month: str                  # "2026-07"
    days: list[CalendarDay]


# ---------------------------------------------------------------------------
# 公共端 - 排行榜
# ---------------------------------------------------------------------------
class RankingItem(BaseModel):
    """C4. 排行项"""
    rank: int
    name: str
    count: int
    emoji: str = ""


class RankingsResponse(BaseModel):
    """C4. GET /api/public/rankings"""
    breed_ranking: list[RankingItem]
    location_ranking: list[RankingItem]


# ---------------------------------------------------------------------------
# 公共端 - 撸猫指南
# ---------------------------------------------------------------------------
class GuideLocation(BaseModel):
    """C5. 单个地点的指南"""
    location_name: str
    breeds: list[str]
    safety_tip: str | None = None
    recent_count: int
    emoji: str = "🐱"


class GuideResponse(BaseModel):
    """C5. GET /api/public/guide"""
    locations: list[GuideLocation]


# ---------------------------------------------------------------------------
# 公共端 - 社区分享
# ---------------------------------------------------------------------------
class CommunityShareResponse(BaseModel):
    """C8/C9. 社区分享响应"""
    id: int
    location_id: int | None = None
    location_name: str | None = None
    image_url: str
    description: str | None = None
    nickname: str | None = None
    breed: str | None = None
    breed_info: dict | None = None   # 品种知识卡片（来自 breed_info.json）
    created_at: str


class CommunityListResponse(BaseModel):
    """C9. GET /api/public/community"""
    items: list[CommunityShareResponse]
    total: int
    page: int
    page_size: int


# ---------------------------------------------------------------------------
# 报表
# ---------------------------------------------------------------------------
class ReportMetric(BaseModel):
    """B16/B17. 报表指标"""
    metric: str
    value: str | int


class ReportData(BaseModel):
    """B16/B17. 报表数据"""
    type: str                   # "weekly" | "monthly"
    period: dict                # {start, end} 或 {year, month}
    data: list[ReportMetric]


# ---------------------------------------------------------------------------
# 简单确认响应
# ---------------------------------------------------------------------------
class OKResponse(BaseModel):
    """通用操作确认"""
    ok: bool = True
