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
    import time

    debug_log("✅ Visual System Basic v2.2.1 cargado.")

    # -------------------------------------------------------
    # Estado del log (store-safe)
    # -------------------------------------------------------
    if not hasattr(S, "battle_log"):
        S.battle_log = []

    battle_log = S.battle_log

    if not hasattr(S, "ui_show_battle_debug_log"):
        S.ui_show_battle_debug_log = False
    if not hasattr(S, "ui_show_offensive_operation_details"):
        S.ui_show_offensive_operation_details = False
    if not hasattr(S, "ui_show_target_assignment_details"):
        S.ui_show_target_assignment_details = False
    if not hasattr(S, "ui_show_queue_2v2_details"):
        S.ui_show_queue_2v2_details = False

    # Fase 8: persistencia de toggles por sesión (runtime store)
    if not hasattr(S, "battle_log_ui_session_prefs") or not isinstance(getattr(S, "battle_log_ui_session_prefs", None), dict):
        S.battle_log_ui_session_prefs = {
            "ui_show_battle_debug_log": bool(getattr(S, "ui_show_battle_debug_log", False)),
            "ui_show_offensive_operation_details": bool(getattr(S, "ui_show_offensive_operation_details", False)),
            "ui_show_target_assignment_details": bool(getattr(S, "ui_show_target_assignment_details", False)),
            "ui_show_queue_2v2_details": bool(getattr(S, "ui_show_queue_2v2_details", False)),
        }

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


    def battle_log_on_dragged(d, drop):
        try:
            save_battle_log_position_xy(_drag_pos_safe(d))
        except:
            pass


    def battle_log_set_ui_flag(flag_name, value):
        try:
            setattr(S, str(flag_name), bool(value))
        except:
            pass
        try:
            prefs = getattr(S, "battle_log_ui_session_prefs", None)
            if isinstance(prefs, dict):
                prefs[str(flag_name)] = bool(value)
        except:
            pass

    def battle_log_toggle_ui_flag(flag_name):
        cur = bool(getattr(S, str(flag_name), False))
        battle_log_set_ui_flag(flag_name, (not cur))

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

    def _to_line_text(raw_text):
        try:
            return str(raw_text or "")
        except:
            return ""

    def _is_debug_line_text(raw_text):
        txt = _to_line_text(raw_text)
        return "[DEBUG]" in txt

    def _row_group_for_text(raw_text):
        txt = _to_line_text(raw_text)
        low = txt.lower()

        # C2: colapsables
        if ("operación" in low):
            return "operation"
        if ("target asignado" in low) or ("ai target policy" in low):
            return "target_assignment"
        if ("daño en cola 2v2" in low) or ("daño entrante en cola 2v2" in low):
            return "queue_2v2"

        return None

    def battle_log_add(text, color=None, tech_key=None, is_debug=None, group=None):
        techniques = getattr(S, "battle_techniques", {}) or {}
        tech = techniques.get(tech_key, {}) if tech_key else {}

        if is_debug is None:
            is_debug = _is_debug_line_text(text)

        row_group = group if group is not None else _row_group_for_text(text)

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
            "color": color,
            "debug": bool(is_debug),
            "group": row_group
        })

        _trim_log_if_needed()

        if renpy.get_screen("battle_log_screen"):
            renpy.restart_interaction()

    def battle_log_add_debug(text, color="#80DEEA"):
        battle_log_add(text, color=color, is_debug=True)

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

    def bs_dev_instant_victory():
        """
        Herramienta dev-only:
        fuerza KO del equipo enemigo y redirige al cierre canónico `battle_end`.
        Guardrails:
          - requiere config.developer
          - requiere flag runtime bs_saga_dev_admin_enabled=true
        """
        if not bool(getattr(config, "developer", False)):
            return {"ok": False, "reason": "developer_mode_required"}

        if not bool(getattr(S, "bs_saga_dev_admin_enabled", False)):
            return {"ok": False, "reason": "dev_admin_flag_required"}

        affected = []
        fn_alive = getattr(S, "bs_get_alive_unit_keys", None)
        fn_apply = getattr(S, "bs_apply_damage_to_unit_key", None)
        fn_set_hp = getattr(S, "bs_set_hp", None)

        try:
            if callable(fn_alive) and callable(fn_apply):
                enemy_keys = list(fn_alive("enemy") or [])
                for key in enemy_keys:
                    rr = fn_apply(key, 10 ** 9, source_key=getattr(S, "bs_current_actor_key", lambda: "")())
                    affected.append({
                        "key": str(key),
                        "ok": bool(isinstance(rr, dict) and rr.get("ok", False)),
                    })
            elif callable(fn_set_hp):
                fn_set_hp("enemy", 0)
                affected.append({"key": "enemy:active", "ok": True})
            else:
                S.enemy_hp = 0
                affected.append({"key": "enemy_legacy", "ok": True})
        except Exception as ex:
            return {"ok": False, "reason": "instant_victory_exception", "error": str(ex)}

        S.enemy_hp = 0
        S.story_pilot_debug_last_force_victory = {
            "ts": int(time.time()),
            "action": "dev_instant_victory",
            "affected": list(affected),
        }

        fn_log = getattr(S, "battle_log_add", None)
        if callable(fn_log):
            fn_log("{color=#80DEEA}[DEV] Victoria instantánea activada → cierre battle_end.{/color}")

        renpy.jump("battle_end")
        return {"ok": True, "reason": "jump_battle_end"}

    # Export opcional a store (por si otros módulos lo buscan ahí)
    S.save_battle_log_position_xy = save_battle_log_position_xy
    S.get_battle_log_position = get_battle_log_position
    S.battle_log_clear = battle_log_clear
    S.battle_log_add = battle_log_add
    S.battle_log_add_debug = battle_log_add_debug
    S.battle_log_phase = battle_log_phase
    S.battle_log_result = battle_log_result
    S.bs_dev_instant_victory = bs_dev_instant_victory
    S._drag_pos_safe = _drag_pos_safe


