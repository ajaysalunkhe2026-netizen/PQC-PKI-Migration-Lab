import subprocess
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).parent
engine = root / "policy_engine.py"
results_dir = root / "results"
results_dir.mkdir(exist_ok=True)

tests = [
    {"algorithm": "ML-DSA-65", "expected": "DENY"},
    {"algorithm": "SLH-DSA-SHA2-128s", "expected": "ALLOW"},
    {"algorithm": "ML-DSA-44", "expected": "DENY"},
]

results = []

for test in tests:
    run = subprocess.run(
        [sys.executable, str(engine), test["algorithm"]],
        capture_output=True,
        text=True
    )

    actual = "ALLOW" if run.returncode == 0 else (
        "DENY" if run.returncode == 1 else "ERROR"
    )

    results.append({
        "algorithm": test["algorithm"],
        "expected": test["expected"],
        "actual": actual,
        "status": "PASS" if actual == test["expected"] else "FAIL",
        "output": run.stdout.strip()
    })

report = {
    "test_suite": "PQC Algorithm Retirement Policy",
    "environment": "LAB",
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "results": results,
    "overall_status": (
        "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL"
    )
}

output = results_dir / "retirement-policy-test-report.json"
output.write_text(json.dumps(report, indent=2), encoding="utf-8")

for result in results:
    print(f'{result["algorithm"]}: {result["actual"]} — {result["status"]}')

print(f'\nOverall: {report["overall_status"]}')
print(f'Report: {output}')

sys.exit(0 if report["overall_status"] == "PASS" else 1)
