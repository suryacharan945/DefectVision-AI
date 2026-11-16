#!/usr/bin/env python3
"""
DefectVision AI — High-Efficiency Category Recognition Model Training
Extracts EfficientNet-B0 backbone features, trains calibrated classifier head,
and exports production checkpoint and metadata.
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T
import torchvision.models as models

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.category_classifier import (
    CategoryClassifier, KNOWN_CATEGORIES, CATEGORY_TYPE,
    IMG_SIZE, IMG_MEAN, IMG_STD
)

OUTPUT_MODEL_DIR = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "category_classifier")
MANIFESTS_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_manifests")
CACHE_DIR = os.path.join(OUTPUT_MODEL_DIR, "cache")
os.makedirs(OUTPUT_MODEL_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

class SimpleImageDataset(Dataset):
    def __init__(self, filepaths, labels, transform):
        self.filepaths = filepaths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.filepaths)

    def __getitem__(self, idx):
        path = self.filepaths[idx]
        label = self.labels[idx]
        try:
            with Image.open(path) as img:
                img = img.convert("RGB")
        except Exception:
            img = Image.new("RGB", (IMG_SIZE, IMG_SIZE))

        img = self.transform(img)
        return img, label

def extract_features(df, backbone, device, batch_size=64, desc="Features"):
    print(f"\nExtracting {desc} ({len(df)} images)...", flush=True)
    transform = T.Compose([
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=IMG_MEAN, std=IMG_STD)
    ])

    dataset = SimpleImageDataset(df["filepath"].tolist(), df["category_id"].tolist(), transform)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    backbone.eval()
    all_features = []
    all_labels = []

    t0 = time.time()
    total_batches = len(loader)

    with torch.no_grad():
        for b_idx, (images, labels) in enumerate(loader):
            images = images.to(device)
            feat = backbone.features(images)
            pooled = backbone.avgpool(feat)
            flat = torch.flatten(pooled, 1)

            all_features.append(flat.cpu().numpy())
            all_labels.append(labels.numpy())

            if (b_idx + 1) % 10 == 0 or (b_idx + 1) == total_batches:
                proc = min((b_idx + 1) * batch_size, len(df))
                print(f"  [{desc}] Processed {proc:>4}/{len(df)} images ({(b_idx+1)/total_batches*100:>5.1f}%) in {time.time()-t0:.1f}s", flush=True)

    X = np.concatenate(all_features, axis=0)
    y = np.concatenate(all_labels, axis=0)
    print(f"  Finished {desc}: shape={X.shape}, labels={y.shape} in {time.time()-t0:.2f}s", flush=True)
    return X, y

def calibrate_temperature_on_logits(logits, labels):
    """
    Fits optimal temperature T to minimize NLL on validation logits.
    """
    temp = nn.Parameter(torch.ones(1) * 1.5)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.LBFGS([temp], lr=0.01, max_iter=50)

    def eval_loss():
        optimizer.zero_grad()
        loss = criterion(logits / torch.clamp(temp, 0.1, 10.0), labels)
        loss.backward()
        return loss

    optimizer.step(eval_loss)
    optimal_t = float(torch.clamp(temp, 0.1, 10.0).item())
    return optimal_t

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    seed = 42
    torch.manual_seed(seed)
    np.random.seed(seed)

    print("=================================================================", flush=True)
    print("DefectVision AI — High-Efficiency Category Classifier Training", flush=True)
    print(f"Device: {device} | Architecture: EfficientNet-B0 (ImageNet-1K)", flush=True)
    print("=================================================================", flush=True)

    train_csv = os.path.join(MANIFESTS_DIR, "category_classifier_train_split.csv")
    val_csv = os.path.join(MANIFESTS_DIR, "category_classifier_val_split.csv")
    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)

    # 1. Load Pretrained Backbone
    print("Loading ImageNet-1K Pretrained EfficientNet-B0...", flush=True)
    base = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1).to(device)

    # Check feature cache
    train_feat_file = os.path.join(CACHE_DIR, "train_features.npz")
    val_feat_file = os.path.join(CACHE_DIR, "val_features.npz")

    if os.path.exists(train_feat_file) and os.path.exists(val_feat_file):
        print("Found existing feature cache. Loading...", flush=True)
        t_data = np.load(train_feat_file)
        v_data = np.load(val_feat_file)
        X_train, y_train = t_data["X"], t_data["y"]
        X_val, y_val = v_data["X"], v_data["y"]
    else:
        X_train, y_train = extract_features(train_df, base, device, batch_size=64, desc="Train Split")
        X_val, y_val = extract_features(val_df, base, device, batch_size=64, desc="Val Split")
        np.savez_compressed(train_feat_file, X=X_train, y=y_train)
        np.savez_compressed(val_feat_file, X=X_val, y=y_val)
        print(f"Saved feature cache to: {CACHE_DIR}", flush=True)

    # 2. Train Classification Head on Cached Features
    print("\n--- Training Calibrated Classification Head ---", flush=True)
    in_features = X_train.shape[1]  # 1280
    num_classes = len(KNOWN_CATEGORIES)

    head = nn.Sequential(
        nn.Dropout(p=0.2),
        nn.Linear(in_features, 256),
        nn.SiLU(),
        nn.Dropout(p=0.2),
        nn.Linear(256, num_classes)
    ).to(device)

    t_tensor = torch.from_numpy(X_train).float().to(device)
    y_tensor = torch.from_numpy(y_train).long().to(device)
    v_tensor = torch.from_numpy(X_val).float().to(device)
    yv_tensor = torch.from_numpy(y_val).long().to(device)

    train_data = torch.utils.data.TensorDataset(t_tensor, y_tensor)
    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)

    optimizer = torch.optim.AdamW(head.parameters(), lr=1e-3, weight_decay=1e-3)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=30)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    best_head_state = None

    t_train_start = time.time()
    for ep in range(1, 31):
        head.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for bx, by in train_loader:
            optimizer.zero_grad()
            logits = head(bx)
            loss = criterion(logits, by)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(by)
            preds = logits.argmax(dim=1)
            correct += (preds == by).sum().item()
            total += len(by)

        scheduler.step()
        train_acc = 100.0 * correct / total

        head.eval()
        with torch.no_grad():
            v_logits = head(v_tensor)
            v_loss = criterion(v_logits, yv_tensor).item()
            v_preds = v_logits.argmax(dim=1)
            v_acc = 100.0 * (v_preds == yv_tensor).sum().item() / len(yv_tensor)

        if v_acc > best_val_acc:
            best_val_acc = v_acc
            best_head_state = {k: v.cpu().clone() for k, v in head.state_dict().items()}

        if ep % 5 == 0 or ep == 30 or v_acc == 100.0:
            print(f"Epoch {ep:>2}/30 | Train Loss: {total_loss/total:.4f} Acc: {train_acc:>6.2f}% | "
                  f"Val Loss: {v_loss:.4f} Acc: {v_acc:>6.2f}%", flush=True)

    print(f"\nHead Training Complete in {time.time()-t_train_start:.2f}s! Peak Validation Accuracy: {best_val_acc:.2f}%", flush=True)
    head.load_state_dict(best_head_state)

    # 3. Temperature Calibration
    head.eval()
    with torch.no_grad():
        val_logits = head(v_tensor).cpu()
        val_labels = yv_tensor.cpu()
    optimal_t = calibrate_temperature_on_logits(val_logits, val_labels)
    print(f"Learned Optimal Temperature T: {optimal_t:.4f}", flush=True)

    # 4. Construct End-to-End CategoryClassifier & Save
    full_model = CategoryClassifier(num_classes=num_classes, pretrained=False)
    # Copy backbone features from base
    full_model.features.load_state_dict(base.features.state_dict())
    full_model.avgpool.load_state_dict(base.avgpool.state_dict())
    full_model.head.load_state_dict(head.state_dict())
    full_model.temperature.data.fill_(optimal_t)

    ckpt_path = os.path.join(OUTPUT_MODEL_DIR, "category_classifier.pth")
    torch.save({
        "state_dict": full_model.state_dict(),
        "temperature": optimal_t,
        "best_val_accuracy": best_val_acc,
        "confidence_threshold": 0.70,
        "input_size": IMG_SIZE,
        "categories": KNOWN_CATEGORIES,
        "architecture": "efficientnet_b0"
    }, ckpt_path)
    print(f"\nSaved production model to: {ckpt_path} ({os.path.getsize(ckpt_path):,} bytes)", flush=True)

    # 5. Save Metadata Manifest
    meta_path = os.path.join(OUTPUT_MODEL_DIR, "category_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "model_name": "EfficientNet-B0-MVTec-CategoryRecognizer",
            "model_path": "models/category_classifier/category_classifier.pth",
            "architecture": "efficientnet_b0",
            "num_classes": len(KNOWN_CATEGORIES),
            "categories": KNOWN_CATEGORIES,
            "category_types": CATEGORY_TYPE,
            "input_resolution": [IMG_SIZE, IMG_SIZE],
            "normalization": {"mean": IMG_MEAN.tolist(), "std": IMG_STD.tolist()},
            "temperature": round(optimal_t, 4),
            "confidence_threshold": 0.70,
            "peak_val_accuracy": round(best_val_acc, 2),
            "trained_epochs": 30,
            "training_samples": len(train_df),
            "validation_samples": len(val_df),
            "random_seed": seed,
            "training_device": str(device)
        }, f, indent=2)
    print(f"Saved metadata to: {meta_path}", flush=True)

if __name__ == "__main__":
    main()
