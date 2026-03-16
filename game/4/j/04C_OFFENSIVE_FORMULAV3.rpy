# ============================================================
# 04C_OFFENSIVE_FORMULA.rpy – Fórmula final (SIN reflect)
# ============================================================
# v5.1 – SafeLogHub + StoreSafe log_* + PctDisplay Fix
# ------------------------------------------------------------
# ✅ NUEVO PARADIGMA:
# - Reflect NO se consume aquí.
# - Reflect del atacante se resuelve al INICIO de su turno
#   (ej: battle_offensive_turn / battle_enemy_turn).
#
# - Construye texto de operación mostrando ×N cuando es exacto
# - Guarda S.offensive_formula_text para HUD
# - Debuff defensivo normalizado (0..1). Acepta 0.10 o 10
# - Logs usan hub: S.safe_battle_log_add / S.battle_log_add_ex si existe
# - log_operation/log_total se buscan en S primero y luego globals
# - Pct display: pasa 0..100 (no 0.1)
# - Nunca devuelve negativos (clamp a 0)
# ============================================================

label offensive_formula(dmg, attack_records):

    python:
        import renpy.store as S
        global total_damage

        # ----------------------------------------------------
        # fmt seguro (usa S.battle_fmt_num si existe)
        # ----------------------------------------------------
        def _fmt(n):
            try:
                fn = getattr(S, "battle_fmt_num", None)
                if callable(fn):
                    return fn(n)
            except:
                pass
            try:
                return "{:,}".format(int(n)).replace(",", ".")
            except:
                try:
                    return str(int(n))
                except:
                    return str(n)

        # ----------------------------------------------------
        # helpers int/clamp
        # ----------------------------------------------------
        def _to_int(v, default=0):
            try:
                return int(v)
            except:
                try:
                    return int(float(v))
                except:
                    return default

        def _clamp0(v):
            v = _to_int(v, 0)
            if v < 0:
                v = 0
            return v

        # ----------------------------------------------------
        # logger hub (preferir store-safe helper común)
        # ----------------------------------------------------
        def _blog(t, c=None, border=None):
            # 1) safe wrapper si existe (ideal)
            try:
                fn = getattr(S, "safe_battle_log_add", None)
                if callable(fn):
                    try:
                        if c is None and border is None:
                            fn(t)
                        else:
                            fn(t, color=c, border=border)
                    except:
                        try:
                            if c is None: fn(t)
                            else: fn(t, c)
                        except:
                            pass
                    return
            except:
                pass

            # 2) battle_log_add_ex si existe (border opcional)
            try:
                fn2 = getattr(S, "battle_log_add_ex", None)
                if callable(fn2):
                    try:
                        fn2(t, border=border)
                    except:
                        try:
                            fn2(t)
                        except:
                            pass
                    return
            except:
                pass

            # 3) fallback global/store battle_log_add
            try:
                g = globals().get("battle_log_add", None)
                if callable(g):
                    if c is None: g(t)
                    else: g(t, c)
                    return
            except:
                pass
            try:
                s = getattr(S, "battle_log_add", None)
                if callable(s):
                    if c is None: s(t)
                    else: s(t, c)
            except:
                pass

        # ----------------------------------------------------
        # 1) Construcción del texto de fórmula (×N real)
        # ----------------------------------------------------
        parts_raw = []

        for pair in (attack_records or []):
            try:
                base, dmg_i = pair
            except:
                continue

            b = _to_int(base, 0)
            d = _to_int(dmg_i, 0)

            if b <= 0:
                continue

            if d == b:
                parts_raw.append(_fmt(b))
                continue

            mult = None
            try:
                mult = d // b
            except:
                mult = None

            if mult and mult >= 2:
                try:
                    if (b * mult) == d:
                        parts_raw.append("{}×{}({})".format(_fmt(b), int(mult), _fmt(d)))
                    else:
                        parts_raw.append("{}→{}".format(_fmt(b), _fmt(d)))
                except:
                    parts_raw.append("{}→{}".format(_fmt(b), _fmt(d)))
            else:
                parts_raw.append("{}→{}".format(_fmt(b), _fmt(d)))

        formula_text = " + ".join(parts_raw) if parts_raw else "0"

        try:
            S.offensive_formula_text = formula_text
        except:
            pass

        # ----------------------------------------------------
        # 2) REFLECT (NUEVO SISTEMA) — NO SE CONSUME AQUÍ
        # ----------------------------------------------------
        # Reflect del atacante ya fue cobrado al inicio del turno
        # (battle_offensive_turn / battle_enemy_turn).
        extra_reflect = 0

        dmg_int = _clamp0(dmg)
        total_with_reflect = dmg_int  # 👈 ya no se suma reflect acá

        # ----------------------------------------------------
        # 3) Debuff defensivo (Ataque Reductor) — normalizado 0..1
        # ----------------------------------------------------
        reduction = getattr(S, "next_defense_reduction", 0)
        try:
            reduction = float(reduction or 0.0)
        except:
            reduction = 0.0

        if reduction < 0.0:
            reduction = 0.0

        # Si viene 10, asumir 10% -> 0.10
        if reduction > 1.0:
            try:
                reduction = reduction / 100.0
            except:
                reduction = 1.0

        if reduction > 1.0:
            reduction = 1.0

        # Para logs: 0..100 entero
        try:
            reduction_pct_display = int(round(reduction * 100.0))
        except:
            reduction_pct_display = 0

        # ----------------------------------------------------
        # 4) LOGS — Operación + Daño total (store-safe)
        # ----------------------------------------------------
        try:
            op_fn = getattr(S, "log_operation", None)
            if not callable(op_fn):
                op_fn = globals().get("log_operation", None)

            # seguimos llamando con reflect=0 para no romper formato
            if callable(op_fn):
                _op_line = op_fn(formula_text, extra_reflect, _fmt(total_with_reflect))
            else:
                _op_line = "Operación: {} (+Reflect {}) = {}".format(
                    formula_text, _fmt(extra_reflect), _fmt(total_with_reflect)
                )

            _fn_bla = getattr(S, "battle_log_add", None)
            if callable(_fn_bla):
                _fn_bla(_op_line, group="operation")
            else:
                _blog(_op_line)
        except:
            pass

        # ----------------------------------------------------
        # 4.1) Desglose de recursos ofensivos (spoiler [I])
        # ----------------------------------------------------
        try:
            _bla = getattr(S, "battle_log_add", None)
            if callable(_bla):
                def _safe_int(v, d=0):
                    try:
                        return int(v)
                    except:
                        try:
                            return int(str(v or "0").replace(".", "").replace(",", "").strip() or d)
                        except:
                            return int(d)

                rei_before = _safe_int(getattr(S, "turn_off_rei_before", getattr(S, "player_reiatsu", 0)), 0)
                rei_after = _safe_int(getattr(S, "turn_off_rei_after", getattr(S, "player_reiatsu", 0)), 0)
                ene_before = _safe_int(getattr(S, "turn_off_ene_before", getattr(S, "player_energy", 0)), 0)
                ene_after = _safe_int(getattr(S, "turn_off_ene_after", getattr(S, "player_energy", 0)), 0)

                rei_base = _safe_int(getattr(S, "player_reiatsu_base", rei_before), rei_before)
                ene_base = _safe_int(getattr(S, "player_energy_base", ene_before), ene_before)

                rei_turn_use = max(0, int(rei_before - rei_after))
                ene_turn_use = max(0, int(ene_before - ene_after))

                # Fallback robusto: si no hubo acumulador válido, usar consumo del turno.
                rei_tech_sum = max(0, _safe_int(getattr(S, "turn_off_rei_tech_sum", rei_turn_use), rei_turn_use))
                ene_tech_sum = max(0, _safe_int(getattr(S, "turn_off_ene_tech_sum", ene_turn_use), ene_turn_use))

                _bla("▸ Recursos ofensivos:", "#FFFFFF", group="resource_detail")
                _bla("   {color=#88CCFF}Reiatsu: {} - {} = {}{/color}".format(_fmt(rei_base), _fmt(rei_turn_use), _fmt(rei_after)), group="resource_detail")
                _bla("   {color=#FFAA66}Energía: {} - {} = {}{/color}".format(_fmt(ene_base), _fmt(ene_turn_use), _fmt(ene_after)), group="resource_detail")
        except:
            pass

        try:
            tot_fn = getattr(S, "log_total", None)
            if not callable(tot_fn):
                tot_fn = globals().get("log_total", None)

            dmg_directo = 0
            try:
                dmg_directo = int(getattr(S, "direct_pending_damage", 0) or 0)
            except:
                dmg_directo = 0
            if dmg_directo < 0:
                dmg_directo = 0

            if callable(tot_fn):
                _blog(tot_fn(
                    total_with_reflect + dmg_directo,
                    reduction_pct_display,
                    defendible=total_with_reflect,
                    directo=dmg_directo
                ))
            else:
                if dmg_directo > 0:
                    _blog("TOTAL: {} defendibles + {} directos = {}".format(
                        _fmt(total_with_reflect), _fmt(dmg_directo), _fmt(total_with_reflect + dmg_directo)
                    ))
                else:
                    _blog("TOTAL: {} defendibles".format(_fmt(total_with_reflect)))
        except:
            pass

        # ----------------------------------------------------
        # 5) Resultado final hacia el resolutor
        # ----------------------------------------------------
        total_damage = total_with_reflect

    return
