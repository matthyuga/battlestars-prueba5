from tools.economy_lab import (
    SimInput,
    antiabuso_multiplier,
    normalize_mode,
    normalize_tier,
    risk_multiplier,
    simulate_once,
    tier_exp_boost,
    tier_gold_boost,
)


def test_normalizers():
    assert normalize_tier("ss") == "SS"
    assert normalize_tier("unknown") == "C"
    assert normalize_mode("tower") == "torre"
    assert normalize_mode("duel") == "duelo_libre"


def test_antiabuso_curve():
    assert antiabuso_multiplier(1) == 1.0
    assert antiabuso_multiplier(2) == 0.60
    assert antiabuso_multiplier(3) == 0.30
    assert antiabuso_multiplier(7) == 0.10


def test_policy_boost_by_mode():
    assert tier_gold_boost("duelo_libre", "A") > 1.0
    assert tier_gold_boost("torneo", "A") == 1.0
    assert tier_exp_boost("torneo", "A") > 1.0
    assert tier_exp_boost("duelo_libre", "A") == 1.0


def test_simulate_once_duelo_has_gold_boost_not_exp_boost():
    inp = SimInput(
        mode="duelo_libre",
        account_tier="A",
        base_exp=100,
        gold_min=10,
        gold_max=1000,
        player_register=0,
        rival_register=0,
        is_victory=True,
        stars=15,
        repetition_count=1,
        eff_ec_ep=1.0,
        eff_damage=1.0,
        eff_block=1.0,
        eff_survival=1.0,
        rng_factor=1.0,
    )
    out = simulate_once(inp)
    assert out["policy_boost"]["gold_final"] >= out["normal"]["gold_final"]
    assert out["policy_boost"]["exp_final"] == out["normal"]["exp_final"]


def test_risk_multiplier_clamped_range():
    lo = risk_multiplier(-999, for_exp=True)
    hi = risk_multiplier(999, for_exp=True)
    assert lo == risk_multiplier(-5, for_exp=True)
    assert hi == risk_multiplier(5, for_exp=True)
