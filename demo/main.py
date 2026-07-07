"""PawVigil YOLOv8 检测演示 - 上传图片查看检测效果"""

from pathlib import Path
import shutil
import uuid
import base64

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from ultralytics import YOLO
import cv2

# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.resolve()
MODEL_PATH = BASE_DIR.parent / "best.pt"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 加载模型
# ---------------------------------------------------------------------------
model = YOLO(str(MODEL_PATH))
BREEDS = model.names  # {0: 'Abyssinian', …}

# 品种中文映射（Oxford Pets 37类）
BREED_CN = {
    "Abyssinian": "阿比西尼亚猫", "american_bulldog": "美国斗牛犬",
    "american_pit_bull_terrier": "美国比特犬", "basset_hound": "巴吉度猎犬",
    "beagle": "比格犬", "Bengal": "孟加拉猫", "Birman": "伯曼猫",
    "Bombay": "孟买猫", "boxer": "拳师犬", "British_Shorthair": "英国短毛猫",
    "chihuahua": "吉娃娃", "Egyptian_Mau": "埃及猫",
    "english_cocker_spaniel": "英国可卡犬", "english_setter": "英国雪达犬",
    "german_shorthaired": "德国短毛指示犬", "great_pyrenees": "大白熊犬",
    "havanese": "哈瓦那犬", "japanese_chin": "日本狆", "keeshond": "荷兰毛狮犬",
    "leonberger": "兰伯格犬", "Maine_Coon": "缅因猫",
    "miniature_pinscher": "迷你品犬", "newfoundland": "纽芬兰犬",
    "Persian": "波斯猫", "pomeranian": "博美犬", "pug": "巴哥犬",
    "Ragdoll": "布偶猫", "Russian_Blue": "俄罗斯蓝猫",
    "saint_bernard": "圣伯纳犬", "samoyed": "萨摩耶",
    "scottish_terrier": "苏格兰梗", "shiba_inu": "柴犬",
    "Siamese": "暹罗猫", "Sphynx": "斯芬克斯猫",
    "staffordshire_bull_terrier": "斯塔福郡斗牛梗",
    "wheaten_terrier": "软毛麦色梗", "yorkshire_terrier": "约克夏梗",
}

# ---------------------------------------------------------------------------
# FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(title="PawVigil YOLO Demo")

# 首页：直接读取 HTML 文件
HTML_PATH = BASE_DIR / "templates" / "index.html"


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=HTML_PATH.read_text(encoding="utf-8"))


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    """上传图片 → YOLO检测 → 返回标注图(base64) + 检测结果"""
    # 保存上传文件
    ext = Path(file.filename).suffix if file.filename else ".jpg"
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / save_name
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # YOLO 检测（降低iou避免多只猫被合并成一个框）
    results = model(str(save_path), conf=0.25, iou=0.4, max_det=100)
    result = results[0]

    # --- 标注图 (plot返回BGR, cv2.imencode直接编码, 浏览器正常显示) ---
    annotated = result.plot(line_width=2, font_size=14)
    _, buf = cv2.imencode(".jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 92])
    img_b64 = base64.b64encode(buf).decode("utf-8")

    # --- 原始图 base64 (cv2.imread返回BGR, 直接编码即可) ---
    orig = cv2.imread(str(save_path))
    _, buf_orig = cv2.imencode(".jpg", orig, [cv2.IMWRITE_JPEG_QUALITY, 92])
    orig_b64 = base64.b64encode(buf_orig).decode("utf-8")

    # --- 检测详情 ---
    detections = []
    if result.boxes is not None:
        for box, cls_id, conf in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf):
            breed_en = BREEDS[int(cls_id)]
            breed_cn = BREED_CN.get(breed_en, breed_en)
            x1, y1, x2, y2 = [round(float(v), 1) for v in box]
            detections.append({
                "breed_en": breed_en.replace("_", " ").title(),
                "breed_cn": breed_cn,
                "confidence": f"{float(conf):.1%}",
                "location": f"({x1}, {y1}) ~ ({x2}, {y2})",
            })

    return {
        "image_base64": img_b64,
        "original_base64": orig_b64,
        "detections": detections,
        "count": len(detections),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
