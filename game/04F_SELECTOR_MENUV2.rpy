# ============================================================
# 04F_SELECTOR_MENUV2.rpy – Menú de Técnicas Moderno (v7.2 FIXED)
# Dynamic Cost Edition – basado en el sistema 04X
# ------------------------------------------------------------
# ✔ Tooltips muestran daño/bloqueo FINAL REAL (post buffs)
# ✔ Reiatsu/Energía muestran costo REAL dinámico
# ✔ Focus/Potenciar: tooltip explica EFECTO FUTURO (no estado interno)
# ✔ Si ya hay Focus/Potenciar en cola, lo informa
# ✔ FIX: no usa S.get_real_cost (usa get_real_cost global)
# ✔ FIX: no mezcla tech_id/None con label (canal uniforme por tech_key)
# ✔ NUEVO: tooltip muestra BASE → FINAL y si está afectada por Focus/Potenciar
# ✔ SAFE: no crashea si falta reiatsu_energy_base / get_tech_id / selector_find_focus_target_index
# ============================================================

default selector_compact = False
default bs_saga_text_tech_ui = True

# ------------------------------------------------------------
# UTIL
# ------------------------------------------------------------
init python:
    import renpy.store as S

    def _tech_icon_with_fallback(*candidates):
        _renpy_api = getattr(S, "renpy", None)
        _loadable = getattr(_renpy_api, "loadable", None)
        for p in (candidates or []):
            try:
                if p and callable(_loadable) and _loadable(p):
                    return p
            except:
                pass
        return "gui/tech_buttons/concentrar_x2.png"

    # ÍCONOS para cada técnica
    TECH_ICON = {
        "extra_attack":         "gui/tech_buttons/atk_extra.png",
        "extra_tech":           "gui/tech_buttons/tec_extra.png",
        "attack_reducer":       "gui/tech_buttons/atk_reductor.png",
        "direct_attack":        "gui/tech_buttons/atk_directo.png",
        "noatk_attack":         "gui/tech_buttons/atk_negador.png",
        "stronger_attack":      "gui/tech_buttons/atk_fuerte.png",
        "ladron_ofensivo":      "gui/tech_buttons/ladron_ofensivo.png",
        "ladron_defensivo":     "gui/tech_buttons/ladron_defensivo.png",
        "ladron_concentrar":    "gui/tech_buttons/ladron_concentrar.png",

        "defense_extra":        "gui/tech_buttons/def_extra.png",
        "defense_reducer":      "gui/tech_buttons/def_reductora.png",
        "defense_reflect":      "gui/tech_buttons/def_reflectora.png",
        "defense_strong_block": "gui/tech_buttons/def_fuerte.png",
        "salvaguarda_principiante": "gui/tech_buttons/salvaguarda_principiante.png",

        "focus_attack":         "gui/tech_buttons/concentrar_x2.png",
        "focus_defense":        "gui/tech_buttons/potenciar_x2.png",
        "fury_attack":          _tech_icon_with_fallback(
                                    "gui/tech_buttons/dados_furia.png",
                                    "gui/tech_buttons/dados_furia.webp",
                                    "gui/tech_buttons/dados_furia.jpg",
                                    "gui/tech_buttons/dados_furia",
                                    "gui/tech_buttons/concentrar_x2.png"
                                ),
        "rest_recovery":        "gui/tech_buttons/desc.png",
    }

    # Etiquetas visibles (lo que viaja a la cola del selector)
    TECH_LABEL = {
        "extra_attack": "Ataque Extra",
        "extra_tech": "Técnica Extra",
        "attack_reducer": "Ataque Reductor",
        "direct_attack": "Ataque Directo",
        "noatk_attack": "Ataque Negador",
        "stronger_attack": "Ataque básico",
        "ladron_ofensivo": "Ladrón ofensivo",
        "ladron_defensivo": "Ladrón defensivo",
        "ladron_concentrar": "Ladrón de concentrar",

        "defense_extra": "Defensa Extra",
        "defense_reducer": "Defensa Reductora",
        "defense_reflect": "Defensa Reflectora",
        "defense_strong_block": "Defensa Básica",
        "salvaguarda_principiante": "Salvaguarda principiante",

        "focus_attack": "Concentrar x2",
        "focus_defense": "Potenciar",
        "fury_attack": "Dados de furia",
        "rest_recovery": "Descansar",
    }

    # Keys que NO son técnicas reales (son "special buttons")
    _SPECIAL_ZERO_COST_KEYS = ("focus_attack", "focus_defense", "rest_recovery", "fury_attack")

    # ------------------------------------------------------------
    # Gating por tier del héroe (capa mínima sin romper lógica base)
    # ------------------------------------------------------------
    _TIER_TECH_KEYS = {
        "C": set(["stronger_attack", "defense_strong_block", "direct_attack", "focus_attack", "focus_defense", "rest_recovery", "fury_attack"]),
        "B": set(["extra_attack", "defense_extra", "focus_attack", "focus_defense", "rest_recovery", "fury_attack"]),
        "A": set(["extra_tech", "attack_reducer", "defense_reducer", "focus_attack", "focus_defense", "rest_recovery", "fury_attack"]),
        "S": set(["noatk_attack", "defense_reflect", "focus_attack", "focus_defense", "rest_recovery", "fury_attack"]),
    }

    def _selector_player_tier():
        try:
            hid = str(getattr(S, "battle_player_id", "") or "").strip()
        except:
            hid = ""
        if not hid:
            return "C"
        try:
            fn_tier = getattr(S, "bs_saga_hero_tier", None)
            if callable(fn_tier):
                return str(fn_tier(hid, "C") or "C").upper()
        except:
            pass
        return "C"

    def selector_filter_tech_keys_by_player_tier(keys):
        try:
            seq = list(keys or [])
        except:
            seq = []
        if not seq:
            return []

        # 1) Perfil preparado (preconfig) si existe
        try:
            fn_allowed = getattr(S, "bs_saga_allowed_tech_ids_for_combat", None)
            hid = str(getattr(S, "battle_player_id", "") or "").strip()
            if callable(fn_allowed):
                arr = list(fn_allowed(hid) or [])
                prof_allowed = set([str(x or "").strip().lower() for x in arr if str(x or "").strip()])
                if len(prof_allowed) > 0:
                    # Normalizar ids de perfil -> keys del selector.
                    # Ej.: focus -> focus_attack, fury_dice -> fury_attack.
                    selector_allowed = set()
                    for tid in prof_allowed:
                        selector_allowed.add(tid)
                        if tid == "focus":
                            selector_allowed.add("focus_attack")
                        elif tid == "defense_boost":
                            selector_allowed.add("focus_defense")
                        elif tid == "fury_dice":
                            selector_allowed.add("fury_attack")
                        elif tid == "rest_recovery":
                            selector_allowed.add("rest_recovery")

                    # Mantener especiales de tier en preconfig para no ocultarlos
                    # por diferencias de naming entre capas.
                    t = _selector_player_tier()
                    tier_keys = _TIER_TECH_KEYS.get(t, set())
                    for sk in ("focus_attack", "focus_defense", "fury_attack", "rest_recovery"):
                        if sk in tier_keys:
                            selector_allowed.add(sk)

                    out_prof = [k for k in seq if str(k or "").strip().lower() in selector_allowed]
                    if len(out_prof) > 0:
                        return out_prof
        except:
            pass

        # 2) Fallback por tier (regla base)
        t = _selector_player_tier()
        allowed = _TIER_TECH_KEYS.get(t, None)
        if not isinstance(allowed, set) or (len(allowed) == 0):
            return seq

        out = [k for k in seq if k in allowed]
        return out if out else seq


    # ============================================================
    # CHEQUEO DE COSTOS REALES usando el sistema 04X dinámico
    # tech_key = key del menú (extra_attack / focus_attack / etc.)
    # ============================================================
    def tech_cost_check(tech_key):

        # Focus/Potenciar/Descansar → siempre seleccionable por recursos
        if (tech_key is None) or (tech_key in ("focus_attack", "focus_defense", "rest_recovery")):
            return True, 0, 0

        if tech_key == "fury_attack":
            try:
                _fn_can = getattr(S, "can_use_fury_dice", None)
                can_now = bool(_fn_can("player")) if callable(_fn_can) else False
            except:
                can_now = False
            if not can_now:
                return False, 0, 0

            try:
                _fn_cost = getattr(S, "fury_activation_costs", None)
                _ci = _fn_cost("player") if callable(_fn_cost) else {}
            except:
                _ci = {}
            _need_r = int((_ci or {}).get("reiatsu_need", 0) or 0)
            _need_e = int((_ci or {}).get("energy_need", 0) or 0)
            _cur_r = int((_ci or {}).get("reiatsu_current", 0) or 0)
            _cur_e = int((_ci or {}).get("energy_current", 0) or 0)
            _fr = max(0, _need_r - _cur_r)
            _fe = max(0, _need_e - _cur_e)
            return (_fr == 0 and _fe == 0), _fr, _fe

        # Label visible → get_real_cost trabaja por NOMBRE
        name = TECH_LABEL.get(tech_key, None)
        if not name:
            return False, 999999, 999999

        # get_real_cost vive en 04F_SELECTOR_FUNCTIONS (o patch init que pegaste)
        rei, ene, val = get_real_cost(name)

        falta_r = max(0, rei - S.simulated_reiatsu)
        falta_e = max(0, ene - S.simulated_energy)

        ok = (falta_r == 0 and falta_e == 0)
        return ok, falta_r, falta_e


    # ============================================================
    # 🔎 Helper: detectar si ya hay Focus/Potenciar en cola
    # ============================================================
    def _queue_has_focus(mode):
        try:
            q = list(S.player_action_queue)
        except:
            q = []

        if mode == "offensive":
            return ("Concentrar x2" in q) or ("Concentrar" in q)
        else:
            return ("Potenciar" in q)


    def _queue_focus_target(mode):
        """
        Devuelve el nombre visible de la primera técnica afectada
        por Focus/Potenciar según el ORDEN EN LA COLA.
        Si existe selector_find_focus_target_index(q, mode) se usa.
        Si no existe, fallback seguro.
        """
        try:
            q = list(S.player_action_queue)
        except:
            q = []

        # Preferido: tu función del 04F_SELECTOR_QUEUE.rpy
        try:
            idx = selector_find_focus_target_index(q, mode)
            if idx is None:
                return None
            return q[idx]
        except:
            pass

        # Fallback: primera ofensiva/defensiva después del focus
        focus_name = "Concentrar x2" if mode == "offensive" else "Potenciar"
        try:
            if focus_name not in q:
                return None
            start = q.index(focus_name) + 1
        except:
            return None

        for nm in q[start:]:
            try:
                tid = get_tech_id(nm)  # definido en 04F_SELECTOR_FUNCTIONS
            except:
                tid = None

            if tid is None:
                continue

            try:
                t = S.battle_techniques.get(tid, {}).get("type", "")
            except:
                t = ""

            if mode == "offensive" and t == "offensive":
                return nm
            if mode == "defensive" and t == "defensive":
                return nm

        return None


    # ============================================================
    # Tooltip REAL (Daño/Bloqueo FINAL + costos reales)
    # tech_key = key del menú
    # ============================================================
    def tech_preview(tech_key, mode):

        # ---------------------------
        # FOCUS / POTENCIAR
        # ---------------------------
        if tech_key in _SPECIAL_ZERO_COST_KEYS:
            if tech_key == "rest_recovery":
                return (
                    "Descansar\n"
                    "Recupera 5% de HP base, 25% de EP y 25% de EC base.\n"
                    "Consume 1 acción del turno actual.\n"
                    "No inflige daño ni bloquea."
                )

            if tech_key == "fury_attack":
                txt = (
                    "Dados de furia (x1/x2/x3)\n"
                    "Técnica especial implícita tipo Concentrar.\n"
                    "Al resolverse, tira 5 dados:\n"
                    "- 5 éxitos: x3\n"
                    "- 3-4 éxitos: x2\n"
                    "- 0-2 éxitos: x1\n"
                    "Requiere HP ≤ 25% (o ítem).\n"
                    "Consume 10% del EP/EC TOTAL."
                )
                try:
                    _fn_cost = getattr(S, "fury_activation_costs", None)
                    _ci = _fn_cost("player") if callable(_fn_cost) else {}
                except:
                    _ci = {}
                txt += "\nCosto actual: R {} / E {}".format(
                    int((_ci or {}).get("reiatsu_need", 0) or 0),
                    int((_ci or {}).get("energy_need", 0) or 0),
                )
                try:
                    _fn_can = getattr(S, "can_use_fury_dice", None)
                    _can_now = bool(_fn_can("player")) if callable(_fn_can) else False
                except:
                    _can_now = False
                if not _can_now:
                    txt += "\n\n⚠ No disponible aún: requiere HP ≤ 25%."
                return txt

            already = _queue_has_focus(mode)
            target  = _queue_focus_target(mode)

            if mode == "offensive":
                txt = (
                    "Concentrar (×2)\n"
                    "Aplica ×2 al DAÑO y al costo de REIATSU\n"
                    "de la PRIMERA técnica ofensiva siguiente en la cola.\n"
                    "La ENERGÍA no se duplica.\n"
                    "Costo: 0"
                )
            else:
                txt = (
                    "Potenciar (×2)\n"
                    "Aplica ×2 al BLOQUEO y al costo de REIATSU\n"
                    "de la PRIMERA defensa siguiente en la cola.\n"
                    "La ENERGÍA no se duplica.\n"
                    "Costo: 0"
                )

            if target:
                txt += "\n\n🎯 Afectará a: {}".format(target)
            else:
                txt += "\n\n🎯 Afectará a: (ninguna aún)"

            if already:
                txt += "\n\n⚠ Ya hay uno en la cola."

            return txt


        # ---------------------------
        # Técnicas REALES
        # ---------------------------
        name = TECH_LABEL.get(tech_key, tech_key)

        # Base value (SAFE)
        base_val = 0
        try:
            base_info = S.reiatsu_energy_base(tech_key)
            base_val  = int(base_info.get("value", 0) or 0)
        except:
            base_val = 0

        # Costos + final (SAFE) usando get_real_cost (global)
        rei, ene, final_val = get_real_cost(name)

        tipo = "Daño" if mode == "offensive" else "Bloqueo"
        ok, fr, fe = tech_cost_check(tech_key)

        # ¿Es el objetivo actual de Focus/Potenciar en la cola?
        focus_note = ""
        try:
            target = _queue_focus_target(mode)
            if target and target == name:
                if mode == "offensive":
                    focus_note = "\n\n✨ ×2 por Concentrar (daño/bloqueo)"
                else:
                    focus_note = "\n\n✨ ×2 por Potenciar (daño/bloqueo)"
        except:
            pass

        txt = (
            "{} base: {}\n"
            "{} final real: {}\n"
            "Costo EP real: {}\n"
            "Costo EC real: {}"
        ).format(
            tipo,
            S.battle_fmt_num(base_val),
            tipo,
            S.battle_fmt_num(final_val),
            S.battle_fmt_num(rei),
            S.battle_fmt_num(ene)
        )

        # Mostrar base -> final cuando cambia (más claro visualmente)
        try:
            if int(final_val) != int(base_val) and base_val > 0:
                txt += "\n\n{}: {} → {}".format(
                    tipo,
                    S.battle_fmt_num(base_val),
                    S.battle_fmt_num(final_val)
                )
        except:
            pass

        if focus_note:
            txt += focus_note

        if not ok:
            txt += "\n\n❌ Recursos insuficientes:"
            if fr > 0:
                txt += "\n - Faltan {} EP".format(fr)
            if fe > 0:
                txt += "\n - Faltan {} EC".format(fe)

        return txt

    def tech_chip_caption(tech_key, mode):
        """
        Texto corto para botones tipo tarjeta (sin iconos pesados).
        """
        name = TECH_LABEL.get(tech_key, str(tech_key or ""))
        try:
            ok, _, _ = tech_cost_check(tech_key)
        except:
            ok = False

        if tech_key in _SPECIAL_ZERO_COST_KEYS:
            if tech_key == "rest_recovery":
                return "{} · Acción".format(name)
            return "{} · Gratis".format(name)

        try:
            rei, ene, _ = get_real_cost(name)
        except:
            rei, ene = 0, 0

        status = "OK" if ok else "Sin recursos"
        return "{} · R{} E{} · {}".format(name, int(rei or 0), int(ene or 0), status)


    # ============================================================
    # Wrapper para añadir técnica correctamente
    # label = nombre visible ("Ataque Extra", "Potenciar", etc.)
    # tech_key = key del menú
    # ============================================================
    def add_technique_safe(label, tech_key):

        # Focus/Potenciar: se agregan por label, sin costo
        if tech_key in ("focus_attack", "focus_defense", "rest_recovery"):
            add_technique_to_queue(label)
            return

        ok, fr, fe = tech_cost_check(tech_key)

        if ok:
            add_technique_to_queue(label)
            return

        msg = S.fmt_pink("No puedes seleccionar {}: ".format(label))
        if fr > 0:
            msg += S.fmt_white("Falta EP. ")
        if fe > 0:
            msg += S.fmt_white("Falta EC.")

        S.battle_log_add(msg)


