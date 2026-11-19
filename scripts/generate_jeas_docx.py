import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUTPUT_DIR = r"C:\Users\surya\Downloads\Mini Project\release\JEAS_final_submission"
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_manuscript_docx():
    doc = docx.Document()
    
    # Page setup: Standard Letter, 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # Base style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # -------------------------------------------------------------
    # Title & Metadata
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(12)
    title_run = title_p.add_run("Hybrid Visual Defect Inspection and Nominal-Only Adaptation: An Empirical Study of Detection Trade-Offs and Operational Constraints")
    title_run.font.name = 'Times New Roman'
    title_run.font.size = Pt(16)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)

    author_p = doc.add_paragraph()
    author_p.paragraph_format.space_after = Pt(4)
    a_run = author_p.add_run("Surya Charan")
    a_run.bold = True
    a_run.font.size = Pt(11.5)
    
    affil_p = doc.add_paragraph()
    affil_p.paragraph_format.space_after = Pt(12)
    affil_run = affil_p.add_run("[Affiliation: AUTHOR CONFIRMATION REQUIRED]\nEmail: suryacharan945@gmail.com\n*Corresponding author")
    affil_run.font.size = Pt(10)
    affil_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    # -------------------------------------------------------------
    # Abstract & Keywords
    # -------------------------------------------------------------
    abs_heading = doc.add_paragraph()
    abs_heading.paragraph_format.space_before = Pt(8)
    abs_heading.paragraph_format.space_after = Pt(4)
    h_run = abs_heading.add_run("Abstract")
    h_run.bold = True
    h_run.font.size = Pt(12)
    h_run.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)

    abs_p = doc.add_paragraph()
    abs_p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abs_p.paragraph_format.space_after = Pt(10)
    abs_text = (
        "Automated surface defect inspection in high-throughput manufacturing operates under an asymmetric cost matrix: "
        "undetected defect escapes risk catastrophic downstream failures, while excessive false alarms induce costly scrap and line stoppages. "
        "Supervised deep convolutional classifiers achieve high precision on anticipated flaw types but fail on novel geometries. "
        "Conversely, unsupervised memory-bank anomaly detectors identify arbitrary deviations without defect supervision but often suffer from "
        "elevated false-positive rates on natural surface texturing. In this paper, we conduct an empirical applied-engineering investigation "
        "into a dual-branch hybrid inspection architecture combining a supervised visual classifier (EfficientNet-B0 v3) with an unsupervised "
        "patch-distribution memory bank (PatchCore) via logical OR decision fusion. On an audited development-exposed benchmark of 856 industrial "
        "images from MVTec AD, hybrid fusion increased defect recall from 82.24% to 90.88%, recovering 54 defects missed by the standalone classifier, "
        "while increasing false alarms from 1 to 12 (false positive rate rising from 0.43% to 5.19%). To evaluate nominal adaptation without defect "
        "supervision, the patch memory pipeline was independently tested on 200 untouched Visual Anomaly (VisA) Cashew specimens after calibration on "
        "50 held-out nominals (tau_p99.5 = 1.7452, calibrated on 350 registration images and 50 held-out calibration nominals). PatchCore achieved "
        "an image AUROC of 0.9237 and a full-census pixel AUROC of 0.9930. Operating at the locked 99.5th-percentile calibration threshold enforced high "
        "specificity (98.0%, 2 false alarms), but granular morphology reconciliation across all 100 defective specimens (90 single-defect, 10 compound) "
        "revealed an overall 43.0% defect escape rate: gross structural breaks achieved 100% recall (8/8 middle breakage, 6/6 stuck together), localized "
        "voids (small holes) achieved 81.8% marginal recall (18/22 caught; 17/20 on single-defect specimens), whereas hairline scratches suffered a 93.8% "
        "marginal escape rate (1/16 caught; 1/15 on single-defect specimens) and same-color indentations suffered an 85.7% marginal escape rate "
        "(2/14 caught; 0/10 on single-defect specimens). Execution profiling on a 13th Gen Intel Core i5-1335U CPU confirmed a median PatchCore "
        "latency of 392.5 ms and a direct dual-model latency of 450.6 ms (mean 558.97 ms), confirming computational feasibility for discrete line takt times "
        "(>= 1.5 s). We disclose all experimental boundaries, concluding that while nominal adaptation provides viable containment assistance, unassisted autonomous "
        "sorting requires addressing feature downsampling limits on micro-flaws."
    )
    abs_run = abs_p.add_run(abs_text)
    abs_run.font.size = Pt(10.5)

    kw_p = doc.add_paragraph()
    kw_p.paragraph_format.space_after = Pt(16)
    kw_title = kw_p.add_run("Keywords: ")
    kw_title.bold = True
    kw_p.add_run("Industrial visual inspection, Anomaly detection, PatchCore, EfficientNet, Decision fusion, VisA benchmark.")

    # -------------------------------------------------------------
    # Helper to add section headings
    # -------------------------------------------------------------
    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(0x0A, 0x25, 0x40)
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(0x1B, 0x49, 0x65)
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(text)
        r.bold = True
        r.italic = True
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(0x2B, 0x2D, 0x42)
        return p

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        p.add_run(text)
        return p

    def add_fig_image(filename, caption_text, width_inches=6.0):
        img_path = os.path.join(FIG_DIR, filename)
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.add_run().add_picture(img_path, width=Inches(width_inches))
            
            cp = doc.add_paragraph()
            cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(12)
            c_run = cp.add_run(caption_text)
            c_run.font.size = Pt(9.5)
            c_run.italic = True
            c_run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # -------------------------------------------------------------
    # Section 1: Introduction
    # -------------------------------------------------------------
    add_h1("1. Introduction")
    add_body(
        "Automated surface defect inspection represents an essential quality assurance function across precision manufacturing sectors, "
        "including semiconductor device packaging, automotive metal stamping, pharmaceutical blister auditing, and consumer goods sorting [10, 11, 26]. "
        "In practical production environments, visual quality gating operates under an inherently asymmetric cost matrix. A Type II error "
        "(false negative / defect escape) delivers substandard or structurally compromised components to downstream assembly lines or end customers, "
        "risking equipment damage, safety hazards, warranty liabilities, and costly product recalls. Conversely, a Type I error "
        "(false positive / false alarm) falsely flags conforming product as defective, inducing unnecessary component scrap, excessive manual reinspection labor, "
        "and disruptive production line stoppages [11, 12]."
    )
    add_body(
        "In recent years, deep learning methodologies for automated visual inspection have bifurcated into two primary paradigms:\n"
        "1. Supervised Visual Classification: Deep convolutional neural networks (CNNs) and Vision Transformers trained on extensive annotated libraries "
        "of defective and conforming components [4, 10, 13]. When evaluated against recurring, pre-defined flaw topologies, supervised models deliver high precision "
        "and low false-alarm rates. However, they rely on a closed-world assumption: when presented with novel, unmodeled defect geometries, anomalous foreign "
        "materials, or unrepresented physical damage, supervised classifiers exhibit overconfident misclassifications, leading to severe defect escapes [10].\n"
        "2. Unsupervised Anomaly Detection: Systems trained exclusively on nominal (defect-free) component imagery to model the distribution of normal appearances, "
        "such as memory-bank nearest-neighbor methods [1, 6, 7], normalizing flows [16, 17], and knowledge distillation frameworks [20, 21, 24]. Because they require "
        "no defect annotations, these methods theoretically detect arbitrary deviations from nominality. However, in factory environments characterized by natural "
        "intra-class texture variations, illumination drifts, and part positioning jitter, purely unsupervised models frequently suffer from elevated false-alarm rates "
        "that factory operators cannot tolerate [1, 10, 22]."
    )
    add_body(
        "To combine the strengths of both paradigms, industrial practitioners frequently explore dual-branch hybrid architectures, combining a supervised classifier "
        "with an unsupervised anomaly detector via logical disjunction (OR-logic) [10]. Under this regime, a specimen is quarantined if either branch flags a potential flaw. "
        "While the conceptual appeal of such hybrid gating is widely recognized, literature in applied instrumentation and measurement rarely quantifies the precise operational "
        "penalty curve: how many false alarms must a manufacturing line absorb to reduce defect escapes by a given margin? Furthermore, while unsupervised methods claim rapid "
        "adaptation to new manufacturing lines, empirical studies evaluating nominal-only adaptation on completely unseen, out-of-distribution industrial substrates under strict "
        "audit protocols remain scarce."
    )
    
    add_h2("1.1 Contributions and Scope of This Work")
    add_body(
        "In this paper, we present an empirical evaluation of hybrid defect detection and nominal-only category adaptation under concrete operational and hardware constraints. "
        "Rather than asserting architectural, mathematical, or algorithmic novelty, the primary scientific and engineering contributions of this work are:\n"
        "1. Empirical Quantification of the Hybrid Operating Trade-Off: On an audited development-exposed benchmark of 856 industrial images (MVTec AD [3]), we quantify the exact "
        "cost curve of dual-branch decision fusion: pairing an EfficientNet-B0 v3 classifier [4] with a PatchCore memory bank [1] captured 54 defect instances missed by the supervised "
        "model alone (reducing missed defects from 111 to 57; recall rising from 82.24% to 90.88%), at the operational expense of 11 additional false alarms (increasing false alarm rate "
        "from 0.43% to 5.19%).\n"
        "2. First-Party Independent Adaptation Validation: We execute a strictly isolated, out-of-distribution evaluation of nominal-only PatchCore registration on the untouched "
        "Visual Anomaly (VisA) Cashew benchmark [2], using 350 nominal registration images and 50 held-out nominal calibration images. Across 200 independent test specimens (100 nominal, "
        "100 defective), the system achieved an image-level AUROC of 0.9237 [95% CI: 0.8852, 0.9565], an image-level AUPRC of 0.9270, and a full-census pixel-level AUROC of 0.9930 across "
        "10.03 million evaluated pixels.\n"
        "3. Reconciled Granular Morphology Breakdown: We unpack aggregate AUROC metrics across all 100 defective specimens in the VisA Cashew benchmark, explicitly reconciling the 90 single-morphology "
        "specimens and 10 compound multi-defect specimens with overlapping annotations. This analysis exposes the physical boundary conditions of patch-distance anomaly scoring: while macroscopic "
        "deformities and gross structural breaks achieved 100% recall, hairline surface scratches and subtle same-color indentations yielded catastrophic escape rates of 93.8% and 85.7% under "
        "factory-grade false-alarm constraints (tau_p99.5).\n"
        "4. Laboratory Hardware Execution Profiling on Multi-Core CPU: We demonstrate that memory-bank adaptation and CPU inference are achievable on standard multi-core CPU workstations "
        "without GPU acceleration: registration of 350 nominal images completed in 392.25 s (40.2 MB memory footprint), with deterministic per-image inference latencies of 392.5 ms median "
        "(p95: 438.1 ms), establishing computational feasibility for discrete inspection stations with cycle times >= 1.5 s.\n"
        "5. Transparent Documentation of Negative Engineering Findings: We document architectural modifications that failed to yield performance improvements during development, specifically the "
        "failure of Context-Preserving Normalization Dropout (CPND) to improve generalization and the optimization instability of Multi-Axis Cross-Branch Attention (MACBA).\n"
        "6. Explicit Operational Boundaries and Disclosures: We prominently disclose that MVTec results represent Category C development-exposed performance, that independent validation evaluates "
        "PatchCore exclusively without the supervised classifier, that environmental stress tests were executed using synthetic perturbations rather than live line shifts, that laboratory latency "
        "metrics do not establish production readiness, and that no live factory conveyor trial was conducted."
    )

    add_fig_image("fig1_architecture.png", "Fig. 1. Architecture of the DefectVision AI dual-branch hybrid inspection pipeline combining supervised classification (EfficientNet-B0 v3) and unsupervised patch anomaly memory (PatchCore) via logical OR decision fusion.")

    # -------------------------------------------------------------
    # Section 2: Related Work
    # -------------------------------------------------------------
    add_h1("2. Related Work")
    add_body(
        "Supervised convolutional networks (e.g. EfficientNet-B0 [4], ResNet [5]) excel at feature discrimination across known classes but operate under closed-world assumptions [10, 25]. "
        "Unsupervised methods address this by modeling nominal appearance exclusively. While generative models (Autoencoders, GANs) suffer from reconstruction blur [3], "
        "feature-embedding frameworks (SPADE [7], PaDiM [6], PatchCore [1], DifferNet [16], CFLOW-AD [17], EfficientAD [20], Reverse Distillation [21]) achieve state-of-the-art localization. "
        "PatchCore condenses mid-level convolutional patch representations via greedy minimax coreset selection, enabling fast nearest-neighbor anomaly scoring [1]. "
        "However, comprehensive evaluations on independent non-rigid organic benchmarks such as VisA [2] under frozen audit protocols remain necessary to verify cross-domain adaptation."
    )

    # -------------------------------------------------------------
    # Section 3: Materials and Methods
    # -------------------------------------------------------------
    add_h1("3. Materials and Methods")
    add_body(
        "The DefectVision AI architecture integrates two decoupled inspection engines executing concurrently on an incoming component image: "
        "a supervised defect classifier (EfficientNet-B0 v3) and an unsupervised patch-distribution memory bank (PatchCore). The overall pipeline is illustrated in Fig. 1."
    )
    add_h2("3.1 Unsupervised Patch-Level Memory Pipeline (PatchCore)")
    add_body(
        "Feature Extraction: Given an input image x in R^{3 x 224 x 224}, patch representations are extracted from intermediate residual stages of a frozen ImageNet-pretrained "
        "ResNet-18: layer2 (stride 8, 128 channels) and layer3 (stride 16, 256 channels). To capture spatial context, each feature map is smoothed via 3x3 local adaptive average pooling "
        "with stride 1. The feature maps are bilinearly interpolated to a common spatial resolution (28x28) and concatenated channel-wise, producing a dense grid of 784 patch vectors "
        "with feature dimension D = 128 + 256 = 384.\n\n"
        "Greedy Minimax Coreset Subsampling: For a nominal registration cohort of K_reg images, the raw patch collection M_raw contains K_reg x 784 feature vectors. Storing and searching "
        "this collection introduces excessive memory and latency overhead. We apply the iterative greedy k-Center minimax facility location algorithm [1] to select a representative subset "
        "M_coreset of size M at target ratio kappa = 0.10, condensing the memory bank by an order of magnitude.\n\n"
        "Fast Nearest-Neighbor Indexing: The coreset feature vectors are indexed using an exact Euclidean distance flat index (IndexFlatL2) via the FAISS library [8] executing natively on "
        "multi-threaded CPU hardware. We note specifically that nearest-neighbor distances are calculated via standard L2 Euclidean metric, and are not parameterized by full covariance "
        "Mahalanobis distance matrices.\n\n"
        "Anomaly Scoring and Heatmap Generation: At test time, patch vectors p extracted from an input image are queried against M_coreset. The patch-level anomaly score is defined as the "
        "Euclidean distance to its nearest nominal neighbor: s(p) = min_{c in M_coreset} ||p - c||_2. The patch scores are reshaped to 28x28, bilinearly upsampled to 224x224, and smoothed "
        "with a 2D Gaussian kernel (sigma = 4.0) to generate the continuous anomaly heatmap A(u,v). The specimen-level score S_img is the maximum spatial value across A(u,v)."
    )
    add_h2("3.2 Statistical Decision Threshold Calibration")
    add_body(
        "To establish an operational binary decision boundary without defect supervision, we enforce a strict quantile-based calibration protocol. A cohort of K_cal = 50 nominal specimens "
        "held out from coreset registration is processed through the memory pipeline to compute nominal baseline scores. The operational decision threshold tau_p99.5 is set to the empirical "
        "99.5th percentile of the calibration distribution: tau_p99.5 = Percentile({S_cal,1, ..., S_cal,50}, 99.5) = 1.745232. For audit rigor, we clarify that while software configuration "
        "manifests designated this parameter as threshold_p99, its mathematical evaluation is the exact 99.5th empirical percentile of the 50 calibration scores, enforcing a theoretical nominal "
        "false-alarm rate <= 1.0% prior to evaluating any unseen test data."
    )
    add_h2("3.3 Supervised Visual Classification Pipeline (EfficientNet-B0 v3)")
    add_body(
        "The supervised branch executes a fine-tuned EfficientNet-B0 classifier [4]. Input images are resized to 256x256, normalized using ImageNet channel statistics, and processed through "
        "mobile inverted bottleneck convolutions (MBConv) to produce a 1280-dimensional global representation vector. A fully connected classification head with softmax activation outputs "
        "the posterior defect probability p_defect. The binary supervised decision is parameterized by standard operating threshold: d_clf = I(p_defect >= 0.50)."
    )
    add_h2("3.4 Dual-Branch Decision Fusion Rule")
    add_body(
        "Decisions are integrated via a logical disjunction (OR-logic) gating rule: y_hybrid = d_clf OR I(S_img >= tau_p99.5). A component is quarantined if either branch flags a potential flaw."
    )

    # -------------------------------------------------------------
    # Section 4: Experimental Design
    # -------------------------------------------------------------
    add_h1("4. Experimental Design and Audit Protocols")
    add_body(
        "Hardware and Software Stack: All experiments were executed on an engineering workstation equipped with a 13th Gen Intel Core i5-1335U CPU @ 1.30 GHz (10 physical cores [2 P-cores, "
        "8 E-cores], 12 logical threads), 16.0 GB DDR4 RAM (15.63 GiB usable), 512 GB NVMe SSD, Windows 11 Enterprise AMD64, Python 3.12.4, PyTorch 2.15.0+cpu, Torchvision 0.29.2+cpu, "
        "FAISS-CPU 1.15.1, scikit-learn 1.9.1, and SciPy 1.18.1. Random seed was permanently fixed to S=42 with deterministic algorithms enabled.\n\n"
        "Datasets: (1) MVTec AD (856 test images across 15 categories: 625 defect, 231 normal; CC BY-NC-SA 4.0), designated as Category C Development-Exposed. (2) VisA Cashew (Apache 2.0), "
        "evaluated under an untouched zero-leakage protocol: 350 nominal registration, 50 nominal calibration, and 200 independent test specimens (100 nominal, 100 defective).\n\n"
        "Evaluation Metrics: Binomial proportions evaluated using Wilson score intervals [9] (z = 1.95996 for 95% CI). Continuous image AUROC evaluated via 1,000 empirical bootstraps. "
        "Full-census pixel AUROC evaluated across all 10,035,200 test pixels against binarized ground-truth polygon masks."
    )

    # -------------------------------------------------------------
    # Section 5: Results
    # -------------------------------------------------------------
    add_h1("5. Results")
    add_h2("5.1 Development-Exposed Benchmark Evaluation (MVTec AD)")
    add_body(
        "Table 1 details the performance comparison across the 856-image MVTec AD benchmark. Standalone EfficientNet-B0 missed 111 defects (recall 82.24%) with exceptional "
        "specificity (99.57%, 1 false alarm). The dual-branch hybrid captured 54 of those missed defects (reducing escapes to 57, recall 90.88%), but increased false alarms "
        "twelve-fold (12 false alarms, FPR 5.19%). This confirms that hybrid fusion reallocates operational risk rather than achieving universal metric dominance."
    )

    # Table 1: MVTec Comparison
    t1_p = doc.add_paragraph()
    t1_p.paragraph_format.space_before = Pt(8)
    t1_p.paragraph_format.space_after = Pt(4)
    t1_title = t1_p.add_run("Table 1. Quantitative Performance Comparison on the Audited 856-Image MVTec AD Benchmark")
    t1_title.bold = True
    t1_title.font.size = Pt(10)

    t1_data = [
        ["Metric", "PatchCore (Alone)", "EffNet-B0 (Alone)", "DefectVision Hybrid", "Hybrid Delta vs EffNet"],
        ["Evaluation Population", "856 images", "856 images", "856 images", "--"],
        ["True Positives (TP)", "449", "514", "568", "+54 caught"],
        ["True Negatives (TN)", "220", "230", "219", "-11"],
        ["False Positives (FP)", "11", "1", "12", "+11 false alarms"],
        ["False Negatives (FN)", "176", "111", "57", "-54 escapes (-48.6%)"],
        ["Accuracy", "78.15%", "86.92%", "91.94%", "+5.02%"],
        ["Defect Recall (TPR)", "71.84%", "82.24%", "90.88%", "+8.64%"],
        ["Specificity (TNR)", "95.24%", "99.57%", "94.81%", "-4.76%"],
        ["F1-Score", "0.8277", "0.9018", "0.9427", "+0.0409"],
        ["False Positive Rate", "4.76%", "0.43%", "5.19%", "+4.76%"],
        ["False Negative Rate", "28.16%", "17.76%", "9.12%", "-8.64%"],
        ["Image-Level AUROC", "0.9373*", "0.9809", "0.9608", "-0.0201"]
    ]
    t1_table = doc.add_table(rows=len(t1_data), cols=5)
    t1_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            cell = t1_table.cell(r_idx, c_idx)
            cell.text = val
            set_cell_margins(cell, 80, 80, 120, 120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "EAECEF")
            p.runs[0].font.size = Pt(9)

    add_fig_image("fig2_confusion_matrices.png", "Fig. 2. Confusion matrix comparison on 856 MVTec AD specimens (Category C Development-Exposed) demonstrating that hybrid decision fusion reduces missed defects by 54 at the cost of 11 additional false alarms.")

    add_h2("5.2 Independent Out-of-Distribution Validation (VisA Cashew)")
    add_body(
        "On 200 untouched VisA Cashew specimens, PatchCore nominal adaptation achieved an Image AUROC of 0.9237 [95% CI: 0.8852, 0.9565] and a full-census Pixel AUROC of 0.9930 "
        "across 10.03 million evaluated pixels. At tau_p99.5 = 1.7452, specificity was 98.00% (2 false alarms). However, defect recall was limited to 57.00% (43 escapes). "
        "Table 2 summarizes these metrics, and Table 3 exposes the underlying morphological failure modes."
    )

    # Table 2: VisA Summary
    t2_p = doc.add_paragraph()
    t2_p.paragraph_format.space_before = Pt(8)
    t2_p.paragraph_format.space_after = Pt(4)
    t2_title = t2_p.add_run("Table 2. Independent Validation Results on the Untouched VisA Cashew Benchmark (N=200)")
    t2_title.bold = True
    t2_title.font.size = Pt(10)

    t2_data = [
        ["Metric", "Measured Value", "95% Confidence Interval / Notes"],
        ["Evaluation Population", "200 specimens", "100 Nominal, 100 Defective (1:1 split)"],
        ["True Positives (TP)", "57", "Defective specimens correctly flagged"],
        ["True Negatives (TN)", "98", "Nominal specimens correctly cleared"],
        ["False Positives (FP)", "2", "Nominal specimens falsely rejected (2.00% FPR)"],
        ["False Negatives (FN)", "43", "Defective specimens escaped inspection (43.00% FNR)"],
        ["Accuracy", "77.50%", "[71.22%, 82.68%] (Wilson Score Interval)"],
        ["Defect Precision (PPV)", "96.61%", "[88.48%, 99.07%] (Wilson Score Interval)"],
        ["Defect Recall (TPR)", "57.00%", "[47.24%, 66.24%] (Wilson Score Interval)"],
        ["Specificity (TNR)", "98.00%", "[92.96%, 99.45%] (Wilson Score Interval)"],
        ["Image-Level AUROC", "0.9237", "[0.8852, 0.9565] (1,000 Empirical Bootstraps)"],
        ["Image-Level AUPRC", "0.9270", "Area under Precision-Recall curve"],
        ["Full-Census Pixel AUROC", "0.9930", "10,035,200 evaluated test pixels (all 200 images)"],
        ["Defect-Only Pixel AUROC", "0.9877", "5,017,600 evaluated pixels (100 defective images)"]
    ]
    t2_table = doc.add_table(rows=len(t2_data), cols=3)
    t2_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            cell = t2_table.cell(r_idx, c_idx)
            cell.text = val
            set_cell_margins(cell, 80, 80, 120, 120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx == 1 else WD_ALIGN_PARAGRAPH.LEFT
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "EAECEF")
            p.runs[0].font.size = Pt(9)

    add_fig_image("fig3_roc_pr_curves.png", "Fig. 3. Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves for PatchCore nominal adaptation on 200 untouched VisA Cashew test specimens, highlighting the locked operating point (tau_p99.5 = 1.7452).")

    add_h2("5.3 Reconciled Morphology Breakdown Across Defect Taxonomies")
    add_body(
        "In the official VisA Cashew annotations, 90 defective specimens exhibit a single primary flaw morphology, while 10 specimens exhibit multiple co-occurring flaw types. "
        "Table 3 partitions the 100 defective specimens into single- and compound-morphology cohorts, while documenting marginal flaw sensitivity across all 110 morphology annotations."
    )

    # Table 3: Morphology Breakdown
    t3_p = doc.add_paragraph()
    t3_p.paragraph_format.space_before = Pt(8)
    t3_p.paragraph_format.space_after = Pt(4)
    t3_title = t3_p.add_run("Table 3. Granular Defect Detection Across VisA Cashew Defect Morphologies (N=100 Defective Specimens)")
    t3_title.bold = True
    t3_title.font.size = Pt(10)

    t3_data = [
        ["Defect Category / Morphology", "Total", "TP", "FN", "Recall (%)"],
        ["A. Single-Morphology Cohort (n=90)", "", "", "", ""],
        ["middle breakage", "6", "6", "0", "100.0%"],
        ["stuck together", "6", "6", "0", "100.0%"],
        ["different colour spot", "9", "8", "1", "88.9%"],
        ["small holes", "20", "17", "3", "85.0%"],
        ["corner or edge breakage", "14", "11", "3", "78.6%"],
        ["burnt", "10", "4", "6", "40.0%"],
        ["small scratches", "15", "1", "14", "6.7%"],
        ["same colour spot", "10", "0", "10", "0.0%"],
        ["Subtotal (Single-Morphology)", "90", "53", "37", "58.9%"],
        ["B. Co-Occurring Compound Morphologies (n=10)", "", "", "", ""],
        ["middle breakage + small holes", "1", "1", "0", "100.0%"],
        ["middle breakage + same colour spot", "1", "1", "0", "100.0%"],
        ["burnt + corner/edge breakage", "2", "1", "1", "50.0%"],
        ["different colour spot + same colour spot", "2", "1", "1", "50.0%"],
        ["burnt + different colour spot", "1", "0", "1", "0.0%"],
        ["burnt + same colour spot", "1", "0", "1", "0.0%"],
        ["corner/edge breakage + small scratches", "1", "0", "1", "0.0%"],
        ["different colour spot + small holes", "1", "0", "1", "0.0%"],
        ["Subtotal (Compound Morphologies)", "10", "4", "6", "40.0%"],
        ["Total Defective Cohort (Census)", "100", "57", "43", "57.0%"]
    ]
    t3_table = doc.add_table(rows=len(t3_data), cols=5)
    t3_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t3_data):
        for c_idx, val in enumerate(row):
            cell = t3_table.cell(r_idx, c_idx)
            cell.text = val
            set_cell_margins(cell, 80, 80, 120, 120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "EAECEF")
            elif r_idx in [1, 10]:
                p.runs[0].bold = True
                p.runs[0].italic = True
                set_cell_background(cell, "F4F5F7")
            elif r_idx in [9, 19, 20]:
                p.runs[0].bold = True
                set_cell_background(cell, "F0F2F5")
            p.runs[0].font.size = Pt(9)

    add_fig_image("fig4_defect_morphology.png", "Fig. 4. Granular defect recall across VisA Cashew defect morphologies (N=100 defective specimens), demonstrating the severe escape rate on hairline scratches and same-color indentations under conservative factory thresholds. Note that 10 specimens exhibit co-occurring overlapping flaw morphologies.")

    add_h2("5.4 Computational Execution Profiling on CPU")
    add_body(
        "Computational profiling on an Intel Core i5-1335U CPU workstation demonstrated that target-domain registration of 350 images required 392.25 seconds (~6.5 minutes), "
        "producing a compact 40.2 MB memory index. Per-image inference latency on CPU was 392.5 ms median (p95: 438.1 ms) for standalone PatchCore, and 881.7 ms median "
        "(p95: 1455.7 ms) for end-to-end hybrid API calls. Table 4 and Fig. 5 summarize these measurements."
    )

    # Table 4: CPU Profiling
    t4_p = doc.add_paragraph()
    t4_p.paragraph_format.space_before = Pt(8)
    t4_p.paragraph_format.space_after = Pt(4)
    t4_title = t4_p.add_run("Table 4. Computational Execution Latency Profiling across Pipeline Stages (Intel Core i5-1335U CPU)")
    t4_title.bold = True
    t4_title.font.size = Pt(10)

    t4_data = [
        ["Pipeline Stage", "Hardware / Implementation", "Mean (ms)", "Median (ms)", "p95 (ms)"],
        ["Feature Extraction", "ResNet-18 (layer2+layer3, D=384)", "166.8", "164.2", "181.4"],
        ["FAISS Flat L2 Search", "IndexFlatL2 (M=27,440 tokens)", "173.2", "172.5", "196.2"],
        ["Gaussian Smoothing & Heatmap", "Gaussian blur (sigma=4.0) + bilinear upsample", "55.4", "55.8", "60.5"],
        ["PatchCore Forward Pass Total", "Full CPU inference (224x224 input)", "395.4", "392.5", "438.1"],
        ["EfficientNet-B0 v3 Forward Pass", "Supervised classification (256x256 input)", "173.1", "170.1", "256.3"],
        ["Hybrid Decision API (End-to-End)", "Full HTTP roundtrip (EffNet + PatchCore + OR)", "914.2", "881.7", "1455.7"]
    ]
    t4_table = doc.add_table(rows=len(t4_data), cols=5)
    t4_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(t4_data):
        for c_idx, val in enumerate(row):
            cell = t4_table.cell(r_idx, c_idx)
            cell.text = val
            set_cell_margins(cell, 80, 80, 120, 120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx >= 2 else WD_ALIGN_PARAGRAPH.LEFT
            if r_idx == 0:
                p.runs[0].bold = True
                set_cell_background(cell, "EAECEF")
            p.runs[0].font.size = Pt(9)

    add_fig_image("fig5_cpu_latency.png", "Fig. 5. Computational execution latency profiling across individual pipeline stages on a 13th Gen Intel Core i5-1335U CPU workstation, showing compatibility with discrete line takt times (>= 1.5 s).")

    # -------------------------------------------------------------
    # Section 6: Discussion
    # -------------------------------------------------------------
    add_h1("6. Discussion")
    add_body(
        "Quality Control Economics: The operational viability of the hybrid decision policy is governed by the relative economic cost balance between "
        "defect escapes and false alarms. In manufacturing environments where defect escapes carry severe consequences compared to the cost of reinspecting "
        "false alarms (such as automotive safety components, aerospace fasteners, or pharmaceutical packaging), the hybrid policy is operationally advantageous: "
        "capturing 54 additional defects substantially offsets the overhead of 11 additional false alarms. Conversely, in high-volume, low-margin production "
        "where false rejections directly degrade yield profitability, factory operators must prioritize specificity and conservative thresholding to maintain viable economics.\n\n"
        "Forensic Analysis of Escapes: In VisA Cashew, fine hairline surface scratches occupy a minor spatial fraction of the effective convolutional receptive field. "
        "When processed through ResNet-18 layer2 (stride 8) and layer3 (stride 16) with 3x3 local average pooling, high-frequency spatial gradients are smoothed into "
        "surrounding nominal features. Furthermore, natural cashew kernels possess organic furrows and striations whose embeddings exhibit natural variance overlapping "
        "with subtle scratches. Similarly, same-colour spots represent shallow monochromatic depressions that share the exact hue and reflectance of healthy cashew kernel "
        "meat, producing negligible nearest-neighbor displacement under diffuse illumination. We emphasize that our benchmark evaluations do not isolate optical resolution "
        "as the sole causal mechanism; rather, feature spatial strides, pooling operations, illumination geometry, and representation choices act together as contributing factors.\n\n"
        "Takt-Time Viability: Discrete batch inspection stations (cycle times >= 1.5 s) are computationally viable on CPU without GPU investment. However, high-speed "
        "continuous production (< 100 ms) is unviable on CPU and requires tensor quantization (INT8) or edge GPU accelerators.\n\n"
        "Documentation of Negative Findings: We transparently document two negative results: (1) Context-Preserving Normalization Dropout (CPND) yielded statistically "
        "indistinguishable generalization relative to standard dropout (p = 0.42); and (2) Multi-Axis Cross-Branch Attention (MACBA) suffered gradient divergence during "
        "joint branch backpropagation. While this negative finding highlights the practical implementation stability of decoupled late-stage decision fusion (OR-logic) "
        "over early cross-branch coupling in our evaluated pipeline, it reflects the behavior of our specific experimental configuration and does not imply that decision-level "
        "fusion is universally superior across all possible joint optimization architectures."
    )

    # -------------------------------------------------------------
    # Section 7: Limitations and Future Work
    # -------------------------------------------------------------
    add_h1("7. Limitations and Future Work")
    add_body(
        "We explicitly acknowledge several fundamental boundaries:\n"
        "1. Benchmark Latency vs. Live Industrial Deployment: Benchmark latency on static test images does not establish live production line readiness, which entails "
        "vibrations, optic contamination, triggering jitter, and 24/7 daemon stability.\n"
        "2. Asymmetric Scope of Independent Validation: Independent validation on VisA Cashew evaluated PatchCore exclusively; the supervised EfficientNet branch was "
        "not evaluated cross-domain due to class specificity.\n"
        "3. Single External Category Scope: Validation on VisA Cashew demonstrates adaptation to an organic substrate, but multi-category validation remains necessary.\n"
        "4. The Single-Threshold Dilemma: Operating at conservative false-alarm thresholds suppresses sensitivity to subtle surface flaws. Addressing this trade-off "
        "remains an open research challenge; multi-resolution feature pyramids or photometric stereo represent promising avenues for future research.\n"
        "5. Synthetic Noise vs. Physical Perturbations: Robustness evaluations relied on algorithmic perturbations rather than physical plant disturbances.\n"
        "6. Absence of Live Factory Conveyor Trials: No closed-loop PLC sorting trial was conducted."
    )

    # -------------------------------------------------------------
    # Section 8: Conclusion
    # -------------------------------------------------------------
    add_h1("8. Conclusion")
    add_body(
        "In this paper, we presented an empirical evaluation of hybrid defect detection and nominal-only category adaptation under laboratory test constraints. "
        "On MVTec AD, hybrid OR-logic fusion reduced defect escapes by 48.6% (+54 defects caught) at the expense of 11 additional false alarms. On VisA Cashew, "
        "nominal adaptation achieved 0.9237 image AUROC and 0.9930 pixel AUROC on CPU, yet exposed a 93.8% escape rate on hairline scratches under conservative "
        "false-alarm boundaries. These findings demonstrate that while nominal adaptation provides baseline containment for discrete manufacturing, automated quality "
        "control requires further architectural investigation to resolve the fundamental operational tension between false-alarm suppression and micro-defect escapes."
    )

    # -------------------------------------------------------------
    # Declarations Section (Springer Nature Mandatory)
    # -------------------------------------------------------------
    add_h1("Declarations")
    
    add_h2("Abbreviations")
    add_body("AD: Anomaly Detection; AUPRC: Area Under the Precision-Recall Curve; AUROC: Area Under the Receiver Operating Characteristic; CNN: Convolutional Neural Network; CPND: Context-Preserving Normalization Dropout; FAISS: Facebook AI Similarity Search; FNR: False Negative Rate; FPR: False Positive Rate; MACBA: Multi-Axis Cross-Branch Attention; MVTec AD: MVTec Anomaly Detection Dataset; PLC: Programmable Logic Controller; TNR: True Negative Rate (Specificity); TPR: True Positive Rate (Sensitivity / Recall); VisA: Visual Anomaly Dataset.")

    add_h2("Acknowledgements")
    add_body("The author thanks the computer vision research community and the creators of the MVTec Anomaly Detection and Visual Anomaly (VisA) datasets for releasing benchmark imagery to the public research community.")

    add_h2("Authors' Contributions")
    add_body("S.C. conceived the research design, implemented the hybrid inspection pipeline, executed the experimental evaluations and latency profiling, performed the forensic failure analysis, and wrote the manuscript.")

    add_h2("Funding")
    add_body("This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. It was entirely self-supported by the author.")

    add_h2("Availability of Data and Materials")
    add_body("The datasets evaluated in this study are publicly available from their original creators:\n"
             "- The MVTec Anomaly Detection (MVTec AD) dataset is available at: https://www.mvtec.com/company/research/datasets/mvtec-ad\n"
             "- The Visual Anomaly (VisA) dataset is available via Amazon Science at: https://github.com/amazon-science/spot-diff\n"
             "Supporting evaluation manifests and prediction logs generated during this research are archived in the study's research repository.")

    add_h2("Code Availability")
    add_body("The software implementation utilized open-source frameworks (PyTorch, Torchvision, FAISS, scikit-learn). Core evaluation scripts and model manifests are documented in the study repository.")

    add_h2("Ethics Approval and Consent to Participate")
    add_body("Not applicable. This study evaluated publicly available benchmark image datasets and did not involve human participants, animal subjects, or clinical tissue data.")

    add_h2("Consent for Publication")
    add_body("Not applicable. No individual person's personal identifying data or images are contained in this article.")

    add_h2("Competing Interests")
    add_body("The author declares that they have no competing financial or non-financial interests that could have appeared to influence the work reported in this paper.")

    add_h2("Generative AI and AI-Assisted Technologies")
    add_body("During the preparation of this manuscript, the author utilized large language model assistance (Google Gemini / Claude) for comprehensive manuscript drafting, text synthesis from experimental evaluation logs, section restructuring, literature review synthesis, grammar and style refinement, mathematical notation consistency checking, and formatting. All primary experimental protocols, algorithm code implementations, model registrations, baseline evaluations, numerical data collections, confusion matrices, and empirical failure analyses were conceived, executed, verified, and audited by the author. The author reviewed and edited all generated manuscript drafts, verifies the accuracy of all claims, and takes full intellectual and ethical responsibility for the contents of this publication.")

    # -------------------------------------------------------------
    # References
    # -------------------------------------------------------------
    add_h1("References")
    refs = [
        "[1] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler, 'Towards total recall in industrial anomaly detection,' in Proc. IEEE/CVF CVPR, 2022, pp. 14318–14328. doi: 10.1109/CVPR52688.2022.01392.",
        "[2] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, 'SPOT-the-difference self-supervised pre-training for anomaly detection and segmentation,' in Proc. ECCV, Springer, 2022, pp. 392–408. doi: 10.1007/978-3-031-19821-2_23.",
        "[3] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, 'The MVTec anomaly detection dataset: A comprehensive real-world dataset for unsupervised anomaly detection,' Int. J. Comput. Vis., vol. 129, no. 4, pp. 1038–1059, 2021. doi: 10.1007/s11263-020-01400-4.",
        "[4] M. Tan and Q. V. Le, 'EfficientNet: Rethinking model scaling for convolutional neural networks,' in Proc. 36th ICML, PMLR, vol. 97, 2019, pp. 6105–6114.",
        "[5] K. He, X. Zhang, S. Ren, and J. Sun, 'Deep residual learning for image recognition,' in Proc. IEEE CVPR, 2016, pp. 770–778. doi: 10.1109/CVPR.2016.90.",
        "[6] T. Defard, A. Setkov, A. Loesch, and R. Audigier, 'PaDiM: A patch distribution modeling framework for anomaly detection and localization,' in Proc. ICPR, 2021, pp. 475–489. doi: 10.1007/978-3-030-68799-1_35.",
        "[7] N. Cohen and Y. Hoshen, 'Sub-image anomaly detection with deep pyramid correspondences,' arXiv preprint arXiv:2005.02357, 2020.",
        "[8] J. Johnson, M. Douze, and H. Jégou, 'Billion-scale similarity search with GPUs,' IEEE Trans. Big Data, vol. 7, no. 3, pp. 535–547, 2019. doi: 10.1109/TBDATA.2019.2921572.",
        "[9] E. B. Wilson, 'Probable inference, the law of large numbers, and run of evidence,' J. Amer. Statist. Assoc., vol. 22, no. 158, pp. 209–212, 1927. doi: 10.1080/01621459.1927.10502953.",
        "[10] D. Weimer, B. Scholz-Reiter, and M. Shpitalni, 'Design of deep convolutional neural networks for industrial inspection,' CIRP Annals — Manuf. Technol., vol. 65, no. 1, pp. 417–420, 2016. doi: 10.1016/j.cirp.2016.04.053.",
        "[11] A. Kumar, 'Computer vision-based fabric defect detection: A survey,' IEEE Trans. Ind. Electron., vol. 55, no. 1, pp. 348–363, 2008. doi: 10.1109/TIE.2007.895135.",
        "[12] R. O. Duda, P. E. Hart, and D. G. Stork, Pattern Classification, 2nd ed. New York, NY: John Wiley & Sons, 2001.",
        "[13] P. Mishra, C. Verkateren, B. Kamath, and Q. Zhou, 'VT-ADL: A vision transformer network for image anomaly detection and localization,' in Proc. IEEE WACV, 2021, pp. 398–407. doi: 10.1109/WACV48630.2021.00398.",
        "[14] Z. You, K. Yang, W. Luo, L. Cui, Y. Zheng, and X. Liu, 'A unified model for multi-class anomaly detection,' in Adv. Neural Inf. Process. Syst. (NeurIPS), vol. 35, 2022, pp. 4571–4584.",
        "[15] J. Bae, J.-H. Park, and S.-B. Pan, 'PNI: Industrial anomaly detection using position and neighborhood information,' IEEE Access, vol. 11, pp. 78263–78274, 2023. doi: 10.1109/ACCESS.2023.3298684.",
        "[16] M. Rudolph, B. Wandt, and B. Rosenhahn, 'Same same but DifferNet: Semi-supervised defect detection with normalizing flows,' in Proc. IEEE WACV, 2021, pp. 1907–1916. doi: 10.1109/WACV48630.2021.01912.",
        "[17] D. Gudovskiy, S. Ishizaka, and K. Kozuka, 'CFLOW-AD: Real-time unsupervised anomaly detection with localization via conditional normalizing flows,' in Proc. IEEE/CVF WACV, 2022, pp. 98–107. doi: 10.1109/WACV51458.2022.00105.",
        "[18] O. Rippel, P. Mertens, and D. Merhof, 'Modeling the distribution of normal data in pre-trained deep features for anomaly detection,' in Proc. 25th ICPR, 2021, pp. 6726–6733. doi: 10.1109/ICPR48806.2021.9412702.",
        "[19] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, 'CutPaste: Self-supervised learning for anomaly detection and localization,' in Proc. IEEE/CVF CVPR, 2021, pp. 9664–9674. doi: 10.1109/CVPR46437.2021.00951.",
        "[20] K. Batzner, L. Heckler, and R. König, 'EfficientAD: Accurate visual anomaly detection at millisecond-level latencies,' in Proc. IEEE/CVF WACV, 2024, pp. 128–138. doi: 10.1109/WACV57701.2024.00019.",
        "[21] H. Deng and X. Li, 'Anomaly detection via reverse distillation from one-class embedding,' in Proc. IEEE/CVF CVPR, 2022, pp. 9737–9746. doi: 10.1109/CVPR52688.2022.00950.",
        "[22] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, 'Beyond dents and scratches: Logical constraints in unsupervised anomaly detection and localization,' Int. J. Comput. Vis., vol. 130, no. 4, pp. 947–969, 2022. doi: 10.1007/s11263-022-01614-7.",
        "[23] X. Zhang, S. Li, X. Li, P. Huang, J. Shan, and T. Chen, 'DeSTSeg: Segmentation guided denoising student-teacher architecture for unsupervised anomaly detection,' in Proc. IEEE/CVF WACV, 2023, pp. 991–1000. doi: 10.1109/WACV56688.2023.00104.",
        "[24] Y. Cao, Q. Wan, W. Shen, and L. Gao, 'Informative knowledge distillation for image anomaly detection,' IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 11, pp. 13287–13302, 2023. doi: 10.1109/TPAMI.2023.3298457.",
        "[25] T. Czimmermann, G. Ciuti, M. Milazzo, M. Chiurazzi, S. Roccella, C. Stefanini, and P. Dario, 'Visual-based defect detection and classification approaches for industrial applications—A survey,' Sensors, vol. 20, no. 5, p. 1459, 2020. doi: 10.3390/s20051459.",
        "[26] Y. Wang, H. Shen, D. Chen, X. Yang, and L. Shen, 'Automated surface defect detection of industrial products: A comprehensive review,' IEEE Trans. Instrum. Meas., vol. 70, pp. 1–18, 2021. doi: 10.1109/TIM.2021.3117467.",
        "[27] A. Radford, J. W. Kim, C. Hallacy, A. Ramesh, G. Goh, S. Agarwal, G. Sastry, A. Askell, P. Mishkin, J. Clark, G. Krueger, and I. Sutskever, 'Learning transferable visual models from natural language supervision,' in Proc. 38th ICML, PMLR, vol. 139, 2021, pp. 8748–8763.",
        "[28] J. Yang, Y. Shi, and Z. He, 'DFR: Deep feature reconstruction for unsupervised anomaly detection,' arXiv preprint arXiv:2012.07122, 2020."
    ]
    for ref_str in refs:
        rp = doc.add_paragraph()
        rp.paragraph_format.space_after = Pt(4)
        rp.paragraph_format.line_spacing = 1.15
        r_run = rp.add_run(ref_str)
        r_run.font.size = Pt(9.5)

    docx_path = os.path.join(OUTPUT_DIR, "DefectVisionAI_JEAS_Manuscript.docx")
    doc.save(docx_path)
    print(f"Successfully generated DOCX manuscript: {docx_path}")

def create_cover_letter_docx():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(8)

    # Date & Addressee
    p = doc.add_paragraph()
    p.add_run("November 3, 2026\n\nTo:\nProf. Dr. Sayed A. Ward\nEditor-in-Chief, Journal of Engineering and Applied Science (JEAS)\nSpringerOpen / Faculty of Engineering, Cairo University\nEmail: jeas@cu.edu.eg")
    p.runs[0].bold = True

    # Subject
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(8)
    sp.paragraph_format.space_after = Pt(8)
    s_run = sp.add_run("Subject: Submission of Original Research Article to Journal of Engineering and Applied Science")
    s_run.bold = True

    # Body
    doc.add_paragraph("Dear Prof. Dr. Sayed A. Ward and Esteemed Editorial Board Members,")
    
    doc.add_paragraph(
        "I am pleased to submit our original research manuscript entitled 'Hybrid Visual Defect Inspection and Nominal-Only "
        "Adaptation: An Empirical Study of Detection Trade-Offs and Operational Constraints' for consideration as an original research article "
        "in the Journal of Engineering and Applied Science (JEAS)."
    )

    doc.add_paragraph(
        "Industrial surface inspection in modern high-throughput manufacturing faces an asymmetric operational challenge: undetected defect escapes "
        "lead to catastrophic downstream liabilities, while excessive false alarms incur substantial scrap costs and line stoppages. "
        "While deep learning has made remarkable progress, existing studies rarely quantify the concrete operational trade-off curve of hybrid "
        "decision fusion under production-like constraints."
    )

    doc.add_paragraph(
        "In this empirical applied-engineering study, we evaluate a dual-branch hybrid inspection architecture combining a supervised visual classifier "
        "(EfficientNet-B0 v3) with an unsupervised patch-distribution memory bank (PatchCore) via logical OR decision fusion. Our principal findings include:\n"
        "1. Decision-Fusion Trade-off: On an audited development-exposed benchmark of 856 MVTec AD specimens, OR-logic fusion reduced defect escapes "
        "by 48.6% (recovering 54 defects missed by EfficientNet-B0), at the operational expense of 11 additional false alarms (false positive rate rising from 0.43% to 5.19%).\n"
        "2. Independent Out-of-Distribution Validation: On 200 untouched Visual Anomaly (VisA) Cashew specimens, nominal-only PatchCore adaptation achieved "
        "an image AUROC of 0.9237 and full-census pixel AUROC of 0.9930 after registration on 350 nominals and threshold calibration on 50 held-out nominals (tau_p99.5 = 1.7452).\n"
        "3. Granular Failure Mode Forensics: A fine-grained reconciliation of the 100 defective specimens (90 single-morphology, 10 compound multi-defect) "
        "revealed an overall 43.0% escape rate concentrated heavily in fine surface flaws: gross structural breaks achieved 100% recall (8/8 middle breakage, 6/6 stuck together), "
        "localized voids achieved 81.8% marginal recall (18/22 caught; 17/20 single-defect), while hairline scratches suffered a 93.8% marginal escape rate "
        "(1/16 caught; 1/15 on single-defect specimens) and same-color indentations suffered an 85.7% marginal escape rate (2/14 caught; 0/10 single-defect).\n"
        "4. Hardware Feasibility on CPU: Full pipeline execution profiling on a 13th Gen Intel Core i5-1335U CPU workstation demonstrated deterministic PatchCore "
        "inference of 392.5 ms (median) and direct dual-model latency of 450.6 ms (mean 558.97 ms), confirming computational viability for discrete batch stations with cycle times >= 1.5 s."
    )

    doc.add_paragraph(
        "This manuscript adheres strictly to Springer Nature research integrity standards:\n"
        "- The manuscript represents original scholarly work and has not been published previously, nor is it under consideration by any other journal.\n"
        "- The single author has approved the manuscript and agrees with its submission to JEAS.\n"
        "- Full transparent disclosures regarding benchmark development exposure, single-category external validation, laboratory timing boundaries, "
        "and negative engineering findings (CPND and MACBA) are explicitly detailed.\n"
        "- The research evaluated publicly available benchmark datasets in strict compliance with their respective academic licenses (MVTec AD under CC BY-NC-SA 4.0, VisA under CC BY 4.0).\n"
        "- Generative AI assistance (Claude / Google Gemini) utilized for manuscript drafting, structuring, and editing support has been fully disclosed in compliance with Springer Nature policy.\n"
        "- The author confirms there are no competing financial or non-financial conflicts of interest."
    )

    doc.add_paragraph("Thank you very much for your time and consideration of our manuscript. I look forward to hearing from you following the peer-review process.")

    # Sign-off
    sop = doc.add_paragraph()
    sop.paragraph_format.space_before = Pt(8)
    sop.add_run("Sincerely,\n\nSurya Charan\n[Affiliation: AUTHOR CONFIRMATION REQUIRED]\nEmail: suryacharan945@gmail.com")

    cl_path = os.path.join(OUTPUT_DIR, "JEAS_Cover_Letter.docx")
    doc.save(cl_path)
    print(f"Successfully generated Cover Letter DOCX: {cl_path}")

if __name__ == "__main__":
    create_manuscript_docx()
    create_cover_letter_docx()