# -----------------------------------------------------------
# 📜 SCREEN PRINCIPAL DEL REGISTRO
# -----------------------------------------------------------
screen battle_log_screen():
    tag battlelog
    modal False
    zorder 120

    key "ctrl_K_b" action ToggleVariable("ui_show_battle_debug_log")
    key "ctrl_K_d" action ToggleVariable("ui_show_offensive_operation_details")
    key "ctrl_K_g" action ToggleVariable("ui_show_target_assignment_details")
    key "ctrl_K_q" action ToggleVariable("ui_show_queue_2v2_details")
    key "d" action ToggleVariable("ui_show_offensive_operation_details")
    key "g" action ToggleVariable("ui_show_target_assignment_details")
    key "q" action ToggleVariable("ui_show_queue_2v2_details")
    key "b" action ToggleVariable("ui_show_battle_debug_log")
    key "ctrl_K_v" action Function(bs_dev_instant_victory)

    $ start_pos = get_battle_log_position()

    drag:
        drag_name "battle_log_drag"
        draggable True
        droppable False
        drag_raise True
        pos start_pos
        dragged battle_log_on_dragged

        frame:
            background "#111C"
            xmaximum 480
            ymaximum 460
            padding (10, 10)

            vbox:
                spacing 4
                text "Registro de combate (narrativo)" size 22 color "#FFD700" bold True
                textbutton ("[[B]] Debug: visible" if ui_show_battle_debug_log else "[[B]] Debug: oculto"):
                    action ToggleVariable("ui_show_battle_debug_log")
                    text_size 14
                    text_color "#80DEEA"
                    background "#0000"
                    xalign 1.0

                hbox:
                    spacing 10
                    textbutton ("[[D]] ▸ Operación" if not ui_show_offensive_operation_details else "[[D]] ▾ Operación"):
                        action ToggleVariable("ui_show_offensive_operation_details")
                        text_size 13
                        text_color "#E0E0E0"
                        background "#0000"
                    textbutton ("[[G]] ▸ Target" if not ui_show_target_assignment_details else "[[G]] ▾ Target"):
                        action ToggleVariable("ui_show_target_assignment_details")
                        text_size 13
                        text_color "#B0E0E6"
                        background "#0000"
                    textbutton ("[[Q]] ▸ Cola 2v2" if not ui_show_queue_2v2_details else "[[Q]] ▾ Cola 2v2"):
                        action ToggleVariable("ui_show_queue_2v2_details")
                        text_size 13
                        text_color "#B39DDB"
                        background "#0000"

                if config.developer and bool(getattr(store, "bs_saga_dev_admin_enabled", False)):
                    textbutton "[[Ctrl+K+V]] ⚡ Victoria instantánea (dev)":
                        action Function(bs_dev_instant_victory)
                        text_size 13
                        text_color "#80DEEA"
                        background "#0000"

                null height 6

                viewport:
                    draggable True
                    mousewheel True
                    yinitial 1.0
                    scrollbars "vertical"
                    style_prefix "battlelog_scroll"

                    vbox:
                        for row in battle_log:
                            $ _show_debug = (not row.get("debug", False)) or ui_show_battle_debug_log
                            $ _grp = row.get("group", None)
                            $ _show_grp = (
                                (_grp is None) or
                                (_grp == "operation" and ui_show_offensive_operation_details) or
                                (_grp == "offensive_operation" and ui_show_offensive_operation_details) or
                                (_grp == "defensive_operation" and ui_show_offensive_operation_details) or
                                (_grp == "target_assignment" and ui_show_target_assignment_details) or
                                (_grp == "queue_2v2" and ui_show_queue_2v2_details)
                            )
                            if _show_debug and _show_grp:
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
# [DEPRECATED] Mantener solo como referencia visual legacy.
# El owner canónico de battle_popup_turn vive en 06D_BATTLE_POPUP_TURN.RPY.
screen battle_popup_turn_legacy_visual(text, color="#FFD700", delay=2.5):
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
    timer delay action Hide("battle_popup_turn_legacy_visual")


