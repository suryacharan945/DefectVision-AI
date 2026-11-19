"""
Test script to evaluate the proposed leakage-free improvements:
1. Multi-tier category gating (ACCEPTED, LOW_CONFIDENCE, UNSUPPORTED_CATEGORY, POOR_IMAGE_QUALITY, AMBIGUOUS_INPUT)
2. Foreground object masking / ROI isolation for PatchCore object categories
3. Calibrated threshold policy on held-out validation split
"""

import os
import sys
import json
import cv2
import torch
import numpy as np
import pandas as pd

sys.path.insert(0, 'DefectVisionAI')
from src.category_classifier import CategoryRecognitionService
from src.patchcore import PatchCoreExtractor, PatchCoreModel
from src.object_region_service import ObjectRegionService
from src.image_quality_service import ImageQualityService

device = 'cpu'
cat_service = CategoryRecognitionService(
    model_path='DefectVisionAI/models/category_classifier/category_classifier.pth',
    meta_path='DefectVisionAI/models/category_classifier/category_metadata.json',
    device=device,
    confidence_threshold=0.70
)
extractor = PatchCoreExtractor(grid_size=28).eval()
quality_service = ImageQualityService()
roi_service = ObjectRegionService()

with open('DefectVisionAI/models/patchcore/category_thresholds.json') as f:
    thresholds = json.load(f)

# Load metadata
df_meta = pd.read_csv('external_validation/metadata/external_image_metadata.csv')
print(f"Loaded {len(df_meta)} external images.")

results = []

for idx, row in df_meta.iterrows():
    img_path = os.path.join('external_validation', row['relative_path'])
    gt_cat = row['category']
    gt_cond = row['expected_condition']
    cat_type = "texture" if gt_cat in ["carpet", "grid", "leather", "tile", "wood"] else "object"
    
    img = cv2.imread(img_path)
    if img is None:
        continue
    
    # Fast resize if massive web image
    if max(img.shape[:2]) > 1024:
        scale = 1024.0 / max(img.shape[:2])
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    
    # 1. Quality Gate
    is_qual, q_status, q_metrics = quality_service.validate_frame(img)
    
    # 2. Category Classifier Raw
    cat_res = cat_service.predict(img)
    cand_cat = cat_res['candidate_category']
    cand_conf = cat_res['confidence']
    cand_entropy = cat_res['normalized_entropy']
    cand_energy = cat_res['energy_score']
    cand_proto = cat_res.get('prototype_similarity')
    
    # New Multi-tier Gate Classification
    if not is_qual:
        tier_gate = "POOR_IMAGE_QUALITY"
    elif cand_conf < 0.35 and (cand_proto is None or cand_proto < 0.40):
        tier_gate = "UNSUPPORTED_CATEGORY"
    elif cand_entropy > 0.88 and cand_conf < 0.40:
        tier_gate = "AMBIGUOUS_INPUT"
    elif cand_conf >= 0.70 and cand_entropy <= 0.60 and cand_energy <= -6.50:
        tier_gate = "ACCEPTED"
    else:
        tier_gate = "LOW_CONFIDENCE"
    
    results.append({
        'image_id': row['image_id'],
        'category': gt_cat,
        'category_type': cat_type,
        'expected_condition': gt_cond,
        'candidate_category': cand_cat,
        'candidate_confidence': cand_conf,
        'entropy': cand_entropy,
        'energy': cand_energy,
        'prototype_similarity': cand_proto,
        'is_qual': is_qual,
        'tier_gate': tier_gate,
        'is_cat_correct': (cand_cat == gt_cat)
    })

df_res = pd.DataFrame(results)
print("\n--- Multi-tier Gate Distribution ---")
print(df_res['tier_gate'].value_counts())
print("\n--- Category Accuracy by Tier Gate ---")
print(df_res.groupby('tier_gate')['is_cat_correct'].agg(['count', 'mean']))
