import pygame
import random
from dataclasses import dataclass
from enum import Enum

SPOT_W      = 62
SPOT_H      = 82
SPOT_MARGIN =  6
ROW_GAP     = 40

COLOR_NORMAL_BG   = (58,  58,  58)
COLOR_DISABLED_BG = (28,  72, 155)
COLOR_OUTLINE     = (100, 100, 100)
COLOR_VIOLATION   = (200,  30,  30)
COLOR_CLEAR       = ( 30, 200,  80)
COLOR_DISABLED_SYM= (180, 210, 255)


class SpotType(Enum):
    NORMAL   = "normal"
    DISABLED = "disabled"


class SpotStatus(Enum):
    EMPTY     = "empty"
    CLEAR     = "clear"
    VIOLATION = "violation"
    UNSCANNED = "unscanned"


@dataclass
class ParkingSpot:
    index:     int
    spot_type: SpotType
    rect:      pygame.Rect
    vehicle:   object = None
    status:    SpotStatus = SpotStatus.EMPTY

    @property
    def is_occupied(self) -> bool:
        return self.vehicle is not None

    @property
    def needs_scan(self) -> bool:
        return (self.is_occupied
                and self.spot_type == SpotType.DISABLED
                and self.status    == SpotStatus.UNSCANNED)

    @property
    def screen_center(self) -> tuple[int, int]:
        return self.rect.center

    @property
    def scan_approach_point(self) -> tuple[int, int]:
        cx = self.rect.centerx
        if self.index < 9:
            return (cx, self.rect.bottom + 16)
        else:
            return (cx, self.rect.top - 16)


class ParkingLot:
    COLS = 3
    ROWS = 3
    DISABLED_CANDIDATES = list(range(6, 12))

    def __init__(self, origin_x: int, origin_y: int):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.spots: list[ParkingSpot] = []
        self._build()

    def _build(self):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                idx  = row * self.COLS + col
                x    = self.origin_x + col * (SPOT_W + SPOT_MARGIN)
                y    = self.origin_y + row * (SPOT_H + SPOT_MARGIN)
                rect = pygame.Rect(x, y, SPOT_W, SPOT_H)
                self.spots.append(ParkingSpot(index=idx, spot_type=SpotType.NORMAL, rect=rect))

        block_h  = self.ROWS * (SPOT_H + SPOT_MARGIN)
        second_y = self.origin_y + block_h + ROW_GAP
        for row in range(self.ROWS):
            for col in range(self.COLS):
                idx  = self.ROWS * self.COLS + row * self.COLS + col
                x    = self.origin_x + col * (SPOT_W + SPOT_MARGIN)
                y    = second_y + row * (SPOT_H + SPOT_MARGIN)
                rect = pygame.Rect(x, y, SPOT_W, SPOT_H)
                self.spots.append(ParkingSpot(index=idx, spot_type=SpotType.NORMAL, rect=rect))

    def randomize_disabled(self, count: int = 4):
        for spot in self.spots:
            spot.spot_type = SpotType.NORMAL
        chosen = random.sample(self.DISABLED_CANDIDATES,
                               min(count, len(self.DISABLED_CANDIDATES)))
        for idx in chosen:
            self.spots[idx].spot_type = SpotType.DISABLED

    def corridor_y(self) -> int:
        block_h = self.ROWS * (SPOT_H + SPOT_MARGIN)
        return self.origin_y + block_h + ROW_GAP // 2

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        for spot in self.spots:
            self._draw_spot(surface, font, spot)

    def _draw_spot(self, surface, font, spot: ParkingSpot):
        r  = spot.rect
        bg = COLOR_DISABLED_BG if spot.spot_type == SpotType.DISABLED else COLOR_NORMAL_BG
        pygame.draw.rect(surface, bg, r, border_radius=4)

        if spot.status == SpotStatus.VIOLATION:
            pygame.draw.rect(surface, COLOR_VIOLATION, r, 3, border_radius=4)
        elif spot.status == SpotStatus.CLEAR:
            pygame.draw.rect(surface, COLOR_CLEAR, r, 3, border_radius=4)
        else:
            pygame.draw.rect(surface, COLOR_OUTLINE, r, 1, border_radius=4)

        if spot.spot_type == SpotType.DISABLED:
            sym = font.render("♿", True, COLOR_DISABLED_SYM)
            sym.set_alpha(65)
            surface.blit(sym, sym.get_rect(center=r.center))

        num = font.render(str(spot.index), True, (120, 120, 120))
        surface.blit(num, (r.x + 4, r.y + 4))
