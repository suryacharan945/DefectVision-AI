import re

with open('scripts/generate_jeas_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Header
text = re.sub(
    r'header_text = "Journal of Engineering and Applied Science \(JEAS\) [^"]+"',
    'header_text = "Author-Compiled Review Copy (Prepared for Submission to JEAS)"',
    text
)

# 2. Title
old_title = 'Hybrid Visual Defect Inspection with Nominal-Only Anomaly Adaptation: Detection Trade-offs, Failure Modes, and CPU Runtime Evaluation'
new_title = 'Hybrid Visual Defect Inspection and Nominal-Only Adaptation: An Empirical Study of Detection Trade-Offs and Operational Constraints'
text = text.replace(old_title, new_title)

# 3. Add top disclaimer banner before Abstract
if 'Author Review Copy' not in text:
    target = 'story.append(Paragraph("Abstract", abs_title_style))'
    replacement = '''disclaimer_style = ParagraphStyle(
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
    story.append(Paragraph("Abstract", abs_title_style))'''
    text = text.replace(target, replacement, 1)

# 4. Abstract text replacement
old_abs_part = 'granular morphology reconciliation revealed a 43.0% defect escape rate concentrated heavily in fine surface flaws: gross structural breaks achieved 100% recall, whereas hairline scratches suffered a 93.8% escape rate (1/16 recall).'
new_abs_part = 'Operating at the locked 99.5th-percentile calibration threshold enforced high specificity (98.0%, 2 false alarms), but granular morphology reconciliation across all 100 defective specimens (90 single-defect, 10 compound) revealed an overall 43.0% defect escape rate: gross structural breaks achieved 100% recall (8/8 middle breakage, 6/6 stuck together), localized voids (small holes) achieved 81.8% marginal recall (18/22 caught; 17/20 on single-defect specimens), whereas hairline scratches suffered a 93.8% marginal escape rate (1/16 caught; 1/15 on single-defect specimens) and same-color indentations suffered an 85.7% marginal escape rate (2/14 caught; 0/10 on single-defect specimens).'
if old_abs_part in text:
    text = text.replace(old_abs_part, new_abs_part)

# 5. Economics & Forensics & Negative Findings replacement
old_disc = (
    '        "Quality Control Economics: The operational viability of the hybrid decision policy is governed by the relative economic cost ratio "\n'
    '        "R_cost = C_escape / C_scrap. When R_cost > 15 (e.g. automotive safety parts, aerospace fasteners), capturing 54 additional defects easily offsets "\n'
    '        "the cost of 11 additional false alarms. When R_cost <= 2 (e.g. low-margin bulk agricultural produce), false alarms dominate unit economics, "\n'
    '        "requiring operators to tune thresholds toward higher specificity.\\n\\n"\n'
    '        "Forensic Analysis of Escapes: In VisA Cashew, small scratches measure only 2 to 4 pixels in width. When processed through ResNet-18 layer2 (stride 8) "\n'
    '        "and layer3 (stride 16) with 3x3 local pooling, high-frequency spatial gradients are heavily diluted across the broader receptive field. Furthermore, natural "\n'
    '        "cashew kernels possess organic furrows whose embeddings overlap with subtle scratches. Similarly, same-colour spots represent shallow monochromatic depressions "\n'
    '        "that share the exact hue and reflectance of healthy cashew kernel meat, producing negligible nearest-neighbor displacement.\\n\\n"\n'
    '        "Takt-Time Viability: Discrete batch inspection stations (cycle times >= 1.5 s) are computationally viable on CPU without GPU investment. However, high-speed "\n'
    '        "continuous production (< 100 ms) is unviable on CPU and requires tensor quantization (INT8) or edge GPU accelerators.\\n\\n"\n'
    '        "Documentation of Negative Findings: We transparently document two negative results: (1) Context-Preserving Normalization Dropout (CPND) yielded statistically "\n'
    '        "indistinguishable generalization relative to standard dropout (p = 0.42); and (2) Multi-Axis Cross-Branch Attention (MACBA) suffered gradient divergence during "\n'
    '        "joint branch backpropagation, demonstrating that decoupled late-stage decision fusion (OR-logic) is structurally superior to early deep feature coupling in our evaluated pipeline."'
)

new_disc = (
    '        "Quality Control Economics: The operational viability of the hybrid decision policy is governed by the relative economic cost balance between "\n'
    '        "defect escapes and false alarms. In manufacturing environments where defect escapes carry severe consequences compared to the cost of reinspecting "\n'
    '        "false alarms (such as automotive safety components, aerospace fasteners, or pharmaceutical packaging), the hybrid policy is operationally advantageous: "\n'
    '        "capturing 54 additional defects substantially offsets the overhead of 11 additional false alarms. Conversely, in high-volume, low-margin production "\n'
    '        "where false rejections directly degrade yield profitability, factory operators must prioritize specificity and conservative thresholding to maintain viable economics.\\n\\n"\n'
    '        "Forensic Analysis of Escapes: In VisA Cashew, fine hairline surface scratches occupy a minor spatial fraction of the effective convolutional receptive field. "\n'
    '        "When processed through ResNet-18 layer2 (stride 8) and layer3 (stride 16) with 3x3 local average pooling, high-frequency spatial gradients are smoothed into "\n'
    '        "surrounding nominal features. Furthermore, natural cashew kernels possess organic furrows and striations whose embeddings exhibit natural variance overlapping "\n'
    '        "with subtle scratches. Similarly, same-colour spots represent shallow monochromatic depressions that share the exact hue and reflectance of healthy cashew kernel "\n'
    '        "meat, producing negligible nearest-neighbor displacement under diffuse illumination. We emphasize that our benchmark evaluations do not isolate optical resolution "\n'
    '        "as the sole causal mechanism; rather, feature spatial strides, pooling operations, illumination geometry, and representation choices act together as contributing factors.\\n\\n"\n'
    '        "Takt-Time Viability: Discrete batch inspection stations (cycle times >= 1.5 s) are computationally viable on CPU without GPU investment. However, high-speed "\n'
    '        "continuous production (< 100 ms) is unviable on CPU and requires tensor quantization (INT8) or edge GPU accelerators.\\n\\n"\n'
    '        "Documentation of Negative Findings: We transparently document two negative results: (1) Context-Preserving Normalization Dropout (CPND) yielded statistically "\n'
    '        "indistinguishable generalization relative to standard dropout (p = 0.42); and (2) Multi-Axis Cross-Branch Attention (MACBA) suffered gradient divergence during "\n'
    '        "joint branch backpropagation. While this negative finding highlights the practical implementation stability of decoupled late-stage decision fusion (OR-logic) "\n'
    '        "over early cross-branch coupling in our evaluated pipeline, it reflects the behavior of our specific experimental configuration and does not imply that decision-level "\n'
    '        "fusion is universally superior across all possible joint optimization architectures."'
)
if old_disc in text:
    text = text.replace(old_disc, new_disc)

# 6. AI Disclosure replacement
old_ai = 'During manuscript preparation, the author utilized AI-assisted language editing tools to audit LaTeX formatting syntax, verify bibliographic citation metadata, and improve English prose readability. The author reviewed and approved all technical content and takes full responsibility for the published work.'
new_ai = 'During the preparation of this manuscript, the author utilized large language model assistance (Google Gemini / Claude) for comprehensive manuscript drafting, text synthesis from experimental evaluation logs, section restructuring, literature review synthesis, grammar and style refinement, mathematical notation consistency checking, and formatting. All primary experimental protocols, algorithm code implementations, model registrations, baseline evaluations, numerical data collections, confusion matrices, and empirical failure analyses were conceived, executed, verified, and audited by the author. The author reviewed and edited all generated manuscript drafts, verifies the accuracy of all claims, and takes full intellectual and ethical responsibility for the contents of this publication.'
if old_ai in text:
    text = text.replace(old_ai, new_ai)

with open('scripts/generate_jeas_pdf.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Successfully patched scripts/generate_jeas_pdf.py!')
