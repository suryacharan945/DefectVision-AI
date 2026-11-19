import os
import zipfile
import hashlib

ZIP_OUTPUT_PATH = r"C:\Users\surya\Downloads\DefectVisionAI_JEAS_Final_Review_Package.zip"
BASE_DIR = r"C:\Users\surya\Downloads\Mini Project"

# Mapping: (Source relative to BASE_DIR, Destination path inside ZIP)
PACKAGE_MAPPING = [
    ("release/JEAS_final_submission/README_FIRST.md", "DefectVisionAI_JEAS_Final_Review_Package/README_FIRST.md"),
    
    # 01_Manuscript
    ("release/JEAS_final_submission/DefectVisionAI_JEAS_Manuscript.pdf", "DefectVisionAI_JEAS_Final_Review_Package/01_Manuscript/DefectVisionAI_JEAS_Manuscript.pdf"),
    ("release/JEAS_final_submission/DefectVisionAI_JEAS_Manuscript.docx", "DefectVisionAI_JEAS_Final_Review_Package/01_Manuscript/DefectVisionAI_JEAS_Manuscript.docx"),
    ("release/JEAS_final_submission/DefectVisionAI_JEAS_Manuscript.tex", "DefectVisionAI_JEAS_Final_Review_Package/01_Manuscript/DefectVisionAI_JEAS_Manuscript.tex"),
    
    # 02_Submission
    ("release/JEAS_final_submission/JEAS_Cover_Letter.docx", "DefectVisionAI_JEAS_Final_Review_Package/02_Submission/JEAS_Cover_Letter.docx"),
    ("release/JEAS_final_submission/JEAS_REQUIREMENTS_FINAL_CHECK.md", "DefectVisionAI_JEAS_Final_Review_Package/02_Submission/JEAS_REQUIREMENTS_FINAL_CHECK.md"),
    ("release/JEAS_final_submission/SUBMISSION_CHECKLIST.md", "DefectVisionAI_JEAS_Final_Review_Package/02_Submission/SUBMISSION_CHECKLIST.md"),
    
    # 03_Research_Evidence
    ("release/JEAS_final_submission/EVIDENCE_AND_NUMERICAL_AUDIT.md", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/EVIDENCE_AND_NUMERICAL_AUDIT.md"),
    ("release/JEAS_final_submission/CORRECTION_REPORT.md", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/CORRECTION_REPORT.md"),
    ("release/JEAS_final_submission/FINAL_REVIEWER_REPORT.md", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/FINAL_REVIEWER_REPORT.md"),
    ("release/JEAS_final_submission/REFERENCES_VERIFICATION.md", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/REFERENCES_VERIFICATION.md"),
    ("release/JEAS_final_submission/ORIGINALITY_AND_AI_DISCLOSURE_REPORT.md", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/ORIGINALITY_AND_AI_DISCLOSURE_REPORT.md"),
    ("release/JEAS_final_submission/references.bib", "DefectVisionAI_JEAS_Final_Review_Package/03_Research_Evidence/references.bib"),
    
    # 04_Verification_Data
    ("release/phase49_independent_results/SPLIT_MANIFEST.csv", "DefectVisionAI_JEAS_Final_Review_Package/04_Verification_Data/SPLIT_MANIFEST.csv"),
    ("release/phase49_independent_results/TEST_PREDICTIONS.csv", "DefectVisionAI_JEAS_Final_Review_Package/04_Verification_Data/TEST_PREDICTIONS.csv"),
    ("release/final_18h_validation/latency_benchmark.csv", "DefectVisionAI_JEAS_Final_Review_Package/04_Verification_Data/latency_benchmark.csv"),
    ("release/JEAS_final_submission/morphology_summary.csv", "DefectVisionAI_JEAS_Final_Review_Package/04_Verification_Data/morphology_summary.csv"),
    
    # 05_Figures
    ("release/JEAS_final_submission/figures/fig1_architecture.png", "DefectVisionAI_JEAS_Final_Review_Package/05_Figures/fig1_architecture.png"),
    ("release/JEAS_final_submission/figures/fig2_confusion_matrices.png", "DefectVisionAI_JEAS_Final_Review_Package/05_Figures/fig2_confusion_matrices.png"),
    ("release/JEAS_final_submission/figures/fig3_roc_pr_curves.png", "DefectVisionAI_JEAS_Final_Review_Package/05_Figures/fig3_roc_pr_curves.png"),
    ("release/JEAS_final_submission/figures/fig4_defect_morphology.png", "DefectVisionAI_JEAS_Final_Review_Package/05_Figures/fig4_defect_morphology.png"),
    ("release/JEAS_final_submission/figures/fig5_cpu_latency.png", "DefectVisionAI_JEAS_Final_Review_Package/05_Figures/fig5_cpu_latency.png"),
    
    # 06_Final_QA
    ("release/JEAS_final_submission/FINAL_CONSISTENCY_REPORT.md", "DefectVisionAI_JEAS_Final_Review_Package/06_Final_QA/FINAL_CONSISTENCY_REPORT.md"),
    ("release/JEAS_final_submission/REMAINING_ISSUES.md", "DefectVisionAI_JEAS_Final_Review_Package/06_Final_QA/REMAINING_ISSUES.md"),
    ("release/JEAS_final_submission/PACKAGE_MANIFEST.md", "DefectVisionAI_JEAS_Final_Review_Package/06_Final_QA/PACKAGE_MANIFEST.md"),
]

def build_zip():
    print(f"Creating ZIP package at: {ZIP_OUTPUT_PATH}")
    os.makedirs(os.path.dirname(ZIP_OUTPUT_PATH), exist_ok=True)
    
    with zipfile.ZipFile(ZIP_OUTPUT_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for src_rel, arcname in PACKAGE_MAPPING:
            src_full = os.path.join(BASE_DIR, src_rel)
            if not os.path.exists(src_full):
                raise FileNotFoundError(f"Missing required package source file: {src_full}")
            zipf.write(src_full, arcname=arcname)
            print(f"Added: {arcname} (from {src_rel})")

    print(f"\nTesting ZIP integrity with testzip()...")
    with zipfile.ZipFile(ZIP_OUTPUT_PATH, 'r') as zipf:
        bad_file = zipf.testzip()
        if bad_file:
            print(f"FAILED: Corrupt file detected in ZIP: {bad_file}")
            return False
        else:
            print("ZIP integrity test: PASS (Zero corrupt entries)")
            infolist = zipf.infolist()
            print(f"Total entries in ZIP: {len(infolist)}")

    # Calculate SHA-256
    sha256 = hashlib.sha256()
    with open(ZIP_OUTPUT_PATH, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    zip_hash = sha256.hexdigest()
    zip_size = os.path.getsize(ZIP_OUTPUT_PATH)
    
    print(f"\n=== ZIP PACKAGE SUMMARY ===")
    print(f"Path: {ZIP_OUTPUT_PATH}")
    print(f"Size: {zip_size:,} bytes ({zip_size / (1024*1024):.2f} MB)")
    print(f"SHA-256: {zip_hash}")
    return True

if __name__ == "__main__":
    build_zip()
