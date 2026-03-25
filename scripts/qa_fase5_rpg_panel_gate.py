#!/usr/bin/env python3
from pathlib import Path
import re
import math
import sys

ROOT = Path(__file__).resolve().parents[1]

CORE = ROOT / 'game/10A_RPG_PANEL_CORE_V1.rpy'
UI = ROOT / 'game/10B_RPG_PANEL_UI_V1.rpy'
PLAN_CAPS = ROOT / 'docs/PLANILLA_CAPS_TECNICAS_REGISTROS_V1.md'
PLAN_REW = ROOT / 'docs/PLANILLA_EXP_ORO_DESEMPENO_V1.md'


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def find_line(text, needle):
    for i, ln in enumerate(text.splitlines(), start=1):
        if needle in ln:
            return i
    return -1


def compute_caps(register, mode):
    blocks = [
        ("D", 0, 1, 900, 1000, 1.00),
        ("C", 2, 3, 2000, 2300, 1.00),
        ("B", 4, 5, 5000, 5500, 1.00),
        ("A", 6, 7, 12000, 13000, 1.00),
        ("S", 8, 9, 25000, 27000, 0.95),
        ("SS", 10, 29, 80000, 90000, 0.85),
        ("SSS", 30, 50, 200000, 240000, 0.75),
    ]
    reg = max(0, min(50, int(register)))
    prev_off, prev_def = 400, 450
    for name, rs, re, off_end, def_end, pvp in blocks:
        if rs <= reg <= re:
            n = re - rs + 1
            off_start = prev_off + 1
            def_start = prev_def + 1
            idx = reg - rs
            t = (idx / (n - 1)) if n > 1 else 0
            off_base = round(off_start + (off_end - off_start) * t)
            def_base = round(def_start + (def_end - def_start) * t)
            if mode == 'pvp':
                return int(round(off_base * pvp)), int(round(def_base * pvp)), name
            return int(off_base), int(def_base), name
        prev_off, prev_def = off_end, def_end
    return 200000, 240000, 'SSS'


def reward(base_exp, base_oro, player_reg, rival_reg, is_win, stars, rep):
    exp_t = {-5:0.15,-4:0.25,-3:0.40,-2:0.60,-1:0.82,0:1.00,1:1.25,2:1.55,3:1.90,4:2.30,5:2.80}
    oro_t = {-5:0.25,-4:0.40,-3:0.55,-2:0.72,-1:0.88,0:1.00,1:1.12,2:1.28,3:1.45,4:1.65,5:1.85}
    dr = max(-5, min(5, rival_reg - player_reg))
    m_des_exp = 0.70 + (0.02 * stars)
    m_des_oro = 0.80 + (0.01 * stars)
    m_res_exp = 1.00 if is_win else 0.70
    m_res_oro = 1.00 if is_win else 0.50
    if rep <= 1:
        anti = 1.0
    elif rep == 2:
        anti = 0.6
    elif rep == 3:
        anti = 0.3
    else:
        anti = 0.1
    exp = round(base_exp * exp_t[dr] * m_res_exp * m_des_exp * anti)
    oro = round(base_oro * oro_t[dr] * m_res_oro * m_des_oro * anti)
    return exp, oro


def main():
    core_t = CORE.read_text(encoding='utf-8')
    ui_t = UI.read_text(encoding='utf-8')
    caps_t = PLAN_CAPS.read_text(encoding='utf-8')
    rew_t = PLAN_REW.read_text(encoding='utf-8')

    # Function presence
    for fn in [
        'def compute_register', 'def compute_pool_total', 'def compute_stat_effects',
        'def compute_principal_bonus', 'def compute_caps_for_register',
        'def compute_consumption_at_cap', 'def compute_exp_oro_reward',
        'def compute_preview', 'def validate_panel_state'
    ]:
        assert_true(fn in core_t, f'Falta función en core: {fn}')

    for tok in ['screen rpg_panel_v1', 'screen rpg_panel_confirm_modal_v1', 'Recompensa post-combate (integración Fase 4)']:
        assert_true(tok in ui_t, f'Falta bloque en UI: {tok}')

    # Numeric checks against known plan values
    off, deff, tier = compute_caps(0, 'pve')
    assert_true((off, deff, tier) == (401, 451, 'D'), 'Reg0 PVE no coincide')
    off, deff, tier = compute_caps(10, 'pve')
    assert_true((off, deff, tier) == (25001, 27001, 'SS'), 'Reg10 PVE no coincide')
    off, deff, tier = compute_caps(35, 'pvp')
    assert_true((off, deff, tier) == (82501, 95626, 'SSS'), 'Reg35 PVP no coincide')

    # Reward checks from v1 formula examples
    exp, oro = reward(100, 60, 10, 10, True, 22, 1)
    assert_true((exp, oro) == (114, 61), 'Caso recompensa A no coincide')
    exp, oro = reward(100, 60, 10, 13, False, 22, 1)
    assert_true((exp, oro) == (152, 44), 'Caso recompensa derrota no coincide')

    # Doc anchors
    assert_true('Reg | Nivel de referencia | Tier' in caps_t, 'Planilla caps incompleta')
    assert_true('M_riesgo_exp' in rew_t and 'M_riesgo_oro' in rew_t, 'Planilla recompensa incompleta')

    print('QA Fase5 RPG Panel: OK')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        print(f'QA Fase5 RPG Panel: FAIL - {e}')
        sys.exit(1)
