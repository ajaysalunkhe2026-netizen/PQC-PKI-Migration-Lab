#!/usr/bin/env python3
"""Run the small deterministic policy regression suite."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "policy_engine.py"
RESULTS_DIR = ROOT / "results"

TESTS = [
    {"algorithm": "ML-DSA-65", "expected": "DENY"},
    {"algorithm": "SLH-DSA-SHA2-128s", "expected": "ALLOW"},
    {"algorithm": "ML-DSA-44", "expected": "DENY"},
]


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    for test in TESTS:
        run = subprocess.run(
            [sys.executable, str(ENGINE), test["algorithm"]],
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode == 0:
            actual = "ALLOW"
        elif run.returncode == 1:
            actual = "DENY"
        else:
            actual = "ERROR"

        results.append({
            "algorithm": test["algorithm"],
            "expected": test["expected"],
            "actual": actual,
            "status": "PASS" if actual == test["expected"] else "FAIL",
            "output": run.stdout.strip(),
            "error": run.stderr.strip() if run.returncode not in (0, 1) else None,
        })

    report = {
        "test_suite": "PQC Algorithm Retirement Policy",
        "environment": "LAB",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "overall_status": "PASS" if all(item["status"] == "PASS" for item in results) else "FAIL",
    }

    output = RESULTS_DIR / "retirement-policy-test-report.json"
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    for item in results:
        print(f'{item["algorithm"]}: {item["actual"]} — {item["status"]}')
    print(f'\nOverall: {report["overall_status"]}')
    print(f'Report: {output}')

    return 0 if report["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
