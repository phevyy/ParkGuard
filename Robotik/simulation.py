import pygame
import random
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from parking  import (ParkingLot, SpotType, SpotStatus,
                      SPOT_W, SPOT_H, SPOT_MARGIN, ROW_GAP)
from vehicle  import Vehicle, VEHICLE_W, VEHICLE_H
from robot    import Robot, RobotState
from detector import Detector
from ui       import Dashboard
import logger

SIM_W  = 720
PNL_W  = 280
WIDTH  = SIM_W + PNL_W
HEIGHT = 680
FPS    = 60
TITLE  = "Otopark Engelli Arac Kontrol Sistemi"

C_BG   = (38, 38, 38)
C_ROAD = (52, 52, 52)
C_CURB = (78, 78, 78)

SCENARIOS = {
    pygame.K_1: ("AZ IHLAL",   0.78, 0.85),
    pygame.K_2: ("ORTA IHLAL", 0.78, 0.45),
    pygame.K_3: ("COK IHLAL",  0.78, 0.08),
}
_current_scenario = ("ORTA IHLAL", 0.78, 0.45)

REFRESH_DELAY = 180


def timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M:%S")


def place_vehicles(lot: ParkingLot, occ: float, dis: float):
    for spot in lot.spots:
        spot.vehicle = None
        spot.status  = SpotStatus.EMPTY
        if random.random() > occ:
            continue
        is_dis = (random.random() < dis) if spot.spot_type == SpotType.DISABLED else False
        spot.vehicle = Vehicle(is_disabled=is_dis)
        spot.status  = SpotStatus.UNSCANNED


def build_patrol(lot: ParkingLot, margin: int = 22) -> list[tuple[int, int]]:
    ox      = lot.origin_x
    block_w = lot.COLS * (SPOT_W + SPOT_MARGIN)
    block_h = lot.ROWS * (SPOT_H + SPOT_MARGIN)
    cy      = lot.corridor_y()
    left    = ox - margin
    right   = ox + block_w + margin
    top     = lot.origin_y - margin
    bot     = lot.origin_y + 2 * block_h + ROW_GAP + margin
    return [
        (left, cy), (left, top), (right, top),
        (right, cy), (right, bot), (left, bot),
    ]


def draw_background(surface: pygame.Surface, lot: ParkingLot):
    surface.fill(C_BG)
    ox      = lot.origin_x
    block_w = lot.COLS  * (SPOT_W + SPOT_MARGIN)
    block_h = lot.ROWS  * (SPOT_H + SPOT_MARGIN)
    road    = pygame.Rect(ox - 55, lot.origin_y - 55,
                          block_w + 110, 2 * block_h + ROW_GAP + 110)
    pygame.draw.rect(surface, C_ROAD, road, border_radius=8)
    pygame.draw.rect(surface, C_CURB, road, 3,  border_radius=8)
    cy = lot.corridor_y()
    pygame.draw.line(surface, (175, 170, 130),
                     (ox - 45, cy), (ox + block_w + 45, cy), 1)


