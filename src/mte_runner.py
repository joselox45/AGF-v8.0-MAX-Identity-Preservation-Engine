#!/usr/bin/env python3
import json
import sys
from pathlib import Path

VALID = {"PASS", "FAIL", "BLOCKED", "UNVERIFIED", "NOT_RUN", "NOT_APPLICABLE"}

def evaluate(records):
    if not records:
        return "NOT_RUN"
    for r in records:
        if r.get("status") not in VALID:
            return "INVALID_EVIDENCE"
        if r["status"] == "PASS" and not (r.get("evidence_ref") and r.get("reason", "").strip()):
            return "INVALID_EVIDENCE"
    statuses = {r["status"] for r in records}
    if "FAIL" in statuses: return "NON_CONFORMANT"
    if "BLOCKED" in statuses: return "BLOCKED"
    if "UNVERIFIED" in statuses: return "UNVERIFIED"
    if "NOT_RUN" in statuses: return "INCOMPLETE"
    return "CONFORMANT_WITHIN_TESTED_SCOPE"

def main():
    if len(sys.argv) != 2:
        print("Usage: python src/mte_runner.py <results.json>")
        return 2
    path = Path(sys.argv[1])
    records = json.loads(path.read_text(encoding="utf-8"))
    status = evaluate(records)
    print(json.dumps({"suite_status": status, "records": len(records)}, indent=2))
    return 0 if status == "CONFORMANT_WITHIN_TESTED_SCOPE" else 1

if __name__ == "__main__":
    raise SystemExit(main())
