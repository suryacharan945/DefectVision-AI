"""
make_manifest_release.py
Generates cryptographic SHA-256 manifest for release open-source readiness deliverables.
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
    target_dir = "release/open_source_readiness"
    files = [
        "RELEASE_AUDIT.md",
        "TEST_RESULTS.md",
        "MODEL_AND_DATA_PROVENANCE.md",
        "TECHNICAL_CASE_STUDY.md",
        "DEMO_SCRIPT.md",
        "INTERVIEW_PREPARATION.md",
        "RELEASE_CHECKLIST.md",
        "FINAL_RELEASE_DECISION.md"
    ]

    manifest = {
        "suite": "Open-Source Release Readiness",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "final_decision": "READY FOR PUBLIC OPEN-SOURCE RELEASE",
        "status": "Advanced Research Prototype",
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
