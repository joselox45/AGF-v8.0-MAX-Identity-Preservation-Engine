#!/usr/bin/env bash
set -euo pipefail

REPO="joselox45/AGF-v8.0-MAX-Identity-Preservation-Engine"
RULESET_ID="26237246"
FILE=".github/rulesets/frozen-main-v12.3-minimal.proposed.json"

if [[ ! -f "$FILE" ]]; then
  echo "ERROR: falta $FILE"
  exit 1
fi

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "DRY-RUN — payload que se enviaria:"
  python3 -m json.tool "$FILE"
  exit 0
fi

echo "Vas a aplicar el ruleset a $REPO (id=$RULESET_ID)."
read -r -p "Confirmas? [y/N] " ok
if [[ ! "$ok" =~ ^[Yy]$ ]]; then
  echo "Cancelado."
  exit 1
fi

gh api -X PUT "repos/$REPO/rulesets/$RULESET_ID" \
  --input "$FILE" \
  --jq '{id, name, enforcement, updated_at}'

echo "OK: ruleset aplicado."
