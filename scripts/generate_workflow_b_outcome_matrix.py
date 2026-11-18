import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, "release", "final_validation")
CSV_PATH = os.path.join(OUT_DIR, "WORKFLOW_B_STRATIFIED_RESULTS.csv")

def plot_outcome_matrix():
    df = pd.read_csv(CSV_PATH)

    # Multi-state Outcome Mapping:
    # Columns: NORMAL, DEFECTIVE, REVIEW REQUIRED, UNSUPPORTED
    # Rows: Ground Truth Normal (is_defect=0), Ground Truth Defective (is_defect=1)

    outcomes = ["NORMAL", "DEFECTIVE", "REVIEW REQUIRED", "UNSUPPORTED"]

    matrix = np.zeros((2, 4), dtype=int)
    for _, r in df.iterrows():
        row_idx = int(r["is_defect"])
        verdict = str(r["wf_b_verdict"]).strip()
        status = str(r.get("wf_b_status", "")).strip()

        if verdict == "UNSUPPORTED" or status in ["REJECTED_OOD", "LOW_CONFIDENCE", "UNSUPPORTED_OR_UNCERTAIN"]:
            col_idx = 3
        elif verdict == "REVIEW REQUIRED" or r.get("is_review_required") == 1:
            col_idx = 2
        elif verdict == "DEFECTIVE":
            col_idx = 1
        elif verdict == "NORMAL":
            col_idx = 0
        else:
            col_idx = 3
        matrix[row_idx, col_idx] += 1

    fig, ax = plt.subplots(figsize=(9, 5), dpi=200)

    # Custom color display
    cax = ax.matshow(matrix, cmap="Blues", alpha=0.85)

    # Colorbar
    fig.colorbar(cax, fraction=0.03, pad=0.04)

    # Annotations with percentages and operational descriptions
    row_totals = [45, 45]
    desc = [
        ["Cleared Normal\n(Optimal Safe)", "False Defect Alarm\n(Definite False Pos)", "Nominal Review Flag\n(Audit Burden)", "Unsupported OOD\n(N/A)"],
        ["Defect Escape\n(CRITICAL MISS)", "Direct Defect Capture\n(True Positive)", "Boundary Review Flag\n(Fail-Safe Triage)", "OOD Rejection\n(Deferred to Operator)"]
    ]

    for i in range(2):
        for j in range(4):
            val = matrix[i, j]
            pct = (val / row_totals[i]) * 100
            txt = f"{val}\n({pct:.1f}%)\n{desc[i][j]}"
            text_color = "white" if val > 20 else "black"
            ax.text(j, i, txt, ha="center", va="center", color=text_color, fontsize=9, fontweight="bold")

    ax.set_xticks(range(4))
    ax.set_yticks(range(2))
    ax.set_xticklabels(outcomes, fontsize=10, fontweight="bold")
    ax.set_yticklabels(["Normal Specimens\n(N=45)", "Defective Specimens\n(N=45)"], fontsize=10, fontweight="bold")

    ax.set_xlabel("Workflow B Autonomous Decision Outcome", fontsize=11, fontweight="bold", labelpad=12)
    ax.set_ylabel("Ground-Truth Condition", fontsize=11, fontweight="bold", labelpad=12)

    plt.title("DefectVision AI â€” Workflow B Multi-State Outcome & Triage Matrix (N=90)\n"
              "Disclosing Direct Classifications, Fail-Safe Review Flags, and OOD Fallback",
              fontsize=12, fontweight="bold", pad=20)

    plt.tight_layout()
    out_png = os.path.join(OUT_DIR, "workflow_b_90specimen_outcome_matrix.png")
    plt.savefig(out_png)
    plt.close()
    print(f"Workflow B Multi-State Outcome Matrix Plot saved to: {out_png}")

if __name__ == "__main__":
    plot_outcome_matrix()