# ------------------------------------------------------------
# MENÚ PRINCIPAL
# ------------------------------------------------------------
screen battle_item_use_panel():
    zorder 80
    modal True

    add Solid("#00000088")
    frame:
        align (0.5, 0.5)
        xsize 760
        ysize 520
        padding (16, 16)
        background Solid("#101722EE")
        vbox:
            spacing 10
            hbox:
                xfill True
                text "Usar objeto" size 28 color "#EAF6FF"
                textbutton "Cerrar":
                    xalign 1.0
                    action SetVariable("bs_battle_item_panel_open", False)
            text ("Turno: " + str(getattr(store, "battle_mode", "offensive")) + " · Acciones: " + str(int(getattr(store, "actions_available", 0) or 0))) size 15 color "#9FC4E2"
            hbox:
                spacing 8
                textbutton "Pociones":
                    action SetVariable("bs_battle_item_tab", "potions")
                textbutton "Amuleto":
                    action SetVariable("bs_battle_item_tab", "amulet")
                textbutton "Sellos":
                    action SetVariable("bs_battle_item_tab", "seals")

            $ _tab = str(getattr(store, "bs_battle_item_tab", "potions") or "potions")
            $ _entries = bs_battle_item_runtime_entries(_tab)
            frame:
                xfill True
                yfill True
                background Solid("#17283A")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 380
                    vbox:
                        spacing 8
                        if _entries:
                            for row in _entries:
                                $ _iid = str(row.get("item_id", ""))
                                $ _name = str(row.get("name", _iid) or _iid)
                                $ _meta = str(row.get("meta", "") or "")
                                $ _avail = int(row.get("available", 0) or 0)
                                frame:
                                    xfill True
                                    background Solid("#20384F")
                                    padding (8, 8)
                                    hbox:
                                        spacing 10
                                        vbox:
                                            xmaximum 500
                                            text (_name + " x" + str(_avail)) size 18 color ("#EAF6FF" if _avail > 0 else "#8F8F8F")
                                            text _meta size 13 color "#9FC4E2"
                                        if _tab == "potions":
                                            textbutton "Usar":
                                                sensitive (_avail > 0)
                                                action Function(bs_battle_use_item, _iid)
                                        else:
                                            text "Efecto pendiente" size 14 color "#FFD166" yalign 0.5
                        else:
                            text "No hay objetos preparados en esta categoria." size 17 color "#9FB9D1"

