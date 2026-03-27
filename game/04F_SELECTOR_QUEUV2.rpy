# ============================================================
# 04F_SELECTOR_QUEUE.rpy – Cola de Técnicas (Modern v4.2 FIXED)
# Soporta Focus/Potenciar según posición en la cola
# ------------------------------------------------------------
# ✔ Muestra correctamente el x2 en daño/bloqueo y Reiatsu
#   para la PRIMERA técnica afectada por Concentrar/Potenciar
# ✔ Energía NO se duplica
# ✔ No modifica la lógica interna del turno, solo la vista
# ✔ Toggle panel con tecla Ctrl+U (no modal, no bloquea otros paneles)
# ✔ FIX: key "K_u" (Ren'Py no entiende "toggle_technique_selector" como tecla)
# ✔ FIX: preview usa get_real_cost() (coherente con selector_functions)
# ============================================================


# ------------------------------------------------------------
# 🔑 Toggle del panel (tecla Ctrl+U)
# ------------------------------------------------------------
init -990 python:
    import renpy.store as S
    import renpy.exports as R

    # (Opcional) también queda en keymap por si luego querés bindearlo global
    config.keymap["toggle_technique_selector"] = ["ctrl_K_u"]

    def toggle_technique_selector():
        S.show_technique_selector = not getattr(S, "show_technique_selector", True)
        R.restart_interaction()


