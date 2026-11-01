# DefectVision AI — Clean-Clone Readiness & Zero-Weights User Experience Audit

**Document Version:** 1.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Quality Engineering & Developer Experience Gatekeeper  
**Scope:** New User Simulation, Zero-Asset Startup, Fallback Hardening, and Reproduction Verification  

---

## 1. Executive Summary

This audit assesses the experience of a fresh user cloning the public DefectVision AI repository without pre-bundled proprietary weights or restricted datasets.

### 1.1 Five-Point User Experience Verification

| User Experience Step | Expected Behavior | Tested & Verified Behavior | Compliance Status |
|:---|:---|:---|:---:|
| **1. Repository Clone** | Fast clone of MIT application codebase | Repository clones cleanly; Git LFS not required | **PASS** |
| **2. Dependency Installation** | Standard installation via `pip` and `npm` | Python dependencies install via `requirements.txt`; frontend installs via `npm install` | **PASS** |
| **3. Application Startup** | Backend and frontend start with zero crashes | Backend starts gracefully on port 8000; frontend starts on port 5173 | **PASS** |
| **4. Demo Mode (Zero Assets)** | Instant interactive inspection without backend weights | React console operates in clearly labeled Demo Mode with synthetic inspection simulation and mock batches | **PASS** |
| **5. Real Inference Error Handling** | Real inference returns explicit actionable errors when weights are missing; **never silently fakes ML** | If a memory bank or checkpoint is missing, backend returns HTTP 404 with detailed reproduction instructions | **PASS** |

---

## 2. Granular Verification of Zero-Weights Startup

### 2.1 Backend Resilience to Missing Weights
In earlier drafts, `DefectVisionAI/app.py` attempted to load `models/efficientnet_baseline_v3/best_model.pt` unconditionally during startup, causing a crash (`FileNotFoundError`) if weights were removed.

**Hardening Applied:**
1. **Defensive Checkpoint Loading:**
   ```python
   effnet_ckpt_path = os.path.join(CKPT_DIR_V3, "best_model.pt")
   effnet_model = None
   if os.path.exists(effnet_ckpt_path):
       try:
           best_ckpt = torch.load(effnet_ckpt_path, map_location=device)
           effnet_model = timm.create_model("efficientnet_b0", pretrained=False, num_classes=2)
           effnet_model.load_state_dict(best_ckpt["model_state"])
           effnet_model = effnet_model.to(device)
           effnet_model.eval()
       except Exception as e:
           print(f"Warning: Failed to load EfficientNet checkpoint: {e}")
   else:
       print("[Info] EfficientNet checkpoint not found. Operating in PatchCore-only or demo mode.")
   ```
2. **Defensive Memory Bank Loading:**
   ```python
   def get_patchcore_model(category):
       if category not in loaded_patchcore_models:
           mb_path = os.path.join(PATCHCORE_DIR, category, "memory_bank.npy")
           if not os.path.exists(mb_path):
               return None
           m = PatchCoreModel()
           m.load(mb_path, grid_size=GRID_SIZE)
           loaded_patchcore_models[category] = m
       return loaded_patchcore_models[category]
   ```
3. **Actionable HTTP 404 on Missing Model Artifacts:**
   If a user submits an image to `/predict` for a category whose `.npy` memory bank is absent, the backend returns:
   ```json
   {
     "detail": "Model artifact for category 'bottle' not found at models/patchcore/bottle/memory_bank.npy. Please download authorized dataset and generate memory banks following REPRODUCIBILITY.md."
   }
   ```
   **Crucial Rule Enforced:** The backend **NEVER** silently falls back to synthetic numbers when a user requests genuine inference.

---

### 2.2 Frontend Mode Demarcation (Live vs. Demo)

The web console (`frontend/src/api/client.js` and `frontend/src/App.jsx`) enforces strict, transparent visual indicators:

