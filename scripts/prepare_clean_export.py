#!/usr/bin/env python3
"""
DefectVision AI — Clean-Room Export and Audit Pipeline

Executes a strict allowlist-based export of approved source code, documentation,
tests, and synthetic assets into an isolated clean directory. Computes SHA-256
hashes and produces both APPROVED_EXPORT_MANIFEST.csv and EXCLUDED_ARTIFACTS_AUDIT.csv.
"""

import os
import sys
import shutil
import hashlib
import csv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_EXPORT_DIR = r"C:\Users\surya\Downloads\DefectVisionAI-CleanExport"
RELEASE_DIR = os.path.join(PROJECT_ROOT, "release", "clean_room_publication")

# Explicit Allowlist
ALLOWLIST_EXACT_FILES = [
    # Root documentation & configuration
    "README.md",
    "ARCHITECTURE.md",
    "MODEL_CARD.md",
    "DATASET_PROVENANCE.md",
    "REPRODUCIBILITY.md",
    "SECURITY.md",
    "LIMITATIONS.md",
    "DEMO_GUIDE.md",
    "LICENSE",
    ".gitignore",
    "requirements.txt",
    "package.json",
    "package-lock.json",
    # DefectVisionAI application & config
    "DefectVisionAI/app.py",
    "DefectVisionAI/models/rag_knowledge_base/defect_knowledge_base.csv",
    "DefectVisionAI/models/padim_threshold.json",
    "DefectVisionAI/reports/step9_severity_baselines.csv",
    "DefectVisionAI/reports/step8_model_comparison_FAIR.csv",
    "DefectVisionAI/reports/step8_per_category_auroc_matrix.csv",
    "DefectVisionAI/reports/step11_threshold_sensitivity.csv",
    "DefectVisionAI/logs/step9_severity_log.csv",
    "DefectVisionAI/logs/step12_drift_log_v3.csv",
    # Frontend config
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/vite.config.js",
    "frontend/index.html",
]

ALLOWLIST_DIRECTORIES = [
    # Source modules
    ("DefectVisionAI/src", (".py",)),
    ("DefectVisionAI/research/cpnd", (".py", ".csv")),
    # Synthetic samples
    ("DefectVisionAI/outputs/similarity_search_samples", (".png",)),
    ("DefectVisionAI/models/faiss_index", (".json",)),
    # Frontend source & public assets
    ("frontend/src", (".jsx", ".js", ".json", ".css")),
    ("frontend/public", (".svg", ".ico", ".png", ".jpg", ".json")),
    # Tests
    ("tests", (".py",)),
]

APPROVED_SCRIPTS = [
    "scripts/reproduce_memory_banks.py",
    "scripts/calibrate_thresholds.py",
    "scripts/train_efficientnet_baseline.py",
    "scripts/generate_synthetic_demo_samples.py",
    "scripts/test_app_startup.py",
    "scripts/test_backend_inference.py",
    "scripts/test_vite_proxy.py",
    "scripts/test_invalid_inputs_safety.py",
    "scripts/e2e_backend_test.py",
    "scripts/benchmark_inference_latency.py",
    "scripts/analyze_phase8c_equivalence.py",
]

