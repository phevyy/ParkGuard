import pygame
import random

VEHICLE_W = 50
VEHICLE_H = 76
PLATE_W   = 46
PLATE_H   = 13
EMBLEM_W  = 11

BODY_COLORS = [
    (185,  50,  50), (50, 105, 185), (55, 160,  55),
    (200, 162,  32), (158,  78, 182), (205, 205, 205),
    ( 82,  82,  82), (202, 122,  40), ( 40, 152, 170),
]
C_PLATE_NRM  = (248, 248, 248)
C_PLATE_DIS  = ( 28, 108, 225)
C_TEXT_NRM   = ( 12,  12,  12)
C_TEXT_DIS   = (238, 243, 255)
C_WINDOW     = (140, 190, 220)
C_WINDOW_DRK = ( 80, 128, 158)


class Vehicle:
    _id_counter = 0

    def __init__(self, is_disabled: bool = False, body_color=None):
        Vehicle._id_counter += 1
        self.vehicle_id  = Vehicle._id_counter
        self.is_disabled = is_disabled
        self.body_color  = body_color or random.choice(BODY_COLORS)
        self.plate_text  = self._gen_plate()
        self.surface     = self._render()

    def _gen_plate(self) -> str:
        city = random.randint(1, 81)
        lets = "".join(random.choices("ABCDEFGHJKLMNPRSTUVYZ", k=2))
        nums = random.randint(100, 999)
        pref = "E" if self.is_disabled else ""
        return f"{pref}{city}{lets}{nums}"

    def _render(self) -> pygame.Surface:
        surf = pygame.Surface((VEHICLE_W, VEHICLE_H), pygame.SRCALPHA)
        bc   = self.body_color

        body = pygame.Rect(2, 2, VEHICLE_W - 4, VEHICLE_H - 4)
        pygame.draw.rect(surf, bc, body, border_radius=8)
        pygame.draw.rect(surf, (28, 28, 28), body, 2, border_radius=8)

        win_t = pygame.Rect(8, 10, VEHICLE_W - 16, 20)
        pygame.draw.rect(surf, C_WINDOW,     win_t, border_radius=4)
        pygame.draw.rect(surf, C_WINDOW_DRK, win_t, 1, border_radius=4)

        win_b = pygame.Rect(8, VEHICLE_H - 32, VEHICLE_W - 16, 18)
        pygame.draw.rect(surf, C_WINDOW,     win_b, border_radius=4)
        pygame.draw.rect(surf, C_WINDOW_DRK, win_b, 1, border_radius=4)

        for wx, wy in [(2, 14), (VEHICLE_W - 8, 14),
                       (2, VEHICLE_H - 30), (VEHICLE_W - 8, VEHICLE_H - 30)]:
            pygame.draw.rect(surf, (18, 18, 18),
                             pygame.Rect(wx, wy, 6, 16), border_radius=3)

        px = (VEHICLE_W - PLATE_W) // 2
        py = VEHICLE_H - 19
        pr = pygame.Rect(px, py, PLATE_W, PLATE_H)
        pygame.draw.rect(surf, C_PLATE_NRM, pr, border_radius=2)
        pygame.draw.rect(surf, (75, 75, 75),  pr, 1, border_radius=2)

        try:
            pfont   = pygame.font.SysFont("consolas", 7, bold=True)
            symfont = pygame.font.SysFont("segoeuisymbol", 7)
        except Exception:
            pfont   = pygame.font.Font(None, 8)
            symfont = pfont

        if self.is_disabled:
            emb = pygame.Rect(px + 1, py + 1, EMBLEM_W, PLATE_H - 2)
            pygame.draw.rect(surf, C_PLATE_DIS, emb, border_radius=1)
            sym = symfont.render("♿", True, (255, 255, 255))
            surf.blit(sym, sym.get_rect(center=emb.center))
            text_rect = pygame.Rect(px + EMBLEM_W + 2, py,
                                    PLATE_W - EMBLEM_W - 3, PLATE_H)
            short = self.plate_text.lstrip("E")[-5:]
            ptxt  = pfont.render(short, True, C_TEXT_NRM)
            surf.blit(ptxt, ptxt.get_rect(center=text_rect.center))
        else:
            short = self.plate_text[-5:]
            ptxt  = pfont.render(short, True, C_TEXT_NRM)
            surf.blit(ptxt, ptxt.get_rect(center=pr.center))

        return surf

    def draw(self, surface: pygame.Surface, x: int, y: int):
        surface.blit(self.surface, (x, y))
