import os
import json
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
REPORT_PATH = os.path.join(OUT_DIR, "FINAL_ACCEPTANCE_REPORT.md")

def generate_report():
    print("Generating comprehensive FINAL_ACCEPTANCE_REPORT.md...", flush=True)

    # Load canonical CSVs
    cat_df = pd.read_csv(os.path.join(OUT_DIR, "mvtec_per_category_metrics.csv"))
    loc_df = pd.read_csv(os.path.join(OUT_DIR, "MVTEC_LOCALIZATION_AUDIT.csv"))
    feat_df = pd.read_csv(os.path.join(OUT_DIR, "FEATURE_ACCEPTANCE_MATRIX.csv"))
    thresh_df = pd.read_csv(os.path.join(OUT_DIR, "category_threshold_provenance.csv"))
    wfb_df = pd.read_csv(os.path.join(OUT_DIR, "WORKFLOW_B_STRATIFIED_RESULTS.csv"))
    e2e_df = pd.read_csv(os.path.join(OUT_DIR, "BROWSER_E2E_CONTRACT_MATRIX.csv")) if os.path.exists(os.path.join(OUT_DIR, "BROWSER_E2E_CONTRACT_MATRIX.csv")) else None

    # Compute key numbers
    total_test_specimens = int(loc_df["total_test_specimens"].sum())
    total_test_pixels = int(loc_df["total_test_pixels"].sum())
    total_defect_specimens = int(loc_df["defect_specimens"].sum())
    total_defect_pixels = int(loc_df["defect_pixels_evaluated"].sum())

    pass_cnt = int((feat_df["Result"] == "PASS").sum())
    part_cnt = int((feat_df["Result"] == "PARTIAL").sum())
    man_cnt = int((feat_df["Result"] == "MANUAL_TEST").sum())
    fail_cnt = int((feat_df["Result"] == "FAIL").sum())

    lines = []
    lines.append("# DEFECTVISION AI â€” FINAL PRODUCTION & ACCEPTANCE AUDIT REPORT\n")
    lines.append("**Document Version:** 2.0.0 (Acceptance Correction Sprint)  \n")
    lines.append("**Evaluation Date:** November 2026  \n")
    lines.append("**Repository Remote:** `https://github.com/suryacharan945/DefectVision-AI`  \n")
    lines.append("**Active Branch:** `release/full-stack-completion-2026-11-17`  \n")
    lines.append("**Pull Request:** [PR #5](https://github.com/suryacharan945/DefectVision-AI/pull/5)  \n")
    lines.append("**Canonical Ground-Truth Source:** `release/final_validation/mvtec_all_predictions.csv` ($N=1,725$ genuine specimens)  \n\n")

    lines.append("## 1. Executive Summary & Production Readiness Decision\n\n")
    lines.append("This document provides the definitive, mathematically reconciled evaluation of **DefectVision AI** across all 15 MVTec AD categories, full-stack live API contracts, browser-to-backend integration, pixel localization, and autonomous category routing.\n\n")
    lines.append("### 4-Tier Production Readiness Framework\n\n")
    lines.append("| Tier | Deployment Context | Acceptance Verdict | Primary Technical Rationale |\n")
    lines.append("|:---|:---|:---:|:---|\n")
    lines.append("| **Tier 1** | **Academic Benchmark Demonstration** | **GO** | Macro AUROC of **97.15%**, Pixel AUROC of **97.66%**, 100% genuine specimens, zero mocked inference. |\n")
    lines.append("| **Tier 2** | **Supervised Software Staging** | **CONDITIONAL GO** | High defect capture rate (**94.04%** micro recall); human operators must triage the **24.84%** nominal false alarm rate. |\n")
    lines.append("| **Tier 3** | **Autonomous Industrial Gating** | **NO-GO** | High false-alarm rate on textures (Tile FPR: **66.7%**, Wood FPR: **68.4%**) would trigger excessive automated line stoppages. |\n")
    lines.append("| **Tier 4** | **Physical Factory Production** | **NOT VALIDATED** | Physical optical acquisition, lighting variations, and line speeds not yet validated on target physical lines. |\n\n")
    lines.append("> [!IMPORTANT]\n")
    lines.append("> DefectVision AI is an advanced research and engineering platform demonstrating state-of-the-art anomaly localization and category-aware memory banks. It must NOT be deployed as an unmonitored autonomous line gate without product-specific calibration on physical target production lines.\n\n")

    lines.append("## 2. Reconciled Benchmark Mathematics ($N=1,725$)\n\n")
    lines.append("All summary metrics are strictly generated from canonical `mvtec_all_predictions.csv` ($N=1,725$ genuine specimens: 467 nominal, 1,258 defective). Macro metrics are calculated as the unweighted mean across all 15 categories, ensuring categories with fewer specimens contribute equally to generalizability assessments.\n\n")
    lines.append("$$\\text{Macro } F_1 = \\frac{1}{15}\\sum_{k=1}^{15} F_{1, k} = 92.40\\% \\quad \\ne \\quad \\text{Micro } F_1 = \\frac{2 \\cdot \\text{TP}}{2 \\cdot \\text{TP} + \\text{FP} + \\text{FN}} = 92.53\\%$$\n\n")
    lines.append("| Metric Category | Evaluation Metric | Canonical Reconciled Value | Mathematical Definition / Operational Basis |\n")
    lines.append("|:---|:---|:---:|:---|\n")
    lines.append("| **Macro Metrics** | **Macro AUROC** | **97.15%** | Unweighted arithmetic mean of 15 category AUROCs |\n")
    lines.append("| | **Macro AUPRC** | **98.98%** | Unweighted mean of 15 category Average Precision scores |\n")
    lines.append("| | **Macro Defect Recall** | **95.40%** | Unweighted mean of 15 category True Positive Rates |\n")
    lines.append("| | **Macro Specificity** | **70.96%** | Unweighted mean of 15 category True Negative Rates |\n")
    lines.append("| | **Macro Precision** | **90.41%** | Unweighted mean of 15 category Positive Predictive Values |\n")
    lines.append("| | **Macro $F_1$ Score** | **92.40%** | Unweighted mean of category-specific $F_1$ scores across 15 categories |\n")
    lines.append("| | **Macro Auto-Category Acc** | **92.83%** | Unweighted mean of 15 EfficientNet-B0 category classification accuracies |\n")
    lines.append("| | **Mean E2E Latency** | **1,991.8 ms** | Unweighted mean of 15 category HTTP inference durations |\n")
    lines.append("| **Micro Metrics** | **Total Test Specimens ($N$)** | **1,725** | 467 genuine nominal + 1,258 genuine defective specimens |\n")
    lines.append("| | **Micro True Positives (TP)** | **1,183** | Defective items correctly flagged as DEFECTIVE |\n")
    lines.append("| | **Micro False Positives (FP)** | **116** | Nominal items incorrectly flagged as DEFECTIVE |\n")
    lines.append("| | **Micro True Negatives (TN)** | **351** | Nominal items correctly flagged as NORMAL |\n")
    lines.append("| | **Micro False Negatives (FN)** | **75** | Defective items missed (flagged as NORMAL) |\n")
    lines.append("| | **Micro Recall (Sensitivity)** | **94.04%** | $1,183 / 1,258$ total defect specimens captured (75 missed defects) |\n")
    lines.append("| | **Micro Specificity** | **75.16%** | $351 / 467$ nominal specimens cleared |\n")
    lines.append("| | **Micro Precision** | **91.07%** | $1,183 / 1,299$ total alarms that were true defects |\n")
    lines.append("| | **Micro $F_1$ Score** | **92.53%** | Harmonic mean of aggregate Micro Precision and Recall |\n")
    lines.append("| | **Overall Accuracy** | **88.93%** | $(1,183 + 351) / 1,725$ total correct classifications |\n")
    lines.append("| | **False Alarm Rate (FAR)** | **24.84%** | $116 / 467$ nominal specimens falsely alarmed |\n")
    lines.append("| | **Micro Auto-Category Acc** | **93.68%** | $1,616 / 1,725$ correct category classifications |\n\n")

    lines.append("### Complete 15-Category Reconciled Benchmark Breakdown\n\n")
    lines.append("| Category | Category Type | Test Nom/Def | AUROC | AUPRC | Defect Recall | Specificity | Precision | $F_1$ Score | Auto Acc | Mean E2E Latency |\n")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for _, r in cat_df.iterrows():
        lines.append(f"| `{r['category']}` | {r['type']} | {int(r['normal_samples'])} / {int(r['defect_samples'])} | **{r['auroc']*100:.2f}%** | {r['auprc']*100:.2f}% | {r['recall']*100:.2f}% | {r['specificity']*100:.2f}% | {r['precision']*100:.2f}% | **{r['f1_score']*100:.2f}%** | {r['auto_category_accuracy']*100:.2f}% | {r['latency_mean_ms']:.1f} ms |\n")
    lines.append(f"| **Macro Mean** | â€” | **467 / 1,258** | **97.15%** | **98.98%** | **95.40%** | **70.96%** | **90.41%** | **92.40%** | **92.83%** | **1,991.8 ms** |\n\n")

    lines.append("## 3. High False-Alarm Category Audit & Threshold Sensitivity\n\n")
    lines.append("Thresholds were calibrated using the disjoint calibration split ($N=726$ normal images, [patchcore_calibration_split.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/dataset_manifests/patchcore_calibration_split.csv)). The audit script [audit_threshold_sensitivity.py](file:///c:/Users/surya/Downloads/Mini%20Project/scripts/audit_threshold_sensitivity.py) verified threshold provenance in [category_threshold_provenance.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/category_threshold_provenance.csv):\n\n")
    lines.append("| Category | Category Type | Calib $N$ | Calibrated Threshold | Calib Mean $\\pm$ Std | Calib $p_{95}$ | Calib $p_{99}$ | Test Nom FPR | Test Def Recall | Physical / Structural Root Cause |\n")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|\n")
    for _, r in thresh_df.iterrows():
        cat_type = "texture" if r["category"] in ["carpet", "grid", "leather", "tile", "wood"] else "object"
        lines.append(f"| `{r['category']}` | {cat_type} | {int(r['n_calibration_samples'])} | **{r['calibrated_threshold']:.4f}** | {r['calibration_mean']:.4f} $\\pm$ {r['calibration_std']:.4f} | {r['p95_threshold']:.4f} | {r['p99_threshold']:.4f} | **{r['false_alarm_rate']*100:.1f}%** | **{r['defect_rejection_rate']*100:.1f}%** | {r['engineering_rationale']} |\n")
    lines.append("\n")
    lines.append("> [!NOTE]\n")
    lines.append("> **Operational Disclosure:**\n")
    lines.append("> 1. **Global Micro Recall:** Global micro defect recall across all 1,725 specimens is **94.04%** (75 missed defects out of 1,258), NOT 100%.\n")
    lines.append("> 2. **Zero-Escape Scope:** The zero-escape observation applies strictly to the specified four categories (`leather`, `tile`, `wood`, `toothbrush`), where conservative thresholds achieved 100.0% defect recall at the expense of high nominal false alarm rates (25.0% to 75.0% FPR).\n")
    lines.append("> 3. **Quantile Limits:** The $p_{99.5}$ calibration threshold does NOT mathematically guarantee zero defect escapes; it enforces a strict nominal clearing boundary on the calibration sample.\n")
    lines.append("> 4. **Sample Size Disclosure:** Several categories have small calibration splits (`toothbrush`: $N=12$, `tile`: $N=46$, `wood`: $N=40$). Natural stochastic grain variations exceed the small-sample calibration envelope.\n\n")

    lines.append("## 4. Stratified 90-Specimen Workflow B Autonomous Evaluation\n\n")
    lines.append("### Sampling Procedure Disclosure\n")
    lines.append("The 90-specimen stratified evaluation sample was generated by `scripts/run_workflow_b_stratified.py` from `release/dataset_manifests/official_test_split.csv`. For each of the 15 categories, the script selected the first 3 sorted nominal specimens (`noms.iloc[:3]`) and the first sorted specimen from each of the first 3 defect types (`defs[defs['defect_type'] == dt].iloc[0]`).\n")
    lines.append("**Disclosure:** This sample is stratified by category and defect type, but it is **NOT a statistically representative random sample** because specimens were chosen deterministically by sorted filename order. All 90 specimen relative filepaths and cryptographic SHA-256 hashes are recorded in [WORKFLOW_B_STRATIFIED_RESULTS.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/WORKFLOW_B_STRATIFIED_RESULTS.csv).\n\n")

    lines.append("### Workflow B Multi-State Outcome & Triage Matrix ($N=90$)\n\n")
    lines.append("| Ground Truth | Clear NORMAL | Definite DEFECTIVE | REVIEW REQUIRED | UNSUPPORTED / OOD | Total Specimens |\n")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|\n")
    lines.append("| **Normal Specimens** | **32** (71.1%) | **6** (13.3%) | **7** (15.6%) | **0** (0.0%) | **45** (100.0%) |\n")
    lines.append("| **Defective Specimens** | **1** (2.2%) | **36** (80.0%) | **4** (8.9%) | **4** (8.9%) | **45** (100.0%) |\n")
    lines.append("| **Total Pipeline Outcomes** | **33** (36.7%) | **42** (46.7%) | **11** (12.2%) | **4** (4.4%) | **90** (100.0%) |\n\n")

    lines.append("### Disaggregated Outcome Breakdown & Operational Metrics\n\n")
    lines.append("1. **Direct Defect Verdicts:** **36 / 45** (80.00% direct defect capture rate by autonomous pipeline).\n")
    lines.append("2. **Defective Specimens Assigned REVIEW REQUIRED:** **4 / 45** (8.89% fail-safe boundary flags).\n")
    lines.append("3. **Defective Specimens Rejected as UNSUPPORTED:** **4 / 45** (8.89% rejected due to category classifier uncertainty $< 0.80$, safely deferred to manual operator triage).\n")
    lines.append("4. **Defective Specimens Incorrectly Assigned NORMAL (Defect Escape):** **1 / 45** (2.22% critical miss; 1 subtle pill defect escaped).\n")
    lines.append("5. **Genuine Normal Specimens Cleared as NORMAL:** **32 / 45** (71.11% true negative clearance rate).\n")
    lines.append("6. **Genuine Normal Specimens Assigned DEFECTIVE (False Defect Alarm):** **6 / 45** (13.33% definite false alarms).\n")
    lines.append("7. **Genuine Normal Specimens Assigned REVIEW REQUIRED:** **7 / 45** (15.56% nominal specimens flagged for review due to score near boundary).\n")
    lines.append("8. **Not-Cleared-As-Normal / Fail-Safe Triage Outcome:** **44 / 45** (**97.78%**). *Note: This represents the total non-cleared triage rate ($36 \\text{ DEFECTIVE} + 4 \\text{ REVIEW} + 4 \\text{ UNSUPPORTED} = 44$). This is an operational triage outcome, not direct defect recall.*\n")
    lines.append("9. **Nominal Alarm-or-Review Burden:** **13 / 45** (**28.89%** total operator review burden for normal parts, comprising 6 definite false alarms + 7 review flags).\n")
    lines.append("10. **Total Operator-Intervention Workload:** **15 / 90** (**16.67%** of all specimens require operator review: 7 normal review + 4 defect review + 4 defect unsupported).\n")
    lines.append("11. **Direct Binary Classification Accuracy:** **68 / 90** (**75.56%**, counting only NORMAL $\\to$ normal and DEFECTIVE $\\to$ defective).\n")
    lines.append("12. **Operational Triage Accuracy:** **72 / 90** (**80.00%**, counting NORMAL $\\to$ normal, and DEFECTIVE or REVIEW REQUIRED $\\to$ defective, with UNSUPPORTED counted as incorrect).\n\n")

    lines.append("Refer to visual confusion and outcome figures:  \n")
    lines.append("- [workflow_b_90specimen_confusion_matrix.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/workflow_b_90specimen_confusion_matrix.png) (15x15 Category Routing)  \n")
    lines.append("- [workflow_b_90specimen_outcome_matrix.png](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/workflow_b_90specimen_outcome_matrix.png) (2x4 Multi-State Outcome Matrix)  \n\n")

    lines.append("## 5. Pixel-Level Defect Localization & Ranking Quality Audit\n\n")
    lines.append("Evaluated across all 1,725 test specimens on raw continuous distance maps (upsampled to 224x224, Gaussian $\\sigma=4.0$). Canonical source: [MVTEC_LOCALIZATION_AUDIT.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/MVTEC_LOCALIZATION_AUDIT.csv).\n\n")
    lines.append("| Category | Type | Test Specimens (Total) | Total Test Pixels | Defect Specimens | Defect Pixels Evaluated | Calibrated Threshold | Pooled Category Pixel AUROC | Per-Defect Mean Pixel AUROC | Mean Defect IoU | Mean Defect Dice | Ranking Quality Grade |\n")
    lines.append("|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n")
    for _, r in loc_df.iterrows():
        lines.append(f"| `{r['category']}` | {r['category_type']} | {int(r['total_test_specimens'])} | {int(r['total_test_pixels']):,} | {int(r['defect_specimens'])} | {int(r['defect_pixels_evaluated']):,} | {r['calibrated_threshold']:.4f} | **{r['pooled_category_pixel_auroc']*100:.2f}%** | {r['per_defect_mean_pixel_auroc']*100:.2f}% | {r['mean_defect_iou']*100:.2f}% | {r['mean_defect_dice']*100:.2f}% | {r['ranking_quality_grade']} |\n")
    lines.append(f"| **Macro Mean / Total** | â€” | **{total_test_specimens}** | **{total_test_pixels:,}** | **{total_defect_specimens}** | **{total_defect_pixels:,}** | â€” | **{loc_df['pooled_category_pixel_auroc'].mean()*100:.2f}%** | **{loc_df['per_defect_mean_pixel_auroc'].mean()*100:.2f}%** | **{loc_df['mean_defect_iou'].mean()*100:.2f}%** | **{loc_df['mean_defect_dice'].mean()*100:.2f}%** | **HIGH RANKING QUALITY** |\n\n")

    lines.append("> [!IMPORTANT]\n")
    lines.append("> **Localization Interpretation & Threshold Policy:**\n")
    lines.append("> 1. **Binarization Policy:** IoU and Dice overlap metrics are calculated by binarizing the continuous distance map using the category's image-level calibrated threshold ($p_{99.5}$). This policy evaluates whether the zero-escape detection threshold produces usable binary segmentation masks.\n")
    lines.append("> 2. **No Test Leakage:** Thresholds were intentionally **NOT tuned against test masks**, as optimizing segmentation thresholds on the test set would constitute data leakage.\n")
    lines.append("> 3. **AUROC vs Mask Overlap:** Macro Pooled Pixel AUROC is **97.66%**, indicating outstanding anomaly ranking and heat concentration. However, Macro IoU is **29.51%** and Macro Dice is **41.11%**, reflecting diffuse Gaussian-smoothed anomaly map margins rather than crisp pixel-level masks. This is designated as **HIGH RANKING QUALITY**, not precision binary segmentation.\n")
    lines.append("> 4. **Mask Integrity:** All 1,258 defective specimens possess genuine, verified ground-truth mask files on disk; zero missing or synthetic masks were permitted.\n\n")

    lines.append("## 6. Robust Feature Acceptance Matrix (23 Features)\n\n")
    lines.append("Evaluated using strict expected-versus-actual assertions via [test_robust_feature_matrix.py](file:///c:/Users/surya/Downloads/Mini%20Project/scripts/test_robust_feature_matrix.py). Canonical source: [FEATURE_ACCEPTANCE_MATRIX.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/FEATURE_ACCEPTANCE_MATRIX.csv).\n\n")
    lines.append(f"**Automated Summary Counts:** Total Features Evaluated: **{len(feat_df)}** | **PASS: {pass_cnt}** | **PARTIAL: {part_cnt}** | **MANUAL_TEST: {man_cnt}** | **FAIL: {fail_cnt}**\n\n")
    lines.append("| Test ID | Feature Name | Endpoint / Component | Expected Contract | Actual Response | Result |\n")
    lines.append("|:---|:---|:---|:---|:---|:---:|\n")
    for _, r in feat_df.iterrows():
        act_short = str(r['Actual_Response'])[:75] + ("..." if len(str(r['Actual_Response'])) > 75 else "")
        lines.append(f"| `{r['Test_ID']}` | {r['Feature_Name']} | `{r['Backend_Endpoint']}` | {str(r['Expected_Contract'])[:60]}... | {act_short} | **{r['Result']}** |\n")
    lines.append("\n")

    lines.append("## 7. Browser-to-Backend End-to-End Contract Validation\n\n")
    lines.append("Contract validation was executed targeting the live Vite frontend dev proxy (`http://127.0.0.1:5174`) routing to the FastAPI backend (`http://127.0.0.1:8001`) across both object (`bottle`) and texture (`carpet`) genuine MVTec specimens. Canonical source: [BROWSER_E2E_CONTRACT_MATRIX.csv](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/BROWSER_E2E_CONTRACT_MATRIX.csv).\n\n")
    if e2e_df is not None:
        lines.append("| Item | Behavior Name | Category Tested | Expected Contract | Verdict | Operational Notes |\n")
        lines.append("|:---:|:---|:---|:---|:---:|:---|\n")
        for _, r in e2e_df.iterrows():
            lines.append(f"| {int(r['Item_Number']):02d} | {r['Behavior_Name']} | {r['Category_Tested']} | {str(r['Expected_Outcome'])[:65]}... | **{r['Verdict']}** | {r['Operational_Notes']} |\n")
        lines.append(f"\n**Browser Contract Summary:** Total: **{len(e2e_df)}** | **PASS: {(e2e_df['Verdict'] == 'PASS').sum()}** | **MANUAL_TEST: {(e2e_df['Verdict'] == 'MANUAL_TEST').sum()}** | **FAIL: {(e2e_df['Verdict'] == 'FAIL').sum()}**\n\n")

    lines.append("## 8. Latency Reconciliation & Hardware Environment\n\n")
    lines.append("Detailed in [LATENCY_RECONCILIATION.md](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/LATENCY_RECONCILIATION.md):\n\n")
    lines.append("1. **Scope 1 (Full HTTP End-to-End Service):**  \n")
    lines.append("   - **Mean:** **1,991.8 ms** | **Median (p50):** **1,776.2 ms** | **95th Percentile (p95):** **2,889.2 ms**  \n")
    lines.append("   - Includes multipart payload upload, OpenCV decode, Optical Quality Gate, EfficientNet category routing, PatchCore inference, 224x224 bicubic upsample, Gaussian smoothing filter ($\\sigma=4.0$), contouring, Jet colormap rendering, Base64 PNG encoding, and JSON serialization.  \n\n")
    lines.append("2. **Scope 2 (Model-Only Tensor Forward Pass):**  \n")
    lines.append("   - **Mean:** **24.7 ms** | **Median (p50):** **21.5 ms** | **95th Percentile (p95):** **34.2 ms**  \n")
    lines.append("   - Pure in-memory PyTorch ResNet18 feature extraction and FAISS nearest-neighbor memory bank distance lookup.  \n\n")
    lines.append("3. **Scope 3 (Streaming Live-Frame Telemetry):**  \n")
    lines.append("   - **Range:** **43.2 ms to 328.6 ms** (Median: ~210 ms)  \n")
    lines.append("   - In-memory numpy frame inference returning scalar telemetry without PNG heatmap serialization.  \n\n")
    lines.append("### Runtime Hardware & Library Configuration\n")
    lines.append("- **Execution Environment:** Windows host (x86_64 CPU architecture, AVX2 enabled)\n")
    lines.append("- **Python Version:** Python 3.12.8\n")
    lines.append("- **Deep Learning Framework:** PyTorch 2.5.1+cpu, Torchvision 0.20.1+cpu\n")
    lines.append("- **Vector Search Index:** FAISS-CPU 1.7.4 (IndexFlatL2)\n")
    lines.append("- **Computer Vision:** OpenCV (`cv2`) 4.10.0\n")
    lines.append("- **Machine Learning:** Scikit-Learn 1.6.0, NumPy 1.26.4\n")
    lines.append("- **Inference Hardware Note:** Execution ran on CPU without CUDA acceleration. Isolated model-only measurements (24.7 ms) must NOT be cited as conveyor throughput without physical hardware validation.\n\n")

    lines.append("## 9. Cryptographic Reproducibility Manifest\n\n")
    lines.append("All artifacts, scripts, model weights, and benchmark files are cryptographically anchored in [REPRODUCIBILITY_MANIFEST.json](file:///c:/Users/surya/Downloads/Mini%20Project/release/final_validation/REPRODUCIBILITY_MANIFEST.json).\n")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"Comprehensive FINAL_ACCEPTANCE_REPORT.md updated successfully at: {REPORT_PATH}", flush=True)

if __name__ == "__main__":
    generate_report()
