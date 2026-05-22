import csv
import datetime
import pathlib

CSV_PATH     = pathlib.Path("D:/Robotik/violations.csv")
SUMMARY_PATH = pathlib.Path("D:/Robotik/session_summary.txt")

_session_start: datetime.datetime | None = None


def init(clear: bool = False):
    global _session_start
    _session_start = datetime.datetime.now()
    if clear or not CSV_PATH.exists():
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["Tarih", "Saat", "Yer No", "Plaka", "Sonuc", "YOLO Skoru"]
            )


def log_scan(spot_idx: int, plate: str, result: str, confidence: float):
    now = datetime.datetime.now()
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            spot_idx,
            plate,
            result,
            f"{confidence:.3f}",
        ])


def save_summary(total_scanned: int, total_violation: int, scenario: str):
    now  = datetime.datetime.now()
    dur  = (now - _session_start).seconds if _session_start else 0
    mins, secs = divmod(dur, 60)
    temiz = total_scanned - total_violation
    oran  = (total_violation / total_scanned * 100) if total_scanned else 0

    lines = [
        "=" * 38,
        "   OTOPARK KONTROL — OTURUM OZETI",
        "=" * 38,
        f"Tarih/Saat : {now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Sure       : {mins}dk {secs}sn",
        f"Senaryo    : {scenario}",
        "-" * 38,
        f"Taranan    : {total_scanned}",
        f"Temiz      : {temiz}",
        f"Ihlal      : {total_violation}",
        f"Ihlal Orani: %{oran:.1f}",
        "=" * 38,
        f"CSV        : {CSV_PATH}",
    ]
    text = "\n".join(lines)
    SUMMARY_PATH.write_text(text, encoding="utf-8")
    print("\n" + text)
