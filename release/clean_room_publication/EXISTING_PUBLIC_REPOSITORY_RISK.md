# DefectVision AI — Existing Public Repository Security & Exposure Audit

**Document Version:** 1.0.0  
**Audit Date:** November 1, 2026  
**Target Repository:** `https://github.com/suryacharan945/DefectVision-AI`  
**Classification:** HIGH-PRIORITY EXPOSURE AUDIT & MITIGATION PLAN  

---

## 1. Executive Summary & Exposure Identification

An authoritative audit of the existing remote repository `https://github.com/suryacharan945/DefectVision-AI.git` was conducted via the GitHub REST API and local Git object tree analysis.

### Key Audit Findings:
1. **Public Visibility:** The remote repository is currently **Public** (`"private": false`), meaning all committed assets are cloneable and indexed worldwide without authentication.
2. **Tracked Proprietary Artifacts in Git History:**
   - In commit `f2a0662` ("Initial commit"):
     - All 151 PatchCore `.npy` memory banks and PaDiM statistical arrays derived from MVTec AD were committed directly to the Git tree.
     - 33 MVTec ground truth defect segmentation masks were committed under `DefectVisionAI/dataset/`.
   - In commits `f2a0662` and `84918e7`:
     - 17 university literature survey presentations and scanned research paper first pages (`.pdf`, `.pptx`, ~60 MB) were committed.
   - In commit `f6b1a80` ("Remove heavy PDF literature survey files and large presentation decks"):
     - The PDF and PPTX files were removed from the working tree (`HEAD`), **but remain permanently stored in Git object history** (unpruned packfiles). Any user cloning the repository downloads the full history and can extract the original files via `git checkout f2a0662`.
3. **Crucial Scientific & Legal Reality:**
   Creating and publishing a separate clean-room repository (Option B) achieves a 100% clean, license-compliant codebase for new users, **but does NOT retroactively remove or remediate the exposure already present on `https://github.com/suryacharan945/DefectVision-AI`**.

---

## 2. Granular Inventory of Exposed Historical Assets

| Commit SHA | Commit Message | Files Exposed | Exposure Status at HEAD | Threat Assessment |
|:---|:---|:---|:---:|:---|
| `f2a0662` | Initial commit | 151 `.npy` memory banks, PaDiM arrays, 33 MVTec masks, 17 literature PDFs | Memory banks still at HEAD; PDFs deleted at HEAD but in packfile | **CRITICAL** (MVTec Non-Commercial license violation; copyright on literature) |
| `84918e7` | Add mini project presentation | Additional project presentation deck | Deleted at HEAD | **MEDIUM** (Internal coursework disclosure) |
| `f6b1a80` | Remove heavy PDF files | Removed from working tree | Dangling / historical object | **HIGH** (False sense of deletion; files fully recoverable via Git checkout) |
| `91d3743` | `origin/main` HEAD | Core application source and memory banks | Active on public `main` | **HIGH** (Memory banks publicly cloneable) |

---

## 3. Threat Modeling & Legal Implications

### 3.1 MVTec AD Non-Commercial License Compliance
- The MVTec Anomaly Detection dataset is licensed under a strict Non-Commercial License with redistribution restrictions.
- Distributing raw specimen images, ground truth masks, and precomputed feature banks (which encode direct spatial embeddings of the underlying training images) on a public GitHub repository violates Section 2 of the MVTec license agreement.

### 3.2 Academic Literature Copyright
- The 17 surveyed research papers included in the initial commits are protected by publisher copyright (IEEE, Springer, Elsevier). Public redistribution of publisher PDF preprints creates potential copyright liability.

---

## 4. Remediation Options & Actionable Protocols

To ensure complete compliance and eliminate exposure, the repository owner must execute one of the following remediation options:

### Option 1 (Recommended): Convert Existing Repository to Private, Publish Clean Room to New Repo
This is the safest, fastest, and lowest-risk approach:
1. **Immediately Make Existing Repo Private:**
   - Navigate to `https://github.com/suryacharan945/DefectVision-AI/settings`
   - Scroll to the **Danger Zone** at the bottom.
   - Click **Change repository visibility** -> Select **Make private**.
   - Confirm by typing repository name.
   - *Result:* All historical commits and packfiles become immediately inaccessible to the public.
2. **Publish the Verified Clean-Room Export to a Fresh Repository:**
   - Create a new public repository: `https://github.com/suryacharan945/DefectVision-AI-OpenSource` (or re-use `DefectVision-AI` after deleting the old repository).
   - Push only the clean-room commit (single initial commit with zero historical packfiles).

### Option 2: Complete History Rewrite via `git-filter-repo` (If URL must be preserved)
If the exact URL `https://github.com/suryacharan945/DefectVision-AI` must be maintained:
1. Clone a fresh mirror:
   ```bash
   git clone --mirror https://github.com/suryacharan945/DefectVision-AI.git repo-mirror
   cd repo-mirror
   ```
2. Purge all restricted file types and paths from history:
   ```bash
   pip install git-filter-repo
   git filter-repo --invert-paths \
     --path-glob '*.npy' \
     --path-glob '*.npz' \
     --path-glob '*.pt' \
     --path-glob '*.pth' \
     --path-glob '*.faiss' \
     --path-glob '*.pdf' \
     --path-glob '*.pptx' \
     --path-glob 'DefectVisionAI/dataset/*' \
     --path-glob 'Mini project*'
   ```
3. Force-push rewritten history:
   ```bash
   git remote add origin https://github.com/suryacharan945/DefectVision-AI.git
   git push origin --force --all
   git push origin --force --tags
   ```
4. Contact GitHub Support:
   - Request a cache prune / reflog purge for the repository to destroy dangling commit caches on GitHub's servers.

### Option 3: Complete Deletion of Old Repository
1. Navigate to Settings -> Danger Zone -> **Delete this repository**.
2. Create a brand-new repository with the exact same name `DefectVision-AI`.
3. Push the clean-room export as the first and only commit.

---

## 5. Owner Authorization Checklist

Before any public announcement or release:
- [ ] Repository owner has reviewed this risk audit.
- [ ] Repository owner has selected Option 1, Option 2, or Option 3.
- [ ] Existing repository visibility is changed to **Private** or repository is deleted.
- [ ] Clean-room repository is published with zero historical Git artifacts.
