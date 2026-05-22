import pygame
from parking import SpotStatus, SpotType
from robot import RobotState

COLOR_PANEL_BG   = (25,  25,  35)
COLOR_PANEL_LINE = (50,  50,  70)
COLOR_TITLE      = (100, 200, 255)
COLOR_WHITE      = (230, 230, 230)
COLOR_GRAY       = (140, 140, 140)
COLOR_GREEN      = (50,  210,  90)
COLOR_RED        = (210,  50,  50)
COLOR_YELLOW     = (240, 210,  40)
COLOR_ORANGE     = (230, 130,  30)
COLOR_CYAN       = ( 80, 220, 220)

PANEL_X = 720
PANEL_W = 280
LOG_MAX = 8


class Dashboard:
    def __init__(self, screen: pygame.Surface, screen_h: int):
        self.screen          = screen
        self.panel           = pygame.Rect(PANEL_X, 0, PANEL_W, screen_h)
        self.violations:     list[str] = []
        self.scan_crop:      pygame.Surface | None = None
        self.scan_result:    str   = ""
        self.scan_confidence: float = 0.0
        self.total_scanned    = 0
        self.total_violation  = 0
        self.scenario_name:  str   = "ORTA IHLAL"
        self._refresh_progress: float = 0.0
        self._refresh_msg:      str   = ""

        try:
            self.font_title = pygame.font.SysFont("segoeui",  16, bold=True)
            self.font_body  = pygame.font.SysFont("consolas", 12)
            self.font_small = pygame.font.SysFont("consolas", 10)
        except Exception:
            self.font_title = pygame.font.Font(None, 18)
            self.font_body  = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 12)

    def add_violation(self, spot_idx: int, plate: str, timestamp: str):
        entry = f"[{timestamp}] Yer {spot_idx:02d} {plate}"
        self.violations.insert(0, entry)
        if len(self.violations) > LOG_MAX:
            self.violations.pop()
        self.total_violation += 1

    def add_scan(self):
        self.total_scanned += 1

    def set_scan_result(self, crop: pygame.Surface | None,
                        result: str, confidence: float = 0.0):
        self.scan_crop       = crop
        self.scan_result     = result
        self.scan_confidence = confidence

    def set_scenario(self, name: str):
        self.scenario_name = name

    def set_refresh_progress(self, progress: float, message: str = ""):
        self._refresh_progress = progress
        self._refresh_msg      = message

    # ── Ana çizim ──────────────────────────────────────────────────────
    def draw(self, robot, spots):
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.panel)
        pygame.draw.line(self.screen, COLOR_PANEL_LINE,
                         (PANEL_X, 0), (PANEL_X, self.panel.h), 2)

        y = 12
        y = self._section_title("OTOPARK ROBOTU", y)
        y = self._stats(spots, y)
        y = self._robot_status(robot, y)
        y = self._scan_preview(y)
        y = self._violation_log(y)
        y = self._scenario_bar(y)
        y = self._legend(y)

    # ── Yardımcı çiziciler ─────────────────────────────────────────────
    def _section_title(self, text: str, y: int) -> int:
        surf = self.font_title.render(text, True, COLOR_TITLE)
        self.screen.blit(surf, (PANEL_X + 10, y))
        pygame.draw.line(self.screen, COLOR_PANEL_LINE,
                         (PANEL_X + 6, y + 20), (PANEL_X + PANEL_W - 6, y + 20), 1)
        return y + 28

    def _sub_title(self, text: str, y: int) -> int:
        surf = self.font_body.render(text, True, COLOR_YELLOW)
        self.screen.blit(surf, (PANEL_X + 10, y))
        return y + 18

    def _line(self, text: str, color, y: int) -> int:
        surf = self.font_body.render(text, True, color)
        self.screen.blit(surf, (PANEL_X + 14, y))
        return y + 16

    def _stats(self, spots, y: int) -> int:
        y = self._sub_title("ISTATISTIK", y)
        total    = len(spots)
        occupied = sum(1 for s in spots if s.is_occupied)
        oran_str = (f"%{self.total_violation/self.total_scanned*100:.0f}"
                    if self.total_scanned else "—")

        y = self._line(f"Toplam yer : {total}", COLOR_WHITE,  y)
        y = self._line(f"Dolu       : {occupied}", COLOR_WHITE, y)
        y = self._line(f"Taranan    : {self.total_scanned}", COLOR_GREEN, y)
        y = self._line(f"Ihlal      : {self.total_violation}  ({oran_str})",
                       COLOR_RED if self.total_violation else COLOR_GREEN, y)
        return y + 4

    def _robot_status(self, robot, y: int) -> int:
        y = self._sub_title("ROBOT DURUMU", y)
        state_colors = {
            RobotState.PATROLLING:  COLOR_GREEN,
            RobotState.APPROACHING: COLOR_YELLOW,
            RobotState.SCANNING:    COLOR_ORANGE,
            RobotState.REPORTING:   COLOR_RED,
            RobotState.RETURNING:   COLOR_CYAN,
        }
        col = state_colors.get(robot.state, COLOR_WHITE)
        y = self._line(f"Durum  : {robot.state.name}", col, y)
        y = self._line(f"Konum  : ({robot.pos[0]:4d}, {robot.pos[1]:4d})", COLOR_GRAY, y)
        if robot.target_spot:
            y = self._line(f"Hedef  : Yer {robot.target_spot.index}", COLOR_YELLOW, y)
        return y + 4

    def _scan_preview(self, y: int) -> int:
        y = self._sub_title("SON TARAMA", y)

        # Büyük önizleme kutusu
        box = pygame.Rect(PANEL_X + 10, y, PANEL_W - 20, 95)
        pygame.draw.rect(self.screen, (12, 12, 22), box, border_radius=4)
        pygame.draw.rect(self.screen, COLOR_PANEL_LINE, box, 1, border_radius=4)

        if self.scan_crop:
            scaled = pygame.transform.scale(self.scan_crop, (box.w - 4, box.h - 4))
            self.screen.blit(scaled, (box.x + 2, box.y + 2))

        y += box.h + 4

        # Sonuç metni
        is_ok    = "OK"    in self.scan_result
        is_ihlal = "IHLAL" in self.scan_result
        res_color = COLOR_GREEN if is_ok else (COLOR_RED if is_ihlal else COLOR_GRAY)
        # Kısa metin (confidence kısmını ayır)
        short_result = self.scan_result.split("%")[0].strip() if "%" in self.scan_result else self.scan_result
        surf = self.font_small.render(short_result or "—", True, res_color)
        self.screen.blit(surf, (PANEL_X + 10, y))
        y += 14

        # YOLO güven skoru çubuğu
        if self.scan_confidence > 0:
            bar_w  = PANEL_W - 20
            fill_w = int(bar_w * self.scan_confidence)
            bar_bg = pygame.Rect(PANEL_X + 10, y, bar_w, 8)
            bar_fg = pygame.Rect(PANEL_X + 10, y, fill_w, 8)
            pygame.draw.rect(self.screen, (40, 40, 55), bar_bg, border_radius=3)
            pygame.draw.rect(self.screen, res_color,    bar_fg, border_radius=3)

            conf_txt = self.font_small.render(
                f"YOLO: %{self.scan_confidence*100:.1f}", True, res_color)
            self.screen.blit(conf_txt, (PANEL_X + 10, y + 10))
            y += 22

        return y + 4

    def _violation_log(self, y: int) -> int:
        y = self._sub_title("IHLAL KAYITLARI", y)
        if not self.violations:
            y = self._line("Henuz ihlal yok.", COLOR_GRAY, y)
        else:
            for entry in self.violations:
                surf = self.font_small.render(entry, True, COLOR_RED)
                self.screen.blit(surf, (PANEL_X + 10, y))
                y += 14
        return y + 4

    def _scenario_bar(self, y: int) -> int:
        pygame.draw.line(self.screen, COLOR_PANEL_LINE,
                         (PANEL_X + 6, y), (PANEL_X + PANEL_W - 6, y), 1)
        y += 6
        surf = self.font_small.render(
            f"Senaryo: {self.scenario_name}", True, COLOR_CYAN)
        self.screen.blit(surf, (PANEL_X + 10, y))
        y += 14
        hint = self.font_small.render("1:Az  2:Orta  3:Cok ihlal", True, COLOR_GRAY)
        self.screen.blit(hint, (PANEL_X + 10, y))
        y += 14

        # Yenileme geri sayım çubuğu
        if self._refresh_progress > 0:
            bar_w  = PANEL_W - 20
            fill_w = int(bar_w * self._refresh_progress)
            pygame.draw.rect(self.screen, (40, 40, 55),
                             pygame.Rect(PANEL_X + 10, y, bar_w, 7), border_radius=3)
            pygame.draw.rect(self.screen, COLOR_CYAN,
                             pygame.Rect(PANEL_X + 10, y, fill_w, 7), border_radius=3)
            y += 10
            msg = self.font_small.render(self._refresh_msg, True, COLOR_CYAN)
            self.screen.blit(msg, (PANEL_X + 10, y))
            y += 14

        return y + 2

    def _legend(self, y: int) -> int:
        pygame.draw.line(self.screen, COLOR_PANEL_LINE,
                         (PANEL_X + 6, y), (PANEL_X + PANEL_W - 6, y), 1)
        y += 6
        items = [
            ("Engelli yer", (30, 80, 160)),
            ("Ihlal",       (200, 30, 30)),
            ("Temiz",       (30, 200, 80)),
        ]
        for label, color in items:
            pygame.draw.rect(self.screen, color,
                             pygame.Rect(PANEL_X + 10, y + 2, 12, 12), border_radius=2)
            surf = self.font_small.render(label, True, COLOR_WHITE)
            self.screen.blit(surf, (PANEL_X + 26, y))
            y += 16
        return y
