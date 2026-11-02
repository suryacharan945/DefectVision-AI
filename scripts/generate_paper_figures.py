import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sklearn.metrics import roc_curve, precision_recall_curve, auc

# Style configuration for IEEE publication
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': '--'
})

OUTPUT_DIR = r"C:\Users\surya\Downloads\Mini Project\release\phase52_submission_package\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Figure 1: System Architecture Diagram
# -----------------------------------------------------------------------------
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.axis('off')

    # Draw Boxes
    def draw_box(x, y, w, h, title, subtitle, color='#EBF3FB', edgecolor='#2A6F97'):
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", 
                                     facecolor=color, edgecolor=edgecolor, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', weight='bold', fontsize=8.5, color='#012A4A')
        ax.text(x + w/2, y + h*0.30, subtitle, ha='center', va='center', fontsize=7.2, color='#2C3E50')

    # Input Image
    draw_box(0.05, 0.40, 0.16, 0.22, "Input Specimen\nImage (x)", "256x256 / 224x224 RGB", color='#F8F9FA', edgecolor='#495057')

    # Branch 1: Supervised EfficientNet-B0 v3
    draw_box(0.28, 0.65, 0.28, 0.24, "Supervised Classifier\n(EfficientNet-B0 v3)", "ImageNet Pretrained + Fine-Tuned\np_defect in [0, 1]", color='#E8F4F8', edgecolor='#0077B6')
    draw_box(0.62, 0.65, 0.16, 0.24, "Supervised Gate", "d_clf = (p >= 0.50)\nBinary Decision", color='#E8F4F8', edgecolor='#0077B6')

    # Branch 2: PatchCore Memory Bank
    draw_box(0.28, 0.15, 0.28, 0.28, "Unsupervised Memory Bank\n(PatchCore + ResNet-18)", "Layer2+3 Patch Embeddings (D=384)\nMinimax Coreset (M=27,440)", color='#E9F5ED', edgecolor='#2D6A4F')
    draw_box(0.62, 0.15, 0.16, 0.28, "PatchCore Gate", "d_ano = (S >= tau_p99)\ntau_p99 = 1.7452", color='#E9F5ED', edgecolor='#2D6A4F')

    # Decision Fusion & Output
    draw_box(0.83, 0.38, 0.15, 0.28, "Dual-Branch Fusion\n(Logical OR)", "y = d_clf OR d_ano\nQuarantine / Pass", color='#FFF3CD', edgecolor='#B5838D')

    # Arrows
    def draw_arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", lw=1.2, color='#343A40', mutation_scale=12))

    draw_arrow(0.21, 0.55, 0.28, 0.77)
    draw_arrow(0.21, 0.47, 0.28, 0.29)
    draw_arrow(0.56, 0.77, 0.62, 0.77)
    draw_arrow(0.56, 0.29, 0.62, 0.29)
    draw_arrow(0.78, 0.77, 0.83, 0.58)
    draw_arrow(0.78, 0.29, 0.83, 0.46)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    plt.title("Fig. 1. Architecture of the DefectVision AI Dual-Branch Hybrid Inspection Pipeline", pad=12, weight='bold')
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_architecture.pdf"))
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_architecture.png"))
    plt.close()
    print("Generated Fig 1: Architecture diagram.")

# -----------------------------------------------------------------------------
# Figure 2: MVTec Confusion Matrix Comparison
# -----------------------------------------------------------------------------
def generate_fig2_confusion_matrices():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.2))

    # Confusion matrix data from FINAL_EVIDENCE_AUDIT.md
    cm_eff = np.array([[230, 1], [111, 514]])
    cm_hyb = np.array([[219, 12], [57, 568]])

    def plot_cm(ax, cm, title, subtitle):
        im = ax.imshow(cm, cmap='Blues', vmin=0, vmax=600)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(['Nominal (0)', 'Defect (1)'], weight='bold')
        ax.set_yticklabels(['Nominal (0)', 'Defect (1)'], weight='bold')
        ax.set_xlabel('Predicted Class', labelpad=4)
        ax.set_ylabel('True Class', labelpad=4)
        ax.set_title(title, weight='bold', pad=8)
        
        # Annotate numbers
        for i in range(2):
            for j in range(2):
                val = cm[i, j]
                color = 'white' if val > 300 else 'black'
                txt = f"{val}"
                if i == 0 and j == 1:
                    txt += "\n(False Alarm)"
                elif i == 1 and j == 0:
                    txt += "\n(Escape / FN)"
                ax.text(j, i, txt, ha='center', va='center', color=color, fontsize=8, weight='bold')
        ax.text(0.5, -0.28, subtitle, transform=ax.transAxes, ha='center', fontsize=7.5, style='italic')

    plot_cm(ax1, cm_eff, "Standalone EfficientNet-B0 v3", "Acc: 86.92% | Recall: 82.24%\nMissed: 111 | False Alarms: 1")
    plot_cm(ax2, cm_hyb, "Dual-Branch Hybrid System", "Acc: 91.94% | Recall: 90.88%\nMissed: 57 (-54) | False Alarms: 12 (+11)")

    fig.suptitle("Fig. 2. Confusion Matrix Comparison on 856 MVTec AD Specimens (Category C Development-Exposed)", weight='bold', y=1.04)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_confusion_matrices.pdf"))
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_confusion_matrices.png"))
    plt.close()
    print("Generated Fig 2: Confusion matrices comparison.")

