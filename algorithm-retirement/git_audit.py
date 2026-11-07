from pathlib import Path
import subprocess
import json
import re
import sys

ROOT = Path.cwd()
REPORT = ROOT / "docs" / "git-security-audit.json"
REPORT.parent.mkdir(exist_ok=True)

PRIVATE_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"-----BEGIN ENCRYPTED PRIVATE KEY-----")
]

SENSITIVE_EXTENSIONS = {
    ".pem", ".key", ".p12", ".pfx", ".p8"
}

IGNORE = [
    "*.key", "*.pem", "*.p12", "*.pfx", "*.p8", "*.der",
    ".env", ".env.*", "secrets/",
    "__pycache__/", "*.pyc", "*.tmp", "*.log"
]

gitignore = ROOT / ".gitignore"
existing = gitignore.read_text(encoding="utf-8-sig") if gitignore.exists() else ""
with gitignore.open("a", encoding="utf-8") as f:
    for rule in IGNORE:
        if rule not in existing.splitlines():
            f.write(rule + "\n")

findings = []
skipped = {".git", "__pycache__", ".venv", "venv"}

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in skipped for part in path.parts):
        continue

    if path.suffix.lower() in SENSITIVE_EXTENSIONS:
        findings.append({
            "file": str(path.relative_to(ROOT)),
            "type": "Sensitive extension",
            "action": "EXCLUDE FROM PUBLIC REPOSITORY"
        })
        continue

    try:
        if path.stat().st_size > 5_000_000:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(content):
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "type": "Private key content detected",
                    "action": "DO NOT PUBLISH"
                })
                break
    except OSError:
        pass

git = subprocess.run(
    ["git", "rev-parse", "--is-inside-work-tree"],
    capture_output=True, text=True
)

tracked = []
if git.returncode == 0:
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True
    )
    tracked = result.stdout.splitlines()

report = {
    "project": ROOT.name,
    "scan_type": "Local Git security preflight",
    "sensitive_files_found": findings,
    "currently_tracked_files": tracked,
    "git_repository_detected": git.returncode == 0,
    "push_authorized": False,
    "status": "REVIEW REQUIRED" if findings or tracked else "NO FINDINGS"
}

REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n===== GIT SECURITY PREFLIGHT =====")
print("Git repository:", report["git_repository_detected"])
print("Sensitive files found:", len(findings))
print("Currently tracked files:", len(tracked))

for item in findings:
    print("WARNING:", item["file"], "-", item["action"])

for item in tracked:
    if Path(item).suffix.lower() in SENSITIVE_EXTENSIONS:
        print("CRITICAL: Sensitive file already tracked:", item)

print("\nReport:", REPORT)
print("Status:", report["status"])
print("\nNo files have been pushed or uploaded.")
