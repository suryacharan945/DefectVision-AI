#!/usr/bin/env python3
"""
DefectVision AI — Category Recognition Classifier Training Pipeline
Trains an ImageNet-pretrained EfficientNet-B0 on defect-free nominal images across all
15 official MVTec AD categories, performs temperature-scaled confidence calibration,
and exports the production model artifact.
"""

import os
import sys
import time
import json
import argparse
import numpy as np
import pandas as pd
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as T

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.category_classifier import (
    CategoryClassifier, KNOWN_CATEGORIES, CATEGORY_TYPE,
    IMG_SIZE, IMG_MEAN, IMG_STD
)

OUTPUT_MODEL_DIR = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "category_classifier")
MANIFESTS_DIR = os.path.join(PROJECT_ROOT, "release", "dataset_manifests")
os.makedirs(OUTPUT_MODEL_DIR, exist_ok=True)

class MVTecCategoryDataset(Dataset):
    def __init__(self, df, transform=None):
        self.filepaths = df["filepath"].tolist()
        self.labels = df["category_id"].tolist()
        self.categories = df["category"].tolist()
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
            # Fallback zero image
            img = Image.new("RGB", (IMG_SIZE, IMG_SIZE))

        if self.transform:
            img = self.transform(img)

        return img, label

def get_transforms():
    train_transform = T.Compose([
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.5),
        T.RandomRotation(degrees=15),
        T.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
        T.ToTensor(),
        T.Normalize(mean=IMG_MEAN, std=IMG_STD)
    ])

    val_transform = T.Compose([
        T.Resize((IMG_SIZE, IMG_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=IMG_MEAN, std=IMG_STD)
    ])

    return train_transform, val_transform

def calibrate_temperature(model, val_loader, device):
    """
    Learns optimal temperature parameter T on validation set using NLL minimization.
    """
    print("\n[Calibrating Temperature Parameter on Validation Set]...", flush=True)
    model.eval()
    logits_list = []
    labels_list = []

    with torch.no_grad():
        for images, targets in val_loader:
            images = images.to(device)
            logits = model(images)
            logits_list.append(logits.cpu())
            labels_list.append(targets)

    logits = torch.cat(logits_list, dim=0)
    labels = torch.cat(labels_list, dim=0)

    # Optimize temperature
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
    print(f"Optimal Temperature T: {optimal_t:.4f}", flush=True)
    model.temperature.data.fill_(optimal_t)
    return optimal_t

def train(epochs=8, batch_size=32, lr=1e-3, device="cpu", seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)

    print("=================================================================", flush=True)
    print("DefectVision AI — Category Recognition Model Training", flush=True)
    print(f"Device: {device} | Epochs: {epochs} | Batch Size: {batch_size} | LR: {lr}", flush=True)
    print("=================================================================", flush=True)

    train_csv = os.path.join(MANIFESTS_DIR, "category_classifier_train_split.csv")
    val_csv = os.path.join(MANIFESTS_DIR, "category_classifier_val_split.csv")

    if not os.path.exists(train_csv) or not os.path.exists(val_csv):
        raise FileNotFoundError(f"Split manifests missing in {MANIFESTS_DIR}. Run generate_mvtec_splits.py first.")

    train_df = pd.read_csv(train_csv)
    val_df = pd.read_csv(val_csv)

    print(f"Train samples: {len(train_df)} across {train_df['category'].nunique()} categories", flush=True)
    print(f"Val samples:   {len(val_df)} across {val_df['category'].nunique()} categories", flush=True)

    train_tf, val_tf = get_transforms()
    train_dataset = MVTecCategoryDataset(train_df, transform=train_tf)
    val_dataset = MVTecCategoryDataset(val_df, transform=val_tf)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize model
    model = CategoryClassifier(num_classes=len(KNOWN_CATEGORIES), pretrained=True)
    model.to(device)

    # Two-phase training:
    # Phase 1: Freeze features, train classifier head (2 epochs)
    for p in model.features.parameters():
        p.requires_grad = False

    optimizer = torch.optim.AdamW(model.head.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    print("\n--- Phase 1: Warmup Classifier Head (Frozen Backbone) ---", flush=True)
    for ep in range(1, 3):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(targets)
            preds = logits.argmax(dim=1)
            correct += (preds == targets).sum().item()
            total += len(targets)

        train_acc = 100.0 * correct / total
        dt = time.time() - t0
        print(f"Epoch {ep}/2 (Head Only) | Loss: {train_loss/total:.4f} | Acc: {train_acc:.2f}% | Time: {dt:.1f}s", flush=True)

    # Phase 2: Unfreeze top layers of EfficientNet backbone (layers 5-8) and train end-to-end
    print("\n--- Phase 2: Fine-Tuning Top Convolutional Blocks ---", flush=True)
    for idx, child in enumerate(model.features):
        if idx >= 5:  # Unfreeze higher semantic blocks
            for p in child.parameters():
                p.requires_grad = True

    trainable_params = [
        {"params": model.head.parameters(), "lr": lr * 0.5},
        {"params": [p for idx, child in enumerate(model.features) if idx >= 5 for p in child.parameters()], "lr": lr * 0.1}
    ]
    optimizer = torch.optim.AdamW(trainable_params, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    best_weights = None

    for ep in range(1, epochs + 1):
        t0 = time.time()
        model.train()
        train_loss = 0.0
        correct = 0
        total = 0

        for images, targets in train_loader:
            images, targets = images.to(device), targets.to(device)
            optimizer.zero_grad()
            logits = model(images)
            loss = criterion(logits, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(targets)
            preds = logits.argmax(dim=1)
            correct += (preds == targets).sum().item()
            total += len(targets)

        scheduler.step()
        train_acc = 100.0 * correct / total

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, targets in val_loader:
                images, targets = images.to(device), targets.to(device)
                logits = model(images)
                loss = criterion(logits, targets)

                val_loss += loss.item() * len(targets)
                preds = logits.argmax(dim=1)
                val_correct += (preds == targets).sum().item()
                val_total += len(targets)

        val_acc = 100.0 * val_correct / val_total
        dt = time.time() - t0

        is_best = val_acc > best_val_acc
        if is_best:
            best_val_acc = val_acc
            best_weights = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        print(f"Epoch {ep:>2}/{epochs} | Train Loss: {train_loss/total:.4f} Acc: {train_acc:>6.2f}% | "
              f"Val Loss: {val_loss/val_total:.4f} Acc: {val_acc:>6.2f}% | Time: {dt:>4.1f}s {'[BEST]' if is_best else ''}", flush=True)

    # Restore best weights
    model.load_state_dict(best_weights)
    print(f"\nTraining Complete. Peak Validation Accuracy: {best_val_acc:.2f}%", flush=True)

    # Calibrate temperature
    optimal_t = calibrate_temperature(model, val_loader, device)

    # Save model checkpoint
    ckpt_path = os.path.join(OUTPUT_MODEL_DIR, "category_classifier.pth")
    torch.save({
        "state_dict": model.state_dict(),
        "temperature": optimal_t,
        "best_val_accuracy": best_val_acc,
        "confidence_threshold": 0.70,
        "input_size": IMG_SIZE,
        "categories": KNOWN_CATEGORIES,
        "architecture": "efficientnet_b0"
    }, ckpt_path)
    print(f"Model saved to: {ckpt_path} ({os.path.getsize(ckpt_path):,} bytes)", flush=True)

    # Save metadata JSON
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
            "trained_epochs": epochs + 2,
            "training_samples": len(train_df),
            "validation_samples": len(val_df),
            "random_seed": seed,
            "training_device": str(device)
        }, f, indent=2)
    print(f"Metadata saved to: {meta_path}", flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=5, help="Number of fine-tuning epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--device", type=str, default="cpu", help="Compute device ('cpu' or 'cuda')")
    args = parser.parse_args()

    train(epochs=args.epochs, batch_size=args.batch_size, lr=args.lr, device=args.device)
