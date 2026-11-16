# DefectVision AI — Git History Exposure & Forensic Lineage Audit

**Document Version:** 1.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** DevSecOps & Release Governance Gatekeeper  
**Repository:** `suryacharan945/DefectVision-AI`  
**Target Publication Scope:** Commit `7a4a2d3` / Release Preflight  

---

## 1. Executive Summary

This forensic audit inspected the entire reachable Git commit history (all 20 commits spanning from initial commit `f2a0662` to HEAD `7a4a2d3`) to determine whether restricted datasets, proprietary model weights, academic literature PDFs, university presentation decks, or private credentials exist in historical commits, even if excluded from the active tree.

### 1.1 Key Audit Findings
1. **Existing Remote Public State:** The remote repository (`https://github.com/suryacharan945/DefectVision-AI`) is **already configured as public** (`"private": false`). Commits 1 through 9 (`f2a0662` through `91d3743`) were previously pushed to `origin/main` on October 31, 2026.
2. **Historical Asset Exposure in Commits 1–2:** In the initial commit `f2a0662` (and commit `0a4c728`), 17 PDF/PPTX files (university slide decks, literature survey papers, and student project code listings) were tracked. Although removed from the active tree in commit `f6b1a80`, they remain recoverable in Git object storage for those historical commits.
3. **Model & Mask Longevity:** All 151 model artifacts (PatchCore memory banks, PaDiM parameters, autoencoders, FAISS indexes) and 33 MVTec ground truth masks were committed in commit 1 (`f2a0662`) and have remained in the tree across all 20 commits.
4. **Clean Unpushed Commit Delta:** The 11 unpushed commits (`7a8bed2` through `7a4a2d3`) on local `main` **introduced zero restricted weights, zero datasets, and zero credentials**. They consist exclusively of scientific documentation, unit tests, protocol specifications, research audit reports, and UI resilience guards.
5. **Zero Secret Leaks:** Full commit regex auditing confirmed that **no private API keys, cloud tokens, bearer JWTs, or passwords have ever been committed** in any of the 20 commits.

---

## 2. Commit-by-Commit Forensic Tree Audit

The table below catalogs every commit in the repository history, detailing the exact count of model artifacts, dataset masks, PDF/PPTX files, and environment files present in each commit's tree object:

| Commit Index | Commit SHA | Author Date | Commit Message Summary | Models Tracked | Dataset Masks | PDF/PPTX Files | Env Config Files | Remote Push Status |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | `f2a0662` | 2026-10-08 | Initial commit: DefectVision AI full-stack platform | 151 | 33 | **17** | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 2 | `0a4c728` | 2026-10-13 | docs & ui: link live Vercel deployment | 151 | 33 | **17** | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 3 | `f6b1a80` | 2026-10-13 | fix(vercel): remove presentation documents | 151 | 33 | **0** | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 4 | `b3f3c63` | 2026-10-13 | build(vercel): configure root postinstall hook | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 5 | `9f5d402` | 2026-10-13 | fix(offline): bundle benchmark data in-memory | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 6 | `2fd4867` | 2026-10-13 | build: add .vercelignore to exclude models | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 7 | `42facb4` | 2026-10-13 | fix(rag): resolve toLowerCase undefined error | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 8 | `4510815` | 2026-10-31 | chore: add CI workflow, tests, MIT license | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 9 | `91d3743` | 2026-10-31 | feat(release): v1.0.0 production verification | 151 | 33 | 0 | 1 (`.env.example`) | **Pushed to GitHub (`origin/main`)** |
| 10 | `7a8bed2` | 2026-10-31 | feat(hardening): finalize release verification | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 11 | `78ecd20` | 2026-10-31 | docs(research): formalize Q1 research freeze | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* (Tagged: `v1.0.0-research-prototype`) |
| 12 | `8276f26` | 2026-10-31 | docs(phase7a): complete research protocol audit | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 13 | `e013eff` | 2026-10-31 | feat(cpnd): implement CPND module & tests | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 14 | `8abbc7a` | 2026-10-31 | feat(phase7c): complete density-norm CPND | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 15 | `e00551c` | 2026-10-31 | docs(phase8a): complete literature review | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 16 | `87d9775` | 2026-10-31 | feat(phase8b): complete MACBA protocol audit | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 17 | `cae06dd` | 2026-10-31 | feat(phase8c): complete MACBA equivalence proof | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 18 | `68682ec` | 2026-11-01 | feat(phase9a): complete research reset | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 19 | `b9d087c` | 2026-11-01 | docs(release): complete open-source case study | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit* |
| 20 | `7a4a2d3` | 2026-11-01 | docs(release): complete release integrity gate | 151 | 33 | 0 | 1 (`.env.example`) | *Unpushed Local Commit (HEAD)* |