init python:
    import renpy.store as S
    import renpy.store as store

    # --------------------------------------------------------
    # Mapa global Visual → TECH_ID (04X)
    # --------------------------------------------------------
    TECH_MAP_GLOBAL = {
        "Ataque Extra":        "extra_attack",
        "Técnica Extra":       "extra_tech",
        "Ataque Reductor":     "attack_reducer",
        "Ataque Directo":      "direct_attack",
        "Ataque Negador":      "noatk_attack",
        "Ataque más fuerte":   "stronger_attack",
        "Ladrón ofensivo":     "ladron_ofensivo",
        "Ladrón defensivo":    "ladron_defensivo",
        "Ladrón de concentrar": "ladron_concentrar",

        "Defensa Extra":       "defense_extra",
        "Defensa Reductora":   "defense_reducer",
        "Defensa Reflectora":  "defense_reflect",
        "Defensa Fuerte":      "defense_strong_block",
        "Salvaguarda principiante": "salvaguarda_principiante",

        # especiales (no consumen recursos directos)
        "Concentrar":          "focus",
        "Concentrar x2":       "focus",
        "Dados de furia":      "fury_dice",
        "Potenciar":           "defense_boost",
        "Descansar":           "rest_recovery",
    }

    # --------------------------------------------------------
    # UTIL: efecto textual
    # --------------------------------------------------------
    def selector_get_effect(name, tech_id):
        # Focus/Potenciar
        if name in ("Concentrar", "Concentrar x2", "Potenciar"):
            return "x2"
        if name == "Dados de furia":
            return "x1/x2/x3"
        if name == "Descansar":
            return "+25% R/E"

        if not tech_id:
            return "—"

        tech = store.battle_techniques.get(tech_id, {})

        if tech.get("bonus_actions", 0) > 0:
            return "+1 Acción"
        if tech.get("attack_reduction", 0) > 0:
            return "-{}% Atk".format(int(tech["attack_reduction"] * 100))
        if tech.get("attack_reflect", 0) > 0:
            return "Reflect {}%".format(int(tech["attack_reflect"] * 100))

        return "—"

    def selector_find_next_offensive_index(queue, start_idx):
        for j in range(int(start_idx) + 1, len(queue)):
            nm = str(queue[j] or "")
            tid = TECH_MAP_GLOBAL.get(nm)
            if not tid:
                continue
            t = store.battle_techniques.get(tid, {}).get("type", "")
            if t == "offensive":
                return j
        return None


    # --------------------------------------------------------
    # UTIL: ¿qué técnica será afectada por Focus/Boost?
    # --------------------------------------------------------
    def selector_find_focus_target_index(queue, mode):
        """
        Devuelve el índice de la PRIMERA técnica que será afectada por:
        - Concentrar / Concentrar x2 (modo ofensivo)
        - Potenciar (modo defensivo)

        Si no hay ninguna, devuelve None.
        """
        focus_seen = False
        boost_seen = False

        for i, name in enumerate(queue):

            # -------------------------------
            # MODO OFENSIVO → CONCENTRAR
            # -------------------------------
            if mode == "offensive":
                if name in ("Concentrar", "Concentrar x2"):
                    focus_seen = True
                    continue

                if focus_seen:
                    tech_id = TECH_MAP_GLOBAL.get(name)
                    if tech_id in (
                        "extra_attack", "extra_tech",
                        "attack_reducer", "direct_attack",
                        "noatk_attack", "strong_attack",
                        "stronger_attack", "ladron_ofensivo",
                        "ladron_defensivo", "ladron_concentrar"
                    ):
                        return i

            # -------------------------------
            # MODO DEFENSIVO → POTENCIAR
            # -------------------------------
            elif mode == "defensive":
                if name == "Potenciar":
                    boost_seen = True
                    continue

                if boost_seen:
                    tech_id = TECH_MAP_GLOBAL.get(name)
                    if tech_id in (
                        "defense_extra", "defense_reducer",
                        "defense_reflect", "defense_strong_block",
                        "salvaguarda_principiante"
                    ):
                        return i

        return None


    def selector_cycle_target_key(target_team="enemy"):
        try:
            valid = list(S.bs_get_valid_target_keys(target_team) or []) if hasattr(S, "bs_get_valid_target_keys") else []
        except:
            valid = []
        if not valid:
            S.offensive_selected_target_key = ""
            return ""

        cur = str(getattr(S, "offensive_selected_target_key", "") or "")
        if cur in valid:
            i = valid.index(cur)
            nxt = valid[(i + 1) % len(valid)]
        else:
            nxt = valid[0]
        S.offensive_selected_target_key = str(nxt)
        return str(nxt)


    def selector_toggle_split_mode():
        mode = str(getattr(S, "offensive_targeting_policy", "single_target") or "single_target").strip().lower()
        if mode == "split_equal":
            mode = "single_target"
        else:
            mode = "split_equal"
        S.offensive_targeting_policy = mode
        return mode

    def selector_target_preview_text(target_team="enemy"):
        mode = str(getattr(S, "offensive_targeting_policy", "single_target") or "single_target").strip().lower()
        sel = str(getattr(S, "offensive_selected_target_key", "") or "")
        fn_desc = getattr(S, "bs_describe_unit_key", None)
        fn_valid = getattr(S, "bs_get_valid_target_keys", None)

        if mode == "split_equal":
            valid = list(fn_valid(target_team) or []) if callable(fn_valid) else []
            if not valid:
                return "AUTO"
            labels = []
            for k in valid:
                if callable(fn_desc):
                    labels.append(str(fn_desc(k, default_side=target_team, default_slot=0) or k))
                else:
                    labels.append(str(k))
            return " + ".join(labels)

        if sel:
            if callable(fn_desc):
                return str(fn_desc(sel, default_side=target_team, default_slot=0) or sel)
            return sel
        return "AUTO"


# ============================================================
# TOOLTIP MODERNO
# ============================================================
screen tech_tooltip(
    label, tipo,
    base_val, base_rei, base_ene,
    final_val, final_rei, final_ene,
    is_focus=False, warn_text=None
):

    frame:
        background "#000C"
        padding (18, 14)
        xalign 0.50
        yalign 0.40
        at tooltip_fade

        vbox spacing 6:

            text "[label]" size 24 color "#FFD700" bold True

            if is_focus:
                text "Multiplicador activo: x2" size 20 color "#7FDBFF"
                text "Sin costo de Reiatsu / Energía" size 18 color "#AAAAAA"
            else:
                text "[tipo]: [final_val]" size 20 color "#C586C0"
                text "Reiatsu: [final_rei]" size 18 color "#88CCFF"
                text "Energía: [final_ene]" size 18 color "#FF8844"


transform tooltip_fade:
    alpha 0.0
    linear 0.15 alpha 1.0


