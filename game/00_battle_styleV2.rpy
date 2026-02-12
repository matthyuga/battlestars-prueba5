#============================================================
#00_BATTLE_STYLE.RPY – Estilos, Formato y Logs del Sistema
#Versión v4.3 – Store-Safe + Markup-Safe + Wrapper-Aware + SafeLogHub
#------------------------------------------------------------
#- Paleta centralizada en renpy.store (S.PALETTE) + alias local
#- fmt_* completos + fmt_cyan_text FIX
#- Logs ofensivos y defensivos unificados
#- Fallback seguro para op_def_* en renpy.store
#- Fallback seguro para battle_fmt_num (renpy.store)
#- colorize_numbers / highlight_x2 markup-safe (no toca {...})
#- Late Sync de OP_COLOR_* si existe op_colors_sync()
#- battle_log_add_ex inteligente: intenta pasar border si battle_log_add lo soporta
#- ✅ NUEVO: S.safe_battle_log_add() wrapper universal (global/store + color + border)
#============================================================

init -970 python:

    import re
    import inspect
    import renpy.store as S

    ###############################################
    # 🎨 PALETA CENTRALIZADA (STORE-SAFE)
    ###############################################
    if not hasattr(S, "PALETTE") or not isinstance(getattr(S, "PALETTE", None), dict):
        S.PALETTE = {
            "white":   "#FFFFFF",
            "red":     "#FF4444",
            "blue":    "#00BFFF",
            "purple":  "#C586C0",
            "gold":    "#FFD700",
            "orange":  "#FFA500",
            "pink":    "#FF66CC",

            # Separados: effect puede cambiarse sin afectar cyan (defensivo)
            "effect":  "#55FFFF",
            "cyan":    "#55FFFF",

            "green":   "#00FF00",
            "hp_red":  "#FF6666"
        }

    PALETTE = S.PALETTE

    def fmt(color_key, t):
        return "{color=%s}%s{/color}" % (PALETTE.get(color_key, "#FFFFFF"), t)

    fmt_white   = lambda t: fmt("white", t)
    fmt_red     = lambda t: fmt("red", t)
    fmt_blue    = lambda t: fmt("blue", t)
    fmt_gold    = lambda t: fmt("gold", t)
    fmt_orange  = lambda t: fmt("orange", t)
    fmt_purple  = lambda t: fmt("purple", t)
    fmt_pink    = lambda t: fmt("pink", t)
    fmt_effect  = lambda t: fmt("effect", t)
    fmt_cyan    = lambda t: fmt("cyan", t)

    # ⭐ FIX: requerido por defensive_operation
    fmt_cyan_text = fmt_cyan


    ###########################################################
    # 🔢 FALLBACK battle_fmt_num (store-safe)
    ###########################################################
    if not hasattr(S, "battle_fmt_num"):
        def battle_fmt_num(x):
            try:
                if isinstance(x, float) and x.is_integer():
                    x = int(x)

                if isinstance(x, basestring):
                    sx = x.strip()
                    if sx.isdigit():
                        x = int(sx)

                return "{:,}".format(int(x)).replace(",", ".")
            except:
                return str(x)

        S.battle_fmt_num = battle_fmt_num

    battle_fmt_num = S.battle_fmt_num


    ###########################################################
    # 🧠 SAFE LOG HUB (wrapper universal)
    # ----------------------------------------------------------
    # Evita repetir _blog/_safe_log_add en cada módulo.
    # - Busca battle_log_add primero en globals() (compat vieja)
    # - Luego en store (S.battle_log_add)
    # - Soporta color y (si existe) border kwarg
    # - Py2-safe: unicode-safe para tildes/ñ
    ###########################################################
    def _bl_supports_kwarg(fn, name):
        try:
            spec = inspect.getargspec(fn)  # Py2 compatible
            # si tiene **kwargs, soporta cualquier kwarg
            if spec.keywords is not None:
                return True
            if spec.args and name in spec.args:
                return True
            return False
        except:
            return False

    def _to_text_safe(x):
        # Py2: evitar crashes con unicode (tildes/ñ)
        try:
            return unicode(x)
        except:
            try:
                return str(x)
            except:
                return "<?>"

    def safe_battle_log_add(text, color=None, border=None):
        """
        Uso recomendado desde cualquier script:
            S.safe_battle_log_add("Hola")
            S.safe_battle_log_add("Texto", "#FF66CC")
            S.safe_battle_log_add("Texto", color="#FF66CC", border="#000000")
        """
        bl = None

        # 1) global (compat)
        try:
            bl = globals().get("battle_log_add", None)
        except:
            bl = None

        # 2) store
        if not callable(bl):
            try:
                bl = getattr(S, "battle_log_add", None)
            except:
                bl = None

        if not callable(bl):
            return

        t = _to_text_safe(text)

        supports_border = _bl_supports_kwarg(bl, "border")
        supports_color  = _bl_supports_kwarg(bl, "color")

        # ----------------------------------------------------
        # Intento 1: border + color por kwargs (si soporta)
        # ----------------------------------------------------
        if (border is not None) and supports_border:
            if (color is not None) and supports_color:
                try:
                    bl(t, color=color, border=border)
                    return
                except:
                    pass

            # ------------------------------------------------
            # Intento 2: border (y color posicional si hace falta)
            # ------------------------------------------------
            try:
                if color is None:
                    bl(t, border=border)
                else:
                    # compat: muchos logs viejos aceptan (text, color, border=..)
                    bl(t, color, border=border)
                return
            except:
                pass

        # ----------------------------------------------------
        # Intento 3: color por kwargs (si soporta)
        # ----------------------------------------------------
        if (color is not None) and supports_color:
            try:
                bl(t, color=color)
                return
            except:
                pass

        # ----------------------------------------------------
        # Intento 4: color posicional
        # ----------------------------------------------------
        if color is not None:
            try:
                bl(t, color)
                return
            except:
                pass

        # ----------------------------------------------------
        # Fallback final: solo texto
        # ----------------------------------------------------
        try:
            bl(t)
        except:
            pass

    # Export al store (clave)
    S.safe_battle_log_add = safe_battle_log_add


    ###########################################################
    # 🛑 FALLBACK PARA OPERACIÓN DEFENSIVA (op_def_*) – store-safe
    ###########################################################
    if not hasattr(S, "op_def_enemy"):
        def op_def_enemy(base, pct, reduced, final, color_key="effect"):
            return "{} {} → {} - {} = {}".format(
                fmt_white("Daño enemigo"),
                fmt(color_key, battle_fmt_num(base)),
                fmt_orange(str(pct)),
                fmt_blue(battle_fmt_num(reduced)),
                fmt_white(battle_fmt_num(final))
            )
        S.op_def_enemy = op_def_enemy

    if not hasattr(S, "op_def_damage"):
        def op_def_damage(base_eff, block, received):
            return "{} {} - {} = {}".format(
                fmt_white("Daño neto"),
                fmt_blue(battle_fmt_num(base_eff)),
                fmt_blue(battle_fmt_num(block)),
                fmt_red(battle_fmt_num(received))
            )
        S.op_def_damage = op_def_damage

    if not hasattr(S, "op_def_hp"):
        def op_def_hp(before, dmg, after):
            return "{} {} - {} = {}".format(
                fmt_white("HP"),
                fmt_blue(battle_fmt_num(before)),
                fmt_red(battle_fmt_num(dmg)),
                fmt_blue(battle_fmt_num(after))
            )
        S.op_def_hp = op_def_hp

    if not hasattr(S, "op_reflect_clean"):
        def op_reflect_clean(pct, value):
            return "{} {} ({})".format(
                fmt_effect("Reflejo"),
                fmt_blue(battle_fmt_num(value)),
                fmt_orange(str(pct))
            )
        S.op_reflect_clean = op_reflect_clean


    ###########################################################
    # 🔥 LOGS UNIFICADOS – CONCENTRAR / POTENCIAR
    ###########################################################
    def log_focus_unified(mode=None):
        return "{} {} → {} {}".format(
            fmt_purple("Concentrar"),
            fmt_white("Activado"),
            fmt_white("Próximo ataque"),
            fmt_purple("×2")
        )

    def log_potenciar_unified():
        return "{} {} → {} {}".format(
            fmt_effect("Potenciar"),
            fmt_white("Activado"),
            fmt_white("Próxima defensa"),
            fmt_purple("×2")
        )


    ###########################################################
    # 🔵 DEFENSIVO – Logs dinámicos
    ###########################################################
    def log_defense_extra(base, final):
        if base != final:
            txt = "{}×2({})".format(battle_fmt_num(base), battle_fmt_num(final))
        else:
            txt = battle_fmt_num(final)

        return "{} → Bloquea {}".format(
            fmt_cyan("Defensa Extra"),
            fmt_blue(txt)
        )

    def log_defense_reducer(block, percent, reduced):
        return "{} → Bloquea {} y reduce {}({})".format(
            fmt_cyan("Defensa Reductora"),
            fmt_blue(battle_fmt_num(block)),
            fmt_effect("{}%".format(percent)),
            fmt_blue(battle_fmt_num(reduced))
        )

    def log_defense_reflect(block, percent, reflected):
        return "{} → Bloquea {} y refleja {}({})".format(
            fmt_cyan("Defensa Reflectora"),
            fmt_blue(battle_fmt_num(block)),
            fmt_effect("{}%".format(percent)),
            fmt_blue(battle_fmt_num(reflected))
        )

    def log_defense_strong(base, final):
        if base != final:
            v = "{}×2({})".format(battle_fmt_num(base), battle_fmt_num(final))
        else:
            v = battle_fmt_num(final)

        return "{} → Bloquea {}".format(
            fmt_cyan("Defensa Fuerte"),
            fmt_blue(v)
        )


    ###########################################################
    # 🔥 OFENSIVO – Logs dinámicos (Markup-safe)
    ###########################################################
    def _split_renpy_tags(text):
        return re.split(r"(\{[^}]*\})", text)

    def colorize_numbers(text):
        chunks = _split_renpy_tags(text)
        for i, ch in enumerate(chunks):
            if ch.startswith("{") and ch.endswith("}"):
                continue
            chunks[i] = re.sub(r"(?<!#)\b(\d[\d\.]*)\b", lambda m: fmt_red(m.group(1)), ch)
        return "".join(chunks)

    def highlight_x2(text):
        chunks = _split_renpy_tags(text)
        for i, ch in enumerate(chunks):
            if ch.startswith("{") and ch.endswith("}"):
                continue
            ch = ch.replace("×2", fmt_purple("×2"))
            ch = ch.replace("x2", fmt_purple("×2"))
            chunks[i] = ch
        return "".join(chunks)

    def log_attack_simple(tech, dmg_text):
        return "{} → {} {} {}".format(
            fmt_red(tech),
            fmt_white("Inflige"),
            fmt_red(dmg_text),
            fmt_white("de daño.")
        )

    def log_attack_reducer(tech, dmg_text, pct):
        return (
            fmt_red(tech) + " " +
            fmt_white("→ Inflige ") +
            fmt_red(dmg_text) + fmt_white(" y reduce ") +
            fmt_orange("{}%".format(pct)) + fmt_white(" las defensas enemigas.")
        )

    def log_attack_direct(dmg_text):
        return (
            fmt_gold("Ataque Directo") + " " +
            fmt_white("→ ") + fmt_gold(dmg_text) + fmt_white(" de daño directo (ignora defensas).")
        )

    def log_attack_noatk(dmg_text):
        return (
            fmt_pink("Ataque Negador") + " " +
            fmt_white("→ ") + fmt_red(dmg_text) +
            fmt_white(" e impide el ataque enemigo.")
        )


    ###########################################################
    # ⭐ OPERACIÓN FINAL (ofensiva)
    ###########################################################
    def log_operation(parts, reflect, total):
        p = highlight_x2(colorize_numbers(parts))
        txt = fmt_white("Operación: ") + p

        if reflect > 0:
            txt += fmt_white(" + ") + fmt_blue(battle_fmt_num(reflect))

        txt += fmt_white(" = ") + fmt_gold(battle_fmt_num(total))
        return txt


    ###########################################################
    # ⭐ DAÑO TOTAL
    ###########################################################
    def log_total(total, reduction_pct=0):
        txt = fmt_white("Daño total: ") + fmt_gold(battle_fmt_num(total))
        if reduction_pct > 0:
            txt += fmt_white(" (") + fmt_orange("-{}% defensa general".format(reduction_pct)) + fmt_white(")")
        return txt


    ###########################################################
    # 🎲 RESULTADO DE DADOS (robusto)
    ###########################################################
    def _dice_to_bool(r):
        if r is True:
            return True
        if r is False or r is None:
            return False

        if isinstance(r, (int, long)):
            return (r != 0)
        if isinstance(r, float):
            return (r != 0.0)

        if isinstance(r, basestring):
            s = r.strip().lower()
            if s in ("1", "true", "t", "yes", "y", "ok", "success", "win", "hit", "acierto"):
                return True
            if s in ("0", "false", "f", "no", "n", "fail", "failure", "lose", "miss", "fallo", "error"):
                return False
            return False

        try:
            return bool(r)
        except:
            return False

    def log_dice_slots(rolls):
        if not rolls:
            return fmt_white("Resultados de tirada: — — —")

        icons = []
        for r in rolls:
            if _dice_to_bool(r):
                icons.append("{image=dice_success_icon}")
            else:
                icons.append("{image=dice_fail_icon}")

        return fmt_white("Resultados de tirada: ") + " ".join(icons)


    # --------------------------------------------------------
    # Late Sync: ahora sí existe PALETTE, sincronizamos OP_COLOR_*
    # --------------------------------------------------------
    if hasattr(S, "op_colors_sync"):
        try:
            S.op_colors_sync(force=True)
        except:
            pass


    # --------------------------------------------------------
    # Extensión segura: battle_log_add_ex (opcional border)
    # (la dejo, pero ahora puede delegar en safe_battle_log_add)
    # --------------------------------------------------------
    if not hasattr(S, "battle_log_add_ex"):

        def battle_log_add_ex(text, border=None):
            # Reusa el hub universal
            try:
                S.safe_battle_log_add(text, border=border)
            except:
                pass

        S.battle_log_add_ex = battle_log_add_ex


    # --------------------------------------------------------
    # Export útiles al store (opcional pero recomendado)
    # Para que otros módulos no dependan de globals().
    # --------------------------------------------------------
    S.fmt = fmt
    S.fmt_white = fmt_white
    S.fmt_red = fmt_red
    S.fmt_blue = fmt_blue
    S.fmt_gold = fmt_gold
    S.fmt_orange = fmt_orange
    S.fmt_purple = fmt_purple
    S.fmt_pink = fmt_pink
    S.fmt_effect = fmt_effect
    S.fmt_cyan = fmt_cyan
    S.fmt_cyan_text = fmt_cyan_text

    S.log_operation = log_operation
    S.log_total = log_total
    S.log_focus_unified = log_focus_unified
    S.log_potenciar_unified = log_potenciar_unified
    S.log_dice_slots = log_dice_slots
    S.colorize_numbers = colorize_numbers
    S.highlight_x2 = highlight_x2
