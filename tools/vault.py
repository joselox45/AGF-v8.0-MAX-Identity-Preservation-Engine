#!/usr/bin/env python3
"""
AGF Vault CLI — genesis + append + verify + metrics del Evidence Vault.
Uso:
  python tools/vault.py genesis            # encadena evidencias existentes
  python tools/vault.py append <ev.json>   # anade una corrida
  python tools/vault.py verify             # recomputo completo desde disco
  python tools/vault.py metrics            # MOAT_METRICS
"""
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from evidence_vault import EvidenceVault

V = EvidenceVault(os.environ.get("AGF_VAULT", "evidence/vault_v2.jsonl"))
cmd = sys.argv[1] if len(sys.argv) > 1 else "metrics"

if cmd == "genesis":
    seeds = ["evidence/t21.json", "evidence/t22.json",
             "evidence/benchmark_t30.json", "evidence/benchmark_corpus.json"]
    for root in ["evidence/verify_2026-10-14"]:
        if os.path.isdir(root):
            seeds += [os.path.join(root, f) for f in sorted(os.listdir(root))
                      if f.endswith(".json")]
    for s in seeds:
        if os.path.exists(s):
            r = V.append(s)
            print(f"#{r.seq:3d} {r.evidence_file}  L3={r.verdict_l3}")
    print(json.dumps(V.verify(), ensure_ascii=False))
elif cmd == "append":
    r = V.append(sys.argv[2])
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=1))
    print(json.dumps(V.verify(), ensure_ascii=False))
elif cmd == "verify":
    print(json.dumps(V.verify(), indent=1, ensure_ascii=False))
elif cmd == "metrics":
    print(json.dumps(V.metrics(), indent=2, ensure_ascii=False))
elif cmd == "metrics-append":
    rates = json.load(open(sys.argv[2]))
    r = V.append_metrics(rates, source=sys.argv[3] if len(sys.argv) > 3 else "kernel_v3")
    print(json.dumps(r.to_dict(), ensure_ascii=False, indent=1))
    print(json.dumps(V.verify(), ensure_ascii=False))
else:
    print(__doc__); sys.exit(2)
