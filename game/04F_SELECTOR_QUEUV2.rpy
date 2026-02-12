# ============================================================
# 04F_SELECTOR_QUEUE.rpy – Cola de Técnicas (Modern v4.2 FIXED)
# Soporta Focus/Potenciar según posición en la cola
# ------------------------------------------------------------
# ✔ Muestra correctamente el x2 en daño/bloqueo y Reiatsu
#   para la PRIMERA técnica afectada por Concentrar/Potenciar
# ✔ Energía NO se duplica
# ✔ No modifica la lógica interna del turno, solo la vista
# ✔ Toggle panel con tecla U (no modal, no bloquea otros paneles)
# ✔ FIX: key "K_u" (Ren'Py no entiende "toggle_technique_selector" como tecla)
# ✔ FIX: preview usa get_real_cost() (coherente con selector_functions)
# ============================================================


# ------------------------------------------------------------
# 🔑 Toggle del panel (tecla U)
# ------------------------------------------------------------
init -990 python:
    import renpy.store as S
    import renpy.exports as R

    # (Opcional) también queda en keymap por si luego querés bindearlo global
    config.keymap["toggle_technique_selector"] = ["K_u"]

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

        "Defensa Extra":       "defense_extra",
        "Defensa Reductora":   "defense_reducer",
        "Defensa Reflectora":  "defense_reflect",
        "Defensa Fuerte":      "defense_strong_block",

        # especiales (no consumen recursos directos)
        "Concentrar":          "focus",
        "Concentrar x2":       "focus",
        "Potenciar":           "defense_boost",
    }

    # --------------------------------------------------------
    # UTIL: efecto textual
    # --------------------------------------------------------
    def selector_get_effect(name, tech_id):
        # Focus/Potenciar
        if name in ("Concentrar", "Concentrar x2", "Potenciar"):
            return "x2"

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
                        "stronger_attack"
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
                        "defense_reflect", "defense_strong_block"
                    ):
                        return i

        return None


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

    # Toggle con tecla U (no bloquea otros paneles)
    key "K_u" action Function(toggle_technique_selector)

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

                        text "🌀 Técnicas en espera:" size 26 color "#FFFFFF" bold True
                        text "Acciones disponibles: [actions_available]" size 22 color "#FFD700"
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
                                            is_focus = is_focus_tech or is_boost_tech

                                            tipo = "Daño" if battle_mode == "offensive" else "Bloqueo"

                                            # ---------------------------
                                            # CONCENTRAR / POTENCIAR
                                            # ---------------------------
                                            if is_focus:
                                                base_val  = "x2"
                                                base_rei  = 0
                                                base_ene  = 0
                                                final_val = "x2"
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
                                                text label_txt size 20 color "#40BFFF" xminimum 160
                                                text str(final_val) size 20 color "#FFDADA" xminimum 70
                                                text "{} / {}".format(final_rei, final_ene) size 18 color "#CCCCCC" xminimum 110
                                                text effect_txt size 18 color "#AAAAFF"

                                                textbutton "✖":
                                                    text_size 18
                                                    action Function(remove_technique_from_queue, i)

                        else:
                            text "Ninguna técnica seleccionada." size 20 color "#AAAAAA"

                # -------------------------------------------------
                # COLUMNA DERECHA
                # -------------------------------------------------
                frame:
                    background "#0004"
                    padding (14, 12)
                    xmaximum 220

                    vbox spacing 20:
                        textbutton "✅ Finalizar Turno":
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
