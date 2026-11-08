#!/usr/bin/env python3
"""Read-only preflight for accidental private-key publication."""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "git-security-audit.json"
PRIVATE_KEY_MARKER = re.compile(
    r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----",
    re.IGNORECASE,
)
ALWAYS_SENSITIVE = {".key", ".p12", ".pfx", ".p8"}
MAX_SCAN_BYTES = 5_000_000


def git_files() -> tuple[bool, list[str]]:
    check = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True, check=False,
    )
    if check.returncode != 0:
        return False, []

    listing = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=False,
    )
    if listing.returncode != 0:
        raise RuntimeError(listing.stderr.strip() or "Unable to list Git files")
    return True, sorted(set(listing.stdout.splitlines()))


def inspect_file(relative: str) -> dict | None:
    path = ROOT / relative
    suffix = path.suffix.lower()
    if suffix in ALWAYS_SENSITIVE or "private" in path.name.lower():
        return {"file": relative, "type": "Sensitive filename", "action": "KEEP OUT OF PUBLIC REPOSITORY"}

    if not path.is_file() or path.stat().st_size > MAX_SCAN_BYTES:
        return None

    try:
        content = path.read_bytes()
    except OSError:
        return {"file": relative, "type": "Unreadable file", "action": "REVIEW MANUALLY"}

    if PRIVATE_KEY_MARKER.search(content.decode("utf-8", errors="ignore")):
        return {"file": relative, "type": "Private-key PEM content", "action": "REMOVE FROM PUBLIC REPOSITORY"}
    return None


def main() -> int:
    try:
        is_git, files = git_files()
        findings = [item for name in files if (item := inspect_file(name))]
    except (OSError, RuntimeError) as exc:
        print(f"Security preflight failed: {exc}")
        return 2

    report = {
        "project": ROOT.name,
        "scan_type": "Read-only Git security preflight",
        "git_repository_detected": is_git,
        "files_scanned": len(files),
        "sensitive_files_found": findings,
        "status": "REVIEW REQUIRED" if findings else "NO FINDINGS",
        "note": "This audit does not modify .gitignore, stage files, or push changes.",
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("===== GIT SECURITY PREFLIGHT =====")
    print("Git repository:", is_git)
    print("Files scanned:", len(files))
    print("Sensitive findings:", len(findings))
    for item in findings:
        print("WARNING:", item["file"], "-", item["action"])
    print("Report:", REPORT)
    print("Status:", report["status"])
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
