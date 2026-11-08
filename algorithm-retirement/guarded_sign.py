#!/usr/bin/env python3
"""Policy-gated SLH-DSA signing demo for the PQC retirement lab."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
POLICY_ENGINE = BASE / "policy_engine.py"
RESULTS = BASE / "results"
LOG_FILE = RESULTS / "execution-audit.jsonl"
MESSAGE = RESULTS / "sample-message.txt"
SIGNATURE = RESULTS / "guarded-signature.bin"

KEYS = {
    "SLH-DSA-SHA2-128s": {
        "private": BASE / "keys" / "slh-dsa-private.pem",
        "public": BASE / "keys" / "slh-dsa-public.pem",
    }
}


def find_openssl() -> str | None:
    configured = os.environ.get("OPENSSL_BIN")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return str(candidate)
        located = shutil.which(configured)
        return located

    located = shutil.which("openssl")
    if located:
        return located

    windows_default = Path(r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe")
    return str(windows_default) if windows_default.is_file() else None


def log_event(event: dict) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def run_policy(algorithm: str) -> tuple[str, str]:
    result = subprocess.run(
        [sys.executable, str(POLICY_ENGINE), algorithm],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return "ALLOW", result.stdout.strip()
    if result.returncode == 1:
        return "DENY", result.stdout.strip()
    return "ERROR", result.stderr.strip() or "Policy engine failed"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python guarded_sign.py <algorithm>", file=sys.stderr)
        return 2

    algorithm = sys.argv[1]
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "algorithm": algorithm,
        "policy_decision": "ERROR",
        "openssl_executed": False,
    }

    try:
        decision, detail = run_policy(algorithm)
        event["policy_decision"] = decision

        if decision == "DENY":
            event["execution_result"] = "BLOCKED"
            log_event(event)
            print("POLICY: DENY")
            print("OpenSSL execution blocked.")
            return 1

        if decision == "ERROR":
            event["execution_result"] = "POLICY_ERROR"
            log_event(event)
            print("Policy evaluation failed; signing was not attempted.", file=sys.stderr)
            if detail:
                print(detail, file=sys.stderr)
            return 2

        if algorithm not in KEYS:
            event["execution_result"] = "NOT_CONFIGURED"
            log_event(event)
            print("POLICY: ALLOW")
            print("No signing key is configured for this approved algorithm.")
            return 3

        openssl = find_openssl()
        key = KEYS[algorithm]
        missing = [p.name for p in (key["private"], key["public"], MESSAGE) if not p.is_file()]
        if not openssl or missing:
            event["execution_result"] = "PREREQUISITE_MISSING"
            log_event(event)
            print("Required signing prerequisites are missing; no signing was attempted.", file=sys.stderr)
            if not openssl:
                print("OpenSSL was not found. Install it or set OPENSSL_BIN.", file=sys.stderr)
            if missing:
                print("Missing lab file(s): " + ", ".join(missing), file=sys.stderr)
            return 2

        RESULTS.mkdir(parents=True, exist_ok=True)
        sign = subprocess.run(
            [openssl, "pkeyutl", "-sign", "-inkey", str(key["private"]),
             "-rawin", "-in", str(MESSAGE), "-out", str(SIGNATURE)],
            capture_output=True, text=True, check=False,
        )
        event["openssl_executed"] = True
        if sign.returncode != 0:
            event["execution_result"] = "SIGNING_FAILED"
            log_event(event)
            print("POLICY: ALLOW")
            print("OpenSSL signing failed; see local OpenSSL diagnostics.", file=sys.stderr)
            return 4

        verify = subprocess.run(
            [openssl, "pkeyutl", "-verify", "-pubin", "-inkey", str(key["public"]),
             "-rawin", "-in", str(MESSAGE), "-sigfile", str(SIGNATURE)],
            capture_output=True, text=True, check=False,
        )
        event["verification_result"] = "PASS" if verify.returncode == 0 else "FAIL"
        event["execution_result"] = "SUCCESS" if verify.returncode == 0 else "VERIFICATION_FAILED"
        event["signature_file"] = "results/guarded-signature.bin"
        log_event(event)

        print("POLICY: ALLOW")
        print("OpenSSL signing: SUCCESS")
        print("Signature verification:", event["verification_result"])
        return 0 if verify.returncode == 0 else 5

    except (OSError, subprocess.SubprocessError) as exc:
        event["execution_result"] = "ERROR"
        log_event(event)
        print(f"Signing workflow error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
