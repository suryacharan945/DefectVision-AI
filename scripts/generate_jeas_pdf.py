import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = r"C:\Users\surya\Downloads\Mini Project\release\JEAS_final_submission\DefectVisionAI_JEAS_Manuscript.pdf"
FIG_DIR = r"C:\Users\surya\Downloads\Mini Project\release\JEAS_final_submission\figures"

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
        self.setFont("Times-Roman", 8.5)
        self.setFillColor(colors.HexColor("#495057"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            header_text = "Author-Compiled Review Copy (Prepared for Submission to JEAS)"
            self.drawRightString(612 - 54, 792 - 36, header_text)
            self.setStrokeColor(colors.HexColor("#CED4DA"))
            self.setLineWidth(0.5)
            self.line(54, 792 - 40, 612 - 54, 792 - 40)

        # Footer
        footer_left = "DefectVision AI: Hybrid Defect Inspection & Nominal-Only Adaptation"
        footer_right = f"Page {self._pageNumber} of {page_count}"
        self.drawString(54, 34, footer_left)
        self.drawRightString(612 - 54, 34, footer_right)
        self.setStrokeColor(colors.HexColor("#CED4DA"))
        self.setLineWidth(0.5)
        self.line(54, 42, 612 - 54, 42)
        
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom academic styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=16,
        leading=21,
        alignment=0, # Left
        textColor=colors.HexColor("#0A2540"),
        spaceAfter=12
    )
    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#1A1A1A"),
        spaceAfter=2
    )
    affil_style = ParagraphStyle(
        'DocAffil',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12
    )
    abs_title_style = ParagraphStyle(
        'AbsTitle',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#0A2540"),
        spaceBefore=8,
        spaceAfter=4
    )
    abs_body_style = ParagraphStyle(
        'AbsBody',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        alignment=4, # Justify
        spaceAfter=8
    )
    kw_style = ParagraphStyle(
        'KeywordsStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=14,
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Times-Bold',
        fontSize=12.5,
        leading=16,
        spaceBefore=14,
        spaceAfter=4,
        textColor=colors.HexColor("#0A2540")
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Times-BoldItalic',
        fontSize=11,
        leading=14.5,
        spaceBefore=10,
        spaceAfter=3,
        textColor=colors.HexColor("#1B4965")
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=10,
        leading=13.8,
        alignment=4, # Justify
        spaceAfter=6
    )
    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8.5,
        leading=11.5,
        alignment=1, # Center
        textColor=colors.HexColor("#333333"),
        spaceBefore=4,
        spaceAfter=10
    )
    ref_style = ParagraphStyle(
        'RefStyle',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=8.5,
        leading=11.5,
        spaceAfter=3.5
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Hybrid Visual Defect Inspection and Nominal-Only Adaptation: An Empirical Study of Detection Trade-Offs and Operational Constraints", title_style))
    story.append(Paragraph("Surya Charan*", author_style))
    story.append(Paragraph("<b>[Affiliation: AUTHOR CONFIRMATION REQUIRED]</b><br/>Email: suryacharan945@gmail.com | *Corresponding author", affil_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0A2540"), spaceAfter=10))

    # Abstract Box
    disclaimer_style = ParagraphStyle(
        'DocDisclaimer',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#721C24"),
        alignment=1,
        spaceAfter=10
    )
    story.append(Paragraph("<b>Author Review Copy — Formatted for Offline Inspection and Review (Formal Submission Document is DefectVisionAI_JEAS_Manuscript.docx)</b>", disclaimer_style))
    story.append(Paragraph("Abstract", abs_title_style))
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
        "50 held-out nominals (tau_p99.5 = 1.7452). PatchCore achieved an image AUROC of 0.9237 and a full-census pixel AUROC of 0.9930. However, "
        "granular morphology reconciliation revealed a 43.0% defect escape rate concentrated heavily in fine surface flaws: gross structural breaks "
        "achieved 100% recall, whereas hairline scratches suffered a 93.8% escape rate (1/16 recall). CPU execution profiling on an Intel Core "
        "i5-1335U demonstrated measured median inference latency of 392.5 ms (p95: 438.1 ms), confirming computational feasibility for discrete line takt times (>= 1.5 s). "
        "We disclose all experimental boundaries, concluding that while nominal adaptation provides viable containment assistance, unassisted autonomous "
        "sorting requires addressing downsampling limits on micro-flaws."
    )
    story.append(Paragraph(abs_text, abs_body_style))
    story.append(Paragraph("<b>Keywords:</b> Industrial visual inspection, Anomaly detection, PatchCore, EfficientNet, Decision fusion, VisA benchmark.", kw_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#0A2540"), spaceBefore=4, spaceAfter=12))

    # SECTION 1: INTRODUCTION
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph(
        "Automated surface defect inspection represents an essential quality assurance function across precision manufacturing sectors, "
        "including semiconductor device packaging, automotive metal stamping, pharmaceutical blister auditing, and consumer goods sorting [10, 11, 26]. "
        "In practical production environments, visual quality gating operates under an inherently asymmetric cost matrix. A Type II error "
        "(false negative / defect escape) delivers substandard or structurally compromised components to downstream assembly lines or end customers, "
        "risking equipment damage, safety hazards, warranty liabilities, and costly product recalls. Conversely, a Type I error "
        "(false positive / false alarm) falsely flags conforming product as defective, inducing unnecessary component scrap, excessive manual reinspection labor, "
        "and disruptive production line stoppages [11, 12].",
        body_style
    ))
    story.append(Paragraph(
        "In recent years, deep learning methodologies for automated visual inspection have bifurcated into two primary paradigms: "
        "(1) Supervised Visual Classification, which trains deep convolutional neural networks or Vision Transformers on annotated flaw libraries [4, 10, 13]; "
        "and (2) Unsupervised Anomaly Detection, which models nominal component distributions without defect supervision [1, 6, 7, 16, 20]. "
        "Combining both branches via logical disjunction (OR-logic) offers an intuitive compromise, yet prior literature rarely quantifies the concrete "
        "false-alarm penalty required to reduce defect escapes by a given margin. Furthermore, empirical evaluations under rigorous zero-leakage adaptation "
        "protocols on unseen organic substrates remain scarce.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Contributions of This Work:</b> Rather than asserting algorithmic novelty, this work contributes an empirical systems characterization under realistic "
        "industrial constraints: (1) direct quantification of the hybrid cost curve on 856 MVTec AD specimens; (2) zero-leakage independent validation of nominal "
        "PatchCore adaptation on 200 VisA Cashew specimens; (3) fine-grained morphology sensitivity breakdown uncovering the hairline scratch failure mode; "
        "(4) CPU hardware latency and takt-time profiling; (5) transparent reporting of negative findings (CPND and MACBA); and (6) full disclosure of operational "
        "boundaries—including MVTec development exposure, synthetic robustness testing, and the absence of live factory conveyor trials.",
        body_style
    ))

    # Figure 1: Architecture
    fig1_path = os.path.join(FIG_DIR, "fig1_architecture.png")
    if os.path.exists(fig1_path):
        story.append(Image(fig1_path, width=480, height=260))
        story.append(Paragraph("Fig. 1. Architecture of the DefectVision AI dual-branch hybrid inspection pipeline combining supervised classification (EfficientNet-B0 v3) and unsupervised patch anomaly memory (PatchCore) via logical OR decision fusion.", caption_style))

    # SECTION 2: RELATED WORK
    story.append(Paragraph("2. Related Work", h1_style))
    story.append(Paragraph(
        "Supervised convolutional networks (e.g. EfficientNet-B0 [4], ResNet [5]) excel at feature discrimination across known classes but operate under closed-world assumptions [10, 25]. "
        "Unsupervised methods address this by modeling nominal appearance exclusively. While generative models suffer from reconstruction blur [3], "
        "feature-embedding frameworks (SPADE [7], PaDiM [6], PatchCore [1], DifferNet [16], CFLOW-AD [17], EfficientAD [20], Reverse Distillation [21]) achieve state-of-the-art localization. "
        "PatchCore condenses mid-level convolutional patch representations via greedy minimax coreset selection, enabling fast nearest-neighbor anomaly scoring [1]. "
        "However, comprehensive evaluations on independent non-rigid organic benchmarks such as VisA [2] under frozen audit protocols remain necessary to verify cross-domain adaptation.",
        body_style
    ))

    # SECTION 3: MATERIALS AND METHODS
    story.append(Paragraph("3. Materials and Methods", h1_style))
    story.append(Paragraph(
        "The system processes incoming imagery through two concurrent pipelines: (1) An unsupervised PatchCore branch utilizing frozen ResNet-18 intermediate stages "
        "(layer2 and layer3, D=384 channels) subsampled to 27,440 coreset tokens (kappa=0.10) indexed in a FAISS L2 flat index [8]; and (2) A supervised EfficientNet-B0 v3 "
        "classifier producing posterior probability p_defect. Statistical decision threshold calibration locks tau_p99.5 = 1.7452 on 50 nominal held-out samples. "
        "For audit precision, we record that while software configuration manifests designated this parameter as threshold_p99, its mathematical derivation "
        "corresponds to the empirical 99.5th percentile of the calibration distribution. The dual-branch decision fusion rule executes as y_hybrid = d_clf OR (S_img >= tau_p99.5).",
        body_style
    ))

    # SECTION 4: EXPERIMENTAL DESIGN
    story.append(Paragraph("4. Experimental Design and Audit Protocols", h1_style))
    story.append(Paragraph(
        "All experiments were executed on an engineering workstation equipped with a 13th Gen Intel Core i5-1335U CPU @ 1.30 GHz (10 cores, 12 threads), 16.0 GB DDR4 RAM, "
        "Python 3.12.4, PyTorch 2.15.0+cpu, Torchvision 0.29.2+cpu, and FAISS-CPU 1.15.1 with fixed seed S=42. Two benchmarks were evaluated: (1) MVTec AD (856 test images, "
        "Category C Development-Exposed, CC BY-NC-SA 4.0); and (2) VisA Cashew (200 test images, Apache 2.0), evaluated under an untouched, zero-leakage protocol "
        "(350 nominal registration, 50 nominal calibration, 100 nominal / 100 defective independent test). Confidence intervals were derived via Wilson score intervals (z=1.96) [9] "
        "and empirical bootstrap (B=1,000) for AUROC.",
        body_style
    ))

    # SECTION 5: RESULTS
    story.append(Paragraph("5. Results", h1_style))
    story.append(Paragraph(
        "Table 1 details the performance comparison across the 856-image MVTec AD benchmark. Standalone EfficientNet-B0 missed 111 defects (recall 82.24%) with exceptional "
        "specificity (99.57%, 1 false alarm). The dual-branch hybrid captured 54 of those missed defects (reducing escapes to 57, recall 90.88%), but increased false alarms "
        "twelve-fold (12 false alarms, FPR 5.19%). This confirms that hybrid fusion reallocates operational risk rather than achieving universal metric dominance.",
        body_style
    ))

    # Table 1: MVTec Comparison
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
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0A2540")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0A2540")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t1)
    story.append(Paragraph("Table 1. Quantitative Performance Comparison on the Audited 856-Image MVTec AD Benchmark. *PatchCore AUROC reflects category-standardized z-scores.", caption_style))

    # Figure 2: Confusion Matrices
    fig2_path = os.path.join(FIG_DIR, "fig2_confusion_matrices.png")
    if os.path.exists(fig2_path):
        story.append(Image(fig2_path, width=475, height=220))
        story.append(Paragraph("Fig. 2. Confusion matrix comparison on 856 MVTec AD specimens (Category C Development-Exposed) demonstrating that hybrid decision fusion reduces missed defects by 54 at the cost of 11 additional false alarms.", caption_style))

    # SECTION 5.2: VisA Independent Validation
    story.append(Paragraph("5.2 Independent Out-of-Distribution Validation (VisA Cashew)", h2_style))
    story.append(Paragraph(
        "On 200 untouched VisA Cashew specimens, PatchCore nominal adaptation achieved an Image AUROC of 0.9237 [95% CI: 0.8852, 0.9565] and a full-census Pixel AUROC of 0.9930 "
        "across 10.03 million evaluated pixels. At tau_p99.5 = 1.7452, specificity was 98.00% (2 false alarms). However, defect recall was limited to 57.00% (43 escapes). "
        "Table 2 summarizes these metrics, and Table 3 exposes the underlying morphological failure modes.",
        body_style
    ))

    # Figure 3: ROC & PR Curves
    fig3_path = os.path.join(FIG_DIR, "fig3_roc_pr_curves.png")
    if os.path.exists(fig3_path):
        story.append(Image(fig3_path, width=475, height=220))
        story.append(Paragraph("Fig. 3. Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves for PatchCore nominal adaptation on 200 untouched VisA Cashew test specimens, highlighting the locked operating point (tau_p99.5 = 1.7452).", caption_style))

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
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0A2540")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0A2540")),
        ('ALIGN', (1,0), (1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t2)
    story.append(Paragraph("Table 2. Independent Validation Results on the Untouched VisA Cashew Benchmark (N=200).", caption_style))

    # SECTION 5.3: Morphology Breakdown
    story.append(Paragraph("5.3 Reconciled Morphology Breakdown Across Defect Taxonomies", h2_style))
    story.append(Paragraph(
        "In the official VisA Cashew annotations, 90 defective specimens exhibit a single primary flaw morphology, while 10 specimens exhibit multiple co-occurring flaw types. "
        "Table 3 partitions the 100 defective specimens into single- and compound-morphology cohorts, while documenting marginal flaw sensitivity across all 110 morphology annotations.",
        body_style
    ))

    # Figure 4: Morphology Breakdown
    fig4_path = os.path.join(FIG_DIR, "fig4_defect_morphology.png")
    if os.path.exists(fig4_path):
        story.append(Image(fig4_path, width=475, height=235))
        story.append(Paragraph("Fig. 4. Granular defect recall across VisA Cashew defect morphologies (N=100 defective specimens), demonstrating the severe escape rate on hairline scratches and same-color indentations under conservative factory thresholds. Note that 10 specimens exhibit co-occurring overlapping flaw morphologies.", caption_style))

    # Table 3: Morphology Breakdown Table
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
    t3 = Table(t3_data, colWidths=[170, 60, 60, 60, 120])
    t3.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.0),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('FONTNAME', (0,9), (-1,9), 'Times-Bold'),
        ('FONTNAME', (0,19), (-1,19), 'Times-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAECEF")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#F4F5F7")),
        ('BACKGROUND', (0,10), (-1,10), colors.HexColor("#F4F5F7")),
        ('BACKGROUND', (0,9), (-1,9), colors.HexColor("#F0F2F5")),
        ('BACKGROUND', (0,19), (-1,19), colors.HexColor("#F0F2F5")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0A2540")),
        ('LINEABOVE', (0,-1), (-1,-1), 0.8, colors.HexColor("#0A2540")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0A2540")),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t3)
    story.append(Paragraph("Table 3. Granular Detection Performance Across VisA Cashew Defect Morphologies (N=100 Defective Specimens).", caption_style))

    # SECTION 5.4: CPU Profiling
    story.append(Paragraph("5.4 Computational Execution Profiling on CPU", h2_style))
    story.append(Paragraph(
        "Computational profiling on an Intel Core i5-1335U CPU workstation demonstrated that target-domain registration of 350 images required 392.25 seconds (~6.5 minutes), "
        "producing a compact 40.2 MB memory index. Per-image inference latency on CPU was 392.5 ms median (p95: 438.1 ms) for standalone PatchCore, and 881.7 ms median "
        "(p95: 1455.7 ms) for end-to-end hybrid API calls. Table 4 and Fig. 5 summarize these measurements.",
        body_style
    ))

    # Figure 5: Latency Profiling
    fig5_path = os.path.join(FIG_DIR, "fig5_cpu_latency.png")
    if os.path.exists(fig5_path):
        story.append(Image(fig5_path, width=475, height=220))
        story.append(Paragraph("Fig. 5. Computational execution latency profiling across individual pipeline stages on a 13th Gen Intel Core i5-1335U CPU workstation, showing compatibility with discrete line takt times (>= 1.5 s).", caption_style))

    # Table 4: CPU Latency Table
    t4_data = [
        ["Pipeline Stage", "Hardware / Implementation", "Mean (ms)", "Median (ms)", "p95 (ms)"],
        ["Feature Extraction", "ResNet-18 (layer2+layer3, D=384)", "166.8", "164.2", "181.4"],
        ["FAISS Flat L2 Search", "IndexFlatL2 (M=27,440 tokens)", "173.2", "172.5", "196.2"],
        ["Gaussian Smoothing & Heatmap", "Gaussian blur (sigma=4.0) + bilinear upsample", "55.4", "55.8", "60.5"],
        ["PatchCore Forward Pass Total", "Full CPU inference (224x224 input)", "395.4", "392.5", "438.1"],
        ["EfficientNet-B0 v3 Forward Pass", "Supervised classification (256x256 input)", "173.1", "170.1", "256.3"],
        ["Hybrid Decision API (End-to-End)", "Full HTTP roundtrip (EffNet + PatchCore + OR)", "914.2", "881.7", "1455.7"]
    ]
    t4 = Table(t4_data, colWidths=[130, 160, 60, 60, 60])
    t4.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Times-Roman'),
        ('FONTSIZE', (0,0), (-1,-1), 7.2),
        ('FONTNAME', (0,0), (-1,0), 'Times-Bold'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EAECEF")),
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#0A2540")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#0A2540")),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(t4)
    story.append(Paragraph("Table 4. Computational Execution Latency Profiling across Pipeline Stages (Intel Core i5-1335U CPU).", caption_style))

    # SECTION 6: DISCUSSION
    story.append(Paragraph("6. Discussion", h1_style))
    story.append(Paragraph(
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
        "fusion is universally superior across all possible joint optimization architectures.",
        body_style
    ))

    # SECTION 7: LIMITATIONS AND FUTURE WORK
    story.append(Paragraph("7. Limitations and Future Work", h1_style))
    story.append(Paragraph(
        "We explicitly acknowledge several fundamental boundaries:\n"
        "1. Benchmark Latency vs. Live Industrial Deployment: Benchmark latency on static test images does not establish live production line readiness, which entails "
        "vibrations, optic contamination, triggering jitter, and 24/7 daemon stability.\n"
        "2. Asymmetric Scope of Independent Validation: Independent validation on VisA Cashew evaluated PatchCore exclusively; the supervised EfficientNet branch was "
        "not evaluated cross-domain due to class specificity.\n"
        "3. Single External Category Scope: Validation on VisA Cashew demonstrates adaptation to an organic substrate, but multi-category validation remains necessary.\n"
        "4. The Single-Threshold Dilemma: Operating at conservative false-alarm thresholds suppresses sensitivity to subtle surface flaws. Addressing this trade-off "
        "remains an open research challenge; multi-resolution feature pyramids or photometric stereo represent promising avenues for future research.\n"
        "5. Synthetic Noise vs. Physical Perturbations: Robustness evaluations relied on algorithmic perturbations rather than physical plant disturbances.\n"
        "6. Absence of Live Factory Conveyor Trials: No closed-loop PLC sorting trial was conducted.",
        body_style
    ))

    # SECTION 8: CONCLUSION
    story.append(Paragraph("8. Conclusion", h1_style))
    story.append(Paragraph(
        "In this paper, we presented an empirical evaluation of hybrid defect detection and nominal-only category adaptation under laboratory test constraints. "
        "On MVTec AD, hybrid OR-logic fusion reduced defect escapes by 48.6% (+54 defects caught) at the expense of 11 additional false alarms. On VisA Cashew, "
        "nominal adaptation achieved 0.9237 image AUROC and 0.9930 pixel AUROC on CPU, yet exposed a 93.8% escape rate on hairline scratches under conservative "
        "false-alarm boundaries. These findings demonstrate that while nominal adaptation provides baseline containment for discrete manufacturing, automated quality "
        "control requires further architectural investigation to resolve the fundamental operational tension between false-alarm suppression and micro-defect escapes.",
        body_style
    ))

    # DECLARATIONS
    story.append(Paragraph("Declarations", h1_style))
    story.append(Paragraph("<b>Abbreviations:</b> AD: Anomaly Detection; AUPRC: Area Under the Precision-Recall Curve; AUROC: Area Under the Receiver Operating Characteristic; CNN: Convolutional Neural Network; CPND: Context-Preserving Normalization Dropout; FAISS: Facebook AI Similarity Search; FNR: False Negative Rate; FPR: False Positive Rate; MACBA: Multi-Axis Cross-Branch Attention; MVTec AD: MVTec Anomaly Detection Dataset; PLC: Programmable Logic Controller; TNR: True Negative Rate (Specificity); TPR: True Positive Rate (Sensitivity / Recall); VisA: Visual Anomaly Dataset.", body_style))
    story.append(Paragraph("<b>Acknowledgements:</b> The author thanks the computer vision research community and the creators of the MVTec Anomaly Detection and Visual Anomaly (VisA) datasets for releasing benchmark imagery to the public research community.", body_style))
    story.append(Paragraph("<b>Authors' Contributions:</b> S.C. conceived the research design, implemented the hybrid inspection pipeline, executed the experimental evaluations and latency profiling, performed the forensic failure analysis, and wrote the manuscript.", body_style))
    story.append(Paragraph("<b>Funding:</b> This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. It was entirely self-supported by the author.", body_style))
    story.append(Paragraph("<b>Availability of Data and Materials:</b> The datasets evaluated in this study are publicly available: MVTec AD (https://www.mvtec.com/company/research/datasets/mvtec-ad) and VisA (https://github.com/amazon-science/spot-diff). Supporting evaluation manifests are archived in the study repository.", body_style))
    story.append(Paragraph("<b>Ethics Approval and Consent to Participate:</b> Not applicable. No human participants or animal subjects were involved.", body_style))
    story.append(Paragraph("<b>Consent for Publication:</b> Not applicable. No individual personal data is included.", body_style))
    story.append(Paragraph("<b>Competing Interests:</b> The author declares no competing financial or non-financial interests.", body_style))
    story.append(Paragraph("<b>Generative AI and AI-Assisted Technologies:</b> During the preparation of this manuscript, the author utilized large language model assistance (Google Gemini / Claude) for comprehensive manuscript drafting, text synthesis from experimental evaluation logs, section restructuring, literature review synthesis, grammar and style refinement, mathematical notation consistency checking, and formatting. All primary experimental protocols, algorithm code implementations, model registrations, baseline evaluations, numerical data collections, confusion matrices, and empirical failure analyses were conceived, executed, verified, and audited by the author. The author reviewed and edited all generated manuscript drafts, verifies the accuracy of all claims, and takes full intellectual and ethical responsibility for the contents of this publication.", body_style))

    # REFERENCES
    story.append(Paragraph("References", h1_style))
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
    for r in refs:
        story.append(Paragraph(r, ref_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled JEAS publication PDF: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
