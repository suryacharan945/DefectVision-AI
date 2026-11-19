# DefectVision AI — Model Versioning & Artifact Immutability Policy

## 1. Frozen Benchmark Immutability Policy

DefectVision AI strictly enforces **Artifact Immutability** for the MVTec AD frozen benchmark models:

1. **Frozen Checkpoints:**
   - `DefectVisionAI/models/category_classifier/category_classifier.pth` (EfficientNet-B0 v3)
   - `DefectVisionAI/models/patchcore/<category>/memory_bank.npy` (15 Category Banks)
2. **Policy Guarantee:**
   - These files MUST NEVER be retrained, fine-tuned, or overwritten.
   - Any modification will invalidate the frozen baseline audit ($N=1,725$).
   - When new products or visual domains are introduced, they MUST be encapsulated as new **Production Profiles** under `models/production_profiles/<profile_id>/`.

---

## 2. Production Profile Versioning Convention

Product profiles follow Semantic Versioning (`vMAJOR.MINOR.PATCH-TAG`):

| Component | Meaning | Example Transition |
|:---|:---|:---|
| `MAJOR` | Architectural change in feature extractor or dimensionality | `v1.0.0-prod` -> `v2.0.0-prod` |
| `MINOR` | Additional reference images integrated, rebuilding memory bank | `v1.0.0-adapted` -> `v1.1.0-adapted` |
| `PATCH` | Threshold adjustment or ROI coordinate recalibration | `v1.1.0-adapted` -> `v1.1.1-adapted` |
| `TAG` | Validation status tag (`-adapted`, `-prod`, `-provisional`, `-audit`) | `v1.0.0-provisional` |

---

## 3. Cryptographic Artifact Integrity

Every profile directory includes a `manifest.json` recording SHA-256 checksums of all persisted artifacts:

```bash
sha256sum models/production_profiles/bottle_sku_btl_adapt_002/memory_bank.npy
# bae34d34eb8069da65d870c0ba64a5b5068f6c8479915c9460a3f077cfd11fa5
```

The system automatically checks these hashes upon profile loading to guard against silent data corruption.
