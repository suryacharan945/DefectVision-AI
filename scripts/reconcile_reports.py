import os
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, precision_recall_fscore_support

def main():
    preds_path = 'release/final_validation/mvtec_all_predictions.csv'
    preds = pd.read_csv(preds_path)

    cat_metrics = []
    for cat in sorted(preds['category'].unique()):
        cdf = preds[preds['category'] == cat]
        y_true = cdf['is_defect'].values
        y_scores = cdf['anomaly_score'].values
        y_pred = cdf['predicted_label'].values

        auroc = roc_auc_score(y_true, y_scores)
        auprc = average_precision_score(y_true, y_scores)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0
        auto_acc = cdf['auto_category_correct'].mean()
        lat_mean = cdf['latency_ms'].mean()
        lat_p50 = cdf['latency_ms'].median()
        lat_p95 = cdf['latency_ms'].quantile(0.95)

        cat_metrics.append({
            'category': cat,
            'category_type': cdf['category_type'].iloc[0] if 'category_type' in cdf.columns else 'unknown',
            'nom': tn+fp,
            'def': tp+fn,
            'tp': tp,
            'fp': fp,
            'tn': tn,
            'fn': fn,
            'auroc': auroc,
            'auprc': auprc,
            'recall': rec,
            'specificity': spec,
            'precision': prec,
            'f1': f1,
            'auto_acc': auto_acc,
            'lat_mean': lat_mean,
            'lat_p50': lat_p50,
            'lat_p95': lat_p95
        })

    mdf = pd.DataFrame(cat_metrics)
    print("--- RECOMPUTED PER-CATEGORY METRICS ---")
    for _, r in mdf.iterrows():
        print(f"{r['category']:12s} | Nom/Def: {r['nom']:2d}/{r['def']:3d} | AUROC: {r['auroc']*100:6.2f}% | AUPRC: {r['auprc']*100:6.2f}% | Rec: {r['recall']*100:6.2f}% | Spec: {r['specificity']*100:6.2f}% | Prec: {r['precision']*100:6.2f}% | F1: {r['f1']*100:6.2f}% | AutoAcc: {r['auto_acc']*100:5.2f}% | Lat: {r['lat_mean']:6.1f}ms")

    print("\n--- RECOMPUTED MACRO METRICS (UNWEIGHTED MEAN ACROSS 15 CATEGORIES) ---")
    print(f"Macro AUROC:       {mdf['auroc'].mean()*100:6.2f}%")
    print(f"Macro AUPRC:       {mdf['auprc'].mean()*100:6.2f}%")
    print(f"Macro Recall:      {mdf['recall'].mean()*100:6.2f}%")
    print(f"Macro Specificity: {mdf['specificity'].mean()*100:6.2f}%")
    print(f"Macro Precision:   {mdf['precision'].mean()*100:6.2f}%")
    print(f"Macro F1:          {mdf['f1'].mean()*100:6.2f}% (unweighted mean of category F1 scores)")
    print(f"Macro Auto Acc:    {mdf['auto_acc'].mean()*100:6.2f}%")
    print(f"Mean E2E Latency:  {mdf['lat_mean'].mean():6.1f} ms")

    # Global Aggregate (Micro)
    y_true_all = preds['is_defect'].values
    y_pred_all = preds['predicted_label'].values
    tot_tp = int(((y_true_all == 1) & (y_pred_all == 1)).sum())
    tot_fp = int(((y_true_all == 0) & (y_pred_all == 1)).sum())
    tot_tn = int(((y_true_all == 0) & (y_pred_all == 0)).sum())
    tot_fn = int(((y_true_all == 1) & (y_pred_all == 0)).sum())
    tot_n = tot_tp + tot_fp + tot_tn + tot_fn

    micro_rec = tot_tp / (tot_tp + tot_fn)
    micro_spec = tot_tn / (tot_tn + tot_fp)
    micro_prec = tot_tp / (tot_tp + tot_fp)
    micro_f1 = 2 * micro_prec * micro_rec / (micro_prec + micro_rec)
    acc = (tot_tp + tot_tn) / tot_n
    fpr = tot_fp / (tot_fp + tot_tn)
    micro_auto_acc = preds['auto_category_correct'].mean()

    print("\n--- RECOMPUTED MICRO METRICS (AGGREGATE CONFUSION MATRIX, N=1725) ---")
    print(f"Total: {tot_n} | TP: {tot_tp}, FP: {tot_fp}, TN: {tot_tn}, FN: {tot_fn}")
    print(f"Micro Recall:      {micro_rec*100:6.2f}% ({tot_tp}/{tot_tp+tot_fn})")
    print(f"Micro Specificity: {micro_spec*100:6.2f}% ({tot_tn}/{tot_tn+tot_fp})")
    print(f"Micro Precision:   {micro_prec*100:6.2f}% ({tot_tp}/{tot_tp+tot_fp})")
    print(f"Micro F1:          {micro_f1*100:6.2f}%")
    print(f"Overall Accuracy:  {acc*100:6.2f}% ({tot_tp+tot_tn}/{tot_n})")
    print(f"False Alarm Rate:  {fpr*100:6.2f}% ({tot_fp}/{tot_fp+tot_tn})")
    print(f"Micro Auto Acc:    {micro_auto_acc*100:6.2f}%")

if __name__ == '__main__':
    main()
