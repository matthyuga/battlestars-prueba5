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
    SIM_ALLOWED_MID_BATTLE_EVENTS = ("passive_proc", "technique_proc", "item_proc")

    # D1 - Catálogo canónico de eventos mid-battle.
    SIM_MID_BATTLE_EVENT_CATALOG_V1 = {
        "passive_proc": {
            "enabled": True,
            "description": "Proc de pasiva por condición de combate.",
            "allowed_actor_types": ("PLAYER", "ALPHA", "DELTA"),
            "required_fields": ("event_key", "actor_id", "match_id", "trigger_uid"),
        },
        "technique_proc": {
            "enabled": True,
            "description": "Activación exitosa de técnica especial.",
            "allowed_actor_types": ("PLAYER", "ALPHA", "DELTA"),
            "required_fields": ("event_key", "actor_id", "match_id", "trigger_uid"),
        },
        "item_proc": {
            "enabled": True,
            "description": "Disparo de recompensa condicional por item.",
            "allowed_actor_types": ("PLAYER", "ALPHA", "DELTA"),
            "required_fields": ("event_key", "actor_id", "match_id", "trigger_uid"),
        },
    }

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

    def _sim_save_persistent_compat():
        """
        Compat Ren'Py 7.x/8.x:
        - algunas versiones exponen renpy.save_persistent()
        - otras requieren renpy.loadsave.save_persistent()
        """
        import renpy
        fn = getattr(renpy, "save_persistent", None)
        if callable(fn):
            fn()
            return True
        ls = getattr(renpy, "loadsave", None)
        fn2 = getattr(ls, "save_persistent", None) if ls is not None else None
        if callable(fn2):
            fn2()
            return True
        return False

    def sim_build_mid_battle_reward_event_id(event_ctx):
        ec = event_ctx if isinstance(event_ctx, dict) else {}
        match_id = str(ec.get("match_id", "match_unknown") or "match_unknown")
        event_key = str(ec.get("event_key", "event_unknown") or "event_unknown")
        actor_id = str(ec.get("actor_id", "actor_unknown") or "actor_unknown")
        trigger_uid = str(ec.get("trigger_uid", "t0") or "t0")
        return "mbe::%s::%s::%s::%s" % (match_id, event_key, actor_id, trigger_uid)

    def sim_is_mid_battle_actor_authorized(event_ctx, battle_ctx=None):
        """
        E3 - Regla mínima host/invitado para grants mid-battle.
        Si multiplayer no está activo, permite (compat backward).
        """
        ec = event_ctx if isinstance(event_ctx, dict) else {}
        bc = battle_ctx if isinstance(battle_ctx, dict) else {}

        if not bool(bc.get("multiplayer_enabled", False)):
            return {"ok": True, "reason": "single_player_or_disabled"}

        actor_id = str(ec.get("actor_id", "") or "").strip()
        if actor_id == "":
            return {"ok": False, "reason": "missing_actor_id"}

        host_actor_id = str(bc.get("host_actor_id", "") or "").strip()
        strict_host_only = bool(bc.get("strict_host_only", False))
        guest_ids = bc.get("allowed_guest_actor_ids", [])
        if not isinstance(guest_ids, list):
            guest_ids = []
        guest_set = set([str(x or "").strip() for x in guest_ids if str(x or "").strip() != ""])

        if strict_host_only:
            if host_actor_id != "" and actor_id == host_actor_id:
                return {"ok": True, "reason": "host_allowed_strict"}
            return {"ok": False, "reason": "strict_host_only_block"}

        if host_actor_id != "" and actor_id == host_actor_id:
            return {"ok": True, "reason": "host_allowed"}
        if actor_id in guest_set:
            return {"ok": True, "reason": "guest_allowed"}
        return {"ok": False, "reason": "actor_not_allowed_in_session"}

    def sim_validate_mid_battle_event(event_ctx):
        """
        D1 - Validador de catálogo de eventos mid-battle.
        """
        ec = copy.deepcopy(event_ctx if isinstance(event_ctx, dict) else {})
        errors = []
        warnings = []

        event_key = str(ec.get("event_key", "") or "").strip()
        if event_key not in SIM_ALLOWED_MID_BATTLE_EVENTS:
            errors.append("event_key inválido/no catalogado: %s" % event_key)
            return {"ok": False, "errors": errors, "warnings": warnings, "normalized": ec}

        meta = SIM_MID_BATTLE_EVENT_CATALOG_V1.get(event_key, {})
        if not bool(meta.get("enabled", False)):
            errors.append("event_key deshabilitado: %s" % event_key)

        req_fields = meta.get("required_fields", ())
        for f in req_fields:
            vv = ec.get(f, None)
            if vv is None or str(vv).strip() == "":
                errors.append("campo requerido ausente en mid_battle_event: %s" % f)

        actor_type = str(ec.get("actor_type", "PLAYER") or "PLAYER").upper()
        allowed_types = meta.get("allowed_actor_types", ())
        if len(allowed_types) > 0 and actor_type not in allowed_types:
            errors.append("actor_type no permitido para %s: %s" % (event_key, actor_type))

        ec["source"] = "mid_battle_event"
        ec["event_type"] = "conditional_gain"
        ec["event_key"] = event_key
        ec["actor_type"] = actor_type

        if str(ec.get("reward_event_id", "") or "").strip() == "":
            ec["reward_event_id"] = sim_build_mid_battle_reward_event_id(ec)
            warnings.append("reward_event_id no provisto; se autogenera desde match/event/actor/trigger.")

        # canon para dedupe semántico adicional
        ec["canonical_trigger_key"] = "%s|%s|%s|%s" % (
            str(ec.get("match_id", "") or ""),
            event_key,
            str(ec.get("actor_id", "") or ""),
            str(ec.get("trigger_uid", "") or ""),
        )

        return {
            "ok": (len(errors) == 0),
            "errors": errors,
            "warnings": warnings,
            "normalized": ec,
        }

    def sim_build_request_from_mid_battle_event(event_ctx, battle_ctx=None):
        """
        D2 - Bridge evento mid-battle -> Partial SimulationRequest.
        """
        vv = sim_validate_mid_battle_event(event_ctx)
        ec = vv.get("normalized", {}) if isinstance(vv.get("normalized", {}), dict) else {}
        errors = list(vv.get("errors", [])) if isinstance(vv.get("errors", []), list) else []
        warnings = list(vv.get("warnings", [])) if isinstance(vv.get("warnings", []), list) else []
        bc = battle_ctx if isinstance(battle_ctx, dict) else {}

        if not vv.get("ok", False):
            return {
                "ok": False,
                "errors": errors,
                "warnings": warnings,
                "request": {},
                "event": ec,
            }

        # Actores desde contexto de combate si existe; fallback parcial por evento.
        actors = []
        team_a = bc.get("team_a_actors", None)
        team_b = bc.get("team_b_actors", None)

        if isinstance(team_a, list) and isinstance(team_b, list) and (len(team_a) + len(team_b) > 0):
            for i, a in enumerate(team_a):
                actors.append(_sim_build_actor_from_runtime("A", "ally", a, i))
            for i, a in enumerate(team_b):
                actors.append(_sim_build_actor_from_runtime("B", "enemy", a, i))
        else:
            # Fallback: actor evento + rival placeholder para mantener shape de simulación.
            ev_actor = {
                "actor_id": str(ec.get("actor_id", "event_actor") or "event_actor"),
                "actor_type": str(ec.get("actor_type", "PLAYER") or "PLAYER"),
                "level": _sim_to_int(ec.get("level", 1), 1),
                "register": ec.get("register", None),
                "exp_current": _sim_to_int(ec.get("exp_current", 0), 0),
                "exp_max": max(1, _sim_to_int(ec.get("exp_max", 100), 100)),
                "oro_current": _sim_to_int(ec.get("oro_current", 0), 0),
                "stars": ec.get("stars", {k: 0 for k in SIM_STAR_KEYS}),
                "flags": ec.get("flags", {"eligible_rewards": True, "allow_level_up": True, "allow_inventory_rewards": True}),
            }
            ev_team = str(ec.get("team", "A") or "A").upper()
            if ev_team not in ("A", "B"):
                ev_team = "A"
            rv_team = "B" if ev_team == "A" else "A"
            actors.append(_sim_build_actor_from_runtime(ev_team, "ally", ev_actor, 0))
            actors.append(_sim_build_actor_from_runtime(rv_team, "enemy", {
                "actor_id": "mid_dummy_rival",
                "actor_type": "BETA",
                "level": max(1, _sim_to_int(ec.get("rival_level", ev_actor["level"]), ev_actor["level"])),
                "register": ec.get("rival_register", ev_actor.get("register", 0)),
                "exp_current": 0,
                "exp_max": 100,
                "oro_current": 0,
                "stars": {k: 0 for k in SIM_STAR_KEYS},
                "flags": {"eligible_rewards": False, "allow_level_up": False, "allow_inventory_rewards": False},
            }, 0))
            warnings.append("battle_ctx sin equipos; se usa rival placeholder para request parcial.")

        team_a_count = len([x for x in actors if str(x.get("team", "")).upper() == "A"])
        team_b_count = len([x for x in actors if str(x.get("team", "")).upper() == "B"])
        mode = "custom"
        if team_a_count == 1 and team_b_count == 1:
            mode = "1v1"
        elif team_a_count == 2 and team_b_count == 1:
            mode = "2v1"
        elif team_a_count == 1 and team_b_count == 2:
            mode = "1v2"
        elif team_a_count == 2 and team_b_count == 2:
            mode = "2v2"

        match_id = str(ec.get("match_id", bc.get("match_id", "match_unknown")) or "match_unknown")
        req = {
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "simulation_id": "mid_%s" % match_id,
            "mode": str(bc.get("mode", mode) or mode),
            "source": "mid_battle_event",
            "event_type": "conditional_gain",
            "winner_team": "DRAW",
            "reward_event_id": str(ec.get("reward_event_id", sim_build_mid_battle_reward_event_id(ec)) or sim_build_mid_battle_reward_event_id(ec)),
            "actors": actors,
            "config": {
                "preset": str(bc.get("preset", "medium_v2") or "medium_v2"),
                "allow_mid_battle_grants": True,
                "repetition_count": max(1, _sim_to_int(bc.get("repetition_count", 1), 1)),
                "multi_factor_enabled": bool(bc.get("multi_factor_enabled", True)),
                "idempotency_registry": bc.get("idempotency_registry", {}),
            },
            "mid_battle_meta": {
                "event_key": str(ec.get("event_key", "") or ""),
                "trigger_uid": str(ec.get("trigger_uid", "") or ""),
                "canonical_trigger_key": str(ec.get("canonical_trigger_key", "") or ""),
                "match_id": match_id,
                "session_id": str(bc.get("session_id", "") or ""),
                "host_actor_id": str(bc.get("host_actor_id", "") or ""),
            },
        }

        vr = sim_validate_request(req)
        if not vr.get("ok", False):
            errors.extend(vr.get("errors", []))
        warnings.extend(vr.get("warnings", []))

        return {
            "ok": (len(errors) == 0),
            "errors": errors,
            "warnings": warnings,
            "request": vr.get("normalized", req),
            "event": ec,
        }

    def sim_run_mid_battle_event(event_ctx, battle_ctx=None):
        """
        D3 - Pipeline runtime para trigger mid-battle:
        build -> run -> persist -> apply
        """
        import renpy.store as S

        ec = event_ctx if isinstance(event_ctx, dict) else {}
        bc = copy.deepcopy(battle_ctx if isinstance(battle_ctx, dict) else {})

        if "idempotency_registry" not in bc:
            bc["idempotency_registry"] = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        if "match_id" not in bc:
            bc["match_id"] = str(getattr(S, "story_pilot_battle_id", "match_unknown") or "match_unknown")
        if "max_mid_battle_grants_per_match" not in bc:
            bc["max_mid_battle_grants_per_match"] = 12
        if "max_mid_battle_reward_ratio" not in bc:
            bc["max_mid_battle_reward_ratio"] = 0.40
        if "projected_end_exp" not in bc:
            bc["projected_end_exp"] = 1000
        if "projected_end_oro" not in bc:
            bc["projected_end_oro"] = 600

        bridge = sim_build_request_from_mid_battle_event(ec, bc)
        if not bridge.get("ok", False):
            return {
                "ok": False,
                "errors": list(bridge.get("errors", [])),
                "warnings": list(bridge.get("warnings", [])),
                "request": {},
                "result": {},
                "persist": {"ok": False},
                "apply": {"ok": False},
            }

        req = bridge.get("request", {}) if isinstance(bridge.get("request", {}), dict) else {}
        cfg = req.get("config", {}) if isinstance(req.get("config", {}), dict) else {}
        mm = req.get("mid_battle_meta", {}) if isinstance(req.get("mid_battle_meta", {}), dict) else {}
        match_id = str(mm.get("match_id", bc.get("match_id", "match_unknown")) or "match_unknown")

        if not bool(cfg.get("allow_mid_battle_grants", True)):
            return {
                "ok": False,
                "errors": [],
                "warnings": ["allow_mid_battle_grants=false: trigger ignorado."],
                "request": req,
                "result": {},
                "persist": {"ok": False, "skipped": True},
                "apply": {"ok": False, "skipped": True},
            }

        auth = sim_is_mid_battle_actor_authorized(ec, bc)
        if not bool(auth.get("ok", False)):
            return {
                "ok": False,
                "errors": [],
                "warnings": ["authz_block: %s" % str(auth.get("reason", "unknown") or "unknown")],
                "request": req,
                "result": {},
                "persist": {"ok": False, "skipped": True, "reason": "authz_block"},
                "apply": {"ok": False, "skipped": True, "reason": "authz_block"},
            }

        # D5 Guard rail #1: límite de grants por match.
        guards = getattr(S, "sim_mid_battle_guard_v1", None)
        if not isinstance(guards, dict):
            guards = {}
        g = guards.get(match_id, {}) if isinstance(guards.get(match_id, {}), dict) else {}
        grants_count = max(0, _sim_to_int(g.get("grants_count", 0), 0))
        max_count = max(1, _sim_to_int(bc.get("max_mid_battle_grants_per_match", 12), 12))
        if grants_count >= max_count:
            return {
                "ok": False,
                "errors": [],
                "warnings": ["guard_rail: max_mid_battle_grants_per_match alcanzado."],
                "request": req,
                "result": {},
                "persist": {"ok": False, "skipped": True, "reason": "max_grants_per_match"},
                "apply": {"ok": False, "skipped": True, "reason": "max_grants_per_match"},
            }

        res = run_simulation(req)
        pack = {
            "request": req,
            "result": res,
            "event": bridge.get("event", {}),
        }

        # D5 Guard rail #2: ratio máximo mid-battle respecto al cierre proyectado.
        rows = res.get("results", []) if isinstance(res.get("results", []), list) else []
        event_exp = 0
        event_oro = 0
        for rr in rows:
            if not isinstance(rr, dict):
                continue
            if not bool(rr.get("eligible", False)):
                continue
            ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
            event_exp += max(0, _sim_to_int(ff.get("exp_gain", 0), 0))
            event_oro += max(0, _sim_to_int(ff.get("oro_gain", 0), 0))

        current_exp = max(0, _sim_to_int(g.get("total_exp", 0), 0))
        current_oro = max(0, _sim_to_int(g.get("total_oro", 0), 0))
        ratio = float(bc.get("max_mid_battle_reward_ratio", 0.40) or 0.40)
        if ratio < 0.05:
            ratio = 0.05
        if ratio > 1.00:
            ratio = 1.00
        projected_end_exp = max(1, _sim_to_int(bc.get("projected_end_exp", 1000), 1000))
        projected_end_oro = max(1, _sim_to_int(bc.get("projected_end_oro", 600), 600))
        cap_exp = int(round(float(projected_end_exp) * ratio))
        cap_oro = int(round(float(projected_end_oro) * ratio))
        if (current_exp + event_exp) > cap_exp or (current_oro + event_oro) > cap_oro:
            # Persistimos intento, pero sin aplicar ni registrar en ledger de pagos.
            persist = sim_persist_simulation_artifacts(pack)
            return {
                "ok": False,
                "errors": [],
                "warnings": ["guard_rail: max_mid_battle_reward_ratio excedido."],
                "request": req,
                "result": res,
                "persist": persist,
                "apply": {"ok": False, "skipped": True, "reason": "max_mid_battle_reward_ratio"},
            }

        persist = sim_persist_simulation_artifacts(pack)
        apply_report = sim_apply_simulation_rewards_to_runtime(pack)

        # D4 base: ledger de pagos mid-battle por match/actor para reconciliación en battle_end.
        grants = getattr(S, "sim_mid_battle_grants_v1", None)
        if not isinstance(grants, dict):
            grants = {}
        by_match = grants.get(match_id, {}) if isinstance(grants.get(match_id, {}), dict) else {}
        for it in (apply_report.get("items", []) if isinstance(apply_report.get("items", []), list) else []):
            if not isinstance(it, dict):
                continue
            aid = str(it.get("actor_id", "") or "")
            if aid == "":
                continue
            row = by_match.get(aid, {}) if isinstance(by_match.get(aid, {}), dict) else {}
            row["exp_paid"] = max(0, _sim_to_int(row.get("exp_paid", 0), 0) + _sim_to_int(it.get("exp_gain", 0), 0))
            row["oro_paid"] = max(0, _sim_to_int(row.get("oro_paid", 0), 0) + _sim_to_int(it.get("oro_gain", 0), 0))
            by_match[aid] = row
        grants[match_id] = by_match
        S.sim_mid_battle_grants_v1 = grants

        # D5 guard ledger update.
        g["grants_count"] = grants_count + 1
        g["total_exp"] = current_exp + max(0, _sim_to_int(apply_report.get("total_exp", 0), 0))
        g["total_oro"] = current_oro + max(0, _sim_to_int(apply_report.get("total_oro", 0), 0))
        guards[match_id] = g
        S.sim_mid_battle_guard_v1 = guards

        log = getattr(S, "sim_mid_battle_event_log_v1", None)
        if not isinstance(log, list):
            log = []
        idem_statuses = res.get("audit", {}).get("idempotency", {}).get("statuses", {})
        if not isinstance(idem_statuses, dict):
            idem_statuses = {}
        actor_rows = []
        for rr in res.get("results", []):
            if not isinstance(rr, dict):
                continue
            actor_rows.append({
                "actor_id": str(rr.get("actor_id", "") or ""),
                "exp_gain": _sim_to_int(rr.get("final", {}).get("exp_gain", 0), 0),
                "oro_gain": _sim_to_int(rr.get("final", {}).get("oro_gain", 0), 0),
                "idempotency_status": str(idem_statuses.get(str(rr.get("actor_id", "") or ""), "unknown") or "unknown"),
            })

        log.append({
            "event_key": str(req.get("mid_battle_meta", {}).get("event_key", "") or ""),
            "reward_event_id": str(req.get("reward_event_id", "") or ""),
            "canonical_trigger_key": str(req.get("mid_battle_meta", {}).get("canonical_trigger_key", "") or ""),
            "persist_ok": bool(persist.get("ok", False)),
            "apply_ok": bool(apply_report.get("ok", False)),
            "apply_total_exp": _sim_to_int(apply_report.get("total_exp", 0), 0),
            "apply_total_oro": _sim_to_int(apply_report.get("total_oro", 0), 0),
            "session_id": str(mm.get("session_id", "") or ""),
            "host_actor_id": str(mm.get("host_actor_id", "") or ""),
            "actors": actor_rows,
        })
        if len(log) > 300:
            log = log[-300:]
        S.sim_mid_battle_event_log_v1 = log

        return {
            "ok": True,
            "errors": list(bridge.get("errors", [])),
            "warnings": list(bridge.get("warnings", [])),
            "request": req,
            "result": res,
            "persist": persist,
            "apply": apply_report,
        }

    def sim_reconcile_battle_end_with_mid_grants(sim_pack, runtime=None, policy="subtract_paid"):
        """
        D4 - Reconciliación battle_end vs pagos mid-battle previos.
        Política v1: subtract_paid.
        """
        import renpy.store as S

        pack = copy.deepcopy(sim_pack if isinstance(sim_pack, dict) else {})
        req = pack.get("request", {}) if isinstance(pack.get("request", {}), dict) else {}
        res = pack.get("result", {}) if isinstance(pack.get("result", {}), dict) else {}
        rt = runtime if isinstance(runtime, dict) else {}

        if str(req.get("source", "") or "") != "battle_end":
            return pack
        if str(policy or "subtract_paid") != "subtract_paid":
            return pack

        match_id = str(rt.get("battle_id", rt.get("match_id", req.get("simulation_id", "match_unknown"))) or "match_unknown")
        grants = getattr(S, "sim_mid_battle_grants_v1", None)
        if not isinstance(grants, dict):
            grants = {}
        by_match = grants.get(match_id, {}) if isinstance(grants.get(match_id, {}), dict) else {}
        if len(by_match) == 0:
            return pack

        rows = res.get("results", []) if isinstance(res.get("results", []), list) else []
        out_rows = []
        total_exp_sub = 0
        total_oro_sub = 0

        for rr in rows:
            r = copy.deepcopy(rr if isinstance(rr, dict) else {})
            aid = str(r.get("actor_id", "") or "")
            paid = by_match.get(aid, {}) if isinstance(by_match.get(aid, {}), dict) else {}
            exp_paid = max(0, _sim_to_int(paid.get("exp_paid", 0), 0))
            oro_paid = max(0, _sim_to_int(paid.get("oro_paid", 0), 0))

            ff = r.get("final", {}) if isinstance(r.get("final", {}), dict) else {}
            exp_old = max(0, _sim_to_int(ff.get("exp_gain", 0), 0))
            oro_old = max(0, _sim_to_int(ff.get("oro_gain", 0), 0))
            exp_new = max(0, exp_old - exp_paid)
            oro_new = max(0, oro_old - oro_paid)
            ff["exp_gain"] = exp_new
            ff["oro_gain"] = oro_new
            ff["exp_after"] = max(0, _sim_to_int(ff.get("exp_after", 0), 0) - (exp_old - exp_new))
            ff["oro_after"] = max(0, _sim_to_int(ff.get("oro_after", 0), 0) - (oro_old - oro_new))
            r["final"] = ff

            notes = r.get("notes", []) if isinstance(r.get("notes", []), list) else []
            if exp_paid > 0 or oro_paid > 0:
                notes.append("reconciled_mid_battle_paid")
            r["notes"] = notes

            total_exp_sub += max(0, exp_old - exp_new)
            total_oro_sub += max(0, oro_old - oro_new)
            out_rows.append(r)

        res["results"] = out_rows
        audit = res.get("audit", {}) if isinstance(res.get("audit", {}), dict) else {}
        audit["reconciliation"] = {
            "policy": "subtract_paid",
            "match_id": match_id,
            "total_exp_subtracted": total_exp_sub,
            "total_oro_subtracted": total_oro_sub,
            "actors_reconciled": len(by_match),
        }
        res["audit"] = audit
        pack["result"] = res

        # Consumir ledger de ese match para no arrastrarlo a cierres futuros.
        if match_id in grants:
            del grants[match_id]
        S.sim_mid_battle_grants_v1 = grants

        guards = getattr(S, "sim_mid_battle_guard_v1", None)
        if not isinstance(guards, dict):
            guards = {}
        if match_id in guards:
            del guards[match_id]
        S.sim_mid_battle_guard_v1 = guards
        return pack

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
                "hp_reward_multiplier": 1,
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
        cfg["hp_reward_multiplier"] = _sim_hp_reward_multiplier(cfg.get("hp_reward_multiplier", 1))
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

    def _sim_hp_reward_multiplier(value):
        try:
            m = int(value or 1)
        except:
            m = 1
        if m < 1:
            m = 1
        if m > 5:
            m = 5
        return int(m)

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
        hp_reward_mult = _sim_hp_reward_multiplier(cfg.get("hp_reward_multiplier", 1))

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
                float(multi_factor) *
                float(hp_reward_mult)
            )
            oro_raw = (
                float(base["oro"]) *
                float(risk["risk_oro"]) *
                float(result_mult["result_oro"]) *
                float(perf["performance_oro"]) *
                float(anti) *
                float(multi_factor) *
                float(hp_reward_mult)
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
                "hp_reward_multiplier": int(hp_reward_mult),
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
                "hp_reward_multiplier": _sim_hp_reward_multiplier(_sim_get_from_sources(sources, ("hp_reward_multiplier",), 1)),
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
        pack = {
            "request": req,
            "result": res,
        }
        pack = sim_reconcile_battle_end_with_mid_grants(pack, runtime=runtime, policy="subtract_paid")
        return {
            "request": pack.get("request", req),
            "result": pack.get("result", res),
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
        _sim_save_persistent_compat()

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
        player_exp_total = 0
        player_oro_total = 0

        # Wallet runtime para ALPHA/DELTA (persistencia de sesión).
        wallet = getattr(S, "sim_actor_runtime_wallet_v1", None)
        if not isinstance(wallet, dict):
            wallet = {}
        if len(wallet) == 0:
            pw = getattr(S.persistent, "sim_actor_wallet_v1", None)
            if isinstance(pw, dict):
                wallet = copy.deepcopy(pw)

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
                player_exp_total += int(exp_gain)
                player_oro_total += int(oro_gain)

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
        wallet_persist = sim_persist_actor_wallets()

        # Bridge post-combate -> cuenta/lobby (oro/exp visibles en UI Hub).
        account_bridge = {
            "attempted": False,
            "applied": False,
            "skipped_duplicate": False,
            "exp_gain": int(player_exp_total),
            "gold_gain": int(player_oro_total),
            "key": "",
            "error": "",
        }
        if player_exp_total > 0 or player_oro_total > 0:
            account_bridge["attempted"] = True
            bridge_registry = getattr(S, "sim_account_reward_bridge_registry_v1", None)
            if not isinstance(bridge_registry, dict):
                bridge_registry = {}
            source = str(req.get("source", "battle_end") or "battle_end")
            sim_id = str(res.get("simulation_id", req.get("battle_id", "sim_unknown")) or "sim_unknown")
            bridge_key = source + "::" + sim_id
            account_bridge["key"] = bridge_key

            if bool(bridge_registry.get(bridge_key, False)):
                account_bridge["skipped_duplicate"] = True
            else:
                fn_gain_account = getattr(S, "bs_saga_gain_account_rewards", None)
                if callable(fn_gain_account):
                    try:
                        rr_acc = fn_gain_account(player_exp_total, player_oro_total, source="battle_end_reward_bridge")
                        account_bridge["applied"] = bool(rr_acc.get("ok", False)) if isinstance(rr_acc, dict) else True
                        if account_bridge["applied"]:
                            bridge_registry[bridge_key] = True
                            S.sim_account_reward_bridge_registry_v1 = bridge_registry
                    except Exception as ex:
                        account_bridge["error"] = "account_bridge_exception: %s" % ex
                else:
                    account_bridge["error"] = "bs_saga_gain_account_rewards no disponible en store."

        report = {
            "ok": True,
            "applied_count": len(applied),
            "total_exp": total_exp,
            "total_oro": total_oro,
            "player_total_exp": int(player_exp_total),
            "player_total_oro": int(player_oro_total),
            "items": applied,
            "wallet_persist": wallet_persist,
            "account_bridge": account_bridge,
        }
        S.sim_battle_end_last_apply_v1 = report
        return report

    def sim_persist_actor_wallets(max_items=1000):
        """
        C3+ - Persistencia fuerte de wallets ALPHA/DELTA.
        Fuente: S.sim_actor_runtime_wallet_v1
        Destino: S.persistent.sim_actor_wallet_v1
        """
        import renpy
        import renpy.store as S

        runtime_wallet = getattr(S, "sim_actor_runtime_wallet_v1", None)
        if not isinstance(runtime_wallet, dict):
            runtime_wallet = {}

        persistent_wallet = getattr(S.persistent, "sim_actor_wallet_v1", None)
        if not isinstance(persistent_wallet, dict):
            persistent_wallet = {}

        merged = copy.deepcopy(persistent_wallet)
        updated = 0

        for actor_id, row in runtime_wallet.items():
            rr = row if isinstance(row, dict) else {}
            aid = str(actor_id or rr.get("actor_id", "") or "").strip()
            if aid == "":
                continue

            at = str(rr.get("actor_type", "") or "").upper()
            if at not in ("ALPHA", "DELTA"):
                continue

            prev = merged.get(aid, {}) if isinstance(merged.get(aid, {}), dict) else {}
            merged[aid] = {
                "actor_id": aid,
                "actor_type": at,
                "exp": max(0, _sim_to_int(rr.get("exp", prev.get("exp", 0)), 0)),
                "oro": max(0, _sim_to_int(rr.get("oro", prev.get("oro", 0)), 0)),
                "updated_ts_unix": int(time.time()),
            }
            updated += 1

        # Hard cap por cantidad de actores para evitar crecimiento no controlado.
        lim = max(100, _sim_to_int(max_items, 1000))
        if len(merged) > lim:
            # ordena por timestamp y conserva más recientes
            rows = []
            for k, v in merged.items():
                vv = v if isinstance(v, dict) else {}
                rows.append((k, _sim_to_int(vv.get("updated_ts_unix", 0), 0), vv))
            rows.sort(key=lambda x: x[1], reverse=True)
            cut = rows[:lim]
            merged = {k: vv for (k, _, vv) in cut}

        S.persistent.sim_actor_wallet_v1 = merged
        _sim_save_persistent_compat()

        return {
            "ok": True,
            "updated": updated,
            "total_persistent_wallet": len(merged),
        }

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

    def sim_phaseE_multiplayer_fixture_requests():
        """
        E4 - Fixtures canónicos host/guest para validar autorización y audit.
        """
        base_bc = {
            "mode": "2v2",
            "multiplayer_enabled": True,
            "session_id": "sess_e4_001",
            "host_actor_id": "host_p1",
            "allowed_guest_actor_ids": ["guest_a1"],
            "team_a_actors": [
                {"actor_id": "host_p1", "actor_type": "PLAYER", "level": 10, "register": 1},
                {"actor_id": "guest_a1", "actor_type": "ALPHA", "level": 10, "register": 1},
            ],
            "team_b_actors": [
                {"actor_id": "enemy_b1", "actor_type": "BETA", "level": 10, "register": 1},
                {"actor_id": "enemy_b2", "actor_type": "BETA", "level": 10, "register": 1},
            ],
        }
        return {
            "e4_host_allowed": {
                "event_ctx": {"event_key": "passive_proc", "actor_id": "host_p1", "actor_type": "PLAYER", "team": "A", "match_id": "e4_m1", "trigger_uid": "e4_t1"},
                "battle_ctx": copy.deepcopy(base_bc),
                "expect_blocked": False,
            },
            "e4_guest_allowed": {
                "event_ctx": {"event_key": "passive_proc", "actor_id": "guest_a1", "actor_type": "ALPHA", "team": "A", "match_id": "e4_m1", "trigger_uid": "e4_t2"},
                "battle_ctx": copy.deepcopy(base_bc),
                "expect_blocked": False,
            },
            "e4_guest_blocked": {
                "event_ctx": {"event_key": "passive_proc", "actor_id": "guest_forbidden", "actor_type": "ALPHA", "team": "A", "match_id": "e4_m1", "trigger_uid": "e4_t3"},
                "battle_ctx": copy.deepcopy(base_bc),
                "expect_blocked": True,
            },
        }

    def sim_run_phaseE_e4_tests():
        """
        E4 - Smoke de fixtures multiplayer + metadata de sesión en audit log.
        """
        import renpy.store as S

        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        fixtures = sim_phaseE_multiplayer_fixture_requests()
        snap_registry = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        snap_log = copy.deepcopy(getattr(S, "sim_mid_battle_event_log_v1", []))
        snap_apply = copy.deepcopy(getattr(S, "sim_battle_end_last_apply_v1", {}))

        try:
            for key in ("e4_host_allowed", "e4_guest_allowed", "e4_guest_blocked"):
                fx = fixtures.get(key, {}) if isinstance(fixtures.get(key, {}), dict) else {}
                ev = copy.deepcopy(fx.get("event_ctx", {}))
                bc = copy.deepcopy(fx.get("battle_ctx", {}))
                bc["idempotency_registry"] = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
                rr = sim_run_mid_battle_event(ev, bc)
                blocked = (not bool(rr.get("ok", True))) and ("authz_block" in " ".join(rr.get("warnings", [])))
                _push("%s_expected_block_state" % key, blocked == bool(fx.get("expect_blocked", False)))

            log = getattr(S, "sim_mid_battle_event_log_v1", [])
            session_ok = False
            if isinstance(log, list) and len(log) > 0:
                for row in log:
                    if not isinstance(row, dict):
                        continue
                    if str(row.get("session_id", "") or "") == "sess_e4_001":
                        session_ok = True
                        break
            _push("e4_audit_has_session_id", session_ok)
        finally:
            S.sim_idempotency_registry_v1 = snap_registry
            S.sim_mid_battle_event_log_v1 = snap_log
            S.sim_battle_end_last_apply_v1 = snap_apply

        return out

    def sim_export_phaseE_fixtures_json():
        """
        E4 - Export de fixtures multiplayer + resultados esperados.
        """
        fixtures = sim_phaseE_multiplayer_fixture_requests()
        return json.dumps({
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "phase": "E4",
            "fixtures": fixtures,
            "checks": sim_run_phaseE_e4_tests(),
        }, ensure_ascii=False, sort_keys=True, indent=2)

    def sim_run_phaseE_e5_tests():
        """
        E5 - Gate operacional de cierre (ready/no-ready) previo a testeo manual.
        """
        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        all_rows = []
        fn_d6 = globals().get("sim_run_phaseD_e2e_tests", None)
        if callable(fn_d6):
            rr = fn_d6()
            if isinstance(rr, list):
                all_rows.extend(rr)
        else:
            _push("e5_phaseD_e2e_unavailable", False, "sim_run_phaseD_e2e_tests no disponible")

        fn_e4 = globals().get("sim_run_phaseE_e4_tests", None)
        if callable(fn_e4):
            rr2 = fn_e4()
            if isinstance(rr2, list):
                all_rows.extend(rr2)
        else:
            _push("e5_phaseE_e4_unavailable", False, "sim_run_phaseE_e4_tests no disponible")

        by_name = {}
        for row in all_rows:
            if isinstance(row, dict):
                by_name[str(row.get("name", ""))] = bool(row.get("ok", False))

        required = [
            "phaseD_e2e_required_gate",
            "e4_host_allowed_expected_block_state",
            "e4_guest_allowed_expected_block_state",
            "e4_guest_blocked_expected_block_state",
            "e4_audit_has_session_id",
        ]
        missing = []
        for name in required:
            if not bool(by_name.get(name, False)):
                missing.append(name)

        _push(
            "phaseE_e5_readiness_gate",
            len(missing) == 0,
            ("missing_or_failed=%s" % ",".join(missing)) if len(missing) > 0 else "ready_for_manual_runtime_testing"
        )
        return out

    def sim_phaseE_e5_readiness_report():
        tests = sim_run_phaseE_e5_tests()
        failed = []
        for t in tests:
            if not bool((t or {}).get("ok", False)):
                failed.append(str((t or {}).get("name", "unknown")))
        return {
            "phase": "E5",
            "sim_contract_version": SIM_CONTRACT_VERSION,
            "ready": (len(failed) == 0),
            "failed_checks": failed,
            "checks": tests,
            "generated_ts_unix": int(time.time()),
        }

    def sim_export_phaseE_e5_readiness_json():
        return json.dumps(sim_phaseE_e5_readiness_report(), ensure_ascii=False, sort_keys=True, indent=2)

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

    def sim_run_d1_catalog_tests():
        """
        D1 - Smoke tests del catálogo mid-battle.
        """
        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        ok_keys = list(SIM_ALLOWED_MID_BATTLE_EVENTS)
        _push("d1_catalog_has_min_2_events", len(ok_keys) >= 2)

        ev_ok = {
            "event_key": "passive_proc",
            "actor_id": "player_1",
            "actor_type": "PLAYER",
            "match_id": "m1",
            "trigger_uid": "t01",
        }
        v1 = sim_validate_mid_battle_event(ev_ok)
        _push("d1_validate_passive_ok", bool(v1.get("ok", False)))
        _push("d1_reward_event_id_autogen", str(v1.get("normalized", {}).get("reward_event_id", "") or "") != "")

        ev_bad = {
            "event_key": "unknown_proc",
            "actor_id": "player_1",
            "actor_type": "PLAYER",
            "match_id": "m1",
            "trigger_uid": "t02",
        }
        v2 = sim_validate_mid_battle_event(ev_bad)
        _push("d1_reject_unknown_event_key", not bool(v2.get("ok", True)))

        return out

    def sim_run_d2_bridge_tests():
        """
        D2 - Smoke tests del bridge mid-battle -> request parcial.
        """
        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        ev = {
            "event_key": "technique_proc",
            "actor_id": "player_1",
            "actor_type": "PLAYER",
            "team": "A",
            "match_id": "md2_1",
            "trigger_uid": "tr_001",
        }
        bridge1 = sim_build_request_from_mid_battle_event(ev, battle_ctx={})
        req1 = bridge1.get("request", {}) if isinstance(bridge1.get("request", {}), dict) else {}
        _push("d2_bridge_fallback_ok", bool(bridge1.get("ok", False)))
        _push("d2_bridge_source_mid_battle", str(req1.get("source", "")) == "mid_battle_event")
        _push("d2_bridge_event_type_conditional_gain", str(req1.get("event_type", "")) == "conditional_gain")
        _push("d2_bridge_reward_event_id_present", str(req1.get("reward_event_id", "") or "") != "")

        battle_ctx = {
            "mode": "2v2",
            "team_a_actors": [
                {"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1},
                {"actor_id": "alpha_a1", "actor_type": "ALPHA", "level": 20, "register": 2},
            ],
            "team_b_actors": [
                {"actor_id": "delta_b1", "actor_type": "DELTA", "level": 20, "register": 2},
                {"actor_id": "beta_b1", "actor_type": "BETA", "level": 20, "register": 2},
            ],
        }
        bridge2 = sim_build_request_from_mid_battle_event(ev, battle_ctx=battle_ctx)
        req2 = bridge2.get("request", {}) if isinstance(bridge2.get("request", {}), dict) else {}
        _push("d2_bridge_with_battle_ctx_ok", bool(bridge2.get("ok", False)))
        _push("d2_bridge_mode_2v2", str(req2.get("mode", "")) == "2v2")
        _push("d2_bridge_actors_shape", len(req2.get("actors", [])) == 4)

        return out

    def sim_run_d3_mid_battle_tests():
        """
        D3 - Smoke tests del pipeline mid-battle runtime.
        """
        import renpy.store as S

        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        snap_registry = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        snap_log = copy.deepcopy(getattr(S, "sim_mid_battle_event_log_v1", []))
        snap_apply = copy.deepcopy(getattr(S, "sim_battle_end_last_apply_v1", {}))

        try:
            ev = {
                "event_key": "passive_proc",
                "actor_id": "player_1",
                "actor_type": "PLAYER",
                "team": "A",
                "match_id": "d3_smoke_m1",
                "trigger_uid": "proc001",
                "level": 10,
                "register": 1,
            }
            bc = {
                "mode": "1v1",
                "team_a_actors": [{"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1}],
                "team_b_actors": [{"actor_id": "beta_e1", "actor_type": "BETA", "level": 10, "register": 1}],
                "idempotency_registry": copy.deepcopy(snap_registry),
            }

            r1 = sim_run_mid_battle_event(ev, bc)
            _push("d3_first_trigger_ok", bool(r1.get("ok", False)))
            _push("d3_first_trigger_applies", _sim_to_int(r1.get("apply", {}).get("total_exp", 0), 0) >= 0)

            # Retry exacto con registry actualizado => no doble pago.
            reg2 = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
            bc2 = copy.deepcopy(bc)
            bc2["idempotency_registry"] = reg2
            r2 = sim_run_mid_battle_event(ev, bc2)
            no_double = (
                _sim_to_int(r2.get("apply", {}).get("total_exp", -1), -1) == 0 and
                _sim_to_int(r2.get("apply", {}).get("total_oro", -1), -1) == 0
            )
            _push("d3_retry_no_double_pay", no_double)

            # E3 - actor fuera de lista permitida en sesión multiplayer debe bloquearse.
            ev_block = copy.deepcopy(ev)
            ev_block["actor_id"] = "guest_forbidden"
            ev_block["trigger_uid"] = "proc_block_001"
            bc_auth = copy.deepcopy(bc)
            bc_auth["multiplayer_enabled"] = True
            bc_auth["host_actor_id"] = "player_1"
            bc_auth["allowed_guest_actor_ids"] = ["alpha_guest_1"]
            bc_auth["idempotency_registry"] = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
            r_block = sim_run_mid_battle_event(ev_block, bc_auth)
            blocked = (not bool(r_block.get("ok", True))) and ("authz_block" in " ".join(r_block.get("warnings", [])))
            _push("d3_blocks_unauthorized_guest_actor", blocked)

            log = getattr(S, "sim_mid_battle_event_log_v1", [])
            _push("d3_event_log_written", isinstance(log, list) and len(log) >= 1)
        finally:
            S.sim_idempotency_registry_v1 = snap_registry
            S.sim_mid_battle_event_log_v1 = snap_log
            S.sim_battle_end_last_apply_v1 = snap_apply

        return out

    def sim_run_d4_reconcile_tests():
        """
        D4 - Smoke tests de reconciliación mid-battle vs battle_end.
        """
        import renpy.store as S

        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        snap_registry = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        snap_grants = copy.deepcopy(getattr(S, "sim_mid_battle_grants_v1", {}))
        snap_apply = copy.deepcopy(getattr(S, "sim_battle_end_last_apply_v1", {}))

        try:
            # 1) Pagar un mid-battle.
            ev = {
                "event_key": "technique_proc",
                "actor_id": "player_1",
                "actor_type": "PLAYER",
                "team": "A",
                "match_id": "d4_match_1",
                "trigger_uid": "d4_t01",
                "level": 10,
                "register": 1,
            }
            bc = {
                "mode": "1v1",
                "team_a_actors": [{"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1}],
                "team_b_actors": [{"actor_id": "beta_e1", "actor_type": "BETA", "level": 10, "register": 1}],
                "idempotency_registry": copy.deepcopy(snap_registry),
            }
            r_mid = sim_run_mid_battle_event(ev, bc)
            paid_mid_exp = _sim_to_int(r_mid.get("apply", {}).get("total_exp", 0), 0)
            paid_mid_oro = _sim_to_int(r_mid.get("apply", {}).get("total_oro", 0), 0)
            _push("d4_mid_battle_paid", bool(r_mid.get("ok", False)))

            # 2) Cierre battle_end del mismo match: debe reconciliar restando lo pagado.
            runtime_end = {
                "source": "battle_end",
                "battle_id": "d4_match_1",
                "result": "victory",
                "player_level": 10,
                "player_register": 1,
                "player_exp": 0,
                "player_exp_max": 100,
                "player_oro": 0,
                "player_actor_type": "PLAYER",
                "enemy_level": 10,
                "enemy_register": 1,
                "enemy_actor_type": "BETA",
                "idempotency_registry": copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {})),
            }
            pack_end = sim_run_battle_end_simulation(runtime=runtime_end)
            res_end = pack_end.get("result", {}) if isinstance(pack_end.get("result", {}), dict) else {}
            rows = res_end.get("results", []) if isinstance(res_end.get("results", []), list) else []
            rec = res_end.get("audit", {}).get("reconciliation", {}) if isinstance(res_end.get("audit", {}), dict) else {}

            # Encontrar fila player.
            p_row = None
            for rr in rows:
                if str(rr.get("actor_id", "") or "") == "player_1":
                    p_row = rr
                    break
            p_gain = _sim_to_int((p_row or {}).get("final", {}).get("exp_gain", 0), 0)
            p_oro = _sim_to_int((p_row or {}).get("final", {}).get("oro_gain", 0), 0)

            _push("d4_reconciliation_audit_present", isinstance(rec, dict) and str(rec.get("policy", "")) == "subtract_paid")
            _push("d4_reconciliation_subtracted_non_negative", _sim_to_int(rec.get("total_exp_subtracted", -1), -1) >= 0 and _sim_to_int(rec.get("total_oro_subtracted", -1), -1) >= 0)
            _push("d4_battle_end_respects_paid", p_gain >= 0 and p_oro >= 0 and (_sim_to_int(rec.get("total_exp_subtracted", 0), 0) >= 0))

            # 3) Ledger consumido tras reconciliación.
            grants_after = getattr(S, "sim_mid_battle_grants_v1", {})
            consumed = (not isinstance(grants_after, dict)) or ("d4_match_1" not in grants_after)
            _push("d4_match_ledger_consumed", consumed)
        finally:
            S.sim_idempotency_registry_v1 = snap_registry
            S.sim_mid_battle_grants_v1 = snap_grants
            S.sim_battle_end_last_apply_v1 = snap_apply

        return out

    def sim_run_d5_guard_rail_tests():
        """
        D5 - Smoke tests de guard rails anti-spam mid-battle.
        """
        import renpy.store as S

        out = []

        def _push(name, ok, detail=""):
            out.append({"name": name, "ok": bool(ok), "detail": str(detail or "")})

        snap_registry = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
        snap_guards = copy.deepcopy(getattr(S, "sim_mid_battle_guard_v1", {}))
        snap_grants = copy.deepcopy(getattr(S, "sim_mid_battle_grants_v1", {}))

        try:
            ev = {
                "event_key": "passive_proc",
                "actor_id": "player_1",
                "actor_type": "PLAYER",
                "team": "A",
                "match_id": "d5_match_1",
                "trigger_uid": "d5_t01",
                "level": 10,
                "register": 1,
            }
            base_ctx = {
                "mode": "1v1",
                "team_a_actors": [{"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1}],
                "team_b_actors": [{"actor_id": "beta_e1", "actor_type": "BETA", "level": 10, "register": 1}],
                "idempotency_registry": copy.deepcopy(snap_registry),
                "max_mid_battle_grants_per_match": 1,
                "max_mid_battle_reward_ratio": 0.40,
                "projected_end_exp": 1000,
                "projected_end_oro": 600,
            }

            r1 = sim_run_mid_battle_event(ev, base_ctx)
            _push("d5_first_grant_allowed", bool(r1.get("ok", False)))

            ev2 = copy.deepcopy(ev)
            ev2["trigger_uid"] = "d5_t02"
            ctx2 = copy.deepcopy(base_ctx)
            ctx2["idempotency_registry"] = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
            r2 = sim_run_mid_battle_event(ev2, ctx2)
            blocked_count = (not bool(r2.get("ok", True))) and ("max_mid_battle_grants_per_match" in " ".join(r2.get("warnings", [])))
            _push("d5_blocks_max_grants_per_match", blocked_count)

            # Ratio cap: muy bajo para forzar bloqueo.
            ev3 = copy.deepcopy(ev)
            ev3["match_id"] = "d5_match_2"
            ev3["trigger_uid"] = "d5_t03"
            ctx3 = copy.deepcopy(base_ctx)
            ctx3["idempotency_registry"] = copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {}))
            ctx3["max_mid_battle_grants_per_match"] = 99
            ctx3["max_mid_battle_reward_ratio"] = 0.05
            ctx3["projected_end_exp"] = 10
            ctx3["projected_end_oro"] = 10
            r3 = sim_run_mid_battle_event(ev3, ctx3)
            blocked_ratio = (not bool(r3.get("ok", True))) and ("max_mid_battle_reward_ratio" in " ".join(r3.get("warnings", [])))
            _push("d5_blocks_reward_ratio", blocked_ratio)
        finally:
            S.sim_idempotency_registry_v1 = snap_registry
            S.sim_mid_battle_guard_v1 = snap_guards
            S.sim_mid_battle_grants_v1 = snap_grants

        return out

    def sim_run_phaseD_e2e_tests():
        """
        D6 - Suite E2E consolidada para cierre de Fase D.
        """
        suites = []

        for fn_name in (
            "sim_run_d1_catalog_tests",
            "sim_run_d2_bridge_tests",
            "sim_run_d3_mid_battle_tests",
            "sim_run_d4_reconcile_tests",
            "sim_run_d5_guard_rail_tests",
        ):
            fn = globals().get(fn_name, None)
            if callable(fn):
                try:
                    rr = fn()
                    if isinstance(rr, list):
                        suites.extend(rr)
                    else:
                        suites.append({"name": fn_name, "ok": False, "detail": "suite retornó formato inválido"})
                except Exception as ex:
                    suites.append({"name": fn_name, "ok": False, "detail": "suite lanzó excepción: %s" % ex})
            else:
                suites.append({"name": fn_name, "ok": False, "detail": "suite no disponible"})

        required = set([
            "d1_catalog_has_min_2_events",
            "d2_bridge_with_battle_ctx_ok",
            "d3_retry_no_double_pay",
            "d4_reconciliation_audit_present",
            "d4_match_ledger_consumed",
            "d5_blocks_max_grants_per_match",
            "d5_blocks_reward_ratio",
        ])
        by_name = {}
        for row in suites:
            if isinstance(row, dict):
                by_name[str(row.get("name", ""))] = bool(row.get("ok", False))

        required_ok = True
        missing = []
        for k in required:
            if not bool(by_name.get(k, False)):
                required_ok = False
                missing.append(k)

        suites.append({
            "name": "phaseD_e2e_required_gate",
            "ok": required_ok,
            "detail": ("missing_or_failed=%s" % ",".join(missing)) if len(missing) > 0 else "all_required_checks_ok",
        })

        return suites

    def sim_run_phaseC_e2e_tests():
        """
        C6 - QA E2E mínimo para integración C2/C5/C3/C4.
        Retorna lista [{name, ok, detail}].
        """
        import renpy
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
        snap_pwallet = copy.deepcopy(getattr(S.persistent, "sim_actor_wallet_v1", {}))

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

            # 2b) C3 ampliado sobre flujo real C2/C5/C3: caso multi 2v2.
            rt_2v2 = {
                "source": "battle_end",
                "battle_id": "c6_multi_2v2",
                "result": "victory",
                "team_a_actors": [
                    {"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1, "exp_current": snap_player_exp, "exp_max": 100, "oro_current": snap_player_oro, "stars": {"ofensiva": 4, "defensiva": 4, "control": 4, "eficiencia": 4, "tecnica": 4, "impacto": 4}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "alpha_a1", "actor_type": "ALPHA", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 3, "defensiva": 3, "control": 3, "eficiencia": 3, "tecnica": 3, "impacto": 3}, "flags": {"eligible_rewards": True}},
                ],
                "team_b_actors": [
                    {"actor_id": "delta_b1", "actor_type": "DELTA", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 2, "defensiva": 2, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "beta_b2", "actor_type": "BETA", "level": 20, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 1, "defensiva": 1, "control": 1, "eficiencia": 1, "tecnica": 1, "impacto": 1}, "flags": {"eligible_rewards": True}},
                ],
                "idempotency_registry": copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {})),
            }
            pack_ad = sim_run_battle_end_simulation(runtime=rt_2v2)
            sim_persist_simulation_artifacts(pack_ad)
            sim_apply_simulation_rewards_to_runtime(pack_ad)
            wallet_after = getattr(S, "sim_actor_runtime_wallet_v1", {})
            pw_after = getattr(S.persistent, "sim_actor_wallet_v1", {})
            ok_ad = (
                isinstance(wallet_after, dict) and
                "alpha_a1" in wallet_after and
                "delta_b1" in wallet_after and
                "beta_b2" not in wallet_after and
                isinstance(pw_after, dict) and
                "alpha_a1" in pw_after and
                "delta_b1" in pw_after
            )
            _push("c6_multi_2v2_wallet_apply", ok_ad)

            # 2c) Caso multi 2v1 en flujo real.
            rt_2v1 = {
                "source": "battle_end",
                "battle_id": "c6_multi_2v1",
                "result": "defeat",
                "team_a_actors": [
                    {"actor_id": "player_1", "actor_type": "PLAYER", "level": 10, "register": 1, "exp_current": snap_player_exp, "exp_max": 100, "oro_current": snap_player_oro, "stars": {"ofensiva": 3, "defensiva": 3, "control": 3, "eficiencia": 3, "tecnica": 3, "impacto": 3}, "flags": {"eligible_rewards": True}},
                    {"actor_id": "alpha_a2", "actor_type": "ALPHA", "level": 12, "register": 1, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 2, "defensiva": 2, "control": 2, "eficiencia": 2, "tecnica": 2, "impacto": 2}, "flags": {"eligible_rewards": True}},
                ],
                "team_b_actors": [
                    {"actor_id": "delta_b2", "actor_type": "DELTA", "level": 25, "register": 2, "exp_current": 0, "exp_max": 100, "oro_current": 0, "stars": {"ofensiva": 4, "defensiva": 4, "control": 4, "eficiencia": 4, "tecnica": 4, "impacto": 4}, "flags": {"eligible_rewards": True}},
                ],
                "idempotency_registry": copy.deepcopy(getattr(S, "sim_idempotency_registry_v1", {})),
            }
            pack_2v1 = sim_run_battle_end_simulation(runtime=rt_2v1)
            sim_persist_simulation_artifacts(pack_2v1)
            ap_2v1 = sim_apply_simulation_rewards_to_runtime(pack_2v1)
            ok_2v1 = bool(ap_2v1.get("ok", False)) and _sim_to_int(ap_2v1.get("applied_count", 0), 0) >= 1
            _push("c6_multi_2v1_flow", ok_2v1)

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
            S.persistent.sim_actor_wallet_v1 = snap_pwallet

            # Persist restore snapshot para trazabilidad QA.
            cur = getattr(S.persistent, "sim_c6_restore_log_v1", None)
            if not isinstance(cur, list):
                cur = []
            cur.append({
                "ts_unix": int(time.time()),
                "restored": True,
                "player_exp_before": snap_player_exp,
                "player_oro_before": snap_player_oro,
                "registry_size_before": len(snap_registry) if isinstance(snap_registry, dict) else 0,
                "wallet_size_before": len(snap_wallet) if isinstance(snap_wallet, dict) else 0,
                "persistent_wallet_size_before": len(snap_pwallet) if isinstance(snap_pwallet, dict) else 0,
            })
            if len(cur) > 200:
                cur = cur[-200:]
            S.persistent.sim_c6_restore_log_v1 = cur
            _sim_save_persistent_compat()

        return out
