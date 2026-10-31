import pandas as pd
import numpy as np

def analyze_model_log(path, name):
    df = pd.read_csv(path)
    print(f"\n================ {name} ================")
    print(f"Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    y_true = (df['true_label'].str.lower() == 'defective').astype(int)
    scores = df['anomaly_score']
    
    # Check if there is an official report for threshold
    rep = pd.read_csv("DefectVisionAI/reports/step8_model_comparison.csv")
    row = rep[rep['Model'].str.contains(name, case=False, na=False)]
    if not row.empty:
        print("Reported in step8_model_comparison.csv:")
        print(row.to_dict(orient='records')[0])
    
    # Let's find optimal threshold by F1 or match recall/precision
    best_f1 = 0
    best_th = None
    best_cm = None
    for th in np.percentile(scores, np.linspace(1, 99, 500)):
        y_pred = (scores >= th).astype(int)
        tp = ((y_true == 1) & (y_pred == 1)).sum()
        tn = ((y_true == 0) & (y_pred == 0)).sum()
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        if f1 > best_f1:
            best_f1 = f1
            best_th = th
            best_cm = (tp, tn, fp, fn, prec, rec, f1)
            
    print(f"Best F1 threshold={best_th:.4f}:")
    tp, tn, fp, fn, prec, rec, f1 = best_cm
    print(f"TP={tp}, TN={tn}, FP={fp}, FN={fn}, Total Errors={fp+fn}")
    print(f"Accuracy={(tp+tn)/len(df):.4f}, Prec={prec:.4f}, Rec={rec:.4f}, F1={f1:.4f}")

analyze_model_log("DefectVisionAI/logs/step7_patchcore_inference_log.csv", "PatchCore")
analyze_model_log("DefectVisionAI/logs/step6_padim_inference_log.csv", "PaDiM")
analyze_model_log("DefectVisionAI/logs/step5_ae_inference_log.csv", "Autoencoder")