# -----------------------------------------------------------------------------
# Figure 3: VisA Cashew ROC and Precision-Recall Curves
# -----------------------------------------------------------------------------
def generate_fig3_roc_pr_curves():
    pred_file = r"C:\Users\surya\Downloads\Mini Project\release\phase49_independent_results\TEST_PREDICTIONS.csv"
    y_true = []
    scores = []
    with open(pred_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            y_true.append(int(r["ground_truth"]))
            scores.append(float(r["raw_anomaly_score"]))

    y_true = np.array(y_true)
    scores = np.array(scores)

    fpr, tpr, thresholds_roc = roc_curve(y_true, scores)
    prec, rec, thresholds_pr = precision_recall_curve(y_true, scores)
    roc_auc = auc(fpr, tpr)
    pr_auc = auc(rec, prec)

    # Operating point at tau_p99 = 1.745232
    tau = 1.745232
    preds = (scores >= tau).astype(int)
    op_fpr = np.mean(preds[y_true == 0]) # 0.02
    op_tpr = np.mean(preds[y_true == 1]) # 0.57
    op_prec = 57 / 59 # 0.9661
    op_rec = 0.57

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.8, 3.2))

    # ROC Curve
    ax1.plot(fpr, tpr, color='#0077B6', lw=1.8, label=f'PatchCore (AUROC = {roc_auc:.4f})')
    ax1.plot([0, 1], [0, 1], color='#6C757D', lw=1.0, linestyle=':')
    ax1.scatter([op_fpr], [op_tpr], color='#D00000', s=45, zorder=5, 
                label=f'$\\tau_{{p99}}={tau:.4f}$\n(FPR=2.0%, TPR=57.0%)')
    ax1.set_xlabel('False Positive Rate (1 - Specificity)')
    ax1.set_ylabel('True Positive Rate (Recall)')
    ax1.set_title('Receiver Operating Characteristic', weight='bold')
    ax1.legend(loc='lower right', frameon=True)
    ax1.set_xlim([-0.02, 1.02])
    ax1.set_ylim([-0.02, 1.02])

    # PR Curve
    ax2.plot(rec, prec, color='#2D6A4F', lw=1.8, label=f'PatchCore (AUPRC = {pr_auc:.4f})')
    ax2.scatter([op_rec], [op_prec], color='#D00000', s=45, zorder=5, 
                label=f'$\\tau_{{p99}}={tau:.4f}$\n(Prec=96.6%, Rec=57.0%)')
    ax2.set_xlabel('Recall (Sensitivity)')
    ax2.set_ylabel('Precision (PPV)')
    ax2.set_title('Precision-Recall Curve', weight='bold')
    ax2.legend(loc='lower left', frameon=True)
    ax2.set_xlim([-0.02, 1.02])
    ax2.set_ylim([0.45, 1.02])

    fig.suptitle("Fig. 3. Image-Level Discrimination on 200 Untouched VisA Cashew Test Specimens", weight='bold', y=1.04)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_roc_pr_curves.pdf"))
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_roc_pr_curves.png"))
    plt.close()
    print("Generated Fig 3: ROC and Precision-Recall curves.")

