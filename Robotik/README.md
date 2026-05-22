# ParkGuard
### Smart Parking Disabled Vehicle Control System
### Akıllı Otopark Engelli Araç Kontrol Sistemi

---

## English

### Overview

A robotics course project that simulates an autonomous robot patrolling a parking lot to detect whether vehicles parked in disabled spots are authorized. The robot uses YOLO11 to classify license plates as disabled or normal, logs all scan results to CSV, and generates a session summary on exit.

### Features

- 2D top-down parking lot simulation with 18 spots (6 disabled, randomly placed each round)
- Vehicles with Turkish license plates — disabled vehicles carry a blue ♿ emblem on the plate
- Autonomous patrol robot with a 5-state FSM: `PATROLLING → APPROACHING → SCANNING → REPORTING → RETURNING`
- YOLO11s model trained on 1800 synthetic plate images (mAP50 = 0.995)
- Real-time dashboard: scan preview, YOLO confidence bar, violation log, scenario selector
- Auto-refresh: after all disabled spots are scanned, vehicles and spot positions renew automatically
- CSV violation log and session summary saved on exit

### Project Structure

```
D:\Robotik\
├── simulation.py        Main entry point
├── parking.py           Parking lot, spots, and spot logic
├── vehicle.py           Vehicle sprite and license plate rendering
├── robot.py             Patrol robot with FSM
├── detector.py          YOLO11 inference and plate preview renderer
├── ui.py                Right-panel dashboard
├── logger.py            CSV logging and session summary
├── generate_dataset.py  Synthetic training data generator
├── train.py             YOLO11 training script
├── dataset/             Training images and labels
├── models/
│   └── best.pt          Trained YOLO11s model
├── violations.csv        Per-scan log (updated live)
└── session_summary.txt   End-of-session report
```

### Requirements

```
Python 3.10+
pygame >= 2.5
ultralytics >= 8.3  (YOLO11)
opencv-python >= 4.9
numpy >= 1.26
Pillow >= 10.0
torch >= 2.0 (CUDA recommended)
```

Install:
```bash
pip install -r requirements.txt
```

### Running

```bash
cd D:\Robotik
python simulation.py
```

### Controls

| Key | Action |
|-----|--------|
| `1` | Low violation scenario (85% of disabled spots have authorized vehicles) |
| `2` | Medium violation scenario (45%) |
| `3` | High violation scenario (8%) |
| `R` | Refresh vehicles (keep current disabled spot layout) |
| `SPACE` | Add a test violation to an empty disabled spot |
| `ESC` | Exit and save session summary |

### Re-training the Model

```bash
python generate_dataset.py   # generates 1800 synthetic images
python train.py              # trains YOLO11s, saves models/best.pt
```

### Output Files

| File | Description |
|------|-------------|
| `violations.csv` | Date, time, spot index, plate, result, YOLO confidence for every scan |
| `session_summary.txt` | Total scanned / violations / duration — written when simulation exits |

---

## Türkçe

### Genel Bakış

Robotik dersi projesi. Bir otopark simülasyonunda gezici bir robot, engelli park yerlerine park eden araçların yetkili olup olmadığını denetler. Robot, YOLO11 ile plakaları engelli/normal olarak sınıflandırır; tüm tarama sonuçları CSV'ye kaydedilir ve çıkışta oturum özeti oluşturulur.

### Özellikler

- 18 park yerli 2D top-down otopark simülasyonu (6 engelli yer, her turda rastgele konumlanır)
- Türk plakasına sahip araçlar — engelli araçlar plakada mavi ♿ amblemi taşır
- 5 durumlu FSM ile özerk devriye robotu: `PATROL → APPROACH → SCAN → REPORT → RETURN`
- 1800 sentetik plaka görseli ile eğitilmiş YOLO11s modeli (mAP50 = 0.995)
- Gerçek zamanlı dashboard: tarama önizleme, YOLO güven çubuğu, ihlal günlüğü, senaryo seçici
- Otomatik yenileme: tüm engelli spotlar tarandıktan sonra araçlar ve spot konumları yenilenir
- Çıkışta CSV ihlal günlüğü ve oturum özeti kaydedilir

### Proje Yapısı

```
D:\Robotik\
├── simulation.py        Ana giriş noktası
├── parking.py           Otopark, spotlar ve spot mantığı
├── vehicle.py           Araç sprite ve plaka render
├── robot.py             FSM'li devriye robotu
├── detector.py          YOLO11 çıkarımı ve plaka önizleme
├── ui.py                Sağ panel dashboard
├── logger.py            CSV kayıt ve oturum özeti
├── generate_dataset.py  Sentetik eğitim verisi üretici
├── train.py             YOLO11 eğitim scripti
├── dataset/             Eğitim görselleri ve etiketleri
├── models/
│   └── best.pt          Eğitilmiş YOLO11s modeli
├── violations.csv        Tarama kayıtları (canlı güncellenir)
└── session_summary.txt   Oturum sonu raporu
```

### Gereksinimler

```
Python 3.10+
pygame >= 2.5
ultralytics >= 8.3  (YOLO11)
opencv-python >= 4.9
numpy >= 1.26
Pillow >= 10.0
torch >= 2.0 (CUDA önerilir)
```

Kurulum:
```bash
pip install -r requirements.txt
```

### Çalıştırma

```bash
cd D:\Robotik
python simulation.py
```

### Kontroller

| Tuş | Eylem |
|-----|-------|
| `1` | Az ihlal senaryosu (engelli spotların %85'inde yetkili araç) |
| `2` | Orta ihlal senaryosu (%45) |
| `3` | Çok ihlal senaryosu (%8) |
| `R` | Araçları yenile (engelli spot konumları korunur) |
| `SPACE` | Boş bir engelli spota test ihlali ekle |
| `ESC` | Çıkış ve oturum özetini kaydet |

### Modeli Yeniden Eğitme

```bash
python generate_dataset.py   # 1800 sentetik görsel üretir
python train.py              # YOLO11s eğitir, models/best.pt kaydeder
```

### Çıktı Dosyaları

| Dosya | Açıklama |
|-------|----------|
| `violations.csv` | Her tarama için tarih, saat, spot no, plaka, sonuç, YOLO güven skoru |
| `session_summary.txt` | Toplam taranan / ihlal / süre — simülasyon kapanınca yazılır |

### Teknik Detaylar

| Bileşen | Detay |
|---------|-------|
| Simülasyon | Pygame 2D, 60 FPS |
| Tespit modeli | YOLO11s, imgsz=160 |
| Eğitim verisi | 1800 sentetik görsel (900 engelli + 900 normal), Pillow ile üretildi |
| Eğitim | 21 epoch, RTX 3050 Ti, ~2 dakika |
| mAP50 | 0.995 |
| Robot FSM | 5 durum: PATROLLING, APPROACHING, SCANNING, REPORTING, RETURNING |
