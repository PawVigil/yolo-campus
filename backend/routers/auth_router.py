"""鉴权路由 —— POST /api/auth/login（参考 SDS 6.2 A1）"""

from fastapi import APIRouter, HTTPException, status

from auth import AuthService
from models.request import LoginRequest
from models.response import TokenResponse

router = APIRouter(prefix="/api/auth", tags=["鉴权"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(req: LoginRequest):
    """管理员登录 → JWT Token"""
    try:
        result = AuthService.login(req.username, req.password)
    except HTTPException:
        raise
    return TokenResponse(
        token=result["token"],
        username=result["username"],
        role=result["role"],
    )
