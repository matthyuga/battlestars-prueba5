# ===============================================================
# 10D_SIM_LAB_UI_V1.rpy
# Fase B Incremento 3 (B7 + B8 + B9 + B10 + B11)
# - Resultados por actor + auditoría/idempotencia
# - Carga de fixtures + export QA
# - Smoke checklist
# ===============================================================

default sim_lab_state_v1 = {}
default sim_lab_last_result_v1 = None
default sim_lab_export_text_v1 = ""
default sim_lab_smoke_results_v1 = []
default sim_lab_mid_battle_rows_v1 = []

init -870 python:
    import copy
    import json
    import renpy.store as S

    def _sim_lab_to_int(v, default=0):
        try:
            return int(v)
        except Exception:
            return int(default or 0)

    def sim_lab_make_actor(idx=1):
        n = int(idx or 1)
        if n < 1:
            n = 1
        return {
            "actor_id": "actor_%d" % n,
            "actor_type": "PLAYER" if n == 1 else "ALPHA",
            "team": "A" if (n % 2 == 1) else "B",
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
        }

    def sim_lab_ensure_min_actor(st):
        req = st if isinstance(st, dict) else {}
        actors = req.get("actors", []) if isinstance(req.get("actors", []), list) else []
        if len(actors) < 1:
            actors = [sim_lab_make_actor(1)]
        req["actors"] = actors
        return req

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
            S.sim_lab_state_v1 = sim_lab_clone_request(sim_lab_ensure_min_actor(st))
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
        S.sim_lab_state_v1 = sim_lab_ensure_min_actor(S.sim_lab_state_v1)
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
        actors.append(sim_lab_make_actor(idx))
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

    def sim_lab_set_actor_id(index, actor_id):
        st, actors, i, a = _sim_lab_get_actor(index)
        if a is None:
            return st
        aid = str(actor_id or "").strip()
        if len(aid) == 0:
            aid = "actor_%d" % (i + 1)
        a["actor_id"] = aid
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

    def sim_lab_load_fixture(fixture_key):
        key = str(fixture_key or "").strip()
        fn = getattr(S, "sim_phaseA_fixture_requests", None)
        if not callable(fn):
            return None
        fixtures = fn()
        if not isinstance(fixtures, dict):
            return None
        req = fixtures.get(key)
        if not isinstance(req, dict):
            return None
        S.sim_lab_state_v1 = sim_lab_clone_request(sim_lab_ensure_min_actor(req))
        S.sim_lab_last_result_v1 = None
        return S.sim_lab_state_v1

    def sim_lab_export_last_result_json():
        payload = {
            "request": sim_lab_get_state(),
            "last_result": S.sim_lab_last_result_v1 if isinstance(S.sim_lab_last_result_v1, dict) else None,
        }
        S.sim_lab_export_text_v1 = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        return S.sim_lab_export_text_v1

    def sim_lab_export_phaseA_json():
        fn = getattr(S, "sim_export_phaseA_fixtures_json", None)
        if callable(fn):
            S.sim_lab_export_text_v1 = str(fn() or "")
        else:
            S.sim_lab_export_text_v1 = json.dumps({
                "error": "sim_export_phaseA_fixtures_json no disponible.",
            }, ensure_ascii=False, indent=2)
        return S.sim_lab_export_text_v1

    def sim_lab_export_phaseE_json():
        fn = getattr(S, "sim_export_phaseE_fixtures_json", None)
        if callable(fn):
            S.sim_lab_export_text_v1 = str(fn() or "")
        else:
            S.sim_lab_export_text_v1 = json.dumps({
                "error": "sim_export_phaseE_fixtures_json no disponible.",
            }, ensure_ascii=False, indent=2)
        return S.sim_lab_export_text_v1

    def sim_lab_export_phaseE_e5_json():
        fn = getattr(S, "sim_export_phaseE_e5_readiness_json", None)
        if callable(fn):
            S.sim_lab_export_text_v1 = str(fn() or "")
        else:
            S.sim_lab_export_text_v1 = json.dumps({
                "error": "sim_export_phaseE_e5_readiness_json no disponible.",
            }, ensure_ascii=False, indent=2)
        return S.sim_lab_export_text_v1

    def sim_lab_run_smoke_checklist():
        out = []

        fn_a = getattr(S, "sim_run_phaseA_tests", None)
        if callable(fn_a):
            raw = fn_a()
            if isinstance(raw, list):
                out.extend(raw)
        else:
            out.append({
                "name": "phaseA_tests_unavailable",
                "ok": False,
                "detail": "sim_run_phaseA_tests no disponible.",
            })

        fn_c = getattr(S, "sim_run_phaseC_e2e_tests", None)
        if callable(fn_c):
            raw_c = fn_c()
            if isinstance(raw_c, list):
                out.extend(raw_c)
        else:
            out.append({
                "name": "phaseC_e2e_tests_unavailable",
                "ok": False,
                "detail": "sim_run_phaseC_e2e_tests no disponible.",
            })

        fn_d1 = getattr(S, "sim_run_d1_catalog_tests", None)
        if callable(fn_d1):
            raw_d1 = fn_d1()
            if isinstance(raw_d1, list):
                out.extend(raw_d1)
        else:
            out.append({
                "name": "d1_catalog_tests_unavailable",
                "ok": False,
                "detail": "sim_run_d1_catalog_tests no disponible.",
            })

        fn_d2 = getattr(S, "sim_run_d2_bridge_tests", None)
        if callable(fn_d2):
            raw_d2 = fn_d2()
            if isinstance(raw_d2, list):
                out.extend(raw_d2)
        else:
            out.append({
                "name": "d2_bridge_tests_unavailable",
                "ok": False,
                "detail": "sim_run_d2_bridge_tests no disponible.",
            })

        fn_d3 = getattr(S, "sim_run_d3_mid_battle_tests", None)
        if callable(fn_d3):
            raw_d3 = fn_d3()
            if isinstance(raw_d3, list):
                out.extend(raw_d3)
        else:
            out.append({
                "name": "d3_mid_battle_tests_unavailable",
                "ok": False,
                "detail": "sim_run_d3_mid_battle_tests no disponible.",
            })

        fn_d4 = getattr(S, "sim_run_d4_reconcile_tests", None)
        if callable(fn_d4):
            raw_d4 = fn_d4()
            if isinstance(raw_d4, list):
                out.extend(raw_d4)
        else:
            out.append({
                "name": "d4_reconcile_tests_unavailable",
                "ok": False,
                "detail": "sim_run_d4_reconcile_tests no disponible.",
            })

        fn_d5 = getattr(S, "sim_run_d5_guard_rail_tests", None)
        if callable(fn_d5):
            raw_d5 = fn_d5()
            if isinstance(raw_d5, list):
                out.extend(raw_d5)
        else:
            out.append({
                "name": "d5_guard_rail_tests_unavailable",
                "ok": False,
                "detail": "sim_run_d5_guard_rail_tests no disponible.",
            })

        fn_d6 = getattr(S, "sim_run_phaseD_e2e_tests", None)
        if callable(fn_d6):
            raw_d6 = fn_d6()
            if isinstance(raw_d6, list):
                out.extend(raw_d6)
        else:
            out.append({
                "name": "phaseD_e2e_tests_unavailable",
                "ok": False,
                "detail": "sim_run_phaseD_e2e_tests no disponible.",
            })

        fn_e4 = getattr(S, "sim_run_phaseE_e4_tests", None)
        if callable(fn_e4):
            raw_e4 = fn_e4()
            if isinstance(raw_e4, list):
                out.extend(raw_e4)
        else:
            out.append({
                "name": "phaseE_e4_tests_unavailable",
                "ok": False,
                "detail": "sim_run_phaseE_e4_tests no disponible.",
            })

        fn_e5 = getattr(S, "sim_run_phaseE_e5_tests", None)
        if callable(fn_e5):
            raw_e5 = fn_e5()
            if isinstance(raw_e5, list):
                out.extend(raw_e5)
        else:
            out.append({
                "name": "phaseE_e5_tests_unavailable",
                "ok": False,
                "detail": "sim_run_phaseE_e5_tests no disponible.",
            })

        S.sim_lab_smoke_results_v1 = out
        return S.sim_lab_smoke_results_v1

    def sim_lab_refresh_mid_battle_view(limit=20):
        lim = int(limit or 20)
        if lim < 1:
            lim = 1
        if lim > 100:
            lim = 100

        raw = getattr(S, "sim_mid_battle_event_log_v1", None)
        if not isinstance(raw, list):
            raw = []

        rows = []
        for ev in reversed(raw[-lim:]):
            if not isinstance(ev, dict):
                continue
            event_key = str(ev.get("event_key", "") or "")
            reward_event_id = str(ev.get("reward_event_id", "") or "")
            actors = ev.get("actors", []) if isinstance(ev.get("actors", []), list) else []

            if len(actors) > 0:
                for aa in actors:
                    if not isinstance(aa, dict):
                        continue
                    rows.append({
                        "event_key": event_key,
                        "reward_event_id": reward_event_id,
                        "actor_id": str(aa.get("actor_id", "") or "n/a"),
                        "exp_gain": _sim_lab_to_int(aa.get("exp_gain", 0), 0),
                        "oro_gain": _sim_lab_to_int(aa.get("oro_gain", 0), 0),
                        "idempotency_status": str(aa.get("idempotency_status", "unknown") or "unknown"),
                    })
            else:
                rows.append({
                    "event_key": event_key,
                    "reward_event_id": reward_event_id,
                    "actor_id": "n/a",
                    "exp_gain": _sim_lab_to_int(ev.get("apply_total_exp", 0), 0),
                    "oro_gain": _sim_lab_to_int(ev.get("apply_total_oro", 0), 0),
                    "idempotency_status": "unknown",
                })

        S.sim_lab_mid_battle_rows_v1 = rows
        return S.sim_lab_mid_battle_rows_v1

    def sim_lab_clear_mid_battle_view():
        S.sim_lab_mid_battle_rows_v1 = []
        return S.sim_lab_mid_battle_rows_v1


