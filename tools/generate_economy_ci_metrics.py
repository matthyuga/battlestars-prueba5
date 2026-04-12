#!/usr/bin/env python3
"""Genera métricas operativas de CI para Economy Toolkit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera resumen de métricas operativas desde diff JSON.")
    ap.add_argument("--diff-json", required=True)
    ap.add_argument("--out-json", default="/tmp/economy_ci_metrics.json")
    args = ap.parse_args()

    payload = load_json(args.diff_json)
    rows = (((payload or {}).get("diff") or {}).get("scenarios") or [])
    alerts = (payload or {}).get("alerts") or []

    max_abs = 0.0
    per_metric_max: Dict[str, float] = {
        "gold_final_policy.p50": 0.0,
        "gold_final_policy.p95": 0.0,
        "exp_final_policy.p50": 0.0,
        "exp_final_policy.p95": 0.0,
    }

    for row in rows:
        metrics = row.get("metrics", {})
        for block in ("gold_final_policy", "exp_final_policy"):
            for stat in ("p50", "p95"):
                key = f"{block}.{stat}"
                dp = float((((metrics.get(block) or {}).get(stat) or {}).get("delta_pct") or 0.0))
                adp = abs(dp)
                max_abs = max(max_abs, adp)
                per_metric_max[key] = max(per_metric_max.get(key, 0.0), adp)

    out = {
        "meta": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_diff_json": args.diff_json,
            "old_version": ((payload.get("meta") or {}).get("old_version")),
            "new_version": ((payload.get("meta") or {}).get("new_version")),
        },
        "summary": {
            "num_scenarios": len(rows),
            "num_alerts": len(alerts),
            "max_abs_delta_pct": max_abs,
            "max_abs_delta_pct_by_metric": per_metric_max,
        },
    }

    out_path = Path(args.out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] métricas CI guardadas: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
