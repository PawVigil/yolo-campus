"""公共端路由（无需鉴权）—— 参考 SDS 6.2 C1-C9"""

import json
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status

from db import get_db
from models.request import CommunityUploadRequest
from models.response import (
    CalendarDay,
    CalendarDayLocation,
    CalendarResponse,
    CommunityListResponse,
    GuideLocation,
    GuideResponse,
    PublicDashboard,
    RankingItem,
    RankingsResponse,
)
from services.community_service import CommunityService
from services.dashboard_service import DashboardService
from services.safety_tip_service import SafetyTipService
from services.share_card_service import ShareCardService

router = APIRouter(prefix="/api/public", tags=["公共端"])


# ======================================================================
# C1. GET /api/public/dashboard — 实时大屏
# ======================================================================

@router.get("/dashboard")
async def public_dashboard():
    return DashboardService.get_public_dashboard().model_dump()


# ======================================================================
# C2. GET /api/public/calendar — 出没日历
# ======================================================================

@router.get("/calendar", response_model=CalendarResponse)
async def calendar(month: str = Query(..., description="YYYY-MM", pattern=r"^\d{4}-\d{2}$")):
    """返回指定月的每日动物出没汇总"""
    # 校验月份格式
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=422, detail="月份格式错误，应为 YYYY-MM，如 2026-07")

    conn = get_db()
    try:
        # 查询该月所有有动物的日期
        rows = conn.execute(
            """SELECT date(detect_time) as day, d.location_id, l.name as loc_name,
                      d.result_json
               FROM detection d
               JOIN location l ON d.location_id = l.id
               WHERE strftime('%Y-%m', detect_time) = ?
                 AND d.total_animals > 0
               ORDER BY day, d.location_id""",
            (month,),
        ).fetchall()

        # 按日期分组
        day_map: dict[str, dict[int, dict]] = {}
        for r in rows:
            day = r["day"]
            if day not in day_map:
                day_map[day] = {}
            if r["location_id"] not in day_map[day]:
                day_map[day][r["location_id"]] = {"name": r["loc_name"], "breeds": []}
            try:
                for a in json.loads(r["result_json"]):
                    breed_cn = a.get("breed_cn", "")
                    if breed_cn and breed_cn not in day_map[day][r["location_id"]]["breeds"]:
                        day_map[day][r["location_id"]]["breeds"].append(breed_cn)
            except (json.JSONDecodeError, KeyError):
                pass

        # 生成当月全部日期
        year, mon = int(month[:4]), int(month[5:7])
        import calendar as cal_mod
        num_days = cal_mod.monthrange(year, mon)[1]
        days: list[CalendarDay] = []
        for d in range(1, num_days + 1):
            date_str = f"{year}-{mon:02d}-{d:02d}"
            locs = day_map.get(date_str, {})
            locations = [
                CalendarDayLocation(name=v["name"], breeds=v["breeds"])
                for v in locs.values()
            ]
            days.append(CalendarDay(
                date=date_str,
                has_animals=len(locations) > 0,
                locations=locations,
            ))

        return CalendarResponse(month=month, days=days)
    finally:
        conn.close()


# ======================================================================
# C3. GET /api/public/detections — 按日期查检测详情
# ======================================================================

@router.get("/detections")
async def public_detections(date: str = Query(..., description="YYYY-MM-DD")):
    """查询指定日期的所有检测记录"""
    conn = get_db()
    try:
        rows = conn.execute(
            """SELECT d.id, d.image_path, d.detect_time, d.total_animals,
                      d.result_json, l.name as location_name
               FROM detection d
               JOIN location l ON d.location_id = l.id
               WHERE date(d.detect_time) = ?
               ORDER BY d.detect_time DESC""",
            (date,),
        ).fetchall()

        items = []
        for r in rows:
            items.append({
                "id": r["id"],
                "location_name": r["location_name"],
                "image_url": f"/{r['image_path']}",
                "annotated_url": f"/uploads/annotated/annotated_{r['image_path'].rsplit('/',1)[-1].rsplit('.',1)[0]}.jpg",
                "detect_time": r["detect_time"],
                "total_animals": r["total_animals"],
            })
        return {"items": items}
    finally:
        conn.close()


# ======================================================================
# C4. GET /api/public/rankings — 趣味排行榜
# ======================================================================

