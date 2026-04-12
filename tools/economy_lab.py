#!/usr/bin/env python3
"""
Economy Lab MVP (CLI)
---------------------
Simula EXP/Oro para Battlestars según:
- tier de cuenta
- modo (duelo_libre / torneo / torre)
- desempeño
- riesgo (delta de registro)
- antiabuso por repetición
- boosts por tier según política documental

Salida:
- Resumen en consola
- JSON opcional
- CSV opcional
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import dataclass
from typing import Dict, List


EXP_RISK_TABLE = {
    -5: 0.15, -4: 0.25, -3: 0.40, -2: 0.60, -1: 0.82,
     0: 1.00,  1: 1.25,  2: 1.55,  3: 1.90,  4: 2.30, 5: 2.80,
}

ORO_RISK_TABLE = {
    -5: 0.25, -4: 0.40, -3: 0.55, -2: 0.72, -1: 0.88,
     0: 1.00,  1: 1.12,  2: 1.28,  3: 1.45,  4: 1.65, 5: 1.85,
}

GOLD_BOOST_BY_TIER = {
    "C": 1.00,
    "B": 1.05,
    "A": 1.10,
    "S": 1.16,
    "SS": 1.23,
    "SSS": 1.31,
    "IV": 1.40,
}

EXP_BOOST_BY_TIER = {
    "C": 1.00,
    "B": 1.03,
    "A": 1.06,
    "S": 1.10,
    "SS": 1.14,
    "SSS": 1.19,
    "IV": 1.25,
}


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def normalize_tier(v: str) -> str:
    t = str(v or "C").strip().upper()
    return t if t in GOLD_BOOST_BY_TIER else "C"


def normalize_mode(v: str) -> str:
    m = str(v or "duelo_libre").strip().lower()
    aliases = {
        "duelo": "duelo_libre",
        "duel": "duelo_libre",
        "duel_free": "duelo_libre",
        "free_duel": "duelo_libre",
        "torneo": "torneo",
        "tournament": "torneo",
        "tower": "torre",
        "torre": "torre",
    }
    return aliases.get(m, m if m in ("duelo_libre", "torneo", "torre") else "duelo_libre")


def antiabuso_multiplier(repetition_count: int) -> float:
    rep = int(repetition_count)
    if rep <= 1:
        return 1.00
    if rep == 2:
        return 0.60
    if rep == 3:
        return 0.30
    return 0.10


def risk_multiplier(delta_register: int, for_exp: bool) -> float:
    d = int(clamp(delta_register, -5, 5))
    table = EXP_RISK_TABLE if for_exp else ORO_RISK_TABLE
    return float(table[d])


def tier_gold_boost(mode: str, tier: str) -> float:
    # Política vigente: boost de oro en Duelo Libre.
    if mode == "duelo_libre":
        return GOLD_BOOST_BY_TIER[tier]
    return 1.00


def tier_exp_boost(mode: str, tier: str) -> float:
    # Política vigente: boost de EXP en Torneo/Torre.
    if mode in ("torneo", "torre"):
        return EXP_BOOST_BY_TIER[tier]
    return 1.00


@dataclass
class SimInput:
    mode: str
    account_tier: str
    base_exp: float
    gold_min: float
    gold_max: float
    player_register: int
    rival_register: int
    is_victory: bool
    stars: int
    repetition_count: int
    eff_ec_ep: float
    eff_damage: float
    eff_block: float
    eff_survival: float
    rng_factor: float


def simulate_once(inp: SimInput) -> Dict[str, object]:
    dr = int(inp.rival_register - inp.player_register)
    anti = antiabuso_multiplier(inp.repetition_count)
    perf = float(inp.eff_ec_ep * inp.eff_damage * inp.eff_block * inp.eff_survival)

    # Componente desempeño/resultado (alineado a runtime actual de reward sim).
    stars = int(clamp(inp.stars, 0, 30))
    m_des_exp = 0.70 + (0.02 * stars)
    m_des_oro = 0.80 + (0.01 * stars)
    m_res_exp = 1.00 if inp.is_victory else 0.70
    m_res_oro = 1.00 if inp.is_victory else 0.50
    m_risk_exp = risk_multiplier(dr, for_exp=True)
    m_risk_oro = risk_multiplier(dr, for_exp=False)

    gold_base = (float(inp.gold_min) + float(inp.gold_max)) / 2.0
    exp_base = max(0.0, float(inp.base_exp))

    gold_raw_normal = gold_base * perf * inp.rng_factor * m_risk_oro * m_res_oro * m_des_oro * anti
    exp_raw_normal = exp_base * m_risk_exp * m_res_exp * m_des_exp * anti

    gold_boost = tier_gold_boost(inp.mode, inp.account_tier)
    exp_boost = tier_exp_boost(inp.mode, inp.account_tier)

    gold_raw_policy = gold_base * gold_boost * perf * inp.rng_factor * m_risk_oro * m_res_oro * m_des_oro * anti
    exp_raw_policy = exp_base * exp_boost * m_risk_exp * m_res_exp * m_des_exp * anti

    gold_final_normal = int(round(clamp(gold_raw_normal, inp.gold_min, inp.gold_max)))
    gold_final_policy = int(round(clamp(gold_raw_policy, inp.gold_min, inp.gold_max)))
    exp_final_normal = int(round(max(0.0, exp_raw_normal)))
    exp_final_policy = int(round(max(0.0, exp_raw_policy)))

    return {
        "input": {
            "mode": inp.mode,
            "account_tier": inp.account_tier,
            "base_exp": inp.base_exp,
            "gold_min": inp.gold_min,
            "gold_max": inp.gold_max,
            "player_register": inp.player_register,
            "rival_register": inp.rival_register,
            "is_victory": inp.is_victory,
            "stars": inp.stars,
            "repetition_count": inp.repetition_count,
            "eff_ec_ep": inp.eff_ec_ep,
            "eff_damage": inp.eff_damage,
            "eff_block": inp.eff_block,
            "eff_survival": inp.eff_survival,
            "rng_factor": inp.rng_factor,
        },
        "multipliers": {
            "delta_register": dr,
            "risk_exp": m_risk_exp,
            "risk_oro": m_risk_oro,
            "result_exp": m_res_exp,
            "result_oro": m_res_oro,
            "performance_exp": m_des_exp,
            "performance_oro": m_des_oro,
            "antiabuso": anti,
            "perf_product": perf,
            "tier_gold_boost": gold_boost,
            "tier_exp_boost": exp_boost,
        },
        "normal": {
            "exp_raw": exp_raw_normal,
            "exp_final": exp_final_normal,
            "gold_raw": gold_raw_normal,
            "gold_final": gold_final_normal,
        },
        "policy_boost": {
            "exp_raw": exp_raw_policy,
            "exp_final": exp_final_policy,
            "gold_raw": gold_raw_policy,
            "gold_final": gold_final_policy,
        },
        "delta": {
            "exp_abs": exp_final_policy - exp_final_normal,
            "gold_abs": gold_final_policy - gold_final_normal,
            "exp_pct": (0.0 if exp_final_normal == 0 else ((exp_final_policy / float(exp_final_normal)) - 1.0) * 100.0),
            "gold_pct": (0.0 if gold_final_normal == 0 else ((gold_final_policy / float(gold_final_normal)) - 1.0) * 100.0),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Economy Lab MVP — simulador EXP/Oro.")
    p.add_argument("--mode", default="duelo_libre", help="duelo_libre | torneo | torre")
    p.add_argument("--account-tier", default="C", help="C|B|A|S|SS|SSS|IV")
    p.add_argument("--base-exp", type=float, default=100.0)
    p.add_argument("--gold-min", type=float, default=10.0)
    p.add_argument("--gold-max", type=float, default=100.0)
    p.add_argument("--player-register", type=int, default=0)
    p.add_argument("--rival-register", type=int, default=0)
    p.add_argument("--victory", action="store_true", default=False)
    p.add_argument("--stars", type=int, default=15)
    p.add_argument("--repetition-count", type=int, default=1)
    p.add_argument("--eff-ec-ep", type=float, default=1.00)
    p.add_argument("--eff-damage", type=float, default=1.00)
    p.add_argument("--eff-block", type=float, default=1.00)
    p.add_argument("--eff-survival", type=float, default=1.00)
    p.add_argument("--rng-factor", type=float, default=1.00)

    p.add_argument("--runs", type=int, default=1, help="Cantidad de corridas para batch.")
    p.add_argument("--seed", type=int, default=42, help="Seed para batch.")
    p.add_argument("--randomize", action="store_true", help="Randomiza desempeño/rng en cada corrida batch.")
    p.add_argument("--json-out", default="", help="Ruta salida JSON opcional.")
    p.add_argument("--csv-out", default="", help="Ruta salida CSV opcional.")
    return p


def run_batch(args: argparse.Namespace) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    random.seed(args.seed)

    mode = normalize_mode(args.mode)
    tier = normalize_tier(args.account_tier)
    runs = max(1, int(args.runs))

    for _ in range(runs):
        if args.randomize:
            eff_ec_ep = random.uniform(0.85, 1.15)
            eff_damage = random.uniform(0.85, 1.15)
            eff_block = random.uniform(0.85, 1.15)
            eff_survival = random.uniform(0.85, 1.15)
            rng_factor = random.uniform(0.95, 1.05)
        else:
            eff_ec_ep = args.eff_ec_ep
            eff_damage = args.eff_damage
            eff_block = args.eff_block
            eff_survival = args.eff_survival
            rng_factor = args.rng_factor

        sim_in = SimInput(
            mode=mode,
            account_tier=tier,
            base_exp=float(args.base_exp),
            gold_min=float(min(args.gold_min, args.gold_max)),
            gold_max=float(max(args.gold_min, args.gold_max)),
            player_register=int(args.player_register),
            rival_register=int(args.rival_register),
            is_victory=bool(args.victory),
            stars=int(args.stars),
            repetition_count=int(args.repetition_count),
            eff_ec_ep=float(eff_ec_ep),
            eff_damage=float(eff_damage),
            eff_block=float(eff_block),
            eff_survival=float(eff_survival),
            rng_factor=float(rng_factor),
        )
        results.append(simulate_once(sim_in))
    return results


def print_console_summary(results: List[Dict[str, object]]) -> None:
    if not results:
        print("Sin resultados.")
        return
    first = results[0]
    inp = first["input"]
    print("=== Economy Lab MVP ===")
    print(f"mode={inp['mode']} tier={inp['account_tier']} runs={len(results)}")

    # promedios básicos
    avg_gold_normal = sum(float(r["normal"]["gold_final"]) for r in results) / float(len(results))
    avg_gold_policy = sum(float(r["policy_boost"]["gold_final"]) for r in results) / float(len(results))
    avg_exp_normal = sum(float(r["normal"]["exp_final"]) for r in results) / float(len(results))
    avg_exp_policy = sum(float(r["policy_boost"]["exp_final"]) for r in results) / float(len(results))
    avg_gold_delta_pct = sum(float(r["delta"]["gold_pct"]) for r in results) / float(len(results))
    avg_exp_delta_pct = sum(float(r["delta"]["exp_pct"]) for r in results) / float(len(results))

    print(f"gold_final avg: normal={avg_gold_normal:.2f} | policy={avg_gold_policy:.2f} | delta={avg_gold_delta_pct:.2f}%")
    print(f"exp_final  avg: normal={avg_exp_normal:.2f} | policy={avg_exp_policy:.2f} | delta={avg_exp_delta_pct:.2f}%")

    if len(results) == 1:
        print("\n--- Detalle corrida ---")
        print(json.dumps(first, ensure_ascii=False, indent=2))


def write_json(path: str, payload: Dict[str, object]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def write_csv(path: str, results: List[Dict[str, object]]) -> None:
    cols = [
        "mode", "account_tier", "gold_final_normal", "gold_final_policy", "gold_delta_pct",
        "exp_final_normal", "exp_final_policy", "exp_delta_pct", "delta_register",
        "risk_oro", "risk_exp", "antiabuso", "rng_factor", "perf_product",
    ]
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            inp = r["input"]
            mul = r["multipliers"]
            w.writerow({
                "mode": inp["mode"],
                "account_tier": inp["account_tier"],
                "gold_final_normal": r["normal"]["gold_final"],
                "gold_final_policy": r["policy_boost"]["gold_final"],
                "gold_delta_pct": round(float(r["delta"]["gold_pct"]), 4),
                "exp_final_normal": r["normal"]["exp_final"],
                "exp_final_policy": r["policy_boost"]["exp_final"],
                "exp_delta_pct": round(float(r["delta"]["exp_pct"]), 4),
                "delta_register": mul["delta_register"],
                "risk_oro": mul["risk_oro"],
                "risk_exp": mul["risk_exp"],
                "antiabuso": mul["antiabuso"],
                "rng_factor": inp["rng_factor"],
                "perf_product": round(float(mul["perf_product"]), 6),
            })


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    results = run_batch(args)

    payload = {
        "meta": {
            "tool": "economy_lab",
            "version": "v1",
            "runs": len(results),
        },
        "results": results,
    }

    print_console_summary(results)

    if args.json_out:
        write_json(args.json_out, payload)
        print(f"[ok] JSON guardado en: {args.json_out}")
    if args.csv_out:
        write_csv(args.csv_out, results)
        print(f"[ok] CSV guardado en: {args.csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
