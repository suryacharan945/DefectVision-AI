# DefectVision AI — Public Repository Security & Integrity Audit

**Document Version:** 3.0.0  
**Date:** November 2026  
**Repository:** `https://github.com/suryacharan945/DefectVision-AI`  
**Target Branch:** `main`  
**Security Status:** **PASSED — ZERO SECRETS, COMPLIANT FILE SIZES, FULLY SANITIZED PATHS**  

---

## 1. Tracked Files & Binary Size Audit

GitHub imposes a strict 100 MB per-file limit. All files tracked in Git HEAD were audited using `git ls-tree -r -l HEAD` to verify compliance.

### 1.1 Largest Tracked Files in Repository

| File Path | Size (Bytes) | Size (MB) | GitHub 100MB Limit Compliance | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `DefectVisionAI/models/efficientnet_baseline_v3/last_checkpoint.pt` | 50,683,189 | 48.33 MB | **COMPLIANT (< 50% limit)** | PyTorch model checkpoint (v3) |
| `DefectVisionAI/models/patchcore/hazelnut/memory_bank.npy` | 42,267,776 | 40.31 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/screw/memory_bank.npy` | 34,681,472 | 33.07 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/carpet/memory_bank.npy` | 30,345,344 | 28.94 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/pill/memory_bank.npy` | 28,901,504 | 27.56 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/grid/memory_bank.npy` | 28,538,176 | 27.22 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/wood/memory_bank.npy` | 26,732,672 | 25.49 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/leather/memory_bank.npy` | 26,493,056 | 25.27 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/zipper/memory_bank.npy` | 26,011,776 | 24.81 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/tile/memory_bank.npy` | 24,926,336 | 23.77 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/cable/memory_bank.npy` | 24,204,416 | 23.08 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/metal_nut/memory_bank.npy` | 23,843,264 | 22.74 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/capsule/memory_bank.npy` | 23,722,112 | 22.62 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/transistor/memory_bank.npy` | 23,000,192 | 21.93 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/bottle/memory_bank.npy` | 22,638,720 | 21.59 MB | **COMPLIANT** | PatchCore coreset memory bank |
| `DefectVisionAI/models/patchcore/toothbrush/memory_bank.npy` | 6,502,016 | 6.20 MB | **COMPLIANT** | PatchCore coreset memory bank |

**Audit Outcome:**  
Zero files exceed 50 MB; zero files trigger Git LFS or GitHub push rejections.

---

## 2. Secrets and Credentials Scan

A comprehensive scan was conducted across all files for sensitive tokens, private keys, API secrets, and cloud credentials.

| Credential Type | Patterns Scanned | Matches Found | Status |
| :--- | :--- | :--- | :--- |
| **Vercel API Tokens** | `VERCEL_TOKEN`, `vc_token_*` | 0 | **CLEAN** |
| **AWS Credentials** | `AKIA[0-9A-Z]{16}`, `aws_secret_access_key` | 0 | **CLEAN** |
| **Private Keys** | `BEGIN RSA PRIVATE KEY`, `BEGIN PRIVATE KEY` | 0 | **CLEAN** |
| **HuggingFace Tokens** | `hf_[A-Za-z0-9]{34}` | 0 | **CLEAN** |
| **Generic Passwords** | `password=`, `api_key=`, `secret=` | 0 | **CLEAN** |

**Audit Outcome:**  
Zero credentials or live secrets exist in tracked files.

---

## 3. Host Path Sanitization Audit

All runtime source files (`.py`, `.jsx`, `.js`, `.json`) were verified to ensure no developer-specific or operating-system-specific absolute paths are hardcoded.

- **Python Backend Code:** Searched for `C:\Users\surya` across all `.py` files.  
  **Result:** **0 matches found.** All paths are resolved relative to `os.path.dirname(os.path.abspath(__file__))` or configured via `DEFECTVISION_DATA_DIR` and `DEFECTVISION_PROFILES_DIR`.
- **JSON Profile Configurations:** Verified that profile serializations (`profile.json`) strip runtime attributes like `_profile_dir` before writing to disk.
- **Frontend Code:** All API calls use relative paths (`/api/*`) or resolve dynamically from `import.meta.env.VITE_API_URL`.

---

## 4. Release Tag & Git Invariants Verification

- **Tag `v1.0.0-rc1`:** Confirmed preserved at commit `7a298d7cd778b9cb06580bee0922630ed91ab1a6`.
- **Target Branch:** Directly delivering to `main`. No extraneous Pull Requests opened.
- **Safety Recovery Branch:** `backup/pre-production-upgrade-5211076` created and intact.
