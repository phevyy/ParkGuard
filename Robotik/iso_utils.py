"""
İzometrik koordinat yardımcıları.
Formül: sx = OX + (col - row) * TILE_W/2
        sy = OY + (col + row) * TILE_H/2
"""
import pygame

TILE_W    = 100   # izometrik döşeme genişliği
TILE_H    =  50   # izometrik döşeme yüksekliği (= TILE_W / 2)
VEHICLE_H =  42   # araç toplam kutu yüksekliği (piksel)
ORIGIN_X  = 465   # ekran kökeni — (0,0) döşemesinin tepe noktası
ORIGIN_Y  = 148


def to_screen(col: float, row: float) -> tuple[int, int]:
    return (
        ORIGIN_X + int((col - row) * (TILE_W >> 1)),
        ORIGIN_Y + int((col + row) * (TILE_H >> 1)),
    )


def tile_pts(col: float, row: float) -> list[tuple[int, int]]:
    """Bir döşemenin 4 köşe noktası (üst, sağ, alt, sol)."""
    tx, ty = to_screen(col, row)
    hw, hh = TILE_W >> 1, TILE_H >> 1
    return [(tx, ty), (tx + hw, ty + hh), (tx, ty + TILE_H), (tx - hw, ty + hh)]


def box_faces(col: float, row: float,
              height: int) -> tuple[list, list, list]:
    """(üst yüz, sol yüz, sağ yüz) köşe listelerini döndürür."""
    tx, ty = to_screen(col, row)
    hw, hh = TILE_W >> 1, TILE_H >> 1
    h = height
    top   = [(tx, ty - h), (tx + hw, ty + hh - h),
             (tx, ty + TILE_H - h), (tx - hw, ty + hh - h)]
    left  = [(tx - hw, ty + hh - h), (tx, ty + TILE_H - h),
             (tx, ty + TILE_H), (tx - hw, ty + hh)]
    right = [(tx, ty + TILE_H - h), (tx + hw, ty + hh - h),
             (tx + hw, ty + hh), (tx, ty + TILE_H)]
    return top, left, right


def shade(color: tuple, factor: float) -> tuple:
    return tuple(max(0, min(255, int(c * factor))) for c in color[:3])


def lerp_pt(a: tuple, b: tuple, t: float) -> tuple[int, int]:
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t))


def draw_tile(surface: pygame.Surface, col: float, row: float,
              color: tuple, outline: tuple | None = None, ow: int = 1):
    pts = tile_pts(col, row)
    pygame.draw.polygon(surface, color, pts)
    if outline:
        pygame.draw.polygon(surface, outline, pts, ow)


def draw_box(surface: pygame.Surface, col: float, row: float,
             height: int, color: tuple,
             outline: tuple | None = None) -> tuple[list, list, list]:
    """İzometrik kutu çizer; (top, left, right) yüz noktalarını döndürür."""
    top, left, right = box_faces(col, row, height)
    lc = shade(color, 0.58)
    rc = shade(color, 0.76)
    pygame.draw.polygon(surface, lc,    left)
    pygame.draw.polygon(surface, rc,    right)
    pygame.draw.polygon(surface, color, top)
    if outline:
        for pts in (left, right, top):
            pygame.draw.polygon(surface, outline, pts, 1)
    return top, left, right
