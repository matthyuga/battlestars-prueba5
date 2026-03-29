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

