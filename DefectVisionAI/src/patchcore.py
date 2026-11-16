
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import numpy as np
import faiss
import cv2

class PatchCoreExtractor(nn.Module):
    def __init__(self, grid_size=28):
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
        fused = torch.cat([f2r, f3r], dim=1)
        return fused


def greedy_coreset_gpu(patch_embeddings, coreset_ratio=0.10, seed=42, device="cuda", log_every=2000):
    """
    GPU-vectorized greedy k-center coreset selection.
    Replaces the old O(N*K) pure-NumPy loop — same algorithm, ~50-100x faster
    because each iteration's distance-to-all-points update runs as one
    vectorized GPU tensor op instead of a Python-level NumPy call.
    """
    patches = torch.from_numpy(patch_embeddings).float().to(device)
    N, D = patches.shape
    K = max(1, int(N * coreset_ratio))

    rng = np.random.RandomState(seed)
    start_idx = int(rng.randint(N))
    selected_idx = [start_idx]

    min_dists = torch.norm(patches - patches[start_idx], dim=1)

    for i in range(1, K):
        next_idx = int(torch.argmax(min_dists).item())
        selected_idx.append(next_idx)
        new_dists = torch.norm(patches - patches[next_idx], dim=1)
        min_dists = torch.minimum(min_dists, new_dists)

        if log_every and i % log_every == 0:
            print(f"    coreset progress: {i}/{K}")

    coreset = patches[selected_idx].cpu().numpy()
    return coreset


class PatchCoreModel:
    def __init__(self):
        self.memory_bank = None
        self.index = None
        self.grid_size = None

    def fit(self, coreset_embeddings, grid_size):
        self.memory_bank = coreset_embeddings.astype(np.float32)
        self.grid_size = grid_size
        self.index = faiss.IndexFlatL2(self.memory_bank.shape[1])
        self.index.add(self.memory_bank)

    def score(self, patch_embedding):
        C, g, _ = patch_embedding.shape
        patches = patch_embedding.reshape(C, g * g).T.astype(np.float32)
        distances, _ = self.index.search(patches, k=1)
        dist_map = np.sqrt(np.clip(distances[:, 0], 0, None)).reshape(g, g)
        image_score = float(dist_map.max())
        return dist_map, image_score

    def save(self, path):
        np.save(path, self.memory_bank)

    def load(self, path, grid_size=28):
        self.memory_bank = np.load(path)
        self.grid_size = grid_size
        self.index = faiss.IndexFlatL2(self.memory_bank.shape[1])
        self.index.add(self.memory_bank)


def calibrate_score_map(dist_map, threshold=None, baseline_mean=None):
    """
    Calibrates PatchCore distance map relative to the category's calibrated anomaly threshold.
    Applies Gaussian smoothing to eliminate discrete patch artifacts.
    """
    import scipy.ndimage
    if dist_map.shape[0] == 28 and dist_map.shape[1] == 28:
        smooth_map = cv2.resize(dist_map, (224, 224), interpolation=cv2.INTER_CUBIC)
        smooth_map = scipy.ndimage.gaussian_filter(smooth_map, sigma=4.0)
    else:
        smooth_map = scipy.ndimage.gaussian_filter(dist_map.astype(np.float32), sigma=4.0)

    if threshold is None or threshold <= 0:
        denom = smooth_map.max() - smooth_map.min()
        return (smooth_map - smooth_map.min()) / denom if denom > 1e-6 else np.zeros_like(smooth_map)

    base = baseline_mean if baseline_mean is not None else threshold * 0.70
    cal_map = np.zeros_like(smooth_map, dtype=np.float32)

    # Below threshold: scaled smoothly in cool range [0.0, 0.45]
    below_mask = (smooth_map > base) & (smooth_map < threshold)
    cal_map[below_mask] = 0.45 * (smooth_map[below_mask] - base) / max(threshold - base, 1e-6)

    # Above threshold: scaled in defect range [0.50, 1.0]
    above_mask = smooth_map >= threshold
    headroom = max(threshold * 0.50, 1e-6)
    cal_map[above_mask] = 0.50 + 0.50 * np.clip((smooth_map[above_mask] - threshold) / headroom, 0.0, 1.0)

    return np.clip(cal_map, 0.0, 1.0)


def normalize_map(m):
    """Normalized distance map with smoothing to prevent circular patch artifacts."""
    import scipy.ndimage
    if m.shape[0] == 28 and m.shape[1] == 28:
        smoothed = cv2.resize(m, (224, 224), interpolation=cv2.INTER_CUBIC)
        smoothed = scipy.ndimage.gaussian_filter(smoothed, sigma=4.0)
    else:
        smoothed = scipy.ndimage.gaussian_filter(m.astype(np.float32), sigma=2.0)
    denom = smoothed.max() - smoothed.min()
    return (smoothed - smoothed.min()) / denom if denom > 1e-6 else np.zeros_like(smoothed)


def overlay_heatmap(image_rgb_uint8, score_map_norm, alpha=0.45, is_defective=True):
    """
    Overlays calibrated anomaly heatmap onto RGB image.
    When is_defective is False (nominal specimen), keeps the image pristine
    without misleading false-defect artifacts.
    """
    h, w = image_rgb_uint8.shape[:2]
    if score_map_norm.shape[:2] != (h, w):
        hm_res = cv2.resize(score_map_norm, (w, h), interpolation=cv2.INTER_CUBIC)
    else:
        hm_res = score_map_norm

    if not is_defective:
        # Nominal specimen: return unaltered specimen without false red patches
        return image_rgb_uint8.copy()

    hm_colored = cv2.applyColorMap(np.uint8(255 * np.clip(hm_res, 0.0, 1.0)), cv2.COLORMAP_JET)
    hm_rgb = cv2.cvtColor(hm_colored, cv2.COLOR_BGR2RGB)

    intensity_mask = np.clip((hm_res - 0.35) / 0.65, 0.0, 1.0)[:, :, np.newaxis]
    effective_alpha = alpha * intensity_mask

    overlay = (effective_alpha * hm_rgb + (1.0 - effective_alpha) * image_rgb_uint8).astype(np.uint8)
    return overlay


def map_iou(score_map_norm, gt_mask, threshold=0.5):
    sm = cv2.resize(score_map_norm, (gt_mask.shape[1], gt_mask.shape[0]))
    sm_bin = (sm >= threshold).astype(np.uint8)
    gt_bin = (gt_mask > 0).astype(np.uint8)
    intersection = np.logical_and(sm_bin, gt_bin).sum()
    union = np.logical_or(sm_bin, gt_bin).sum()
    if union == 0:
        return 0.0
    return intersection / union
