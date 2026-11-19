"""
Evaluate foreground masking vs full-frame PatchCore scoring across all 150 external images:
- Compare raw_score (max over all 784 patches) vs fg_score (max over foreground patches for objects)
- Evaluate impact on False Positive Rate on normal images and Recall on defective images.
"""

import os
import sys
import json
import cv2
import torch
import numpy as np
import pandas as pd

sys.path.insert(0, 'DefectVisionAI')
from src.patchcore import PatchCoreExtractor, PatchCoreModel
from src.object_region_service import ObjectRegionService

device = 'cpu'
extractor = PatchCoreExtractor(grid_size=28).eval()
roi_service = ObjectRegionService()

with open('DefectVisionAI/models/patchcore/category_thresholds.json') as f:
    thresholds = json.load(f)

df_meta = pd.read_csv('external_validation/metadata/external_image_metadata.csv')

# Cache loaded PatchCore models
models = {}
for cat in thresholds.keys():
    mb_path = f'DefectVisionAI/models/patchcore/{cat}/memory_bank.npy'
    if os.path.exists(mb_path):
        m = PatchCoreModel()
        m.load(mb_path, grid_size=28)
        models[cat] = m

print(f"Loaded {len(models)} PatchCore models.", flush=True)

results = []

for idx, row in df_meta.iterrows():
    img_path = os.path.join('external_validation', row['relative_path'])
    gt_cat = row['category']
    gt_cond = row['expected_condition']
    cat_type = "texture" if gt_cat in ["carpet", "grid", "leather", "tile", "wood"] else "object"
    thresh = float(thresholds.get(gt_cat, {}).get("calibrated_threshold", 1.50))
    
    img = cv2.imread(img_path)
    if img is None or gt_cat not in models:
        continue
    
    if max(img.shape[:2]) > 1024:
        scale = 1024.0 / max(img.shape[:2])
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    
    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    res = cv2.resize(rgb, (224, 224)).astype(np.float32) / 255.0
    norm = (res - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    t = torch.from_numpy(norm).permute(2, 0, 1).unsqueeze(0).float()
    with torch.no_grad():
        fused = extractor(t)[0].numpy()
    
    model = models[gt_cat]
    dist_map, raw_score = model.score(fused)
    
    # Foreground mask for objects
    if cat_type == "object":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)
        _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        border_mean = (otsu_thresh[0, :].mean() + otsu_thresh[-1, :].mean() + otsu_thresh[:, 0].mean() + otsu_thresh[:, -1].mean()) / 4.0
        if border_mean > 127:
            otsu_thresh = cv2.bitwise_not(otsu_thresh)
        mask_28 = cv2.resize(otsu_thresh, (28, 28), interpolation=cv2.INTER_AREA) > 30
        if mask_28.sum() >= 15:
            fg_score = float(np.max(dist_map[mask_28]))
            fg_patches = int(mask_28.sum())
        else:
            fg_score = raw_score
            fg_patches = 784
    else:
        # Texture: full-frame
        fg_score = raw_score
        fg_patches = 784
    
    results.append({
        'image_id': row['image_id'],
        'category': gt_cat,
        'category_type': cat_type,
        'expected_condition': gt_cond,
        'manual_validation_status': row['manual_validation_status'],
        'similarity_group': row['similarity_group'],
        'threshold': thresh,
        'raw_score': raw_score,
        'fg_score': fg_score,
        'raw_pred': "DEFECTIVE" if raw_score >= thresh else "NORMAL",
        'fg_pred': "DEFECTIVE" if fg_score >= thresh else "NORMAL",
        'fg_patches': fg_patches
    })

df_res = pd.DataFrame(results)
print("\n--- Raw vs Foreground Scoring on Approved Images ---", flush=True)
appr = df_res[df_res['manual_validation_status'].isin(['APPROVED_NORMAL', 'APPROVED_DEFECTIVE'])]

print("\nRaw Pred on Approved Normal:")
print(appr[appr['expected_condition'] == 'NORMAL']['raw_pred'].value_counts())

print("\nForeground Pred on Approved Normal:")
print(appr[appr['expected_condition'] == 'NORMAL']['fg_pred'].value_counts())

print("\nRaw Pred on Approved Defective:")
print(appr[appr['expected_condition'] == 'DEFECTIVE']['raw_pred'].value_counts())

print("\nForeground Pred on Approved Defective:")
print(appr[appr['expected_condition'] == 'DEFECTIVE']['fg_pred'].value_counts())

df_res.to_csv('external_validation/experiments/foreground_isolation_experiment.csv', index=False)
print("\nSaved external_validation/experiments/foreground_isolation_experiment.csv", flush=True)
