"""User 实体模型 —— 参考 SDS 5.2.1"""

from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    """管理员用户"""
    id: int
    username: str
    password_hash: str
    role: str = "admin"
    created_at: datetime | None = None

    def verify_password(self, raw: str) -> bool:
        """验证明文密码是否匹配 SHA-256 哈希"""
        import hashlib
        return hashlib.sha256(raw.encode()).hexdigest() == self.password_hash

    def to_dict(self) -> dict:
        """返回不含 password_hash 的字典"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
