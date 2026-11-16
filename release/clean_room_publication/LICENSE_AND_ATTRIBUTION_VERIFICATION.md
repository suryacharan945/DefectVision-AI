# DefectVision AI — License, Attribution, and Intellectual Property Verification

**Document Version:** 1.0.0  
**Verification Date:** November 1, 2026  
**Auditor:** Open-Source Licensing & Compliance Preflight  
**Audit Scope:** Repository Source Code, External Dependencies, Dataset Rights, and Clean-Room Provenance  

---

## 1. Primary Repository License

DefectVision AI is released under the permissive **MIT License**:

```text
MIT License

Copyright (c) 2026 DefectVision AI Authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

The MIT License applies to all original source code files in `DefectVisionAI/`, `frontend/`, `scripts/`, `tests/`, and all accompanying documentation.

---

## 2. Third-Party Software Dependency Audit

All runtime dependencies incorporated into `requirements.txt` and `package.json` have been verified for license compatibility with permissive open-source release:

| Component / Library | Version Specified | License Type | Distribution Compatibility | Commercial Reuse Permitted |
|:---|:---:|:---:|:---:|:---:|
| **PyTorch (`torch`)** | `2.15.0+cpu` | BSD-3-Clause | Compatible | Yes |
| **TorchVision (`torchvision`)** | `0.29.2+cpu` | BSD-3-Clause | Compatible | Yes |
| **FAISS (`faiss-cpu`)** | `1.15.1` | MIT License | Compatible | Yes |
| **FastAPI** | `0.162.0` | MIT License | Compatible | Yes |
| **Uvicorn** | `0.54.0` | BSD-3-Clause | Compatible | Yes |
| **Pydantic** | `2.12.5` | MIT License | Compatible | Yes |
| **timm (PyTorch Image Models)** | `1.1.2` | Apache 2.0 | Compatible | Yes |
| **OpenCV (`opencv-python`)** | `4.11.0` | Apache 2.0 | Compatible | Yes |
| **Albumentations** | `1.4.15` | MIT License | Compatible | Yes |
| **Sentence-Transformers** | `2.7.0` | Apache 2.0 | Compatible | Yes |
| **Pandas / NumPy / SciPy** | Latest Stable | BSD-3-Clause | Compatible | Yes |
| **React / React-DOM** | `^18.3.1` | MIT License | Compatible | Yes |
| **Vite** | `^5.4.2` | MIT License | Compatible | Yes |
| **Lucide React** | `^0.441.0` | MIT License | Compatible | Yes |
| **TailwindCSS** | `^3.4.10` | MIT License | Compatible | Yes |

*Finding:* Zero GPL/AGPL copyleft libraries are linked into the application runtime, ensuring complete freedom for downstream users and commercial adopters.

---

## 3. Dataset Attribution & Intellectual Property Protection

To prevent copyright or non-commercial license violations, all proprietary and third-party benchmark datasets are strictly **excluded** from the clean-room release:

### 3.1 MVTec Anomaly Detection Dataset (MVTec AD)
- **Origin:** MVTec Software GmbH, Munich, Germany.
- **License:** MVTec AD Non-Commercial License (redistribution prohibited).
- **Compliance Action:**
  - Zero raw images (`.png`, `.jpg`) or ground-truth defect masks are bundled in the repository.
  - Zero memory banks (`.npy`) containing spatial patch embeddings are distributed.
  - Users are directed to official download channels at [https://www.mvtec.com/company/research/datasets/mvtec-ad](https://www.mvtec.com/company/research/datasets/mvtec-ad).
  - Automated reproduction scripts (`scripts/reproduce_memory_banks.py`) allow authorized users to build models locally from official archives.

### 3.2 Visual Anomaly Dataset (VisA)
- **Origin:** Amazon Research / VisA Authors.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Compliance Action:**
  - VisA was reserved as an independent generalization benchmark in research protocols.
  - Completely absent from both the clean release and the development runtime.

---

## 4. Demonstration Assets and Synthetic Provenance

In previous versions, UI previews utilized 15 small specimen crops from MVTec AD. In this clean-room release:
1. **100% Synthetic Replacement:** All 15 demonstration images in `frontend/public/outputs/similarity_search_samples/` are procedurally synthesized via `scripts/generate_synthetic_demo_samples.py`.
2. **Clear Watermarking:** Every sample is explicitly stamped with `"SYNTHETIC DEMO SPECIMEN"` and category labels.
3. **Clean-Room License:** All generated synthetic textures are released under the project's MIT License.

---

## 5. Certification of Clean-Room Provenance

The DefectVision AI repository is certified to contain:
- [x] Zero third-party proprietary weights or memory banks (`.pt`, `.pth`, `.npy`, `.npz`, `.faiss`).
- [x] Zero third-party proprietary dataset images or ground-truth segmentation masks.
- [x] Zero copyright-infringing literature surveys or publisher PDF preprints.
- [x] Zero personal environment variables, API tokens, or hardcoded absolute local paths.
- [x] 100% verified permissive open-source source code, build manifests, tests, and documentation.
