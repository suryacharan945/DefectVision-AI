# DefectVision AI — Clean-Install Verification & Reproduction Guide

**Document Version:** 2.0.0  
**Verification Date:** November 1, 2026  
**Auditor:** DevOps & Deployment Engineering  
**Platform Tested:** Windows 11 Pro 64-bit (Host), Python 3.12.9, Node.js v20.18.0, npm 10.9.2  
**Target Release:** `v1.0.0-research-prototype`  

---

## 1. System Requirements & Compatibility Matrix

| Component | Minimum Specification | Recommended Production Specification | Tested & Certified In Audit |
|:---|:---|:---|:---|
| **Operating System** | Windows 10 64-bit / Ubuntu 20.04 LTS / macOS 12+ | Windows 11 64-bit / Ubuntu 22.04 LTS | Windows 11 Pro 64-bit |
| **CPU Architecture** | x86_64 with AVX2 instruction support | 8+ physical cores (Intel Core i7/i9 or AMD Ryzen 7/9) | Intel/AMD x86_64 with AVX2 |
| **System Memory (RAM)** | 8 GB RAM | 16 GB RAM | 16 GB RAM |
| **Disk Storage** | 2.5 GB free disk space (models + dependencies) | 10 GB free SSD storage | NVMe SSD |
| **Python Runtime** | Python 3.10 | Python 3.11 or 3.12 | **Python 3.12.9** |
| **Node.js Runtime** | Node.js v18.0.0 LTS | Node.js v20.x or v22.x LTS | **Node.js v20.18.0** (npm 10.9.2) |
| **GPU Acceleration** | *Optional* (CPU is first-class citizen) | NVIDIA GPU with 8GB+ VRAM (CUDA 12.1) | CPU Mode (PyTorch 2.15.0+cpu) |

---

## 2. Step-by-Step Clean Installation Procedure

### 2.1 Repository Cloning
```bash
git clone https://github.com/suryacharan945/DefectVision-AI.git
cd DefectVision-AI
```

### 2.2 Python Virtual Environment Setup
Ensure Python 3.10–3.12 is available on system PATH:

**On Windows (PowerShell):**
```powershell
# Create isolated virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Upgrade core package managers
python -m pip install --upgrade pip setuptools wheel

# Install all certified Python dependencies
pip install -r requirements.txt
```

**On Linux / macOS:**
```bash
# Create isolated virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade package managers
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

*(Note for CUDA Users: To enable GPU acceleration instead of CPU inference, install CUDA-enabled PyTorch prior to requirements: `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121`)*

---

### 2.3 Frontend Dependencies & Build Verification

The root `package.json` contains automated scripts that delegate directly to the `frontend/` directory:

```bash
# Install frontend npm dependencies
npm install

# Test production build compilation
npm run build
```

**Verified Build Output:**
```
vite v8.3.0 building client environment for production...
✓ 2459 modules transformed.
rendering chunks...
dist/index.html                     2.30 kB │ gzip:   0.90 kB
dist/assets/index-8vyLY23k.css     78.50 kB │ gzip:  11.59 kB
dist/assets/index-D5wDqQ5e.js   1,400.74 kB │ gzip: 355.62 kB
✓ built in 4.25s
```

---

## 3. Automated Test Suite Execution

Verify installation integrity by running the test suites immediately after environment setup:

### 3.1 Run Unit Tests (22 Tests)
```powershell
python -m unittest discover -s tests -v
```
*Expected Result:* `Ran 22 tests in ~0.39s ... OK`

### 3.2 Verify PyTorch & FAISS Inference (1 Test)
```powershell
python scripts/test_backend_inference.py
```
*Expected Result:*
- Checks EfficientNet-B0 and Bottle PatchCore memory bank SHA-256 hashes.
- Loads FAISS FlatL2 index with 14,739 tokens.
- Executes forward inference on `bottle_demo.png` returning score `4.5088`.
- Outputs `--- INFERENCE TEST PASSED COMPLETELY ---`.

---

## 4. Application Launch Verification

### 4.1 Automated One-Click Launch (Windows)
Run the provided batch script from the repository root:
```cmd
start_defectvision.bat
```
This script automatically:
1. Validates `.venv` presence.
2. Starts FastAPI backend on `http://127.0.0.1:8000`.
3. Starts Vite dev server on `http://localhost:5173`.
4. Opens the default browser to the web console.

### 4.2 Manual Multi-Terminal Launch (Cross-Platform)

**Terminal 1 — FastAPI Backend:**
```bash
# Activate virtual environment
source .venv/bin/activate   # (or .\.venv\Scripts\Activate.ps1 on Windows)

# Start backend ASGI server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*Verification:* Navigate to `http://127.0.0.1:8000/docs` to inspect Swagger UI.

**Terminal 2 — React/Vite Frontend:**
```bash
npm run dev --prefix frontend
```
*Verification:* Navigate to `http://localhost:5173` to interact with the full operator console.

---

## 5. Troubleshooting & Environment Gotchas

| Symptom / Error | Root Cause | Verified Resolution |
|:---|:---|:---|
| `OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized.` | Conflicting OpenMP runtimes between PyTorch, OpenCV, and FAISS on Windows. | The application natively sets `os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"` in `backend/main.py`. If running standalone scripts, ensure this variable is exported before importing torch. |
| `Execution of scripts is disabled on this system` in PowerShell | Windows restricted script execution policy. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` prior to activating `.venv\Scripts\Activate.ps1`. |
| `No module named 'DefectVisionAI'` | Python path does not include project root. | Run Python commands from repository root with `PYTHONPATH=.` or rely on `backend/main.py` which dynamically appends the root directory. |
| `npm ERR! code ERESOLVE` during `npm install` | Strict peer dependency checks on React 19. | The project uses `--legacy-peer-deps` configured in root `package.json` scripts to allow smooth React 19 / Three.js tree compatibility. |
