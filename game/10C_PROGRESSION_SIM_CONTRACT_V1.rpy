# ===============================================================
# 10C_PROGRESSION_SIM_CONTRACT_V1.rpy
# Fase A (A1 + A2) — Contrato y validación del simulador
# ===============================================================

init -875 python:

    import copy

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

        return {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": str(req.get("simulation_id", "sim_unknown")),
            "mode": str(req.get("mode", "custom")),
            "winner_team": str(winner_team),
            "results": results,
            "audit": {
                "warnings": warnings,
                "errors": errors,
                "sim_contract_version": SIM_CONTRACT_VERSION,
            },
        }
