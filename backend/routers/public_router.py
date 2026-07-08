"""公共端路由（无需鉴权）—— 参考 SDS 6.2 C1-C9"""

import json
from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Body, File, Form, HTTPException, Query, UploadFile, status

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
    RankingsResponse,
    MostSeenRank,
    HomebodyRank,
    RareRank,
    BusiestPlaceRank,
    BestTimeRank,
    MainBreed,
    BestTime,
)

# breed_info.json 缓存
import json as json_module
from pathlib import Path as PathModule
_breed_info_cache = None

def _get_breed_info():
    global _breed_info_cache
    if _breed_info_cache is None:
        path = PathModule(__file__).parent.parent / "breed_info.json"
        with open(path, "r", encoding="utf-8") as f:
            _breed_info_cache = json_module.load(f)
    return _breed_info_cache
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
# /api/public/breed-stats — 品种检测统计（前端品种百科页面使用）
# ======================================================================

@router.get("/breed-stats")
async def breed_stats():
    """返回各品种的检测次数统计"""
    conn = get_db()
    try:
        breed_info = _get_breed_info()
        # 构建中文名→英文key的映射
        cn_to_en = {}
        for key, info in breed_info.items():
            cn_to_en[info.get("name_cn", key)] = key

        rows = conn.execute(
            "SELECT result_json FROM detection WHERE total_animals > 0"
        ).fetchall()

        breed_count: Counter = Counter()
        for r in rows:
            try:
                for a in json.loads(r["result_json"]):
                    breed_count[a.get("breed_cn", "")] += 1
            except (json.JSONDecodeError, KeyError):
                pass

        stats = {b: c for b, c in breed_count.items()}
        return {"stats": stats, "breed_info": breed_info}
    finally:
        conn.close()


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
    """趣味排行榜（参考 SDS 4.3 排行榜聚合算法）"""
    conn = get_db()
    try:
        # 查询所有有动物的记录
        rows = conn.execute(
            """SELECT d.result_json, d.detect_time, d.location_id, l.name as location_name
               FROM detection d
               JOIN location l ON d.location_id = l.id
               WHERE d.total_animals > 0"""
        ).fetchall()

        # 展平——每条记录可能含多个品种
        breed_records = []
        for row in rows:
            try:
                animals = json.loads(row["result_json"])
                hour_str = row["detect_time"]  # "2026-07-06 12:30:00"
                hour = int(hour_str[11:13]) if len(hour_str) >= 13 else 0
                for animal in animals:
                    breed_records.append({
                        "breed": animal.get("breed_cn", "未知"),
                        "location": row["location_name"],
                        "hour": hour
                    })
            except (json.JSONDecodeError, KeyError):
                pass

        if not breed_records:
            # 没有数据时返回空结果
            return RankingsResponse(
                most_seen=MostSeenRank(breed="暂无", count=0, percentage=0),
                homebody=HomebodyRank(breed="暂无", location="暂无", percentage=0),
                rare=RareRank(breed="暂无", count=0),
                busiest_place=BusiestPlaceRank(name="暂无", count=0, percentage=0),
                best_time=BestTimeRank(hour_range="暂无", avg_count=0),
            )

        total = len(breed_records)

        # 1. 出镜之王——频率最高的品种
        breed_counts = Counter(r["breed"] for r in breed_records)
        most_seen_breed, most_seen_count = breed_counts.most_common(1)[0]

        # 2. 最佳宅猫——单一地点集中度最高的品种
        breed_location = Counter(
            (r["breed"], r["location"]) for r in breed_records
        )
        breed_concentration = {}
        for breed in set(r["breed"] for r in breed_records):
            breed_total = breed_counts[breed]
            max_spot = max(
                ((loc, count) for (b, loc), count in breed_location.items() if b == breed),
                key=lambda x: x[1]
            )
            breed_concentration[breed] = {
                "location": max_spot[0],
                "percentage": max_spot[1] / breed_total
            }
        homebody = max(breed_concentration.items(),
                       key=lambda x: x[1]["percentage"])

        # 3. 独行侠——出现次数最少的品种
        rare_breed, rare_count = breed_counts.most_common()[-1]

        # 4. 最热闹地点
        location_counts = Counter(r["location"] for r in breed_records)
        busiest_place, busiest_count = location_counts.most_common(1)[0]

        # 5. 最佳观测时间——2小时滑动窗口
        hour_counts = Counter(r["hour"] for r in breed_records)
        best_start = max(range(0, 23),
            key=lambda h: hour_counts.get(h, 0) + hour_counts.get(h+1, 0))

        return RankingsResponse(
            most_seen=MostSeenRank(
                breed=most_seen_breed,
                count=most_seen_count,
                percentage=round(most_seen_count / total, 2)
            ),
            homebody=HomebodyRank(
                breed=homebody[0],
                location=homebody[1]["location"],
                percentage=round(homebody[1]["percentage"], 2)
            ),
            rare=RareRank(
                breed=rare_breed,
                count=rare_count
            ),
            busiest_place=BusiestPlaceRank(
                name=busiest_place,
                count=busiest_count,
                percentage=round(busiest_count / total, 2)
            ),
            best_time=BestTimeRank(
                hour_range=f"{best_start:02d}:00 - {best_start+2:02d}:00",
                avg_count=round(
                    (hour_counts.get(best_start, 0) +
                     hour_counts.get(best_start+1, 0)) / 2, 1
                )
            ),
        )
    finally:
        conn.close()


# ======================================================================
# C5. GET /api/public/guide — 撸猫指南
# ======================================================================

