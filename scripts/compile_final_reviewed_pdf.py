import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = r"C:\Users\surya\Downloads\Mini Project\release\final_publication_review\DefectVisionAI_Final_Reviewed.pdf"
FIG_DIR = r"C:\Users\surya\Downloads\Mini Project\release\final_publication_review\figures"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Times-Roman", 8)
        self.setFillColor(colors.HexColor("#495057"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            header_text = "IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, REGULAR PAPER, NOVEMBER 2026"
            self.drawRightString(612 - 36, 792 - 28, header_text)
            self.setStrokeColor(colors.HexColor("#CED4DA"))
            self.setLineWidth(0.5)
            self.line(36, 792 - 32, 612 - 36, 792 - 32)

        # Footer
        footer_left = "DEFECTVISION AI — REPRODUCIBLE RESEARCH MANUSCRIPT (FINAL REVIEWED VERSION)"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(36, 25, footer_left)
        self.drawRightString(612 - 36, 25, footer_right)
        self.setStrokeColor(colors.HexColor("#CED4DA"))
        self.setLineWidth(0.5)
        self.line(36, 32, 612 - 36, 32)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Custom Academic Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor("#0B2545")
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#134074")
    )
    abstract_heading = ParagraphStyle(
        'AbstractHeading',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0B2545")
    )
    abstract_body = ParagraphStyle(
        'AbstractBody',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8.2,
        leading=11.0,
        alignment=4 # Justify
    )
    keywords_style = ParagraphStyle(
        'KeywordsStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.2,
        leading=11.0
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=10.5,
        leading=14,
        spaceBefore=10,
        spaceAfter=3,
        textColor=colors.HexColor("#0B2545")
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=9.2,
        leading=12.5,
        spaceBefore=7,
        spaceAfter=2,
        textColor=colors.HexColor("#134074")
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.8,
        leading=11.8,
        alignment=4, # Justify
        spaceAfter=4
    )
    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=7.8,
        leading=10.0,
        alignment=1,
        textColor=colors.HexColor("#2B2D42"),
        spaceBefore=3,
        spaceAfter=6
    )
    ref_style = ParagraphStyle(
        'RefStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=7.8,
        leading=10.0,
        spaceAfter=2.5
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Hybrid Visual Defect Inspection and Nominal-Only Adaptation:<br/>An Empirical Study of Detection Trade-Offs and Operational Constraints", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Surya Charan</b><br/>Department of Computer Science and Engineering &bull; DefectVision AI Research Group<br/>Email: suryacharan945@gmail.com", author_style))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0B2545"), spaceAfter=6))

    # Abstract Box
    abs_text = (
        "<b><i>Abstract</i>—Automated visual inspection in high-throughput manufacturing confronts an asymmetric operational penalty: "
        "undetected defect escapes can result in catastrophic downstream product failures, while excessive false alarms incur substantial scrap costs "
        "and line stoppages. Supervised deep convolutional classifiers achieve high precision on recurring, anticipated defect classes but frequently "
        "fail on rare, novel defect morphologies. Conversely, unsupervised patch-based anomaly detectors capture arbitrary distribution shifts without "
        "defect supervision, but can suffer from elevated false-positive rates due to natural intra-class surface variance. In this paper, we conduct an "
        "empirical investigation into a dual-branch hybrid inspection architecture combining a supervised visual classifier (EfficientNet-B0 v3) with an "
        "unsupervised patch-distribution memory bank (PatchCore), characterizing the concrete trade-offs, computational overhead, and adaptation boundaries "
        "inherent to practical deployment. On an audited development-exposed benchmark of 856 industrial specimens from the MVTec Anomaly Detection dataset, "
        "the hybrid decision policy (logical OR) increased defect recall from 82.24% to 90.88%, successfully capturing 54 defect instances missed by the "
        "standalone supervised model (slashing escapes from 111 to 57), while increasing false alarms from 1 to 12 (false positive rate rising from 0.43% to 5.19%). "
        "To assess cross-domain transfer without defect supervision, we independently evaluated the patch-level memory pipeline on the untouched Visual Anomaly (VisA) "
        "Cashew benchmark using 350 domain-specific nominal specimens for registration and 50 held-out nominals for threshold calibration (&tau;<sub>p99.5</sub> = 1.7452, "
        "evaluated at the 99.5th percentile of the calibration distribution, designated &tau;<sub>p99</sub> in software manifests). "
        "Across 200 independent test specimens (100 nominal, 100 defective), the adapted model achieved an image-level AUROC of 0.9237 [95% CI: 0.8852, 0.9565], "
        "an image-level AUPRC of 0.9270, and a full-census pixel-level AUROC of 0.9930 across 10.03 million evaluated pixels. Operating at the locked 99.5th-percentile "
        "calibration threshold enforced a high specificity of 98.00% (2.00% false alarm rate); however, granular sensitivity profiling revealed a 43.00% defect "
        "escape rate concentrated heavily in fine surface flaws: gross structural breaks and boundary distortions achieved 100% recall (6/6), dark voids achieved 85.0% "
        "recall (17/20), whereas hairline scratches and same-color depressions yielded escape rates of 93.3% (1/15 recall) and 100.0% (0/10 recall), respectively. "
        "Execution profiling on consumer multi-core CPU hardware confirmed memory registration in 392.25 s (27,440 coreset tokens, 40.2 MB index) and deterministic forward "
        "inference of 392.5 ms median (p95: 438.1 ms), confirming computational feasibility for discrete inspection stations with cycle times &ge; 1.5 s. "
        "We explicitly disclose that: (1) MVTec AD evaluations represent development-exposed benchmark results; (2) independent validation is restricted to PatchCore on VisA Cashew; "
        "(3) all robustness evaluations utilized synthetic perturbations rather than factory drifts; and (4) no live factory conveyor trial was conducted. "
        "Our findings demonstrate that while nominal-only adaptation provides robust baseline containment and high localization precision, automated unassisted sorting requires "
        "multi-scale optical resolution or secondary verification to mitigate the severe tension between false-alarm suppression and hairline flaw escapes.</b>"
    )
    story.append(Paragraph(abs_text, abstract_body))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b><i>Index Terms</i>—Industrial defect inspection, anomaly detection, PatchCore, EfficientNet, decision fusion, quality control, operational trade-offs, VisA benchmark.</b>", keywords_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#0B2545"), spaceBefore=5, spaceAfter=8))

    # SECTION I: INTRODUCTION
    story.append(Paragraph("I. INTRODUCTION", h1_style))
    story.append(Paragraph(
        "Automated surface defect inspection represents a critical quality assurance pillar across precision manufacturing, including semiconductor fabrication, "
        "automotive stamping, pharmaceutical packaging, and consumer goods sorting [10], [11]. In modern production environments, visual quality gating operates under an "
        "asymmetric cost matrix. A Type II error (false negative / defect escape) delivers substandard or structurally compromised components to downstream assembly lines "
        "or end customers, risking catastrophic equipment damage, safety hazards, and costly product recalls. Conversely, a Type I error (false positive / false alarm) falsely "
        "flags conforming product as defective, inducing unnecessary component scrap, excessive manual reinspection labor, and disruptive production line stoppages [11], [12].",
        body_style
    ))
    story.append(Paragraph(
        "In recent years, deep learning methodologies for automated visual inspection have bifurcated into two primary paradigms: (1) Supervised Visual Classification, "
        "which achieves high precision on recurring, anticipated defect classes but fails on unrepresented anomaly geometries [4], [10]; and (2) Unsupervised Anomaly Detection, "
        "which models nominal distributions to identify novel anomalies without defect annotations, but often suffers from elevated false-alarm rates in the presence of natural "
        "material variance [1], [6]. Combining both engines via logical disjunction (OR-logic) offers an intuitive compromise, yet prior literature rarely quantifies the concrete "
        "false-alarm penalty required to reduce defect escapes by a given margin. Furthermore, empirical evaluations under rigorous zero-leakage adaptation protocols remain scarce.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Contributions and Disclosures:</b> Rather than claiming mathematical or algorithmic novelty, this work contributes an empirical systems characterization under realistic "
        "industrial constraints: (1) empirical quantification of the hybrid cost curve on 856 MVTec AD specimens; (2) zero-leakage independent validation of nominal PatchCore adaptation "
        "on 200 VisA Cashew specimens; (3) fine-grained morphology sensitivity breakdown uncovering the hairline scratch failure mode; (4) CPU hardware latency and takt-time profiling; "
        "(5) transparent reporting of negative findings (CPND and MACBA); and (6) full disclosure of operational boundaries—including MVTec development exposure, synthetic robustness testing, "
        "and the absence of live factory conveyor trials.",
        body_style
    ))

    # Figure 1: Architecture
    fig1_path = os.path.join(FIG_DIR, "fig1_architecture.png")
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=490, height=265))
        story.append(Paragraph("Fig. 1. Architecture of the DefectVision AI dual-branch hybrid inspection pipeline combining supervised classification (EfficientNet-B0 v3) and unsupervised patch anomaly memory (PatchCore) via logical OR decision fusion.", caption_style))

    # SECTION II: RELATED WORK
    story.append(Paragraph("II. RELATED WORK", h1_style))
    story.append(Paragraph(
        "Supervised convolutional networks (e.g. EfficientNet-B0 [4], ResNet [5]) excel at feature discrimination but assume a closed-world distribution [10]. "
        "Unsupervised methods address this by modeling nominal appearance exclusively. While generative models (Autoencoders, GANs) suffer from reconstruction blur, "
        "feature-embedding frameworks (SPADE [7], PaDiM [6], PatchCore [1]) achieve state-of-the-art localization. PatchCore condenses mid-level convolutional patch "
        "representations via greedy minimax coreset selection, enabling fast nearest-neighbor anomaly scoring [1]. However, comprehensive evaluations on independent "
        "non-rigid organic benchmarks such as VisA [2] under frozen audit protocols remain necessary to verify cross-domain adaptation.",
        body_style
    ))

    # SECTION III: SYSTEM METHODOLOGY
    story.append(Paragraph("III. SYSTEM METHODOLOGY AND ARCHITECTURE", h1_style))
    story.append(Paragraph(
        "The system processes incoming imagery through two concurrent pipelines: (1) An unsupervised PatchCore branch utilizing frozen ResNet-18 intermediate stages "
        "(layer2 and layer3, D=384 channels) subsampled to 27,440 coreset tokens (&kappa;=0.10) indexed in a FAISS L2 flat index [8]; and (2) A supervised EfficientNet-B0 v3 "
        "classifier producing posterior probability p_defect. Statistical decision threshold calibration locks &tau;<sub>p99.5</sub> = 1.7452 on 50 nominal held-out samples. "
        "For audit precision, we record that while software configuration manifests designated this parameter as <code>threshold_p99</code> or <code>tau_p99</code>, "
        "its mathematical derivation corresponds to the empirical 99.5th percentile of the calibration distribution. The dual-branch decision fusion rule executes "
        "as y_hybrid = d_clf OR (S_img &ge; &tau;<sub>p99.5</sub>).",
        body_style
    ))

    # SECTION IV: EXPERIMENTAL SETUP
    story.append(Paragraph("IV. EXPERIMENTAL SETUP AND AUDIT PROTOCOLS", h1_style))
    story.append(Paragraph(
        "All experiments were conducted on an Intel Core i7-10750H CPU @ 2.60GHz with 16 GB DDR4 RAM running PyTorch 2.15.0+cpu with fixed random seed S=42. "
        "Two benchmark datasets were utilized: (1) MVTec AD (856 test images, CC BY-NC-SA 4.0), designated as Category C Development-Exposed; and (2) VisA Cashew "
        "(200 test images, Apache 2.0), evaluated under an untouched, zero-leakage protocol (350 nominal registration, 50 nominal calibration, 100 nominal / 100 defective independent test). "
        "Confidence intervals were derived via Wilson score intervals (z=1.96) for binomial proportions [9] and empirical bootstrap (B=1,000) for AUROC. "
        "All robustness evaluations utilized synthetic perturbations (Gaussian noise, illumination scaling, affine jitter); no live factory trial was conducted.",
        body_style
    ))

    # Table I: MVTec Comparison
    story.append(Paragraph("V. DEVELOPMENT-EXPOSED BENCHMARK EVALUATION (MVTEC AD)", h1_style))
    story.append(Paragraph(
        "Table I details the performance comparison across the 856-image MVTec AD benchmark. Standalone EfficientNet-B0 missed 111 defects (recall 82.24%) with exceptional "
        "specificity (99.57%, 1 false alarm). The dual-branch hybrid captured 54 of those missed defects (reducing escapes to 57, recall 90.88%), but increased false alarms "
        "twelve-fold (12 false alarms, FPR 5.19%). This confirms that hybrid fusion reallocates operational risk rather than achieving universal metric dominance.",
        body_style
    ))

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
    t1 = Table(t1_data, colWidths=[110, 85, 85, 95, 115])
    t1.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E9ECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0B2545")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0B2545")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t1)
    story.append(Paragraph("TABLE I: Quantitative Performance Comparison on the Audited 856-Image MVTec AD Benchmark. *PatchCore AUROC reflects category-standardized z-scores.", caption_style))

    # Figure 2: Confusion Matrices
    fig2_path = os.path.join(FIG_DIR, "fig2_confusion_matrices.png")
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=475, height=220))
        story.append(Paragraph("Fig. 2. Confusion matrix comparison on 856 MVTec AD specimens demonstrating that hybrid decision fusion reduces missed defects by 54 at the cost of 11 additional false alarms.", caption_style))

    # SECTION VI: INDEPENDENT VALIDATION
    story.append(Paragraph("VI. INDEPENDENT OUT-OF-DISTRIBUTION VALIDATION (VISA CASHEW)", h1_style))
    story.append(Paragraph(
        "On 200 untouched VisA Cashew specimens, PatchCore nominal adaptation achieved an Image AUROC of 0.9237 [95% CI: 0.8852, 0.9565] and a full-census Pixel AUROC of 0.9930 "
        "across 10.03 million evaluated pixels. At &tau;<sub>p99.5</sub> = 1.7452, specificity was 98.00% (2 false alarms). However, defect recall was limited to 57.00% (43 escapes). "
        "Table II summarizes these metrics, and Table III exposes the underlying morphological failure modes.",
        body_style
    ))

    # Figure 3: ROC & PR Curves
    fig3_path = os.path.join(FIG_DIR, "fig3_roc_pr_curves.png")
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=475, height=220))
        story.append(Paragraph("Fig. 3. Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves for PatchCore nominal adaptation on 200 untouched VisA Cashew test specimens, highlighting the locked operating point (&tau;<sub>p99.5</sub> = 1.7452).", caption_style))

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
    t2 = Table(t2_data, colWidths=[130, 95, 245])
    t2.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E9ECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0B2545")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0B2545")),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t2)
    story.append(Paragraph("TABLE II: Independent Validation Results on the Untouched VisA Cashew Benchmark (N=200).", caption_style))

    # Figure 4: Morphology Breakdown
    fig4_path = os.path.join(FIG_DIR, "fig4_defect_morphology.png")
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=475, height=235))
        story.append(Paragraph("Fig. 4. Granular defect recall across primary VisA Cashew defect morphologies (N=100 defective specimens), demonstrating the severe escape rate on hairline scratches and same-color indentations under conservative factory thresholds.", caption_style))

    # Table III: Morphology Breakdown Table
    t3_data = [
        ["Defect Category / Morphology", "Total", "TP", "FN", "Recall (%)"],
        ["middle breakage", "6", "6", "0", "100.0%"],
        ["stuck together", "6", "6", "0", "100.0%"],
        ["different colour spot", "9", "8", "1", "88.9%"],
        ["small holes", "20", "17", "3", "85.0%"],
        ["corner or edge breakage", "14", "11", "3", "78.6%"],
        ["burnt", "10", "4", "6", "40.0%"],
        ["small scratches", "15", "1", "14", "6.7% (93.3% Escape)"],
        ["same colour spot", "10", "0", "10", "0.0% (100.0% Escape)"],
        ["Total Defective Cohort", "100", "57", "43", "57.0% (43.0% Escape)"]
    ]
    t3 = Table(t3_data, colWidths=[170, 60, 60, 60, 120])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTNAME', (0,-1), (-1,-1), 'Times-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E9ECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0B2545")),
        ('LINEABOVE', (0,-1), (-1,-1), 0.8, colors.HexColor("#0B2545")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0B2545")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t3)
    story.append(Paragraph("TABLE III: Granular Detection Performance Across Primary VisA Cashew Defect Morphologies.", caption_style))

    # SECTION VII: OPERATIONAL FEASIBILITY
    story.append(Paragraph("VII. OPERATIONAL FEASIBILITY, LATENCY PROFILING, AND QUALITY ECONOMICS", h1_style))
    story.append(Paragraph(
        "Computational profiling on an Intel Core i7-10750H CPU demonstrated that target-domain registration of 350 images required 392.25 seconds (~6.5 minutes), "
        "producing a compact 40.2 MB memory index. Per-image inference latency on CPU was 392.5 ms median (p95: 438.1 ms) for standalone PatchCore, and 881.7 ms median "
        "(p95: 1455.7 ms) for end-to-end hybrid API calls. This confirms computational compatibility for discrete inspection stations with cycle times >= 1.5 seconds, "
        "while high-speed continuous lines (< 100 ms) require dedicated edge GPU acceleration or quantization.",
        body_style
    ))

    # Figure 5: Latency Profiling
    fig5_path = os.path.join(FIG_DIR, "fig5_cpu_latency.png")
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=475, height=220))
        story.append(Paragraph("Fig. 5. Computational execution latency profiling across individual pipeline stages on an Intel Core i7-10750H CPU, showing compatibility with discrete line takt times (>= 1.5 s).", caption_style))

    # SECTION VIII: DISCUSSION & LIMITATIONS
    story.append(Paragraph("VIII. DISCUSSION, LIMITATIONS, AND NEGATIVE FINDINGS", h1_style))
    story.append(Paragraph(
        "We transparently disclose two negative findings encountered during development: (1) Context-Preserving Normalization Dropout (CPND) yielded statistically "
        "indistinguishable generalization relative to standard dropout (p=0.42); and (2) Multi-Axis Cross-Branch Attention (MACBA) suffered gradient divergence during "
        "joint branch backpropagation, demonstrating that late-stage OR-logic decision fusion is structurally superior to early deep feature coupling. "
        "We also explicitly record our operational limitations: (1) absence of live factory conveyor trials; (2) asymmetric validation of PatchCore alone without the supervised classifier; "
        "(3) evaluation on a single external category; and (4) reliance on synthetic noise rather than industrial plant drifts. "
        "Due to the 43.0% escape rate on subtle hairline scratches, DefectVision AI is formally gated as APPROVED for supervised operator-assist shadow-piloting, "
        "but STRICT NO-GO for unassisted autonomous inline rejection.",
        body_style
    ))

    # SECTION IX: CONCLUSION
    story.append(Paragraph("IX. CONCLUSION", h1_style))
    story.append(Paragraph(
        "This empirical investigation quantified the operational trade-offs of hybrid defect inspection and nominal-only adaptation. On MVTec AD, hybrid fusion reduced defect escapes "
        "by 48.6% (+54 defects caught) at the expense of 11 additional false alarms. On VisA Cashew, nominal adaptation achieved 0.9237 image AUROC and 0.9930 pixel AUROC on CPU, "
        "yet exposed a 93.3% escape rate on hairline scratches under conservative false-alarm boundaries. Automated quality control must employ multi-resolution or multi-stage "
        "architectures to resolve this fundamental operational tension.",
        body_style
    ))

    # REFERENCES
    story.append(Paragraph("REFERENCES", h1_style))
    refs = [
        "[1] K. Roth, L. Pemula, J. Zepeda, B. Schölkopf, T. Brox, and P. Gehler, 'Towards total recall in industrial anomaly detection,' in Proc. IEEE/CVF CVPR, 2022, pp. 14318–14328. doi: 10.1109/CVPR52688.2022.01392.",
        "[2] Y. Zou, J. Jeong, L. Pemula, D. Zhang, and O. Dabeer, 'SPOT-the-difference self-supervised pre-training for anomaly detection and segmentation,' in Proc. ECCV, Springer, 2022, pp. 392–408. doi: 10.1007/978-3-031-19821-2_23.",
        "[3] P. Bergmann, K. Batzner, M. Fauser, D. Sattlegger, and C. Steger, 'The MVTec anomaly detection dataset: A comprehensive real-world dataset for unsupervised anomaly detection,' Int. J. Comput. Vis., vol. 129, no. 4, pp. 1038–1059, 2021. doi: 10.1007/s11263-020-01400-4.",
        "[4] M. Tan and Q. V. Le, 'EfficientNet: Rethinking model scaling for convolutional neural networks,' in Proc. 36th ICML, PMLR, vol. 97, 2019, pp. 6105–6114.",
        "[5] K. He, X. Zhang, S. Ren, and Jian Sun, 'Deep residual learning for image recognition,' in Proc. IEEE CVPR, 2016, pp. 770–778. doi: 10.1109/CVPR.2016.90.",
        "[6] T. Defard, A. Setkov, A. Loesch, and R. Audigier, 'PaDiM: A patch distribution modeling framework for anomaly detection and localization,' in Proc. ICPR, 2021, pp. 475–489. doi: 10.1007/978-3-030-68799-1_35.",
        "[7] N. Cohen and Y. Hoshen, 'Sub-image anomaly detection with deep pyramid correspondences,' arXiv preprint arXiv:2005.02357, 2020.",
        "[8] J. Johnson, M. Douze, and H. Jégou, 'Billion-scale similarity search with GPUs,' IEEE Trans. Big Data, vol. 7, no. 3, pp. 535–547, 2019. doi: 10.1109/TBDATA.2019.2921572.",
        "[9] E. B. Wilson, 'Probable inference, the law of large numbers, and run of evidence,' J. Amer. Statist. Assoc., vol. 22, no. 158, pp. 209–212, 1927. doi: 10.1080/01621459.1927.10502953.",
        "[10] D. Weimer, B. Scholz-Reiter, and M. Shpitalni, 'Design of deep convolutional neural networks for industrial inspection,' CIRP Annals — Manuf. Technol., vol. 65, no. 1, pp. 417–420, 2016. doi: 10.1016/j.cirp.2016.04.053.",
        "[11] A. Kumar, 'Computer vision-based fabric defect detection: A survey,' IEEE Trans. Ind. Electron., vol. 55, no. 1, pp. 348–363, 2008. doi: 10.1109/TIE.2007.895135.",
        "[12] R. O. Duda, P. E. Hart, and D. G. Stork, Pattern Classification, 2nd ed. New York, NY: John Wiley & Sons, 2001."
    ]
    for r in refs:
        story.append(Paragraph(r, ref_style))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled publication manuscript PDF: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
