"""
YOLO11 engelli plaka dedektörü eğitim scripti.
Önce generate_dataset.py'yi çalıştır!
"""
import pathlib, sys, yaml

DATASET_DIR = pathlib.Path("D:/Robotik/dataset")
MODEL_DIR   = pathlib.Path("D:/Robotik/models")
MODEL_DIR.mkdir(exist_ok=True)

# ── dataset.yaml ─────────────────────────────────────────────────────────
yaml_content = {
    "path":  str(DATASET_DIR),
    "train": "images/train",
    "val":   "images/val",
    "nc":    2,
    "names": ["disabled_plate", "normal_plate"],
}
yaml_path = DATASET_DIR / "dataset.yaml"
with open(yaml_path, "w") as f:
    yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
print(f"dataset.yaml yazildi: {yaml_path}")

# ── Veri seti kontrolü ────────────────────────────────────────────────────
for split in ("train", "val"):
    imgs = list((DATASET_DIR / "images" / split).glob("*.png"))
    lbls = list((DATASET_DIR / "labels" / split).glob("*.txt"))
    print(f"  {split}: {len(imgs)} goruntu, {len(lbls)} etiket")
    if len(imgs) == 0:
        print("HATA: Once generate_dataset.py calistir!")
        sys.exit(1)

# ── YOLO11 eğitimi ────────────────────────────────────────────────────────
try:
    from ultralytics import YOLO
except ImportError:
    print("ultralytics yuklu degil. Yuklemek icin: pip install ultralytics")
    sys.exit(1)

print("\nYOLO11s modeli yukleniyor...")
model = YOLO("yolo11s.pt")   # otomatik indirir

print("Egitim basliyor...")
results = model.train(
    data    = str(yaml_path),
    epochs  = 60,
    imgsz   = 160,
    batch   = 32,
    project = str(MODEL_DIR),
    name    = "plate_detector",
    exist_ok= True,
    device  = 0,
    verbose = True,
    patience= 15,
    cache   = True,
    workers = 0,        # Windows multiprocessing sorunu icin
)

# En iyi modeli kopyala
best = MODEL_DIR / "plate_detector" / "weights" / "best.pt"
if best.exists():
    import shutil
    shutil.copy(best, MODEL_DIR / "best.pt")
    print(f"\nEn iyi model kaydedildi: {MODEL_DIR / 'best.pt'}")
    print("Simülasyonda kullanmak icin:")
    print("  detector = Detector(screen, model_path='D:/Robotik/models/best.pt')")
else:
    print("best.pt bulunamadi, kontrol et.")
