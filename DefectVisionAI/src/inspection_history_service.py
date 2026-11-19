"""
DefectVision AI — Inspection History Service
Logs and manages in-memory and persistent records of all optical inspections,
supporting querying, category filtering, search, and statistical reporting.
"""

import os
import json
import time
from datetime import datetime

class InspectionHistoryService:
    def __init__(self, history_file=None, max_records=200):
        self.max_records = max_records
        if history_file is None:
            env_data = os.environ.get("DEFECTVISION_DATA_DIR")
            if env_data:
                history_file = os.path.join(env_data, "reports", "inspection_history.json")
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                history_file = os.path.join(base_dir, "reports", "inspection_history.json")
        self.history_file = history_file
        self.records = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        try:
            import numpy as np
            cleaned = []
            for r in self.records[:self.max_records]:
                cleaned.append({k: v for k, v in r.items() if not isinstance(v, (np.ndarray, np.generic))})
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save inspection history: {e}")

    def add_inspection(self, record):
        """
        Appends an inspection record with guaranteed production telemetry schema.
        """
        # Ensure timestamp and ID
        if "id" not in record:
            record["id"] = f"insp_{int(time.time()*1000)}"
        if "inspection_id" not in record:
            record["inspection_id"] = record["id"]
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()
        if "data_provenance" not in record:
            mode = record.get("routing_mode", "benchmark")
            if mode == "production":
                record["data_provenance"] = "few_shot_product_adaptation"
            elif mode == "universal":
                record["data_provenance"] = "universal_triage"
            else:
                record["data_provenance"] = "official_mvtec_ad_benchmark"
        if "quality_gate_status" not in record:
            record["quality_gate_status"] = record.get("image_quality_status", "VALID")
        if "masking_status" not in record:
            record["masking_status"] = record.get("foreground_mask_validity", "SKIPPED")
        if "processing_latency_ms" not in record:
            record["processing_latency_ms"] = record.get("processing_time_ms", 0.0)

        # Prepend to list (latest first)
        self.records.insert(0, record)
        if len(self.records) > self.max_records:
            self.records = self.records[:self.max_records]

        # Async or periodic save
        self.save_history()
        return record

    def get_recent(self, limit=50, category=None, verdict=None):
        filtered = self.records
        if category and category != "all":
            filtered = [r for r in filtered if r.get("detected_category") == category or r.get("category") == category]
        if verdict and verdict != "all":
            filtered = [r for r in filtered if r.get("verdict") == verdict or r.get("predicted_label") == verdict]

        return filtered[:limit]

    def get_history(self, limit=50, category=None, verdict=None):
        return self.get_recent(limit=limit, category=category, verdict=verdict)

    def clear(self):
        self.records = []
        self.save_history()

    def clear_history(self):
        self.clear()

    def get_statistics(self):
        total = len(self.records)
        verdicts = {}
        total_latency = 0.0
        for r in self.records:
            v = r.get("verdict", "UNKNOWN")
            verdicts[v] = verdicts.get(v, 0) + 1
            total_latency += float(r.get("processing_time_ms", 0.0))

        avg_lat = round(total_latency / total, 2) if total > 0 else 0.0
        return {
            "total_inspections": total,
            "verdicts": verdicts,
            "avg_latency_ms": avg_lat
        }
