import hashlib
import json
import os

deliverables = [
    ("PHASE7C_PRECHECK.md", "VisA inventory verification, category name resolution, prediction parity, and metric disambiguation"),
    ("DENSITY_NORMALIZATION_IMPLEMENTATION.md", "Mathematical formulation and implementation of density-normalized CPND and boundary gating"),
    ("UNIT_TEST_RESULTS.md", "Verification ledger of the 8 unit and integration tests (100% pass)"),
    ("PAIRED_COMPARISON.csv", "Paired comparison with 2,000 bootstrap iterations and confidence intervals for Delta ECR and Delta DER"),
    ("BUDGET_SWEEP.csv", "Multi-budget performance across 1%, 2%, 5%, 10%, 15%, 20% review budgets"),
    ("ABLATION_RESULTS.csv", "Ablation results across 10 configurations covering normalization, gating, k, and dispersion type"),
    ("ERROR_ANALYSIS.md", "Theoretical and geometric analysis of CPND failure and coreset spacing mechanics"),
    ("COMPUTE_PROFILE.md", "Latency, memory residency, precomputation time, and throughput profiling"),
    ("FINAL_METHOD_DECISION.md", "Formal scientific evaluation against stop-rule gates recommending STOP CPND"),
    ("ARTIFACT_MANIFEST.json", "Cryptographic checksum ledger of all Phase 7C artifacts")
]

base_dir = "research/phase7c_density_normalized_cpnd"
manifest = {
    "phase": "Phase 7C - One Controlled CPND Revision and Final Method Decision",
    "protocol_reference": "research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json",
    "protocol_sha256": "effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1",
    "generated_at": "2026-10-31T23:28:00Z",
    "final_decision": "STOP CPND",
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

print(f"Phase 7C Manifest written with {len(manifest['artifacts'])} items.")
