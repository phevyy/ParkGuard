"""
Sentetik engelli plaka veri seti üretici.
Çıktı: dataset/images/{train,val}/ + dataset/labels/{train,val}/
Sınıflar: 0 = disabled_plate  |  1 = normal_plate
"""
import os, random, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# ── Dizinler ────────────────────────────────────────────────────────────
BASE   = pathlib.Path("D:/Robotik/dataset")
for split in ("train", "val"):
    (BASE / "images" / split).mkdir(parents=True, exist_ok=True)
    (BASE / "labels" / split).mkdir(parents=True, exist_ok=True)

# ── Görüntü boyutları ────────────────────────────────────────────────────
IMG_W, IMG_H     = 160, 80     # çıktı görüntü
PLATE_W, PLATE_H = 108, 26     # plaka alanı
EMBLEM_W         = 20          # mavi engelli kare genişliği

PX = (IMG_W - PLATE_W) // 2   # plaka sol x
PY = (IMG_H - PLATE_H) // 2   # plaka üst y

# YOLO bounding box (sabit, normalize)
BX = (PX + PLATE_W / 2) / IMG_W
BY = (PY + PLATE_H / 2) / IMG_H
BW = PLATE_W / IMG_W
BH = PLATE_H / IMG_H

# ── Renkler ──────────────────────────────────────────────────────────────
BODY_COLORS = [
    (185, 50, 50), (50, 110, 190), (55, 160, 55), (200, 162, 32),
    (155, 78, 182), (205, 205, 205), (82, 82, 82), (202, 122, 40),
    (40, 152, 170), (120, 80, 40), (30, 30, 30), (160, 160, 100),
]
C_PLATE_WHITE = (248, 248, 248)
C_PLATE_BLUE  = (28, 108, 225)
C_TEXT_DARK   = (15, 15, 15)
C_TEXT_WHITE  = (240, 245, 255)
C_PLATE_EDGE  = (90, 90, 90)

# ── Font yükleme ─────────────────────────────────────────────────────────
def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    paths = [
        f"C:/Windows/Fonts/{name}",
        f"C:/Windows/Fonts/{name.lower()}",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

plate_font  = _load_font("consola.ttf",  13)
symbol_font = _load_font("seguisym.ttf", 15)

# ── Plaka numarası üretici ────────────────────────────────────────────────
LETTERS = "ABCDEFGHJKLMNPRSTUVYZ"
def gen_plate() -> str:
    city  = random.randint(1, 81)
    lets  = "".join(random.choices(LETTERS, k=2))
    nums  = random.randint(100, 999)
    return f"{city} {lets} {nums}"

# ── Tek görüntü üret ─────────────────────────────────────────────────────
def make_image(is_disabled: bool) -> Image.Image:
    body = random.choice(BODY_COLORS)
    img  = Image.new("RGB", (IMG_W, IMG_H), color=body)
    draw = ImageDraw.Draw(img)

    # Plaka zemini (beyaz)
    draw.rectangle([PX, PY, PX + PLATE_W - 1, PY + PLATE_H - 1],
                   fill=C_PLATE_WHITE, outline=C_PLATE_EDGE, width=1)

    num_text = gen_plate()

    if is_disabled:
        # Sol mavi engelli karesi
        draw.rectangle([PX + 1, PY + 1, PX + EMBLEM_W - 1, PY + PLATE_H - 1],
                       fill=C_PLATE_BLUE)
        # ♿ sembolü
        try:
            draw.text((PX + EMBLEM_W // 2, PY + PLATE_H // 2),
                      "♿", font=symbol_font, fill=C_TEXT_WHITE, anchor="mm")
        except Exception:
            draw.text((PX + 4, PY + 6), "E", font=plate_font, fill=C_TEXT_WHITE)

        # Sağda plaka numarası
        text_cx = PX + EMBLEM_W + (PLATE_W - EMBLEM_W) // 2
        draw.text((text_cx, PY + PLATE_H // 2),
                  num_text, font=plate_font, fill=C_TEXT_DARK, anchor="mm")
    else:
        draw.text((PX + PLATE_W // 2, PY + PLATE_H // 2),
                  num_text, font=plate_font, fill=C_TEXT_DARK, anchor="mm")

    # ── Augmentation ────────────────────────────────────────────────
    # Parlaklık
    img = ImageEnhance.Brightness(img).enhance(random.uniform(0.72, 1.28))
    # Kontrast
    img = ImageEnhance.Contrast(img).enhance(random.uniform(0.85, 1.15))
    # Hafif blur (rastgele)
    if random.random() < 0.25:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.8)))
    # Gürültü (PIL'de manuel)
    if random.random() < 0.35:
        import numpy as np
        arr  = np.array(img, dtype=np.int16)
        noise = np.random.randint(-12, 13, arr.shape, dtype=np.int16)
        arr  = np.clip(arr + noise, 0, 255).astype(np.uint8)
        img  = Image.fromarray(arr)

    return img

# ── Veri seti üret ───────────────────────────────────────────────────────
def generate(n_per_class: int = 800, val_ratio: float = 0.2):
    n_val   = int(n_per_class * val_ratio)
    n_train = n_per_class - n_val
    total   = 0

    for cls_id, is_dis in [(0, True), (1, False)]:
        cls_name = "disabled" if is_dis else "normal"
        counts   = {"train": n_train, "val": n_val}
        for split, count in counts.items():
            for i in range(count):
                img  = make_image(is_disabled=is_dis)
                name = f"{cls_name}_{split}_{i:04d}"

                img.save(BASE / "images" / split / f"{name}.png")

                label = f"{cls_id} {BX:.6f} {BY:.6f} {BW:.6f} {BH:.6f}\n"
                (BASE / "labels" / split / f"{name}.txt").write_text(label)

                total += 1
                if total % 200 == 0:
                    print(f"  {total}/{n_per_class * 2} goruntu uretildi...")

    print(f"\nTamamlandi: {n_per_class*2} goruntu")
    print(f"  Train: {n_train*2}  |  Val: {n_val*2}")
    print(f"  Konum: {BASE}")


if __name__ == "__main__":
    print("Sentetik veri seti uretiliyor...")
    generate(n_per_class=900)
