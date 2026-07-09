"""管理端路由（需 JWT 鉴权）—— 参考 SDS 6.2 B1-B17"""

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from auth import get_current_user
from models.request import (
    DetectionFilter,
    LocationCreate,
    LocationUpdate,
    SaveDetectionRequest,
    SafetyTipCreate,
    SafetyTipStatusUpdate,
    SafetyTipUpdate,
)
from models.response import (
    DetectionDetailResponse,
    DetectionListResponse,
    DetectionListItem,
    DetectionPreviewResponse,
    LocationListResponse,
    LocationResponse,
    OKResponse,
    SafetyTipListResponse,
    SafetyTipResponse,
    SafetyTipStatusResponse,
    SuggestionListResponse,
)
from services.detection_service import DetectionService
from services.dashboard_service import DashboardService
from services.location_service import LocationService
from services.report_service import ReportService
from services.safety_tip_service import SafetyTipService

router = APIRouter(prefix="/api", tags=["管理端"], dependencies=[Depends(get_current_user)])


def _to_url(path: str) -> str:
    """将绝对/相对路径转为前端可用的相对URL"""
    if not path:
        return ""
    p = str(path).replace("\\", "/")
    if "uploads" in p:
        p = p.split("uploads", 1)[1]  # /community/xxx.jpg
        p = p.lstrip("/")
        return f"/uploads/{p}"
    if p.startswith("/"):
        return p
    return f"/{p}"


# ======================================================================
# B1. POST /api/upload — 上传图片+YOLO检测（预览，不存库）
# ======================================================================

@router.post("/upload", response_model=DetectionPreviewResponse)
async def upload_detect(
    file: UploadFile = File(...),
    location_id: int = Form(...),
    user: dict = Depends(get_current_user),
):
    """上传图片 → YOLO 检测 → 返回预览结果（不存库）"""
    # 校验文件
    file_data = await file.read()
    try:
        DetectionService.validate_file(file.filename or "unknown.jpg", len(file_data))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 保存文件
    image_path = DetectionService.save_upload_file(file_data, file.filename or "unknown.jpg")

    # YOLO 检测
    animals = DetectionService.detect(image_path)

    # 标注图
    annotated_path = DetectionService.annotate(image_path, animals) if animals else ""

    return DetectionPreviewResponse(
        image_url=_to_url(image_path),
        annotated_url=_to_url(annotated_path) if annotated_path else "",
        animals=[a.to_dict() for a in animals],
        total=len(animals),
    )


# ======================================================================
# B2. POST /api/detections — 保存检测记录
# ======================================================================

@router.post("/detections", status_code=status.HTTP_201_CREATED)
async def save_detection(
    req: SaveDetectionRequest,
    user: dict = Depends(get_current_user),
):
    """保存检测记录到数据库（使用 B1 预览的确认结果，不重新检测）"""
    from services.dashboard_service import clear_breed_count_cache
    clear_breed_count_cache()
    # 从请求体解析已确认的 animals
    from models.detection import AnimalResult, Box as BBox
    raw = json.loads(req.result_json)
    animals = [
        AnimalResult(
            breed_en=a["breed_en"], breed_cn=a["breed_cn"],
            confidence=a["confidence"], box=BBox(**a["box"]),
        )
        for a in raw
    ]
    det = DetectionService.save(
        location_id=req.location_id,
        user_id=user["id"],
        image_path=req.image_path,
        detect_time=req.detect_time,
        animals=animals,
        annotated_path=req.annotated_path,
    )
    return {"id": det.id, "created_at": det.created_at}


# ======================================================================
# B3. GET /api/detections — 检测记录列表
# ======================================================================

@router.get("/detections", response_model=DetectionListResponse)
async def list_detections(
    location_id: int | None = Query(None),
    breed: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=50),
):
    """分页+筛选查询"""
    filters = DetectionFilter(
        location_id=location_id,
        breed=breed,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )
    result = DetectionService.get_list(filters)
    items = [
        DetectionListItem(
            id=it["id"],
            location_name=it["location_name"],
            image_url=_to_url(it["image_url"]),
            detect_time=it["detect_time"],
            total_animals=it["total_animals"],
            breed_summary=it["breed_summary"],
        )
        for it in result.items
    ]
    return DetectionListResponse(
        items=items, total=result.total, page=result.page, page_size=result.page_size,
    )


