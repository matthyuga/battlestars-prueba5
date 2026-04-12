import json
from pathlib import Path

from tools.generate_economy_ci_metrics import main as metrics_main


def test_generate_ci_metrics(tmp_path, monkeypatch):
    diff = {
        "meta": {"old_version": "v1", "new_version": "v2"},
        "diff": {
            "scenarios": [
                {
                    "scenario": "normal",
                    "metrics": {
                        "gold_final_policy": {
                            "p50": {"delta_pct": 5.0},
                            "p95": {"delta_pct": -7.0},
                        },
                        "exp_final_policy": {
                            "p50": {"delta_pct": 2.0},
                            "p95": {"delta_pct": 1.0},
                        },
                    },
                }
            ]
        },
        "alerts": [{"scenario": "normal", "metric": "gold_final_policy.p95"}],
    }
    diff_path = tmp_path / "diff.json"
    out_path = tmp_path / "metrics.json"
    diff_path.write_text(json.dumps(diff), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "generate_economy_ci_metrics.py",
            "--diff-json",
            str(diff_path),
            "--out-json",
            str(out_path),
        ],
    )

    rc = metrics_main()
    assert rc == 0

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["summary"]["num_scenarios"] == 1
    assert payload["summary"]["num_alerts"] == 1
    assert payload["summary"]["max_abs_delta_pct"] == 7.0
