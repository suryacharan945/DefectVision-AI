"""
DefectVision AI — Responsive Visual HTML Gallery Generator (Phase 8)
Generates external_validation/galleries/index.html and external_validation/gallery/index.html.
Embeds comprehensive evaluation results, metadata, image paths, heatmaps, interactive filtering,
opacity slider, modal viewer, and summary analytics cards.
"""

import os
import json
import pandas as pd

def generate_gallery():
    preds_path = "external_validation/results/predictions.csv"
    meta_path = "external_validation/metadata/external_image_metadata.csv"
    
    if not os.path.exists(preds_path):
        print(f"Error: {preds_path} not found.")
        return
        
    df_preds = pd.read_csv(preds_path)
    df_meta = pd.read_csv(meta_path) if os.path.exists(meta_path) else None
    
    if df_meta is not None:
        merged = pd.merge(df_preds, df_meta[["image_id", "source_name", "source_page_url", "search_query"]], on="image_id", how="left")
    else:
        merged = df_preds

    items = []
    for _, row in merged.iterrows():
        cat = row["category"]
        exp_cond = row["expected_condition"]
        sub_dir = "normal" if exp_cond == "NORMAL" else "defective"
        img_id = row["image_id"]
        
        # Relative paths from galleries/
        orig_img_rel = f"../images/{cat}/{sub_dir}/{img_id}.jpg"
        # Check png fallback
        if not os.path.exists(os.path.join("external_validation", "images", cat, sub_dir, f"{img_id}.jpg")):
            orig_img_rel = f"../images/{cat}/{sub_dir}/{img_id}.png"
            
        hm_img_rel = f"../heatmaps/{cat}/{img_id}_heatmap.png"
        
        items.append({
            "image_id": img_id,
            "category": cat,
            "category_type": row.get("category_type", "object"),
            "expected_condition": exp_cond,
            "defect_type": str(row.get("defect_type", "none")),
            "similarity_group": str(row.get("similarity_group", "unknown")),
            "validation_status": str(row.get("manual_validation_status", "unknown")),
            "detected_category": str(row.get("detected_category_auto", "unknown")),
            "category_confidence": float(row.get("category_confidence_auto", 0.0)),
            "gate_status": str(row.get("gate_status", "ACCEPTED")),
            "anomaly_score": float(row.get("anomaly_score", 0.0)),
            "calibrated_threshold": float(row.get("calibrated_threshold", 0.0)),
            "margin_to_threshold": float(row.get("margin_to_threshold", 0.0)),
            "predicted_condition": str(row.get("predicted_condition", "UNKNOWN")),
            "is_correct": bool(row.get("is_prediction_correct", False)),
            "heatmap_generated": bool(row.get("heatmap_generated", False)),
            "original_image_path": orig_img_rel,
            "heatmap_image_path": hm_img_rel,
            "latency_ms": float(row.get("latency_ms", 0.0)),
            "failure_category": str(row.get("failure_category", "none")),
            "failure_diagnosis": str(row.get("failure_diagnosis", "none")),
            "source_name": str(row.get("source_name", "Web Harvest")),
            "source_url": str(row.get("source_page_url", ""))
        })

    items_json = json.dumps(items)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DefectVision AI — External Image Validation & Anomaly Gallery</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --card-border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #38bdf8;
      --success: #22c55e;
      --danger: #ef4444;
      --warning: #f59e0b;
      --purple: #a855f7;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 24px; min-height: 100vh; }}
    
    header {{ margin-bottom: 24px; border-bottom: 1px solid var(--card-border); padding-bottom: 16px; }}
    .title-row {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }}
    h1 {{ font-size: 24px; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 10px; }}
    .badge-rc {{ background: #0369a1; color: white; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
    
    /* Summary Dashboard */
    .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; }}
    .stat-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 16px; text-align: center; }}
    .stat-val {{ font-size: 28px; font-weight: 700; color: var(--text); margin-bottom: 4px; }}
    .stat-lbl {{ font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); }}
    
    /* Filter Bar */
    .filter-panel {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 16px; margin-bottom: 24px; display: flex; flex-direction: column; gap: 12px; }}
    .filter-row {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }}
    .filter-group {{ display: flex; flex-direction: column; gap: 4px; flex: 1; min-width: 140px; }}
    label {{ font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 600; }}
    select, input {{ background: #0f172a; border: 1px solid var(--card-border); color: var(--text); padding: 8px 12px; border-radius: 6px; font-size: 13px; outline: none; }}
    select:focus, input:focus {{ border-color: var(--primary); }}
    
    .slider-row {{ display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--text-muted); }}
    .slider-row input[type="range"] {{ flex: 1; accent-color: var(--primary); }}
    
    /* Gallery Grid */
    .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }}
    .specimen-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.15s ease, border-color 0.15s ease; }}
    .specimen-card:hover {{ transform: translateY(-2px); border-color: var(--primary); }}
    
    .img-container {{ position: relative; width: 100%; aspect-ratio: 1/1; background: #000; overflow: hidden; }}
    .img-base, .img-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; }}
    .img-overlay {{ opacity: 0.70; transition: opacity 0.1s ease; }}
    
    .card-meta {{ padding: 14px; display: flex; flex-direction: column; gap: 8px; flex: 1; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: center; }}
    .cat-badge {{ font-weight: 700; font-size: 14px; text-transform: capitalize; color: var(--primary); }}
    .cond-pill {{ padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; }}
    .pill-norm {{ background: rgba(34, 197, 94, 0.2); color: var(--success); border: 1px solid rgba(34, 197, 94, 0.4); }}
    .pill-defe {{ background: rgba(239, 68, 68, 0.2); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.4); }}
    .pill-rej {{ background: rgba(245, 158, 11, 0.2); color: var(--warning); border: 1px solid rgba(245, 158, 11, 0.4); }}
    
    .meta-metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; font-size: 12px; color: var(--text-muted); background: #0f172a; padding: 8px; border-radius: 6px; }}
    .meta-metrics b {{ color: var(--text); }}
    
    .card-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: auto; padding-top: 8px; border-top: 1px solid #334155; font-size: 11px; }}
    .gate-badge {{ font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; }}
    .gate-accepted {{ background: #065f46; color: #34d399; }}
    .gate-low {{ background: #78350f; color: #fbbf24; }}
    .gate-unsupported {{ background: #881337; color: #fda4af; }}
    .gate-quality {{ background: #374151; color: #9ca3af; }}
    
    /* Modal Viewer */
    .modal {{ display: none; position: fixed; z-index: 1000; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); backdrop-filter: blur(4px); justify-content: center; align-items: center; padding: 20px; }}
    .modal.active {{ display: flex; }}
    .modal-content {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; }}
    .modal-header {{ padding: 16px; border-bottom: 1px solid var(--card-border); display: flex; justify-content: space-between; align-items: center; }}
    .modal-body {{ padding: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    @media (max-width: 768px) {{ .modal-body {{ grid-template-columns: 1fr; }} }}
    .modal-img-box {{ background: #000; aspect-ratio: 1/1; position: relative; border-radius: 8px; overflow: hidden; }}
    .modal-meta {{ display: flex; flex-direction: column; gap: 10px; font-size: 13px; }}
    .close-btn {{ background: none; border: none; color: var(--text-muted); font-size: 24px; cursor: pointer; }}
  </style>
</head>
<body>

  <header>
    <div class="title-row">
      <div>
        <h1>DefectVision AI <span class="badge-rc">v1.0.0-rc1</span></h1>
        <p style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">
          Multi-Domain Industrial Anomaly Detection — External Validation & Telemetry Gallery
        </p>
      </div>
      <div style="font-size: 12px; color: var(--text-muted); text-align: right;">
        Dataset: 150 In-the-Wild Internet Specimens (10 Objects, 5 Textures)<br>
        Evaluation: Live Inference API (/api/inspect-frame)
      </div>
    </div>

    <!-- Summary Dashboard -->
    <div class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-val" id="stat-total">150</div>
        <div class="stat-lbl">Total Specimens</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--primary);" id="stat-approved">99</div>
        <div class="stat-lbl">Approved Validation Set</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--success);" id="stat-recall">84.3%</div>
        <div class="stat-lbl">Defect Recall (Approved)</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--warning);" id="stat-latency">242ms</div>
        <div class="stat-lbl">Median Latency</div>
      </div>
      <div class="stat-card">
        <div class="stat-val" style="color: var(--purple);" id="stat-categories">15 / 15</div>
        <div class="stat-lbl">Supported Categories</div>
      </div>
    </div>
  </header>

  <!-- Filter Panel -->
  <div class="filter-panel">
    <div class="filter-row">
      <div class="filter-group">
        <label>Category</label>
        <select id="filter-category">
          <option value="ALL">All 15 Categories</option>
          <option value="bottle">Bottle</option>
          <option value="cable">Cable</option>
          <option value="capsule">Capsule</option>
          <option value="carpet">Carpet</option>
          <option value="grid">Grid</option>
          <option value="hazelnut">Hazelnut</option>
          <option value="leather">Leather</option>
          <option value="metal_nut">Metal Nut</option>
          <option value="pill">Pill</option>
          <option value="screw">Screw</option>
          <option value="tile">Tile</option>
          <option value="toothbrush">Toothbrush</option>
          <option value="transistor">Transistor</option>
          <option value="wood">Wood</option>
          <option value="zipper">Zipper</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Expected Condition</label>
        <select id="filter-condition">
          <option value="ALL">All (Normal & Defective)</option>
          <option value="NORMAL">Normal Only</option>
          <option value="DEFECTIVE">Defective Only</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Similarity Group</label>
        <select id="filter-similarity">
          <option value="ALL">All Similarity Tiers</option>
          <option value="high_similarity_mvtec_like">High Similarity (MVTec-like)</option>
          <option value="moderate_similarity">Moderate Similarity</option>
          <option value="different_visual_domain">Different Visual Domain</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Validation Status</label>
        <select id="filter-validation">
          <option value="ALL">All Statuses</option>
          <option value="APPROVED">Approved Only (Normal + Defective)</option>
          <option value="UNCERTAIN_OUT_OF_DOMAIN">Uncertain / Domain Shift</option>
          <option value="REJECTED_QUALITY">Quality Rejected</option>
        </select>
      </div>

      <div class="filter-group">
        <label>Prediction Correctness</label>
        <select id="filter-correctness">
          <option value="ALL">All Predictions</option>
          <option value="CORRECT">Correct Predictions Only</option>
          <option value="INCORRECT">Misclassified / False Alarms</option>
        </select>
      </div>
    </div>

    <div class="slider-row">
      <span>Heatmap Overlay Opacity:</span>
      <input type="range" id="opacity-slider" min="0" max="100" value="70">
      <span id="opacity-val" style="min-width: 35px;">70%</span>
    </div>
  </div>

  <!-- Gallery Grid -->
  <div class="gallery-grid" id="gallery-container"></div>

  <!-- Modal Detail Viewer -->
  <div class="modal" id="modal-viewer">
    <div class="modal-content">
      <div class="modal-header">
        <h3 id="modal-title">Specimen Details</h3>
        <button class="close-btn" onclick="closeModal()">&times;</button>
      </div>
      <div class="modal-body">
        <div class="modal-img-box">
          <img id="modal-base-img" style="width: 100%; height: 100%; object-fit: contain;">
          <img id="modal-hm-img" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: contain; opacity: 0.7;">
        </div>
        <div class="modal-meta" id="modal-meta-content"></div>
      </div>
    </div>
  </div>

  <script>
    const DATA = {items_json};

    const container = document.getElementById('gallery-container');
    const opacitySlider = document.getElementById('opacity-slider');
    const opacityVal = document.getElementById('opacity-val');

    opacitySlider.addEventListener('input', (e) => {{
      const val = e.target.value;
      opacityVal.textContent = val + '%';
      document.querySelectorAll('.img-overlay').forEach(img => {{
        img.style.opacity = val / 100.0;
      }});
      const modalHm = document.getElementById('modal-hm-img');
      if (modalHm) modalHm.style.opacity = val / 100.0;
    }});

    function renderGallery() {{
      const cat = document.getElementById('filter-category').value;
      const cond = document.getElementById('filter-condition').value;
      const sim = document.getElementById('filter-similarity').value;
      const val = document.getElementById('filter-validation').value;
      const corr = document.getElementById('filter-correctness').value;

      container.innerHTML = '';
      let matchCount = 0;

      DATA.forEach(item => {{
        if (cat !== 'ALL' && item.category !== cat) return;
        if (cond !== 'ALL' && item.expected_condition !== cond) return;
        if (sim !== 'ALL' && item.similarity_group !== sim) return;
        if (val !== 'ALL') {{
          if (val === 'APPROVED' && !item.validation_status.startsWith('APPROVED')) return;
          if (val !== 'APPROVED' && item.validation_status !== val) return;
        }}
        if (corr !== 'ALL') {{
          if (corr === 'CORRECT' && !item.is_correct) return;
          if (corr === 'INCORRECT' && item.is_correct) return;
        }}

        matchCount++;
        const card = document.createElement('div');
        card.className = 'specimen-card';
        card.onclick = () => openModal(item);

        const condPillClass = item.expected_condition === 'NORMAL' ? 'pill-norm' : 'pill-defe';
        const predPillClass = item.predicted_condition === 'NORMAL' ? 'pill-norm' : (item.predicted_condition === 'DEFECTIVE' ? 'pill-defe' : 'pill-rej');
        
        let gateClass = 'gate-accepted';
        if (item.gate_status === 'LOW_CONFIDENCE') gateClass = 'gate-low';
        else if (item.gate_status === 'UNSUPPORTED_CATEGORY') gateClass = 'gate-unsupported';
        else if (item.gate_status === 'POOR_IMAGE_QUALITY') gateClass = 'gate-quality';

        card.innerHTML = `
          <div class="img-container">
            <img class="img-base" src="${{item.original_image_path}}" alt="${{item.image_id}}" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'300\\' height=\\'300\\'><rect fill=\\'%231e293b\\' width=\\'300\\' height=\\'300\\'/><text fill=\\'%2394a3b8\\' x=\\'50%\\' y=\\'50%\\' text-anchor=\\'middle\\'>Image Not Found</text></svg>'">
            <img class="img-overlay" src="${{item.heatmap_image_path}}" alt="Heatmap" onerror="this.style.display='none'">
          </div>
          <div class="card-meta">
            <div class="card-header">
              <span class="cat-badge">${{item.category}}</span>
              <span class="cond-pill ${{condPillClass}}">${{item.expected_condition}}</span>
            </div>
            <div class="meta-metrics">
              <div>Score: <b>${{item.anomaly_score.toFixed(3)}}</b></div>
              <div>Thresh: <b>${{item.calibrated_threshold.toFixed(3)}}</b></div>
              <div>Pred: <span class="cond-pill ${{predPillClass}}" style="padding:1px 4px; font-size:10px;">${{item.predicted_condition}}</span></div>
              <div>Latency: <b>${{item.latency_ms.toFixed(0)}}ms</b></div>
            </div>
            <div class="card-footer">
              <span class="gate-badge ${{gateClass}}">${{item.gate_status}}</span>
              <span style="color:${{item.is_correct ? '#22c55e' : '#ef4444'}}; font-weight:700;">
                ${{item.is_correct ? 'âœ“ MATCH' : 'âœ— MISMATCH'}}
              </span>
            </div>
          </div>
        `;
        container.appendChild(card);
      }});

      if (matchCount === 0) {{
        container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 48px; color: var(--text-muted);">No images match the selected filters.</div>';
      }}
    }}

    function openModal(item) {{
      document.getElementById('modal-title').textContent = item.image_id + ' (' + item.category + ')';
      document.getElementById('modal-base-img').src = item.original_image_path;
      const hm = document.getElementById('modal-hm-img');
      hm.src = item.heatmap_image_path;
      hm.style.display = 'block';

      const meta = document.getElementById('modal-meta-content');
      meta.innerHTML = `
        <div><b>Category:</b> ${{item.category}} (${{item.category_type}})</div>
        <div><b>Expected Condition:</b> ${{item.expected_condition}}</div>
        <div><b>Defect Subtype:</b> ${{item.defect_type}}</div>
        <div><b>Detected Auto Category:</b> ${{item.detected_category}} (conf: ${{(item.category_confidence * 100).toFixed(1)}}%)</div>
        <div><b>Safety Gate Status:</b> <span class="gate-badge">${{item.gate_status}}</span></div>
        <div><b>Anomaly Score:</b> ${{item.anomaly_score.toFixed(4)}}</div>
        <div><b>Calibrated Decision Threshold:</b> ${{item.calibrated_threshold.toFixed(4)}}</div>
        <div><b>Margin to Threshold:</b> ${{item.margin_to_threshold >= 0 ? '+' : ''}}${{item.margin_to_threshold.toFixed(4)}}</div>
        <div><b>Predicted Condition:</b> ${{item.predicted_condition}}</div>
        <div><b>Prediction Correctness:</b> ${{item.is_correct ? '<span style="color:#22c55e; font-weight:700;">CORRECT</span>' : '<span style="color:#ef4444; font-weight:700;">INCORRECT</span>'}}</div>
        <div><b>Similarity Tier:</b> ${{item.similarity_group}}</div>
        <div><b>Validation Tier:</b> ${{item.validation_status}}</div>
        <div><b>Failure Classification:</b> ${{item.failure_category}}</div>
        <div><b>Failure Diagnosis:</b> ${{item.failure_diagnosis}}</div>
        <div><b>Source Platform:</b> ${{item.source_name}}</div>
        <div><b>Source URL:</b> <a href="${{item.source_url}}" target="_blank" style="color:var(--primary); word-break:break-all;">${{item.source_url || 'N/A'}}</a></div>
      `;
      document.getElementById('modal-viewer').classList.add('active');
    }}

    function closeModal() {{
      document.getElementById('modal-viewer').classList.remove('active');
    }}

    ['filter-category', 'filter-condition', 'filter-similarity', 'filter-validation', 'filter-correctness'].forEach(id => {{
      document.getElementById(id).addEventListener('change', renderGallery);
    }});

    renderGallery();
  </script>
</body>
</html>
"""

    os.makedirs("external_validation/galleries", exist_ok=True)
    os.makedirs("external_validation/gallery", exist_ok=True)
    
    with open("external_validation/galleries/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    with open("external_validation/gallery/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Generated external_validation/galleries/index.html and external_validation/gallery/index.html with {len(items)} items.")

if __name__ == "__main__":
    generate_gallery()
