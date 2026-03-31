# ===============================================================
# 10C_PROGRESSION_SIM_CONTRACT_V1.rpy
# Fase A (A1 + A2) — Contrato y validación del simulador
# ===============================================================

init -875 python:

    import copy
    import json
    import time

    SIM_CONTRACT_VERSION = "v1"

    SIM_ALLOWED_MODES = ("1v1", "2v1", "1v2", "2v2", "custom")
    SIM_ALLOWED_SOURCES = ("battle_end", "mid_battle_event", "lab_manual")
    SIM_ALLOWED_EVENT_TYPES = ("victory", "defeat", "draw", "conditional_gain")
    SIM_ALLOWED_WINNER_TEAM = ("A", "B", "DRAW")
    SIM_ALLOWED_ACTOR_TYPES = ("PLAYER", "ALPHA", "BETA", "GAMMA", "DELTA")
    SIM_ALLOWED_TEAMS = ("A", "B")

    SIM_STAR_KEYS = ("ofensiva", "defensiva", "control", "eficiencia", "tecnica", "impacto")
    SIM_RISK_EXP_TABLE = {
        -5: 0.15, -4: 0.25, -3: 0.40, -2: 0.60, -1: 0.82,
         0: 1.00,  1: 1.25,  2: 1.55,  3: 1.90,  4: 2.30, 5: 2.80,
    }
    SIM_RISK_ORO_TABLE = {
        -5: 0.25, -4: 0.40, -3: 0.55, -2: 0.72, -1: 0.88,
         0: 1.00,  1: 1.12,  2: 1.28,  3: 1.45,  4: 1.65, 5: 1.85,
    }

    def _sim_to_int(v, default=0):
        try:
            return int(v)
        except:
            return int(default)

    def _sim_clamp(v, lo, hi):
        vv = _sim_to_int(v, lo)
        if vv < lo:
            return lo
        if vv > hi:
            return hi
        return vv

    def sim_build_min_request():
        """
        Request mínimo válido para pruebas de contrato.
        """
        return {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": "sim_min_v1",
            "mode": "1v1",
            "source": "lab_manual",
            "event_type": "draw",
            "winner_team": "DRAW",
            "actors": [
                {
                    "actor_id": "player_1",
                    "actor_type": "PLAYER",
                    "team": "A",
                    "level": 1,
                    "register": 0,
                    "exp_current": 0,
                    "exp_max": 100,
                    "oro_current": 0,
                    "stars": {k: 0 for k in SIM_STAR_KEYS},
                    "flags": {
                        "eligible_rewards": True,
                        "allow_level_up": True,
                        "allow_inventory_rewards": True,
                    },
                }
            ],
            "config": {
                "preset": "medium_v2",
                "allow_mid_battle_grants": True,
                "repetition_count": 1,
                "multi_factor_enabled": True,
            },
        }

    def sim_validate_request(request):
        """
        Valida y normaliza SimulationRequest (A1+A2).

        Retorna:
        {
          "ok": bool,
          "errors": [str],
          "warnings": [str],
          "normalized": dict,
        }
        """
        req = request if isinstance(request, dict) else {}
        out = copy.deepcopy(req)
        errors = []
        warnings = []

        # versión de contrato
        ver = str(out.get("sim_contract_version", SIM_CONTRACT_VERSION) or SIM_CONTRACT_VERSION)
        out["sim_contract_version"] = ver
        if ver != SIM_CONTRACT_VERSION:
            warnings.append("sim_contract_version distinto de v1; se intenta compatibilidad best-effort.")

        # campos raíz
        out["simulation_id"] = str(out.get("simulation_id", "sim_unknown") or "sim_unknown")

        mode = str(out.get("mode", "1v1") or "1v1")
        if mode not in SIM_ALLOWED_MODES:
            errors.append("mode inválido: %s" % mode)
        out["mode"] = mode

        source = str(out.get("source", "lab_manual") or "lab_manual")
        if source not in SIM_ALLOWED_SOURCES:
            errors.append("source inválido: %s" % source)
        out["source"] = source

        event_type = str(out.get("event_type", "draw") or "draw")
        if event_type not in SIM_ALLOWED_EVENT_TYPES:
            errors.append("event_type inválido: %s" % event_type)
        out["event_type"] = event_type

        winner_team = str(out.get("winner_team", "DRAW") or "DRAW")
        if winner_team not in SIM_ALLOWED_WINNER_TEAM:
            errors.append("winner_team inválido: %s" % winner_team)
        out["winner_team"] = winner_team

        # config
        cfg = out.get("config", {}) if isinstance(out.get("config", {}), dict) else {}
        cfg["preset"] = str(cfg.get("preset", "medium_v2") or "medium_v2")
        cfg["allow_mid_battle_grants"] = bool(cfg.get("allow_mid_battle_grants", True))
        cfg["repetition_count"] = max(1, _sim_to_int(cfg.get("repetition_count", 1), 1))
        cfg["multi_factor_enabled"] = bool(cfg.get("multi_factor_enabled", True))
        out["config"] = cfg

        # actors no vacío
        actors = out.get("actors", [])
        if not isinstance(actors, list) or len(actors) == 0:
            errors.append("actors no puede estar vacío.")
            actors = []

        norm_actors = []
        teams_present = set()

        for idx, a in enumerate(actors):
            aa = a if isinstance(a, dict) else {}

            actor_id = str(aa.get("actor_id", "actor_%d" % idx) or ("actor_%d" % idx))
            actor_type = str(aa.get("actor_type", "ALPHA") or "ALPHA").upper()
            team = str(aa.get("team", "") or "").upper()

            if actor_type not in SIM_ALLOWED_ACTOR_TYPES:
                errors.append("actor[%d].actor_type inválido: %s" % (idx, actor_type))
            if team not in SIM_ALLOWED_TEAMS:
                errors.append("actor[%d].team inválido/ausente: %s" % (idx, team))
            else:
                teams_present.add(team)

            level = max(1, _sim_to_int(aa.get("level", 1), 1))
            register = _sim_clamp(aa.get("register", 0), 0, 50)
            exp_current = max(0, _sim_to_int(aa.get("exp_current", 0), 0))
            exp_max = max(1, _sim_to_int(aa.get("exp_max", 100), 100))
            oro_current = max(0, _sim_to_int(aa.get("oro_current", 0), 0))

            stars_in = aa.get("stars", {}) if isinstance(aa.get("stars", {}), dict) else {}
            stars = {}
            stars_total_raw = 0
            for k in SIM_STAR_KEYS:
                vv = _sim_clamp(stars_in.get(k, 0), 0, 5)
                stars[k] = vv
                stars_total_raw += vv
            stars_total = _sim_clamp(stars_total_raw, 0, 30)

            flags = aa.get("flags", {}) if isinstance(aa.get("flags", {}), dict) else {}
            eligible = bool(flags.get("eligible_rewards", True))
            allow_level_up = bool(flags.get("allow_level_up", True))
            allow_inventory_rewards = bool(flags.get("allow_inventory_rewards", True))

            # Regla de elegibilidad por tipo (A2)
            if actor_type == "GAMMA" and eligible:
                warnings.append("actor[%d] GAMMA no es elegible para recompensas de combate por default; se fuerza eligible_rewards=false." % idx)
                eligible = False

            norm_actors.append({
                "actor_id": actor_id,
                "actor_type": actor_type,
                "team": team,
                "level": level,
                "register": register,
                "exp_current": exp_current,
                "exp_max": exp_max,
                "oro_current": oro_current,
                "stars": stars,
                "stars_total": stars_total,
                "flags": {
                    "eligible_rewards": eligible,
                    "allow_level_up": allow_level_up,
                    "allow_inventory_rewards": allow_inventory_rewards,
                },
            })

        out["actors"] = norm_actors

        # coherencia winner_team
        if winner_team != "DRAW":
            if winner_team not in teams_present:
                errors.append("winner_team=%s pero no hay actores en ese equipo." % winner_team)

        return {
            "ok": (len(errors) == 0),
            "errors": errors,
            "warnings": warnings,
            "normalized": out,
        }

    def sim_build_min_result(validated_request):
        """
        Construye un SimulationResult mínimo a partir del request validado.
        """
        vr = validated_request if isinstance(validated_request, dict) else {}
        req = vr.get("normalized", {}) if isinstance(vr.get("normalized", {}), dict) else {}

        results = []
        for a in req.get("actors", []):
            results.append({
                "actor_id": str(a.get("actor_id", "unknown")),
                "eligible": bool(a.get("flags", {}).get("eligible_rewards", True)),
                "stars_total": int(a.get("stars_total", 0) or 0),
                "delta_register": 0,
                "multipliers": {},
                "base": {"exp": 0, "oro": 0},
                "final": {
                    "exp_gain": 0,
                    "oro_gain": 0,
                    "exp_after": int(a.get("exp_current", 0) or 0),
                    "oro_after": int(a.get("oro_current", 0) or 0),
                    "level_after": int(a.get("level", 1) or 1),
                    "register_after": int(a.get("register", 0) or 0),
                },
                "notes": [],
            })

        return {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": str(req.get("simulation_id", "sim_unknown")),
            "mode": str(req.get("mode", "1v1")),
            "winner_team": str(req.get("winner_team", "DRAW")),
            "results": results,
            "audit": {
                "warnings": list(vr.get("warnings", [])) if isinstance(vr.get("warnings", []), list) else [],
                "errors": list(vr.get("errors", [])) if isinstance(vr.get("errors", []), list) else [],
                "sim_contract_version": SIM_CONTRACT_VERSION,
            },
        }

    # ===================================================
    # Fase A (A3 + A4): Núcleo matemático + orquestador
    # ===================================================

    def compute_stars_total(actor_stars):
        st = actor_stars if isinstance(actor_stars, dict) else {}
        total = 0
        clean = {}
        for k in SIM_STAR_KEYS:
            vv = _sim_clamp(st.get(k, 0), 0, 5)
            clean[k] = vv
            total += vv
        return {
            "stars": clean,
            "stars_total": _sim_clamp(total, 0, 30),
        }

    def compute_delta_register(actor, rivals):
        a = actor if isinstance(actor, dict) else {}
        rv = rivals if isinstance(rivals, list) else []
        reg_actor = _sim_clamp(a.get("register", 0), 0, 50)
        if len(rv) == 0:
            return 0
        s = 0.0
        n = 0
        for r in rv:
            if isinstance(r, dict):
                s += float(_sim_clamp(r.get("register", 0), 0, 50))
                n += 1
        if n <= 0:
            return 0
        avg = s / float(n)
        return int(round(avg - float(reg_actor)))

    def _sim_base_rewards_from_stars(stars_total, preset):
        st = _sim_clamp(stars_total, 0, 30)
        p = str(preset or "medium_v2").strip().lower()

        # Preset principal acordado: grindeo medio (v2)
        if p == "medium_v2":
            return {
                "exp": int(round(35 + (3.5 * st))),
                "oro": int(round(15 + (2.0 * st))),
            }

        # Fallback compat con fórmula histórica del panel (base 100/60)
        return {
            "exp": int(round(100 * (0.70 + (0.02 * st)))),
            "oro": int(round(60 * (0.80 + (0.01 * st)))),
        }

    def compute_performance_multipliers(stars_total, preset):
        st = _sim_clamp(stars_total, 0, 30)
        p = str(preset or "medium_v2").strip().lower()
        if p == "medium_v2":
            # En medium_v2 el desempeño está integrado en base por estrellas.
            return {
                "performance_exp": 1.0,
                "performance_oro": 1.0,
                "base_model": "preset_medium_v2_base_by_stars",
            }
        return {
            "performance_exp": 0.70 + (0.02 * st),
            "performance_oro": 0.80 + (0.01 * st),
            "base_model": "legacy_panel_formula",
        }

    def compute_risk_multipliers(delta_register):
        d = _sim_to_int(delta_register, 0)
        if d < -5:
            d = -5
        if d > 5:
            d = 5
        return {
            "delta_register": d,
            "risk_exp": float(SIM_RISK_EXP_TABLE.get(d, 1.0)),
            "risk_oro": float(SIM_RISK_ORO_TABLE.get(d, 1.0)),
        }

    def compute_multi_factor(team_sizes, enabled=True):
        if not bool(enabled):
            return 1.0
        ts = team_sizes if isinstance(team_sizes, dict) else {}
        allies = max(1, _sim_to_int(ts.get("allies", 1), 1))
        enemies = max(1, _sim_to_int(ts.get("enemies", 1), 1))
        raw = (float(enemies) / float(allies)) ** 0.5
        if raw < 0.85:
            return 0.85
        if raw > 1.35:
            return 1.35
        return float(raw)

    def _sim_result_multipliers_for_actor(actor, winner_team):
        team = str((actor or {}).get("team", "A") or "A").upper()
        wt = str(winner_team or "DRAW").upper()
        if wt == "DRAW":
            return {"result_exp": 0.85, "result_oro": 0.75, "outcome": "draw"}
        if team == wt:
            return {"result_exp": 1.00, "result_oro": 1.00, "outcome": "victory"}
        return {"result_exp": 0.70, "result_oro": 0.50, "outcome": "defeat"}

    def compute_actor_reward(actor, rivals, winner_team, config):
        a = actor if isinstance(actor, dict) else {}
        cfg = config if isinstance(config, dict) else {}
        flags = a.get("flags", {}) if isinstance(a.get("flags", {}), dict) else {}

        eligible = bool(flags.get("eligible_rewards", True))
        stars_pack = compute_stars_total(a.get("stars", {}))
        stars_total = stars_pack["stars_total"]
        delta_register = compute_delta_register(a, rivals)
        risk = compute_risk_multipliers(delta_register)
        result_mult = _sim_result_multipliers_for_actor(a, winner_team)
        perf = compute_performance_multipliers(stars_total, cfg.get("preset", "medium_v2"))
        base = _sim_base_rewards_from_stars(stars_total, cfg.get("preset", "medium_v2"))

        team_sizes = {
            "allies": max(1, _sim_to_int(cfg.get("_allies_count", 1), 1)),
            "enemies": max(1, _sim_to_int(cfg.get("_enemies_count", 1), 1)),
        }
        multi_factor = compute_multi_factor(team_sizes, cfg.get("multi_factor_enabled", True))

        repetition_count = max(1, _sim_to_int(cfg.get("repetition_count", 1), 1))
        if repetition_count <= 1:
            anti = 1.00
        elif repetition_count == 2:
            anti = 0.60
        elif repetition_count == 3:
            anti = 0.30
        else:
            anti = 0.10

        exp_gain = 0
        oro_gain = 0
        notes = []

        if eligible:
            exp_raw = (
                float(base["exp"]) *
                float(risk["risk_exp"]) *
                float(result_mult["result_exp"]) *
                float(perf["performance_exp"]) *
                float(anti) *
                float(multi_factor)
            )
            oro_raw = (
                float(base["oro"]) *
                float(risk["risk_oro"]) *
                float(result_mult["result_oro"]) *
                float(perf["performance_oro"]) *
                float(anti) *
                float(multi_factor)
            )
            exp_gain = max(0, int(round(exp_raw)))
            oro_gain = max(0, int(round(oro_raw)))
        else:
            notes.append("reward_ineligible")

        exp_after = max(0, _sim_to_int(a.get("exp_current", 0), 0) + exp_gain)
        oro_after = max(0, _sim_to_int(a.get("oro_current", 0), 0) + oro_gain)

        level_now = max(1, _sim_to_int(a.get("level", 1), 1))
        register_now = _sim_clamp(a.get("register", 0), 0, 50)

        return {
            "actor_id": str(a.get("actor_id", "unknown")),
            "eligible": eligible,
            "outcome": result_mult["outcome"],
            "stars_total": stars_total,
            "delta_register": risk["delta_register"],
            "multipliers": {
                "risk_exp": risk["risk_exp"],
                "risk_oro": risk["risk_oro"],
                "result_exp": result_mult["result_exp"],
                "result_oro": result_mult["result_oro"],
                "performance_exp": perf["performance_exp"],
                "performance_oro": perf["performance_oro"],
                "antiabuso": anti,
                "multi_factor": float(multi_factor),
            },
            "base": {
                "exp": int(base["exp"]),
                "oro": int(base["oro"]),
            },
            "final": {
                "exp_gain": int(exp_gain),
                "oro_gain": int(oro_gain),
                "exp_after": int(exp_after),
                "oro_after": int(oro_after),
                "level_after": int(level_now),
                "register_after": int(register_now),
            },
            "notes": notes,
        }

    def run_simulation(request):
        """
        A4 - Orquestador de simulación.
        """
        vr = sim_validate_request(request)
        req = vr.get("normalized", {}) if isinstance(vr.get("normalized", {}), dict) else {}
        results = []
        warnings = list(vr.get("warnings", [])) if isinstance(vr.get("warnings", []), list) else []
        errors = list(vr.get("errors", [])) if isinstance(vr.get("errors", []), list) else []

        if not vr.get("ok", False):
            return {
                "sim_contract_version": SIM_CONTRACT_VERSION,
                "simulation_id": str(req.get("simulation_id", "sim_unknown")),
                "mode": str(req.get("mode", "custom")),
                "winner_team": str(req.get("winner_team", "DRAW")),
                "results": [],
                "audit": {
                    "warnings": warnings,
                    "errors": errors,
                    "sim_contract_version": SIM_CONTRACT_VERSION,
                },
            }

        actors = req.get("actors", []) if isinstance(req.get("actors", []), list) else []
        winner_team = req.get("winner_team", "DRAW")
        config = req.get("config", {}) if isinstance(req.get("config", {}), dict) else {}

        for a in actors:
            team = str(a.get("team", "") or "").upper()
            allies = [x for x in actors if str(x.get("team", "") or "").upper() == team]
            rivals = [x for x in actors if str(x.get("team", "") or "").upper() != team]

            cfg_local = copy.deepcopy(config)
            cfg_local["_allies_count"] = len(allies)
            cfg_local["_enemies_count"] = len(rivals)

            rr = compute_actor_reward(a, rivals, winner_team, cfg_local)
            results.append(rr)

        # A5 - idempotencia por reward_event_id
        idem = sim_apply_reward_event_idempotency(req, results)
        results = idem["results"]
        if idem["warnings"]:
            warnings.extend(idem["warnings"])
        if idem["errors"]:
            errors.extend(idem["errors"])

        return {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": str(req.get("simulation_id", "sim_unknown")),
            "mode": str(req.get("mode", "custom")),
            "winner_team": str(winner_team),
            "results": results,
            "audit": {
                "warnings": warnings,
                "errors": errors,
                "idempotency": idem["audit"],
                "sim_contract_version": SIM_CONTRACT_VERSION,
            },
        }

    # ===================================================
    # Fase C (C1): Adaptador runtime -> SimulationRequest
    # ===================================================

    def _sim_get_from_sources(sources, keys, default=None):
        srcs = sources if isinstance(sources, list) else []
        for src in srcs:
            if src is None:
                continue
            for k in keys:
                try:
                    if isinstance(src, dict):
                        if k in src:
                            return src.get(k)
                    else:
                        if hasattr(src, k):
                            return getattr(src, k)
                except:
                    pass
        return default

    def _sim_level_to_register(level):
        lvl = max(1, _sim_to_int(level, 1))
        # Usa compute_register del panel si está disponible.
        fn = globals().get("compute_register", None)
        if callable(fn):
            try:
                return _sim_clamp(fn(lvl), 0, 50)
            except:
                pass
        # Fallback estable (Acordado en diseño): 10 niveles = 1 registro.
        return _sim_clamp(int(lvl // 10), 0, 50)

    def _sim_resolve_winner_team(runtime):
        rt = runtime if isinstance(runtime, dict) else {}
        w = str(rt.get("winner_team", "") or "").upper()
        if w in SIM_ALLOWED_WINNER_TEAM:
            return w

        # Permite mapear desde story_pilot_last_result o result textual.
        result_raw = str(rt.get("result", rt.get("story_pilot_last_result", "")) or "").strip().lower()
        if result_raw in ("victory", "win", "player_win"):
            return "A"
        if result_raw in ("defeat", "lose", "loss", "enemy_win"):
            return "B"
        if result_raw in ("draw", "tie", "empate"):
            return "DRAW"

        # Heurística por hp final.
        a_hp = _sim_to_int(rt.get("team_a_hp", rt.get("player_hp", 0)), 0)
        b_hp = _sim_to_int(rt.get("team_b_hp", rt.get("enemy_hp", 0)), 0)
        if a_hp > 0 and b_hp <= 0:
            return "A"
        if b_hp > 0 and a_hp <= 0:
            return "B"
        if a_hp <= 0 and b_hp <= 0:
            return "DRAW"
        return "DRAW"

    def _sim_build_reward_event_id(runtime, winner_team, source):
        rt = runtime if isinstance(runtime, dict) else {}
        match_id = str(rt.get("match_id", rt.get("battle_id", rt.get("simulation_id", "battle_unknown"))) or "battle_unknown")
        turn = _sim_to_int(rt.get("turn_index", rt.get("turn", 0)), 0)
        return "be::%s::%s::%s::t%s" % (str(source or "battle_end"), match_id, winner_team, turn)

    def _sim_build_actor_from_runtime(team, role, base, index):
        b = base if isinstance(base, dict) else {}
        idx = _sim_to_int(index, 0)
        role_s = str(role or "ally").strip().lower()
        actor_id = str(b.get("actor_id", "%s_%d" % (role_s, idx + 1)) or ("%s_%d" % (role_s, idx + 1)))

        actor_type = str(b.get("actor_type", "ALPHA") or "ALPHA").upper()
        if role_s in ("player", "host_player", "main_player"):
            actor_type = "PLAYER"

        level = max(1, _sim_to_int(b.get("level", 1), 1))
        register = b.get("register", None)
        register = _sim_level_to_register(level) if register is None else _sim_clamp(register, 0, 50)
        exp_current = max(0, _sim_to_int(b.get("exp_current", 0), 0))
        exp_max = max(1, _sim_to_int(b.get("exp_max", 100), 100))
        oro_current = max(0, _sim_to_int(b.get("oro_current", b.get("gold_current", 0)), 0))

        stars_in = b.get("stars", {}) if isinstance(b.get("stars", {}), dict) else {}
        stars = {}
        for k in SIM_STAR_KEYS:
            stars[k] = _sim_clamp(stars_in.get(k, 0), 0, 5)

        # Defaults por tipo, alineados con blueprint.
        default_eligible = actor_type not in ("GAMMA", "BETA")
        flags_in = b.get("flags", {}) if isinstance(b.get("flags", {}), dict) else {}
        flags = {
            "eligible_rewards": bool(flags_in.get("eligible_rewards", default_eligible)),
            "allow_level_up": bool(flags_in.get("allow_level_up", actor_type in ("PLAYER", "ALPHA", "DELTA"))),
            "allow_inventory_rewards": bool(flags_in.get("allow_inventory_rewards", actor_type in ("PLAYER", "ALPHA", "DELTA"))),
        }

        return {
            "actor_id": actor_id,
            "actor_type": actor_type if actor_type in SIM_ALLOWED_ACTOR_TYPES else "ALPHA",
            "team": str(team or "A").upper(),
            "level": level,
            "register": register,
            "exp_current": exp_current,
            "exp_max": exp_max,
            "oro_current": oro_current,
            "stars": stars,
            "flags": flags,
        }

    def sim_build_request_from_battle_state(runtime=None, overrides=None):
        """
        C1 - Adaptador runtime -> SimulationRequest.
        Convierte un estado de combate real (o parcial) al contrato v1.

        Parámetros:
          runtime: dict opcional con estado del combate.
          overrides: dict opcional para sobreescribir campos del request final.
        """
        import renpy.store as S

        rt = runtime if isinstance(runtime, dict) else {}
        ov = overrides if isinstance(overrides, dict) else {}
        sources = [ov, rt, S]

        source = str(_sim_get_from_sources(sources, ("source",), "battle_end") or "battle_end")
        if source not in SIM_ALLOWED_SOURCES:
            source = "battle_end"

        event_type = str(_sim_get_from_sources(sources, ("event_type",), "draw") or "draw").lower()
        if event_type not in SIM_ALLOWED_EVENT_TYPES:
            event_type = "draw"

        winner_team = _sim_resolve_winner_team({
            "winner_team": _sim_get_from_sources(sources, ("winner_team",), ""),
            "result": _sim_get_from_sources(sources, ("result", "story_pilot_last_result"), ""),
            "player_hp": _sim_get_from_sources(sources, ("player_hp", "team_a_hp"), 0),
            "enemy_hp": _sim_get_from_sources(sources, ("enemy_hp", "team_b_hp"), 0),
            "team_a_hp": _sim_get_from_sources(sources, ("team_a_hp", "player_hp"), 0),
            "team_b_hp": _sim_get_from_sources(sources, ("team_b_hp", "enemy_hp"), 0),
        })

        if winner_team == "A":
            event_type = "victory"
        elif winner_team == "B":
            event_type = "defeat"
        elif winner_team == "DRAW":
            event_type = "draw"

        # Actores A/B: permite arrays o fallback 1v1.
        actors_team_a = _sim_get_from_sources(sources, ("team_a_actors", "player_team_actors"), None)
        actors_team_b = _sim_get_from_sources(sources, ("team_b_actors", "enemy_team_actors"), None)

        norm_actors = []

        if isinstance(actors_team_a, list) and len(actors_team_a) > 0:
            for i, a in enumerate(actors_team_a):
                norm_actors.append(_sim_build_actor_from_runtime("A", "ally", a, i))
        else:
            a1 = {
                "actor_id": _sim_get_from_sources(sources, ("player_actor_id", "player_id"), "player_1"),
                "actor_type": _sim_get_from_sources(sources, ("player_actor_type",), "PLAYER"),
                "level": _sim_get_from_sources(sources, ("player_level", "level"), 1),
                "register": _sim_get_from_sources(sources, ("player_register", "register"), None),
                "exp_current": _sim_get_from_sources(sources, ("player_exp", "exp_current"), 0),
                "exp_max": _sim_get_from_sources(sources, ("player_exp_max", "exp_max"), 100),
                "oro_current": _sim_get_from_sources(sources, ("player_oro", "player_gold", "oro_current"), 0),
                "stars": _sim_get_from_sources(sources, ("player_stars",), {}),
                "flags": _sim_get_from_sources(sources, ("player_flags",), {}),
            }
            norm_actors.append(_sim_build_actor_from_runtime("A", "player", a1, 0))

        if isinstance(actors_team_b, list) and len(actors_team_b) > 0:
            for i, a in enumerate(actors_team_b):
                norm_actors.append(_sim_build_actor_from_runtime("B", "enemy", a, i))
        else:
            b1 = {
                "actor_id": _sim_get_from_sources(sources, ("enemy_actor_id", "enemy_id"), "enemy_1"),
                "actor_type": _sim_get_from_sources(sources, ("enemy_actor_type",), "BETA"),
                "level": _sim_get_from_sources(sources, ("enemy_level",), 1),
                "register": _sim_get_from_sources(sources, ("enemy_register",), None),
                "exp_current": _sim_get_from_sources(sources, ("enemy_exp",), 0),
                "exp_max": _sim_get_from_sources(sources, ("enemy_exp_max",), 100),
                "oro_current": _sim_get_from_sources(sources, ("enemy_oro", "enemy_gold"), 0),
                "stars": _sim_get_from_sources(sources, ("enemy_stars",), {}),
                "flags": _sim_get_from_sources(sources, ("enemy_flags",), {}),
            }
            norm_actors.append(_sim_build_actor_from_runtime("B", "enemy", b1, 0))

        team_a_count = len([x for x in norm_actors if x.get("team") == "A"])
        team_b_count = len([x for x in norm_actors if x.get("team") == "B"])
        mode = "custom"
        if team_a_count == 1 and team_b_count == 1:
            mode = "1v1"
        elif team_a_count == 2 and team_b_count == 1:
            mode = "2v1"
        elif team_a_count == 1 and team_b_count == 2:
            mode = "1v2"
        elif team_a_count == 2 and team_b_count == 2:
            mode = "2v2"

        simulation_id = str(_sim_get_from_sources(sources, ("simulation_id", "battle_id", "match_id"), "battle_sim_v1") or "battle_sim_v1")
        reward_event_id = str(_sim_get_from_sources(sources, ("reward_event_id",), "") or "").strip()
        if reward_event_id == "":
            reward_event_id = _sim_build_reward_event_id({
                "simulation_id": simulation_id,
                "battle_id": _sim_get_from_sources(sources, ("battle_id",), simulation_id),
                "match_id": _sim_get_from_sources(sources, ("match_id",), simulation_id),
                "turn_index": _sim_get_from_sources(sources, ("turn_index", "turn"), 0),
            }, winner_team, source)

        req = {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": simulation_id,
            "mode": mode,
            "source": source,
            "event_type": event_type,
            "winner_team": winner_team,
            "reward_event_id": reward_event_id,
            "actors": norm_actors,
            "config": {
                "preset": str(_sim_get_from_sources(sources, ("preset",), "medium_v2") or "medium_v2"),
                "allow_mid_battle_grants": bool(_sim_get_from_sources(sources, ("allow_mid_battle_grants",), True)),
                "repetition_count": max(1, _sim_to_int(_sim_get_from_sources(sources, ("repetition_count",), 1), 1)),
                "multi_factor_enabled": bool(_sim_get_from_sources(sources, ("multi_factor_enabled",), True)),
                "idempotency_registry": _sim_get_from_sources(sources, ("idempotency_registry",), {}),
            },
        }

        # Overrides finales explícitos.
        for k, v in ov.items():
            if k in ("sim_contract_version", "simulation_id", "mode", "source", "event_type", "winner_team", "reward_event_id", "actors", "config"):
                req[k] = copy.deepcopy(v)

        return req

    def sim_run_battle_end_simulation(runtime=None, overrides=None):
        """
        C2 - Ejecuta pipeline de cierre:
        runtime -> SimulationRequest -> run_simulation.
        """
        req = sim_build_request_from_battle_state(runtime=runtime, overrides=overrides)
        res = run_simulation(req)
        return {
            "request": req,
            "result": res,
        }

    def sim_persist_simulation_artifacts(sim_pack, max_log_items=300):
        """
        C5 - Persistencia de audit + idempotency registry.
        Guarda:
          - registry en store (session/runtime)
          - snapshots de auditoría en persistent
        """
        import renpy
        import renpy.store as S

        pack = sim_pack if isinstance(sim_pack, dict) else {}
        req = pack.get("request", {}) if isinstance(pack.get("request", {}), dict) else {}
        res = pack.get("result", {}) if isinstance(pack.get("result", {}), dict) else {}
        audit = res.get("audit", {}) if isinstance(res.get("audit", {}), dict) else {}
        idem = audit.get("idempotency", {}) if isinstance(audit.get("idempotency", {}), dict) else {}

        registry_out = idem.get("registry_out", {}) if isinstance(idem.get("registry_out", {}), dict) else {}
        S.sim_idempotency_registry_v1 = copy.deepcopy(registry_out)
        # Alias para C1/C2 (sources lookup por clave directa).
        S.idempotency_registry = copy.deepcopy(registry_out)

        snap = {
            "ts_unix": int(time.time()),
            "simulation_id": str(res.get("simulation_id", req.get("simulation_id", "sim_unknown")) or "sim_unknown"),
            "source": str(req.get("source", "unknown") or "unknown"),
            "mode": str(res.get("mode", req.get("mode", "custom")) or "custom"),
            "winner_team": str(res.get("winner_team", req.get("winner_team", "DRAW")) or "DRAW"),
            "reward_event_id": str(req.get("reward_event_id", "") or ""),
            "errors": list(audit.get("errors", [])) if isinstance(audit.get("errors", []), list) else [],
            "warnings": list(audit.get("warnings", [])) if isinstance(audit.get("warnings", []), list) else [],
            "idempotency": {
                "enabled": bool(idem.get("enabled", False)),
                "event_id": str(idem.get("event_id", "") or ""),
                "statuses": list(idem.get("statuses", [])) if isinstance(idem.get("statuses", []), list) else [],
                "registry_size": len(registry_out),
            },
        }

        cur = getattr(S.persistent, "sim_audit_log_v1", None)
        if not isinstance(cur, list):
            cur = []
        cur.append(snap)

        lim = max(50, _sim_to_int(max_log_items, 300))
        if len(cur) > lim:
            cur = cur[-lim:]
        S.persistent.sim_audit_log_v1 = cur
        renpy.save_persistent()

        return {
            "ok": True,
            "registry_size": len(registry_out),
            "audit_items": len(cur),
            "last_snapshot": snap,
        }

    def sim_apply_simulation_rewards_to_runtime(sim_pack):
        """
        C3 - Aplicación real de recompensas visibles (v1).
        Alcance:
          - Aplica rewards para actor_type PLAYER / ALPHA / DELTA.
          - PLAYER: muta player_exp/player_oro + bridge opcional panel RPG.
          - ALPHA/DELTA: muta wallet runtime por actor_id.
          - Mantiene trazabilidad en `sim_battle_end_last_apply_v1`.
        """
        import renpy.store as S

        pack = sim_pack if isinstance(sim_pack, dict) else {}
        req = pack.get("request", {}) if isinstance(pack.get("request", {}), dict) else {}
        res = pack.get("result", {}) if isinstance(pack.get("result", {}), dict) else {}
        actors = req.get("actors", []) if isinstance(req.get("actors", []), list) else []
        results = res.get("results", []) if isinstance(res.get("results", []), list) else []

        actor_by_id = {}
        for a in actors:
            if isinstance(a, dict):
                actor_by_id[str(a.get("actor_id", ""))] = a

        applied = []
        total_exp = 0
        total_oro = 0

        # Wallet runtime para ALPHA/DELTA (persistencia de sesión).
        wallet = getattr(S, "sim_actor_runtime_wallet_v1", None)
        if not isinstance(wallet, dict):
            wallet = {}

        for rr in results:
            if not isinstance(rr, dict):
                continue
            actor_id = str(rr.get("actor_id", "") or "")
            a = actor_by_id.get(actor_id, {})
            actor_type = str(a.get("actor_type", "") or "").upper()
            eligible = bool(rr.get("eligible", False))
            ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
            exp_gain = max(0, _sim_to_int(ff.get("exp_gain", 0), 0))
            oro_gain = max(0, _sim_to_int(ff.get("oro_gain", 0), 0))

            if (not eligible) or actor_type not in ("PLAYER", "ALPHA", "DELTA"):
                continue
            if exp_gain <= 0 and oro_gain <= 0:
                continue

            if actor_type == "PLAYER":
                # Store runtime principal (jugador).
                S.player_exp = max(0, _sim_to_int(getattr(S, "player_exp", 0), 0) + exp_gain)
                S.player_oro = max(0, _sim_to_int(getattr(S, "player_oro", 0), 0) + oro_gain)

                # Bridge opcional con panel RPG.
                st = getattr(S, "rpg_panel_state_v1", None)
                if isinstance(st, dict):
                    p = st.get("player", {}) if isinstance(st.get("player", {}), dict) else {}
                    p["exp_current"] = max(0, _sim_to_int(p.get("exp_current", 0), 0) + exp_gain)
                    p["oro_current"] = max(0, _sim_to_int(p.get("oro_current", 0), 0) + oro_gain)
                    st["player"] = p
                    S.rpg_panel_state_v1 = st
            else:
                # Runtime wallet para actores progresables no jugador (ALPHA/DELTA).
                cur = wallet.get(actor_id, {}) if isinstance(wallet.get(actor_id, {}), dict) else {}
                cur["actor_id"] = actor_id
                cur["actor_type"] = actor_type
                cur["exp"] = max(0, _sim_to_int(cur.get("exp", 0), 0) + exp_gain)
                cur["oro"] = max(0, _sim_to_int(cur.get("oro", 0), 0) + oro_gain)
                wallet[actor_id] = cur

            total_exp += exp_gain
            total_oro += oro_gain
            applied.append({
                "actor_id": actor_id,
                "actor_type": actor_type,
                "exp_gain": exp_gain,
                "oro_gain": oro_gain,
            })

        S.sim_actor_runtime_wallet_v1 = wallet

        report = {
            "ok": True,
            "applied_count": len(applied),
            "total_exp": total_exp,
            "total_oro": total_oro,
            "items": applied,
        }
        S.sim_battle_end_last_apply_v1 = report
        return report

    def sim_apply_reward_event_idempotency(normalized_request, results):
        """
        A5 - Anti-duplicación por reward_event_id.
        No muta estado externo: devuelve registry_out para que caller lo persista.
        """
        req = normalized_request if isinstance(normalized_request, dict) else {}
        r_in = results if isinstance(results, list) else []
        out_results = copy.deepcopy(r_in)

        warnings = []
        errors = []
        statuses = []

        event_id = str(req.get("reward_event_id", "") or "").strip()
        source = str(req.get("source", "lab_manual") or "lab_manual")
        cfg = req.get("config", {}) if isinstance(req.get("config", {}), dict) else {}
        registry_in = cfg.get("idempotency_registry", {})
        registry = copy.deepcopy(registry_in if isinstance(registry_in, dict) else {})

        if event_id == "":
            return {
                "results": out_results,
                "warnings": warnings,
                "errors": errors,
                "audit": {
                    "enabled": False,
                    "reason": "missing_reward_event_id",
                    "statuses": [],
                    "registry_out": registry,
                },
            }

        for rr in out_results:
            actor_id = str(rr.get("actor_id", "unknown") or "unknown")
            key = "%s|%s|%s" % (event_id, actor_id, source)
            fp = "%s|%s|%s|%s|%s" % (
                int(rr.get("final", {}).get("exp_gain", 0) or 0),
                int(rr.get("final", {}).get("oro_gain", 0) or 0),
                str(rr.get("outcome", "unknown") or "unknown"),
                int(rr.get("stars_total", 0) or 0),
                int(rr.get("delta_register", 0) or 0),
            )

            if key not in registry:
                registry[key] = fp
                statuses.append({"key": key, "status": "APPLY_OK"})
                continue

            prev = str(registry.get(key, "") or "")
            if prev == fp:
                # duplicado exacto: no volver a pagar
                statuses.append({"key": key, "status": "DUPLICATE_IGNORED"})
                warnings.append("reward_event_id duplicado ignorado para actor_id=%s." % actor_id)
            else:
                # mismo id, payload distinto
                statuses.append({"key": key, "status": "DUPLICATE_CONFLICT"})
                errors.append("reward_event_id en conflicto para actor_id=%s." % actor_id)

            ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
            exp_before = max(0, _sim_to_int(ff.get("exp_after", 0), 0) - _sim_to_int(ff.get("exp_gain", 0), 0))
            oro_before = max(0, _sim_to_int(ff.get("oro_after", 0), 0) - _sim_to_int(ff.get("oro_gain", 0), 0))
            ff["exp_gain"] = 0
            ff["oro_gain"] = 0
            ff["exp_after"] = exp_before
            ff["oro_after"] = oro_before
            rr["final"] = ff
            notes = rr.get("notes", []) if isinstance(rr.get("notes", []), list) else []
            notes.append("duplicate_reward_event_id")
            rr["notes"] = notes

        return {
            "results": out_results,
            "warnings": warnings,
            "errors": errors,
            "audit": {
                "enabled": True,
                "event_id": event_id,
                "statuses": statuses,
                "registry_out": registry,
            },
        }

    # ======================================
    # A6 + A7 helpers (tests y fixtures base)
    # ======================================

    def sim_phaseA_fixture_requests():
        """
        A7 - Fixtures reproducibles base.
        """
        base = sim_build_min_request()
        base["event_type"] = "victory"
        base["winner_team"] = "A"
        base["reward_event_id"] = "fixture::c::1v1::dr0"

        fix_a = {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": "fixture_a_2v2",
            "mode": "2v2",
            "source": "lab_manual",
            "event_type": "victory",
            "winner_team": "A",
            "reward_event_id": "fixture::a::2v2::1",
            "actors": [
                {"actor_id": "a_l1", "actor_type": "PLAYER", "team": "A", "level": 1, "register": 0, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 4, "defensiva": 4, "control": 4, "eficiencia": 4, "tecnica": 3, "impacto": 3}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
                {"actor_id": "a_l30", "actor_type": "ALPHA", "team": "A", "level": 30, "register": 3, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 3, "defensiva": 3, "control": 3, "eficiencia": 3, "tecnica": 3, "impacto": 3}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
                {"actor_id": "b_l30", "actor_type": "ALPHA", "team": "B", "level": 30, "register": 3, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 2, "defensiva": 2, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
                {"actor_id": "b_l10", "actor_type": "ALPHA", "team": "B", "level": 10, "register": 1, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 1, "defensiva": 1, "control": 1, "eficiencia": 1, "tecnica": 1, "impacto": 1}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
            ],
            "config": {"preset": "medium_v2", "allow_mid_battle_grants": True, "repetition_count": 1, "multi_factor_enabled": True},
        }

        fix_b = {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": "fixture_b_2v1",
            "mode": "2v1",
            "source": "lab_manual",
            "event_type": "victory",
            "winner_team": "B",
            "reward_event_id": "fixture::b::2v1::1",
            "actors": [
                {"actor_id": "a_l20", "actor_type": "ALPHA", "team": "A", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 3, "defensiva": 3, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
                {"actor_id": "a_l30", "actor_type": "ALPHA", "team": "A", "level": 30, "register": 3, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 3, "defensiva": 3, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
                {"actor_id": "b_l10", "actor_type": "PLAYER", "team": "B", "level": 10, "register": 1, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 5, "defensiva": 4, "control": 4, "eficiencia": 4, "tecnica": 4, "impacto": 5}, "flags": {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}},
            ],
            "config": {"preset": "medium_v2", "allow_mid_battle_grants": True, "repetition_count": 1, "multi_factor_enabled": True},
        }

        return {
            "fixture_a_2v2": fix_a,
            "fixture_b_2v1": fix_b,
            "fixture_c_1v1_dr0": base,
        }

    def sim_run_phaseA_tests():
        """
        A6 - Batería mínima de tests unitarios (runtime helper).
        Retorna lista de resultados {name, ok, detail}.
        """
        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        # Caso feliz 1v1
        r1 = sim_build_min_request()
        r1["event_type"] = "victory"
        r1["winner_team"] = "A"
        r1["reward_event_id"] = "t::1"
        s1 = run_simulation(r1)
        _push("1v1_victory_ok", len(s1.get("results", [])) == 1 and s1["results"][0]["final"]["exp_gain"] >= 0)

        # Derrota parcial
        r2 = sim_build_min_request()
        r2["event_type"] = "defeat"
        r2["winner_team"] = "B"
        r2["reward_event_id"] = "t::2"
        s2 = run_simulation(r2)
        _push("defeat_partial_reward", len(s2.get("results", [])) == 1 and s2["results"][0]["outcome"] == "defeat")

        # Empate
        r3 = sim_build_min_request()
        r3["event_type"] = "draw"
        r3["winner_team"] = "DRAW"
        r3["reward_event_id"] = "t::3"
        s3 = run_simulation(r3)
        _push("draw_reward", len(s3.get("results", [])) == 1 and s3["results"][0]["outcome"] == "draw")

        # 2v1 multi factor
        fx = sim_phaseA_fixture_requests()["fixture_b_2v1"]
        s4 = run_simulation(fx)
        ok4 = (len(s4.get("results", [])) == 3)
        _push("2v1_multi_factor_shape", ok4)

        # GAMMA no elegible
        r5 = sim_build_min_request()
        r5["actors"][0]["actor_type"] = "GAMMA"
        r5["actors"][0]["flags"]["eligible_rewards"] = True
        r5["reward_event_id"] = "t::5"
        s5 = run_simulation(r5)
        ok5 = (len(s5.get("results", [])) == 1 and not bool(s5["results"][0].get("eligible", True)))
        _push("gamma_not_eligible", ok5)

        # Clamp estrellas
        r6 = sim_build_min_request()
        r6["actors"][0]["stars"] = {k: 99 for k in SIM_STAR_KEYS}
        r6["reward_event_id"] = "t::6"
        v6 = sim_validate_request(r6)
        ok6 = bool(v6.get("normalized", {}).get("actors", [{}])[0].get("stars_total", 0) == 30)
        _push("stars_clamp_0_30", ok6)

        # Duplicado reward_event_id
        r7 = sim_build_min_request()
        r7["event_type"] = "victory"
        r7["winner_team"] = "A"
        r7["reward_event_id"] = "t::7"
        r7["config"]["idempotency_registry"] = {}
        s7a = run_simulation(r7)
        reg = s7a.get("audit", {}).get("idempotency", {}).get("registry_out", {})
        r7b = copy.deepcopy(r7)
        r7b["config"]["idempotency_registry"] = reg
        s7b = run_simulation(r7b)
        ok7 = (s7b.get("results", [{}])[0].get("final", {}).get("exp_gain", -1) == 0)
        _push("duplicate_reward_event_id", ok7)

        return out

    def sim_export_phaseA_fixtures_json():
        """
        A7 - Export en memoria de fixtures + outputs para diff de versión.
        """
        fx = sim_phaseA_fixture_requests()
        out = {}
        for k, req in fx.items():
            out[k] = run_simulation(req)
        return json.dumps({
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "fixtures": fx,
            "outputs": out,
        }, ensure_ascii=False, sort_keys=True, indent=2)

    def sim_phaseA_checkpoint_report():
        """
        A8 - Reporte consolidado de cierre de Fase A.
        """
        tests = sim_run_phaseA_tests()
        total = len(tests)
        passed = 0
        failed_names = []
        for t in tests:
            ok = bool((t or {}).get("ok", False))
            if ok:
                passed += 1
            else:
                failed_names.append(str((t or {}).get("name", "unknown")))

        return {
            "phase": "A",
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "deliverables": {
                "contract_v1_stable": True,
                "run_simulation_available": True,
                "fixtures_available": True,
                "tests_available": True,
                "params_changelog_available": True,
            },
            "tests": {
                "total": total,
                "passed": passed,
                "failed": (total - passed),
                "failed_names": failed_names,
                "results": tests,
            },
            "params_changelog": {
                "preset_default": "medium_v2",
                "stars_range_per_category": "0..5",
                "stars_total_range": "0..30",
                "register_range": "0..50",
                "risk_tables": {
                    "exp": copy.deepcopy(SIM_RISK_EXP_TABLE),
                    "oro": copy.deepcopy(SIM_RISK_ORO_TABLE),
                },
                "multi_factor_formula": "clamp((enemies/allies)^0.5, 0.85, 1.35)",
                "antiabuso_repetition": {
                    "1": 1.00,
                    "2": 0.60,
                    "3": 0.30,
                    "4_plus": 0.10,
                },
                "idempotency_key": "reward_event_id|actor_id|source",
            },
        }

    def sim_run_c1_adapter_smoke_tests():
        """
        C1 - Smoke tests del adaptador runtime->request.
        """
        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        # Caso 1: fallback mínimo 1v1 desde estado base.
        req1 = sim_build_request_from_battle_state({
            "battle_id": "smoke_c1_1",
            "player_hp": 150,
            "enemy_hp": 0,
            "player_level": 12,
            "enemy_level": 6,
        })
        v1 = sim_validate_request(req1)
        _push("c1_min_1v1_request_valid", bool(v1.get("ok", False)))

        # Caso 2: 2v2 desde listas explícitas.
        req2 = sim_build_request_from_battle_state({
            "battle_id": "smoke_c1_2",
            "result": "victory",
            "team_a_actors": [
                {"actor_id": "a1", "actor_type": "PLAYER", "level": 10, "register": 1},
                {"actor_id": "a2", "actor_type": "ALPHA", "level": 20, "register": 2},
            ],
            "team_b_actors": [
                {"actor_id": "b1", "actor_type": "BETA", "level": 20, "register": 2},
                {"actor_id": "b2", "actor_type": "BETA", "level": 30, "register": 3},
            ],
        })
        v2 = sim_validate_request(req2)
        ok2 = bool(v2.get("ok", False)) and str(v2.get("normalized", {}).get("mode", "")) == "2v2"
        _push("c1_explicit_2v2_valid", ok2)

        # Caso 3: event id autogenerado cuando no viene en runtime.
        rid = str(req2.get("reward_event_id", "") or "")
        _push("c1_reward_event_id_autogen", rid != "")

        return out

    def sim_run_phaseC_e2e_tests():
        """
        C6 - QA E2E mínimo para integración C2/C5/C3/C4.
        Retorna lista [{name, ok, detail}].
        """
        import renpy.store as S

        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        # Snapshot para evitar side-effects en sesión QA.
        snap_player_exp = _sim_to_int(getattr(S, "player_exp", 0), 0)
        snap_player_oro = _sim_to_int(getattr(S, "player_oro", 0), 0)
        snap_registry = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        snap_apply = copy.deepcopy(getattr(S, "sim_battle_end_last_apply_v1", {}))
        snap_wallet = copy.deepcopy(getattr(S, "sim_actor_runtime_wallet_v1", {}))

        try:
            runtime = {
                "source": "battle_end",
                "battle_id": "c6_e2e_1v1",
                "result": "victory",
                "player_hp": 120,
                "enemy_hp": 0,
                "player_level": 10,
                "player_register": 1,
                "player_exp": snap_player_exp,
                "player_exp_max": 100,
                "player_oro": snap_player_oro,
                "player_actor_type": "PLAYER",
                "enemy_level": 10,
                "enemy_register": 1,
                "enemy_actor_type": "BETA",
                "idempotency_registry": copy.deepcopy(snap_registry),
            }

            # 1) Simulación y aplicación inicial.
            pack1 = sim_run_battle_end_simulation(runtime=runtime)
            res1 = pack1.get("result", {}) if isinstance(pack1.get("result", {}), dict) else {}
            rows1 = res1.get("results", []) if isinstance(res1.get("results", []), list) else []
            apply1 = sim_apply_simulation_rewards_to_runtime(pack1)
            persist1 = sim_persist_simulation_artifacts(pack1)

            ok1 = isinstance(rows1, list) and len(rows1) >= 1 and bool(apply1.get("ok", False))
            _push("c6_real_1v1_pipeline", ok1)

            # 2) Reintento mismo evento -> no doble pago.
            reg_after_1 = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
            runtime_retry = copy.deepcopy(runtime)
            runtime_retry["idempotency_registry"] = reg_after_1
            pack2 = sim_run_battle_end_simulation(runtime=runtime_retry)
            apply2 = sim_apply_simulation_rewards_to_runtime(pack2)
            no_double = (_sim_to_int(apply2.get("total_exp", -1), -1) == 0 and _sim_to_int(apply2.get("total_oro", -1), -1) == 0)
            _push("c6_no_double_payment_retry", no_double)

            # 2b) C3 ampliado: aplica también ALPHA/DELTA en wallet runtime.
            req_ad = {
                "sim_contract_version": SIM_CONTRACT_VERSION,
                "simulation_id": "c6_alpha_delta",
                "mode": "2v2",
                "source": "battle_end",
                "event_type": "victory",
                "winner_team": "A",
                "reward_event_id": "c6::alpha_delta::1",
                "actors": [
                    {"actor_id": "player_1", "actor_type": "PLAYER", "team": "A", "level": 10, "register": 1, "exp_current": snap_player_exp, "exp_max": 100, "oro_current": snap_player_oro, "stars": {"ofensiva": 4, "defensiva": 4, "control": 4, "eficiencia": 4, "tecnica": 4, "impacto": 4}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "alpha_a1", "actor_type": "ALPHA", "team": "A", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 3, "defensiva": 3, "control": 3, "eficiencia": 3, "tecnica": 3, "impacto": 3}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "delta_b1", "actor_type": "DELTA", "team": "B", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 2, "defensiva": 2, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "beta_b2", "actor_type": "BETA", "team": "B", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 1, "defensiva": 1, "control": 1, "eficiencia": 1, "tecnica": 1, "impacto": 1}, "flags": {"eligible_rewards": True}},
                ],
                "config": {"preset": "medium_v2", "allow_mid_battle_grants": True, "repetition_count": 1, "multi_factor_enabled": True},
            }
            pack_ad = {"request": req_ad, "result": run_simulation(req_ad)}
            sim_apply_simulation_rewards_to_runtime(pack_ad)
            wallet_after = getattr(S, "sim_actor_runtime_wallet_v1", {})
            ok_ad = (
                isinstance(wallet_after, dict) and
                "alpha_a1" in wallet_after and
                "delta_b1" in wallet_after and
                "beta_b2" not in wallet_after
            )
            _push("c6_c3_alpha_delta_wallet_apply", ok_ad)

            # 3) Coherencia cálculo vs resumen/aplicación (C4 consume estos mismos datos).
            sum_exp = 0
            sum_oro = 0
            for rr in rows1:
                if not isinstance(rr, dict):
                    continue
                ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
                if bool(rr.get("eligible", False)):
                    sum_exp += max(0, _sim_to_int(ff.get("exp_gain", 0), 0))
                    sum_oro += max(0, _sim_to_int(ff.get("oro_gain", 0), 0))

            # C3 aplica PLAYER/ALPHA/DELTA; el total aplicado no debe exceder elegible.
            ok3 = (
                _sim_to_int(apply1.get("total_exp", -1), -1) >= 0 and
                _sim_to_int(apply1.get("total_oro", -1), -1) >= 0 and
                _sim_to_int(apply1.get("total_exp", 0), 0) <= sum_exp and
                _sim_to_int(apply1.get("total_oro", 0), 0) <= sum_oro
            )
            _push("c6_view_matches_calculation_source", ok3)

            # 4) Persistencia mínima disponible.
            _push("c6_audit_registry_persisted", bool(persist1.get("ok", False)))

        finally:
            # Restore snapshot (safe helper QA).
            S.player_exp = snap_player_exp
            S.player_oro = snap_player_oro
            S.sim_idempotency_registry_v1 = snap_registry
            S.sim_battle_end_last_apply_v1 = snap_apply
            S.sim_actor_runtime_wallet_v1 = snap_wallet

        return out
