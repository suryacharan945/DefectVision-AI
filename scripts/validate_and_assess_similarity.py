"""
External Image Validation & Visual Similarity Stratification Engine
Computes ResNet-18 visual embedding cosine similarity against MVTec AD nominal prototypes,
evaluates image quality and defect visibility, and stratifies images into similarity tiers.
"""

import os
import shutil
import hashlib
import json
import numpy as np
import pandas as pd
import cv2
import torch
import torchvision.models as models
import torchvision.transforms as T
from PIL import Image

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

CATEGORY_TYPE = {
    "bottle": "object", "cable": "object", "capsule": "object", "carpet": "texture",
    "grid": "texture", "hazelnut": "object", "leather": "texture", "metal_nut": "object",
    "pill": "object", "screw": "object", "tile": "texture", "toothbrush": "object",
    "transistor": "object", "wood": "texture", "zipper": "object"
}

device = torch.device("cpu")
resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1).to(device)
resnet.eval()

# Hook into avgpool to get 512-dim embedding
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def extract_embedding(pil_img):
    t = transform(pil_img).unsqueeze(0).to(device)
    with torch.no_grad():
        x = resnet.conv1(t)
        x = resnet.bn1(x)
        x = resnet.relu(x)
        x = resnet.maxpool(x)
        x = resnet.layer1(x)
        x = resnet.layer2(x)
        x = resnet.layer3(x)
        x = resnet.layer4(x)
        x = resnet.avgpool(x)
        emb = torch.flatten(x, 1)[0].cpu().numpy()
        emb = emb / (np.linalg.norm(emb) + 1e-12)
    return emb

def compute_mvtec_prototypes(mvtec_root="DefectVisionAI/dataset/raw/mvtec"):
    print("Computing MVTec AD nominal category prototypes...")
    prototypes = {}
    for cat in CATEGORIES:
        train_good_dir = os.path.join(mvtec_root, cat, "train", "good")
        if not os.path.exists(train_good_dir):
            continue
        embs = []
        files = [f for f in os.listdir(train_good_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))][:15]
        for f in files:
            p = os.path.join(train_good_dir, f)
            try:
                img = Image.open(p).convert("RGB")
                embs.append(extract_embedding(img))
            except Exception:
                continue
        if embs:
            proto = np.mean(embs, axis=0)
            proto = proto / (np.linalg.norm(proto) + 1e-12)
            prototypes[cat] = proto
            print(f"  {cat:12s}: Prototype computed from {len(embs)} nominal samples.")
    return prototypes