label sim_lab_open:
    call screen sim_lab_v1
    return


screen sim_lab_v1():
    tag menu
    modal True
    zorder 200

    $ st = sim_lab_get_state()
    $ cfg = st.get("config", {}) if isinstance(st.get("config", {}), dict) else {}
    $ actors = st.get("actors", []) if isinstance(st.get("actors", []), list) else []
    $ last = sim_lab_last_result_v1 if isinstance(sim_lab_last_result_v1, dict) else None
    $ smoke = sim_lab_smoke_results_v1 if isinstance(sim_lab_smoke_results_v1, list) else []
    $ mid_rows = sim_lab_mid_battle_rows_v1 if isinstance(sim_lab_mid_battle_rows_v1, list) else []
    $ export_text = sim_lab_export_text_v1 if isinstance(sim_lab_export_text_v1, str) else ""

    frame:
        xfill True
        yfill True
        padding (20, 20)

        vbox:
            spacing 10

            text "SIM LAB V1 — Incremento 3 (B7+B8+B9+B10+B11)" size 34
            text ("Contrato: %s | Simulation ID: %s" % (
                st.get("sim_contract_version", "v1"),
                st.get("simulation_id", "sim_unknown"),
            )) size 18

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Editor principal" size 24

                    text ("Mode actual: %s" % st.get("mode", "1v1")) size 18
                    hbox:
                        spacing 8
                        textbutton "1v1" action Function(sim_lab_set_mode, "1v1")
                        textbutton "2v1" action Function(sim_lab_set_mode, "2v1")
                        textbutton "1v2" action Function(sim_lab_set_mode, "1v2")
                        textbutton "2v2" action Function(sim_lab_set_mode, "2v2")
                        textbutton "Custom" action Function(sim_lab_set_mode, "custom")

                    text ("Winner Team: %s" % st.get("winner_team", "DRAW")) size 18
                    hbox:
                        spacing 8
                        textbutton "A" action Function(sim_lab_set_winner, "A")
                        textbutton "B" action Function(sim_lab_set_winner, "B")
                        textbutton "DRAW" action Function(sim_lab_set_winner, "DRAW")

                    text ("Event Type: %s" % st.get("event_type", "draw")) size 18
                    hbox:
                        spacing 8
                        textbutton "victory" action Function(sim_lab_set_event_type, "victory")
                        textbutton "defeat" action Function(sim_lab_set_event_type, "defeat")
                        textbutton "draw" action Function(sim_lab_set_event_type, "draw")
                        textbutton "conditional_gain" action Function(sim_lab_set_event_type, "conditional_gain")

                    text ("Source: %s" % st.get("source", "lab_manual")) size 18
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
                    text ("Preset: %s | Repetition: %s" % (
                        cfg.get("preset", "medium_v2"),
                        cfg.get("repetition_count", 1),
                    )) size 18
                    text ("multi_factor_enabled: %s | allow_mid_battle_grants: %s" % (
                        "ON" if cfg.get("multi_factor_enabled", True) else "OFF",
                        "ON" if cfg.get("allow_mid_battle_grants", True) else "OFF",
                    )) size 18
                    hbox:
                        spacing 8
                        textbutton "Preset medium_v2" action Function(sim_lab_set_preset, "medium_v2")
                        textbutton "Rep -1" action Function(sim_lab_shift_repetition, -1)
                        textbutton "Rep +1" action Function(sim_lab_shift_repetition, +1)
                        textbutton "Toggle multi_factor" action Function(sim_lab_toggle_multi_factor)
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
                                        text ("(%d) %s | Tipo: %s | Team: %s | Elig: %s" % (
                                            i,
                                            a.get("actor_id", "actor"),
                                            a.get("actor_type", "ALPHA"),
                                            a.get("team", "A"),
                                            "ON" if a.get("flags", {}).get("eligible_rewards", True) else "OFF",
                                        )) size 16
                                        hbox:
                                            spacing 8
                                            textbutton "ID Auto" action Function(sim_lab_set_actor_id, i, "")
                                            textbutton "ID +Sfx" action Function(sim_lab_set_actor_id, i, ("%s_x" % a.get("actor_id", ("actor_%d" % (i + 1)))))
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
                    text "Fixtures (B9)" size 24
                    hbox:
                        spacing 8
                        textbutton "fixture_a_2v2" action Function(sim_lab_load_fixture, "fixture_a_2v2")
                        textbutton "fixture_b_2v1" action Function(sim_lab_load_fixture, "fixture_b_2v1")
                        textbutton "fixture_c_1v1_dr0" action Function(sim_lab_load_fixture, "fixture_c_1v1_dr0")

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

            if last:
                frame:
                    xfill True
                    ymaximum 300
                    padding (12, 12)
                    vbox:
                        spacing 8
                        text "Resultados por actor (B7)" size 24
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 230
                            vbox:
                                spacing 8
                                for rr in last.get("results", []):
                                    $ final = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
                                    $ mult = rr.get("multipliers", {}) if isinstance(rr.get("multipliers", {}), dict) else {}
                                    frame:
                                        xfill True
                                        padding (8, 8)
                                        vbox:
                                            spacing 4
                                            text ("actor_id=%s | outcome=%s | eligible=%s" % (
                                                rr.get("actor_id", "n/a"),
                                                rr.get("outcome", "n/a"),
                                                "YES" if rr.get("eligible", False) else "NO",
                                            )) size 15
                                            text ("stars_total=%s | delta_register=%s | base_exp/oro=%s/%s" % (
                                                rr.get("stars_total", 0),
                                                rr.get("delta_register", 0),
                                                rr.get("base_exp", 0),
                                                rr.get("base_oro", 0),
                                            )) size 14
                                            text ("exp_gain/oro_gain=%s/%s | exp_after/oro_after=%s/%s" % (
                                                final.get("exp_gain", 0),
                                                final.get("oro_gain", 0),
                                                final.get("exp_after", 0),
                                                final.get("oro_after", 0),
                                            )) size 14
                                            text ("multipliers: result=%.2f m_multi=%.2f final=%.2f" % (
                                                float(mult.get("result_multiplier", 1.0) or 1.0),
                                                float(mult.get("m_multi", 1.0) or 1.0),
                                                float(mult.get("final_multiplier", 1.0) or 1.0),
                                            )) size 14

            if last:
                frame:
                    xfill True
                    ymaximum 260
                    padding (12, 12)
                    vbox:
                        spacing 8
                        text "Auditoría + Idempotencia (B8)" size 24
                        $ audit = last.get("audit", {}) if isinstance(last.get("audit", {}), dict) else {}
                        $ errs = audit.get("errors", []) if isinstance(audit.get("errors", []), list) else []
                        $ warns = audit.get("warnings", []) if isinstance(audit.get("warnings", []), list) else []
                        $ idem = audit.get("idempotency", {}) if isinstance(audit.get("idempotency", {}), dict) else {}
                        text ("errors=%d | warnings=%d | idempotency.enabled=%s | event_id=%s" % (
                            len(errs), len(warns), "YES" if idem.get("enabled", False) else "NO", idem.get("event_id", "n/a")
                        )) size 15
                        if len(errs) > 0:
                            text "Errores:" size 14
                            for ee in errs:
                                text ("- %s" % ee) size 13
                        if len(warns) > 0:
                            text "Warnings:" size 14
                            for ww in warns:
                                text ("- %s" % ww) size 13
                        $ statuses = idem.get("statuses", {}) if isinstance(idem.get("statuses", {}), dict) else {}
                        if len(statuses) > 0:
                            text "Idempotency statuses por actor_id:" size 14
                            for kk, vv in statuses.items():
                                text ("- %s: %s" % (kk, vv)) size 13

            frame:
                xfill True
                ymaximum 280
                padding (12, 12)
                vbox:
                    spacing 8
                    text "D7 — QA Mid-battle inspector" size 24
                    hbox:
                        spacing 8
                        textbutton "Refrescar últimos 20" action Function(sim_lab_refresh_mid_battle_view, 20)
                        textbutton "Limpiar vista" action Function(sim_lab_clear_mid_battle_view)
                    if len(mid_rows) > 0:
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 190
                            vbox:
                                spacing 6
                                for row in mid_rows:
                                    text ("%s | %s | actor=%s | gains exp/oro=%s/%s | idem=%s" % (
                                        row.get("event_key", "n/a"),
                                        row.get("reward_event_id", "n/a"),
                                        row.get("actor_id", "n/a"),
                                        row.get("exp_gain", 0),
                                        row.get("oro_gain", 0),
                                        row.get("idempotency_status", "unknown"),
                                    )) size 14
                    else:
                        text "Sin snapshot. Usa 'Refrescar últimos 20' para inspeccionar N recientes." size 14

            frame:
                xfill True
                ymaximum 320
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Export QA (B10)" size 24
                    hbox:
                        spacing 8
                        textbutton "Export last result JSON" action Function(sim_lab_export_last_result_json)
                        textbutton "Export fixtures A JSON" action Function(sim_lab_export_phaseA_json)
                        textbutton "Export fixtures E JSON" action Function(sim_lab_export_phaseE_json)
                        textbutton "Export E5 readiness JSON" action Function(sim_lab_export_phaseE_e5_json)
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 230
                        text (export_text if len(export_text) > 0 else "Sin export aún.") size 12

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Smoke checklist (B11)" size 24
                    hbox:
                        spacing 8
                        textbutton "Run smoke tests" action Function(sim_lab_run_smoke_checklist)
                    if len(smoke) > 0:
                        for t in smoke:
                            $ ok = bool((t or {}).get("ok", False))
                            text ("(%s) %s — %s" % (
                                "OK" if ok else "FAIL",
                                (t or {}).get("name", "unknown"),
                                (t or {}).get("detail", "")
                            )) size 14
                    else:
                        text "Sin ejecución de smoke checklist." size 14

            hbox:
                spacing 8
                textbutton "Reset request" action Function(sim_lab_reset_state)
                textbutton "Cerrar" action Return()
