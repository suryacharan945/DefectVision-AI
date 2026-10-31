import os
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

class BenchmarkEvaluator:
    """
    Standardized benchmark evaluator supporting category-level metrics,
    per-image prediction exports, and fair evaluation splits.
    """
    def __init__(self, predictions_csv_path, thresholds_csv_path=None):
        if not os.path.exists(predictions_csv_path):
            raise FileNotFoundError(f"Predictions file not found: {predictions_csv_path}")
        self.df = pd.read_csv(predictions_csv_path)
        self.thresholds = None
        if thresholds_csv_path and os.path.exists(thresholds_csv_path):
            self.thresholds = pd.read_csv(thresholds_csv_path).set_index("category")["baseline_p99"].to_dict()

    def evaluate_category_metrics(self, score_col="anomaly_score", label_col="true_label"):
        """
        Computes AUROC, Balanced Accuracy, Accuracy, Precision, Recall, F1 per category
        and macro-average across all categories.
        """
        y_true_binary = (self.df[label_col] == "defective").astype(int)
        
        categories = sorted(self.df["category"].unique())
        results = []
        
        for cat in categories:
            cat_df = self.df[self.df["category"] == cat]
            y_c = (cat_df[label_col] == "defective").astype(int)
            s_c = cat_df[score_col].values
            
            # AUROC
            try:
                auroc = roc_auc_score(y_c, s_c) if len(np.unique(y_c)) > 1 else 1.0
            except Exception:
                auroc = float("nan")
                
            # Decision threshold
            if self.thresholds and cat in self.thresholds:
                th = self.thresholds[cat]
            else:
                th = 0.5
                
            y_pred_c = (s_c >= th).astype(int)
            acc = accuracy_score(y_c, y_pred_c)
            prec = precision_score(y_c, y_pred_c, zero_division=0)
            rec = recall_score(y_c, y_pred_c, zero_division=0)
            f1 = f1_score(y_c, y_pred_c, zero_division=0)
            
            # Specificity & Balanced Acc
            tn, fp, fn, tp = confusion_matrix(y_c, y_pred_c, labels=[0, 1]).ravel()
            spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
            bal_acc = (rec + spec) / 2.0
            
            results.append({
                "category": cat,
                "n_samples": len(cat_df),
                "n_defect": int(y_c.sum()),
                "n_normal": int((~y_c.astype(bool)).sum()),
                "threshold": th,
                "auroc": round(auroc, 4),
                "accuracy": round(acc, 4),
                "balanced_accuracy": round(bal_acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "specificity": round(spec, 4),
                "f1": round(f1, 4),
                "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn)
            })
            
        res_df = pd.DataFrame(results)
        macro_summary = {
            "category": "MACRO_AVERAGE",
            "n_samples": len(self.df),
            "n_defect": int(y_true_binary.sum()),
            "n_normal": int((~y_true_binary.astype(bool)).sum()),
            "threshold": float("nan"),
            "auroc": round(res_df["auroc"].mean(), 4),
            "accuracy": round(res_df["accuracy"].mean(), 4),
            "balanced_accuracy": round(res_df["balanced_accuracy"].mean(), 4),
            "precision": round(res_df["precision"].mean(), 4),
            "recall": round(res_df["recall"].mean(), 4),
            "specificity": round(res_df["specificity"].mean(), 4),
            "f1": round(res_df["f1"].mean(), 4),
            "tp": int(res_df["tp"].sum()),
            "fp": int(res_df["fp"].sum()),
            "fn": int(res_df["fn"].sum()),
            "tn": int(res_df["tn"].sum())
        }
        res_df = pd.concat([res_df, pd.DataFrame([macro_summary])], ignore_index=True)
        return res_df

    def export_per_image_predictions(self, output_path):
        """
        Exports formatted per-image predictions for external auditing.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"Exported {len(self.df)} image predictions to {output_path}")
