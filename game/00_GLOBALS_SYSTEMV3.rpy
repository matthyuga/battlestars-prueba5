# ===========================================================
# 00_GLOBALS_SYSTEM.RPY – Núcleo Global del Sistema de Combate
# ===========================================================
# v3.5 IdentityStoreFix + FocusFix + Reiatsu/Energy + Reflect Compatibility
# Ren’Py 7.4.9 Compatible
# -----------------------------------------------------------
# ✅ FIX CRÍTICO: current_actor_id / current_enemy_id ahora viven en store
#    y se actualizan correctamente al llamar set_battle_identity().
# -----------------------------------------------------------
# NOTA: Mantengo TODO lo demás igual para no romper módulos.
# ===========================================================


# ===========================================================
# 🔷 INIT PRINCIPAL (carga antes que todos los demás)
# ===========================================================
init -990 python:
    import renpy.store as store

    # =======================================================
    # 🔢 Formateador universal (miles con puntos)
    # =======================================================
    def battle_fmt_num(n):
        try:
            return "{:,}".format(int(n)).replace(",", ".")
        except:
            return str(n)

    store.battle_fmt_num = battle_fmt_num

    # =======================================================
    # ⚠ Debug seguro
    # =======================================================
    def debug_log(msg):
        try:
            if config.developer:
                renpy.log("[DEBUG] " + str(msg))
        except:
            pass

    store.debug_log = debug_log

    # =======================================================
    # ⚠ Validaciones básicas
    # =======================================================
    def battle_is_ko(entity):
        """
        Devuelve True si el HP es <= 0.
        Soporta:
        - dict con clave "HP"
        - objetos con atributo HP
        - valores numéricos directos (hp)
        """
        try:
            # Caso dict (tu flujo actual principal)
            if isinstance(entity, dict):
                return int(entity.get("HP", 0)) <= 0

            # Caso objeto con atributo HP (future-proof)
            hp_attr = getattr(entity, "HP", None)
            if hp_attr is not None:
                return int(hp_attr) <= 0

            # Caso número / string numérica
            return int(entity) <= 0
        except:
            return False

    def battle_clamp_hp(hp, min_value=0, max_value=None):
        """
        Limita el HP entre min_value y el máximo runtime actual.
        - Si max_value viene informado, lo respeta.
        - Si max_value es None, usa el mayor entre battle_hp_player_max y battle_hp_enemy_max.
        - Fallback seguro a 1 para evitar valores inválidos.
        """
        try:
            hp = int(hp)

            if max_value is None:
                try:
                    max_value = max(
                        int(getattr(store, "battle_hp_player_max", 1)),
                        int(getattr(store, "battle_hp_enemy_max", 1))
                    )
                except:
                    max_value = 1

            return max(min(hp, int(max_value)), int(min_value))
        except:
            return int(min_value)

    store.battle_is_ko = battle_is_ko
    store.battle_clamp_hp = battle_clamp_hp

    # =======================================================
    # 📘 REGISTRO DE OPERACIÓN (defensas)
    # =======================================================
    OP_COLOR_TITLE   = "#FFD700"
    OP_COLOR_TEXT    = "#AAAAAA"
    OP_COLOR_DMG     = "#FF4444"
    OP_COLOR_DEF     = "#00BFFF"
    OP_COLOR_FOCUS   = "#C586C0"
    OP_COLOR_RESULT  = "#90EE90"

    debug_operation_log = []

    def operation_clear():
        global debug_operation_log
        debug_operation_log = []

    def operation_add(text, color=None):
        global debug_operation_log
        safe = str(text).replace("[", "[[").replace("]", "]]")
        debug_operation_log.append((safe, color or OP_COLOR_TEXT))

    def operation_dump_to_battle_log(title="▸ Operación Defensiva:"):
        if not debug_operation_log:
            return
        try:
            battle_log_add(title, "#FFFFFF", group="operation")
            for txt, col in debug_operation_log:
                battle_log_add("   " + txt, col or OP_COLOR_TEXT, group="operation")
        except Exception as e:
            debug_log("operation_dump_to_battle_log error: {}".format(e))

    store.operation_clear = operation_clear
    store.operation_add = operation_add
    store.operation_dump_to_battle_log = operation_dump_to_battle_log

    # =======================================================
    # 🎨 Colorador básico
    # =======================================================
    def color_log(text, color="#FFFFFF"):
        return "{color=%s}%s{/color}" % (color, text)

    store.color_log = color_log

    # =======================================================
    # 🧭 Identidad de batalla
    # =======================================================
    BATTLE_IDENTITIES = {
        "Harribel": "ID_HARRIBEL_001",
        "Grimmjow": "ID_GRIMMJOW_002",
        "Nel":      "ID_NELIEL_003",
    }
    store.BATTLE_IDENTITIES = BATTLE_IDENTITIES

    # ✅ FIX: IDs viven en store (evita “congelado en None”)
    if not hasattr(store, "current_actor_id"):
        store.current_actor_id = None
    if not hasattr(store, "current_enemy_id"):
        store.current_enemy_id = None

    def set_battle_identity(actor, enemy):
        # Escribe DIRECTO en store (lo que leen todos los módulos)
        store.current_actor_id = BATTLE_IDENTITIES.get(actor, "ID_ACTOR_UNKNOWN")
        store.current_enemy_id = BATTLE_IDENTITIES.get(enemy, "ID_ENEMY_UNKNOWN")

    store.set_battle_identity = set_battle_identity

    # (Opcional) helper seguro para leerlos
    def get_battle_identity(which="actor"):
        if which == "enemy":
            return getattr(store, "current_enemy_id", None)
        return getattr(store, "current_actor_id", None)

    store.get_battle_identity = get_battle_identity

    # =======================================================
    # 🔷 REFLECT SYSTEM (legacy buffer, se mantiene por compat)
    # =======================================================
    class ReflectedDamage:
        def __init__(self, value=0, source_id=None):
            try:
                self.value = int(value)
            except:
                self.value = 0
            self.source_id = source_id

        def is_owned_by(self, actor_id):
            return self.source_id == actor_id

        def clear(self):
            self.value = 0
            self.source_id = None

        def __repr__(self):
            return "<ReflectedDamage value={} source={}>".format(
                self.value, self.source_id)

    reflected_buffer = ReflectedDamage()

    def clear_reflect(obj):
        if isinstance(obj, ReflectedDamage):
            obj.clear()
        return 0

    def is_reflect_owner(obj, actor_id):
        return isinstance(obj, ReflectedDamage) and obj.source_id == actor_id

    store.ReflectedDamage   = ReflectedDamage
    store.reflected_buffer  = reflected_buffer
    store.clear_reflect     = clear_reflect
    store.is_reflect_owner  = is_reflect_owner

    # =======================================================
    # 🎲 SISTEMA DE TIRADA DE DADOS
    # =======================================================
    def roll_3d():
        import random
        rolls = [random.choice([True, False]) for _ in range(3)]
        successes = sum(1 for r in rolls if r)
        return {
            "rolls": rolls,
            "successes": successes,
            "success": successes >= 2
        }

    def roll_4d():
        import random
        rolls = [random.choice([True, False]) for _ in range(4)]
        successes = sum(1 for r in rolls if r)
        return {
            "rolls": rolls,
            "successes": successes,
            "success": (successes >= 4)
        }

    def bs_counterattack_can_use(unit_key="player:0", incoming_damage=0):
        try:
            in_dmg = max(0, int(incoming_damage or 0))
        except:
            in_dmg = 0

        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        used = bool(getattr(S, "counterattack_used_in_battle", False))

        hp_cur = int(getattr(S, "player_hp", 0) or 0)
        rei_base = int(getattr(S, "player_reiatsu_base", getattr(S, "player_reiatsu", 0)) or 0)
        ene_base = int(getattr(S, "player_energy_base", getattr(S, "player_energy", 0)) or 0)
        rei_cur = int(getattr(S, "player_reiatsu", 0) or 0)
        ene_cur = int(getattr(S, "player_energy", 0) or 0)

        if mode == "2v2":
            fn_get = getattr(S, "bs_get_unit_by_key", None)
            if callable(fn_get):
                u = fn_get(str(unit_key or ""))
                if isinstance(u, dict):
                    hp_cur = int(u.get("hp", hp_cur) or hp_cur)
                    rei_cur = int(u.get("reiatsu", rei_cur) or rei_cur)
                    ene_cur = int(u.get("energy", ene_cur) or ene_cur)
                    rei_base = int(u.get("base_reiatsu", u.get("max_reiatsu", rei_cur)) or rei_cur)
                    ene_base = int(u.get("base_energy", u.get("max_energy", ene_cur)) or ene_cur)

        rei_need = max(0, int(rei_base * 0.5))
        ene_need = max(0, int(ene_base * 0.5))

        ok = True
        reason = ""
        if used:
            ok = False
            reason = "used"
        elif hp_cur <= 0:
            ok = False
            reason = "dead"
        elif hp_cur <= in_dmg:
            ok = False
            reason = "would_die"
        elif rei_cur < rei_need or ene_cur < ene_need:
            ok = False
            reason = "insufficient_current_for_base_half"

        return {
            "ok": bool(ok),
            "reason": str(reason),
            "incoming_damage": int(in_dmg),
            "hp_current": int(hp_cur),
            "reiatsu_base": int(rei_base),
            "energy_base": int(ene_base),
            "reiatsu_current": int(rei_cur),
            "energy_current": int(ene_cur),
            "reiatsu_penalty": int(rei_need),
            "energy_penalty": int(ene_need),
        }

    def bs_counterattack_execute(unit_key="player:0", incoming_damage=0):
        info = bs_counterattack_can_use(unit_key=unit_key, incoming_damage=incoming_damage)
        if not bool(info.get("ok", False)):
            out = dict(info)
            out["executed"] = False
            out["success"] = False
            out["roll"] = None
            return out

        roll = roll_4d()
        S.counterattack_used_in_battle = True

        try:
            fn_show = getattr(S, "show_dice_result", None)
            if callable(fn_show):
                fn_show(roll, label_text="Contraataque")
        except:
            pass

        success = bool(isinstance(roll, dict) and roll.get("success", False))
        if success:
            return {
                "executed": True,
                "success": True,
                "roll": roll,
                "reiatsu_penalty": 0,
                "energy_penalty": 0,
                "incoming_damage": int(info.get("incoming_damage", 0) or 0),
            }

        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        pr = int(info.get("reiatsu_penalty", 0) or 0)
        pe = int(info.get("energy_penalty", 0) or 0)

        # Aplica penalidad de recursos al defensor en estado de unidad y espejo legacy UI.
        _uk = str(unit_key or "player:0")
        fn_get = getattr(S, "bs_get_unit_by_key", None)
        fn_set = getattr(S, "bs_set_unit_resources", None)
        _applied_on_unit = False

        if callable(fn_get) and callable(fn_set):
            u = fn_get(_uk)
            if isinstance(u, dict):
                cur_r = int(u.get("reiatsu", getattr(S, "player_reiatsu", 0)) or 0)
                cur_e = int(u.get("energy", getattr(S, "player_energy", 0)) or 0)
                res = fn_set(_uk, max(0, cur_r - pr), max(0, cur_e - pe))
                _applied_on_unit = bool(isinstance(res, dict) and res.get("ok", False))

                # En 1v1, espejar siempre a variables legacy del HUD para feedback inmediato.
                if mode != "2v2":
                    S.player_reiatsu = int((res.get("reiatsu", max(0, cur_r - pr)) if isinstance(res, dict) else max(0, cur_r - pr)) or 0)
                    S.player_energy = int((res.get("energy", max(0, cur_e - pe)) if isinstance(res, dict) else max(0, cur_e - pe)) or 0)

        if not _applied_on_unit:
            # Fallback seguro si falta capa de estado por unidad.
            if mode == "2v2":
                pass
            else:
                S.player_reiatsu = max(0, int(getattr(S, "player_reiatsu", 0) or 0) - pr)
                S.player_energy = max(0, int(getattr(S, "player_energy", 0) or 0) - pe)

        try:
            # Mantener preview HUD consistente tras penalidad.
            S.simulated_reiatsu = int(getattr(S, "player_reiatsu", 0) or 0)
            S.simulated_energy = int(getattr(S, "player_energy", 0) or 0)
        except:
            pass

        return {
            "executed": True,
            "success": False,
            "roll": roll,
            "reiatsu_penalty": int(pr),
            "energy_penalty": int(pe),
            "incoming_damage": int(info.get("incoming_damage", 0) or 0),
        }

    def show_dice_result(roll_data, label_text=""):
        # Permite mostrar 1 tirada (dict) o varias tiradas simultáneas (list)
        # para que Directo+Negador puedan verse lado a lado en el centro.
        if isinstance(roll_data, list):
            entries = []
            for e in roll_data:
                if not isinstance(e, dict):
                    continue
                entries.append({
                    "label": str(e.get("label", "") or ""),
                    "rolls": list(e.get("rolls", []) or []),
                })
            if entries:
                renpy.show_screen("dice_roll_result_multi", entries=entries)
            return

        renpy.show_screen("dice_roll_result", rolls=roll_data["rolls"], label_text=label_text)

    store.roll_3d = roll_3d
    store.roll_4d = roll_4d
    store.bs_counterattack_can_use = bs_counterattack_can_use
    store.bs_counterattack_execute = bs_counterattack_execute
    store.show_dice_result = show_dice_result



