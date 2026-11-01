# DefectVision AI — Industrial Shadow Pilot Protocol

**Document Type:** Standard Operating Procedure (SOP) & Deployment Protocol  
**Protocol Code:** SOP-DVAI-PILOT-001  
**Version:** 1.0.0  
**Effective Date:** 2026-11-01  
**Authorization Status:** CONDITIONAL APPROVAL (Supervised Shadow Mode Only)  
**Strict Prohibition:** AUTONOMOUS LIVE-LINE GATING IS STRICTLY PROHIBITED  

---

## 1. Scope, Purpose & Core Operating Principle

### 1.1 Purpose
This protocol defines the strict operational rules, setup procedures, and verification criteria for conducting an industrial feasibility trial of the DefectVision AI dual-engine anomaly detection system in an active manufacturing facility.

### 1.2 Core Principle: Non-Interference Shadow Mode
DefectVision AI **MUST NOT** be connected to physical ejection actuators, pneumatic diverters, PLC stop gates, or automated binning mechanisms. 
- The system operates exclusively in **Passive Shadow Mode**, monitoring camera frames in parallel with existing quality control workflows.
- **Human quality inspectors retain 100% final gating and binning authority.**
- No product may be scrapped, reworked, or approved based solely on automated model output during this pilot.

---

## 2. Pre-Deployment Prerequisites & Calibration Phase (Stage 1)

Before initiating live image capture, the deployment team must complete on-site calibration to account for factory-specific optical and material variations:

```
[ Factory Line Installation ] 
              |
              v
[ Step 1: Optical Enclosure Verification ]
  - Enclosed illumination tunnel installed (prevent ambient lighting flicker).
  - Camera rigidly mounted with vibration dampening.
  - Image resolution standardized to 224x224 or scaled letterbox.
              |
              v
[ Step 2: 50-Specimen Baseline Capture ]
  - Capture exactly N >= 50 verified unblemished (nominal) specimens.
  - Verify zero defects under manual high-magnification inspection.
              |
              v
[ Step 3: Local Parameter Calibration ]
  - Feed 50 nominal specimens through PatchCore feature extraction.
  - Compute localized mean distance: \mu_0 = (1/N) \sum S_i
  - Compute localized standard deviation: \sigma_0
  - Set localized operational threshold: \tau_c = \mu_0 + 3.0 \cdot \sigma_0
  - Record parameters in local `factory_baseline_config.json`.
              |
              v
[ Step 4: Dry-Run Latency & Stability Check ]
  - Verify sustained round-trip inference latency <= line cycle time.
  - Minimum cycle time threshold on CPU hardware: >= 1.5 seconds per specimen.
```

---

## 3. Passive Shadow Operation Protocol (Stage 2)

### 3.1 Data Flow Architecture

```
                    [ Manufacturing Line Conveyor ]
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
    [ Human Quality Inspector ]              [ Industrial Vision Camera ]
    - Visual inspection                      - Triggered on part arrival
    - Manual pass/reject decision            - High-resolution frame grab
    - Physical line gating (ACTIVE)                     |
                                                        v
                                            [ DefectVision AI Server ]
                                            - Passive inference (SHADOW)
                                            - Generates: Score, Map, Pred
                                                        |
                                                        v
                                            [ Shadow Telemetry Log ]
                                            - SQLite / CSV Audit DB
                                            - Human vs Model Concordance
```

### 3.2 Operating Guidelines
1. **Parallel Ingestion:** The camera feeds frames directly to the DefectVision AI microservice via the HTTP API (`POST /inspect-frame`) or local message queue.
2. **Telemetry Logging:** For every inspected part, the system records:
   - Part serial number / timestamp
   - Model prediction: $\hat{y}_{\text{hybrid}} \in \{0, 1\}$
   - PatchCore anomaly distance and percentile score
   - EfficientNet-B0 probability and confidence
   - Estimated defect area percentage and severity level
   - Saved high-resolution anomaly heatmap and bounding contours
3. **Zero Operator Disruption:** Human inspectors must not be prompted or delayed by model inference. Inspection proceeds at normal line speed.

---

## 4. Concordance & Performance Audit (Stage 3)

At the end of each production shift, the quality engineering supervisor reviews model telemetry against the human inspector's physical reject log:

### 4.1 Shift Concordance Matrix
```
                            HUMAN INSPECTOR DECISION
                            PASS (Nominal)     REJECT (Defect)
MODEL       PASS            [ True Agree ]     [ Model Escape ]
PREDICTION  FLAGGED         [ False Alarm ]    [ True Agree ]
```

### 4.2 Key Target Metrics for Pilot Viability
- **Concordance Agreement Rate:** $> 90\%$ overall agreement with experienced inspectors.
- **Defect Escape Concordance:** Model escape rate on human-confirmed defects must be $< 10\%$.
- **On-Site False Alarm Rate:** False alarms on human-confirmed good parts must remain $< 5\%$.
- **Latency Consistency:** Zero request drops or HTTP 500 errors across shift duration.

---

## 5. Stop-Work & Safety Abort Criteria

The pilot trial must be immediately suspended and escalated to engineering if any of the following occur:

1. **False Alarm Runaway ($> 8.0\%$):** If false alarms exceed 8% of nominal parts over a 2-hour window, the line baseline has shifted (e.g., lighting drift, dust accumulation on optics, or batch material variation). Recalibration is mandatory.
2. **Model Crash or Unhandled Exception:** Any unhandled process exit, memory leak, or API timeout.
3. **Accidental Actuation:** Any connection or signal sent to physical sorting gates will terminate the pilot immediately.

---

## 6. Pilot Authorization Sign-Off

```
================================================================================
PILOT AUTHORIZATION: SUPERVISED SHADOW TESTING ONLY
================================================================================
Approved Operating Mode:     PASSIVE SHADOW LOGGING
Hardware Platform:           Dedicated Multi-Core CPU / GPU Edge Node
Minimum Part Cycle Time:     1.5 seconds (CPU) / 100 ms (GPU)
Human Review Authority:      100% Gating Authority Retained by Human Staff
Autonomous Line Gating:      STRICTLY PROHIBITED (REJECTED)
================================================================================
```
