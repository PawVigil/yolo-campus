"""FastAPI 入口 —— 参考 SDS 1.1 分层架构 + 5.3 main.py"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import MODEL_PATH, UPLOAD_DIR
from db import init_db
from yolo_engine import engine


# ---------------------------------------------------------------------------
# 生命周期
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动/关闭时执行"""
    # 启动：初始化数据库 + 加载 YOLO 模型
    init_db()
    engine.init(str(MODEL_PATH))
    print(f"[OK] YOLO 模型已加载，{len(engine._breeds)} 个品种")
    yield
    # 关闭：无需特殊清理（SQLite 连接由各请求自行关闭）


# ---------------------------------------------------------------------------
# 创建应用
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PawVigil 校园流浪动物观测关爱系统",
    description="YOLOv8 + FastAPI + SQLite 后端 API",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS 中间件（允许前端跨域）
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# 静态文件挂载（上传图片可通过 URL 直接访问）
# ---------------------------------------------------------------------------

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# ---------------------------------------------------------------------------
# 注册路由（SDS 5.3 三层路由）
# ---------------------------------------------------------------------------

from routers.auth_router import router as auth_router
from routers.admin_router import router as admin_router
from routers.public_router import router as public_router

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(public_router)


# ---------------------------------------------------------------------------
# 直接启动入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
