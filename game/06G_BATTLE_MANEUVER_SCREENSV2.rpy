# ============================================================
# 06F_BATTLE_MANEUVER_SCREENS.rpy
# Sistema de selección de Maniobras
# v1.7.4 Persistent Pos + NoRenpyImport (Ren’Py 7.4.9)
# ------------------------------------------------------------
# - NO modal: no bloquea paneles (IDs/log/teclas)
# - Ventana movible (drag) + guarda posición (x/y)
# - Toggle show/hide con tecla Y + botón ✖
# - Clamp a pantalla (usa config.screen_width/height)
# - ⚠ Sin "import renpy" para evitar pisadas de módulo
# ============================================================

default show_maneuver_choice = True

# Posición persistente
default maneuver_choice_x = 444
default maneuver_choice_y = 70

init -990 python:
    import renpy.store as S
    import renpy.exports as R

    # Keymap para alternar esta ventanita
    config.keymap["toggle_maneuver_choice"] = ["ctrl_K_y"]

    # Tamaño aproximado de la ventana (para clamp)
    MANEUVER_WIN_W = 392
    MANEUVER_WIN_H = 476

    def toggle_maneuver_choice():
        S.show_maneuver_choice = not getattr(S, "show_maneuver_choice", True)
        R.restart_interaction()

    def _clamp_int(v, lo, hi):
        try:
            v = int(v)
        except:
            v = lo
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    class ManeuverChoiceDragged(object):
        """
        Action estable para dragged (Ren'Py 7.4.9).
        Ren'Py lo llama como action(drags, drop)
        """
        def __call__(self, drags, drop):
            try:
                d = drags[0]
                x = int(getattr(d, "x", S.maneuver_choice_x))
                y = int(getattr(d, "y", S.maneuver_choice_y))
            except Exception:
                return

            # Usar config (store) para evitar import renpy.config
            sw = int(getattr(S.config, "screen_width", 1280))
            sh = int(getattr(S.config, "screen_height", 720))

            max_x = max(0, sw - MANEUVER_WIN_W)
            max_y = max(0, sh - MANEUVER_WIN_H)

            S.maneuver_choice_x = _clamp_int(x, 0, max_x)
            S.maneuver_choice_y = _clamp_int(y, 0, max_y)

            R.restart_interaction()


# -----------------------------------------------------------
# CONTRATO DE RESPONSABILIDAD (Paso 1)
# - Concepto B (canónico): battle_maneuver_choice = ventana de
#   daño entrante + elección de maniobra defensiva.
# - NO usar para avisos de turno ofensivo/defensivo.
# - Los avisos de turno viven en 06D_BATTLE_POPUP_TURN.RPY
#   bajo battle_popup_turn.
# -----------------------------------------------------------



style maneuver_option_button is button:
    xfill True
    yminimum 46
    left_padding 14
    right_padding 14
    top_padding 8
    bottom_padding 8
    background Solid("#FFFFFF10")
    hover_background Solid("#FFFFFF20")
    selected_background Solid("#FFD70030")
    insensitive_background Solid("#FFFFFF08")

style maneuver_option_button_text is button_text:
    color "#BBBBBB"
    hover_color "#FFFFFF"
    selected_color "#FFD700"
    insensitive_color "#666666"

style maneuver_confirm_button is button:
    xalign 0.5
    xminimum 320
    yminimum 54
    left_padding 18
    right_padding 18
    top_padding 10
    bottom_padding 10
    background Solid("#FFFFFF10")
    hover_background Solid("#00BFFFA0")
    activate_background Solid("#D32F2FA0")
    insensitive_background Solid("#FFFFFF08")

style maneuver_confirm_button_text is button_text:
    size 24
    color "#FFFFFF"
    hover_color "#E3F2FD"
    insensitive_color "#777777"

