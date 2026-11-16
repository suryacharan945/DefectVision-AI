import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.category_classifier import (
    CategoryClassifier, KNOWN_CATEGORIES, IMG_SIZE, IMG_MEAN, IMG_STD
)

MODEL_PATH = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "category_classifier", "category_classifier.pth")
META_PATH = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "category_classifier", "category_metadata.json")
SPLIT_CSV = os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "category_classifier_train_split.csv")
OUT_NPZ = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "category_classifier", "category_prototypes.npz")

device = torch.device("cpu")
model = CategoryClassifier(num_classes=len(KNOWN_CATEGORIES), pretrained=False)
checkpoint = torch.load(MODEL_PATH, map_location=device)
if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
    model.load_state_dict(checkpoint["state_dict"])
else:
    model.load_state_dict(checkpoint)
model.eval()

def preprocess_image(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_res = cv2.resize(img_rgb, (IMG_SIZE, IMG_SIZE)).astype(np.float32) / 255.0
    img_norm = (img_res - IMG_MEAN) / IMG_STD
    tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float()
    return tensor

df = pd.read_csv(SPLIT_CSV)
print(f"Loaded {len(df)} training split images.")

cat_embeddings = {cat: [] for cat in KNOWN_CATEGORIES}
cat_energies = {cat: [] for cat in KNOWN_CATEGORIES}
cat_sims = {cat: [] for cat in KNOWN_CATEGORIES}

T = 1.0

with torch.no_grad():
    for _, row in df.iterrows():
        fp = row["filepath"]
        cat = row["category"]
        if not os.path.exists(fp):
            continue
        img = cv2.imread(fp)
        if img is None:
            continue
        t = preprocess_image(img)
        feat = model.extract_features(t)[0].cpu().numpy()
        norm_feat = feat / (np.linalg.norm(feat) + 1e-12)
        cat_embeddings[cat].append(norm_feat)
        
        logits = model(t)
        energy = float(-T * torch.logsumexp(logits / T, dim=1).item())
        cat_energies[cat].append(energy)

prototypes = {}
for cat, emb_list in cat_embeddings.items():
    if len(emb_list) == 0:
        continue
    mat = np.array(emb_list)
    proto = np.mean(mat, axis=0)
    proto = proto / (np.linalg.norm(proto) + 1e-12)
    prototypes[cat] = proto
    
    sims = np.dot(mat, proto)
    cat_sims[cat] = sims
    print(f"[{cat:12s}] N={len(emb_list):3d} | ProtoSim: mean={np.mean(sims):.3f}, min={np.min(sims):.3f}, p05={np.percentile(sims, 5):.3f} | Energy: mean={np.mean(cat_energies[cat]):.2f}, max={np.max(cat_energies[cat]):.2f}, p95={np.percentile(cat_energies[cat], 95):.2f}")

np.savez(OUT_NPZ, **prototypes)
print(f"Saved prototypes to {OUT_NPZ}")
