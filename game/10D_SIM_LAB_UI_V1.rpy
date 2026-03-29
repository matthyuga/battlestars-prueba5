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

    def sim_lab_add_actor():
        st = sim_lab_get_state()
        actors = st.get("actors", []) if isinstance(st.get("actors", []), list) else []
        idx = len(actors) + 1
        actors.append({
            "actor_id": "actor_%d" % idx,
            "actor_type": "ALPHA",
            "team": "A" if (idx % 2 == 1) else "B",
            "level": 1,
            "register": 0,
            "exp_current": 0,
            "exp_max": 100,
            "oro_current": 0,
            "stars": {
                "ofensiva": 0, "defensiva": 0, "control": 0,
                "eficiencia": 0, "tecnica": 0, "impacto": 0
            },
            "flags": {
                "eligible_rewards": True,
                "allow_level_up": True,
                "allow_inventory_rewards": True,
            },
        })
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_remove_actor(index):
        st = sim_lab_get_state()
        actors = st.get("actors", []) if isinstance(st.get("actors", []), list) else []
        i = int(index or 0)
        if len(actors) <= 1:
            return st
        if 0 <= i < len(actors):
            del actors[i]
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def _sim_lab_get_actor(index):
        st = sim_lab_get_state()
        actors = st.get("actors", []) if isinstance(st.get("actors", []), list) else []
        i = int(index or 0)
        if not (0 <= i < len(actors)):
            return st, actors, i, None
        return st, actors, i, actors[i]

    def sim_lab_shift_actor_numeric(index, key, delta, lo=0, hi=9999):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        cur = int(a.get(key, lo) or lo)
        nxt = cur + int(delta or 0)
        if nxt < lo:
            nxt = lo
        if nxt > hi:
            nxt = hi
        a[key] = nxt
        if key == "level":
            reg = nxt // 10
            if reg < 0:
                reg = 0
            if reg > 50:
                reg = 50
            a["register"] = reg
        actors[i] = a
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_set_actor_type(index, actor_type):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        t = str(actor_type or "ALPHA").upper()
        if t not in ("PLAYER", "ALPHA", "BETA", "GAMMA", "DELTA"):
            t = "ALPHA"
        a["actor_type"] = t
        actors[i] = a
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_set_actor_team(index, team):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        t = str(team or "A").upper()
        if t not in ("A", "B"):
            t = "A"
        a["team"] = t
        actors[i] = a
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_toggle_actor_eligible(index):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        flags = a.get("flags", {}) if isinstance(a.get("flags", {}), dict) else {}
        flags["eligible_rewards"] = not bool(flags.get("eligible_rewards", True))
        a["flags"] = flags
        actors[i] = a
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_shift_actor_star(index, star_key, delta):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        stars = a.get("stars", {}) if isinstance(a.get("stars", {}), dict) else {}
        cur = int(stars.get(star_key, 0) or 0)
        nxt = cur + int(delta or 0)
        if nxt < 0:
            nxt = 0
        if nxt > 5:
            nxt = 5
        stars[star_key] = nxt
        a["stars"] = stars
        actors[i] = a
        st["actors"] = actors
        S.sim_lab_state_v1 = st
        return st

    def sim_lab_run_simulation():
        st = sim_lab_get_state()
        fn = getattr(S, "run_simulation", None)
        if callable(fn):
            S.sim_lab_last_result_v1 = fn(copy.deepcopy(st))
        else:
            S.sim_lab_last_result_v1 = {
                "results": [],
                "audit": {
                    "warnings": [],
                    "errors": ["run_simulation no disponible."],
                },
            }
        return S.sim_lab_last_result_v1


label sim_lab_open:
    call screen sim_lab_v1
    return


