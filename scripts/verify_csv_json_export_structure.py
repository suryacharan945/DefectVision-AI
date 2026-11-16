import csv
import json
import io

print("--- Testing Batch CSV & JSON Export Logic ---")
mock_report = {
    "batch_id": "batch_20261031_test",
    "timestamp": "2026-10-31 21:16:18",
    "total_inspected": 2,
    "defective_count": 2,
    "normal_count": 0,
    "defect_rate_pct": 100.0,
    "results": [
        {
            "filename": "bottle_01.png",
            "category": "bottle",
            "predicted_label": "defective",
            "severity_level": "Critical",
            "severity_score": 72.5,
            "confidence_pct": 98.45
        },
        {
            "filename": "screw_01.png",
            "category": "screw",
            "predicted_label": "defective",
            "severity_level": "Critical",
            "severity_score": 85.0,
            "confidence_pct": 99.12
        }
    ]
}

# Test CSV export logic
headers = ['filename', 'category', 'predicted_label', 'severity_level', 'severity_score', 'confidence_pct']
output = io.StringIO()
writer = csv.writer(output)
writer.writerow(headers)
for r in mock_report['results']:
    writer.writerow([r['filename'], r['category'], r['predicted_label'], r['severity_level'], r['severity_score'], r['confidence_pct']])

csv_str = output.getvalue()
print("Generated CSV:")
print(csv_str)

# Verify parseable
reader = list(csv.reader(io.StringIO(csv_str)))
assert len(reader) == 3, "CSV rows mismatch!"
assert reader[0] == headers, "CSV headers mismatch!"
print("CSV export logic verified!")

# Test JSON export logic
json_str = json.dumps(mock_report, indent=2)
parsed_json = json.loads(json_str)
assert parsed_json["batch_id"] == mock_report["batch_id"], "JSON mismatch!"
print("JSON export logic verified!")