# ===========================================================
# ⭐ SISTEMA UNIFICADO:
#    CONCENTRAR OFENSIVO + POTENCIAR DEFENSIVO
# ===========================================================
init -982 python:

    # -----------------------------------------------
    # Determinar si puede usarse Concentrar/Potenciar
    # -----------------------------------------------
    def can_use_concentrar(mode):
        if mode == "offensive":
            return focus_off_current_mult == 1
        elif mode == "defensive":
            return boost_def_current_mult == 1
        return False

    # -----------------------------------------------
    # Reset Concentrar al inicio del turno
    # -----------------------------------------------
    def reset_concentrar(mode):
        global focus_off_current_mult, focus_off_stored_mult
        global boost_def_current_mult, boost_def_stored_mult
        global focus_off_used, boost_def_used

        if mode == "offensive":
            focus_off_current_mult = 1
            focus_off_stored_mult  = 1
            focus_off_used = False

        elif mode == "defensive":
            boost_def_current_mult = 1
            boost_def_stored_mult  = 1
            boost_def_used = False

    # -----------------------------------------------
    # Activador unificado
    # -----------------------------------------------
    def activar_concentrar(mode):
        if mode == "offensive":
            activate_offensive_focus()
        elif mode == "defensive":
            activate_defensive_focus()



