# ===============================================================
# 10D_SIM_LAB_UI_V1.rpy
# Fase B Incremento 1 (B1 + B2 + B3)
# - EntryPoint + UI base
# - Estado local del request
# - Editor modo/ganador/config
# ===============================================================

default sim_lab_state_v1 = {}
default sim_lab_last_result_v1 = None

init -870 python:
    import copy
    import renpy.store as S

    def sim_lab_clone_request(req):
        return copy.deepcopy(req if isinstance(req, dict) else {})

    def sim_lab_get_state():
        st = getattr(S, "sim_lab_state_v1", None)
        if not isinstance(st, dict) or len(st) == 0:
            fn = getattr(S, "sim_build_min_request", None)
            if callable(fn):
                st = fn()
            else:
                st = {
                    "sim_contract_version": "v1",
                    "simulation_id": "sim_lab_fallback",
                    "mode": "1v1",
                    "source": "lab_manual",
                    "event_type": "draw",
                    "winner_team": "DRAW",
                    "actors": [],
                    "config": {
                        "preset": "medium_v2",
                        "allow_mid_battle_grants": True,
                        "repetition_count": 1,
                        "multi_factor_enabled": True,
                    },
                }
            S.sim_lab_state_v1 = sim_lab_clone_request(st)
        return S.sim_lab_state_v1

    def sim_lab_reset_state():
        fn = getattr(S, "sim_build_min_request", None)
        if callable(fn):
            S.sim_lab_state_v1 = sim_lab_clone_request(fn())
        else:
            S.sim_lab_state_v1 = {
                "sim_contract_version": "v1",
                "simulation_id": "sim_lab_fallback",
                "mode": "1v1",
                "source": "lab_manual",
                "event_type": "draw",
                "winner_team": "DRAW",
                "actors": [],
                "config": {
                    "preset": "medium_v2",
                    "allow_mid_battle_grants": True,
                    "repetition_count": 1,
                    "multi_factor_enabled": True,
                },
            }
        S.sim_lab_last_result_v1 = None
        return S.sim_lab_state_v1

    def _sim_lab_set_root(key, value):
        st = sim_lab_get_state()
        st[str(key)] = value
        S.sim_lab_state_v1 = st
        return st

    def _sim_lab_set_config(key, value):
        st = sim_lab_get_state()
        cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
        cfg[str(key)] = value
        st["config"] = cfg
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_set_mode(mode):
        m = str(mode or "1v1")
        if m not in ("1v1", "2v1", "1v2", "2v2", "custom"):
            m = "1v1"
        return _sim_lab_set_root("mode", m)

    def sim_lab_set_winner(team):
        t = str(team or "DRAW").upper()
        if t not in ("A", "B", "DRAW"):
            t = "DRAW"
        return _sim_lab_set_root("winner_team", t)

    def sim_lab_set_event_type(ev):
        e = str(ev or "draw")
        if e not in ("victory", "defeat", "draw", "conditional_gain"):
            e = "draw"
        return _sim_lab_set_root("event_type", e)

    def sim_lab_set_source(src):
        s = str(src or "lab_manual")
        if s not in ("battle_end", "mid_battle_event", "lab_manual"):
            s = "lab_manual"
        return _sim_lab_set_root("source", s)

    def sim_lab_toggle_multi_factor():
        st = sim_lab_get_state()
        cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
        cur = bool(cfg.get("multi_factor_enabled", True))
        return _sim_lab_set_config("multi_factor_enabled", (not cur))

    def sim_lab_toggle_mid_battle_grants():
        st = sim_lab_get_state()
        cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
        cur = bool(cfg.get("allow_mid_battle_grants", True))
        return _sim_lab_set_config("allow_mid_battle_grants", (not cur))

    def sim_lab_shift_repetition(delta):
        st = sim_lab_get_state()
        cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
        cur = int(cfg.get("repetition_count", 1) or 1)
        nxt = cur + int(delta or 0)
        if nxt < 1:
            nxt = 1
        if nxt > 10:
            nxt = 10
        return _sim_lab_set_config("repetition_count", nxt)

    def sim_lab_set_preset(preset):
        p = str(preset or "medium_v2")
        return _sim_lab_set_config("preset", p)


label sim_lab_open:
    call screen sim_lab_v1
    return


screen sim_lab_v1():
    tag menu

    $ st = sim_lab_get_state()
    $ cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}

    frame:
        xfill True
        yfill True
        padding (20, 20)

        vbox:
            spacing 10

            text "SIM LAB V1 — Incremento 1 (B1+B2+B3)" size 34
            text "Contrato: [st.get('sim_contract_version', 'v1')] | Simulation ID: [st.get('simulation_id', 'sim_unknown')]" size 18

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Editor principal" size 24

                    text "Mode actual: [st.get('mode', '1v1')]" size 18
                    hbox:
                        spacing 8
                        textbutton "1v1" action Function(sim_lab_set_mode, "1v1")
                        textbutton "2v1" action Function(sim_lab_set_mode, "2v1")
                        textbutton "1v2" action Function(sim_lab_set_mode, "1v2")
                        textbutton "2v2" action Function(sim_lab_set_mode, "2v2")
                        textbutton "Custom" action Function(sim_lab_set_mode, "custom")

                    text "Winner Team: [st.get('winner_team', 'DRAW')]" size 18
                    hbox:
                        spacing 8
                        textbutton "A" action Function(sim_lab_set_winner, "A")
                        textbutton "B" action Function(sim_lab_set_winner, "B")
                        textbutton "DRAW" action Function(sim_lab_set_winner, "DRAW")

                    text "Event Type: [st.get('event_type', 'draw')]" size 18
                    hbox:
                        spacing 8
                        textbutton "victory" action Function(sim_lab_set_event_type, "victory")
                        textbutton "defeat" action Function(sim_lab_set_event_type, "defeat")
                        textbutton "draw" action Function(sim_lab_set_event_type, "draw")
                        textbutton "conditional_gain" action Function(sim_lab_set_event_type, "conditional_gain")

                    text "Source: [st.get('source', 'lab_manual')]" size 18
                    hbox:
                        spacing 8
                        textbutton "lab_manual" action Function(sim_lab_set_source, "lab_manual")
                        textbutton "battle_end" action Function(sim_lab_set_source, "battle_end")
                        textbutton "mid_battle_event" action Function(sim_lab_set_source, "mid_battle_event")

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Config" size 24
                    text "Preset: [cfg.get('preset', 'medium_v2')] | Repetition: [cfg.get('repetition_count', 1)]" size 18
                    text "multi_factor_enabled: [('ON' if cfg.get('multi_factor_enabled', True) else 'OFF')] | allow_mid_battle_grants: [('ON' if cfg.get('allow_mid_battle_grants', True) else 'OFF')]" size 18
                    hbox:
                        spacing 8
                        textbutton "Preset medium_v2" action Function(sim_lab_set_preset, "medium_v2")
                        textbutton "Rep -1" action Function(sim_lab_shift_repetition, -1)
                        textbutton "Rep +1" action Function(sim_lab_shift_repetition, +1)
                        textbutton "Toggle m_multi" action Function(sim_lab_toggle_multi_factor)
                        textbutton "Toggle mid grants" action Function(sim_lab_toggle_mid_battle_grants)

            hbox:
                spacing 8
                textbutton "Reset request" action Function(sim_lab_reset_state)
                textbutton "Cerrar" action Return()

            text "Nota: B6 integrará el botón Simular y panel de resultados." size 16 color "#9ca3af"