APPROVED_RESEARCH_FILES = [
    "research/phase8c_macba_equivalence/BL6_MACBA_DECISION_TRACE.csv",
    "research/phase8c_macba_equivalence/ARTIFACT_MANIFEST.json",
    "research/phase8c_macba_equivalence/PHASE_8C_MACBA_EQUIVALENCE_REPORT.md",
    "research/phase9a_publication_feasibility/ARTIFACT_MANIFEST.json",
    "research/phase9a_publication_feasibility/RESEARCH_RESET_AND_PUBLICATION_FEASIBILITY_REPORT.md",
]

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_rationale(rel_path):
    if rel_path.startswith("frontend/src"):
        return "Frontend UI component / React state management", "Frontend Source"
    elif rel_path.startswith("DefectVisionAI/src"):
        return "Core backend Python vision & inspection library", "Backend Source"
    elif rel_path == "DefectVisionAI/app.py":
        return "FastAPI production inspection server & routing", "Backend Server"
    elif rel_path.startswith("tests/"):
        return "Automated unit and integration test suite", "Automated Tests"
    elif rel_path.startswith("scripts/"):
        return "Reproduction, benchmarking, and verification script", "Reproduction Scripts"
    elif rel_path.endswith(".md"):
        return "Verified technical documentation & reproduction guide", "Documentation"
    elif rel_path == "LICENSE":
        return "Permissive MIT License governing all project source code", "Legal"
    elif rel_path in (".gitignore", "requirements.txt", "package.json", "package-lock.json", "frontend/vite.config.js", "frontend/index.html", "frontend/package.json", "frontend/package-lock.json"):
        return "Standard dependency manifest and build configuration", "Configuration"
    elif "similarity_search_samples" in rel_path:
        return "Procedurally generated synthetic texture specimen for UI demonstration", "Demonstration Asset"
    elif "faiss_index" in rel_path and rel_path.endswith(".json"):
        return "Pre-computed gallery metadata mapping for nearest neighbor lookup", "Model Metadata"
    elif rel_path.startswith("research/"):
        return "Negative result audit and algorithmic equivalence evidence", "Research Archive"
    elif "defect_knowledge_base.csv" in rel_path:
        return "Industrial defect taxonomy knowledge base for RAG explanations", "Knowledge Base"
    elif "step9_severity_baselines.csv" in rel_path:
        return "Calibrated baseline score normalization statistics", "Calibration Data"
    elif "step8_model_comparison_FAIR.csv" in rel_path:
        return "Fair model comparison benchmark results table", "Benchmark Data"
    elif "step8_per_category_auroc_matrix.csv" in rel_path:
        return "Per-category AUROC benchmark matrix across evaluated architectures", "Benchmark Data"
    elif "step11_threshold_sensitivity.csv" in rel_path:
        return "Uncertainty threshold sensitivity analysis table", "Calibration Data"
    elif "step9_severity_log.csv" in rel_path:
        return "Historical inspection execution log for dashboard analytics", "Telemetry Log"
    elif "step12_drift_log_v3.csv" in rel_path:
        return "Statistical distribution drift monitoring telemetry log", "Telemetry Log"
    elif "cpnd" in rel_path:
        return "Patch-neighborhood dispersion negative result reference implementation and scores", "Research Artifact"
    elif "padim_threshold.json" in rel_path:
        return "Calibrated anomaly threshold configuration", "Configuration"
    elif rel_path.startswith("frontend/public"):
        return "Static web application branding asset", "Frontend Static Asset"
    return "Approved open-source asset", "Other"

def get_exclusion_reason(rel_path):
    if rel_path.endswith((".pt", ".pth")):
        return "Pre-trained deep neural network weights (MVTec AD derived)", "Regenerate via scripts/train_efficientnet_baseline.py"
    elif rel_path.endswith((".npy", ".npz")):
        return "PatchCore memory bank feature tokens (MVTec AD derived)", "Regenerate via scripts/reproduce_memory_banks.py"
    elif rel_path.endswith(".faiss"):
        return "Binary FAISS vector index (MVTec AD feature embeddings)", "Rebuild via scripts/reproduce_memory_banks.py"
    elif "DefectVisionAI/dataset" in rel_path or "dataset/raw" in rel_path:
        return "Third-party MVTec AD dataset images subject to Non-Commercial License", "Download authorized dataset directly from MVTec Software GmbH"
    elif "outputs/" in rel_path and ("heatmaps" in rel_path or "gradcam" in rel_path):
        return "Output heatmap visualization dumps from test specimen runs", "Generate locally via /predict or scripts/test_backend_inference.py"
    elif rel_path.endswith((".pdf", ".pptx", ".ppt")):
        return "University academic presentations and literature survey slides", "Retained in private academic archive"
    elif "Mini project" in rel_path:
        return "University coursework and literature survey directory", "Retained in private academic archive"
    elif rel_path.startswith(".env"):
        return "Environment configuration file containing local paths or secrets", "Create clean .env if needed"
    elif rel_path.startswith("delivery_24h"):
        return "Historical packaging workspace", "Internal development archive"
    elif rel_path.startswith("release/"):
        return "Release management audit logs and internal governance records", "Maintained in private repository root"
    elif "scripts/" in rel_path:
        return "Internal exploratory research / audit script not required for public runtime", "Retained in private research branch"
    elif "DefectVisionAI/logs" in rel_path:
        return "Development and calibration execution logs", "Retained in private development history"
    elif "batch_inspections" in rel_path:
        return "Local transient batch inspection runs", "Ephemeral inspection cache"
    return "Artifact not approved on public release allowlist", "Excluded by default under allowlist policy"

