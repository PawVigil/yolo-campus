# 🐾 PawVigil — 校园流浪动物观测关爱系统

> 拍照识别校园流浪猫狗品种，记录出没地点，打造有温度的校园动物地图

## 核心功能

- 📸 **AI 检测** — 上传照片，YOLOv8 自动识别 37 种猫狗品种
- 📊 **实时大屏** — 各地点动物活跃状态 + 近 14 天趋势图
- 📅 **出没日历** — 按月查看每天动物出没记录
- 🏆 **趣味排行榜** — 出镜之王 / 最佳宅猫 / 独行侠 / 最热闹地点
- 🐱 **撸猫指南** — 基于真实数据的地点评分 + 观测建议
- 📖 **品种百科** — 37 种猫狗完整资料（emoji / 体型 / 性格 / 趣味知识）
- 📸 **社区分享** — 多图上传 + 评论互动
- ⚠️ **安全提醒** — 自动生成 + 管理员发布
- 🔐 **管理后台** — 检测记录管理、报表导出

## 技术栈

| 层 | 技术 |
|----|------|
| 模型 | YOLOv8n (Ultralytics) + Oxford Pets 数据集 |
| 后端 | FastAPI + SQLite |
| 前端 | Vue 3 + Naive UI + ECharts + Vue Router + axios |
| 构建 | Vite |

## 项目结构

```
yolo-campus/
├── frontend/                  # Vue 3 前端（胡淦斌）
│   ├── src/
│   │   ├── views/public/      #   公共页面（6个）
│   │   ├── views/admin/       #   管理页面（7个）
│   │   ├── components/        #   通用组件
│   │   ├── api/               #   axios + Mock 数据
│   │   ├── router/            #   路由配置
│   │   └── stores/            #   状态管理
│   ├── 启动前端.vbs           #   Windows 双击启动
│   └── package.json
├── backend/                   # FastAPI 后端（宋鑫旺）
├── demo/                      # YOLO 检测 Demo
├── best.pt                    # 训练好的模型权重
├── breed_info.json            # 37 品种知识库
├── train_with_progress.py     # YOLO 训练脚本
└── docs/                      # 系统文档
    ├── 需求规格说明书/
    └── 系统设计说明书/
```

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev
# 打开 http://localhost:5173
```

> Windows 下可直接双击 `frontend/启动前端.vbs` 一键启动。

### Demo

```bash
cd demo
pip install fastapi uvicorn ultralytics opencv-python
python main.py
# 打开 http://localhost:8000
```

## 作者

| 角色 | 成员 |
|------|------|
| 前端 / 模型 | 胡淦斌 |
| 后端 / 架构 | 宋鑫旺 |
