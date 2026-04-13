#!/usr/bin/env python3
"""
Comparador v1 de baselines Economy Lab.

Compara dos versiones congeladas (suite.json) y reporta deltas por escenario.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Any, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_metric(scenario_payload: Dict[str, Any], block: str, stat: str) -> float:
    agg = scenario_payload.get("aggregate", {}) if isinstance(scenario_payload, dict) else {}
    b = agg.get(block, {}) if isinstance(agg.get(block, {}), dict) else {}
    v = b.get(stat, 0.0)
    try:
        return float(v)
    except Exception:
        return 0.0


def pct_delta(old: float, new: float) -> float:
    if abs(old) < 1e-9:
        return 0.0 if abs(new) < 1e-9 else 100.0
    return ((new / old) - 1.0) * 100.0


def compare_suites(old_suite: Dict[str, Any], new_suite: Dict[str, Any]) -> Dict[str, Any]:
    old_sc = old_suite.get("scenarios", {}) if isinstance(old_suite, dict) else {}
    new_sc = new_suite.get("scenarios", {}) if isinstance(new_suite, dict) else {}

    names = sorted(set(old_sc.keys()) & set(new_sc.keys()))
    rows: List[Dict[str, Any]] = []
    for name in names:
        o = old_sc[name]
        n = new_sc[name]
        row = {"scenario": name, "metrics": {}}
        for block in ("gold_final_policy", "exp_final_policy"):
            row["metrics"][block] = {}
            for stat in ("p50", "p95"):
                ov = get_metric(o, block, stat)
                nv = get_metric(n, block, stat)
                row["metrics"][block][stat] = {
                    "old": ov,
                    "new": nv,
                    "delta_abs": nv - ov,
                    "delta_pct": pct_delta(ov, nv),
                }
        rows.append(row)
    return {"scenarios": rows}


def load_thresholds(path: str) -> Dict[str, float]:
    if not path or not os.path.exists(path):
        return {}
    payload = load_json(path)
    raw = payload.get("thresholds_pct", {}) if isinstance(payload, dict) else {}
    out: Dict[str, float] = {}
    for k, v in raw.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            continue
    return out


def evaluate_alerts(report_diff: Dict[str, Any], thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
    alerts: List[Dict[str, Any]] = []
    rows = report_diff.get("scenarios", []) if isinstance(report_diff, dict) else []
    for row in rows:
        sc = row.get("scenario", "?")
        metrics = row.get("metrics", {})
        for block in ("gold_final_policy", "exp_final_policy"):
            for stat in ("p50", "p95"):
                key = f"{block}.{stat}"
                limit = float(thresholds.get(key, 0.0))
                val = metrics.get(block, {}).get(stat, {})
                dp = float(val.get("delta_pct", 0.0))
                if limit > 0 and abs(dp) >= limit:
                    alerts.append({
                        "scenario": sc,
                        "metric": key,
                        "delta_pct": dp,
                        "threshold_pct": limit,
                    })
    return alerts


def to_markdown(report: Dict[str, Any], old_ver: str, new_ver: str) -> str:
    lines = []
    lines.append(f"# Economy baseline diff: {old_ver} -> {new_ver}")
    lines.append("")
    lines.append("| Scenario | Metric | Old | New | Δ abs | Δ % |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for row in report.get("scenarios", []):
        sc = row.get("scenario", "?")
        metrics = row.get("metrics", {})
        for block in ("gold_final_policy", "exp_final_policy"):
            for stat in ("p50", "p95"):
                m = metrics.get(block, {}).get(stat, {})
                lines.append(
                    "| {sc} | {metric} | {old:.2f} | {new:.2f} | {da:.2f} | {dp:.2f}% |".format(
                        sc=sc,
                        metric=f"{block}.{stat}",
                        old=float(m.get("old", 0.0)),
                        new=float(m.get("new", 0.0)),
                        da=float(m.get("delta_abs", 0.0)),
                        dp=float(m.get("delta_pct", 0.0)),
                    )
                )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Compara dos baselines versionados de Economy Lab.")
    ap.add_argument("--base-dir", default="artifacts/economy_baseline")
    ap.add_argument("--old-version", required=True)
    ap.add_argument("--new-version", required=True)
    ap.add_argument("--out-json", default="")
    ap.add_argument("--out-md", default="")
    ap.add_argument("--thresholds-file", default="tools/scenarios/economy_alert_thresholds.json")
    ap.add_argument("--fail-on-alert", action="store_true")
    args = ap.parse_args()

    old_suite_path = os.path.join(args.base_dir, args.old_version, "suite.json")
    new_suite_path = os.path.join(args.base_dir, args.new_version, "suite.json")

    if not os.path.exists(old_suite_path):
        raise SystemExit(f"[error] no existe old suite: {old_suite_path}")
    if not os.path.exists(new_suite_path):
        raise SystemExit(f"[error] no existe new suite: {new_suite_path}")

    old_suite = load_json(old_suite_path)
    new_suite = load_json(new_suite_path)
    report = {
        "meta": {
            "old_version": args.old_version,
            "new_version": args.new_version,
            "old_suite": old_suite_path,
            "new_suite": new_suite_path,
            "thresholds_file": args.thresholds_file,
        },
        "diff": compare_suites(old_suite, new_suite),
    }
    thresholds = load_thresholds(args.thresholds_file)
    alerts = evaluate_alerts(report["diff"], thresholds)
    report["thresholds_pct"] = thresholds
    report["alerts"] = alerts

    md = to_markdown(report["diff"], args.old_version, args.new_version)
    print(md)
    if alerts:
        print(f"[warn] alertas detectadas: {len(alerts)}")
        for a in alerts:
            print(
                "[alert] scenario={s} metric={m} delta={d:.2f}% threshold={t:.2f}%".format(
                    s=a["scenario"], m=a["metric"], d=float(a["delta_pct"]), t=float(a["threshold_pct"])
                )
            )
    else:
        print("[ok] sin alertas de umbral.")

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[ok] JSON diff guardado en: {args.out_json}")
    if args.out_md:
        with open(args.out_md, "w", encoding="utf-8") as f:
            f.write(md + "\n")
        print(f"[ok] Markdown diff guardado en: {args.out_md}")
    if args.fail_on_alert and alerts:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