# -----------------------------------------------------------------------------
# Figure 4: VisA Cashew Defect Morphology Failure Breakdown
# -----------------------------------------------------------------------------
def generate_fig4_defect_morphology():
    # Primary categories from ERROR_ANALYSIS.md
    categories = [
        "middle breakage (n=6)",
        "stuck together (n=6)",
        "different colour spot (n=9)",
        "small holes (n=20)",
        "corner/edge breakage (n=14)",
        "burnt (n=10)",
        "small scratches (n=15)",
        "same colour spot (n=10)"
    ]
    recalls = [100.0, 100.0, 88.9, 85.0, 78.6, 40.0, 6.7, 0.0]
    escapes = [0, 0, 1, 3, 3, 6, 14, 10]
    totals  = [6, 6, 9, 20, 14, 10, 15, 10]

    colors = ['#2D6A4F' if r >= 75 else '#E76F51' if r >= 40 else '#D00000' for r in recalls]

    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    y_pos = np.arange(len(categories))

    bars = ax.barh(y_pos, recalls, color=colors, height=0.62, edgecolor='#333333', lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=8)
    ax.invert_yaxis()  # Top-down
    ax.set_xlabel('Empirical Defect Recall (%) at Locked Threshold (tau_p99 = 1.7452)', weight='bold')
    ax.set_xlim([0, 115])

    for i, bar in enumerate(bars):
        w = bar.get_width()
        esc = escapes[i]
        tot = totals[i]
        txt = f"{w:.1f}% ({tot-esc}/{tot} caught)"
        if esc > 0:
            txt += f" | {esc} Escapes"
        ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, txt, va='center', fontsize=7.5, weight='bold')

    # Draw vertical threshold reference line
    ax.axvline(80.0, color='#6C757D', linestyle=':', lw=1.2, label='Target 80% Recall Benchmark')
    ax.legend(loc='lower right', frameon=True)
    plt.title("Fig. 4. Granular Recall Across Primary VisA Cashew Defect Morphologies (N=100 Defective)", weight='bold', pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_defect_morphology.pdf"))
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_defect_morphology.png"))
    plt.close()
    print("Generated Fig 4: Defect morphology recall breakdown.")

# -----------------------------------------------------------------------------
# Figure 5: CPU Latency Profiling
# -----------------------------------------------------------------------------
def generate_fig5_cpu_latency():
    stages = [
        "Feature Extract\n(ResNet-18)",
        "FAISS L2 Search\n(M=27,440)",
        "Smoothing &\nHeatmap Map",
        "PatchCore Total\n(Forward Pass)",
        "EfficientNet-B0\n(Forward Pass)",
        "Hybrid API E2E\n(HTTP Roundtrip)"
    ]
    medians = [164.2, 172.5, 55.8, 392.5, 170.1, 881.7]
    p95s    = [181.4, 196.2, 60.5, 438.1, 256.3, 1455.7]

    x = np.arange(len(stages))
    width = 0.38

    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    bars1 = ax.bar(x - width/2, medians, width, label='Median Latency (p50)', color='#0077B6', edgecolor='#012A4A')
    bars2 = ax.bar(x + width/2, p95s, width, label='95th Percentile (p95)', color='#48CAE4', edgecolor='#012A4A')

    ax.set_ylabel('Execution Latency on CPU (ms)', weight='bold')
    ax.set_title('Fig. 5. Computational Execution Latency on Intel Core i7-10750H CPU', weight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=7.5)
    ax.set_ylim([0, 1650])
    ax.legend(loc='upper left', frameon=True)

    # Reference lines for manufacturing takt times
    ax.axhline(1500, color='#D00000', linestyle='--', lw=1.0, alpha=0.7)
    ax.text(4.2, 1520, 'Discrete Line Bound (1.5 s)', color='#D00000', fontsize=7.2, weight='bold')

    for bar in bars1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 25, f"{h:.0f}", ha='center', va='bottom', fontsize=6.8)
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 25, f"{h:.0f}", ha='center', va='bottom', fontsize=6.8)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_cpu_latency.pdf"))
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_cpu_latency.png"))
    plt.close()
    print("Generated Fig 5: CPU latency profiling.")

if __name__ == "__main__":
    generate_fig1_architecture()
    generate_fig2_confusion_matrices()
    generate_fig3_roc_pr_curves()
    generate_fig4_defect_morphology()
    generate_fig5_cpu_latency()
    print("\nAll 5 figures successfully generated in vector PDF and PNG formats.")
