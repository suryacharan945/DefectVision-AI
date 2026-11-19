import os
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = r"C:\Users\surya\Downloads\Mini Project\release\JEAS_final_submission\figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set font styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'Times']
plt.rcParams['font.size'] = 8.5
plt.rcParams['axes.linewidth'] = 0.8

def generate_fig4_reconciled():
    # 9 Mutually Exclusive Cohorts covering all 100 defective specimens
    categories = [
        "middle breakage (single, n=6)",
        "stuck together (single, n=6)",
        "different colour spot (single, n=9)",
        "small holes (single, n=20)",
        "corner/edge breakage (single, n=14)",
        "burnt (single, n=10)",
        "compound multi-defect (n=10)*",
        "small scratches (single, n=15)",
        "same colour spot (single, n=10)"
    ]
    recalls = [100.0, 100.0, 88.9, 85.0, 78.6, 40.0, 40.0, 6.7, 0.0]
    escapes = [0, 0, 1, 3, 3, 6, 6, 14, 10]
    totals  = [6, 6, 9, 20, 14, 10, 10, 15, 10]

    colors = ['#2D6A4F' if r >= 75 else '#E76F51' if r >= 40 else '#D00000' for r in recalls]

    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    y_pos = np.arange(len(categories))

    bars = ax.barh(y_pos, recalls, color=colors, height=0.62, edgecolor='#333333', lw=0.8)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=8)
    ax.invert_yaxis()  # Top-down order
    ax.set_xlabel('Empirical Defect Recall (%) at Locked Threshold (tau_p99.5 = 1.7452)', weight='bold', fontsize=8.5)
    ax.set_xlim([0, 120])

    for i, bar in enumerate(bars):
        w = bar.get_width()
        esc = escapes[i]
        tot = totals[i]
        txt = f"{w:.1f}% ({tot-esc}/{tot} caught)"
        if esc > 0:
            txt += f" | {esc} Escapes"
        ax.text(w + 1.5, bar.get_y() + bar.get_height()/2, txt, va='center', fontsize=7.5, weight='bold')

    # Draw vertical reference lines
    ax.axvline(80.0, color='#6C757D', linestyle=':', lw=1.2, label='Target 80% Recall Benchmark')
    ax.axvline(57.0, color='#0077B6', linestyle='--', lw=1.2, label='Aggregate Defect Recall (57.0%)')
    ax.legend(loc='lower right', frameon=True, fontsize=7.5)

    plt.title("Fig. 4. Reconciled Defect Recall Across All VisA Cashew Defective Specimens (N=100)\n*10 specimens exhibit co-occurring overlapping flaw morphologies (sum = 100 specimens, 57 TP, 43 FN)", weight='bold', pad=8, fontsize=8.5)
    plt.tight_layout()

    pdf_path = os.path.join(OUTPUT_DIR, "fig4_defect_morphology.pdf")
    png_path = os.path.join(OUTPUT_DIR, "fig4_defect_morphology.png")
    plt.savefig(pdf_path, dpi=300)
    plt.savefig(png_path, dpi=300)
    plt.close()
    print(f"Generated reconciled Fig 4: {pdf_path} and {png_path}")

if __name__ == "__main__":
    generate_fig4_reconciled()
