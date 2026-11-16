import hashlib
import json
import os

deliverables = [
    ("IMPLEMENTATION_REPORT.md", "Comprehensive mathematical and architectural specification of CPND"),
    ("UNIT_TEST_RESULTS.md", "Verification ledger of the 12 standalone unit and integration tests"),
    ("DEVELOPMENT_BASELINE_COMPARISON.csv", "Selective review baseline comparison at 10% budget on development partition"),
    ("REVIEW_BUDGET_RESULTS.csv", "Multi-budget selective review performance across 1%, 2%, 5%, 10%, 15%, 20%"),
    ("ABLATION_RESULTS.csv", "Ablation study across distance, PND, k values, aggregation modes, and calibration"),
    ("ERROR_ANALYSIS.md", "Detailed empirical and theoretical error analysis of CPND vs Baselines"),
    ("COMPUTE_PROFILE.md", "Latency, memory footprint, throughput, and scalability profiling of CPND"),
    ("RESEARCH_VIABILITY_DECISION.md", "Executive Q1-readiness viability evaluation recommending REVISE METHOD"),
    ("ARTIFACT_MANIFEST.json", "Cryptographic checksum ledger of all Phase 7B artifacts")
]

base_dir = "research/phase7b_cpnd_development"
manifest = {
    "phase": "Phase 7B - CPND Implementation and Development-Only Experiments",
    "protocol_reference": "research/protocols/Q1_EXPERIMENT_PROTOCOL_V2.json",
    "protocol_sha256": "effd05679ceb637073b6e7081633f2f51ebf2deaece0010041d33b8b07d19ab1",
    "generated_at": "2026-10-31T23:07:00Z",
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

print(f"Manifest written with {len(manifest['artifacts'])} items.")
