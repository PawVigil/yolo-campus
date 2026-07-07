# 🐾 PawVigil — 校园流浪动物观测关爱系统

> 拍照识别校园流浪猫狗品种，记录出没地点，打造有温度的校园动物地图

## 核心功能

- 📸 上传照片 → YOLO 自动检测猫狗品种（37 种）
- 📍 地点记录、出没日历、安全提醒
- 📊 排行榜、周报月报、数据大屏

## 技术栈

| 层 | 技术 |
|----|------|
| 模型 | YOLOv8n + Oxford Pets (37 品种) |
| 后端 | FastAPI + SQLite |
| 前端 | Vue 3 + ECharts |

## 快速开始

```bash
# Demo: 上传图片查看 YOLO 检测效果
cd demo
pip install fastapi uvicorn ultralytics opencv-python
python main.py
# 打开 http://localhost:8001
```

## 项目结构

```
yolo-campus/
├── demo/                    # YOLO 检测 Demo
│   ├── main.py              #   FastAPI 后端
│   └── templates/
│       └── index.html       #   前端页面
├── best.pt                  # 训练好的模型权重
├── train_with_progress.py   # YOLO 训练脚本
└── docs/                    # 文档
```

## 协作方式

1. `git checkout -b feature/xxx` 开分支开发
2. Push 后发起 Pull Request
3. 互审代码后 Merge 到 main
