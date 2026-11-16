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
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.records[:self.max_records], f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save inspection history: {e}")

    def add_inspection(self, record):
        """
        Appends an inspection record.
        """
        # Ensure timestamp and ID
        if "id" not in record:
            record["id"] = f"insp_{int(time.time()*1000)}"
        if "timestamp" not in record:
            record["timestamp"] = datetime.now().isoformat()

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