# -----------------------------------------------------------
# ⌨️ HOTKEYS
# -----------------------------------------------------------
init python:
    def toggle_battle_log():
        if renpy.get_screen("battle_log_screen"):
            renpy.hide_screen("battle_log_screen")
        else:
            renpy.show_screen("battle_log_screen")

    def _dice_icon_pair_for_label(label_text=""):
        try:
            _lbl = str(label_text or "").strip().lower()
        except:
            _lbl = ""
        # Solo Dados de Furia usa las variantes de furia.
        if "furia" in _lbl:
            return "dice_success_fury_icon", "dice_fail_fury_icon"
        return "dice_success_icon", "dice_fail_icon"

screen battle_keymap_layer():
    key "ctrl_K_k" action Function(toggle_battle_log)
    key "ctrl_K_c" action Function(battle_log_clear)

init python:
    if "battle_keymap_layer" not in config.overlay_screens:
        config.overlay_screens.append("battle_keymap_layer")


# -----------------------------------------------------------
# 🎲 RESULTADO DE DADOS
# -----------------------------------------------------------
screen dice_roll_result(rolls, label_text=""):
    tag dice_result
    modal True
    zorder 500

    frame:
        xalign 0.5
        yalign 0.45
        background "#0008"
        padding (20, 20)

        vbox spacing 10:
            $ _ok_icon, _ko_icon = _dice_icon_pair_for_label(label_text)
            if label_text:
                text "[label_text]" size 28 color "#FFD700" bold True xalign 0.5

            hbox spacing 20:
                for r in rolls:
                    if r:
                        add _ok_icon
                    else:
                        add _ko_icon

    timer 2.2 action Hide("dice_roll_result")


screen dice_roll_result_multi(entries):
    tag dice_result
    modal True
    zorder 500

    frame:
        xalign 0.5
        yalign 0.45
        background "#0008"
        padding (20, 20)

        hbox spacing 24:
            for e in (entries or []):
                $ _lbl = str(e.get("label", "") or "") if isinstance(e, dict) else ""
                $ _rolls = list(e.get("rolls", []) or []) if isinstance(e, dict) else []
                $ _ok_icon, _ko_icon = _dice_icon_pair_for_label(_lbl)

                frame:
                    background "#0006"
                    padding (14, 12)

                    vbox spacing 8:
                        if _lbl:
                            text "[_lbl]" size 24 color "#FFD700" bold True xalign 0.5

                        hbox spacing 14:
                            for r in _rolls:
                                if r:
                                    add _ok_icon
                                else:
                                    add _ko_icon

    timer 2.4 action Hide("dice_roll_result_multi")


screen dice_roll_result_stack(entries):
    tag dice_result
    modal True
    zorder 500

    frame:
        xalign 0.5
        yalign 0.45
        background "#0008"
        padding (20, 18)

        vbox:
            spacing 12
            for e in (entries or []):
                $ _lbl = str(e.get("label", "") or "") if isinstance(e, dict) else ""
                $ _rolls = list(e.get("rolls", []) or []) if isinstance(e, dict) else []
                $ _ok_icon, _ko_icon = _dice_icon_pair_for_label(_lbl)

                frame:
                    background "#0006"
                    padding (14, 10)

                    vbox:
                        spacing 8
                        if _lbl:
                            text "[_lbl]" size 24 color "#FFD700" bold True xalign 0.5

                        hbox:
                            spacing 14
                            xalign 0.5
                            for r in _rolls:
                                if r:
                                    add _ok_icon
                                else:
                                    add _ko_icon

    timer 2.7 action Hide("dice_roll_result_stack")


screen recovery_dice_prompt():
    modal True
    zorder 550

    frame:
        xalign 0.5
        yalign 0.5
        background "#000C"
        padding (24, 20)
        xmaximum 900

        vbox:
            spacing 14
            text "Has caído en combate" size 36 color "#FF8888" bold True xalign 0.5
            text "Puedes lanzar 1 dado de recuperación (solo 1 vez por combate)." size 24 color "#DDDDDD" xalign 0.5
            text "Resultado: 0% = KO definitivo | 25/50/75/100% = HP restaurado." size 21 color "#FFD700" xalign 0.5

            hbox:
                spacing 20
                xalign 0.5

                textbutton "🎲 Tirar dado de recuperación":
                    text_size 24
                    action Return("roll")

                textbutton "☠ Caer derrotado":
                    text_size 24
                    action Return("defeat")


screen recovery_dice_result(value_pct=0):
    tag dice_result
    modal True
    zorder 560

    frame:
        xalign 0.5
        yalign 0.45
        background "#0008"
        padding (26, 20)

        vbox:
            spacing 10
            text "Dados de recuperación" size 30 color "#FFD700" bold True xalign 0.5
            text "Resultado de tirada: [value_pct]" size 38 color "#88FF88" bold True xalign 0.5
            $ _dv = int(value_pct or 0)
            if _dv not in (0, 25, 50, 75, 100):
                $ _dv = 0
            $ _dice_img = "gui/dice/dt%d.png" % int(_dv)
            add im.Scale(_dice_img, 200, 200) xalign 0.5

    timer 1.8 action Hide("recovery_dice_result")
