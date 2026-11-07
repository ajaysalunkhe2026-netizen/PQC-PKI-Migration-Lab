import json
import sys
from pathlib import Path

POLICY_FILE = Path(__file__).parent / "policies" / "algorithm-policy.json"

def evaluate_algorithm(algorithm):
    with POLICY_FILE.open("r", encoding="utf-8-sig") as file:
        policy = json.load(file)

    retired = policy["retired_algorithms"]
    approved = policy["approved_algorithms"]

    if algorithm in retired:
        return "DENY", "Algorithm is retired"

    if algorithm in approved:
        return "ALLOW", "Algorithm is approved"

    return "DENY", "Algorithm is not approved by policy"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python policy_engine.py <algorithm>")
        sys.exit(2)

    algorithm = sys.argv[1]
    decision, reason = evaluate_algorithm(algorithm)

    print(f"Algorithm: {algorithm}")
    print(f"Decision:  {decision}")
    print(f"Reason:    {reason}")

    sys.exit(0 if decision == "ALLOW" else 1)
