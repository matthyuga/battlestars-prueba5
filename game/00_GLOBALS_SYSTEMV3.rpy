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
        try:
            if isinstance(entity, dict):
                return int(entity.get("HP", 0)) <= 0
            return int(entity) <= 0
        except:
            return False

    def battle_clamp_hp(hp, min_value=0, max_value=99999):
        try:
            return max(min(int(hp), max_value), min_value)
        except:
            return min_value

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

    def operation_dump_to_battle_log(title="📘 Operación Defensiva:"):
        if not debug_operation_log:
            return
        try:
            battle_log_add(title, "#00FFFF")
            for txt, col in debug_operation_log:
                battle_log_add("   " + txt, col or OP_COLOR_TEXT)
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

    def show_dice_result(roll_data):
        renpy.show_screen("dice_roll_result", rolls=roll_data["rolls"])

    store.roll_3d = roll_3d
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
default battle_reflected_pending = 0

default battle_hp_enemy_max = 10000
default battle_hp_player_max = 10000

default battle_turn_owner = "player"
default turn_count = 1

# Flags Directo / Negador
default direct_success = False
default noatk_success  = False

default maneuver_selected = "none"
default counter_damage = 0

# reiatsu y energia
default player_reiatsu = 0
default player_energy  = 0
default enemy_reiatsu  = 0
default enemy_energy   = 0

# tecnicas con dados ia
default enemy_direct_pending_damage = 0
default enemy_direct_base_damage = 0
default player_skip_attack = False