screen battle_maneuver_choice(damage):

    modal False
    zorder 300

    key "toggle_maneuver_choice" action Function(toggle_maneuver_choice)

    default local_choice = "none"
    default show_submenu = False
    default sac_receiver_key = ""
    default local_counter_mode = str(getattr(store, "counterattack_resolution_mode", "dice") or "dice")

    $ import renpy.store as S
    $ will_die = S.player_hp - damage <= 0
    $ is_dead  = S.player_hp <= 0
    $ _actor_k = str(S.bs_current_actor_key() if callable(getattr(S, "bs_current_actor_key", None)) else "")
    $ _skip_map = getattr(S, "player_skip_attack_by_key", {}) if isinstance(getattr(S, "player_skip_attack_by_key", {}), dict) else {}
    $ offense_locked = bool(getattr(S, "player_skip_attack", False) or (_actor_k and bool(_skip_map.get(_actor_k, False))))
    $ _incoming_key = str(getattr(S, "incoming_damage_target_key", "") or _actor_k or "")
    $ _incoming_team = "player"
    $ _counter_ok = False
    $ _counter_reason = ""
    $ _counter_rei_penalty = 0
    $ _counter_ene_penalty = 0
    $ _counter_rei_cur = int(getattr(S, "player_reiatsu", 0) or 0)
    $ _counter_ene_cur = int(getattr(S, "player_energy", 0) or 0)
    $ _sac_ok = False
    $ _sac_reason = ""
    $ _sac_candidates = []
    $ _sac_receiver_hp = 0
    $ _sac_receiver_name = ""
    $ _sac_warn_ko = False
    $ _incoming_slot = 0
    $ _incoming_name = "-"
    $ _incoming_tag = "P1"
    python:
        import renpy.store as S
        try:
            fn_parse = getattr(S, "bs_parse_unit_key", None)
            if callable(fn_parse):
                inf = fn_parse(_incoming_key, default_side="player", default_slot=0)
                _incoming_team = str(inf.get("team", "player") or "player")
                _incoming_slot = int(inf.get("slot", 0) or 0)
            fn_get = getattr(S, "bs_get_unit_by_key", None)
            if callable(fn_get) and _incoming_key:
                uu = fn_get(_incoming_key)
                if isinstance(uu, dict):
                    _incoming_name = str(uu.get("char_id", "") or "-")
            if (_incoming_name == "-" or not _incoming_name) and _incoming_key and callable(getattr(S, "bs_describe_unit_key", None)):
                _incoming_name = str(S.bs_describe_unit_key(_incoming_key, default_side="player", default_slot=0) or "-")
            fn_tag = getattr(S, "bs_slot_tag", None)
            if callable(fn_tag):
                _incoming_tag = str(fn_tag(_incoming_team, _incoming_slot) or "P1")
            else:
                _incoming_tag = ("P{}" if _incoming_team == "player" else "E{}").format(int(_incoming_slot or 0) + 1)

            fn_ctr = getattr(S, "bs_counterattack_can_use", None)
            if callable(fn_ctr):
                c = fn_ctr(unit_key=_incoming_key or "player:0", incoming_damage=damage)
                if isinstance(c, dict):
                    _counter_ok = bool(c.get("ok", False))
                    _counter_reason = str(c.get("reason", "") or "")
                    _counter_rei_penalty = int(c.get("reiatsu_penalty", 0) or 0)
                    _counter_ene_penalty = int(c.get("energy_penalty", 0) or 0)
                    _counter_rei_cur = int(c.get("reiatsu_current", _counter_rei_cur) or _counter_rei_cur)
                    _counter_ene_cur = int(c.get("energy_current", _counter_ene_cur) or _counter_ene_cur)

            _parry_ok = bool(_counter_ok)
            _parry_reason = str(_counter_reason)
            fn_parry = getattr(S, "bs_parry_typing_can_use", None)
            if callable(fn_parry):
                pp = fn_parry(unit_key=_incoming_key or "player:0", incoming_damage=damage)
                if isinstance(pp, dict):
                    _parry_ok = bool(pp.get("ok", _parry_ok))
                    _parry_reason = str(pp.get("reason", _parry_reason) or _parry_reason)

            fn_sac = getattr(S, "bs_sacrifice_can_use", None)
            if callable(fn_sac):
                sc = fn_sac(defender_key=_incoming_key or "player:0", incoming_damage=damage)
                if isinstance(sc, dict):
                    _sac_ok = bool(sc.get("ok", False))
                    _sac_reason = str(sc.get("reason", "") or "")
                    _sac_candidates = list(sc.get("candidates", []) or [])
                    if (not sac_receiver_key) and _sac_candidates:
                        sac_receiver_key = str((_sac_candidates[0].get("key", "") if isinstance(_sac_candidates[0], dict) else "") or "")
                    for _c in _sac_candidates:
                        if not isinstance(_c, dict):
                            continue
                        if str(_c.get("key", "") or "") == str(sac_receiver_key or ""):
                            _sac_receiver_hp = int(_c.get("hp", 0) or 0)
                            _sac_receiver_name = str(_c.get("name", "") or str(_c.get("key", "") or ""))
                            break
                    _sac_warn_ko = bool(_sac_receiver_hp > 0 and int(damage or 0) >= _sac_receiver_hp)
        except:
            pass

    if show_maneuver_choice:

        drag:
            draggable True
            dragged ManeuverChoiceDragged()
            drag_handle (0, 0, 392, 50)

            xpos maneuver_choice_x
            ypos maneuver_choice_y

            frame:
                background "#1119"
                padding (18, 18)
                xmaximum 560
                zoom 0.7

                vbox spacing 14:

                    hbox:
                        xfill True
                        text "Daño entrante: [damage]" size 32 color "#FFD700" bold True xalign 0.0
                        textbutton "✖":
                            action SetVariable("show_maneuver_choice", False)
                            text_size 21

                    frame:
                        background "#0D2233CC"
                        xfill True
                        padding (8, 6)
                        hbox:
                            spacing 10
                            text "Objetivo:" size 18 color "#80DEEA" bold True
                            text "[_incoming_tag] [_incoming_name]" size 19 color "#FFFFFF" bold True

                    viewport:
                        id "maneuver_choice_scroll"
                        xfill True
                        ymaximum 420
                        mousewheel True
                        draggable True
                        scrollbars "vertical"

                        vbox:
                            spacing 10
                            if not show_submenu:

                                text "¿Qué deseas hacer?" size 22 color "#FFFFFF"

                                textbutton "Defender normalmente":
                                    action SetScreenVariable("local_choice", "defense")
                                    style "maneuver_option_button"
                                    text_style "maneuver_option_button_text"
                                    selected local_choice == "defense"
                                    text_size 21

                                if will_die or is_dead or offense_locked:
                                    textbutton "Ataque por defensa (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Ataque por defensa":
                                        action SetScreenVariable("local_choice", "atk_from_def")
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "atk_from_def"
                                        text_size 21

                                if is_dead or offense_locked:
                                    textbutton "Defensa por ataque (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Defensa por ataque":
                                        action SetScreenVariable("local_choice", "def_from_atk")
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "def_from_atk"
                                        text_size 21

                                if not _counter_ok:
                                    textbutton "Contraataque (dados 4/4) (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Contraataque (dados 4/4)":
                                        action [
                                            SetScreenVariable("local_choice", "counterattack"),
                                            SetScreenVariable("local_counter_mode", "dice")
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "counterattack"
                                        text_size 21
                                        text_color "#BBBBBB"
                                        text_hover_color "#FFFFFF"

                                if not _parry_ok:
                                    textbutton "Parry por teclas (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 19
                                        text_color "#666666"
                                else:
                                    textbutton "Parry por teclas":
                                        action [
                                            SetScreenVariable("local_choice", "parry_typing"),
                                            SetScreenVariable("local_counter_mode", "typing")
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "parry_typing"
                                        text_size 19
                                        text_color "#BBBBBB"
                                        text_hover_color "#FFFFFF"

                                if _counter_reason == "used":
                                    text "{color=#FF8888}Contraataque ya fue usado en esta batalla.{/color}"
                                elif _counter_reason == "would_die":
                                    text "{color=#FF4444}No puedes contraatacar: este daño te matará si fallas.{/color}"
                                elif _counter_reason == "insufficient_current_for_base_half":
                                    text "{color=#FFCC66}Requiere >=50% de recurso actual vs base: R [_counter_rei_cur]/[_counter_rei_penalty] · E [_counter_ene_cur]/[_counter_ene_penalty].{/color}"
                                elif _counter_reason == "dead":
                                    text "{color=#FF4444}Estás derrotada. No puedes contraatacar.{/color}"

                                if will_die:
                                    text "{color=#FF4444}No puedes contraatacar: este daño te matará.{/color}"
                                elif is_dead:
                                    text "{color=#FF4444}Estás derrotada. No puedes contraatacar.{/color}"
                                elif offense_locked:
                                    text "{color=#FF66CC}Ataque negador activo: solo puedes defender normalmente.{/color}"

                                if not _sac_ok:
                                    textbutton "Solicitar maniobra de sacrificio (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 19
                                        text_color "#666666"
                                else:
                                    textbutton "Solicitar maniobra de sacrificio":
                                        action SetScreenVariable("local_choice", "sacrifice_request")
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "sacrifice_request"
                                        text_size 19

                                if _sac_reason == "used":
                                    text "{color=#FF8888}Sacrificio ya fue usado por tu equipo en esta batalla.{/color}"
                                elif _sac_reason == "no_ally_available":
                                    text "{color=#FFCC66}No hay aliado disponible para recibir el daño.{/color}"

                                if local_choice == "sacrifice_request" and _sac_ok and _sac_candidates:
                                    text "Aliado que se sacrifica:" size 16 color "#B3E5FC"
                                    hbox:
                                        spacing 8
                                        for _c in _sac_candidates:
                                            $ _ck = str(_c.get("key", "") or "") if isinstance(_c, dict) else ""
                                            $ _cn = str(_c.get("name", _ck) or _ck) if isinstance(_c, dict) else _ck
                                            $ _ch = int(_c.get("hp", 0) or 0) if isinstance(_c, dict) else 0
                                            textbutton "{} (HP {})".format(_cn, battle_fmt_num(_ch)):
                                                action SetScreenVariable("sac_receiver_key", _ck)
                                                style "maneuver_option_button"
                                                text_style "maneuver_option_button_text"
                                                selected _ck == sac_receiver_key
                                                text_color ("#66CCFF" if _ck == sac_receiver_key else "#FFFFFF")

                                    if _sac_warn_ko:
                                        text "{color=#FF8888}Advertencia: %s podría morir al recibir %s de daño.{/color}" % (str(_sac_receiver_name or "El aliado"), str(battle_fmt_num(damage)))

                                textbutton "Ver maniobras…":
                                    action SetScreenVariable("show_submenu", True)
                                    style "maneuver_option_button"
                                    text_style "maneuver_option_button_text"
                                    text_size 21

                                textbutton "Confirmar decisión":
                                    action [
                                        SetVariable("maneuver_selected", local_choice),
                                        SetVariable("counterattack_resolution_mode", local_counter_mode),
                                        SetVariable("sacrifice_receiver_key", sac_receiver_key),
                                        Hide("battle_maneuver_choice"),
                                        SetVariable("show_maneuver_choice", True)
                                    ]
                                    style "maneuver_confirm_button"
                                    text_style "maneuver_confirm_button_text"
                                    sensitive local_choice != "none"

                                text "Arrastrá para mover • Ctrl+Y: ocultar/mostrar" size 13 color "#BBBBBB" xalign 0.5

                            else:

                                text "Maniobras disponibles:" size 24 color "#FFD700" bold True

                                if will_die or is_dead or offense_locked:
                                    textbutton "Ataque por defensa (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Ataque por defensa":
                                        action [
                                            SetScreenVariable("local_choice", "atk_from_def"),
                                            SetScreenVariable("show_submenu", False)
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "atk_from_def"
                                        text_size 21

                                if is_dead or offense_locked:
                                    textbutton "Defensa por ataque (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Defensa por ataque":
                                        action [
                                            SetScreenVariable("local_choice", "def_from_atk"),
                                            SetScreenVariable("show_submenu", False)
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "def_from_atk"
                                        text_size 21

                                if not _counter_ok:
                                    textbutton "Contraataque (dados 4/4) (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 21
                                        text_color "#666666"
                                else:
                                    textbutton "Contraataque (dados 4/4)":
                                        action [
                                            SetScreenVariable("local_choice", "counterattack"),
                                            SetScreenVariable("local_counter_mode", "dice"),
                                            SetScreenVariable("show_submenu", False)
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "counterattack"
                                        text_size 21
                                        text_color "#BBBBBB"
                                        text_hover_color "#FFFFFF"

                                if not _parry_ok:
                                    textbutton "Parry por teclas (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 19
                                        text_color "#666666"
                                else:
                                    textbutton "Parry por teclas":
                                        action [
                                            SetScreenVariable("local_choice", "parry_typing"),
                                            SetScreenVariable("local_counter_mode", "typing"),
                                            SetScreenVariable("show_submenu", False)
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "parry_typing"
                                        text_size 19
                                        text_color "#BBBBBB"
                                        text_hover_color "#FFFFFF"

                                if not _sac_ok:
                                    textbutton "Solicitar maniobra de sacrificio (no disponible)":
                                        action NullAction()
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        text_size 19
                                        text_color "#666666"
                                else:
                                    textbutton "Solicitar maniobra de sacrificio":
                                        action [
                                            SetScreenVariable("local_choice", "sacrifice_request"),
                                            SetScreenVariable("show_submenu", False)
                                        ]
                                        style "maneuver_option_button"
                                        text_style "maneuver_option_button_text"
                                        selected local_choice == "sacrifice_request"
                                        text_size 19

                                textbutton "Cancelar":
                                    action SetScreenVariable("show_submenu", False)
                                    style "maneuver_option_button"
                                    text_style "maneuver_option_button_text"
                                    text_size 21

                                textbutton "Confirmar decisión":
                                    action [
                                        SetVariable("maneuver_selected", local_choice),
                                        SetVariable("counterattack_resolution_mode", local_counter_mode),
                                        SetVariable("sacrifice_receiver_key", sac_receiver_key),
                                        Hide("battle_maneuver_choice"),
                                        SetVariable("show_maneuver_choice", True)
                                    ]
                                    style "maneuver_confirm_button"
                                    text_style "maneuver_confirm_button_text"
                                    sensitive local_choice != "none"

                                text "Arrastrá para mover • Ctrl+Y: ocultar/mostrar" size 13 color "#BBBBBB" xalign 0.5

# -----------------------------------------------------------
# Contraataque por mecanografía (QTE)
# -----------------------------------------------------------
transform ctr_typing_letter_pulse(_dur=2.0):
    zoom 0.55
    linear _dur zoom 1.85

screen counterattack_typing_qte():
    modal True
    zorder 250

    default _letters = "abcdefghijklmnopqrstuvwxyz"

    python:
        import renpy.store as S
        _st = getattr(S, "counterattack_typing_state", {})
        _cur = str(_st.get("current_letter", "") or "")
        _idx = int(_st.get("index", 0) or 0)
        _tot = int(_st.get("total", 0) or 0)
        _left = float(_st.get("time_left", 0.0) or 0.0)
        _spl = max(2.0, float(_st.get("seconds_per_letter", 2.0) or 2.0))
        _status = str(_st.get("last_status", "active") or "active").strip().lower()
        _hits = int(_st.get("hits", 0) or 0)
        _miss = int(_st.get("misses", 0) or 0)
        _req = int(_st.get("required_hits", 6) or 6)
        _fb = float(_st.get("feedback_time_left", 0.0) or 0.0)
        _progress = 0.0 if _spl <= 0.0 else max(0.0, min(1.0, (_spl - _left) / _spl))

        if _status in ("wrong", "timeout"):
            _c = "#FF4D4D"
        elif _status in ("hit", "success"):
            _c = "#66FF99"
        else:
            _c = "#FFFFFF"

    timer 0.02 repeat True action Function(getattr(store, "bs_counterattack_typing_tick", None), 0.02)

    for _k in _letters:
        key _k action Function(getattr(store, "bs_counterattack_typing_press_key", None), _k)

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        xmaximum 860
        padding (28, 22)

        vbox:
            spacing 12

            frame:
                background "#0000"
                xfill True
                ymaximum 280
                padding (0, 0)

                fixed:
                    xfill True
                    ysize 260

                    text (_cur if _cur else "-"):
                        xalign 0.5
                        yalign 0.5
                        size 120
                        color _c
                        bold True
                        at ctr_typing_letter_pulse(_spl)

            if _fb > 0.0:
                if _status == "hit":
                    text "ÉXITO" size 52 color "#66FF99" bold True xalign 0.5
                elif _status == "timeout":
                    text "FALLO" size 52 color "#FF4D4D" bold True xalign 0.5

            text ("Letra %d/%d   %.2f s   ✔ %d / ✖ %d (mín %d)" % (int(_idx + 1), int(max(1, _tot)), float(_left or 0.0), int(_hits), int(_miss), int(_req))) size 20 color "#D0D0D0" xalign 0.5