---

## 3. Inventory of Exposed Historical Artifacts

### 3.1 Historical Literature Survey & Presentation Artifacts (Commits `f2a0662` and `0a4c728`)
The following 17 binary documents exist in the Git history of commits 1 and 2:

1. **Root University Presentation Documents (7 files):**
   - `0th review Presentation Template.pdf` (303,813 bytes)
   - `DefectVision Ai Project Codes.pdf` (5,050,223 bytes)
   - `Mini Project Presentation .pdf` (370,933 bytes)
   - `Mini Project Presentation .pptx` (2,894,105 bytes)
   - `Project Description.pdf` (266,532 bytes)
   - `Project Timeline.pdf` (4,122,145 bytes)
   - `Project codes2.pdf` (4,311,939 bytes)
2. **Mini Project Literature Survey Papers (5 files):**
   - `Mini project literature survey/1610.02391v4.pdf` (Grad-CAM paper, 7,262,053 bytes)
   - `Mini project literature survey/2011.08785v1.pdf` (PaDiM preprint, 1,201,762 bytes)
   - `Mini project literature survey/2106.08265v2.pdf` (PatchCore preprint, 15,850,530 bytes)
   - `Mini project literature survey/2303.14535v3.pdf` (EfficientAD paper, 13,042,722 bytes)
   - `Mini project literature survey/Bergmann_MVTec_AD_--_A_Comprehensive_Real-World_Dataset_for_Unsupervised_Anomaly_CVPR_2019_paper.pdf` (4,248,056 bytes)
3. **Mini Project Paper First Pages (5 files):**
   - `Mini project paper 1st pages/Bergmann_MVTec_AD_..._CVPR_2019_paper.pdf` (740,785 bytes)
   - `Mini project paper 1st pages/EfficientAD.pdf` (197,896 bytes)
   - `Mini project paper 1st pages/Grad-CAM.pdf` (88,756 bytes)
   - `Mini project paper 1st pages/PaDiM.pdf` (522,558 bytes)
   - `Mini project paper 1st pages/Towards Total Recall in Industrial Anomaly Detection.pdf` (4,544,878 bytes)

*Assessment:* These 17 files were committed during early student project initialization and subsequently removed in commit `f6b1a80`. While academic papers are copyrighted by IEEE/CVF/arXiv, distributing preprints is standard in open-source research but creates unnecessary repository bloat (~60 MB).

### 3.2 Pretrained Model Weights and Ground Truth Masks (All Commits)
- **33 MVTec Ground Truth Masks:** Located under `DefectVisionAI/dataset/raw/mvtec/bottle/ground_truth/`.
- **151 Precomputed Model Files:** Located under `DefectVisionAI/models/` (15 PatchCore memory banks, 16 PaDiM parameter archives, 30 autoencoders, 7 EfficientNet checkpoints, 15 FAISS index binaries, 15 drift reference archives).

---

## 4. History Exposure Risk Assessment

| Exposure Category | Current State | Risk Severity | Safe Mitigation Options |
|:---|:---|:---:|:---|
| **API Keys / Secrets** | Zero secrets in any commit | **ZERO RISK** | Fully clean; no action required. |
| **Historical Presentation PDFs** | Deleted from HEAD in commit 3; reachable in commits 1–2 | **LOW (Repo Bloat)** | Retain in existing history OR filter via clean-room export. |
| **Pretrained Model Weights & Memory Banks** | Present in all 20 commits; already pushed to public GitHub | **MEDIUM (License Ambiguity)** | Publish under Non-Commercial Research Notice OR perform clean-room purge. |
| **MVTec Ground Truth Masks** | 33 masks present in all commits; already pushed to GitHub | **MEDIUM (Redistribution Terms)** | Remove from active HEAD and provide download instructions. |

---

## 5. Strategic Publication Decision

Because commits 1 through 9 are **already publicly visible on GitHub**, retroactively rewriting history on `origin/main` would require a disruptive `--force` push that invalidates existing clones.

Therefore, two safe, transparent publication strategies are formulated for user authorization (detailed in `SAFE_PUBLICATION_PLAN.md`):
1. **Linear Publication (Standard Open-Source Prototype):** Push the 11 unpushed commits directly to `origin/main`, providing complete scientific governance, audit reports, and prominent non-commercial research licensing terms.
2. **Clean-Room Repository Export (Pristine Commercial Release):** Export a clean-slate repository containing only the MIT-licensed code, tests, and documentation, excluding all binary weights, masks, and historical blobs, with automated download/reconstruction scripts.
