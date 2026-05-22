import pygame
import numpy as np
from parking import SpotStatus

PREV_W, PREV_H = 258, 90
YOLO_W, YOLO_H = 160, 80


class Detector:
    def __init__(self, screen: pygame.Surface, model_path: str | None = None):
        self.screen           = screen
        self.model            = None
        self.last_crop:       pygame.Surface | None = None
        self.last_result:     str   = ""
        self.last_confidence: float = 0.0

        if model_path:
            self._load_model(model_path)

    def _load_model(self, path: str):
        try:
            from ultralytics import YOLO
            self.model = YOLO(path)
            print(f"[Detector] YOLO11 yuklendi: {path}")
        except Exception as e:
            print(f"[Detector] Model yuklenemedi ({e}), mock mod.")

    def scan(self, spot) -> SpotStatus:
        if spot.vehicle is None:
            return SpotStatus.EMPTY
        self.last_crop = self._render_preview(spot)
        return self._yolo_scan(spot) if self.model else self._mock_scan(spot)

    def _mock_scan(self, spot) -> SpotStatus:
        is_dis               = spot.vehicle.is_disabled
        self.last_confidence = 1.0
        self.last_result     = "ENGELLI PLAKA [OK]" if is_dis else "NORMAL PLAKA [!] IHLAL"
        result               = SpotStatus.CLEAR if is_dis else SpotStatus.VIOLATION
        print(f"[Detector] Yer {spot.index}: {self.last_result}")
        return result

    def _yolo_scan(self, spot) -> SpotStatus:
        small = self._capture_screen(spot)
        arr   = pygame.surfarray.array3d(small)
        arr   = np.transpose(arr, (1, 0, 2))

        from PIL import Image as PILImage
        arr_in = np.array(PILImage.fromarray(arr).resize((YOLO_W, YOLO_H)))

        results = self.model(arr_in, verbose=False, imgsz=YOLO_W)

        best_cls, best_conf = "normal_plate", 0.0
        for r in results:
            for box in r.boxes:
                c = float(box.conf[0])
                if c > best_conf:
                    best_conf = c
                    best_cls  = self.model.names[int(box.cls[0])]

        self.last_confidence = best_conf

        if best_cls == "disabled_plate":
            self.last_result = f"ENGELLI PLAKA [OK] %{best_conf*100:.1f}"
            return SpotStatus.CLEAR
        self.last_result = f"NORMAL PLAKA [!] IHLAL %{best_conf*100:.1f}"
        return SpotStatus.VIOLATION

    def _render_preview(self, spot) -> pygame.Surface:
        from PIL import Image, ImageDraw, ImageFont
        import os

        vehicle = spot.vehicle
        bc      = vehicle.body_color

        img  = Image.new("RGB", (PREV_W, PREV_H), color=bc)
        draw = ImageDraw.Draw(img)

        PW, PH = 180, 42
        EMBL_W = 34
        px     = (PREV_W - PW) // 2
        py     = (PREV_H - PH) // 2

        draw.rectangle([px, py, px + PW - 1, py + PH - 1],
                       fill=(248, 248, 248), outline=(80, 80, 80), width=2)

        def load_font(name, size):
            p = f"C:/Windows/Fonts/{name}"
            return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

        pfont  = load_font("consola.ttf",  20)
        symfnt = load_font("seguisym.ttf", 22)

        if vehicle.is_disabled:
            draw.rectangle([px + 2, py + 2, px + EMBL_W - 2, py + PH - 2],
                           fill=(28, 108, 225))
            try:
                draw.text((px + EMBL_W // 2, py + PH // 2),
                          "♿", font=symfnt, fill=(255, 255, 255), anchor="mm")
            except Exception:
                draw.text((px + 4, py + 10), "E", font=pfont, fill=(255, 255, 255))

            num_cx = px + EMBL_W + (PW - EMBL_W) // 2
            num    = vehicle.plate_text.lstrip("E") if vehicle.plate_text.startswith("E") else vehicle.plate_text
            draw.text((num_cx, py + PH // 2), num[-6:], font=pfont,
                      fill=(15, 15, 15), anchor="mm")
        else:
            draw.text((px + PW // 2, py + PH // 2),
                      vehicle.plate_text[-6:], font=pfont,
                      fill=(15, 15, 15), anchor="mm")

        arr  = np.array(img)
        surf = pygame.surfarray.make_surface(arr.transpose(1, 0, 2))
        return surf

    def _capture_screen(self, spot) -> pygame.Surface:
        from vehicle import VEHICLE_W, VEHICLE_H, PLATE_W, PLATE_H
        r   = spot.rect
        vx  = r.x + (r.w - VEHICLE_W) // 2
        vy  = r.y + (r.h - VEHICLE_H) // 2
        px  = vx + (VEHICLE_W - PLATE_W) // 2
        py  = vy + VEHICLE_H - 19
        pad = 10
        region = pygame.Rect(px - pad, py - pad,
                             PLATE_W + pad * 2, PLATE_H + pad * 2)
        safe = region.clip(pygame.Rect(0, 0,
                                       self.screen.get_width(),
                                       self.screen.get_height()))
        if safe.width < 4 or safe.height < 4:
            return pygame.Surface((10, 10))
        crop = pygame.Surface((safe.w, safe.h))
        crop.blit(self.screen, (0, 0), safe)
        return crop
