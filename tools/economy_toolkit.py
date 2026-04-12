#!/usr/bin/env python3
"""Economy Toolkit (entrypoint único).

Fase E:
- wizard interactivo para perfiles no técnicos,
- profiles cargables por nombre,
- bundle de reportes (diff + dashboard + manifest).
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


IS_FROZEN = bool(getattr(sys, "frozen", False))
if IS_FROZEN:
    cwd_tools = Path.cwd() / "tools"
    bundled_root = Path(getattr(sys, "_MEIPASS", Path.cwd()))
    bundled_tools = bundled_root / "tools"
    TOOLS_DIR = cwd_tools if cwd_tools.exists() else bundled_tools
    REPO_ROOT = TOOLS_DIR.parent if TOOLS_DIR.name == "tools" else Path.cwd()
else:
    TOOLS_DIR = Path(__file__).resolve().parent
    REPO_ROOT = TOOLS_DIR.parent
PROFILES_DIR = TOOLS_DIR / "profiles"


def run(cmd: list[str]) -> int:
    print("[run]", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return int(proc.returncode)


def script(name: str) -> str:
    return str(TOOLS_DIR / name)


def load_profile(name: str) -> Dict[str, Any]:
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        raise SystemExit(f"[error] profile no existe: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_profiles() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def run_freeze(py: str, version: str, base_dir: str) -> int:
    return run([py, script("run_economy_baseline.py"), "--version", version, "--out-dir", base_dir])


def run_compare(py: str, base_dir: str, old_version: str, new_version: str, thresholds_file: str, out_json: str, out_md: str, fail_on_alert: bool) -> int:
    cmd = [
        py,
        script("compare_economy_baselines.py"),
        "--base-dir",
        base_dir,
        "--old-version",
        old_version,
        "--new-version",
        new_version,
        "--thresholds-file",
        thresholds_file,
        "--out-json",
        out_json,
        "--out-md",
        out_md,
    ]
    if fail_on_alert:
        cmd.append("--fail-on-alert")
    return run(cmd)


def run_dashboard(py: str, base_dir: str, old_version: str, new_version: str, thresholds_file: str, out_html: str, title: str) -> int:
    return run(
        [
            py,
            script("economy_dashboard.py"),
            "--suite-json",
            str(Path(base_dir) / new_version / "suite.json"),
            "--base-dir",
            base_dir,
            "--old-version",
            old_version,
            "--new-version",
            new_version,
            "--thresholds-file",
            thresholds_file,
            "--out-html",
            out_html,
            "--title",
            title,
        ]
    )


def build_bundle(bundle_dir: str, bundle_name: str, old_version: str, new_version: str, diff_json: str, diff_md: str, dashboard_html: str) -> Path:
    root = Path(bundle_dir)
    target = root / bundle_name
    target.mkdir(parents=True, exist_ok=True)

    src_diff_json = Path(diff_json)
    src_diff_md = Path(diff_md)
    src_dashboard = Path(dashboard_html)

    if src_diff_json.exists():
        shutil.copy2(src_diff_json, target / "diff.json")
    if src_diff_md.exists():
        shutil.copy2(src_diff_md, target / "diff.md")
    if src_dashboard.exists():
        shutil.copy2(src_dashboard, target / "dashboard.html")

    manifest = {
        "tool": "economy_toolkit_bundle",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "old_version": old_version,
        "new_version": new_version,
        "artifacts": {
            "diff_json": "diff.json" if src_diff_json.exists() else None,
            "diff_md": "diff.md" if src_diff_md.exists() else None,
            "dashboard_html": "dashboard.html" if src_dashboard.exists() else None,
        },
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] report bundle generado: {target}")
    return target


def run_cycle_and_bundle(py: str, version: str, previous_version: str, base_dir: str, thresholds_file: str, out_json: str, out_md: str, out_html: str, title: str, fail_on_alert: bool, bundle_dir: str, bundle_name: str) -> int:
    rc = run_freeze(py, version, base_dir)
    if rc != 0:
        return rc
    rc = run_compare(py, base_dir, previous_version, version, thresholds_file, out_json, out_md, fail_on_alert)
    if rc != 0:
        return rc
    rc = run_dashboard(py, base_dir, previous_version, version, thresholds_file, out_html, title)
    if rc != 0:
        return rc
    build_bundle(bundle_dir, bundle_name, previous_version, version, out_json, out_md, out_html)
    return 0


def prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val or default


def prompt_yes_no(msg: str, default_yes: bool = False) -> bool:
    default = "y" if default_yes else "n"
    val = prompt(msg + " (y/n)", default=default).lower()
    return val.startswith("y")


def run_wizard(py: str) -> int:
    print("=== Economy Toolkit Wizard ===")
    print("1) Ejecutar profile")
    print("2) Flujo guiado cycle + bundle")
    choice = prompt("Elegí opción", "1")

    if choice == "1":
        names = list_profiles()
        if not names:
            print("[error] no hay profiles en tools/profiles")
            return 1
        print("Profiles disponibles:")
        for idx, name in enumerate(names, 1):
            print(f"  {idx}) {name}")
        sel = prompt("Número de profile", "1")
        try:
            picked = names[max(0, int(sel) - 1)]
        except Exception:
            picked = names[0]
        profile = load_profile(picked)

        version = prompt("Nueva versión", str(profile.get("version", "economy_v_next")))
        previous_version = prompt("Versión previa", str(profile.get("previous_version", "economy_v_prev")))
        base_dir = str(profile.get("base_dir", "artifacts/economy_baseline"))
        thresholds_file = str(profile.get("thresholds_file", "tools/scenarios/economy_alert_thresholds.json"))
        title = str(profile.get("title", f"Economy Dashboard {version}"))
        fail_on_alert = bool(profile.get("fail_on_alert", False))
        bundle_dir = str(profile.get("bundle_dir", "artifacts/economy_reports"))
        bundle_name = prompt("Nombre bundle", f"{previous_version}_to_{version}")

        out_json = str(Path("/tmp") / f"economy_diff_{previous_version}_{version}.json")
        out_md = str(Path("/tmp") / f"economy_diff_{previous_version}_{version}.md")
        out_html = str(Path("/tmp") / f"economy_dashboard_{version}.html")
        return run_cycle_and_bundle(py, version, previous_version, base_dir, thresholds_file, out_json, out_md, out_html, title, fail_on_alert, bundle_dir, bundle_name)

    version = prompt("Nueva versión", "economy_v_next")
    previous_version = prompt("Versión previa", "economy_v_prev")
    base_dir = prompt("Base dir", "artifacts/economy_baseline")
    thresholds_file = prompt("Thresholds file", "tools/scenarios/economy_alert_thresholds.json")
    fail_on_alert = prompt_yes_no("¿Activar fail-on-alert?", default_yes=False)
    bundle_dir = prompt("Directorio bundles", "artifacts/economy_reports")
    bundle_name = prompt("Nombre bundle", f"{previous_version}_to_{version}")
    title = prompt("Título dashboard", f"Economy Dashboard {version}")

    out_json = str(Path("/tmp") / f"economy_diff_{previous_version}_{version}.json")
    out_md = str(Path("/tmp") / f"economy_diff_{previous_version}_{version}.md")
    out_html = str(Path("/tmp") / f"economy_dashboard_{version}.html")
    return run_cycle_and_bundle(py, version, previous_version, base_dir, thresholds_file, out_json, out_md, out_html, title, fail_on_alert, bundle_dir, bundle_name)



def run_doctor() -> int:
    checks = {
        "scenarios": (TOOLS_DIR / "scenarios" / "economy_lab_profiles.json").exists(),
        "thresholds": (TOOLS_DIR / "scenarios" / "economy_alert_thresholds.json").exists(),
        "profiles_dir": PROFILES_DIR.exists(),
        "balance_profile": (PROFILES_DIR / "balance_default.json").exists(),
        "release_profile": (PROFILES_DIR / "release_candidate.json").exists(),
    }
    failed = [k for k, ok in checks.items() if not ok]
    for k, ok in checks.items():
        print(f"[{'ok' if ok else 'fail'}] {k}")
    if failed:
        print("[error] doctor detectó faltantes:", ", ".join(failed))
        return 2
    print("[ok] doctor: entorno mínimo listo.")
    return 0

def main() -> int:
    ap = argparse.ArgumentParser(description="Economy Toolkit - comando único para tools de economía.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_sim = sub.add_parser("simulate", help="Ejecuta economy_lab.py con argumentos libres.")
    p_sim.add_argument("lab_args", nargs=argparse.REMAINDER, help="Argumentos para economy_lab.py")

    p_profile_list = sub.add_parser("profile-list", help="Lista profiles disponibles en tools/profiles.")

    p_run_profile = sub.add_parser("run-profile", help="Ejecuta cycle+bundle a partir de un profile.")
    p_run_profile.add_argument("--name", required=True, help="Nombre profile (sin .json).")
    p_run_profile.add_argument("--version", required=True)
    p_run_profile.add_argument("--previous-version", required=True)

    p_wizard = sub.add_parser("wizard", help="Wizard interactivo para flujo no técnico.")

    p_doctor = sub.add_parser("doctor", help="Chequeo rápido de archivos/perfiles requeridos.")

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

    p_bundle = sub.add_parser("bundle", help="Empaqueta bundle (diff + dashboard + manifest).")
    p_bundle.add_argument("--old-version", required=True)
    p_bundle.add_argument("--new-version", required=True)
    p_bundle.add_argument("--diff-json", required=True)
    p_bundle.add_argument("--diff-md", required=True)
    p_bundle.add_argument("--dashboard-html", required=True)
    p_bundle.add_argument("--bundle-dir", default="artifacts/economy_reports")
    p_bundle.add_argument("--bundle-name", default="")

    p_cycle = sub.add_parser("cycle", help="Ejecuta freeze + compare + dashboard (+bundle opcional).")
    p_cycle.add_argument("--version", required=True, help="Nueva versión a congelar.")
    p_cycle.add_argument("--previous-version", required=True, help="Versión anterior para comparar.")
    p_cycle.add_argument("--base-dir", default="artifacts/economy_baseline")
    p_cycle.add_argument("--thresholds-file", default="tools/scenarios/economy_alert_thresholds.json")
    p_cycle.add_argument("--out-json", default="/tmp/economy_diff_cycle.json")
    p_cycle.add_argument("--out-md", default="/tmp/economy_diff_cycle.md")
    p_cycle.add_argument("--out-html", default="/tmp/economy_dashboard_cycle.html")
    p_cycle.add_argument("--fail-on-alert", action="store_true")
    p_cycle.add_argument("--title", default="Economy Dashboard")
    p_cycle.add_argument("--bundle-dir", default="")
    p_cycle.add_argument("--bundle-name", default="")

    args = ap.parse_args()
    py = sys.executable
    if IS_FROZEN:
        py = shutil.which("python") or shutil.which("py") or sys.executable

    if args.cmd == "simulate":
        lab_args = list(args.lab_args)
        if lab_args and lab_args[0] == "--":
            lab_args = lab_args[1:]
        return run([py, script("economy_lab.py"), *lab_args])

    if args.cmd == "profile-list":
        names = list_profiles()
        if not names:
            print("[warn] no se encontraron profiles en tools/profiles")
            return 0
        for n in names:
            print(n)
        return 0

    if args.cmd == "run-profile":
        profile = load_profile(args.name)
        base_dir = str(profile.get("base_dir", "artifacts/economy_baseline"))
        thresholds_file = str(profile.get("thresholds_file", "tools/scenarios/economy_alert_thresholds.json"))
        title = str(profile.get("title", "Economy Dashboard"))
        fail_on_alert = bool(profile.get("fail_on_alert", False))
        bundle_dir = str(profile.get("bundle_dir", "artifacts/economy_reports"))
        bundle_name = f"{args.previous_version}_to_{args.version}"
        out_json = str(Path("/tmp") / f"economy_diff_{args.previous_version}_{args.version}.json")
        out_md = str(Path("/tmp") / f"economy_diff_{args.previous_version}_{args.version}.md")
        out_html = str(Path("/tmp") / f"economy_dashboard_{args.version}.html")
        return run_cycle_and_bundle(py, args.version, args.previous_version, base_dir, thresholds_file, out_json, out_md, out_html, title, fail_on_alert, bundle_dir, bundle_name)

    if args.cmd == "wizard":
        return run_wizard(py)

    if args.cmd == "doctor":
        return run_doctor()

    if args.cmd == "freeze":
        return run_freeze(py, args.version, args.base_dir)

    if args.cmd == "compare":
        return run_compare(py, args.base_dir, args.old_version, args.new_version, args.thresholds_file, args.out_json, args.out_md, args.fail_on_alert)

    if args.cmd == "dashboard":
        return run_dashboard(py, args.base_dir, args.old_version, args.new_version, args.thresholds_file, args.out_html, args.title)

    if args.cmd == "bundle":
        name = args.bundle_name or f"{args.old_version}_to_{args.new_version}"
        build_bundle(args.bundle_dir, name, args.old_version, args.new_version, args.diff_json, args.diff_md, args.dashboard_html)
        return 0

    if args.cmd == "cycle":
        rc = run_cycle_and_bundle(
            py,
            args.version,
            args.previous_version,
            args.base_dir,
            args.thresholds_file,
            args.out_json,
            args.out_md,
            args.out_html,
            args.title,
            args.fail_on_alert,
            args.bundle_dir or "artifacts/economy_reports",
            args.bundle_name or f"{args.previous_version}_to_{args.version}",
        )
        return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
