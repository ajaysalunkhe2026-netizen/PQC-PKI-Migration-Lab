#!/usr/bin/env python3
"""Default-deny policy evaluator for the PQC algorithm retirement lab."""

import json
import sys
from pathlib import Path
from typing import Any

POLICY_FILE = Path(__file__).resolve().parent / "policies" / "algorithm-policy.json"


def load_policy() -> dict[str, Any]:
    with POLICY_FILE.open("r", encoding="utf-8-sig") as handle:
        policy = json.load(handle)

    if not isinstance(policy, dict):
        raise ValueError("Policy document must be a JSON object")

    retired = policy.get("retired_algorithms")
    approved = policy.get("approved_algorithms")
    if not isinstance(retired, list) or not all(isinstance(x, str) and x for x in retired):
        raise ValueError("'retired_algorithms' must be a list of non-empty strings")
    if not isinstance(approved, list) or not all(isinstance(x, str) and x for x in approved):
        raise ValueError("'approved_algorithms' must be a list of non-empty strings")
    if len(retired) != len(set(retired)) or len(approved) != len(set(approved)):
        raise ValueError("Algorithm lists must not contain duplicates")
    overlap = set(retired) & set(approved)
    if overlap:
        raise ValueError(f"Algorithms cannot be both retired and approved: {sorted(overlap)}")
    if policy.get("default_action") != "DENY":
        raise ValueError("This lab requires default_action to be DENY")

    return policy


def evaluate_algorithm(algorithm: str) -> tuple[str, str]:
    if not isinstance(algorithm, str) or not algorithm.strip():
        raise ValueError("Algorithm name must be a non-empty string")

    policy = load_policy()
    if algorithm in policy["retired_algorithms"]:
        return "DENY", "Algorithm is retired"
    if algorithm in policy["approved_algorithms"]:
        return "ALLOW", "Algorithm is approved"
    return "DENY", "Algorithm is not approved by policy"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python policy_engine.py <algorithm>", file=sys.stderr)
        return 2

    try:
        algorithm = sys.argv[1]
        decision, reason = evaluate_algorithm(algorithm)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Policy evaluation error: {exc}", file=sys.stderr)
        return 2

    print(f"Algorithm: {algorithm}")
    print(f"Decision:  {decision}")
    print(f"Reason:    {reason}")
    return 0 if decision == "ALLOW" else 1


if __name__ == "__main__":
    raise SystemExit(main())
