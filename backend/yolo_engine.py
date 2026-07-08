"""YOLO 模型封装 —— 参考 SDS 5.2.2 YoloEngine + demo/main.py"""

import uuid
from pathlib import Path

import cv2
from ultralytics import YOLO

from config import ANNOTATED_DIR
from models.detection import AnimalResult, Box

# ---------------------------------------------------------------------------
# 37 品种中英文映射（Oxford Pets 数据集）
# ---------------------------------------------------------------------------
BREED_CN: dict[str, str] = {
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


class YoloEngine:
    """YOLOv8n 检测引擎（启动时加载模型，全局单例）"""

    def __init__(self) -> None:
        self._model: YOLO | None = None
        self._breeds: dict[int, str] = {}        # {cls_id: breed_en}
        self._breed_cn: dict[str, str] = BREED_CN

    # ------------------------------------------------------------------
    # SDS 方法
    # ------------------------------------------------------------------

    def init(self, model_path: str) -> None:
        """启动时调用，加载 best.pt"""
        self._model = YOLO(model_path)
        self._breeds = self._model.names or {}

    # ------------------------------------------------------------------
    # Public helpers（显式实现 SDS 定义的能力）
    # ------------------------------------------------------------------

    def detect(self, image_path: str) -> list[AnimalResult]:
        """YOLO 推理 → list[AnimalResult]"""
        if self._model is None:
            raise RuntimeError("YoloEngine 未初始化，请先调用 init()")

        results = self._model(image_path)
        animals: list[AnimalResult] = []

        for result in results:
            if result.boxes is None:
                continue
            for box, cls_id, conf in zip(
                result.boxes.xyxy, result.boxes.cls, result.boxes.conf
            ):
                breed_en = self._breeds.get(int(cls_id), "Unknown")
                breed_cn = self._breed_cn.get(breed_en, breed_en)
                x1, y1, x2, y2 = [round(float(v), 1) for v in box]
                animals.append(AnimalResult(
                    breed_en=breed_en,
                    breed_cn=breed_cn,
                    confidence=round(float(conf), 4),
                    box=Box(x1=x1, y1=y1, x2=x2, y2=y2),
                ))

        return animals

    def annotate(self, image_path: str, animals: list[AnimalResult]) -> str:
        """OpenCV 画框 + 标签，保存到 uploads/annotated/，返回标注图路径"""
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")

        for a in animals:
            b = a.box
            # 画矩形框
            cv2.rectangle(img, (int(b.x1), int(b.y1)), (int(b.x2), int(b.y2)),
                          (0, 255, 0), 2)
            # 画标签
            label = f"{a.breed_cn} {a.confidence:.0%}"
            cv2.putText(img, label, (int(b.x1), int(b.y1) - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # 保存
        ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
        save_name = f"annotated_{uuid.uuid4().hex}.jpg"
        save_path = ANNOTATED_DIR / save_name
        cv2.imwrite(str(save_path), img, [cv2.IMWRITE_JPEG_QUALITY, 92])

        return str(save_path)


# ---------------------------------------------------------------------------
# 全局单例（main.py 启动时调用 engine.init()）
# ---------------------------------------------------------------------------
engine = YoloEngine()