def main():
    global _current_scenario

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock  = pygame.time.Clock()

    try:
        font_ui   = pygame.font.SysFont("segoeui",       14)
        font_big  = pygame.font.SysFont("segoeui",       20, bold=True)
        font_spot = pygame.font.SysFont("segoeuisymbol", 18)
    except Exception:
        font_ui   = pygame.font.Font(None, 16)
        font_big  = pygame.font.Font(None, 22)
        font_spot = pygame.font.Font(None, 18)

    logger.init(clear=True)

    lot = ParkingLot(origin_x=68, origin_y=45)
    lot.randomize_disabled(random.randint(3, 5))
    sname, occ, dis = _current_scenario
    place_vehicles(lot, occ, dis)

    waypoints = build_patrol(lot)
    robot     = Robot(x=waypoints[0][0], y=waypoints[0][1],
                      patrol_waypoints=waypoints)
    robot.set_corridor_y(lot.corridor_y())

    detector  = Detector(screen, model_path="D:/Robotik/models/best.pt")
    dashboard = Dashboard(screen, HEIGHT)
    dashboard.set_scenario(sname)

    def on_scan(spot):
        result = detector.scan(spot)
        spot.status = result
        conf   = detector.last_confidence
        dashboard.add_scan()
        dashboard.set_scan_result(detector.last_crop, detector.last_result, conf)
        plate      = spot.vehicle.plate_text if spot.vehicle else "?"
        ts         = timestamp()
        result_str = "TEMIZ" if result == SpotStatus.CLEAR else "IHLAL"
        logger.log_scan(spot.index, plate, result_str, conf)
        if result == SpotStatus.VIOLATION:
            dashboard.add_violation(spot.index, plate, ts)

    robot.scan_callback = on_scan

    refresh_countdown = -1

    def reset_round():
        nonlocal refresh_countdown
        n_dis = random.randint(3, 5)
        lot.randomize_disabled(n_dis)
        sname, occ, dis = _current_scenario
        place_vehicles(lot, occ, dis)
        Vehicle._id_counter = 0
        robot.state        = RobotState.PATROLLING
        robot.target_spot  = None
        robot._return_wp   = None
        refresh_countdown  = -1
        print(f"[SIM] Yeni tur — {n_dis} engelli yer, yeni araçlar.")

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key in SCENARIOS:
                    sname, occ, dis = SCENARIOS[event.key]
                    _current_scenario = (sname, occ, dis)
                    lot.randomize_disabled(random.randint(3, 5))
                    place_vehicles(lot, occ, dis)
                    Vehicle._id_counter = 0
                    robot.state = RobotState.PATROLLING
                    robot.target_spot = None
                    robot._return_wp = None
                    refresh_countdown = -1
                    dashboard.set_scenario(sname)
                    dashboard.set_refresh_progress(0.0, "")
                    print(f"[SIM] Senaryo: {sname}")

                elif event.key == pygame.K_r:
                    sname, occ, dis = _current_scenario
                    place_vehicles(lot, occ, dis)
                    Vehicle._id_counter = 0
                    print("[SIM] Araçlar yenilendi.")

                elif event.key == pygame.K_SPACE:
                    for spot in lot.spots:
                        if not spot.is_occupied and spot.spot_type == SpotType.DISABLED:
                            spot.vehicle = Vehicle(is_disabled=False)
                            spot.status  = SpotStatus.UNSCANNED
                            print(f"[SIM] Yer {spot.index}: test ihlali.")
                            break

        robot.update(lot.spots)

        disabled_spots    = [s for s in lot.spots if s.spot_type == SpotType.DISABLED]
        occupied_disabled = [s for s in disabled_spots if s.is_occupied]
        all_scanned = (occupied_disabled and
                       all(s.status != SpotStatus.UNSCANNED for s in occupied_disabled))

        if all_scanned and refresh_countdown == -1:
            refresh_countdown = REFRESH_DELAY

        if refresh_countdown > 0:
            refresh_countdown -= 1
            dashboard.set_refresh_progress(
                1.0 - refresh_countdown / REFRESH_DELAY,
                f"Yeni tur... {refresh_countdown // FPS + 1}s"
            )
        elif refresh_countdown == 0:
            reset_round()
            dashboard.set_refresh_progress(0.0, "")

        draw_background(screen, lot)
        lot.draw(screen, font_spot)

        for spot in lot.spots:
            if spot.vehicle:
                vx = spot.rect.x + (spot.rect.w - VEHICLE_W) // 2
                vy = spot.rect.y + (spot.rect.h - VEHICLE_H) // 2
                spot.vehicle.draw(screen, vx, vy)

        robot.draw(screen)
        dashboard.draw(robot, lot.spots)

        title = font_big.render(TITLE, True, (205, 205, 205))
        screen.blit(title, (10, HEIGHT - 28))
        hint = font_ui.render(
            "1/2/3:Senaryo  R:Yenile  SPACE:Test  ESC:Cikis",
            True, (80, 80, 92))
        screen.blit(hint, (10, HEIGHT - 14))

        pygame.display.flip()

    sname, _, _ = _current_scenario
    logger.save_summary(dashboard.total_scanned,
                        dashboard.total_violation,
                        sname)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
