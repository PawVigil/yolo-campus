"""
应用配置常量
参考：系统设计说明书 5.3 类→文件映射表
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# 路径（以 backend/ 为基准解析）
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "campus_animals.db"
MODEL_PATH = BASE_DIR.parent / "best.pt"          # 模型权重在项目根目录
BREED_INFO_PATH = BASE_DIR / "breed_info.json"    # 品种知识库已复制到 backend/
UPLOAD_DIR = BASE_DIR / "uploads"
ANNOTATED_DIR = UPLOAD_DIR / "annotated"
COMMUNITY_DIR = UPLOAD_DIR / "community"

# ---------------------------------------------------------------------------
# JWT 鉴权
# ---------------------------------------------------------------------------
JWT_SECRET_KEY = "pawvigil-yolo-campus-2026-secret-key"  # 演示环境固定密钥
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

# ---------------------------------------------------------------------------
# 文件上传限制
# ---------------------------------------------------------------------------
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# ---------------------------------------------------------------------------
# 分页默认值
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE = 15
MAX_PAGE_SIZE = 50