@router.get("/guide", response_model=GuideResponse)
async def guide():
    """返回每个地点的指南（按出没率排序，参考 SDS 3.2.4）"""
    conn = get_db()
    try:
        locations = conn.execute("SELECT * FROM location ORDER BY id").fetchall()
        result: list[GuideLocation] = []

        # 地点emoji映射
        EMOJI_MAP = {
            "食堂": "🍽️", "宿舍": "🏠", "图书馆": "📚",
            "操场": "🏟️", "花园": "🌳",
        }

        # 出没率→星级映射
        def to_rating(rate: float) -> int:
            if rate >= 0.8: return 5
            if rate >= 0.6: return 4
            if rate >= 0.4: return 3
            if rate >= 0.2: return 2
            return 1

        # 出没率→描述模板
        def to_pattern(rate: float) -> str:
            if rate >= 0.8: return "几乎每天都会出现"
            if rate >= 0.5: return "经常出现"
            if rate >= 0.3: return "偶有出没"
            return "不常出现"

        # 出没率→小贴士
        TIPS = {
            "食堂": "带根火腿肠去食堂后门，中午12点左右是观测最佳时段。",
            "宿舍": "傍晚下课回宿舍的路上多留意绿化带。",
            "图书馆": "下午去图书馆自习时，从后门进去可能会遇到晒太阳的猫咪。",
            "操场": "晨跑时可能会在操场东北角看到狗狗，建议保持距离观察。",
            "花园": "上午阳光好的时候在花园长椅附近可能会遇到小猫。",
        }

        for loc in locations:
            # 出没率 = 有动物的记录数/总检测数
            stats = conn.execute(
                """SELECT COUNT(*) as total,
                          SUM(CASE WHEN total_animals > 0 THEN 1 ELSE 0 END) as with_animals
                   FROM detection
                   WHERE location_id = ?""",
                (loc["id"],),
            ).fetchone()
            total = stats["total"] or 0
            with_animals = stats["with_animals"] or 0
            appearance_rate = round(with_animals / total, 2) if total > 0 else 0

            # 主要住户品种 TOP3
            det_rows = conn.execute(
                """SELECT result_json FROM detection
                   WHERE location_id = ? AND total_animals > 0""",
                (loc["id"],),
            ).fetchall()

            breed_counter: Counter = Counter()
            for r in det_rows:
                try:
                    for a in json.loads(r["result_json"]):
                        breed_counter[a.get("breed_cn", "未知")] += 1
                except (json.JSONDecodeError, KeyError):
                    pass

            main_breeds = [
                MainBreed(breed_cn=b, count=c)
                for b, c in breed_counter.most_common(3)
            ]

            # 最佳观测时段（按小时聚合找峰值）
            time_rows = conn.execute(
                """SELECT detect_time FROM detection
                   WHERE location_id = ? AND total_animals > 0""",
                (loc["id"],),
            ).fetchall()

            hour_counts: Counter = Counter()
            for r in time_rows:
                try:
                    dt = r["detect_time"]
                    hour = int(dt[11:13]) if len(dt) >= 13 else 0
                    hour_counts[hour] += 1
                except (ValueError, IndexError):
                    pass

            best_time = None
            if hour_counts:
                best_hour = hour_counts.most_common(1)[0][0]
                best_time = BestTime(
                    start=f"{best_hour:02d}:00",
                    end=f"{best_hour+2:02d}:00",
                )

            # 文字描述
            pattern_desc = to_pattern(appearance_rate) if appearance_rate > 0 else "暂无记录"
            tip = TIPS.get(loc["name"], "请保持安全距离，不要随意投喂。")

            result.append(GuideLocation(
                name=loc["name"],
                emoji=EMOJI_MAP.get(loc["name"], "🐱"),
                rating=to_rating(appearance_rate),
                appearance_rate=appearance_rate,
                main_breeds=main_breeds,
                best_time=best_time,
                pattern_desc=pattern_desc,
                tip=tip,
            ))

        # 按出没率降序排列
        result.sort(key=lambda x: x.appearance_rate, reverse=True)
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
    images: list[UploadFile] = File(...),
    location_id: int | None = Form(None),
    description: str | None = Form(None),
    nickname: str | None = Form(None),
    auto_detect: bool = Form(False),
):
    """上传社区分享图片（支持多张）"""
    from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES

    image_paths: list[str] = []
    for img in images:
        file_data = await img.read()
        ext = f".{img.filename.rsplit('.', 1)[-1].lower()}" if img.filename and "." in img.filename else ".jpg"
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"仅支持 JPG/PNG 格式: {img.filename}")
        if len(file_data) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"文件大小超过 10MB 限制: {img.filename}")
        saved_path = CommunityService.save_upload_file(file_data, img.filename or "community.jpg")
        image_paths.append(saved_path)

    # 创建记录（存储JSON数组）
    share = CommunityService.create(
        image_paths=image_paths,
        location_id=location_id,
        description=description,
        nickname=nickname,
        auto_detect=auto_detect,
    )
    # 返回完整响应（含image_url, images, comments等）
    result = CommunityService.get_by_id(share.id)
    if result:
        return result.model_dump()
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


# ======================================================================
# POST /api/public/community/{id}/comments — 社区评论
# ======================================================================

@router.post("/community/{share_id}/comments")
async def add_community_comment(
    share_id: int,
    payload: dict = Body(...),
):
    """添加评论到社区分享"""
    result = CommunityService.add_comment(
        share_id,
        payload.get("nickname", ""),
        payload.get("text", ""),
    )
    if result is None:
        raise HTTPException(status_code=404, detail="分享不存在")
    return {"ok": True, "comments": result}
