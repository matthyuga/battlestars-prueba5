import json
from pathlib import Path

from tools.compare_economy_baselines import compare_suites


GOLDEN_DIR = Path(__file__).parent / "golden"


def test_compare_suites_matches_golden():
    old_suite = json.loads((GOLDEN_DIR / "suite_old.json").read_text(encoding="utf-8"))
    new_suite = json.loads((GOLDEN_DIR / "suite_new.json").read_text(encoding="utf-8"))
    expected = json.loads((GOLDEN_DIR / "diff_expected.json").read_text(encoding="utf-8"))

    got = compare_suites(old_suite, new_suite)
    assert got == expected
