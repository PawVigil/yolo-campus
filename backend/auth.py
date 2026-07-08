"""JWT 鉴权服务 + 中间件 —— 参考 SDS 5.2.2 AuthService"""

import hashlib
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request, status

from config import JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_SECRET_KEY
from db import get_db


# ---------------------------------------------------------------------------
# AuthService（SDS 5.2.2）
# ---------------------------------------------------------------------------

class AuthService:
    """JWT 鉴权服务"""

    @staticmethod
    def hash_password(password: str) -> str:
        """SHA-256 哈希 → 64位 hex"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(username: str, password: str) -> dict:
        """
        验证用户名密码，返回 TokenPair。
        失败抛出 HTTPException(401)。
        """
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT id, username, password_hash, role FROM user WHERE username = ?",
                (username,),
            ).fetchone()

            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误",
                )

            pwd_hash = AuthService.hash_password(password)
            if pwd_hash != row["password_hash"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误",
                )

            # 生成 JWT
            now = datetime.now(timezone.utc)
            payload = {
                "sub": str(row["id"]),
                "username": row["username"],
                "role": row["role"],
                "iat": now,
                "exp": now + timedelta(hours=JWT_EXPIRE_HOURS),
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

            return {
                "token": token,
                "username": row["username"],
                "role": row["role"],
            }
        finally:
            conn.close()

    @staticmethod
    def verify_token(token: str) -> dict:
        """
        验证 JWT Token，返回 payload dict (id, username, role)。
        失败抛出 HTTPException(401)。
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return {
                "id": int(payload["sub"]),
                "username": payload["username"],
                "role": payload["role"],
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 已过期，请重新登录",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token 无效",
            )


# ---------------------------------------------------------------------------
# FastAPI 依赖注入（用于路由保护）
# ---------------------------------------------------------------------------

def get_current_user(request: Request) -> dict:
    """
    从 Authorization Header 提取并验证 Token。
    用作 FastAPI Depends 依赖，保护管理端路由。

    用法：
        @router.post("/upload")
        async def upload(..., user: dict = Depends(get_current_user)):
            ...
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或 Token 缺失",
        )

    token = auth_header[len("Bearer "):]
    return AuthService.verify_token(token)
