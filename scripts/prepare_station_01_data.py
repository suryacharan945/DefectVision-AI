"""
DefectVision AI — Prepare Station 01 Target-Domain Dataset
Generates target-domain camera acquisition frames for Station 01 optical inspection.
Simulates realistic station conditions:
- Stationary conveyor positioning jitter (+/- 8 px)
- Station LED backlight illumination fluctuation (+/- 4%)
- Camera sensor thermal noise
- Mechanical guide angle jitter (+/- 0.5 deg)
"""

import os
import cv2
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOMINAL_BOTTLE = os.path.join(
    PROJECT_ROOT, "release", "portfolio_handover", "assets", "04_genuine_specimen_raw_bottle_nominal.png"
)
DEFECTIVE_BOTTLE = os.path.join(
    PROJECT_ROOT, "release", "portfolio_handover", "assets", "01_genuine_specimen_raw_bottle_defective.png"
)

OUT_DIR = os.path.join(PROJECT_ROOT, "data", "station_01")
TRAIN_NORMAL_DIR = os.path.join(OUT_DIR, "train_normal")
VAL_NORMAL_DIR = os.path.join(OUT_DIR, "val_normal")
VAL_DEFECT_DIR = os.path.join(OUT_DIR, "val_defect")


def apply_station_acquisition_jitter(img, dx=0, dy=0, brightness=1.0, angle=0.0, noise_sigma=0.0):
    h, w = img.shape[:2]
    # 1. Translation & Rotation
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    M[0, 2] += dx
    M[1, 2] += dy
    jittered = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    # 2. Illumination scaling
    jittered = np.clip(jittered.astype(np.float32) * brightness, 0, 255).astype(np.uint8)

    # 3. Sensor noise
    if noise_sigma > 0:
        noise = np.random.normal(0, noise_sigma, jittered.shape).astype(np.float32)
        jittered = np.clip(jittered.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return jittered


def generate_station_data():
    os.makedirs(TRAIN_NORMAL_DIR, exist_ok=True)
    os.makedirs(VAL_NORMAL_DIR, exist_ok=True)
    os.makedirs(VAL_DEFECT_DIR, exist_ok=True)

    nom_img = cv2.imread(NOMINAL_BOTTLE)
    if nom_img is None:
        raise FileNotFoundError(f"Missing nominal bottle asset at {NOMINAL_BOTTLE}")

    def_img = cv2.imread(DEFECTIVE_BOTTLE)
    if def_img is None:
        raise FileNotFoundError(f"Missing defective bottle asset at {DEFECTIVE_BOTTLE}")

    rng = np.random.RandomState(101)

    # 1. Training Normal (25 images)
    print("Generating 25 Station 01 normal training captures...")
    for i in range(25):
        dx = int(rng.uniform(-7, 7))
        dy = int(rng.uniform(-7, 7))
        br = float(rng.uniform(0.96, 1.04))
        ang = float(rng.uniform(-0.4, 0.4))
        ns = float(rng.uniform(0.5, 1.5))
        frame = apply_station_acquisition_jitter(nom_img, dx, dy, br, ang, ns)
        out_path = os.path.join(TRAIN_NORMAL_DIR, f"station01_normal_train_{i:03d}.png")
        cv2.imwrite(out_path, frame)

    # 2. Validation Normal (15 images)
    print("Generating 15 Station 01 held-out normal validation captures...")
    for i in range(15):
        dx = int(rng.uniform(-8, 8))
        dy = int(rng.uniform(-8, 8))
        br = float(rng.uniform(0.95, 1.05))
        ang = float(rng.uniform(-0.5, 0.5))
        ns = float(rng.uniform(0.5, 2.0))
        frame = apply_station_acquisition_jitter(nom_img, dx, dy, br, ang, ns)
        out_path = os.path.join(VAL_NORMAL_DIR, f"station01_normal_val_{i:03d}.png")
        cv2.imwrite(out_path, frame)

    # 3. Validation Defect (8 images)
    print("Generating 8 Station 01 defect validation captures...")
    for i in range(8):
        dx = int(rng.uniform(-6, 6))
        dy = int(rng.uniform(-6, 6))
        br = float(rng.uniform(0.96, 1.04))
        ang = float(rng.uniform(-0.4, 0.4))
        ns = float(rng.uniform(0.5, 1.5))
        frame = apply_station_acquisition_jitter(def_img, dx, dy, br, ang, ns)
        out_path = os.path.join(VAL_DEFECT_DIR, f"station01_defect_val_{i:03d}.png")
        cv2.imwrite(out_path, frame)

    print("Data preparation complete:")
    print(f" - Train Normals: {len(os.listdir(TRAIN_NORMAL_DIR))} in {TRAIN_NORMAL_DIR}")
    print(f" - Val Normals:   {len(os.listdir(VAL_NORMAL_DIR))} in {VAL_NORMAL_DIR}")
    print(f" - Val Defects:   {len(os.listdir(VAL_DEFECT_DIR))} in {VAL_DEFECT_DIR}")


if __name__ == "__main__":
    generate_station_data()