def remove_readonly(func, path, excinfo):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    print(f"DefectVision AI Clean Export Pipeline")
    print(f"Source Workspace: {PROJECT_ROOT}")
    print(f"Target Export: {TARGET_EXPORT_DIR}")
    print(f"Release Dir: {RELEASE_DIR}\n")

    # Clean target directory if exists
    if os.path.exists(TARGET_EXPORT_DIR):
        print(f"Cleaning existing export directory: {TARGET_EXPORT_DIR}")
        shutil.rmtree(TARGET_EXPORT_DIR, onerror=remove_readonly)
    os.makedirs(TARGET_EXPORT_DIR, exist_ok=True)

    # 1. Gather all files in project root
    all_workspace_files = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip git, venv, node_modules
        dirs[:] = [d for d in dirs if d not in (".git", ".venv", "venv", "node_modules", ".pytest_cache", "__pycache__", "dist", ".vercel")]
        for f in files:
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, PROJECT_ROOT).replace("\\", "/")
            all_workspace_files.append((rel_p, full_p))

    print(f"Total workspace files scanned (excluding venv/git/node_modules): {len(all_workspace_files)}")

    # 2. Match against allowlist
    approved_files = set()

    for rel_p in ALLOWLIST_EXACT_FILES:
        full_p = os.path.join(PROJECT_ROOT, rel_p)
        if os.path.isfile(full_p):
            approved_files.add(rel_p)

    for dir_rel, extensions in ALLOWLIST_DIRECTORIES:
        full_d = os.path.join(PROJECT_ROOT, dir_rel)
        if os.path.isdir(full_d):
            for root, dirs, files in os.walk(full_d):
                dirs[:] = [d for d in dirs if d not in ("__pycache__", "node_modules")]
                for f in files:
                    if f.endswith(extensions):
                        full_p = os.path.join(root, f)
                        rel_p = os.path.relpath(full_p, PROJECT_ROOT).replace("\\", "/")
                        approved_files.add(rel_p)

    for rel_p in APPROVED_SCRIPTS:
        full_p = os.path.join(PROJECT_ROOT, rel_p)
        if os.path.isfile(full_p):
            approved_files.add(rel_p)

    for rel_p in APPROVED_RESEARCH_FILES:
        full_p = os.path.join(PROJECT_ROOT, rel_p)
        if os.path.isfile(full_p):
            approved_files.add(rel_p)

    # 3. Categorize into Approved and Excluded
    approved_list = []
    excluded_list = []

    for rel_p, full_p in all_workspace_files:
        if rel_p in approved_files:
            # Double check no forbidden extension sneaked in
            if rel_p.endswith((".pt", ".pth", ".npy", ".npz", ".faiss", ".pdf", ".pptx")):
                print(f"SECURITY ALERT: Blocked forbidden extension from approved list: {rel_p}")
                excluded_list.append((rel_p, full_p))
            else:
                approved_list.append((rel_p, full_p))
        else:
            excluded_list.append((rel_p, full_p))

    print(f"Approved for clean export: {len(approved_list)} files")
    print(f"Excluded from clean export: {len(excluded_list)} files")

    # 4. Copy approved files to target export
    for rel_p, full_p in approved_list:
        dest_p = os.path.join(TARGET_EXPORT_DIR, rel_p)
        os.makedirs(os.path.dirname(dest_p), exist_ok=True)
        shutil.copy2(full_p, dest_p)

    # Create empty placeholder directories needed by backend
    os.makedirs(os.path.join(TARGET_EXPORT_DIR, "DefectVisionAI", "models", "patchcore"), exist_ok=True)
    os.makedirs(os.path.join(TARGET_EXPORT_DIR, "DefectVisionAI", "models", "efficientnet_baseline_v3"), exist_ok=True)
    os.makedirs(os.path.join(TARGET_EXPORT_DIR, "DefectVisionAI", "batch_inspections"), exist_ok=True)

    # Add a .gitkeep or README to the empty model dirs explaining zero-weight state
    for placeholder_dir in ["DefectVisionAI/models/patchcore", "DefectVisionAI/models/efficientnet_baseline_v3"]:
        info_file = os.path.join(TARGET_EXPORT_DIR, placeholder_dir, "WEIGHTS_README.md")
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(
                "# Model Weights Directory\n\n"
                "In accordance with open-source licensing and dataset protection guidelines, pre-trained weights and memory banks are excluded from this repository.\n\n"
                "To reproduce or generate weights from authorized data, follow instructions in `REPRODUCIBILITY.md`.\n"
            )

    # Re-scan export directory to verify exact files copied
    exported_files = []
    for root, dirs, files in os.walk(TARGET_EXPORT_DIR):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, TARGET_EXPORT_DIR).replace("\\", "/")
            exported_files.append((rel_p, full_p))

    # 5. Write APPROVED_EXPORT_MANIFEST.csv
    approved_csv_path = os.path.join(RELEASE_DIR, "APPROVED_EXPORT_MANIFEST.csv")
    with open(approved_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Relative Path", "File Category", "Size (Bytes)", "SHA-256 Checksum", "Allowlist Rationale"])
        for rel_p, full_p in sorted(exported_files):
            size = os.path.getsize(full_p)
            sha = compute_sha256(full_p)
            rationale, cat = get_rationale(rel_p)
            writer.writerow([rel_p, cat, size, sha, rationale])

    print(f"Generated: {approved_csv_path} ({len(exported_files)} entries)")

    # 6. Write EXCLUDED_ARTIFACTS_AUDIT.csv
    excluded_csv_path = os.path.join(RELEASE_DIR, "EXCLUDED_ARTIFACTS_AUDIT.csv")
    with open(excluded_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Relative Path", "Size (Bytes)", "SHA-256 Checksum", "Reason for Exclusion", "Actionable Remediation / Reproduction"])
        for rel_p, full_p in sorted(excluded_list):
            try:
                size = os.path.getsize(full_p)
                sha = compute_sha256(full_p)
            except Exception:
                size = 0
                sha = "ERROR_READING_FILE"
            reason, remediation = get_exclusion_reason(rel_p)
            writer.writerow([rel_p, size, sha, reason, remediation])

    print(f"Generated: {excluded_csv_path} ({len(excluded_list)} entries)")

    # 7. Safety Sanity Check: Ensure zero restricted files exist in export
    forbidden_hits = []
    for rel_p, full_p in exported_files:
        if rel_p.endswith((".pt", ".pth", ".npy", ".npz", ".faiss", ".pdf", ".pptx")):
            forbidden_hits.append(rel_p)
        if "defectvisionai/dataset/" in rel_p.lower() and not rel_p.endswith((".json", ".csv", ".md")):
            forbidden_hits.append(rel_p)
        if "raw/mvtec" in rel_p.lower():
            forbidden_hits.append(rel_p)

    if forbidden_hits:
        print("\nCRITICAL SECURITY FAILURE: Forbidden files detected in clean export:")
        for h in forbidden_hits:
            print(f"  FAILED: {h}")
        sys.exit(1)
    else:
        print("\nClean export safety check passed: 0 forbidden artifacts detected.")

if __name__ == "__main__":
    main()