# ============================================================
# PANEL PRINCIPAL SEGMENTADO
# ============================================================
screen technique_selector():
    tag techselector
    modal False
    zorder 60

    default _target_preview = ""
    default _tech_opts_index = -1

    # Toggle con tecla Ctrl+U (no bloquea otros paneles)
    key "ctrl_K_u" action Function(toggle_technique_selector)

    default tooltip_data = None

    # Si está oculto, no dibujamos el panel (sin return).
    if show_technique_selector:

        frame:
            align (1.0, 0.55)
            anchor (1.0, 0.5)
            background "#111C"
            xmaximum 780
            ysize 520
            padding (16, 16)

            hbox:
                spacing 12
                xfill True

                # -------------------------------------------------
                # COLUMNA IZQUIERDA
                # -------------------------------------------------
                frame:
                    background "#0002"
                    padding (10, 10)
                    xfill True
                    xmaximum 540

                    vbox spacing 10:
                        $ _fn_reconcile_fury = getattr(store, "selector_reconcile_fury_selection", None)
                        if callable(_fn_reconcile_fury):
                            $ _fn_reconcile_fury()

                        $ _sim_rei = int(getattr(store, "simulated_reiatsu", getattr(store, "player_reiatsu", 0)) or 0)
                        $ _sim_ene = int(getattr(store, "simulated_energy", getattr(store, "player_energy", 0)) or 0)
                        $ _cur_rei = int(getattr(store, "player_reiatsu", 0) or 0)
                        $ _cur_ene = int(getattr(store, "player_energy", 0) or 0)
                        $ _spent_rei = max(0, _cur_rei - _sim_rei)
                        $ _spent_ene = max(0, _cur_ene - _sim_ene)

                        text "🌀 Técnicas en espera:" size 26 color "#FFFFFF" bold True
                        text "Acciones disponibles: [actions_available]" size 22 color "#FFD700"
                        text "Recursos disponibles → Reiatsu %s | Energía %s" % (_sim_rei, _sim_ene) size 18 color "#88CCFF"
                        text "Gasto proyectado → Reiatsu %s | Energía %s" % (_spent_rei, _spent_ene) size 17 color "#B8B8B8"
                        text "Espacio libre: %s" % actions_available size 17 color "#A0A0A0"
                        null height 4

                        if player_action_queue:

                            # Cálculo previo: índice afectado por Focus/Boost
                            python:
                                focus_target_index = selector_find_focus_target_index(
                                    player_action_queue,
                                    battle_mode
                                )

                            hbox spacing 20:
                                text "Técnica" size 20 color "#DDDDDD" xminimum 160
                                text "Valor" size 20 color "#DDDDDD" xminimum 70
                                text "Costos" size 20 color "#DDDDDD" xminimum 110
                                text "Efecto" size 20 color "#DDDDDD"

                            bar:
                                xmaximum 500
                                ymaximum 2
                                value 1.0 left_bar "#8888" right_bar "#0000"

                            viewport:
                                ymaximum 350
                                scrollbars "vertical"
                                mousewheel True

                                vbox spacing 12:

                                    for i, tech in enumerate(player_action_queue):

                                        python:
                                            tech_id = TECH_MAP_GLOBAL.get(tech, None)

                                            is_focus_tech = (tech in ("Concentrar", "Concentrar x2") and battle_mode == "offensive")
                                            is_boost_tech = (tech == "Potenciar" and battle_mode == "defensive")
                                            is_fury_tech = (tech == "Dados de furia" and battle_mode == "offensive")
                                            is_rest_tech = (tech == "Descansar")
                                            is_focus = is_focus_tech or is_boost_tech or is_rest_tech or is_fury_tech

                                            tipo = "Daño" if battle_mode == "offensive" else "Bloqueo"

                                            # ---------------------------
                                            # CONCENTRAR / POTENCIAR
                                            # ---------------------------
                                            if is_focus:
                                                if is_rest_tech:
                                                    base_val = "+25%"
                                                    final_val = "+25%"
                                                elif is_fury_tech:
                                                    _nxt = selector_find_next_offensive_index(player_action_queue, i)
                                                    if _nxt is not None:
                                                        _nxt_name = str(player_action_queue[_nxt] or "")
                                                        _rei_n, _ene_n, _val_n = get_real_cost(_nxt_name)
                                                        _v = int(_val_n or 0)
                                                        base_val = "x1/x2/x3"
                                                        final_val = "{} / {} / {}".format(_v, int(_v * 2), int(_v * 3))
                                                    else:
                                                        base_val = "x1/x2/x3"
                                                        final_val = "— / — / —"
                                                else:
                                                    base_val  = "x2"
                                                    final_val = "x2"
                                                base_rei  = 0
                                                base_ene  = 0
                                                final_rei = 0
                                                final_ene = 0

                                            # ---------------------------
                                            # Técnicas normales (vista coherente con costos reales del selector)
                                            # ---------------------------
                                            else:
                                                affected = (focus_target_index == i)
                                                mult = 2 if affected else 1

                                                if tech_id:
                                                    # Base "pura" (solo para mostrar base_val)
                                                    base = store.reiatsu_energy_base(tech_id)
                                                    base_val = int(base.get("value", 0))

                                                    # Costos/valor FINAL REAL (sin focus de cola)
                                                    # get_real_cost vive en 04F_SELECTOR_FUNCTIONS y recibe NOMBRE
                                                    rei0, ene0, val0 = get_real_cost(tech)

                                                    final_val = int(val0) * mult
                                                    final_rei = int(rei0) * mult
                                                    final_ene = int(ene0)          # Energía NO se duplica

                                                    # Para tooltip: mostramos "base" como base_val y los costos base como finales sin focus.
                                                    # (Si querés base_rei/base_ene reales del dataset viejo, podés reemplazar estas 2 líneas.)
                                                    base_rei = int(rei0)
                                                    base_ene = int(ene0)

                                                else:
                                                    base_val  = 0
                                                    base_rei  = 0
                                                    base_ene  = 0
                                                    final_val = 0
                                                    final_rei = 0
                                                    final_ene = 0

                                            effect_txt = selector_get_effect(tech, tech_id)
                                            label_txt = "{}. {}".format(i + 1, tech)

                                        # ----------------
                                        # FILA TÉCNICA
                                        # ----------------
                                        button:
                                            background None
                                            padding (0, 0)

                                            hovered SetScreenVariable(
                                                "tooltip_data",
                                                (tech, tipo,
                                                 str(base_val), str(base_rei), str(base_ene),
                                                 str(final_val), str(final_rei), str(final_ene),
                                                 is_focus, None)
                                            )
                                            unhovered SetScreenVariable("tooltip_data", None)

                                            hbox spacing 18:
                                                $ _fs = getattr(store, "fury_selection", {}) if isinstance(getattr(store, "fury_selection", {}), dict) else {}
                                                $ _fidx_current = int(_fs.get("queue_index", getattr(store, "fury_selected_queue_index", -1)) or -1)
                                                $ _farmed_current = bool(_fs.get("armed", (_fidx_current >= 0)))
                                                $ _is_fury_selected = (_farmed_current and _fidx_current == i)
                                                $ _fn_can_fury = getattr(store, "can_use_fury_dice", None)
                                                $ _fury_can_now = bool(_fn_can_fury("player")) if callable(_fn_can_fury) else False
                                                text label_txt size 20 color "#40BFFF" xminimum 160
                                                text str(final_val) size 20 color "#FFDADA" xminimum 70
                                                text "{} / {}".format(final_rei, final_ene) size 18 color "#CCCCCC" xminimum 110
                                                text effect_txt size 18 color "#AAAAFF"

                                                textbutton "✖":
                                                    text_size 18
                                                    xminimum 24
                                                    action Function(remove_technique_from_queue, i)

                                                if battle_mode == "offensive" and (not is_focus):
                                                    textbutton "⚙ Opciones":
                                                        text_size 16
                                                        action SetScreenVariable("_tech_opts_index", (-1 if _tech_opts_index == i else i))

                                        if _is_fury_selected and battle_mode == "offensive" and (not is_focus):
                                            frame:
                                                background "#FF6A0030"
                                                padding (8, 4)
                                                xmaximum 240
                                                text "🔥 Dados de furia cargados" size 14 color "#FFC080"
                                            if not _fury_can_now:
                                                text "Se ejecuta cuando HP ≤ 25% o con ítem." size 12 color "#BBBBBB"

                                        if _tech_opts_index == i and battle_mode == "offensive" and (not is_focus):
                                            frame:
                                                background "#11223388"
                                                padding (8, 6)
                                                xfill True
                                                hbox:
                                                    spacing 8
                                                    text "Opciones (placeholder)" size 14 color "#AABBDD"

                        else:
                            text "Ninguna técnica seleccionada." size 20 color "#AAAAAA"

                # -------------------------------------------------
                # COLUMNA DERECHA
                # -------------------------------------------------
                frame:
                    background "#0004"
                    padding (14, 12)
                    xmaximum 220

                    vbox spacing 14:
                        if battle_mode == "offensive":
                            $ _policy = str(getattr(store, "offensive_targeting_policy", "single_target") or "single_target")
                            $ _sel = str(getattr(store, "offensive_selected_target_key", "") or "")
                            $ _sel_txt = selector_target_preview_text("enemy")
                            $ _dmg_mode_txt = "Dividir x2" if _policy == "split_equal" else "Foco único"
                            $ _fs_side = getattr(store, "fury_selection", {}) if isinstance(getattr(store, "fury_selection", {}), dict) else {}
                            $ _fury_idx_side = int(_fs_side.get("queue_index", getattr(store, "fury_selected_queue_index", -1)) or -1)
                            $ _fury_armed_side = bool(_fs_side.get("armed", (_fury_idx_side >= 0)))
                            $ _fury_name_side = str(_fs_side.get("tech_name", "") or "")
                            if (not _fury_name_side) and _fury_idx_side >= 0 and _fury_idx_side < len(player_action_queue):
                                $ _fury_name_side = player_action_queue[_fury_idx_side]
                            text "Objetivo: [_sel_txt]" size 18 color "#88DDFF"
                            text "Daño: [_dmg_mode_txt]" size 17 color "#FFDDAA"

                            if _fury_armed_side and _fury_name_side:
                                frame:
                                    background "#1E3D2A"
                                    padding (8, 6)
                                    xfill True
                                    vbox:
                                        spacing 6
                                        text "🔥 Furia cargada" size 15 color "#B9FFB9"
                                        text "[_fury_name_side]" size 14 color "#D5FFD5"
                                        $ _fn_fc = getattr(store, "fury_activation_costs", None)
                                        $ _fc = _fn_fc("player") if callable(_fn_fc) else {}
                                        text "Coste: Reiatsu [int((_fc or {}).get('reiatsu_need', 0) or 0)] | Energía [int((_fc or {}).get('energy_need', 0) or 0)]" size 12 color "#DDEECC"
                                        textbutton "✖ Cancelar furia":
                                            text_size 15
                                            action Function(toggle_fury_target_queue_index, _fury_idx_side)

                            textbutton "🎯 Seleccionar objetivo":
                                text_size 20
                                action Function(selector_cycle_target_key, "enemy")

                            textbutton "⚖ Alternar dividir x2":
                                text_size 20
                                action Function(selector_toggle_split_mode)

                            null height 72
                            textbutton "✅ Finalizar turno (objetivo listo)":
                                text_size 22
                                action Function(confirm_turn_actions)
                        else:
                            null height 72
                            textbutton "✅ Finalizar turno":
                                text_size 22
                                action Function(confirm_turn_actions)

                        textbutton "🗑 Cancelar Todo":
                            text_size 22
                            action Function(clear_action_queue)


    # =====================================================
    # Tooltip dinámico (solo si el panel está visible)
    # =====================================================
    if show_technique_selector and tooltip_data:
        use tech_tooltip(
            tooltip_data[0],
            tooltip_data[1],
            tooltip_data[2],
            tooltip_data[3],
            tooltip_data[4],
            tooltip_data[5],
            tooltip_data[6],
            tooltip_data[7],
            tooltip_data[8],
            tooltip_data[9],
        )
