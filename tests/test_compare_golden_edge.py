import json
from pathlib import Path

from tools.compare_economy_baselines import compare_suites


GOLDEN_DIR = Path(__file__).parent / "golden"


def test_compare_suites_edge_behavior():
    old_suite = json.loads((GOLDEN_DIR / "suite_old_edge.json").read_text(encoding="utf-8"))
    new_suite = json.loads((GOLDEN_DIR / "suite_new_edge.json").read_text(encoding="utf-8"))

    diff = compare_suites(old_suite, new_suite)

    # Solo intersección: new_only no debe aparecer.
    names = [row["scenario"] for row in diff["scenarios"]]
    assert names == ["stable_case", "zero_case"]

    zero_case = next(r for r in diff["scenarios"] if r["scenario"] == "zero_case")
    # old=0 y new>0 -> regla especial de pct_delta = 100
    assert zero_case["metrics"]["gold_final_policy"]["p50"]["delta_pct"] == 100.0
    assert zero_case["metrics"]["exp_final_policy"]["p95"]["delta_pct"] == 100.0
