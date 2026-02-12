# ============================================================
# 03_VISUAL_SYSTEM_BASIC.RPY – Log y Popups básicos
# ============================================================
# v2.2.1 Hardened + StoreSafe + DragFix (Ren’Py 7.4.9)
# ------------------------------------------------------------
# ✔ Store-safe (sin globals peligrosos)
# ✔ Drag correcto (soporta lista/drag/tuple)
# ✔ Log con límite (sin memory leak)
# ✔ Sin import directo de battle_techniques
# ✔ Usa iconos de dados escalados
# ============================================================


# -----------------------------------------------------------
# 🔧 FALLBACKS (STORE-SAFE)
# -----------------------------------------------------------
init -980 python:
    import renpy.store as S

    if not hasattr(S, "battle_fmt_num"):
        def battle_fmt_num(n):
            try:
                return "{:,}".format(int(n)).replace(",", ".")
            except:
                return str(n)
        S.battle_fmt_num = battle_fmt_num

    if not hasattr(S, "debug_log"):
        def debug_log(msg):
            try:
                renpy.log("[DEBUG] " + str(msg))
            except:
                pass
        S.debug_log = debug_log

    battle_fmt_num = S.battle_fmt_num
    debug_log = S.debug_log


# -----------------------------------------------------------
# 🔷 SISTEMA VISUAL BASE
# -----------------------------------------------------------
init -978 python:
    import renpy.store as S

    debug_log("✅ Visual System Basic v2.2.1 cargado.")

    # -------------------------------------------------------
    # Estado del log (store-safe)
    # -------------------------------------------------------
    if not hasattr(S, "battle_log"):
        S.battle_log = []

    battle_log = S.battle_log
    MAX_LOG_LINES = 250

    DEFAULT_LOG_POS = (800, 100)

    if not hasattr(persistent, "battle_log_pos"):
        persistent.battle_log_pos = DEFAULT_LOG_POS


    # -------------------------------------------------------
    # Drag helpers (FIX: lista/drag/tuple)
    # -------------------------------------------------------
    def _drag_pos_safe(d):
        """
        Ren'Py puede pasar:
        - Drag con .x/.y
        - lista/tuple de Drag (joined)
        - tuple/list (x, y)
        Devuelve (x, y) seguro.
        """
        try:
            # Si viene lista/tuple de drags, tomamos el primero
            if isinstance(d, (list, tuple)):
                if not d:
                    return DEFAULT_LOG_POS
                d0 = d[0]

                if hasattr(d0, "x") and hasattr(d0, "y"):
                    return (int(d0.x), int(d0.y))

                if isinstance(d0, (list, tuple)) and len(d0) >= 2:
                    return (int(d0[0]), int(d0[1]))

                return DEFAULT_LOG_POS

            # Drag normal
            if hasattr(d, "x") and hasattr(d, "y"):
                return (int(d.x), int(d.y))

            # (x, y)
            if isinstance(d, (list, tuple)) and len(d) >= 2:
                return (int(d[0]), int(d[1]))

        except:
            pass

        return DEFAULT_LOG_POS


    # -------------------------------------------------------
    # Posición persistente
    # -------------------------------------------------------
    def save_battle_log_position_xy(pos):
        try:
            p = _drag_pos_safe(pos)
            persistent.battle_log_pos = (int(p[0]), int(p[1]))
            renpy.save_persistent()
        except Exception as e:
            debug_log("⚠️ Error guardando posición log: {}".format(e))

    def get_battle_log_position():
        try:
            pos = persistent.battle_log_pos
            if not pos or len(pos) < 2:
                raise ValueError("Posición inválida")
            return (int(pos[0]), int(pos[1]))
        except Exception:
            persistent.battle_log_pos = DEFAULT_LOG_POS
            return DEFAULT_LOG_POS


    # -------------------------------------------------------
    # API DEL LOG
    # -------------------------------------------------------
    def _trim_log_if_needed():
        try:
            if len(battle_log) > MAX_LOG_LINES:
                del battle_log[:-MAX_LOG_LINES]
        except:
            pass

    def battle_log_clear():
        del battle_log[:]
        if renpy.get_screen("battle_log_screen"):
            renpy.restart_interaction()

    def battle_log_add(text, color=None, tech_key=None):
        techniques = getattr(S, "battle_techniques", {}) or {}
        tech = techniques.get(tech_key, {}) if tech_key else {}

        if not color:
            if tech.get("reflective"):
                color = "#55FFFF"
            elif tech.get("supportive"):
                color = "#B5CEA8"
            elif tech.get("debuff"):
                color = "#FF9966"
            elif tech.get("type") == "offensive":
                color = "#FF8888"
            elif tech.get("type") == "defensive":
                color = "#9CDCFE"
            elif tech.get("type") == "special":
                color = "#C586C0"
            else:
                color = "#DDDDDD"

        safe_text = str(text).replace("[", "[[").replace("]", "]]")

        battle_log.append({
            "text": safe_text,
            "color": color
        })

        _trim_log_if_needed()

        if renpy.get_screen("battle_log_screen"):
            renpy.restart_interaction()

    def battle_log_phase(title):
        upper = str(title).upper()

        if "OFENSIVO" in upper:
            bg_color = "#FF444480"
        elif "DEFENSIVO" in upper:
            bg_color = "#00BFFFA0"
        elif "COMIENZA" in upper or "COMBATE" in upper:
            bg_color = "#FFFFFF60"
        else:
            bg_color = "#99999960"

        if "HARRIBEL" in upper:
            text_color = "#FFD700"
        elif "GRIMMJOW" in upper:
            text_color = "#00FFFF"
        elif "NEL" in upper:
            text_color = "#99FFFF"
        elif "HOLLOW" in upper:
            text_color = "#FFAAAA"
        else:
            text_color = "#FFFFFF"

        parts = str(title).split("–")
        phase_part = parts[0].strip()
        name_part = parts[1].strip() if len(parts) >= 2 else ""

        if "TURNO" in phase_part:
            phase_part = "— " + phase_part.replace("—", "").replace("-", "").strip() + " —"

        name_part = name_part.replace("—", "").replace("-", "").strip()

        formatted_title = "{b}{color=%s}{size=26}⚔ %s{/size}{/color}{/b}" % (
            text_color, phase_part)

        formatted_name = None
        if name_part:
            formatted_name = "{b}{color=%s}{size=24}%s{/size}{/color}{/b}" % (
                text_color, name_part)

        battle_log.append({
            "text": formatted_title,
            "color": text_color,   # ✅ nunca None
            "bg": bg_color,
            "name": formatted_name
        })

        _trim_log_if_needed()

        if renpy.get_screen("battle_log_screen"):
            renpy.restart_interaction()

    def battle_log_result(target, dmg, hp):
        battle_log_add(
            "[RESULTADO] {} recibe {} (HP: {})".format(
                target, battle_fmt_num(dmg), battle_fmt_num(hp)
            ),
            "#C0FFC0"
        )

    # Export opcional a store (por si otros módulos lo buscan ahí)
    S.save_battle_log_position_xy = save_battle_log_position_xy
    S.get_battle_log_position = get_battle_log_position
    S.battle_log_clear = battle_log_clear
    S.battle_log_add = battle_log_add
    S.battle_log_phase = battle_log_phase
    S.battle_log_result = battle_log_result
    S._drag_pos_safe = _drag_pos_safe