# ======================================================================
# B4. GET /api/detections/{id} — 单条详情
# ======================================================================

@router.get("/detections/{detection_id}")
async def get_detection(detection_id: int):
    """单条检测记录详情（含 location_name + animals）"""
    result = DetectionService.get_by_id(detection_id)
    if result is None:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    det, location_name, annotated_path = result
    animals = det.get_animals()
    # 使用存储的标注图路径，如果为空则用空字符串
    annotated_url = _to_url(annotated_path) if annotated_path else ""
    return DetectionDetailResponse(
        id=det.id,
        location_name=location_name,
        image_url=_to_url(det.image_path),
        annotated_url=annotated_url,
        detect_time=det.detect_time,
        result_json=det.result_json,
        total_animals=det.total_animals,
        animals=[a.to_dict() for a in animals],
        created_at=det.created_at.isoformat() if det.created_at else "",
    )


# ======================================================================
# B5. DELETE /api/detections/{id} — 删除
# ======================================================================

@router.delete("/detections/{detection_id}", response_model=OKResponse)
async def delete_detection(detection_id: int):
    """删除记录 + 图片文件"""
    ok = DetectionService.delete(detection_id)
    if not ok:
        raise HTTPException(status_code=404, detail="检测记录不存在")
    return OKResponse()


# ======================================================================
# B6. GET /api/locations — 地点列表
# ======================================================================

@router.get("/locations", response_model=LocationListResponse)
async def list_locations():
    locs = LocationService.get_all()
    return LocationListResponse(
        items=[
            LocationResponse(
                id=l.id, name=l.name, description=l.description,
                safety_tip=l.safety_tip,
                created_at=l.created_at.isoformat() if l.created_at else "",
            )
            for l in locs
        ]
    )


# ======================================================================
# B7. POST /api/locations — 新增地点
# ======================================================================

@router.post("/locations", status_code=status.HTTP_201_CREATED, response_model=LocationResponse)
async def create_location(req: LocationCreate):
    try:
        loc = LocationService.create(name=req.name, description=req.description)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return LocationResponse(
        id=loc.id, name=loc.name, description=loc.description,
        safety_tip=loc.safety_tip,
        created_at=loc.created_at.isoformat() if loc.created_at else "",
    )


# ======================================================================
# B8. PUT /api/locations/{id} — 编辑地点
# ======================================================================

@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(location_id: int, req: LocationUpdate):
    loc = LocationService.update(location_id, req)
    if loc is None:
        raise HTTPException(status_code=404, detail="地点不存在")
    return LocationResponse(
        id=loc.id, name=loc.name, description=loc.description,
        safety_tip=loc.safety_tip,
        created_at=loc.created_at.isoformat() if loc.created_at else "",
    )


# ======================================================================
# B9. DELETE /api/locations/{id} — 删除地点
# ======================================================================

@router.delete("/locations/{location_id}", response_model=OKResponse)
async def delete_location(location_id: int):
    try:
        ok = LocationService.delete(location_id)
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="地点不存在")
    return OKResponse()


# ======================================================================
# B10. GET /api/safety-tips — 安全提醒列表
# ======================================================================

@router.get("/safety-tips", response_model=SafetyTipListResponse)
async def list_safety_tips():
    tips = SafetyTipService.get_all()
    return SafetyTipListResponse(
        items=[
            SafetyTipResponse(
                id=t["id"], location_id=t["location_id"],
                location_name=t.get("location_name"),
                title=t["title"], content=t["content"], status=t["status"],
                created_at=t["created_at"], published_at=t.get("published_at"),
            )
            for t in tips
        ]
    )


# ======================================================================
# B11. POST /api/safety-tips — 新建安全提醒
# ======================================================================

