import os
import csv
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import faiss

GRID_SIZE = 28
PC_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
PC_STD  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
TAU_P99 = 1.745232

class PatchCoreExtractor(nn.Module):
    def __init__(self, grid_size=GRID_SIZE):
        super().__init__()
        backbone = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.layer0 = nn.Sequential(backbone.conv1, backbone.bn1, backbone.relu, backbone.maxpool)
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.grid_size = grid_size
        self.local_pool = nn.AvgPool2d(kernel_size=3, stride=1, padding=1)
        for p in self.parameters():
            p.requires_grad = False
        self.eval()

    @torch.no_grad()
    def forward(self, x):
        x0 = self.layer0(x)
        f1 = self.layer1(x0)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        f2 = self.local_pool(f2)
        f3 = self.local_pool(f3)
        g = self.grid_size
        f2r = F.interpolate(f2, size=(g, g), mode="bilinear", align_corners=False)
        f3r = F.interpolate(f3, size=(g, g), mode="bilinear", align_corners=False)
        return torch.cat([f2r, f3r], dim=1)

def apply_perturbation(img_bgr, p_type):
    if p_type == "clean":
        return img_bgr
    elif p_type == "brightness_up":
        # +15% scaling
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.15, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    elif p_type == "brightness_down":
        # -15% scaling
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 0.85, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    elif p_type == "contrast_up":
        # +20% contrast from mean
        mean = np.mean(img_bgr)
        res = (img_bgr.astype(np.float32) - mean) * 1.20 + mean
        return np.clip(res, 0, 255).astype(np.uint8)
    elif p_type == "gaussian_blur":
        # Gaussian blur sigma=1.0, ksize=5
        return cv2.GaussianBlur(img_bgr, (5, 5), sigmaX=1.0)
    elif p_type == "jpeg_compression":
        # JPEG quality=50
        _, enc = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
        return cv2.imdecode(enc, cv2.IMREAD_COLOR)
    elif p_type == "framing_shift":
        # Horizontal +4 px, vertical +4 px translation
        M = np.float32([[1, 0, 4], [0, 1, 4]])
        return cv2.warpAffine(img_bgr, M, (img_bgr.shape[1], img_bgr.shape[0]), borderMode=cv2.BORDER_REFLECT)
    else:
        return img_bgr

def preprocess_tensor(img_bgr, size=224):
    img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (size, size)).astype(np.float32) / 255.0
    img = (img - PC_MEAN) / PC_STD
    return torch.from_numpy(img).permute(2, 0, 1).float().unsqueeze(0)

def main():
    print("=== CONTROLLED REAL-WORLD ROBUSTNESS SENSITIVITY TEST (VISA CASHEW) ===")
    index_file = r"release\phase49_independent_results\models\patchcore_cashew\index.faiss"
    pred_file = r"release\phase49_independent_results\TEST_PREDICTIONS.csv"
    manifest_file = r"release\phase49_independent_results\SPLIT_MANIFEST.csv"
    
    faiss_index = faiss.read_index(index_file)
    print(f"Loaded frozen FAISS index: {faiss_index.ntotal} vectors")

    # Get file paths from SPLIT_MANIFEST.csv
    file_map = {}
    with open(manifest_file, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["partition"] == "test":
                file_map[r["specimen_id"]] = r["image_path"]

    # Select balanced cohort: 10 nominals and 10 defectives
    nominals = []
    defectives = []
    with open(pred_file, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            sid = r["specimen_id"]
            if sid in file_map and os.path.exists(file_map[sid]):
                if r["ground_truth"] == "0" and len(nominals) < 10:
                    nominals.append((sid, file_map[sid], 0, r["defect_type"]))
                elif r["ground_truth"] == "1" and len(defectives) < 10:
                    defectives.append((sid, file_map[sid], 1, r["defect_type"]))

    eval_cohort = nominals + defectives
    print(f"Selected controlled evaluation cohort: {len(eval_cohort)} specimens (10 nominal, 10 defective)")

    extractor = PatchCoreExtractor().eval()

    perturbations = [
        ("clean", "None (Baseline)"),
        ("brightness_up", "+15% Brightness"),
        ("brightness_down", "-15% Brightness"),
        ("contrast_up", "+20% Contrast"),
        ("gaussian_blur", "Gaussian Blur (sigma=1.0)"),
        ("jpeg_compression", "JPEG Compression (Q=50)"),
        ("framing_shift", "Framing Shift (+4,+4 px)")
    ]

    results = []
    print("\nExecuting perturbation sensitivity sweeps...")

    for p_key, p_desc in perturbations:
        scores = []
        preds = []
        y_trues = []

        for sid, fpath, gt, dtype in eval_cohort:
            raw_bgr = cv2.imread(fpath)
            p_bgr = apply_perturbation(raw_bgr, p_key)
            t = preprocess_tensor(p_bgr)

            with torch.no_grad():
                feats = extractor(t)
                patches = feats.squeeze(0).permute(1, 2, 0).reshape(-1, 384).cpu().numpy().astype(np.float32)
                dists, _ = faiss_index.search(patches, 1)
                score = float(np.sqrt(np.clip(dists[:, 0], 0, None)).max())
                pred = 1 if score >= TAU_P99 else 0

            scores.append(score)
            preds.append(pred)
            y_trues.append(gt)

        scores = np.array(scores)
        preds = np.array(preds)
        y_trues = np.array(y_trues)

        acc = np.mean(preds == y_trues) * 100
        mean_score = np.mean(scores)
        mean_nom_score = np.mean(scores[y_trues == 0])
        mean_def_score = np.mean(scores[y_trues == 1])
        fp = int(np.sum((y_trues == 0) & (preds == 1)))
        fn = int(np.sum((y_trues == 1) & (preds == 0)))
        tp = int(np.sum((y_trues == 1) & (preds == 1)))
        tn = int(np.sum((y_trues == 0) & (preds == 0)))

        results.append({
            "perturbation_key": p_key,
            "perturbation_desc": p_desc,
            "mean_score": round(float(mean_score), 4),
            "mean_nominal_score": round(float(mean_nom_score), 4),
            "mean_defect_score": round(float(mean_def_score), 4),
            "accuracy_pct": round(float(acc), 1),
            "tp": tp, "tn": tn, "fp": fp, "fn": fn
        })

        print(f"  [{p_desc:<28}] Mean: {mean_score:.4f} (Nom: {mean_nom_score:.4f}, Def: {mean_def_score:.4f}) | Acc: {acc:.1f}% | FP: {fp}, FN: {fn}")

    out_csv = r"release\phase53_final_validation\cashew_robustness_results.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved robustness sensitivity results to: {out_csv}")

if __name__ == "__main__":
    main()
