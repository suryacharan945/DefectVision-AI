# DefectVision AI — Two-Minute Technical Demonstration Script

**Document Version:** 1.0.0  
**Target Duration:** Exactly 2 minutes (120 seconds)  
**Presenter:** AI/ML Systems Engineer  
**Audience:** Technical Hiring Managers, MLOps Leads, Quality Engineering Directors  

---

## Technical Setup Pre-Check (Before Starting Demo)
- Backend running on `http://127.0.0.1:8000` (Terminal 1)
- Frontend running on `http://127.0.0.1:5173` (Terminal 2)
- Browser open at `http://127.0.0.1:5173` showing green `CONNECTED` status badge

---

## Timed Script & Action Sequence

### [00:00 - 00:20] Hook & System Overview (20 seconds)

**Onscreen Action:**  
Display the clean DefectVision AI dashboard. Hover over the top-right green `CONNECTED` badge and category selector dropdown.

**Speaker Dialogue:**  
> *"In manufacturing visual inspection, automated computer vision models face a critical dilemma: achieving zero defect escapes causes false alarms that paralyze production lines, yet 100% manual review is cost-prohibitive.*  
> *This is DefectVision AI—an open-source industrial optical inspection platform that combines unsupervised memory-bank localization, dual explainability heatmaps, and decision-theoretic selective triage to optimize inspection economics."*

---

### [00:20 - 00:50] Real-Time Inference & Dual Explainability (30 seconds)

**Onscreen Action:**  
1. Select category **`bottle`** from dropdown.
2. Click preset pill: **`Broken Large (Defective)`**.
3. Click blue **`Run Optical Inspection`** button.
4. When results render (<50ms), drag the **Heatmap Opacity Slider** back and forth.
5. Scroll down to show the **`Top-3 Nearest Training Exemplars`** panel.

**Speaker Dialogue:**  
> *"Let's test live inference on an industrial glass bottle. Within 42 milliseconds on CPU, the engine scores the specimen against a WideResNet-50 patch memory bank indexed in FAISS.*  
> *It flags a Critical defect with a score of 4.51 against our 1.41 calibrated threshold.*  
> *Notice our dual explainability: the high-temperature Jet heatmap precisely isolates the structural fracture on the bottle shoulder. Below it, FAISS retrieves the three closest nearest-neighbor exemplars from the nominal training distribution, giving operators transparent visual evidence for why the region was flagged."*

---

### [00:50 - 01:15] Asynchronous Batch Processing & RAG Copilot (25 seconds)

**Onscreen Action:**  
1. Click **`Batch Inspection`** tab in the navigation bar.
2. Select 2 images and click **`Submit Batch Lot`**. Point to the real-time progress bar.
3. Switch back to main dashboard and expand the **`RAG Copilot`** panel in the bottom right.
4. Click preset query: *"What causes broken small defects and how do we prevent them?"*
5. Show the grounded remediation response.

**Speaker Dialogue:**  
> *"For high-volume production, the backend features asynchronous batch lot processing with live polling.  
> And when an operator discovers an anomaly, our grounded RAG Copilot queries an embedded defect engineering manual, diagnosing the root cause—such as localized stress concentration in mold thermal shock—and recommending immediate machine parameters to prevent recurring scrap."*

---

### [01:15 - 01:45] Decision-Theoretic Selective Triage (30 seconds)

**Onscreen Action:**  
1. Click **`Selective Inspection`** dashboard tab.
2. Drag the **Review Budget Slider ($K$)** from 5 up to 25 items.
3. Highlight how the priority list dynamically re-ranks specimens and updates the **Expected Cost Reduction** KPI ($+46.27\%$).

**Speaker Dialogue:**  
> *"The core research contribution is our selective triage engine. In factories with finite human review bandwidth, simple distance heuristics waste capacity verifying false alarms.*  
> *Using calibrated Platt probability models and asymmetric misclassification costs—where escaping a defect costs 20 times more than a false alarm—our engine triages parts by marginal loss reduction.*  
> *By sliding our inspection quota to 25 items, the system intercepts 10 critical false negatives that naive sampling missed, slashing realized quality loss by over 30%."*

---

### [01:45 - 02:00] Scientific Rigor & Wrap-Up (15 seconds)

**Onscreen Action:**  
Open `README.md` or the `Technical Case Study` tab showing the mathematical proof and test suites.

**Speaker Dialogue:**  
> *"What sets this project apart is scientific rigor: our technical case study formally proves the mathematical equivalence of this triage to Chow's 1970 Bayes risk rule and documents our negative findings on feature dispersion.*  
> *The entire stack—22 unit tests, full REST API, and React frontend—is open-source and reproducible with a single script. Thank you."*