@router.post("/safety-tips", status_code=status.HTTP_201_CREATED, response_model=SafetyTipResponse)
async def create_safety_tip(req: SafetyTipCreate):
    tip = SafetyTipService.create(
        location_id=req.location_id,
        title=req.title,
        content=req.content,
        status=req.status,
    )
    return SafetyTipResponse(
        id=tip["id"], location_id=tip["location_id"],
        location_name=None, title=tip["title"], content=tip["content"],
        status=tip["status"], created_at=tip["created_at"],
        published_at=tip.get("published_at"),
    )


# ======================================================================
# B12. PUT /api/safety-tips/{id} — 编辑安全提醒
# ======================================================================

@router.put("/safety-tips/{tip_id}", response_model=SafetyTipResponse)
async def update_safety_tip(tip_id: int, req: SafetyTipUpdate):
    tip = SafetyTipService.update(tip_id, req.title, req.content, req.status, req.location_id)
    if tip is None:
        raise HTTPException(status_code=404, detail="安全提醒不存在")
    return SafetyTipResponse(
        id=tip["id"], location_id=tip["location_id"],
        location_name=None, title=tip["title"], content=tip["content"],
        status=tip["status"], created_at=tip["created_at"],
        published_at=tip.get("published_at"),
    )


# ======================================================================
# B13. PUT /api/safety-tips/{id}/status — 发布/下架
# ======================================================================

@router.put("/safety-tips/{tip_id}/status", response_model=SafetyTipStatusResponse)
async def update_safety_tip_status(tip_id: int, req: SafetyTipStatusUpdate):
    if req.status == "published":
        tip = SafetyTipService.publish(tip_id)
    elif req.status == "archived":
        tip = SafetyTipService.archive(tip_id)
    else:
        raise HTTPException(status_code=400, detail="status 仅支持 published 或 archived")
    if tip is None:
        raise HTTPException(status_code=404, detail="安全提醒不存在")
    return SafetyTipStatusResponse(
        id=tip["id"], status=tip["status"],
        published_at=tip.get("published_at"),
    )


# ======================================================================
# DELETE /api/safety-tips/{id} — 删除安全提醒
# ======================================================================

@router.delete("/safety-tips/{tip_id}", response_model=OKResponse)
async def delete_safety_tip(tip_id: int):
    ok = SafetyTipService.delete(tip_id)
    if not ok:
        raise HTTPException(status_code=404, detail="安全提醒不存在")
    return OKResponse(ok=True)


# ======================================================================
# B14. GET /api/safety-tips/suggestions — 自动生成建议
# ======================================================================

@router.get("/safety-tips/suggestions", response_model=SuggestionListResponse)
async def get_safety_suggestions():
    suggestions = SafetyTipService.auto_generate()
    return SuggestionListResponse(suggestions=suggestions)


# ======================================================================
# B15. GET /api/dashboard — 管理端看板
# ======================================================================

@router.get("/dashboard")
async def get_admin_dashboard():
    return DashboardService.get_admin_dashboard().model_dump()


# ======================================================================
# B16. GET /api/reports/weekly — 周报
# ======================================================================

@router.get("/reports/weekly")
async def weekly_report(
    start: str = Query(..., description="YYYY-MM-DD"),
    end: str = Query(..., description="YYYY-MM-DD"),
    format: str = Query("json", description="json | csv"),
):
    from fastapi.responses import PlainTextResponse
    data = ReportService.generate_weekly(start, end)
    if format == "csv":
        csv_str = ReportService.export_csv(data)
        return PlainTextResponse(
            content=csv_str,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename=weekly_{start.replace('-','')}_{end.replace('-','')}.csv"},
        )
    return data.model_dump()


# ======================================================================
# B17. GET /api/reports/monthly — 月报
# ======================================================================

@router.get("/reports/monthly")
async def monthly_report(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    format: str = Query("json", description="json | csv"),
):
    from fastapi.responses import PlainTextResponse
    data = ReportService.generate_monthly(year, month)
    if format == "csv":
        csv_str = ReportService.export_csv(data)
        filename = f"monthly_{year}_{month:02d}.csv"
        return PlainTextResponse(
            content=csv_str,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    return data.model_dump()