# ===========================================================
# 🔹 VARIABLES GLOBALES (fuera de init)
# ===========================================================
default incoming_damage = 0
default incoming_damage_target_key = ""
default incoming_damage_source_key = ""
default incoming_damage_sources = []
default offense_cancelled = False
default player_skip_attack_by_key = {}
default enemy_skip_attack_by_key = {}
default deferred_defense_return_to_offense = False
default deferred_defense_actor_key = ""
default player_pending_damage_by_key = {}
default enemy_pending_def_reduction_by_key = {}
default battle_reflected_pending = 0

# Bootstrap seguro sin hardcode de HP; se sincroniza en runtime al iniciar combate.
default battle_hp_enemy_max = 1
default battle_hp_player_max = 1

default battle_turn_owner = "player"
default turn_count = 1

# Flags Directo / Negador
default direct_success = False
default noatk_success  = False
default enemy_noatk_success = False

default maneuver_selected = "none"
default counter_damage = 0
default counterattack_used_in_battle = False

# recursos base (para reglas de maniobras)
default player_reiatsu_base = 0
default player_energy_base = 0
default enemy_reiatsu_base = 0
default enemy_energy_base = 0

# reiatsu y energia
default player_reiatsu = 0
default player_energy  = 0
default enemy_reiatsu  = 0
default enemy_energy   = 0

# tecnicas con dados ia
default enemy_direct_pending_damage = 0
default enemy_direct_base_damage = 0
default player_skip_attack = False

# visibilidad UI de combate (toggles por hotkey)
default ui_show_options_panel = True
default ui_show_unit_hud = True
default ui_show_2v2_summary = True
default ui_show_offensive_techniques = True
default ui_show_defensive_techniques = True
default ui_safe_mode = False
default ui_safe_mode_prompted = False
