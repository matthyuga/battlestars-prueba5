# ============================================================
# 04D_DEFENSIVE_OPERATION.rpy – Matemática defensiva + logs
# Versión v11.3 – NoHardcodeMultipliers + SafePct + StoreFriendly
# ------------------------------------------------------------
# ✔ No hardcodea ×2, calcula multiplicador
# ✔ Safe division (no crash si base_damage=0)
# ✔ Reflect pct no hardcodeado (usa S.last_reflect_pct si existe)
# ✔ Compatible con Actions v14 / Core v9.3 (S.blocks_list, S.reduc_val, etc.)
# ============================================================

label defensive_operation(base_damage, reduc_val, blocks_list, reflected):

    python:
        import renpy.store as S

        pal = getattr(S, "PALETTE", PALETTE)
        border = pal["white"]

        # fmt fallbacks
        fmt_blue   = getattr(S, "fmt_blue",   lambda t: str(t))
        fmt_cyan   = getattr(S, "fmt_cyan",   lambda t: str(t))
        fmt_orange = getattr(S, "fmt_orange", lambda t: str(t))

        # (0) LOG DE TÉCNICAS SELECCIONADAS
        summary = getattr(S, "summary_lines", [])
        for line in summary:
            S.battle_log_add(line)

        # --------------------------------------------------------
        # (1) REDUCCIÓN DEL ENEMIGO
        # --------------------------------------------------------
        base_damage = int(base_damage or 0)
        reduc_val   = int(reduc_val or 0)

        base_eff = max(0, base_damage - reduc_val)

        if reduc_val > 0:
            # safe pct
            if base_damage > 0:
                pct = int((reduc_val / float(base_damage)) * 100)
            else:
                pct = 0

            operation_add(
                S.op_def_enemy(
                    S.battle_fmt_num(base_damage),
                    "{}%".format(pct),
                    S.battle_fmt_num(reduc_val),
                    S.battle_fmt_num(base_eff),
                    color_key="effect"
                ),
                border
            )

        # --------------------------------------------------------
        # (2) DEFENSAS – BLOQUES
        # --------------------------------------------------------
        # blocks_list = [(base_blk, final_blk), ...]
        total_block = 0
        parts = []

        for base_blk, blk in (blocks_list or []):
            try:
                base_blk_i = int(base_blk or 0)
            except:
                base_blk_i = 0
            try:
                blk_i = int(blk or 0)
            except:
                blk_i = 0

            total_block += blk_i

            # multiplicador “inteligente”
            mult = None
            if base_blk_i > 0 and blk_i != base_blk_i:
                # redondeo a 2 decimales si fuera fraccional
                mult_val = blk_i / float(base_blk_i)
                # si está muy cerca de un entero, lo mostramos entero
                if abs(mult_val - round(mult_val)) < 0.01:
                    mult = str(int(round(mult_val)))
                else:
                    mult = "{:.2f}".format(mult_val)

            if mult:
                parts.append(
                    "{color=%s}%s×%s(%s){/color}" %
                    (pal["blue"],
                     S.battle_fmt_num(base_blk_i),
                     mult,
                     S.battle_fmt_num(blk_i))
                )
            else:
                parts.append(
                    "{color=%s}%s{/color}" %
                    (pal["blue"], S.battle_fmt_num(blk_i))
                )

        parts_str = " + ".join(parts) if parts else fmt_blue("0")

        # --------------------------------------------------------
        # (3) DEBUFF DEFENSIVO
        # --------------------------------------------------------
        deb_pct = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
        deb_val = 0
        eff_blk = total_block

        if total_block > 0 and deb_pct > 0:
            deb_val = int(total_block * deb_pct)
            eff_blk = max(0, total_block - deb_val)

            txt = "{}: {} = {} - {}({}) = {}".format(
                fmt_cyan("Defensas"),
                parts_str,
                fmt_blue(S.battle_fmt_num(total_block)),
                fmt_orange("{}%".format(int(deb_pct * 100))),
                fmt_blue(S.battle_fmt_num(deb_val)),
                fmt_blue(S.battle_fmt_num(eff_blk))
            )
        else:
            txt = "{}: {} = {}".format(
                fmt_cyan("Defensas"),
                parts_str,
                fmt_blue(S.battle_fmt_num(total_block))
            )

        operation_add(txt, border)

        # --------------------------------------------------------
        # (4) DAÑO FINAL
        # --------------------------------------------------------
        received_damage = max(0, base_eff - eff_blk)

        operation_add(
            S.op_def_damage(
                S.battle_fmt_num(base_eff),
                S.battle_fmt_num(eff_blk),
                S.battle_fmt_num(received_damage)
            ),
            border
        )

        # --------------------------------------------------------
        # (5) HP JUGADOR
        # --------------------------------------------------------
        hp_before = int(getattr(S, "player_hp", 0) or 0)
        hp_after  = max(0, hp_before - received_damage)

        operation_add(
            S.op_def_hp(
                S.battle_fmt_num(hp_before),
                S.battle_fmt_num(received_damage),
                S.battle_fmt_num(hp_after)
            ),
            border
        )

        # --------------------------------------------------------
        # (6) REFLECT
        # --------------------------------------------------------
        # Ideal: guardar pct real en Actions cuando se calcula reflect.
        # Por ahora: usa S.last_reflect_pct si existe, si no cae a "?"
        if hp_after > 0 and int(reflected or 0) > 0:
            pct_txt = getattr(S, "last_reflect_pct_txt", None)
            if not pct_txt:
                pct_val = getattr(S, "last_reflect_pct", None)
                pct_txt = "{}%".format(int(pct_val * 100)) if isinstance(pct_val, float) else "?"

            operation_add(
                S.op_reflect_clean(pct_txt, S.battle_fmt_num(reflected)),
                border
            )

        # --------------------------------------------------------
        # (7) LIMPIEZA
        # --------------------------------------------------------
        if hasattr(S, "next_defense_reduction"):
            S.next_defense_reduction = 0.0

        # opcional: limpiar reflect pct “del turno”
        if hasattr(S, "last_reflect_pct"):
            S.last_reflect_pct = None
        if hasattr(S, "last_reflect_pct_txt"):
            S.last_reflect_pct_txt = None

        operation_dump_to_battle_log()

    $ received_damage = received_damage
    $ hp_after = hp_after
    return
