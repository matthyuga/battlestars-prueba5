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
        fmt_white  = getattr(S, "fmt_white",  lambda t: str(t))
        fmt_green  = (lambda t: "{color=%s}%s{/color}" % (pal.get("green", "#00FF00"), t))
        fmt_red    = getattr(S, "fmt_red",    lambda t: str(t))

        # (0) LOG DE TÉCNICAS SELECCIONADAS
        summary = getattr(S, "summary_lines", [])
        for line in summary:
            S.battle_log_add(line)

        # --------------------------------------------------------
        # (1) REDUCCIÓN DEL ENEMIGO
        # --------------------------------------------------------
        base_damage = int(base_damage or 0)
        reduc_val   = int(reduc_val or 0)

        # Daño directo pendiente del defensor activo.
        direct_pending = 0
        _mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        if _mode == "2v2":
            direct_pending = int(getattr(S, "pending_direct_damage_for_defense", 0) or 0)
        else:
            fn_get_direct = getattr(S, "bs_get_direct_pending", None)
            if callable(fn_get_direct):
                direct_pending = int(fn_get_direct("player") or 0)
            else:
                direct_pending = int(getattr(S, "enemy_direct_pending_damage", 0) or 0)

        _direct_only = (base_damage <= 0 and direct_pending > 0)

        _reduc_base = base_damage if base_damage > 0 else (direct_pending if _direct_only else 0)
        base_eff = max(0, int(_reduc_base) - reduc_val)

        if reduc_val > 0:
            # safe pct
            _reduc_base_pct = _reduc_base
            if _reduc_base_pct > 0:
                pct = int((reduc_val / float(_reduc_base_pct)) * 100)
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
                    "{color=%s}%s{/color} ×%s ({color=%s}%s{/color})" %
                    (pal["cyan"],
                     S.battle_fmt_num(base_blk_i),
                     mult,
                     pal["cyan"],
                     S.battle_fmt_num(blk_i))
                )
            else:
                parts.append(
                    "{color=%s}%s{/color}" %
                    (pal["cyan"], S.battle_fmt_num(blk_i))
                )

        parts_str = " + ".join(parts) if parts else fmt_cyan("0")

        # --------------------------------------------------------
        # (3) DEBUFF DEFENSIVO
        # --------------------------------------------------------
        deb_pct = float(getattr(S, "next_defense_reduction", 0.0) or 0.0)
        deb_val = 0
        eff_blk = total_block

        if _direct_only:
            eff_blk = 0
            txt = "{}: {} = {}".format(
                fmt_cyan("Defensas"),
                parts_str,
                fmt_cyan("0")
            )
        elif total_block > 0 and deb_pct > 0:
            deb_val = int(total_block * deb_pct)
            eff_blk = max(0, total_block - deb_val)

            txt = "{}: {} = {} - {}({}) = {}".format(
                fmt_cyan("Defensas"),
                parts_str,
                fmt_cyan(S.battle_fmt_num(total_block)),
                fmt_blue("{}%".format(int(deb_pct * 100))),
                fmt_blue(S.battle_fmt_num(deb_val)),
                fmt_cyan(S.battle_fmt_num(eff_blk))
            )
        else:
            txt = "{}: {} = {}".format(
                fmt_cyan("Defensas"),
                parts_str,
                fmt_cyan(S.battle_fmt_num(total_block))
            )

        operation_add(txt, border)

        # --------------------------------------------------------
        # (4) DAÑO FINAL
        # --------------------------------------------------------
        received_damage_def = max(0, base_eff - eff_blk)

        # --------------------------------------------------------
        # (4-b) REDUCCIÓN ESPECIAL (Salvaguarda) sobre daño defendible
        # Prioridad: ya pasó reducción común; ahora aplica especial.
        # --------------------------------------------------------
        spc_pct = float(getattr(S, "special_defense_reduction_pct", 0.0) or 0.0)
        if not _direct_only and spc_pct > 0.0:
            _before_spc = int(received_damage_def)
            received_damage_def = int(max(0, int(received_damage_def) * (1.0 - spc_pct)))
            operation_add(
                fmt_white("Salvaguarda:") + " " +
                fmt_red(S.battle_fmt_num(_before_spc)) +
                fmt_white(" × 50% = ") +
                fmt_red(S.battle_fmt_num(received_damage_def)),
                border
            )

        if _direct_only:
            received_damage = int(received_damage_def)
        else:
            received_damage = int(received_damage_def) + int(direct_pending)

        operation_add(
            S.op_def_damage(
                S.battle_fmt_num(base_eff),
                S.battle_fmt_num(eff_blk),
                S.battle_fmt_num(received_damage_def)
            ),
            border
        )

        if direct_pending > 0 and not _direct_only:
            operation_add(
                fmt_white("Daño restante:") + " " +
                fmt_red(S.battle_fmt_num(received_damage_def)) +
                fmt_white(" + ") +
                fmt_orange(S.battle_fmt_num(direct_pending)) +
                fmt_white(" = ") +
                fmt_red(S.battle_fmt_num(received_damage)),
                border
            )

        # --------------------------------------------------------
        # (5) RECUBRIMIENTO + HP objetivo defendido
        # --------------------------------------------------------
        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        def_key = str(getattr(S, "defense_target_key", "") or "")
        if not def_key and callable(getattr(S, "bs_get_active_unit_key", None)):
            try:
                def_key = str(S.bs_get_active_unit_key("player") or "player:0")
            except:
                def_key = "player:0"

        hp_before = int(getattr(S, "player_hp", 0) or 0)
        coating_type = "Hierro"
        coating_cover = 0
        coating_dura_before = 0
        coating_active = False
        if mode == "2v2" and def_key:
            fn_get_key = getattr(S, "bs_get_unit_by_key", None)
            if callable(fn_get_key):
                uu = fn_get_key(def_key)
                if isinstance(uu, dict):
                    hp_before = int(uu.get("hp", hp_before) or hp_before)
                    coating_type = str(uu.get("coating_type", "hierro") or "hierro").capitalize()
                    coating_cover = max(0, int(uu.get("coating_cover", 0) or 0))
                    coating_dura_before = max(0, int(uu.get("coating_durability_current", 0) or 0))
                    coating_active = bool(uu.get("coating_active", False))
        elif def_key and callable(getattr(S, "bs_get_unit_by_key", None)):
            uu = S.bs_get_unit_by_key(def_key)
            if isinstance(uu, dict):
                hp_before = int(uu.get("hp", hp_before) or hp_before)
                coating_type = str(uu.get("coating_type", "hierro") or "hierro").capitalize()
                coating_cover = max(0, int(uu.get("coating_cover", 0) or 0))
                coating_dura_before = max(0, int(uu.get("coating_durability_current", 0) or 0))
                coating_active = bool(uu.get("coating_active", False))

        if not (coating_active and coating_cover > 0 and coating_dura_before > 0):
            coating_cover = 0
            coating_dura_before = 0

        after_cover = max(0, int(received_damage) - int(coating_cover))
        coating_dura_after_raw = int(coating_dura_before) - int(after_cover)
        coating_dura_after = max(0, int(coating_dura_after_raw))
        hp_spill = max(0, int(after_cover) - int(coating_dura_before))

        def _fmt_signed(v):
            vv = int(v or 0)
            if vv < 0:
                return "-" + S.battle_fmt_num(abs(vv))
            return S.battle_fmt_num(vv)

        hp_after  = max(0, hp_before - hp_spill)
        S.defense_hp_before = int(hp_before)
        S.defense_hp_expected_after_coating = int(hp_after)

        operation_add(
            "    ◉ {}:".format(str(coating_type or "Recubrimiento")),
            border
        )
        operation_add(
            "      cubre: {} - {} = {}".format(
                S.battle_fmt_num(coating_cover),
                S.battle_fmt_num(received_damage),
                S.battle_fmt_num(after_cover)
            ),
            border
        )
        operation_add(
            "      durabilidad: {} - {} = {}".format(
                S.battle_fmt_num(coating_dura_before),
                S.battle_fmt_num(after_cover),
                _fmt_signed(coating_dura_after_raw)
            ),
            border
        )
        operation_add(
            "      ◉ " + fmt_white("HP:") + " " +
            fmt_green(S.battle_fmt_num(hp_before)) +
            fmt_white(" - ") +
            fmt_red(S.battle_fmt_num(hp_spill)) +
            fmt_white(" = ") +
            (fmt_green(S.battle_fmt_num(hp_after)) if int(hp_after or 0) > 0 else fmt_red("{} KO".format(S.battle_fmt_num(hp_after)))),
            border
        )


        S.defense_received_includes_direct = bool(direct_pending > 0)

        # --------------------------------------------------------
        # (6) REFLECT
        # --------------------------------------------------------
        # Ideal: guardar pct real en Actions cuando se calcula reflect.
        # Por ahora: usa S.last_reflect_pct si existe, si no cae a "?"
        if hp_after > 0 and int(reflected or 0) > 0:
            pct_txt = getattr(S, "last_reflect_pct_txt", None)
            if not pct_txt:
                pct_val = getattr(S, "last_reflect_pct", None)
                if isinstance(pct_val, float):
                    pct_txt = "{}%".format(int(pct_val * 100))
                elif base_damage > 0:
                    pct_txt = "{}%".format(int((int(reflected or 0) / float(base_damage)) * 100))
                else:
                    pct_txt = "0%"

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