@router.get("/rankings", response_model=RankingsResponse)
async def rankings():
    """品种排行 + 地点排行"""
    conn = get_db()
    try:
        # 品种排行
        rows = conn.execute(
            "SELECT result_json FROM detection WHERE total_animals > 0"
        ).fetchall()
        breed_counter: Counter = Counter()
        for r in rows:
            try:
                for a in json.loads(r["result_json"]):
                    breed_counter[a.get("breed_cn", "未知")] += 1
            except (json.JSONDecodeError, KeyError):
                pass

        breed_ranking = [
            RankingItem(rank=i + 1, name=b, count=c, emoji="🐾")
            for i, (b, c) in enumerate(breed_counter.most_common(10))
        ]

        # 地点排行
        loc_rows = conn.execute(
            """SELECT l.name, COUNT(*) as cnt
               FROM detection d
               JOIN location l ON d.location_id = l.id
               GROUP BY d.location_id ORDER BY cnt DESC"""
        ).fetchall()
        location_ranking = [
            RankingItem(rank=i + 1, name=r["name"], count=r["cnt"], emoji="📍")
            for i, r in enumerate(loc_rows)
        ]

        return RankingsResponse(
            breed_ranking=breed_ranking,
            location_ranking=location_ranking,
        )
    finally:
        conn.close()


# ======================================================================
# C5. GET /api/public/guide — 撸猫指南
# ======================================================================

@router.get("/guide", response_model=GuideResponse)
async def guide():
    """返回每个地点的品种列表 + 安全提示"""
    conn = get_db()
    try:
        locations = conn.execute("SELECT * FROM location ORDER BY id").fetchall()
        result: list[GuideLocation] = []

        for loc in locations:
            # 最近品种
            det_rows = conn.execute(
                """SELECT result_json FROM detection
                   WHERE location_id = ? AND total_animals > 0
                   ORDER BY detect_time DESC LIMIT 5""",
                (loc["id"],),
            ).fetchall()

            breed_set: list[str] = []
            for r in det_rows:
                try:
                    for a in json.loads(r["result_json"]):
                        cn = a.get("breed_cn", "")
                        if cn and cn not in breed_set:
                            breed_set.append(cn)
                except (json.JSONDecodeError, KeyError):
                    pass

            # 最近检测数（近7天）
            recent = conn.execute(
                """SELECT COUNT(*) as cnt FROM detection
                   WHERE location_id = ?
                     AND date(detect_time) >= date('now', '-7 days', 'localtime')""",
                (loc["id"],),
            ).fetchone()

            result.append(GuideLocation(
                location_name=loc["name"],
                breeds=breed_set,
                safety_tip=loc["safety_tip"],
                recent_count=recent["cnt"],
                emoji="🐱",
            ))

        return GuideResponse(locations=result)
    finally:
        conn.close()


# ======================================================================
# C6. GET /api/public/safety-tips — 已发布安全提醒
# ======================================================================

@router.get("/safety-tips")
async def public_safety_tips():
    tips = SafetyTipService.get_published()
    return {"items": tips}


# ======================================================================
# C7. GET /api/public/share-card/{detection_id} — 分享卡片
# ======================================================================

@router.get("/share-card/{detection_id}")
async def share_card(detection_id: int):
    from fastapi.responses import HTMLResponse
    try:
        html = ShareCardService.generate(detection_id)
        return HTMLResponse(content=html)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ======================================================================
# C8. POST /api/public/community — 上传社区分享
# ======================================================================

@router.post("/community", status_code=status.HTTP_201_CREATED)
async def upload_community(
    image: UploadFile = File(...),
    location_id: int | None = Form(None),
    description: str | None = Form(None),
    nickname: str | None = Form(None),
    auto_detect: bool = Form(False),
):
    """上传社区分享图片"""
    # 校验文件
    from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES
    file_data = await image.read()
    ext = f".{image.filename.rsplit('.', 1)[-1].lower()}" if image.filename and "." in image.filename else ".jpg"
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 JPG/PNG 格式")
    if len(file_data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="文件大小超过 10MB 限制")

    # 保存文件
    image_path = CommunityService.save_upload_file(file_data, image.filename or "community.jpg")

    # 创建记录
    share = CommunityService.create(
        image_path=image_path,
        location_id=location_id,
        description=description,
        nickname=nickname,
        auto_detect=auto_detect,
    )
    return share.to_dict()


# ======================================================================
# C9. GET /api/public/community — 社区分享列表
# ======================================================================

@router.get("/community", response_model=CommunityListResponse)
async def list_community(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
):
    result = CommunityService.get_list(page=page, page_size=page_size)
    return CommunityListResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )
