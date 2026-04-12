#!/usr/bin/env python3
"""
Economy Dashboard (Module B - mínimo)

Genera un HTML estático a partir de:
- suite.json (baseline congelado)
- diff.json (opcional, salida de compare_economy_baselines.py)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def scenario_rows_from_suite(suite: Dict[str, Any]) -> List[Dict[str, Any]]:
    scenarios = suite.get("scenarios", {}) if isinstance(suite, dict) else {}
    rows = []
    for name in sorted(scenarios.keys()):
        sc = scenarios.get(name, {})
        agg = sc.get("aggregate", {}) if isinstance(sc, dict) else {}
        gp = agg.get("gold_final_policy", {})
        ep = agg.get("exp_final_policy", {})
        rows.append({
            "scenario": name,
            "gold_p50": float(gp.get("p50", 0.0)),
            "gold_p95": float(gp.get("p95", 0.0)),
            "exp_p50": float(ep.get("p50", 0.0)),
            "exp_p95": float(ep.get("p95", 0.0)),
        })
    return rows


def _bar(value: float, max_value: float) -> str:
    if max_value <= 0:
        w = 0
    else:
        w = int((value / max_value) * 100)
    return f"<div class='bar-wrap'><div class='bar' style='width:{w}%'></div></div><span class='bar-label'>{value:.2f}</span>"


def render_suite_section(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "<h2>Suite</h2><p>Sin datos.</p>"
    max_gold = max(r["gold_p95"] for r in rows) if rows else 1.0
    max_exp = max(r["exp_p95"] for r in rows) if rows else 1.0

    lines = ["<h2>Suite (p50/p95 por escenario)</h2>"]
    lines.append("<table><thead><tr><th>Scenario</th><th>Gold p50</th><th>Gold p95</th><th>Exp p50</th><th>Exp p95</th></tr></thead><tbody>")
    for r in rows:
        lines.append(
            "<tr>"
            f"<td>{r['scenario']}</td>"
            f"<td>{r['gold_p50']:.2f}</td>"
            f"<td>{r['gold_p95']:.2f}</td>"
            f"<td>{r['exp_p50']:.2f}</td>"
            f"<td>{r['exp_p95']:.2f}</td>"
            "</tr>"
        )
    lines.append("</tbody></table>")

    lines.append("<h3>Gold p95 por escenario</h3>")
    for r in rows:
        lines.append(f"<div class='bar-row'><span class='name'>{r['scenario']}</span>{_bar(r['gold_p95'], max_gold)}</div>")

    lines.append("<h3>Exp p95 por escenario</h3>")
    for r in rows:
        lines.append(f"<div class='bar-row'><span class='name'>{r['scenario']}</span>{_bar(r['exp_p95'], max_exp)}</div>")
    return "\n".join(lines)


def render_diff_section(diff: Dict[str, Any]) -> str:
    if not diff:
        return "<h2>Diff</h2><p>No se proporcionó diff.json.</p>"
    d = diff.get("diff", {}) if isinstance(diff, dict) else {}
    rows = d.get("scenarios", []) if isinstance(d, dict) else []
    if not rows:
        return "<h2>Diff</h2><p>Sin filas para comparar.</p>"

    out = ["<h2>Diff entre versiones</h2>"]
    out.append("<table><thead><tr><th>Scenario</th><th>Metric</th><th>Old</th><th>New</th><th>Δ abs</th><th>Δ %</th></tr></thead><tbody>")
    for row in rows:
        sc = row.get("scenario", "?")
        m = row.get("metrics", {})
        for block in ("gold_final_policy", "exp_final_policy"):
            for stat in ("p50", "p95"):
                val = m.get(block, {}).get(stat, {})
                out.append(
                    "<tr>"
                    f"<td>{sc}</td>"
                    f"<td>{block}.{stat}</td>"
                    f"<td>{float(val.get('old', 0.0)):.2f}</td>"
                    f"<td>{float(val.get('new', 0.0)):.2f}</td>"
                    f"<td>{float(val.get('delta_abs', 0.0)):.2f}</td>"
                    f"<td>{float(val.get('delta_pct', 0.0)):.2f}%</td>"
                    "</tr>"
                )
    out.append("</tbody></table>")
    return "\n".join(out)


def build_html(title: str, suite_rows: List[Dict[str, Any]], diff_json: Dict[str, Any]) -> str:
    suite_html = render_suite_section(suite_rows)
    diff_html = render_diff_section(diff_json)
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }}
    h1,h2,h3 {{ color:#93c5fd; }}
    .card {{ background:#111827; border:1px solid #1f2937; border-radius:10px; padding:16px; margin-bottom:20px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:10px; }}
    th, td {{ border-bottom:1px solid #1f2937; padding:8px; text-align:left; font-size:14px; }}
    th {{ color:#cbd5e1; }}
    .bar-row {{ display:flex; align-items:center; gap:10px; margin:8px 0; }}
    .name {{ width:90px; color:#cbd5e1; }}
    .bar-wrap {{ flex:1; background:#1f2937; border-radius:8px; height:12px; overflow:hidden; }}
    .bar {{ height:100%; background:#38bdf8; }}
    .bar-label {{ min-width:80px; text-align:right; color:#cbd5e1; font-size:13px; }}
    .muted {{ color:#94a3b8; font-size:13px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <p class="muted">Dashboard mínimo (Módulo B v0) generado desde artefactos JSON de Economy Lab.</p>
  <div class="card">{suite_html}</div>
  <div class="card">{diff_html}</div>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Genera dashboard HTML desde suite/diff de Economy Lab.")
    ap.add_argument("--suite-json", required=True, help="Ruta a suite.json (baseline congelado).")
    ap.add_argument("--diff-json", default="", help="Ruta opcional a diff JSON.")
    ap.add_argument("--out-html", default="/tmp/economy_dashboard.html", help="Ruta de salida HTML.")
    ap.add_argument("--title", default="Economy Lab Dashboard")
    args = ap.parse_args()

    suite = load_json(args.suite_json)
    diff = load_json(args.diff_json) if args.diff_json else {}
    rows = scenario_rows_from_suite(suite)
    html = build_html(args.title, rows, diff)

    out = Path(args.out_html)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"[ok] dashboard generado: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
