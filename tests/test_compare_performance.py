import time

from tools.compare_economy_baselines import compare_suites


def _suite(n: int, factor: float = 1.0):
    scenarios = {}
    for i in range(n):
        base = float(100 + i)
        scenarios[f"s{i:04d}"] = {
            "aggregate": {
                "gold_final_policy": {"p50": base * factor, "p95": (base + 50.0) * factor},
                "exp_final_policy": {"p50": (base / 2.0) * factor, "p95": (base / 2.0 + 30.0) * factor},
            }
        }
    return {"scenarios": scenarios}


def test_compare_suites_performance_smoke():
    old_suite = _suite(400, factor=1.0)
    new_suite = _suite(400, factor=1.03)

    t0 = time.perf_counter()
    out = compare_suites(old_suite, new_suite)
    dt = time.perf_counter() - t0

    assert len(out["scenarios"]) == 400
    assert dt < 1.5, f"compare_suites demasiado lento: {dt:.3f}s"
