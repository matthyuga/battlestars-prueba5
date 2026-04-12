#!/usr/bin/env python3
"""
Economy Toolkit (entrypoint único)

Unifica simulación/freeze/compare/dashboard para no depender de Makefile.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent


def run(cmd: list[str]) -> int:
    print("[run]", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return int(proc.returncode)


def script(name: str) -> str:
    return str(TOOLS_DIR / name)


def main() -> int:
    ap = argparse.ArgumentParser(description="Economy Toolkit - comando único para tools de economía.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("simulate", help="Ejecuta economy_lab.py con argumentos libres.")
    p_sim.add_argument("lab_args", nargs=argparse.REMAINDER, help="Argumentos para economy_lab.py")

    p_freeze = sub.add_parser("freeze", help="Congela baseline por versión.")
    p_freeze.add_argument("--version", required=True)
    p_freeze.add_argument("--base-dir", default="artifacts/economy_baseline")

    p_compare = sub.add_parser("compare", help="Compara dos baselines.")
    p_compare.add_argument("--old-version", required=True)
    p_compare.add_argument("--new-version", required=True)
    p_compare.add_argument("--base-dir", default="artifacts/economy_baseline")
    p_compare.add_argument("--thresholds-file", default="tools/scenarios/economy_alert_thresholds.json")
    p_compare.add_argument("--out-json", default="/tmp/economy_diff.json")
    p_compare.add_argument("--out-md", default="/tmp/economy_diff.md")
    p_compare.add_argument("--fail-on-alert", action="store_true")

    p_dash = sub.add_parser("dashboard", help="Genera dashboard HTML.")
    p_dash.add_argument("--base-dir", default="artifacts/economy_baseline")
    p_dash.add_argument("--old-version", required=True)
    p_dash.add_argument("--new-version", required=True)
    p_dash.add_argument("--thresholds-file", default="tools/scenarios/economy_alert_thresholds.json")
    p_dash.add_argument("--out-html", default="/tmp/economy_dashboard.html")
    p_dash.add_argument("--title", default="Economy Dashboard")

    p_cycle = sub.add_parser("cycle", help="Ejecuta freeze + compare + dashboard.")
    p_cycle.add_argument("--version", required=True, help="Nueva versión a congelar.")
    p_cycle.add_argument("--previous-version", required=True, help="Versión anterior para comparar.")
    p_cycle.add_argument("--base-dir", default="artifacts/economy_baseline")
    p_cycle.add_argument("--thresholds-file", default="tools/scenarios/economy_alert_thresholds.json")
    p_cycle.add_argument("--out-json", default="/tmp/economy_diff_cycle.json")
    p_cycle.add_argument("--out-md", default="/tmp/economy_diff_cycle.md")
    p_cycle.add_argument("--out-html", default="/tmp/economy_dashboard_cycle.html")
    p_cycle.add_argument("--fail-on-alert", action="store_true")

    args = ap.parse_args()
    py = sys.executable

    if args.cmd == "simulate":
        lab_args = list(args.lab_args)
        if lab_args and lab_args[0] == "--":
            lab_args = lab_args[1:]
        return run([py, script("economy_lab.py"), *lab_args])

    if args.cmd == "freeze":
        return run([py, script("run_economy_baseline.py"), "--version", args.version, "--out-dir", args.base_dir])

    if args.cmd == "compare":
        cmd = [
            py,
            script("compare_economy_baselines.py"),
            "--base-dir",
            args.base_dir,
            "--old-version",
            args.old_version,
            "--new-version",
            args.new_version,
            "--thresholds-file",
            args.thresholds_file,
            "--out-json",
            args.out_json,
            "--out-md",
            args.out_md,
        ]
        if args.fail_on_alert:
            cmd.append("--fail-on-alert")
        return run(cmd)

    if args.cmd == "dashboard":
        return run(
            [
                py,
                script("economy_dashboard.py"),
                "--suite-json",
                str(Path(args.base_dir) / args.new_version / "suite.json"),
                "--base-dir",
                args.base_dir,
                "--old-version",
                args.old_version,
                "--new-version",
                args.new_version,
                "--thresholds-file",
                args.thresholds_file,
                "--out-html",
                args.out_html,
                "--title",
                args.title,
            ]
        )

    if args.cmd == "cycle":
        rc = run([py, script("run_economy_baseline.py"), "--version", args.version, "--out-dir", args.base_dir])
        if rc != 0:
            return rc

        cmd_compare = [
            py,
            script("compare_economy_baselines.py"),
            "--base-dir",
            args.base_dir,
            "--old-version",
            args.previous_version,
            "--new-version",
            args.version,
            "--thresholds-file",
            args.thresholds_file,
            "--out-json",
            args.out_json,
            "--out-md",
            args.out_md,
        ]
        if args.fail_on_alert:
            cmd_compare.append("--fail-on-alert")
        rc = run(cmd_compare)
        if rc != 0:
            return rc

        return run(
            [
                py,
                script("economy_dashboard.py"),
                "--suite-json",
                str(Path(args.base_dir) / args.version / "suite.json"),
                "--base-dir",
                args.base_dir,
                "--old-version",
                args.previous_version,
                "--new-version",
                args.version,
                "--thresholds-file",
                args.thresholds_file,
                "--out-html",
                args.out_html,
                "--title",
                "Economy Dashboard " + args.version,
            ]
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
