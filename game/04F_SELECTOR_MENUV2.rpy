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

# ------------------------------------------------------------
# UTIL
# ------------------------------------------------------------
init python:
    import renpy.store as S

    # ÍCONOS para cada técnica
    TECH_ICON = {
        "extra_attack":         "gui/tech_buttons/atk_extra.png",
        "extra_tech":           "gui/tech_buttons/tec_extra.png",
        "attack_reducer":       "gui/tech_buttons/atk_reductor.png",
        "direct_attack":        "gui/tech_buttons/atk_directo.png",
        "noatk_attack":         "gui/tech_buttons/atk_negador.png",
        "stronger_attack":      "gui/tech_buttons/atk_fuerte.png",

        "defense_extra":        "gui/tech_buttons/def_extra.png",
        "defense_reducer":      "gui/tech_buttons/def_reductora.png",
        "defense_reflect":      "gui/tech_buttons/def_reflectora.png",
        "defense_strong_block": "gui/tech_buttons/def_fuerte.png",

        "focus_attack":         "gui/tech_buttons/concentrar_x2.png",
        "focus_defense":        "gui/tech_buttons/potenciar_x2.png",
    }

    # Etiquetas visibles (lo que viaja a la cola del selector)
    TECH_LABEL = {
        "extra_attack": "Ataque Extra",
        "extra_tech": "Técnica Extra",
        "attack_reducer": "Ataque Reductor",
        "direct_attack": "Ataque Directo",
        "noatk_attack": "Ataque Negador",
        "stronger_attack": "Ataque más fuerte",

        "defense_extra": "Defensa Extra",
        "defense_reducer": "Defensa Reductora",
        "defense_reflect": "Defensa Reflectora",
        "defense_strong_block": "Defensa Fuerte",

        "focus_attack": "Concentrar x2",
        "focus_defense": "Potenciar",
    }

    # Keys que NO son técnicas reales (son "special buttons")
    _FOCUS_KEYS = ("focus_attack", "focus_defense")


    # ============================================================
    # CHEQUEO DE COSTOS REALES usando el sistema 04X dinámico
    # tech_key = key del menú (extra_attack / focus_attack / etc.)
    # ============================================================
    def tech_cost_check(tech_key):

        # Focus/Potenciar → siempre seleccionable por recursos
        if (tech_key is None) or (tech_key in _FOCUS_KEYS):
            return True, 0, 0

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
        if tech_key in _FOCUS_KEYS:

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
                    focus_note = "\n\n✨ ×2 por Concentrar (Reiatsu ×2 / Energía normal)"
                else:
                    focus_note = "\n\n✨ ×2 por Potenciar (Reiatsu ×2 / Energía normal)"
        except:
            pass

        txt = (
            "{} base: {}\n"
            "{} final real: {}\n"
            "Costo Reiatsu real: {}\n"
            "Costo Energía real: {}"
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
                txt += "\n - Faltan {} Reiatsu".format(fr)
            if fe > 0:
                txt += "\n - Faltan {} Energía".format(fe)

        return txt


    # ============================================================
    # Wrapper para añadir técnica correctamente
    # label = nombre visible ("Ataque Extra", "Potenciar", etc.)
    # tech_key = key del menú
    # ============================================================
    def add_technique_safe(label, tech_key):

        # Focus/Potenciar: se agregan por label, sin costo
        if tech_key in _FOCUS_KEYS:
            add_technique_to_queue(label)
            return

        ok, fr, fe = tech_cost_check(tech_key)

        if ok:
            add_technique_to_queue(label)
            return

        msg = S.fmt_pink("No puedes seleccionar {}: ".format(label))
        if fr > 0:
            msg += S.fmt_white("Falta Reiatsu. ")
        if fe > 0:
            msg += S.fmt_white("Falta Energía.")

        S.battle_log_add(msg)


# ------------------------------------------------------------
# BOTÓN DE CAMBIO DE VISTA
# ------------------------------------------------------------
screen selector_toggle_button():
    frame:
        background "#0004"
        padding (6, 6)
        textbutton "⇆" action ToggleScreenVariable("selector_compact") text_size 28


# ------------------------------------------------------------
# MENÚ PRINCIPAL
# ------------------------------------------------------------
screen battle_command_menu():
    tag battlecommand
    zorder 50
    modal False

    use selector_toggle_button

    $ OFF = [
        "extra_attack",
        "extra_tech",
        "attack_reducer",
        "direct_attack",
        "noatk_attack",
        "stronger_attack",
        "focus_attack",
    ]

    $ DEF = [
        "defense_extra",
        "defense_reducer",
        "defense_reflect",
        "defense_strong_block",
        "focus_defense",
    ]

    $ current = OFF if battle_mode == "offensive" else DEF

    # ============================================================
    # VISTA COMPACTA
    # ============================================================
    if selector_compact:

        frame:
            background "#0003"
            align (0.50, 0.65)
            padding (10, 10)

            hbox spacing 14 at tech_btn_scale:

                for tech_key in current:

                    $ label = TECH_LABEL[tech_key]
                    $ icon  = TECH_ICON[tech_key]

                    $ tip   = tech_preview(tech_key, battle_mode)
                    $ ok, fr, fe = tech_cost_check(tech_key)

                    if ok:
                        imagebutton:
                            idle icon
                            hover icon
                            action Function(add_technique_safe, label, tech_key)
                            tooltip tip
                    else:
                        imagebutton:
                            idle Transform(icon, alpha=0.40)
                            hover Transform(icon, alpha=0.40)
                            action NullAction()
                            tooltip tip


    # ============================================================
    # VISTA EXPANDIDA
    # ============================================================
    else:

        frame:
            background "#0000"
            align (0.08, 0.55)

            vbox spacing 6 at tech_btn_scale:

                for tech_key in current:

                    $ label = TECH_LABEL[tech_key]
                    $ icon  = TECH_ICON[tech_key]

                    $ tip   = tech_preview(tech_key, battle_mode)
                    $ ok, fr, fe = tech_cost_check(tech_key)

                    if ok:
                        imagebutton:
                            idle icon
                            hover icon
                            action Function(add_technique_safe, label, tech_key)
                            tooltip tip
                    else:
                        imagebutton:
                            idle Transform(icon, alpha=0.40)
                            hover Transform(icon, alpha=0.40)
                            action NullAction()
                            tooltip tip
