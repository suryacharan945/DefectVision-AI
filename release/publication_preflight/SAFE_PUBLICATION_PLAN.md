# DefectVision AI — Safe Public Release Strategy & Options Analysis

**Document Version:** 1.0.0  
**Audit Date:** November 1, 2026  
**Auditor:** Release Governance & Open-Source Strategy Gatekeeper  
**Current State:** Commit `7a4a2d3` / Working tree clean  
**Target Repository:** `https://github.com/suryacharan945/DefectVision-AI`  

---

## 1. Executive Summary & Dilemma Analysis

Prior to authorizing any Git push or release tag publication, project leadership must choose between three distinct publication pathways.

### 1.1 The Underlying Governance Dilemma
* The remote GitHub repository is **already public** and contains commits 1 through 9 (`f2a0662` to `91d3743`).
* Those historical commits already contain the 151 model files (memory banks, PaDiM weights), 33 MVTec masks, and 17 historical presentation/literature PDFs.
* The 11 unpushed commits on local `main` (`7a8bed2` to `7a4a2d3`) contain **zero restricted assets**; they consist exclusively of scientific audits, metric corrections, test suites, and documentation.

---

## 2. Comparison of the Three Safe Publication Strategies

```
+---------------------------------------------------------------------------------------------------+
|                                  STRATEGY COMPARISON OVERVIEW                                     |
+---------------------------------------------------------------------------------------------------+
| Feature / Attribute            | Strategy 1: Linear Push | Strategy 2: Clean Export | Strategy 3: Hybrid  |
+--------------------------------+-------------------------+--------------------------+---------------------+
| Target Remote Repository       | Existing repo           | New clean repository     | Existing repo       |
| History Rewriting Required?    | NO (Linear push)        | NO (Clean initial commit)| NO (Linear push)    |
| Breaks Existing Clones/Forks?  | NO                      | NO (Independent repo)    | NO                  |
| Pretrained Weights in Tree?    | Retained with Notice    | EXCLUDED completely      | Retained with Notice|
| Historical PDFs in History?    | In commits 1-2 only     | EXCLUDED completely      | In commits 1-2 only |
| Commercial Clarity             | Non-commercial notice   | 100% Pure MIT Clean      | Dual-license Notice |
| Implementation Effort          | 1 command (git push)    | 15 minutes export        | 1 command (git push)|
| Recommended For:               | Research / Academic PR  | Enterprise / Commercial  | Research Prototype  |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Granular Analysis of Each Strategy

### 3.1 Strategy 1: Linear Publication with Prominent Research Notice (Recommended for Research Prototype)
* **Mechanism:** Push the 11 unpushed commits directly to `origin/main` without rewriting history:
  ```powershell
  git tag -a v1.0.1-open-source -m "DefectVision AI v1.0.1: Open-Source Research Prototype & Integrity Gate"
  git push origin main --tags
  ```
* **Pros:**
  * Preserves unbroken, authentic commit lineage from initial prototype to final integrity gate.
  * Completely non-disruptive: does not require `--force` pushes or rebases.
  * Adds 800+ lines of rigorous provenance accounting, the 214-item model redistribution matrix, and the 8-metric grounding matrix.
  * Prominent disclaimers in `README.md`, `LICENSE`, and `MODEL_CARD.md` clearly state that code is MIT while bundled memory banks are for non-commercial academic research only.
* **Cons:**
  * Historical PDFs remain in Git object history for commits `f2a0662` and `0a4c728`.
  * Pretrained memory banks remain bundled in `DefectVisionAI/models/`.

---

### 3.2 Strategy 2: Clean-Room Repository Export (Recommended for Commercial Distribution)
* **Mechanism:** Create a pristine, standalone public repository (e.g. `suryacharan945/defectvision-core`) containing only the MIT-licensed application code, tests, documentation, and reproduction scripts, with zero binary weights or MVTec assets:
  ```powershell
  # 1. Create an isolated clean-export branch
  git checkout --orphan clean-release

  # 2. Remove all excluded binary artifacts
  git rm -r --cached DefectVisionAI/dataset/
  git rm -r --cached DefectVisionAI/models/patchcore/
  git rm -r --cached DefectVisionAI/models/padim/
  git rm -r --cached DefectVisionAI/models/autoencoder/
  git rm -r --cached DefectVisionAI/models/faiss_index/*/index.faiss
  git rm -r --cached DefectVisionAI/models/efficientnet_baseline*
  git rm -r --cached DefectVisionAI/models/*.pth DefectVisionAI/models/*.npz
  git rm -r --cached DefectVisionAI/outputs/

  # 3. Commit pure clean application
  git commit -m "feat: initial clean-room open-source release of DefectVision AI (MIT License)"

  # 4. Push to a new dedicated clean repository
  git remote add clean-origin https://github.com/suryacharan945/defectvision-core.git
  git push clean-origin clean-release:main --tags
  ```
* **Pros:**
  * 100% pure MIT-licensed codebase.
  * Zero MVTec AD derivative files, zero third-party specimen crops, and zero historical PDF bloat anywhere in history.
  * Completely safe for commercial evaluation, enterprise adoption, and derivative software packaging.
* **Cons:**
  * Requires setting up a second repository or executing a force-push that would rewrite the existing public repository.
  * Users must run `scripts/reproduce_memory_banks.py` locally to perform real inference (though Demo Mode functions immediately out-of-the-box).

---

### 3.3 Strategy 3: Hybrid Architecture (GitHub Releases Binary Assets)
* **Mechanism:** Linear push of the current tree, but moving the heavy `.npy` and `.pt` checkpoints into GitHub Release assets (`v1.0.1-open-source.tar.gz`) with an explicit click-through research license agreement.

---

## 4. Execution Recommendation & Action Plan

For the immediate objective of publishing DefectVision AI as a transparent, reproducible **research prototype and technical case study**:

1. **Recommended Approach:** **Strategy 1 (Linear Push with Dual-License Notice)**.
   * Reason: The repository is already public. Publishing the 11 unpushed commits provides the complete truth of the project: the CPND negative result, the MACBA equivalence proof, the VisA exposure reconciliation, and the metric grounding matrix.
2. **Next Steps (Awaiting User Command):**
   * If User selects **Strategy 1**: Tag `v1.0.1-open-source` and execute `git push origin main --tags`.
   * If User selects **Strategy 2**: Execute clean-room orphan branch export to a new repository.
   * **Absolute Constraint:** No push, tag creation, or history alteration will be performed until the user explicitly selects and authorizes a strategy.
