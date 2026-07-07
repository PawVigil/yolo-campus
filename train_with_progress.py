"""
YOLOv8 训练脚本 — Oxford Pets 37类品种识别
"""

from ultralytics import YOLO
from pathlib import Path
import torch, time

# ============ 自动定位 ============
BASE_DIR = Path(__file__).parent.resolve()
DATA_DIR = BASE_DIR / "yolo_format"
DATA_YAML = DATA_DIR / "data.yaml"

print("=" * 60)
print("   YOLOv8 训练 — Oxford Pets 37类品种识别")
print("=" * 60)
print(f"  脚本目录: {BASE_DIR}")
print(f"  数据目录: {DATA_DIR}")

# 检查数据集是否存在
if not DATA_DIR.exists():
    print(f"\n  ❌ 错误：找不到 {DATA_DIR}")
    print("  请确认 yolo_format 文件夹和本脚本在同一个目录下")
    print(f"  正确结构：")
    print(f"    {BASE_DIR.name}/")
    print(f"    ├── train_with_progress.py")
    print(f"    └── yolo_format/")
    print(f"        ├── data.yaml")
    print(f"        ├── images/")
    print(f"        └── labels/")
    exit(1)

# 动态生成 data.yaml（绝对路径，保证YOLO能找到）
yaml_content = f"""train: {DATA_DIR / 'images' / 'train'}
val: {DATA_DIR / 'images' / 'val'}
nc: 37
names: ['Abyssinian', 'american_bulldog', 'american_pit_bull_terrier', 'basset_hound', 'beagle', 'Bengal', 'Birman', 'Bombay', 'boxer', 'British_Shorthair', 'chihuahua', 'Egyptian_Mau', 'english_cocker_spaniel', 'english_setter', 'german_shorthaired', 'great_pyrenees', 'havanese', 'japanese_chin', 'keeshond', 'leonberger', 'Maine_Coon', 'miniature_pinscher', 'newfoundland', 'Persian', 'pomeranian', 'pug', 'Ragdoll', 'Russian_Blue', 'saint_bernard', 'samoyed', 'scottish_terrier', 'shiba_inu', 'Siamese', 'Sphynx', 'staffordshire_bull_terrier', 'wheaten_terrier', 'yorkshire_terrier']
"""
DATA_YAML.write_text(yaml_content)
print(f"  ✅ 配置文件已生成: {DATA_YAML}")

# 统计参数量
model = YOLO('yolov8n.pt')
params = sum(p.numel() for p in model.model.parameters() if p.requires_grad)

# 设备
device = 0 if torch.cuda.is_available() else 'cpu'
gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else '无'
print(f"  📊 参数: {params/1e6:.1f}M")
print(f"  💻 设备: {'GPU - ' + gpu_name if device == 0 else 'CPU'}")
print(f"  ⏱  轮数: 50  |  批次: 16  |  尺寸: 640")
print("=" * 60)

# 计时
start = time.time()

# 进度回调
def on_epoch_end(trainer):
    e, t = trainer.epoch, trainer.epochs
    elapsed = time.time() - start
    eta = (elapsed / (e + 1)) * (t - e - 1) if e > 0 else 0
    m = trainer.metrics
    pct = (e + 1) / t * 100
    bar = '█' * int(30 * (e + 1) / t) + '░' * (30 - int(30 * (e + 1) / t))
    print(f"\n  [{bar}] {pct:.0f}%  [{e+1}/{t}]")
    print(f"  Loss: box={m.get('train/box_loss',0):.4f}  cls={m.get('train/cls_loss',0):.4f}")
    print(f"  mAP: {m.get('metrics/mAP50',0):.4f}  P={m.get('metrics/precision',0):.4f}  R={m.get('metrics/recall',0):.4f}")
    print(f"  已用: {elapsed/60:.1f}分  剩余: {eta/60:.1f}分")

model.add_callback("on_train_epoch_end", on_epoch_end)

# 训练
model.train(
    data=str(DATA_YAML),
    epochs=50,
    imgsz=640,
    batch=16,
    device=device,
    patience=10,
    lr0=0.01,
    augment=True,
    name='oxford_pets',
    exist_ok=True,
    verbose=False,
)

print("\n" + "=" * 60)
print(f"  ✅ 训练完成！用时: {(time.time()-start)/60:.1f} 分")
print(f"  📍 模型: runs/detect/oxford_pets/weights/best.pt")
print("=" * 60)