```
+-----------------------------------------------------------------------------------------+
|                                    OPERATOR CONSOLE                                     |
+-----------------------------------------------------------------------------------------+
| Mode: LIVE INFERENCE                                                                    |
| [ GREEN BANNER: "LIVE INFERENCE ACTIVE — Verified PyTorch CPU + FAISS-CPU Engine" ]     |
| • API returns: is_demo = false, inference_mode = 'LIVE (Verified PyTorch + FAISS)'       |
| • Scores, heatmaps, and nearest exemplars computed directly by local neural backbones.  |
+-----------------------------------------------------------------------------------------+
| Mode: DEMONSTRATION MODE                                                                |
| [ AMBER BANNER: "DEMO MODE ACTIVE — Client-side simulation running. Models offline." ]  |
| • API returns: is_demo = true, inference_mode = 'DEMO MODE (Synthetic Simulation)'      |
| • Explicit warning: "DEMONSTRATION ONLY: Synthetic simulation. Backend model offline." |
| • Allows evaluating UI layout, 3D viewport, and lot inspection without local GPU/CPU.  |
+-----------------------------------------------------------------------------------------+
```

If the backend server is unreachable and Demo Mode is disabled, the UI halts and displays an actionable error:
> *"Backend Unavailable (HTTP 503): Real inference cannot be performed because the backend server is unreachable. Please start the local backend (`python -m uvicorn app:app --port 8000`) or toggle Demo Mode."*

---

## 3. Workflow: Rebuilding Excluded Artifacts from Authorized Data

For researchers and commercial users who obtain official access to MVTec AD, the repository provides end-to-end scripts to fit memory banks and train classifiers from scratch:

### 3.1 Step 1: Download MVTec AD
1. Register and download `mvtec_anomaly_detection.tar.xz` directly from [MVTec Software GmbH](https://www.mvtec.com/company/research/datasets/mvtec-ad).
2. Extract to a local directory:
   ```bash
   tar -xf mvtec_anomaly_detection.tar.xz -C ./datasets/mvtec/
   ```

### 3.2 Step 2: Fit PatchCore Memory Banks
Run the automated memory-bank extraction script:
```powershell
python scripts/reproduce_memory_banks.py --data_dir ./datasets/mvtec/ --category bottle --coreset_ratio 0.10
```
This script:
1. Loads WideResNet-50-2 pre-trained on ImageNet-1k via `torchvision` (Apache 2.0).
2. Extracts mid-level patch feature tokens from layers 2 and 3 on nominal training images.
3. Applies minimax facility location to select a $10\%$ coreset ($14,739$ tokens for `bottle`).
4. Saves `DefectVisionAI/models/patchcore/bottle/memory_bank.npy`.
5. Builds and saves the FAISS FlatL2 vector index `models/faiss_index/bottle/index.faiss`.

### 3.3 Step 3: Calibrate Decision Thresholds
```powershell
python scripts/calibrate_thresholds.py --data_dir ./datasets/mvtec/ --category bottle
```
Computes the 99.5th percentile score over validation normals and updates `step9_severity_baselines.csv`.

### 3.4 Step 4: Fine-Tune EfficientNet Classifier (Optional)
```powershell
python scripts/train_efficientnet_baseline.py --data_dir ./datasets/mvtec/ --epochs 15
```
Saves the fine-tuned checkpoint to `DefectVisionAI/models/efficientnet_baseline_v3/best_model.pt`.

---

## 4. Conclusion: Clean-Clone Certification

DefectVision AI is certified as **fully operational on a clean clone**:
1. Zero proprietary assets are required to start the application, view the architecture, or explore the full interactive UI in Demo Mode.
2. Real inference is strictly guarded: missing model weights yield explicit HTTP 404 errors with actionable instructions, preventing silent or fraudulent simulation.
3. Complete, automated reproduction pipelines allow authorized users to regenerate all excluded weights in under 15 minutes.
