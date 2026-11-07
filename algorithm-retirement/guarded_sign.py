import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

POLICY_ENGINE = BASE / "policy_engine.py"
OPENSSL = Path(r"C:\Program Files\OpenSSL-Win64\bin\openssl.exe")

RESULTS = BASE / "results"
LOG_FILE = RESULTS / "execution-audit.jsonl"
MESSAGE = RESULTS / "sample-message.txt"
SIGNATURE = RESULTS / "guarded-signature.bin"

KEYS = {
    "SLH-DSA-SHA2-128s": {
        "private": BASE / "keys" / "slh-dsa-private.pem",
        "public": BASE / "keys" / "slh-dsa-public.pem"
    }
}

def log_event(event):
    RESULTS.mkdir(exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python guarded_sign.py <algorithm>")
        sys.exit(2)

    algorithm = sys.argv[1]

    check = subprocess.run(
        [sys.executable, str(POLICY_ENGINE), algorithm],
        capture_output=True,
        text=True
    )

    decision = (
        "ALLOW" if check.returncode == 0 else
        "DENY" if check.returncode == 1 else "ERROR"
    )

    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "algorithm": algorithm,
        "policy_decision": decision,
        "openssl_executed": False
    }

    if decision != "ALLOW":
        event["execution_result"] = "BLOCKED"
        log_event(event)
        print("POLICY: DENY")
        print("OpenSSL execution blocked.")
        sys.exit(1)

    if algorithm not in KEYS:
        event["execution_result"] = "NOT_CONFIGURED"
        log_event(event)
        print("POLICY: ALLOW")
        print("No signing key configured for this algorithm.")
        sys.exit(3)

    if not OPENSSL.exists() or not MESSAGE.exists():
        event["execution_result"] = "ERROR"
        log_event(event)
        print("OpenSSL executable or test message not found.")
        sys.exit(2)

    key = KEYS[algorithm]

    event["openssl_executed"] = True

    sign = subprocess.run([
        str(OPENSSL), "pkeyutl", "-sign",
        "-inkey", str(key["private"]),
        "-rawin",
        "-in", str(MESSAGE),
        "-out", str(SIGNATURE)
    ], capture_output=True, text=True)

    if sign.returncode != 0:
        event["execution_result"] = "SIGNING_FAILED"
        event["error"] = sign.stderr.strip()
        log_event(event)
        print("POLICY: ALLOW")
        print("Signing failed:", sign.stderr.strip())
        sys.exit(4)

    verify = subprocess.run([
        str(OPENSSL), "pkeyutl", "-verify",
        "-pubin",
        "-inkey", str(key["public"]),
        "-rawin",
        "-in", str(MESSAGE),
        "-sigfile", str(SIGNATURE)
    ], capture_output=True, text=True)

    event["verification_result"] = (
        "PASS" if verify.returncode == 0 else "FAIL"
    )
    event["execution_result"] = (
        "SUCCESS" if verify.returncode == 0 else "VERIFICATION_FAILED"
    )
    event["signature_file"] = str(SIGNATURE)
    log_event(event)

    print("POLICY: ALLOW")
    print("OpenSSL signing: SUCCESS")
    print("Signature verification:", event["verification_result"])

    sys.exit(0 if verify.returncode == 0 else 5)

if __name__ == "__main__":
    main()
