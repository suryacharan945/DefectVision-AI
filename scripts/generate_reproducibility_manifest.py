import os
import sys
import json
import hashlib
import platform
import torch
import torchvision
import faiss
import cv2
import sklearn
import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
os.makedirs(OUT_DIR, exist_ok=True)

CATEGORIES = [
    "bottle", "cable", "capsule", "carpet", "grid",
    "hazelnut", "leather", "metal_nut", "pill", "screw",
    "tile", "toothbrush", "transistor", "wood", "zipper"
]

def sha256_file(filepath):
    if not os.path.exists(filepath):
        return "FILE_NOT_FOUND"
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_manifest():
    print("=" * 70, flush=True)
    print("DefectVision AI — Generating Official Reproducibility Manifest", flush=True)
    print("Hashing Datasets, Memory Banks, Models, Scripts, and Artifacts", flush=True)
    print("=" * 70, flush=True)

    manifest = {
        "project": "DefectVision AI",
        "repository": "https://github.com/suryacharan945/DefectVision-AI",
        "release_branch": "release/full-stack-completion-2026-11-17",
        "pull_request": "https://github.com/suryacharan945/DefectVision-AI/pull/5",
        "timestamp_utc": pd.Timestamp.utcnow().isoformat(),
        "runtime_environment": {
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "torchvision_version": torchvision.__version__,
            "faiss_version": getattr(faiss, "__version__", "1.7.4"),
            "opencv_version": cv2.__version__,
            "sklearn_version": sklearn.__version__,
            "numpy_version": np.__version__,
            "cuda_available": torch.cuda.is_available()
        },
        "dataset_manifests": {
            "official_test_split_csv": {
                "path": "release/dataset_manifests/official_test_split.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "official_test_split.csv")),
                "total_specimens": 1725,
                "nominal_specimens": 467,
                "defective_specimens": 1258
            },
            "patchcore_calibration_split_csv": {
                "path": "release/dataset_manifests/patchcore_calibration_split.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "dataset_manifests", "patchcore_calibration_split.csv")),
                "total_specimens": 726,
                "nominal_specimens": 726
            }
        },
        "threshold_configuration": {
            "path": "DefectVisionAI/models/patchcore/category_thresholds.json",
            "sha256": sha256_file(os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "patchcore", "category_thresholds.json"))
        },
        "neural_models_and_memory_banks": {},
        "production_profiles": {
            "bottle_001_station_01": {
                "path": "DefectVisionAI/models/production_profiles/bottle_001_station_01/profile.json",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "production_profiles", "bottle_001_station_01", "profile.json"))
            }
        },
        "core_verification_scripts": {
            "compute_all_mvtec_localization_py": {
                "path": "scripts/compute_all_mvtec_localization.py",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "scripts", "compute_all_mvtec_localization.py"))
            },
            "run_workflow_b_stratified_py": {
                "path": "scripts/run_workflow_b_stratified.py",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "scripts", "run_workflow_b_stratified.py"))
            },
            "test_robust_feature_matrix_py": {
                "path": "scripts/test_robust_feature_matrix.py",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "scripts", "test_robust_feature_matrix.py"))
            },
            "audit_threshold_sensitivity_py": {
                "path": "scripts/audit_threshold_sensitivity.py",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "scripts", "audit_threshold_sensitivity.py"))
            },
            "reconcile_reports_py": {
                "path": "scripts/reconcile_reports.py",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "scripts", "reconcile_reports.py"))
            }
        },
        "authoritative_validation_artifacts": {
            "mvtec_all_predictions_csv": {
                "path": "release/final_validation/mvtec_all_predictions.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "mvtec_all_predictions.csv")),
                "role": "Single canonical source of truth for all 1,725 official test specimens"
            },
            "mvtec_per_category_metrics_csv": {
                "path": "release/final_validation/mvtec_per_category_metrics.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "mvtec_per_category_metrics.csv")),
                "role": "Per-category performance metrics computed from canonical predictions"
            },
            "category_threshold_provenance_csv": {
                "path": "release/final_validation/category_threshold_provenance.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "category_threshold_provenance.csv")),
                "role": "Operating characteristic curve thresholds (p95 through p99.9) and high-FPR diagnostics"
            },
            "feature_acceptance_matrix_csv": {
                "path": "release/final_validation/FEATURE_ACCEPTANCE_MATRIX.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "FEATURE_ACCEPTANCE_MATRIX.csv")),
                "role": "23-point verified feature acceptance matrix across all endpoints"
            },
            "workflow_b_stratified_results_csv": {
                "path": "release/final_validation/WORKFLOW_B_STRATIFIED_RESULTS.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "WORKFLOW_B_STRATIFIED_RESULTS.csv")),
                "role": "90-specimen autonomous routing and defect decisioning verification"
            },
            "mvtec_localization_audit_csv": {
                "path": "release/final_validation/MVTEC_LOCALIZATION_AUDIT.csv",
                "sha256": sha256_file(os.path.join(PROJECT_ROOT, "release", "final_validation", "MVTEC_LOCALIZATION_AUDIT.csv")),
                "role": "Raw-map pooled and per-defect pixel AUROC, IoU, and Dice across 15 categories"
            }
        }
    }

    # Hash 15 PatchCore memory banks
    for cat in CATEGORIES:
        mb_path = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "patchcore", cat, "memory_bank.npy")
        manifest["neural_models_and_memory_banks"][f"patchcore_{cat}_memory_bank"] = {
            "path": f"DefectVisionAI/models/patchcore/{cat}/memory_bank.npy",
            "sha256": sha256_file(mb_path)
        }

    # Hash EfficientNet-B0 category classifier
    eff_path = os.path.join(PROJECT_ROOT, "DefectVisionAI", "models", "classifier", "efficientnet_b0_mvtec.pth")
    if os.path.exists(eff_path):
        manifest["neural_models_and_memory_banks"]["efficientnet_b0_classifier"] = {
            "path": "DefectVisionAI/models/classifier/efficientnet_b0_mvtec.pth",
            "sha256": sha256_file(eff_path)
        }

    out_json = os.path.join(OUT_DIR, "REPRODUCIBILITY_MANIFEST.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Official Reproducibility Manifest written to: {out_json}", flush=True)
    return manifest

if __name__ == "__main__":
    generate_manifest()
