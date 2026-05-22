import pygame
import math
from enum import Enum, auto
from typing import Optional, Callable

ROBOT_R   = 16
SPEED     = 2.0
SCAN_DIST = 52
SCAN_TIME = 90

_CORRIDOR_Y    = 329
_CORRIDOR_BAND = 55

C_BODY    = ( 40, 205, 125)
C_OUTLINE = ( 20, 122,  70)
C_EYE     = (255, 255, 255)
C_PUPIL   = ( 18,  18,  18)
C_SCAN    = (255, 220,  50)

STATE_COLORS = {
    "PATROLLING":  ( 40, 205, 125),
    "APPROACHING": (235, 195,  35),
    "SCANNING":    (235, 112,  28),
    "REPORTING":   (210,  42,  42),
    "RETURNING":   ( 80, 160, 230),
}


class RobotState(Enum):
    PATROLLING  = auto()
    APPROACHING = auto()
    SCANNING    = auto()
    REPORTING   = auto()
    RETURNING   = auto()


class Robot:
    def __init__(self, x: float, y: float,
                 patrol_waypoints: list[tuple[int, int]]):
        self.x = float(x)
        self.y = float(y)
        self.patrol_waypoints = patrol_waypoints
        self.wp_index  = 0
        self.state        = RobotState.PATROLLING
        self.target_spot  = None
        self.scan_timer   = 0
        self.scan_callback: Optional[Callable] = None
        self.angle        = 0.0
        self._return_wp: tuple[int, int] | None = None

    def set_corridor_y(self, cy: int):
        global _CORRIDOR_Y
        _CORRIDOR_Y = cy

    def update(self, spots):
        if   self.state == RobotState.PATROLLING:
            self._patrol(); self._check_nearby(spots)
        elif self.state == RobotState.APPROACHING: self._approach()
        elif self.state == RobotState.SCANNING:    self._scan()
        elif self.state == RobotState.REPORTING:   self._report()
        elif self.state == RobotState.RETURNING:   self._return_to_patrol()

    def _patrol(self):
        if not self.patrol_waypoints:
            return
        tx, ty = self.patrol_waypoints[self.wp_index]
        self._move_toward(tx, ty)
        if self._dist(tx, ty) < SPEED + 1:
            self.wp_index = (self.wp_index + 1) % len(self.patrol_waypoints)

    def _approach(self):
        if self.target_spot is None:
            self.state = RobotState.PATROLLING; return
        cx, cy = self.target_spot.scan_approach_point
        self._move_toward(cx, cy)
        if self._dist(cx, cy) <= SCAN_DIST:
            self.state = RobotState.SCANNING
            self.scan_timer = SCAN_TIME

    def _scan(self):
        self.scan_timer -= 1
        if self.scan_timer <= 0:
            self.state = RobotState.REPORTING

    def _report(self):
        if self.target_spot and self.scan_callback:
            self.scan_callback(self.target_spot)
        self.target_spot = None
        self._return_wp = self._nearest_waypoint()
        self.state = RobotState.RETURNING

    def _return_to_patrol(self):
        if self._return_wp is None:
            self.state = RobotState.PATROLLING; return
        tx, ty = self._return_wp
        self._move_toward(tx, ty)
        if self._dist(tx, ty) < SPEED + 2:
            self._return_wp = None
            self.state = RobotState.PATROLLING

    def _check_nearby(self, spots):
        if abs(self.y - _CORRIDOR_Y) > _CORRIDOR_BAND:
            return
        for spot in spots:
            if not spot.needs_scan:
                continue
            cx, cy = spot.scan_approach_point
            if self._dist(cx, cy) < 130:
                self._return_wp = self._nearest_waypoint()
                self.target_spot = spot
                self.state = RobotState.APPROACHING
                break

    def _nearest_waypoint(self) -> tuple[int, int]:
        return min(self.patrol_waypoints,
                   key=lambda wp: math.hypot(wp[0] - self.x, wp[1] - self.y))

    def _move_toward(self, tx: float, ty: float):
        dx, dy = tx - self.x, ty - self.y
        dist   = math.hypot(dx, dy)
        if dist < SPEED:
            self.x, self.y = tx, ty; return
        self.x += (dx / dist) * SPEED
        self.y += (dy / dist) * SPEED
        self.angle = math.degrees(math.atan2(-dy, dx))

    def _dist(self, tx: float, ty: float) -> float:
        return math.hypot(tx - self.x, ty - self.y)

    def draw(self, surface: pygame.Surface):
        ix, iy = int(self.x), int(self.y)
        sc = STATE_COLORS.get(self.state.name, C_BODY)

        if self.state in (RobotState.SCANNING, RobotState.APPROACHING):
            alpha = 120 if self.state == RobotState.SCANNING else 50
            cone  = pygame.Surface((SCAN_DIST * 2, SCAN_DIST * 2), pygame.SRCALPHA)
            pygame.draw.circle(cone, (*C_SCAN, alpha), (SCAN_DIST, SCAN_DIST), SCAN_DIST)
            surface.blit(cone, (ix - SCAN_DIST, iy - SCAN_DIST))

        pygame.draw.circle(surface, sc,        (ix, iy), ROBOT_R)
        pygame.draw.circle(surface, C_OUTLINE, (ix, iy), ROBOT_R, 2)

        rad = math.radians(self.angle)
        ex  = ix + int(math.cos(rad) * 7)
        ey  = iy - int(math.sin(rad) * 7)
        pygame.draw.circle(surface, C_EYE,   (ex, ey), 5)
        pygame.draw.circle(surface, C_PUPIL, (ex, ey), 3)

        try:
            lf = pygame.font.SysFont("consolas", 9)
        except Exception:
            lf = pygame.font.Font(None, 10)
        lbl = lf.render(self.state.name[:4], True, (240, 240, 50))
        surface.blit(lbl, (ix - lbl.get_width() // 2, iy + ROBOT_R + 3))

    @property
    def pos(self) -> tuple[int, int]:
        return (int(self.x), int(self.y))
