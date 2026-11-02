# DefectVision AI — Phase 48: Data Provenance and Acquisition Gate Audit

**Document Type:** Dataset Provenance, Source Verification, and Acquisition Gate Audit  
**Phase:** Phase 48 — Controlled Independent Cashew Evaluation  
**Auditor:** Senior Computer Vision Research Engineer & Independent Evaluation Auditor  
**Date:** November 2, 2026  
**Git Baseline Commit:** `e022b03`  
**Status:** **ACQUISITION GATE BLOCKED — MANDATORY STOP RULE TRIGGERED**  

---

## 1. Executive Summary & Acquisition Gate Verdict

In accordance with Phase 48 Step 1 directives, an exhaustive forensic investigation was conducted to verify the official source, distribution architecture, licensing, and category-level availability of the Visual Anomaly (VisA) dataset.

### 1.1 Gate Verdict: **STOP RULE TRIGGERED**
- **Official Distribution Structure:** The official VisA dataset from Amazon Science is distributed exclusively as a single, monolithic 1.93 GB uncompressed tar archive (`VisA_20220922.tar`).
- **Category-Only Download Availability:** **NOT SUPPORTED.** The official AWS S3 bucket does not provide individual category archives (e.g., no `cashew.tar` or `cashew.zip`) or individual category S3 object prefixes.
- **Governing Directive Invoked:**
  > *"If only a large full-dataset archive is available, or acquisition cannot be verified within 20 minutes, STOP. Do not invent URLs or use unverified mirrors."*
  > *"You are NOT authorized to: Download the full VisA dataset merely to extract cashew if it exceeds the resource budget."*
- **Action Taken:** Execution was immediately halted prior to any unauthorized data download, extraction, or model execution. No unverified third-party mirrors or fabricated test outcomes were utilized.

---

## 2. Forensic Source Verification

### 2.1 Official Dataset Provenance
- **Primary Citation:** Zou et al., *"Spot-the-Difference: An Anomaly Detection Benchmark for Spotting Component and Surface Defects"*, European Conference on Computer Vision (ECCV), 2022.
- **Author Organization:** Amazon Science
- **Official Code Repository:** `https://github.com/amazon-science/spot-diff`
- **Official Open Data Registry:** AWS Open Data Sponsorship Program (`https://registry.opendata.aws/amazon-visual-anomaly/`)
- **Direct S3 URI:** `s3://amazon-visual-anomaly/` (Region: `us-west-2`)
- **Public HTTP URL:** `https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar`
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
  - Open academic and commercial use permitted with attribution.
  - Licensing integrity is verified.

---

## 3. Empirical S3 Bucket Verification

Using the verified local AWS CLI installation (`aws-cli/2.31.38`), the official S3 bucket was queried directly without credentials (`--no-sign-request`):

```bash
aws s3 ls --no-sign-request s3://amazon-visual-anomaly/
```

### Empirical Command Output:
```text
2022-09-17 03:37:55  1930393600  VisA.tar
2022-09-23 00:53:39  1929840640  VisA_20220922.tar
```

### Prefix Query Verification:
To verify whether uncompressed category folders were accessible as S3 prefixes, a targeted query was executed:
```bash
aws s3 ls --no-sign-request s3://amazon-visual-anomaly/cashew/
```
**Result:** Return Code 1 (Prefix does not exist). The S3 bucket contains strictly the two monolithic archive files and zero public object prefixes for individual categories.

---

## 4. Evaluation of Third-Party & Community Mirrors

Secondary web search identified several third-party community uploads on Hugging Face (e.g., `imaadd05/visa-anomaly-detection`, `BrachioLab/visa`, `zhKingg/VisA_Extended`) and Kaggle mirrors.

### Methodology Assessment:
1. **Unverified Provenance:** These repositories represent community-uploaded re-packagings with no cryptographic proof of bitwise fidelity against the original 2022 Amazon Science release.
2. **Strict Protocol Prohibition:** The prompt explicitly mandates:
   > *"Do not invent URLs or use unverified mirrors."*
3. **Audit Determination:** In accordance with research integrity standards, utilizing unofficial third-party mirrors to bypass official distribution constraints is **strictly barred**.

---

## 5. Storage and Resource Audit

- **Google Drive Storage:** `G:\My Drive\DefectVisionAI\` is online and accessible, with ample capacity for cloud staging.
- **Local Disk Impact:** Local workspace `C:\Users\surya\Downloads\Mini Project` remains clean.
- **Cashew Footprint in Tarball:** Within `VisA_20220922.tar`, `cashew` represents 600 images (500 nominal, 100 defective) totaling approximately $310\text{ MB}$ uncompressed.
- **Blocker:** Acquiring this $310\text{ MB}$ category through sanctioned official channels currently requires downloading the full $1.93\text{ GB}$ archive, which was explicitly unauthorized under the prompt's strict constraints.

---

## 6. Audit Conclusion & Stop Certification

Because category-only acquisition is not officially supported by Amazon Science, and downloading the full 1.93 GB archive was explicitly excluded from the current authorization scope, the Data Acquisition Gate is formally **CLOSED / BLOCKED**.

Execution has stopped cleanly at Step 1. In accordance with governance rules (*"Create result-specific files only if the experiment actually ran. Do not invent missing measurements or mark incomplete work as passed"*), no synthetic predictions, placeholder splits, or fabricated metrics have been produced.

**Auditor:** Senior Computer Vision Research Engineer & Independent Evaluation Auditor  
**Gate Status:** **HALTED AT STEP 1 (DATA ACQUISITION GATE)**