screen sim_lab_v1():
    tag menu

    $ st = sim_lab_get_state()
    $ cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
    $ actors = st.get("actors", []) if isinstance(st.get("actors", []), list) else []
    $ last = sim_lab_last_result_v1 if isinstance(sim_lab_last_result_v1, dict) else None

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

            frame:
                xfill True
                ymaximum 380
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Actores (B4+B5)" size 24
                    hbox:
                        spacing 8
                        textbutton "+ Actor" action Function(sim_lab_add_actor)

                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 300

                        vbox:
                            spacing 10
                            for i, a in enumerate(actors):
                                $ stars = a.get("stars", {}) if isinstance(a.get("stars", {}), dict) else {}
                                $ st_total = int(stars.get("ofensiva", 0) or 0) + int(stars.get("defensiva", 0) or 0) + int(stars.get("control", 0) or 0) + int(stars.get("eficiencia", 0) or 0) + int(stars.get("tecnica", 0) or 0) + int(stars.get("impacto", 0) or 0)
                                frame:
                                    xfill True
                                    padding (8, 8)
                                    vbox:
                                        spacing 6
                                        text ("[%d] %s | Tipo: %s | Team: %s | Elig: %s" % (
                                            i,
                                            a.get("actor_id", "actor"),
                                            a.get("actor_type", "ALPHA"),
                                            a.get("team", "A"),
                                            "ON" if a.get("flags", {}).get("eligible_rewards", True) else "OFF",
                                        )) size 16
                                        hbox:
                                            spacing 8
                                            text ("Lvl %s | Reg %s | EXP %s | Oro %s" % (
                                                a.get("level", 1),
                                                a.get("register", 0),
                                                a.get("exp_current", 0),
                                                a.get("oro_current", 0),
                                            )) size 15
                                        hbox:
                                            spacing 6
                                            textbutton "PLAYER" action Function(sim_lab_set_actor_type, i, "PLAYER")
                                            textbutton "ALPHA" action Function(sim_lab_set_actor_type, i, "ALPHA")
                                            textbutton "BETA" action Function(sim_lab_set_actor_type, i, "BETA")
                                            textbutton "GAMMA" action Function(sim_lab_set_actor_type, i, "GAMMA")
                                            textbutton "DELTA" action Function(sim_lab_set_actor_type, i, "DELTA")
                                        hbox:
                                            spacing 6
                                            textbutton "Team A" action Function(sim_lab_set_actor_team, i, "A")
                                            textbutton "Team B" action Function(sim_lab_set_actor_team, i, "B")
                                            textbutton "Elig ON/OFF" action Function(sim_lab_toggle_actor_eligible, i)
                                            textbutton "Quitar" action Function(sim_lab_remove_actor, i)
                                        hbox:
                                            spacing 6
                                            textbutton "Lvl -1" action Function(sim_lab_shift_actor_numeric, i, "level", -1, 1, 500)
                                            textbutton "Lvl +1" action Function(sim_lab_shift_actor_numeric, i, "level", +1, 1, 500)
                                            textbutton "Reg -1" action Function(sim_lab_shift_actor_numeric, i, "register", -1, 0, 50)
                                            textbutton "Reg +1" action Function(sim_lab_shift_actor_numeric, i, "register", +1, 0, 50)
                                            textbutton "EXP +100" action Function(sim_lab_shift_actor_numeric, i, "exp_current", +100, 0, 9999999)
                                            textbutton "Oro +50" action Function(sim_lab_shift_actor_numeric, i, "oro_current", +50, 0, 9999999)

                                        text ("Stars total: %s/30" % st_total) size 15
                                        hbox:
                                            spacing 6
                                            textbutton "Of -" action Function(sim_lab_shift_actor_star, i, "ofensiva", -1)
                                            textbutton "Of +" action Function(sim_lab_shift_actor_star, i, "ofensiva", +1)
                                            textbutton "Def -" action Function(sim_lab_shift_actor_star, i, "defensiva", -1)
                                            textbutton "Def +" action Function(sim_lab_shift_actor_star, i, "defensiva", +1)
                                            textbutton "Ctl -" action Function(sim_lab_shift_actor_star, i, "control", -1)
                                            textbutton "Ctl +" action Function(sim_lab_shift_actor_star, i, "control", +1)
                                        hbox:
                                            spacing 6
                                            textbutton "Efi -" action Function(sim_lab_shift_actor_star, i, "eficiencia", -1)
                                            textbutton "Efi +" action Function(sim_lab_shift_actor_star, i, "eficiencia", +1)
                                            textbutton "Tec -" action Function(sim_lab_shift_actor_star, i, "tecnica", -1)
                                            textbutton "Tec +" action Function(sim_lab_shift_actor_star, i, "tecnica", +1)
                                            textbutton "Imp -" action Function(sim_lab_shift_actor_star, i, "impacto", -1)
                                            textbutton "Imp +" action Function(sim_lab_shift_actor_star, i, "impacto", +1)

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Simulación (B6)" size 24
                    hbox:
                        spacing 8
                        textbutton "Simular" action Function(sim_lab_run_simulation)
                    if last:
                        $ ac = len(last.get("results", [])) if isinstance(last.get("results", []), list) else 0
                        $ wa = len(last.get("audit", {}).get("warnings", [])) if isinstance(last.get("audit", {}).get("warnings", []), list) else 0
                        $ er = len(last.get("audit", {}).get("errors", [])) if isinstance(last.get("audit", {}).get("errors", []), list) else 0
                        text ("Última corrida: actors=%s | warnings=%s | errors=%s" % (ac, wa, er)) size 16
                    else:
                        text "Aún no se ejecutó simulación." size 16

            hbox:
                spacing 8
                textbutton "Reset request" action Function(sim_lab_reset_state)
                textbutton "Cerrar" action Return()