# -----------------------------------------------------------
# 📜 SCREEN PRINCIPAL DEL REGISTRO
# -----------------------------------------------------------
screen battle_log_screen():
    tag battlelog
    modal False
    zorder 120

    $ start_pos = get_battle_log_position()

    drag:
        drag_name "battle_log_drag"
        draggable True
        droppable False
        drag_raise True
        pos start_pos
        dragged (lambda d, drop: save_battle_log_position_xy(_drag_pos_safe(d)))

        frame:
            background "#111C"
            xmaximum 480
            ymaximum 460
            padding (10, 10)

            vbox:
                spacing 4
                text "Registro de combate" size 22 color "#FFD700" bold True
                null height 6

                viewport:
                    draggable True
                    mousewheel True
                    yinitial 1.0
                    scrollbars "vertical"
                    style_prefix "battlelog_scroll"

                    vbox:
                        for row in battle_log:
                            if "bg" in row:
                                frame:
                                    background row["bg"]
                                    xfill True
                                    padding (8, 8)
                                    vbox:
                                        spacing 2
                                        text row["text"] size 20 xalign 0.0 outlines [(2, "#000", 0, 0)]
                                        if row.get("name"):
                                            text row["name"] size 20 xalign 0.5 outlines [(2, "#000", 0, 0)]
                            else:
                                text row["text"] size 20 color row.get("color", "#DDDDDD") xalign 0.0


# -----------------------------------------------------------
# 🎨 ESTILOS SCROLLBAR
# -----------------------------------------------------------
style battlelog_scroll_vscrollbar:
    base_bar Frame(Solid("#444444"), 8, 0)
    thumb Frame(Solid("#AAAAAA"), 8, 0)
    xalign 1.0
    yfill True
    unscrollable "hide"

style battlelog_scroll_vthumb:
    xsize 8
    ysize 40


# -----------------------------------------------------------
# POPUP DE TURNO (con delay configurable)
# -----------------------------------------------------------
screen battle_popup_turn(text, color="#FFD700", delay=2.5):
    zorder 300
    frame:
        background "#0008"
        xalign 0.5
        yalign 0.4
        xsize 640
        ysize 130
        vbox:
            xalign 0.5
            spacing 8
            text text size 46 color color bold True xalign 0.5 outlines [(2, "#000", 0, 0)]
    timer delay action Hide("battle_popup_turn")


# -----------------------------------------------------------
# ⌨️ HOTKEYS
# -----------------------------------------------------------
init python:
    def toggle_battle_log():
        if renpy.get_screen("battle_log_screen"):
            renpy.hide_screen("battle_log_screen")
        else:
            renpy.show_screen("battle_log_screen")

screen battle_keymap_layer():
    key "k" action Function(toggle_battle_log)
    key "K" action Function(toggle_battle_log)
    key "c" action Function(battle_log_clear)
    key "C" action Function(battle_log_clear)

init python:
    if "battle_keymap_layer" not in config.overlay_screens:
        config.overlay_screens.append("battle_keymap_layer")


# -----------------------------------------------------------
# 🎲 RESULTADO DE DADOS
# -----------------------------------------------------------
screen dice_roll_result(rolls):
    tag dice_result
    modal True
    zorder 500

    frame:
        xalign 0.5
        yalign 0.45
        background "#0008"
        padding (20, 20)

        hbox spacing 20:
            for r in rolls:
                if r:
                    add "dice_success_icon"
                else:
                    add "dice_fail_icon"

    timer 2.2 action Hide("dice_roll_result")
