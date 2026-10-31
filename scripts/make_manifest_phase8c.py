"""
make_manifest_phase8c.py
Generates cryptographic SHA-256 manifest for Phase 8C MACBA Equivalence deliverables.
"""

import os
import hashlib
import json
import time

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    target_dir = "research/phase8c_macba_equivalence"
    files = [
        "BL6_MACBA_DECISION_TRACE.csv",
        "MATHEMATICAL_EQUIVALENCE_ANALYSIS.md",
        "SYMMETRIC_COST_DISCREPANCY.md",
        "CONSTRAINT_NOVELTY_ASSESSMENT.md",
        "CORRECTED_STATISTICAL_CLAIMS.md",
        "FINAL_RESEARCH_GATE.md",
        "SUMMARY_EQUIVALENCE_METRICS.csv"
    ]

    manifest = {
        "phase": "8C",
        "phase_name": "MACBA Equivalence and Novelty Gate",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "gate_decision": "STANDARD METHOD EQUIVALENCE",
        "files": []
    }

    for fname in files:
        fpath = os.path.join(target_dir, fname)
        if os.path.exists(fpath):
            sha = compute_sha256(fpath)
            size = os.path.getsize(fpath)
            manifest["files"].append({
                "filename": fname,
                "relative_path": fpath.replace("\\", "/"),
                "sha256": sha,
                "size_bytes": size
            })
            print(f"{fname}: {size} bytes | SHA256: {sha}")
        else:
            print(f"WARNING: Missing file {fpath}")

    out_path = os.path.join(target_dir, "ARTIFACT_MANIFEST.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest successfully written to {out_path}")

if __name__ == "__main__":
    main()
