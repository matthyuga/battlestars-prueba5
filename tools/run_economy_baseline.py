#!/usr/bin/env python3
"""
Runner para congelar baseline de Economy Lab.

Genera artefactos versionados:
- suite.json (resumen de escenarios)
- <scenario>.json
- <scenario>.csv
- manifest.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone


def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def load_scenario_names(path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data.get("scenarios", {}) if isinstance(data, dict) else {}
    names = sorted([str(k) for k in scenarios.keys()])
    return names


def main() -> int:
    ap = argparse.ArgumentParser(description="Congela baseline de Economy Lab en carpeta versionada.")
    ap.add_argument("--version", required=True, help="Ej: economy_v1_2026-04-12")
    ap.add_argument("--out-dir", default="artifacts/economy_baseline", help="Directorio base de artefactos.")
    ap.add_argument("--scenario-file", default="tools/scenarios/economy_lab_profiles.json")
    ap.add_argument("--python-bin", default=sys.executable, help="Python ejecutable para invocar el CLI.")
    args = ap.parse_args()

    version = str(args.version).strip()
    target = os.path.join(args.out_dir, version)
    ensure_dir(target)

    suite_json = os.path.join(target, "suite.json")
    cmd_suite = [
        args.python_bin,
        "tools/economy_lab.py",
        "--scenario-file",
        args.scenario_file,
        "--run-all-scenarios",
        "--json-out",
        suite_json,
    ]
    rc, out, err = run_cmd(cmd_suite)
    if rc != 0:
        sys.stderr.write(out + "\n" + err + "\n")
        sys.stderr.write("[error] falló ejecución de suite.\n")
        return rc

    names = load_scenario_names(args.scenario_file)
    rows = []
    for name in names:
        out_json = os.path.join(target, f"{name}.json")
        out_csv = os.path.join(target, f"{name}.csv")
        cmd = [
            args.python_bin,
            "tools/economy_lab.py",
            "--scenario-file",
            args.scenario_file,
            "--scenario",
            name,
            "--json-out",
            out_json,
            "--csv-out",
            out_csv,
        ]
        rc2, out2, err2 = run_cmd(cmd)
        rows.append({
            "scenario": name,
            "exit_code": rc2,
            "json": out_json,
            "csv": out_csv,
        })
        if rc2 != 0:
            sys.stderr.write(out2 + "\n" + err2 + "\n")
            sys.stderr.write(f"[error] falló escenario: {name}\n")
            return rc2

    manifest = {
        "tool": "economy_lab_baseline_runner",
        "version": version,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "scenario_file": args.scenario_file,
        "suite_json": suite_json,
        "scenarios": rows,
    }
    manifest_path = os.path.join(target, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[ok] baseline congelado en: {target}")
    print(f"[ok] manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
