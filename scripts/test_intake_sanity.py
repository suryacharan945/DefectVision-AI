import os
import sys
sys.path.insert(0, os.path.abspath("DefectVisionAI"))

import cv2
from src.universal_intake_service import UniversalImageIntakeService

def main():
    s = UniversalImageIntakeService()
    test_files = [
        "DefectVisionAI/dataset/raw/mvtec/bottle/test/good/000.png",
        "DefectVisionAI/dataset/raw/mvtec/leather/test/good/000.png",
        r"c:\Users\surya\Downloads\clear bottle.jpg",
        r"c:\Users\surya\Downloads\disordered bottle.webp"
    ]
    for p in test_files:
        if not os.path.exists(p):
            print(f"Skipping missing: {p}")
            continue
        img = cv2.imread(p)
        res = s.process_image(img, inspection_mode="universal")
        print(f"File: {os.path.basename(p):25s} | Domain: {res['image_domain']:16s} | Status: {res['suitability_status']:16s} | FG: {res['foreground_coverage_pct']:5.1f}% | Quality: {res['image_quality_status']}")

if __name__ == "__main__":
    main()