screen battle_command_menu():
    tag battlecommand
    zorder 50
    modal False

    key "ctrl_K_o" action ToggleField(store, "ui_show_offensive_techniques")
    key "ctrl_K_d" action ToggleField(store, "ui_show_defensive_techniques")

    $ OFF = [
        "extra_attack",
        "extra_tech",
        "attack_reducer",
        "direct_attack",
        "noatk_attack",
        "stronger_attack",
        "ladron_ofensivo",
        "ladron_defensivo",
        "ladron_concentrar",
        "focus_attack",
        "rest_recovery",
        "fury_attack",
    ]

    $ DEF = [
        "extra_tech",
        "defense_extra",
        "defense_reducer",
        "defense_reflect",
        "defense_strong_block",
        "salvaguarda_principiante",
        "focus_defense",
        "fury_attack",
        "rest_recovery",
    ]

    if getattr(store, "story_mode_active", False):
        $ _allowed_off = list(getattr(store, "story_pilot_allowed_offensive", []) or [])
        $ _allowed_def = list(getattr(store, "story_pilot_allowed_defensive", []) or [])
        if not _allowed_off:
            $ _allowed_off = ["stronger_attack", "direct_attack"]
        if not _allowed_def:
            $ _allowed_def = ["defense_strong_block"]
        if _allowed_off:
            $ OFF = [k for k in OFF if (k in _allowed_off) or (k == "rest_recovery") or (k == "fury_attack")]
        if _allowed_def:
            $ DEF = [k for k in DEF if (k in _allowed_def) or (k == "rest_recovery") or (k == "fury_attack")]

    $ _show_off = bool(getattr(store, "ui_show_offensive_techniques", True))
    $ _show_def = bool(getattr(store, "ui_show_defensive_techniques", True))
    $ _show_off_col = _show_off and (battle_mode == "offensive")
    $ _show_def_col = _show_def and (battle_mode == "defensive")
    $ current = OFF if battle_mode == "offensive" else DEF
    $ current = selector_filter_tech_keys_by_player_tier(current)
    $ current = current if ((battle_mode == "offensive" and _show_off) or (battle_mode == "defensive" and _show_def)) else []
    $ _off_cancel = bool(getattr(store, "offense_cancelled", False))
    $ _only_defense = _off_cancel and battle_mode == "offensive"
    $ _item_potions = bs_battle_item_runtime_entries("potions")
    $ _item_count = sum([int(r.get("available", 0) or 0) for r in _item_potions])

    if bool(getattr(store, "bs_battle_item_panel_open", False)):
        use battle_item_use_panel()

    # ============================================================
    # VISTA COMPACTA
    # ============================================================
    if selector_compact:

        frame:
            background "#0003"
            align (0.50, 0.65)
            padding (10, 10)

            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                ymaximum 350

                vbox spacing 10 at tech_btn_scale:

                    textbutton ("Usar objeto (" + str(_item_count) + ")"):
                        xminimum 585
                        yminimum 70
                        text_size 28
                        text_color "#EAF4FF"
                        background "#20384FE0"
                        hover_background "#2A5D83EE"
                        action SetVariable("bs_battle_item_panel_open", True)

                    for tech_key in current:

                        $ label = TECH_LABEL[tech_key]
                        $ tip   = tech_preview(tech_key, battle_mode)
                        $ ok, fr, fe = tech_cost_check(tech_key)
                        $ locked = bool(_only_defense)
                        $ can_use = bool(ok and not locked)
                        $ tooltip_text = tip + "\n\nTurno ofensivo cancelado: solo Defensa." if locked else tip
                        $ _chip_text = tech_chip_caption(tech_key, battle_mode)

                        textbutton _chip_text:
                            xminimum 585
                            yminimum 98
                            text_size 31
                            text_color ("#EAF4FF" if can_use else "#999999")
                            left_padding 18
                            right_padding 18
                            top_padding 10
                            bottom_padding 10
                            background ("#1A3149E0" if can_use else "#1A1A1A99")
                            hover_background ("#2A4F73EE" if can_use else "#1A1A1A99")
                            action (Function(add_technique_safe, label, tech_key) if can_use else NullAction())
                            tooltip tooltip_text


    # ============================================================
    # VISTA EXPANDIDA
    # ============================================================
    else:
        $ _tech_zoom = BTN_ZOOM if isinstance(BTN_ZOOM, (int, float)) and BTN_ZOOM > 0 else 1.0
        $ _low_spec = bool(getattr(store, "bs_battle_low_spec_mode", False))
        $ _off_src = selector_filter_tech_keys_by_player_tier(OFF)
        $ _def_src = selector_filter_tech_keys_by_player_tier(DEF)
        $ _off_rows = list(_off_src[:12]) if _low_spec else list(_off_src)
        $ _def_rows = list(_def_src[:12]) if _low_spec else list(_def_src)
        $ _btn_h = 72 if _low_spec else 95
        $ _btn_text_size = 23 if _low_spec else 30
        $ _tech_row_height = max(1, int((_btn_h + 6) * _tech_zoom))
        $ _tech_viewport_height = 380
        $ _visible_tech_rows = max(1, _tech_viewport_height // _tech_row_height)
        $ _off_need_scroll = len(_off_rows) > _visible_tech_rows
        $ _def_need_scroll = len(_def_rows) > _visible_tech_rows

        frame:
            background "#0000"
            align (0.03, 0.60)

            vbox spacing 6:
                if _low_spec:
                    text "Low-spec: lista recortada para estabilidad (12 por columna)." size 14 color "#FFD166"

                hbox:
                    spacing 14

                    if _show_off_col:
                        frame:
                            background "#0000"
                            padding (8, 8)
                            xmaximum 510
                            xminimum 510
                            ymaximum 430

                            vbox:
                                spacing 6
                                text "OFENSIVAS" size 28 color ("#66CCFF" if battle_mode == "offensive" else "#8A8A8A")
                                textbutton ("Usar objeto (" + str(_item_count) + ")"):
                                    xminimum 492
                                    yminimum 50
                                    text_size 21
                                    text_color "#EAF4FF"
                                    background "#20384FE0"
                                    hover_background "#2A5D83EE"
                                    action SetVariable("bs_battle_item_panel_open", True)
                                viewport:
                                    draggable True
                                    mousewheel True
                                    scrollbars ("vertical" if _off_need_scroll else None)
                                    ymaximum _tech_viewport_height

                                    vbox spacing 6 at tech_btn_scale:
                                        for tech_key in _off_rows:
                                            $ label = TECH_LABEL[tech_key]
                                            $ tip   = tech_preview(tech_key, "offensive")
                                            $ ok, fr, fe = tech_cost_check(tech_key)
                                            $ locked = bool(_only_defense) or (battle_mode != "offensive")
                                            $ can_use = bool(ok and not locked)
                                            $ tooltip_text = tip + "\n\nTurno actual: usa ofensivas para seleccionar." if (battle_mode != "offensive") else (tip + "\n\nTurno ofensivo cancelado: solo Defensa." if _only_defense else tip)
                                            $ _chip_text = tech_chip_caption(tech_key, "offensive")
                                            textbutton _chip_text:
                                                xminimum 492
                                                yminimum _btn_h
                                                text_size _btn_text_size
                                                text_color ("#DFF2FF" if can_use else "#8F8F8F")
                                                left_padding 16
                                                right_padding 16
                                                top_padding 10
                                                bottom_padding 10
                                                background ("#173752E0" if can_use else "#1B1B1B99")
                                                hover_background ("#2A5D83EE" if can_use else "#1B1B1B99")
                                                action (Function(add_technique_safe, label, tech_key) if can_use else NullAction())
                                                tooltip tooltip_text

                    if _show_def_col:
                        frame:
                            background "#0000"
                            padding (8, 8)
                            xmaximum 510
                            xminimum 510
                            ymaximum 430

                            vbox:
                                spacing 6
                                text "DEFENSIVAS" size 28 color ("#FFAAAA" if battle_mode == "defensive" else "#8A8A8A")
                                textbutton ("Usar objeto (" + str(_item_count) + ")"):
                                    xminimum 492
                                    yminimum 50
                                    text_size 21
                                    text_color "#FFEAEA"
                                    background "#4A2525E0"
                                    hover_background "#7A3C3CEE"
                                    action SetVariable("bs_battle_item_panel_open", True)
                                viewport:
                                    draggable True
                                    mousewheel True
                                    scrollbars ("vertical" if _def_need_scroll else None)
                                    ymaximum _tech_viewport_height

                                    vbox spacing 6 at tech_btn_scale:
                                        for tech_key in _def_rows:
                                            $ label = TECH_LABEL[tech_key]
                                            $ tip   = tech_preview(tech_key, "defensive")
                                            $ ok, fr, fe = tech_cost_check(tech_key)
                                            $ locked = bool(battle_mode != "defensive")
                                            $ can_use = bool(ok and not locked)
                                            $ tooltip_text = tip + "\n\nTurno actual: usa defensivas para seleccionar." if locked else tip
                                            $ _chip_text = tech_chip_caption(tech_key, "defensive")
                                            textbutton _chip_text:
                                                xminimum 492
                                                yminimum _btn_h
                                                text_size _btn_text_size
                                                text_color ("#FFEAEA" if can_use else "#8F8F8F")
                                                left_padding 16
                                                right_padding 16
                                                top_padding 10
                                                bottom_padding 10
                                                background ("#4A2525E0" if can_use else "#1B1B1B99")
                                                hover_background ("#7A3C3CEE" if can_use else "#1B1B1B99")
                                                action (Function(add_technique_safe, label, tech_key) if can_use else NullAction())
                                                tooltip tooltip_text