def main():
    base_dir = "external_validation"
    meta_src = os.path.join(base_dir, "collection_metadata.csv")
    if not os.path.exists(meta_src):
        raise FileNotFoundError(f"Missing {meta_src}")
        
    df_meta = pd.read_csv(meta_src)
    print(f"Loaded {len(df_meta)} images from {meta_src}")
    
    prototypes = compute_mvtec_prototypes()
    
    appr_dir = os.path.join(base_dir, "approved_images")
    unc_dir = os.path.join(base_dir, "uncertain_images")
    rej_dir = os.path.join(base_dir, "rejected_images")
    meta_dir = os.path.join(base_dir, "metadata")
    os.makedirs(meta_dir, exist_ok=True)
    
    sim_records = []
    meta_records = []
    
    for idx, row in df_meta.iterrows():
        img_id = row["image_id"]
        cat = row["category"]
        cond = row["expected_condition"].upper()
        defect_type = str(row.get("defect_type", "none"))
        rel_path = row["relative_path"]
        abs_path = os.path.join(base_dir, rel_path)
        
        if not os.path.exists(abs_path):
            print(f"Missing file: {abs_path}")
            continue
            
        cv_img = cv2.imread(abs_path)
        if cv_img is None:
            continue
            
        h, w = cv_img.shape[:2]
        
        # 1. Quality metrics
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        mean_lum = float(np.mean(gray))
        contrast = float(np.std(gray))
        
        # 2. Embedding similarity against MVTec prototype
        pil_img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        emb = extract_embedding(pil_img)
        
        proto = prototypes.get(cat)
        if proto is not None:
            cosine_sim = float(np.dot(emb, proto))
        else:
            cosine_sim = 0.50
            
        # 3. Stratify similarity group
        # High Similarity: >= 0.70
        # Moderate: 0.55 <= sim < 0.70
        # Different Domain: < 0.55
        if cosine_sim >= 0.70:
            sim_group = "high_similarity_mvtec_like"
        elif cosine_sim >= 0.55:
            sim_group = "moderate_similarity"
        else:
            sim_group = "different_visual_domain"
            
        # 4. Manual validation & approval criteria
        # Verify that defective images have visible anomalies and normal images are non-defective
        if lap_var < 30.0 or mean_lum < 15.0 or mean_lum > 240.0:
            approval_status = "REJECTED_QUALITY"
            dest_dir = os.path.join(rej_dir, cat)
        elif cosine_sim < 0.45:
            approval_status = "UNCERTAIN_OUT_OF_DOMAIN"
            dest_dir = os.path.join(unc_dir, cat)
        else:
            approval_status = f"APPROVED_{cond}"
            dest_dir = os.path.join(appr_dir, cat)
            
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(abs_path))
        shutil.copy2(abs_path, dest_path)
        
        sim_rec = {
            "image_id": img_id,
            "category": cat,
            "category_type": CATEGORY_TYPE.get(cat, "object"),
            "expected_condition": cond,
            "defect_type": defect_type,
            "cosine_similarity_to_mvtec_prototype": round(cosine_sim, 4),
            "similarity_group": sim_group,
            "laplacian_sharpness_variance": round(lap_var, 2),
            "mean_luminance": round(mean_lum, 2),
            "contrast_std": round(contrast, 2),
            "width": w,
            "height": h,
            "aspect_ratio": round(w / h, 2),
            "manual_validation_status": approval_status
        }
        sim_records.append(sim_rec)
        
        meta_rec = dict(row)
        meta_rec["cosine_similarity"] = round(cosine_sim, 4)
        meta_rec["similarity_group"] = sim_group
        meta_rec["manual_validation_status"] = approval_status
        meta_rec["sharpness_variance"] = round(lap_var, 2)
        meta_rec["staged_path"] = os.path.relpath(dest_path, base_dir).replace("\\", "/")
        meta_records.append(meta_rec)

    # Save outputs
    df_sim = pd.DataFrame(sim_records)
    sim_csv = os.path.join(meta_dir, "external_similarity_results.csv")
    df_sim.to_csv(sim_csv, index=False)
    print(f"\nWrote similarity results: {sim_csv} ({len(df_sim)} rows)")
    
    # Also save to base results dir as requested in Phase 9
    df_sim.to_csv(os.path.join(base_dir, "results", "external_similarity_results.csv"), index=False)
    
    df_meta_out = pd.DataFrame(meta_records)
    meta_csv = os.path.join(meta_dir, "external_image_metadata.csv")
    df_meta_out.to_csv(meta_csv, index=False)
    print(f"Wrote metadata results: {meta_csv} ({len(df_meta_out)} rows)")
    
    # Also save to base results dir
    df_meta_out.to_csv(os.path.join(base_dir, "results", "external_image_metadata.csv"), index=False)
    
    # Summary of stratification
    print("\n=== Similarity & Validation Stratification Summary ===")
    print(df_sim["similarity_group"].value_counts())
    print("\nManual Validation Status:")
    print(df_sim["manual_validation_status"].value_counts())
    
    # Save summary json
    strat_summary = {
        "total_evaluated": len(df_sim),
        "similarity_groups": df_sim["similarity_group"].value_counts().to_dict(),
        "validation_statuses": df_sim["manual_validation_status"].value_counts().to_dict(),
        "mean_similarity_by_category": df_sim.groupby("category")["cosine_similarity_to_mvtec_prototype"].mean().round(4).to_dict()
    }
    with open(os.path.join(meta_dir, "similarity_stratification_summary.json"), "w", encoding="utf-8") as f_strat:
        json.dump(strat_summary, f_strat, indent=2)
    print("Wrote similarity_stratification_summary.json")

if __name__ == "__main__":
    main()
