#!/usr/bin/env python3
import sys
import types
from pathlib import Path
import textwrap


def _bootstrap_facade():
    repo = Path(__file__).resolve().parents[1]
    src = (repo / "game/01B_BATTLE_STATE_FACADE.rpy").read_text(encoding="utf-8-sig")
    marker = "init -989 python:\n"
    idx = src.find(marker)
    if idx < 0:
        raise RuntimeError("No se encontró bloque init python en facade")
    code = src[idx + len(marker):]
    code = textwrap.dedent(code)

    renpy_mod = types.ModuleType("renpy")
    store_mod = types.ModuleType("renpy.store")

    def _log(_msg):
        return None

    renpy_mod.log = _log
    renpy_mod.store = store_mod

    sys.modules["renpy"] = renpy_mod
    sys.modules["renpy.store"] = store_mod

    # Defaults mínimos esperados por el facade
    store_mod.battle_player_id = "Harribel"
    store_mod.battle_enemy_id = "Hollow"
    store_mod.player_hp = 100
    store_mod.enemy_hp = 100
    store_mod.battle_hp_player_max = 100
    store_mod.battle_hp_enemy_max = 100
    store_mod.player_reiatsu = 0
    store_mod.player_energy = 0
    store_mod.enemy_reiatsu = 0
    store_mod.enemy_energy = 0
    store_mod.battle_turn_owner = "player"
    store_mod._last_player_direct_damage = 0
    store_mod.enemy_direct_pending_damage = 0
    store_mod._captured_logs = []

    def _safe_battle_log_add(text, color=None, border=None):
        store_mod._captured_logs.append(str(text))

    store_mod.safe_battle_log_add = _safe_battle_log_add
    store_mod.battle_log_add = _safe_battle_log_add

    def _get_character(char_id):
        return {
            "id": str(char_id),
            "race": "human",
            "Reiatsu": 0,
            "Energy": 0,
            "coating_cover": 0,
            "coating_durability": 0,
        }

    store_mod.get_character = _get_character

    env = {}
    exec(code, env, env)
    return store_mod


def _expect(name, condition, details=""):
    if condition:
        print(f"[OK] {name}")
        return True
    print(f"[FAIL] {name} :: {details}")
    return False


def _check_space_invariant(S, keys):
    for k in list(keys or []):
        ss = S.bs_get_unit_stamina_shadow(k)
        st = int(ss.get("stamina_current", 0) or 0)
        sh = int(ss.get("shadow_current", 0) or 0)
        miss = int(ss.get("missing_hp", 0) or 0)
        if st + sh > miss:
            return False, f"{k}: stamina+shadow={st + sh} > missing_hp={miss}"
    return True, ""


