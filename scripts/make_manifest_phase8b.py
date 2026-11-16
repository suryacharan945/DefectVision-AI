import hashlib
import json
import os

deliverables = [
    ("NOVELTY_AND_LITERATURE_AUDIT.md", "Publisher-verified literature audit and de-hyping analysis"),
    ("SPLIT_AND_LEAKAGE_AUDIT.md", "Group-aware split specification, error breakdown, and anti-leakage audit"),
    ("CORRECTED_PROBLEM_FORMULATION.md", "Decision-theoretic loss reduction derivation under imperfect human review"),
    ("STRONG_BASELINE_SPECIFICATION.md", "Mathematical specifications of the 8 benchmark allocation policies"),
    ("FEASIBILITY_RESULTS.csv", "Multi-budget feasibility benchmark across all 8 policies and budget levels"),
    ("PAIRED_POLICY_COMPARISON.csv", "2,000 paired bootstrap resamples comparing MACBA against all baselines"),
    ("COST_SENSITIVITY_RESULTS.csv", "Cost sensitivity sweep across asymmetric loss ratios lambda in {1, 5, 20, 50, 100}"),
    ("PROTOCOL_AMENDMENT.md", "Formal changelog from Protocol V3.0 to V3.1"),
    ("PROPOSED_PROTOCOL_V3_1.json", "Amended prospective research protocol specification (SHA-256: 7d6b8a11...)"),
    ("FINAL_FEASIBILITY_DECISION.md", "Executive feasibility evaluation recommending PROCEED TO FULL DEVELOPMENT"),
    ("ARTIFACT_MANIFEST.json", "Cryptographic checksum ledger of all Phase 8B artifacts")
]

base_dir = "research/phase8b_macba_feasibility"
manifest = {
    "phase": "Phase 8B - MACBA Protocol Correction and Leakage-Free Feasibility",
    "protocol_reference": "research/phase8b_macba_feasibility/PROPOSED_PROTOCOL_V3_1.json",
    "protocol_sha256": "7d6b8a113d4fba6ce34b74d4b98cbc614d650993e761b1a09e590d4cdfb994f0",
    "generated_at": "2026-10-31T23:44:00Z",
    "final_decision": "PROCEED TO FULL DEVELOPMENT",
    "artifacts": []
}

for filename, desc in deliverables[:-1]:
    filepath = os.path.join(base_dir, filename)
    with open(filepath, "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()
    manifest["artifacts"].append({
        "file": filename,
        "path": filepath.replace("\\", "/"),
        "sha256": sha,
        "size_bytes": len(data),
        "description": desc
    })

manifest_path = os.path.join(base_dir, "ARTIFACT_MANIFEST.json")
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

with open(manifest_path, "rb") as f:
    self_data = f.read()
self_sha = hashlib.sha256(self_data).hexdigest()

manifest["artifacts"].append({
    "file": "ARTIFACT_MANIFEST.json",
    "path": manifest_path.replace("\\", "/"),
    "sha256": self_sha,
    "size_bytes": len(self_data),
    "description": deliverables[-1][1]
})

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Phase 8B Manifest written with {len(manifest['artifacts'])} items.")
