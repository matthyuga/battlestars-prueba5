# ============================================================
# 04F_SELECTOR_FUNCTIONSV2.rpy – Selector Moderno (v7.2 FIX SAFE)
# Rebuild Simulation Safe Edition – basado en 04X
# ------------------------------------------------------------
# ✔ Usa reiatsu_energy_dynamic_cost() → valor final real
# ✔ Selector trabaja con recursos simulados coherentes
# ✔ pending_tech_list + HUD sync
# ✔ FIX CRÍTICO: simulación SIEMPRE se reconstruye (sin drift)
# ✔ Focus/Potenciar: duplican SOLO el Reiatsu de la técnica objetivo
# ✔ Define get_real_cost() (evita NameError del menú)
# ✔ can_pay_simulated arranca desde actions_available_start (no drift)
# ✔ FIX: NO import renpy en init (evita crasheos del engine)
# ============================================================

init -959 python:

    import renpy.store as S

    # ------------------------------------------------------------
    # Helpers renpy (safe)
    # ------------------------------------------------------------
    def _rn_notify(msg):
        try:
            renpy.notify(msg)
        except:
            pass

    def _rn_restart():
        try:
            renpy.restart_interaction()
        except:
            pass

    def _rn_hide(scr):
        try:
            renpy.hide_screen(scr)
        except:
            pass

    # ============================================================
    # MAPA NOMBRE → TECH_ID
    # ============================================================
    TECH_NAME_TO_ID = {
        # OFENSIVAS
        "Ataque Extra":      "extra_attack",
        "Técnica Extra":     "extra_tech",
        "Ataque Reductor":   "attack_reducer",
        "Ataque Directo":    "direct_attack",
        "Ataque Negador":    "noatk_attack",
        "Ataque básico": "stronger_attack",
        "Ataque más fuerte": "stronger_attack",  # alias legacy
        "Ladrón ofensivo":   "ladron_ofensivo",
        "Ladrón defensivo":  "ladron_defensivo",
        "Ladrón de concentrar": "ladron_concentrar",

        # DEFENSIVAS
        "Defensa Extra":       "defense_extra",
        "Defensa Reductora":   "defense_reducer",
        "Defensa Reflectora":  "defense_reflect",
        "Defensa Básica":      "defense_strong_block",
        "Defensa Fuerte":      "defense_strong_block",  # alias legacy
        "Salvaguarda principiante": "salvaguarda_principiante",

        # FOCUS (sin tech_id real)
        "Concentrar x2":     None,
        "Potenciar":         None,
        "Descansar":         None,
        "Dados de furia":    "fury_dice",
    }

    def get_tech_id(name):
        return TECH_NAME_TO_ID.get(name, None)

    # ============================================================
    # Fury selection state (estable + compat legacy)
    # ============================================================
    def _fury_sel_get():
        fs = getattr(S, "fury_selection", None)
        if not isinstance(fs, dict):
            fs = {"queue_index": -1, "tech_name": "", "tech_id": "", "armed": False}
            S.fury_selection = dict(fs)
        return dict(fs)

    def _fury_sel_set(idx=-1, tech_name="", tech_id="", armed=False):
        try:
            _idx = int(idx)
        except:
            _idx = -1
        S.fury_selection = {
            "queue_index": int(_idx),
            "tech_name": str(tech_name or ""),
            "tech_id": str(tech_id or ""),
            "armed": bool(armed),
        }
        S.fury_selected_queue_index = int(_idx if bool(armed) else -1)

    def _fury_sel_clear():
        _fury_sel_set(-1, "", "", False)

    def selector_reconcile_fury_selection():
        """
        Auto-saneamiento del estado Fury contra la cola actual.
        Si la referencia quedó stale, limpia selección.
        """
        fs = _fury_sel_get()
        if not bool(fs.get("armed", False)):
            return False

        q = list(getattr(S, "player_action_queue", []) or [])
        idx = int(fs.get("queue_index", -1) or -1)
        if idx < 0 or idx >= len(q):
            _fury_sel_clear()
            return False

        q_name = str(q[idx] or "")
        fs_name = str(fs.get("tech_name", "") or "")
        if fs_name and q_name != fs_name:
            _fury_sel_clear()
            return False
        return True

    # ============================================================
    # COSTO DE ACCIÓN (acciones y bonus)
    # ============================================================
    TECH_ACTION_RULES = {
        "Ataque Directo":    {"cost": 1, "bonus": 0},
        "Ataque Negador":    {"cost": 1, "bonus": 0},
        "Ataque Reductor":   {"cost": 1, "bonus": 0},
        "Ataque básico": {"cost": 1, "bonus": 0},
        "Ataque más fuerte": {"cost": 1, "bonus": 0},  # alias legacy
        "Ladrón ofensivo":   {"cost": 1, "bonus": 0},
        "Ladrón defensivo":  {"cost": 1, "bonus": 0},
        "Ladrón de concentrar": {"cost": 1, "bonus": 0},

        "Ataque Extra":      {"cost": 1, "bonus": 1},
        "Técnica Extra":     {"cost": 1, "bonus": 1},

        "Concentrar x2":     {"cost": 0, "bonus": 0},
        "Potenciar":         {"cost": 0, "bonus": 0},
        "Dados de furia":    {"cost": 0, "bonus": 0},
        "Descansar":         {"cost": 1, "bonus": 0},

        "Defensa Extra":       {"cost": 1, "bonus": 1},
        "Defensa Reductora":   {"cost": 1, "bonus": 0},
        "Defensa Reflectora":  {"cost": 1, "bonus": 0},
        "Defensa Básica":      {"cost": 1, "bonus": 0},
        "Defensa Fuerte":      {"cost": 1, "bonus": 0},  # alias legacy
        "Salvaguarda principiante": {"cost": 1, "bonus": 0},
    }

    def get_action_cost(name):
        return TECH_ACTION_RULES.get(name, {"cost": 1, "bonus": 0})

    def _selector_player_unit_key():
        """
        Resuelve unit_key del jugador para preview/simulación.
        - 2v2: usa slot del turno si está disponible.
        - fallback: unidad activa player o player:0.
        """
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"

        # 2v2: preferir contexto de turno
        if mode == "2v2":
            try:
                fn_ctx = getattr(S, "bs_get_turn_ctx", None)
                fn_key = getattr(S, "bs_unit_key", None)
                if callable(fn_ctx) and callable(fn_key):
                    ctx = fn_ctx() or {}
                    team = str(ctx.get("owner_team", "player") or "player").strip().lower()
                    slot = int(ctx.get("owner_slot", 0) or 0)
                    if team == "player":
                        return str(fn_key("player", slot) or "player:0")
            except:
                pass

        try:
            fn_akt = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_akt):
                return str(fn_akt("player") or "player:0")
        except:
            pass

        return "player:0"

    # ============================================================
    # COSTO REAL dinámico (04X) – RAW
    # ============================================================
    def get_real_cost_raw(tech_name):
        """
        Costo base real (sin regla Focus/Potenciar del selector).
        """
        tech_id = get_tech_id(tech_name)
        if tech_id is None:
            return 0, 0, 0

        data = S.reiatsu_energy_dynamic_cost(tech_id, S, unit_key=_selector_player_unit_key())
        return (
            int(data.get("reiatsu_cost", 0) or 0),
            int(data.get("energy_cost", 0) or 0),
            int(data.get("value_final", 0) or 0),
        )

    # ============================================================
    # Focus/Potenciar: ¿esta técnica es la "objetivo" del focus?
    # ============================================================
    def _is_focus_target(queue, idx, tech_name, mode):

        if tech_name in ("Concentrar x2", "Potenciar"):
            return False

        tech_id = get_tech_id(tech_name)
        if tech_id is None:
            return False

        tech = getattr(S, "battle_techniques", {}).get(tech_id, {})
        t = tech.get("type", None)

        if mode == "offensive" and t != "offensive":
            return False
        if mode == "defensive" and t != "defensive":
            return False

        focus_key = "Concentrar x2" if mode == "offensive" else "Potenciar"

        last_focus_pos = -1
        for i in range(0, idx):
            if queue[i] == focus_key:
                last_focus_pos = i

        if last_focus_pos < 0:
            return False

        for j in range(last_focus_pos + 1, idx):
            name_j = queue[j]
            tech_id_j = get_tech_id(name_j)
            if tech_id_j is None:
                continue
            tech_j = getattr(S, "battle_techniques", {}).get(tech_id_j, {})
            tj = tech_j.get("type", None)
            if mode == "offensive" and tj == "offensive":
                return False
            if mode == "defensive" and tj == "defensive":
                return False

        return True

    # ============================================================
    # ✅ API que usa el MENÚ (evita NameError)
    # Devuelve: (rei, ene, final_val)
    # Regla: aplica x2 SOLO al Reiatsu de la técnica objetivo
    # según la COLA ACTUAL.
    # ============================================================
    def get_real_cost(tech_name, mode=None):

        if mode is None:
            mode = getattr(S, "battle_mode", "offensive")

        if tech_name in ("Concentrar x2", "Potenciar", "Dados de furia", "Descansar"):
            return 0, 0, 0

        rei, ene, val = get_real_cost_raw(tech_name)

        try:
            q = list(getattr(S, "player_action_queue", []))
        except:
            q = []

        # Si la técnica está en cola, evaluamos si es target del focus
        try:
            if tech_name in q:
                idx = q.index(tech_name)
                if _is_focus_target(q, idx, tech_name, mode):
                    rei *= 2
        except:
            pass

        return rei, ene, val

    # Export opcional por compat (si algún screen llama S.get_real_cost)
    S.get_real_cost = get_real_cost

    # ============================================================
    # 🔁 Rebuild total de simulación (ANTI-DRIFT)
    # ============================================================
    def rebuild_selector_simulation():

        q = list(getattr(S, "player_action_queue", []))

        S.simulated_reiatsu = int(getattr(S, "player_reiatsu", 0) or 0)
        S.simulated_energy  = int(getattr(S, "player_energy", 0) or 0)

        S.actions_available = int(getattr(S, "actions_available_start", 1) or 1)

        mode = getattr(S, "battle_mode", "offensive")

        for idx, name in enumerate(q):

            rules = get_action_cost(name)

            if S.actions_available < rules["cost"]:
                continue

            rei, ene, val = get_real_cost_raw(name)

            if _is_focus_target(q, idx, name, mode):
                rei *= 2

            S.simulated_reiatsu -= rei
            S.simulated_energy  -= ene

            S.actions_available -= rules["cost"]
            S.actions_available += rules["bonus"]

        if S.simulated_reiatsu < 0:
            S.simulated_reiatsu = 0
        if S.simulated_energy < 0:
            S.simulated_energy = 0
        if S.actions_available < 0:
            S.actions_available = 0

        try:
            S.pending_tech_list = list(getattr(S, "player_action_queue", []))
        except:
            S.pending_tech_list = []

        try:
            S.hud_update_simulation_costs(S, getattr(S, "pending_tech_list", []))
        except:
            pass

    # ============================================================
    # ¿PUEDE PAGAR? (simulación exacta, mirando el estado actual)
    # ============================================================
    def can_pay_simulated(name):

        q = list(getattr(S, "player_action_queue", []))
        mode = getattr(S, "battle_mode", "offensive")

        if name in q:
            return False, 0, 0

        q2 = q + [name]

        sim_rei = int(getattr(S, "player_reiatsu", 0) or 0)
        sim_ene = int(getattr(S, "player_energy", 0) or 0)

        # ✅ arranca desde acciones base del turno
        sim_act = int(getattr(S, "actions_available_start", 1) or 1)

        for idx, nm in enumerate(q2):

            rules = get_action_cost(nm)

            if sim_act < rules["cost"]:
                return False, 0, 0

            rei, ene, val = get_real_cost_raw(nm)

            if _is_focus_target(q2, idx, nm, mode):
                rei *= 2

            sim_rei -= rei
            sim_ene -= ene
            sim_act = sim_act - rules["cost"] + rules["bonus"]

            if sim_rei < 0 or sim_ene < 0:
                falta_r = max(0, -sim_rei)
                falta_e = max(0, -sim_ene)
                return False, falta_r, falta_e

        return True, 0, 0

    # ============================================================
    # ➕ AÑADIR TÉCNICA A LA COLA
    # ============================================================
    def add_technique_to_queue(tech_name):

        q = getattr(S, "player_action_queue", [])
        if tech_name in q:
            _rn_notify("⚠ Ya seleccionaste '%s'." % tech_name)
            return

        # Técnica Extra comodín: una sola vez por turno (of/def).
        try:
            tech_id = get_tech_id(tech_name)
        except:
            tech_id = None
        if tech_id == "extra_tech":
            fn_can_extra = getattr(S, "can_use_extra_tech", None)
            if callable(fn_can_extra) and (not bool(fn_can_extra("player"))):
                _rn_notify("⚠ Técnica Extra ya fue usada este turno.")
                return

        ok, fr, fe = can_pay_simulated(tech_name)
        if not ok:
            msg = "⚠ No puedes seleccionar '%s':" % tech_name
            if fr > 0:
                msg += " Falta %s Reiatsu." % fr
            if fe > 0:
                msg += " Falta %s Energía." % fe
            _rn_notify(msg)
            return

        q.append(tech_name)
        rebuild_selector_simulation()

        _rn_notify("➕ '%s' añadido." % tech_name)
        _rn_restart()

    # ============================================================
    # ❌ QUITAR TÉCNICA DE LA COLA
    # ============================================================
    def remove_technique_from_queue(index):

        q = getattr(S, "player_action_queue", [])
        try:
            tech = q.pop(int(index))
        except:
            return

        try:
            idx = int(index)
            fs = _fury_sel_get()
            cur = int(fs.get("queue_index", -1) or -1)
            if cur == idx:
                _fury_sel_clear()
            elif cur > idx:
                _fury_sel_set(cur - 1, fs.get("tech_name", ""), fs.get("tech_id", ""), bool(fs.get("armed", False)))
        except:
            pass

        rebuild_selector_simulation()

        _rn_notify("❌ '%s' eliminado." % tech)
        _rn_restart()

    # ============================================================
    # 🗑 CANCELAR TODO
    # ============================================================
    def clear_action_queue():

        q = getattr(S, "player_action_queue", [])
        q[:] = []
        _fury_sel_clear()

        S.actions_available = int(getattr(S, "actions_available_start", 1) or 1)
        S.simulated_reiatsu = int(getattr(S, "player_reiatsu", 0) or 0)
        S.simulated_energy  = int(getattr(S, "player_energy", 0) or 0)

        try:
            S.pending_tech_list = []
            S.hud_update_simulation_costs(S, [])
        except:
            pass

        _rn_notify("🗑 Cola vaciada.")
        _rn_restart()

    # ============================================================
    # 🔥 Selección de técnica para Dados de Furia
    # ============================================================
    def toggle_fury_target_queue_index(index):
        q = list(getattr(S, "player_action_queue", []))
        try:
            idx = int(index)
        except:
            return
        if idx < 0 or idx >= len(q):
            return

        selector_reconcile_fury_selection()
        fs = _fury_sel_get()
        cur = int(fs.get("queue_index", -1) or -1)
        # FIX A: priorizar desasignación (aunque la cola haya cambiado de tipo)
        if cur == idx:
            _fury_sel_clear()
            _rn_notify("🔥 Furia desasignada.")
            _rn_restart()
            return

        tech_name = str(q[idx] or "")
        tech_id = get_tech_id(tech_name)
        tech = getattr(S, "battle_techniques", {}).get(tech_id, {}) if tech_id else {}
        if str(tech.get("type", "") or "") != "offensive":
            _rn_notify("⚠ Solo puedes asignar furia a técnicas ofensivas.")
            return

        try:
            _fn_can = getattr(S, "can_use_fury_dice", None)
            _can_now = bool(_fn_can("player")) if callable(_fn_can) else False
        except:
            _can_now = False
        if not _can_now:
            _rn_notify("⚠ Dados de furia solo disponible con HP ≤ 25% (o ítem).")
            return

        try:
            _fn_pay = getattr(S, "can_pay_fury_activation", None)
            _pay_ok = bool(_fn_pay("player")) if callable(_fn_pay) else True
        except:
            _pay_ok = True
        if not _pay_ok:
            try:
                _fn_cost = getattr(S, "fury_activation_costs", None)
                _ci = _fn_cost("player") if callable(_fn_cost) else {}
            except:
                _ci = {}
            _rn_notify("⚠ Furia requiere 10% total: Reiatsu %s / Energía %s." % (
                str(int((_ci or {}).get("reiatsu_need", 0) or 0)),
                str(int((_ci or {}).get("energy_need", 0) or 0))
            ))
            return

        _fury_sel_set(idx, tech_name, tech_id, True)
        _rn_notify("🔥 Furia asignada a '%s'." % tech_name)
        _rn_restart()

    # ============================================================
    # ✅ CONFIRMAR TURNO (no descuenta recursos reales)
    # ============================================================
    def confirm_turn_actions():

        if not getattr(S, "player_action_queue", []):
            _rn_notify("⚠ Debes elegir al menos una técnica.")
            return

        S.turn_confirmed = True
        try:
            selector_reconcile_fury_selection()
            fs = _fury_sel_get()
            _idx = int(fs.get("queue_index", -1) or -1)
            _armed = bool(fs.get("armed", False))
            q = list(getattr(S, "player_action_queue", []) or [])
            _q_name = str(q[_idx] or "") if (_idx >= 0 and _idx < len(q)) else ""
            _fs_name = str(fs.get("tech_name", "") or "")
            if _armed and _idx >= 0 and _idx < len(q) and (not _fs_name or _q_name == _fs_name):
                S.fury_selected_turn_index = int(_idx)
            else:
                _fury_sel_clear()
                S.fury_selected_turn_index = -1
        except:
            S.fury_selected_turn_index = -1

        try:
            S.pending_tech_list = []
            S.hud_update_simulation_costs(S, [])
        except:
            pass

        _rn_hide("battle_command_menu")
        _rn_hide("technique_selector")

        _rn_notify("✅ Turno confirmado.")
        _rn_restart()

    # Export helper para screens (reconciliación visual/estado)
    try:
        S.selector_reconcile_fury_selection = selector_reconcile_fury_selection
    except:
        pass
