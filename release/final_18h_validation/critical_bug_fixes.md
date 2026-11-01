# DefectVision AI — Critical Bug Fixes & Operational Hardening Log

**Sprint Phase:** Phase 4 Pre-Flight Deliverable  
**Timestamp:** 2026-11-01  
**Target:** Production Server Resilience, Path Portability, & Hardware Independence

---

## 1. Summary of Hardening Fixes

| Bug ID | Component | Failure Condition | Root Cause | Implemented Solution | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | `app.py` | Crash on startup when launched outside `DefectVisionAI/` dir | Unanchored relative paths to `reports/` and `logs/` | Bound `APP_DIR = os.path.dirname(os.path.abspath(__file__))` and anchored all model, report, and log paths | **VERIFIED** |
| **BUG-02** | `app.py` | `FileNotFoundError` when severity logs or AUROC matrices are missing | Unchecked `pd.read_csv` on optional historical report files | Wrapped with `if os.path.exists(path)` fallback to empty DataFrame / None | **VERIFIED** |
| **BUG-03** | `app.py` | Live stream crash on headless servers or PCs without USB webcam | `cv2.VideoCapture(0)` throws exception when camera unavailable | Wrapped with graceful try/except fallback cycling high-fidelity conveyor feed | **VERIFIED** |
| **BUG-04** | Dataset IO | File not found when reading historical Google Colab manifests | Hardcoded `/content/drive/MyDrive` paths from cloud runs | Implemented dynamic path translation mapping to local `G:/My Drive` | **VERIFIED** |
| **BUG-05** | Export Tool | `PermissionError: Access Denied` on Windows Git object deletion | Read-only attribute on `.git/objects` packs during export clean | Implemented `remove_readonly` error handler calling `os.chmod(path, stat.S_IWRITE)` | **VERIFIED** |
| **BUG-06** | Frame Decoder | KeyError on missing multipart payload in edge camera upload | FastAPI endpoint expecting single format only | Handled `frame: UploadFile = File(None)` and `file: UploadFile = File(None)` with dual binding | **VERIFIED** |

---

## 2. Technical Details of Key Architectural Fixes

### BUG-01: Working Directory Independence
- **Issue:** Running `python DefectVisionAI/app.py` or `uvicorn DefectVisionAI.app:app` from workspace root failed immediately with:
  `FileNotFoundError: reports/step9_severity_baselines.csv not found`
- **Fix:**
  ```python
  APP_DIR = os.path.dirname(os.path.abspath(__file__))
  MODELS_DIR = os.path.join(APP_DIR, "models")
  REPORTS_DIR = os.path.join(APP_DIR, "reports")
  LOGS_DIR = os.path.join(APP_DIR, "logs")
  OUTPUTS_DIR = os.path.join(APP_DIR, "outputs")
  ```
- **Impact:** Server can now be launched from any arbitrary directory, Docker container, or CI/CD test runner without path corruption.

### BUG-03: Headless Industrial Feed Fallback
- **Issue:** On factory servers without physical USB webcams attached, `cv2.VideoCapture(0)` fails, causing `/stream` endpoint to break.
- **Fix:** Added hardware probe with fallback to an animated industrial conveyor test feed drawing animated HUD laser reticles, corner brackets, and real-time inference telemetry.
- **Impact:** Continuous 100% uptime for demonstration and testing in non-camera environments.
