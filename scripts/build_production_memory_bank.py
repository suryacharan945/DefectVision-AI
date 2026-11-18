"""
DefectVision AI — Production Memory Bank Builder
Constructs a target-domain PatchCore memory bank and FAISS index from
defect-free normal images captured in a specific production environment.

Features:
- Preserves the frozen ResNet18 feature extractor.
- Applies profile-specific ROI extraction before feature extraction.
- Greedy k-center coreset subsampling.
- Saves memory_bank.npy, index.faiss, and manifest.json with SHA-256 hashes.
- Safety check: strictly forbids overwriting benchmark memory banks in models/patchcore/.
"""

import os
import sys
import argparse
import glob
import json
import time
import hashlib
from datetime import datetime
import numpy as np
import cv2
import torch
import faiss

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "DefectVisionAI"))

from src.patchcore import PatchCoreExtractor, PatchCoreModel, greedy_coreset_gpu
from src.production_profile_service import ProductionProfileService, compute_file_sha256

PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
PC_IMG_SIZE = 224


def build_production_memory_bank(
    profile_id: str,
    images_dir: str,
    output_dir: str,
    coreset_ratio: float = 0.10,
    grid_size: int = 28,
    device: str = "cpu"
):
    print(f"============================================================")
    print(f"DEFECTVISION AI — PRODUCTION MEMORY BANK BUILDER")
    print(f"Profile:     {profile_id}")
    print(f"Images Dir:  {images_dir}")
    print(f"Output Dir:  {output_dir}")
    print(f"Coreset:     {coreset_ratio * 100:.1f}%")
    print(f"Device:      {device}")
    print(f"============================================================")

    # 1. Safety Guard against overwriting benchmark models
    benchmark_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "patchcore"))
    target_abs = os.path.abspath(output_dir)
    if target_abs.startswith(benchmark_dir):
        raise ValueError(
            f"SAFETY VIOLATION: Target directory {target_abs} is inside benchmark directory {benchmark_dir}. "
            f"Benchmark 15-category models must NEVER be modified or overwritten."
        )

    os.makedirs(output_dir, exist_ok=True)

    # 2. Gather defect-free training images
    image_patterns = ["*.png", "*.jpg", "*.jpeg", "*.bmp"]
    image_files = []
    for pat in image_patterns:
        image_files.extend(glob.glob(os.path.join(images_dir, pat)))
        image_files.extend(glob.glob(os.path.join(images_dir, "**", pat), recursive=True))
    image_files = sorted(list(set(image_files)))

    if not image_files:
        raise FileNotFoundError(f"No valid images found in {images_dir}")
    print(f"[1/4] Found {len(image_files)} normal training images.")

    # 3. Load Profile for ROI extraction (if profile.json exists)
    profile_service = ProductionProfileService()
    profile = profile_service.get_profile(profile_id)
    if profile is None:
        # Check if local profile.json exists in output_dir
        local_cfg = os.path.join(output_dir, "profile.json")
        if os.path.exists(local_cfg):
            with open(local_cfg, "r", encoding="utf-8") as f:
                profile = json.load(f)
            print(f"Loaded existing profile config from {local_cfg}")
        else:
            print(f"Notice: No profile.json found for {profile_id}. Using default contour ROI.")

    # 4. Initialize Feature Extractor
    torch_device = torch.device(device if (device == "cuda" and torch.cuda.is_available()) else "cpu")
    print(f"[2/4] Initializing frozen ResNet18 PatchCore Extractor on {torch_device}...")
    extractor = PatchCoreExtractor(grid_size=grid_size).to(torch_device)
    extractor.eval()

    all_patch_embeddings = []
    t_start = time.time()

    for i, img_path in enumerate(image_files):
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            print(f"Warning: Failed to load {img_path}, skipping.")
            continue

        # Extract ROI according to profile config
        if profile is not None:
            roi_bgr, _ = profile_service.extract_roi(img_bgr, profile)
        else:
            roi_bgr = img_bgr

        # Preprocessing
        img_rgb = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img_rgb, (PC_IMG_SIZE, PC_IMG_SIZE)).astype(np.float32) / 255.0
        img_norm = (img_resized - PC_MEAN) / PC_STD
        tensor = torch.from_numpy(img_norm).permute(2, 0, 1).unsqueeze(0).float().to(torch_device)

        with torch.no_grad():
            fused = extractor(tensor)[0].cpu().numpy()  # shape: (384, grid_size, grid_size)

        C, g, _ = fused.shape
        patches = fused.reshape(C, g * g).T.astype(np.float32)  # shape: (g*g, 384)
        all_patch_embeddings.append(patches)

        if (i + 1) % 10 == 0 or (i + 1) == len(image_files):
            print(f"   Processed image {i + 1}/{len(image_files)}")

    if not all_patch_embeddings:
        raise RuntimeError("No patch embeddings extracted from training images.")

    raw_memory_bank = np.vstack(all_patch_embeddings)
    total_patches, dim = raw_memory_bank.shape
    print(f"[3/4] Extracted {total_patches} total patch vectors of dimension {dim}.")

    # 5. Greedy Coreset Subsampling
    print(f"   Running coreset subsampling (ratio={coreset_ratio:.2f})...")
    if torch_device.type == "cuda":
        coreset_bank = greedy_coreset_gpu(raw_memory_bank, coreset_ratio=coreset_ratio, device="cuda")
    else:
        # Fast CPU coreset: if total_patches is large, random uniform selection + k-center
        target_k = max(1, int(total_patches * coreset_ratio))
        if total_patches > target_k:
            rng = np.random.RandomState(42)
            # Pick seed point
            indices = [int(rng.randint(total_patches))]
            # Vectorized CPU batch distance updates
            min_dists = np.linalg.norm(raw_memory_bank - raw_memory_bank[indices[0]], axis=1)
            for step in range(1, target_k):
                next_idx = int(np.argmax(min_dists))
                indices.append(next_idx)
                new_dists = np.linalg.norm(raw_memory_bank - raw_memory_bank[next_idx], axis=1)
                min_dists = np.minimum(min_dists, new_dists)
                if (step + 1) % 500 == 0 or (step + 1) == target_k:
                    print(f"   Coreset progress: {step + 1}/{target_k}")
            coreset_bank = raw_memory_bank[indices].astype(np.float32)
        else:
            coreset_bank = raw_memory_bank.astype(np.float32)

    print(f"   Final memory bank size: {coreset_bank.shape[0]} vectors.")

    # 6. Build and save FAISS L2 index
    print(f"[4/4] Building FAISS IndexFlatL2...")
    index = faiss.IndexFlatL2(dim)
    index.add(coreset_bank.astype(np.float32))

    mb_file = os.path.join(output_dir, "memory_bank.npy")
    faiss_file = os.path.join(output_dir, "index.faiss")
    manifest_file = os.path.join(output_dir, "manifest.json")

    np.save(mb_file, coreset_bank)
    faiss.write_index(index, faiss_file)

    elapsed_sec = round(time.time() - t_start, 2)

    # 7. Generate Manifest
    manifest = {
        "profile_id": profile_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "training_samples_count": len(image_files),
        "raw_patches_count": total_patches,
        "coreset_vectors_count": int(coreset_bank.shape[0]),
        "feature_dim": dim,
        "grid_size": grid_size,
        "coreset_ratio": coreset_ratio,
        "build_duration_sec": elapsed_sec,
        "artifacts": {
            "memory_bank.npy": {
                "sha256": compute_file_sha256(mb_file),
                "size_bytes": os.path.getsize(mb_file)
            },
            "index.faiss": {
                "sha256": compute_file_sha256(faiss_file),
                "size_bytes": os.path.getsize(faiss_file)
            }
        }
    }
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Success! Memory bank and FAISS index generated:")
    print(f" - Memory Bank: {mb_file} ({manifest['artifacts']['memory_bank.npy']['size_bytes']} bytes)")
    print(f" - FAISS Index: {faiss_file} ({manifest['artifacts']['index.faiss']['size_bytes']} bytes)")
    print(f" - Manifest:    {manifest_file}")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build production PatchCore memory bank.")
    parser.add_argument("--profile-id", type=str, required=True, help="Profile ID (e.g. bottle_001_station_01)")
    parser.add_argument("--images-dir", type=str, required=True, help="Directory containing defect-free normal images")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory")
    parser.add_argument("--coreset-ratio", type=float, default=0.10, help="Coreset subsampling ratio (default: 0.10)")
    parser.add_argument("--grid-size", type=int, default=28, help="Patch grid size (default: 28)")
    parser.add_argument("--device", type=str, default="cpu", help="Compute device ('cpu' or 'cuda')")

    args = parser.parse_args()
    if args.output_dir is None:
        args.output_dir = os.path.join(
            PROJECT_ROOT, "DefectVisionAI", "models", "production_profiles", args.profile_id
        )

    build_production_memory_bank(
        profile_id=args.profile_id,
        images_dir=args.images_dir,
        output_dir=args.output_dir,
        coreset_ratio=args.coreset_ratio,
        grid_size=args.grid_size,
        device=args.device
    )