def case_absorb_and_overflow(S):
    S._captured_logs[:] = []
    S.bs_init_single_teams(player_hp=7000, player_max_hp=10000, enemy_hp=10000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("player:0", stamina_current=3000, stamina_cap=10000, stamina_enabled=True)
    r = S.bs_apply_damage_to_unit_key("player:0", 5000)
    st = S.bs_get_unit_stamina_shadow("player:0")
    logs_ok = (
        len(S._captured_logs) >= 3
        and S._captured_logs[0].startswith("Estamina:")
        and S._captured_logs[1].startswith("HP:")
        and S._captured_logs[2].startswith("HP genera")
    )
    return _expect(
        "coating->stamina->hp (absorbe + overflow)",
        (
            r.get("hp_after") == 5000
            and st.get("stamina_current") == 2000
            and r.get("stamina", {}).get("overflow_to_hp") == 2000
            and r.get("stamina", {}).get("gain") == 2000
            and logs_ok
            and _check_space_invariant(S, ["player:0"])[0]
        ),
        details=f"hp_after={r.get('hp_after')} st={st.get('stamina_current')} overflow={r.get('stamina', {}).get('overflow_to_hp')} logs={S._captured_logs[:3]}",
    )


def case_ko_gate(S):
    S.bs_init_single_teams(player_hp=3000, player_max_hp=3000, enemy_hp=10000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("player:0", stamina_current=2000, stamina_cap=3000, stamina_enabled=True)
    r = S.bs_apply_damage_to_unit_key("player:0", 6000)
    st = S.bs_get_unit_stamina_shadow("player:0")
    return _expect(
        "KO gate (sin generación)",
        r.get("hp_after") == 0 and r.get("died") is True and st.get("stamina_current") == 0 and r.get("stamina", {}).get("gain") == 0,
        details=f"hp_after={r.get('hp_after')} died={r.get('died')} st={st.get('stamina_current')} gain={r.get('stamina', {}).get('gain')}",
    )


def case_survive_gain_enabled(S):
    S.bs_init_single_teams(player_hp=4001, player_max_hp=6001, enemy_hp=10000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("player:0", stamina_current=2000, stamina_cap=4001, stamina_enabled=True)
    r = S.bs_apply_damage_to_unit_key("player:0", 6000)
    st = S.bs_get_unit_stamina_shadow("player:0")
    return _expect(
        "sobrevive por 1 HP y genera estamina",
        r.get("hp_after") == 1 and r.get("stamina", {}).get("gain") > 0 and st.get("stamina_current") == r.get("stamina", {}).get("after"),
        details=f"hp_after={r.get('hp_after')} gain={r.get('stamina', {}).get('gain')} st={st.get('stamina_current')}",
    )


def case_no_gain_if_disabled(S):
    S.bs_init_single_teams(player_hp=9000, player_max_hp=10000, enemy_hp=10000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("player:0", stamina_current=0, stamina_cap=10000, stamina_enabled=False)
    r = S.bs_apply_damage_to_unit_key("player:0", 1000)
    st = S.bs_get_unit_stamina_shadow("player:0")
    return _expect(
        "sin stamina_enabled no hay generación",
        r.get("hp_after") == 8000 and r.get("stamina", {}).get("gain") == 0 and st.get("stamina_current") == 0,
        details=f"hp_after={r.get('hp_after')} gain={r.get('stamina', {}).get('gain')} st={st.get('stamina_current')}",
    )


def case_shadow_applied_to_enemy_blocks_target(S):
    S._captured_logs[:] = []
    S.bs_init_single_teams(player_hp=9000, player_max_hp=10000, enemy_hp=10000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow(
        "player:0",
        shadow_active=True,
        shadow_current=1500,
        shadow_cap=10000,
        shadow_target_mode="applied_to_enemy",
    )
    S.bs_set_unit_stamina_shadow("enemy:0", stamina_current=0, stamina_cap=10000, stamina_enabled=True, shadow_active=False)
    r = S.bs_apply_damage_to_unit_key("enemy:0", 1000, source_key="player:0")
    return _expect(
        "shadow applied_to_enemy bloquea free_space rival",
        (
            r.get("hp_after") == 9000
            and r.get("stamina", {}).get("gain") == 0
            and r.get("space", {}).get("blocked_by_shadow") == 1000
            and r.get("shadow", {}).get("source_effective_for_block") == 1000
            and r.get("shadow", {}).get("local_effective_for_block") == 0
            and any(str(x).startswith("Efecto aplicado:") for x in list(S._captured_logs))
        ),
        details=f"hp_after={r.get('hp_after')} gain={r.get('stamina', {}).get('gain')} blocked={r.get('space', {}).get('blocked_by_shadow')} shadow={r.get('shadow', {})} logs={S._captured_logs}",
    )


def case_2v2_applied_shadow_and_invariant(S):
    S.bs_init_teams(
        player_units=[
            {"char_id": "P1", "hp": 10000, "max_hp": 10000},
            {"char_id": "P2", "hp": 9000, "max_hp": 10000},
        ],
        enemy_units=[
            {"char_id": "E1", "hp": 10000, "max_hp": 10000},
            {"char_id": "E2", "hp": 10000, "max_hp": 10000},
        ],
    )
    S.bs_set_unit_stamina_shadow("player:1", shadow_active=True, shadow_current=1200, shadow_cap=10000, shadow_target_mode="applied_to_enemy")
    S.bs_set_unit_stamina_shadow("enemy:1", stamina_current=0, stamina_cap=10000, stamina_enabled=True, shadow_active=False)
    r = S.bs_apply_damage_to_unit_key("enemy:1", 1000, source_key="player:1")
    inv_ok, inv_msg = _check_space_invariant(S, ["player:0", "player:1", "enemy:0", "enemy:1"])
    return _expect(
        "2v2 mantiene semántica + invariante espacial",
        (
            r.get("target_key") == "enemy:1"
            and r.get("space", {}).get("blocked_by_shadow") >= 1000
            and inv_ok
        ),
        details=f"target={r.get('target_key')} blocked={r.get('space', {}).get('blocked_by_shadow')} inv={inv_msg}",
    )


def case_effect_stamina_drain_target(S):
    S.bs_init_single_teams(player_hp=10000, player_max_hp=10000, enemy_hp=9000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("enemy:0", stamina_current=800, stamina_cap=10000, stamina_enabled=True)
    r = S.bs_apply_advanced_resource_effect("stamina_drain_target", source_key="player:0", target_key="enemy:0", magnitude=500)
    st = S.bs_get_unit_stamina_shadow("enemy:0")
    return _expect(
        "effect stamina_drain_target consume rival",
        bool(r.get("ok", False)) and int(r.get("drained", 0) or 0) == 500 and int(st.get("stamina_current", 0) or 0) == 300,
        details=f"result={r} enemy_stamina={st}",
    )


def case_effect_stamina_target_to_hp_self(S):
    S.bs_init_single_teams(player_hp=7000, player_max_hp=10000, enemy_hp=9000, enemy_max_hp=10000)
    S.bs_set_unit_stamina_shadow("enemy:0", stamina_current=900, stamina_cap=10000, stamina_enabled=True)
    r = S.bs_apply_advanced_resource_effect("stamina_target_to_hp_self", source_key="player:0", target_key="enemy:0", magnitude=800)
    src = S.bs_get_unit_by_key("player:0")
    tgt = S.bs_get_unit_stamina_shadow("enemy:0")
    return _expect(
        "effect stamina_target_to_hp_self drena y cura",
        bool(r.get("ok", False)) and int(r.get("drained", 0) or 0) == 800 and int(r.get("healed", 0) or 0) == 800 and int(src.get("hp", 0) or 0) == 7800 and int(tgt.get("stamina_current", 0) or 0) == 100,
        details=f"result={r} source={src} target={tgt}",
    )


def main():
    S = _bootstrap_facade()
    checks = [
        case_absorb_and_overflow(S),
        case_ko_gate(S),
        case_survive_gain_enabled(S),
        case_no_gain_if_disabled(S),
        case_shadow_applied_to_enemy_blocks_target(S),
        case_2v2_applied_shadow_and_invariant(S),
        case_effect_stamina_drain_target(S),
        case_effect_stamina_target_to_hp_self(S),
    ]
    ok = all(checks)
    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
