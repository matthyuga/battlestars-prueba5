# ===========================================================
# 06A_BATTLE_HUD_SYSTEM.RPY – Sistema de Barras de HP y HUD
# v3.5 FocusSync Edition (Ren'Py 7.4.9)
# -----------------------------------------------------------
# - Costos dinámicos EXACTOS (Reiatsu x2 solo en técnica afectada)
# - Energía no se duplica
# - El HUD muestra lo mismo que el selector
# - Cero costos fantasmas / reseteo limpio
# ===========================================================

init -970 python:

    # === Estado HUD ===
    # Bootstrap seguro sin hardcodes: se sincroniza en runtime desde battle_start.
    battle_hp_player_max = 1
    battle_hp_enemy_max = 1
    battle_hp_player = battle_hp_player_max
    battle_hp_enemy = battle_hp_enemy_max

    hp_flash_timer = 0
    hp_flash_color = None
    hud_visible = False

    # === Nombres HUD (display) ===
    hud_player_name = "Jugador"
    hud_enemy_name  = "Enemigo"

    # === Estados de simulación de recursos (jugador) ===
    simulated_reiatsu = 0
    simulated_energy = 0

    enemy_simulated_reiatsu = 0
    enemy_simulated_energy = 0

    # === Estado visual HUD IA (Fase 1) ===
    HUD_AI_STYLES = ("carmesi", "fantasy", "grey", "virtual")
    hud_style_by_unit = {}
    hud_panel_mode_by_unit = {}
    hud_collapsed_by_unit = {}


    # ===========================================================
    # 🔸 MAPA GLOBAL (visual → TECH_ID)
    # ===========================================================
    TECH_MAP_GLOBAL = {
        "Ataque Extra":        "extra_attack",
        "Técnica Extra":       "extra_tech",
        "Ataque Reductor":     "attack_reducer",
        "Ataque Directo":      "direct_attack",
        "Ataque Negador":      "noatk_attack",
        "Ataque más fuerte":   "stronger_attack",

        "Defensa Extra":        "defense_extra",
        "Defensa Reductora":    "defense_reducer",
        "Defensa Reflectora":   "defense_reflect",
        "Defensa Fuerte":       "defense_strong_block",

        "Concentrar":          "focus",
        "Concentrar x2":       "focus",
        "Potenciar":           "defense_boost",
    }


    # ===========================================================
    # 🔍 DETECTAR QUÉ TÉCNICA SERÁ DUPLICADA POR FOCUS
    # ===========================================================
    def hud_find_focus_target_index(queue, mode):

        focus_seen = False
        boost_seen = False

        for i, name in enumerate(queue):

            # -------------------------
            # MODO OFENSIVO
            # -------------------------
            if mode == "offensive":
                if name in ("Concentrar", "Concentrar x2"):
                    focus_seen = True
                    continue

                if focus_seen:
                    tech_id = TECH_MAP_GLOBAL.get(name)
                    if tech_id in (
                        "extra_attack", "extra_tech", "attack_reducer",
                        "direct_attack", "noatk_attack",
                        "strong_attack", "stronger_attack"
                    ):
                        return i

            # -------------------------
            # MODO DEFENSIVO
            # -------------------------
            if mode == "defensive":
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


    def _hud_player_unit_key_for_preview():
        import renpy.store as S
        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"

        if mode == "2v2":
            try:
                fn_ctx = getattr(S, "bs_get_turn_ctx", None)
                fn_key = getattr(S, "bs_unit_key", None)
                if callable(fn_ctx) and callable(fn_key):
                    ctx = fn_ctx() or {}
                    team = str(ctx.get("owner_team", "player") or "player").strip().lower()
                    slot = int(ctx.get("owner_slot", 0) or 0)
                    if team == "player":
                        return str(fn_key("player", slot) or "player:0")
            except:
                pass

        try:
            fn_akt = getattr(S, "bs_get_active_unit_key", None)
            if callable(fn_akt):
                return str(fn_akt("player") or "player:0")
        except:
            pass

        return "player:0"

    # ===========================================================
    # 🔹 FUNCIÓN: Actualizar costos dinámicos simulados (HUD)
    # ===========================================================
    def hud_update_simulation_costs(user, pending_tech_list):

        global simulated_reiatsu, simulated_energy

        import renpy.store as S

        # robustez: al inicio del combate battle_mode puede no existir todavía.
        mode = str(getattr(S, "battle_mode", "offensive") or "offensive")
        queue = list(pending_tech_list or [])

        # detectar técnica afectada por focus
        focus_target = hud_find_focus_target_index(queue, mode)

        total_rei = 0
        total_ene = 0

        for i, tech_name in enumerate(queue):

            tech_id = TECH_MAP_GLOBAL.get(tech_name, None)
            if tech_id is None:
                continue

            cost = S.reiatsu_energy_dynamic_cost(tech_id, user, unit_key=_hud_player_unit_key_for_preview())

            rei_cost = cost["reiatsu_cost"]
            ene_cost = cost["energy_cost"]

            # si esta técnica es la afectada → DUPLICAR SOLO REIATSU
            if i == focus_target:
                rei_cost *= 2

            total_rei += rei_cost
            total_ene += ene_cost

        simulated_reiatsu = S.player_reiatsu - total_rei
        simulated_energy  = S.player_energy  - total_ene


    # ===========================================================
    # 🔸 Actualiza barras de HP
    # ===========================================================
    def battle_update_hp_bars(player_hp, enemy_hp, flash_target=None, color=None):
        global battle_hp_player, battle_hp_enemy, hp_flash_timer, hp_flash_color

        battle_hp_player = int(player_hp)
        battle_hp_enemy = int(enemy_hp)

        if flash_target:
            hp_flash_timer = 10
            hp_flash_color = color

        if renpy.get_screen("battle_hp_overlay"):
            renpy.restart_interaction()

        try:
            battle_update_atmosphere_by_hp(player_hp, enemy_hp)
        except:
            pass


    # ===========================================================
    # 🔸 Mostrar HUD
    # ===========================================================
    def battle_show_hud(sync_fade=True):
        global hud_visible, simulated_reiatsu, simulated_energy
        global enemy_simulated_reiatsu, enemy_simulated_energy
        global hud_player_name, hud_enemy_name

        import renpy.store as S

        hud_visible = True

        # ✅ Nombres dinámicos (display) con fallback seguro
        try:
            hud_player_name = S.battle_player.get("name", "Jugador")
        except:
            hud_player_name = "Jugador"

        try:
            hud_enemy_name = S.battle_enemy.get("name", "Enemigo")
        except:
            hud_enemy_name = "Enemigo"

        simulated_reiatsu = S.player_reiatsu
        simulated_energy  = S.player_energy

        enemy_simulated_reiatsu = S.enemy_reiatsu
        enemy_simulated_energy  = S.enemy_energy

        if sync_fade:
            renpy.with_statement(Dissolve(0.35))

        renpy.show_screen("battle_hp_overlay")
        renpy.show_screen("battle_damage_popups")
        renpy.show_screen("battle_turn_summary_overlay")

        renpy.restart_interaction()


    # ===========================================================
    # 🔸 Ocultar HUD
    # ===========================================================
    def battle_hide_hud():
        global hud_visible
        hud_visible = False

        renpy.with_statement(Dissolve(0.25))

        renpy.hide_screen("battle_hp_overlay")
        renpy.hide_screen("battle_damage_popups")
        renpy.hide_screen("battle_turn_summary_overlay")

        renpy.restart_interaction()


    def hud_ai_normalize_char_id(char_id):
        raw = str(char_id or "").strip().lower()
        return raw.replace(" ", "_").replace("-", "_")


    HUD_AI_CHAR_ALIASES = {
        "neliel": "nel",
        "tier_harribel": "harribel",
        "tia_harribel": "harribel",
    }


    def hud_ai_char_candidates(char_id):
        base = hud_ai_normalize_char_id(char_id)
        if not base:
            return []
        out = [base]
        alias = HUD_AI_CHAR_ALIASES.get(base)
        if alias and alias not in out:
            out.append(alias)
        if "_" in base:
            short = base.split("_")[0]
            if short and short not in out:
                out.append(short)
        return out


    def hud_ai_get_style(unit_key):
        k = str(unit_key or "")
        if not k:
            return "carmesi"
        v = str(hud_style_by_unit.get(k, "carmesi") or "carmesi").strip().lower()
        if v not in HUD_AI_STYLES:
            v = "carmesi"
        hud_style_by_unit[k] = v
        return v


    def hud_ai_get_panel_mode(unit_key):
        k = str(unit_key or "")
        if not k:
            return "stat"
        m = str(hud_panel_mode_by_unit.get(k, "stat") or "stat").strip().lower()
        if m not in ("stat", "option"):
            m = "stat"
        hud_panel_mode_by_unit[k] = m
        return m


    def hud_ai_resolve_frame(style_name, panel_mode):
        style = str(style_name or "carmesi").strip().lower()
        mode = str(panel_mode or "stat").strip().lower()
        path = "gui/battle/hud_ai/frames/frame_{}_{}.png".format(style, mode)
        return path if renpy.loadable(path) else None


    def hud_ai_resolve_portrait(char_id, variant="head"):
        var = str(variant or "head").strip().lower()
        if var not in ("head", "full", "token"):
            var = "head"
        for cid in hud_ai_char_candidates(char_id):
            path = "gui/battle/hud_ai/portraits/portrait_{}_{}.png".format(cid, var)
            if renpy.loadable(path):
                return path
        return None


    def hud_ai_resolve_portrait_for_state(char_id, collapsed=False, mode="stat"):
        if collapsed:
            return (
                hud_ai_resolve_portrait(char_id, "token")
                or hud_ai_resolve_portrait(char_id, "head")
                or hud_ai_resolve_portrait(char_id, "full")
            )
        if str(mode or "stat").strip().lower() == "option":
            return (
                hud_ai_resolve_portrait(char_id, "head")
                or hud_ai_resolve_portrait(char_id, "full")
                or hud_ai_resolve_portrait(char_id, "token")
            )
        return (
            hud_ai_resolve_portrait(char_id, "head")
            or hud_ai_resolve_portrait(char_id, "full")
            or hud_ai_resolve_portrait(char_id, "token")
        )


    def hud_ai_is_autonomous_unit(team_name, unit_data):
        team = str(team_name or "").strip().lower()
        if isinstance(unit_data, dict):
            for k in ("is_ai", "ai", "autonomous"):
                if k in unit_data:
                    try:
                        if bool(unit_data.get(k)):
                            return True
                    except:
                        pass
            c = str(unit_data.get("controller", "") or "").strip().lower()
            if c in ("ai", "cpu", "autonomous", "npc"):
                return True
            ctl = str(unit_data.get("controlled_by", "") or "").strip().lower()
            if ctl in ("ai", "cpu", "autonomous", "npc"):
                return True
            role = str(unit_data.get("team_role", "") or "").strip().lower()
            if role in ("ally_npc", "enemy_npc", "npc"):
                return True
        return team == "enemy"


    def hud_ai_get_collapsed(unit_key):
        k = str(unit_key or "")
        if not k:
            return False
        v = bool(hud_collapsed_by_unit.get(k, False))
        hud_collapsed_by_unit[k] = v
        return v


    def hud_ai_toggle_collapsed(unit_key):
        k = str(unit_key or "")
        if not k:
            return
        hud_collapsed_by_unit[k] = not bool(hud_collapsed_by_unit.get(k, False))
        renpy.restart_interaction()


    def hud_ai_cycle_style(unit_key):
        k = str(unit_key or "")
        if not k:
            return
        cur = hud_ai_get_style(k)
        try:
            idx = list(HUD_AI_STYLES).index(cur)
        except:
            idx = 0
        nxt = HUD_AI_STYLES[(idx + 1) % len(HUD_AI_STYLES)]
        hud_style_by_unit[k] = nxt
        renpy.restart_interaction()


    def hud_ai_toggle_panel_mode(unit_key):
        k = str(unit_key or "")
        if not k:
            return
        cur = hud_ai_get_panel_mode(k)
        hud_panel_mode_by_unit[k] = "option" if cur == "stat" else "stat"
        renpy.restart_interaction()


    def hud_ai_resolve_icon(name):
        path = "gui/battle/hud_ai/icons/{}.png".format(str(name or "").strip())
        return path if renpy.loadable(path) else None


    def hud_ai_layout_profile(mode_tag, pcount=1, ecount=1):
        mode = str(mode_tag or "1v1").strip().lower()
        total = int(max(1, pcount) + max(1, ecount))

        # Baseline (1v1)
        panel_w = 150
        panel_h = 312
        token_w = 118
        token_h = 162
        col_spacing = 8
        root_spacing = 14
        name_size = 17
        stat_size = 9

        # Ajuste para modos con más unidades visibles simultáneamente.
        if mode == "2v2" or total >= 4:
            panel_w = 136
            panel_h = 288
            token_w = 110
            token_h = 154
            col_spacing = 6
            root_spacing = 10
            name_size = 15
            stat_size = 8

        return {
            "panel_w": panel_w,
            "panel_h": panel_h,
            "token_w": token_w,
            "token_h": token_h,
            "col_spacing": col_spacing,
            "root_spacing": root_spacing,
            "name_size": name_size,
            "stat_size": stat_size,
        }


    def hud_ai_team_count(team_name):
        t = str(team_name or "player").strip().lower()
        ids = getattr(renpy.store, "battle_player_ids", []) if t == "player" else getattr(renpy.store, "battle_enemy_ids", [])
        return min(2, max(1, len(ids or [])))


    def hud_ai_resolve_unit_name(team_name, slot_idx, unit_data):
        if isinstance(unit_data, dict):
            nm = str(unit_data.get("char_id", "") or unit_data.get("name", "") or "").strip()
            if nm:
                return nm
        pref = "P" if str(team_name or "player").strip().lower() == "player" else "E"
        return "{}{}".format(pref, int(slot_idx or 0) + 1)


    def hud_ai_res_value(res_map, key):
        try:
            if isinstance(res_map, dict):
                return int(res_map.get(key, 0) or 0)
        except:
            pass
        return 0


    def hud_safe_panel_color(style_name):
        style = str(style_name or "grey").strip().lower()
        return {
            "grey": "#1F2328CC",
            "carmesi": "#4B0D1BCC",
            "virtual": "#0F2F3CCC",
            "fantasy": "#1D3A1CCC",
        }.get(style, "#1F2328CC")


    def hud_safe_label_offense_force(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_offense_force: n/a"
        try:
            mode = str(store.ai_effective_offense_mode(unit_key) or "normal") if hasattr(store, "ai_effective_offense_mode") else "normal"
        except:
            mode = "normal"
        return "label_offense_force: {}".format(mode)


    def hud_safe_label_offense_concat(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_offense_concat: n/a"
        try:
            mode = str(store.ai_effective_offense_concat(unit_key) or "inherit") if hasattr(store, "ai_effective_offense_concat") else "inherit"
        except:
            mode = "inherit"
        return "label_offense_concat: {}".format(mode)


    def hud_safe_label_defense_force(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_defense_force: n/a"
        try:
            mode = str(store.ai_effective_defense_mode(unit_key) or "normal") if hasattr(store, "ai_effective_defense_mode") else "normal"
        except:
            mode = "normal"
        return "label_defense_force: {}".format(mode)


    def hud_safe_label_defense_concat(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_defense_concat: n/a"
        try:
            v = bool(store.ai_effective_defense_concat(unit_key)) if hasattr(store, "ai_effective_defense_concat") else False
        except:
            v = False
        return "label_defense_concat: {}".format("on" if v else "off")


    def hud_safe_label_focus(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_focus: n/a"
        try:
            v = bool(store.ai_effective_allow_focus(unit_key)) if hasattr(store, "ai_effective_allow_focus") else False
        except:
            v = False
        return "label_focus: {}".format("on" if v else "off")


    def hud_safe_label_target(unit_key, team_name="enemy"):
        if str(team_name or "enemy").strip().lower() != "enemy":
            return "label_target: n/a"
        try:
            r = store.ai_effective_target_rule(unit_key) if hasattr(store, "ai_effective_target_rule") else {"mode":"auto","slot":0}
            m = str(r.get("mode", "auto") or "auto")
            s = int(r.get("slot", 0) or 0)
            return "label_target: forzar_p{}".format(s + 1) if m == "force_slot" else "label_target: auto"
        except:
            return "label_target: auto"


    def hud_ai_option_cycle(unit_key, team_name, slot_idx, field_name):
        if str(team_name or "").strip().lower() != "enemy":
            return
        try:
            import renpy.store as S
            S.ai_ui_selected_enemy_slot = int(slot_idx or 0)
        except:
            return

        fn_name = {
            "offense_force": "ai_ui_cycle_offense_mode",
            "offense_concat": "ai_ui_cycle_offense_concat_rule",
            "defense_force": "ai_ui_cycle_defense_mode",
            "defense_concat": "ai_ui_cycle_concat_rule",
            "focus": "ai_ui_cycle_focus_rule",
            "target": "ai_ui_cycle_target_rule",
        }.get(str(field_name or "").strip().lower(), "")
        if not fn_name:
            return

        try:
            fn = getattr(S, fn_name, None)
            if callable(fn):
                fn()
        except:
            pass


    def hud_ai_finalize_phase5_status():
        """Checklist técnico mínimo de cierre Fase 5 (sin ejecutar combate)."""
        return {
            "mode_coverage": True,
            "unit_scoped_controls": True,
            "asset_fallbacks": True,
            "manual_smoke_pending": True,
        }



# ===========================================================
# 🔹 SCREEN HUD (HP, Reiatsu, Energía con dif dinámico)
# ===========================================================
screen battle_hp_overlay():
    zorder 80
    modal False

    if not hud_visible:
        null
    else:

        if hp_flash_timer > 0:
            $ hp_flash_timer -= 1

        # ======================================================
        # ⚔️ HUD DE UNIDADES
        # ======================================================
        if ui_show_unit_hud:
            if hasattr(store, "bs_unit_key") and hasattr(store, "bs_get_unit_by_key"):
                $ _ctx_u = store.bs_get_turn_ctx() if hasattr(store, "bs_get_turn_ctx") else {"owner_team": "player", "owner_slot": 0}
                $ _pcount_hud = hud_ai_team_count("player")
                $ _ecount_hud = hud_ai_team_count("enemy")
                $ _mode_tag = str(getattr(store, "battle_team_mode", "1v1") or "1v1")
                $ _hud_layout = hud_ai_layout_profile(_mode_tag, _pcount_hud, _ecount_hud)
                fixed:
                    xfill True
                    yfit True
                    for _team in ["player", "enemy"]:
                        $ _team_count = _pcount_hud if _team == "player" else _ecount_hud
                        $ _side_align = 0.02 if _team == "player" else 0.98
                        $ _side_anchor = 0.0 if _team == "player" else 1.0
                        hbox:
                            xalign _side_align
                            xanchor _side_anchor
                            yalign 0.0
                            spacing int(_hud_layout.get("root_spacing", 14) or 14)
                            for i in range(_team_count):
                                $ _uk = store.bs_unit_key(_team, i)
                                $ _uu = store.bs_get_unit_by_key(_uk)
                                $ _res = store.bs_get_unit_resources(_uk) if hasattr(store, "bs_get_unit_resources") else {"reiatsu":0,"energy":0}
                                $ _name = hud_ai_resolve_unit_name(_team, i, _uu)
                                $ _hp = int((_uu.get("hp", 0) if isinstance(_uu, dict) else 0) or 0)
                                $ _mx = int((_uu.get("max_hp", 1) if isinstance(_uu, dict) else 1) or 1)
                                $ _active = bool(str(_ctx_u.get("owner_team", "")) == _team and int(_ctx_u.get("owner_slot", 0) or 0) == i)
                                $ _is_autonomous_unit = hud_ai_is_autonomous_unit(_team, _uu)
                                $ _is_framed_unit = bool(_is_autonomous_unit or _team == "player")
                                $ _hud_style = hud_ai_get_style(_uk) if _is_framed_unit else "grey"
                                $ _hud_mode = hud_ai_get_panel_mode(_uk) if _is_autonomous_unit else "stat"
                                $ _hud_collapsed = hud_ai_get_collapsed(_uk) if _is_framed_unit else False
                                $ _frame_path = hud_ai_resolve_frame(_hud_style, _hud_mode) or hud_ai_resolve_frame("grey", "stat")
                                $ _portrait_path = hud_ai_resolve_portrait_for_state(_name, _hud_collapsed, _hud_mode)
                                $ _icon_style = hud_ai_resolve_icon("icon_style_picker_arrow_gold") if _is_framed_unit else None
                                $ _icon_swap = hud_ai_resolve_icon("icon_panel_swap_blue") if _is_autonomous_unit else None
                                $ _icon_close = hud_ai_resolve_icon("icon_panel_close_red") if _is_framed_unit else None
                                $ _show_sim = bool(_team == "player" and _active and hasattr(store, "pending_tech_list") and store.pending_tech_list)
                                $ _rei_diff = int((simulated_reiatsu - player_reiatsu) if _show_sim else 0)
                                $ _ene_diff = int((simulated_energy - player_energy) if _show_sim else 0)
                                $ _safe_mode = bool(getattr(store, "ui_safe_mode", False))
                                if _is_framed_unit:
                                    if _hud_collapsed:
                                        button at hud_fade_in:
                                            action Function(hud_ai_toggle_collapsed, _uk)
                                            xsize int(_hud_layout.get("token_w", 118) or 118)
                                            ysize int(_hud_layout.get("token_h", 162) or 162)
                                            background Solid("#0008")
                                            if _portrait_path:
                                                add _portrait_path xpos 8 ypos 8 xsize int(max(52, int(_hud_layout.get("token_w", 118) or 118) - 16)) ysize 64
                                            else:
                                                text "{}".format(_name[:1]):
                                                    xalign 0.5
                                                    ypos 30
                                                    color "#FFFFFF"
                                                    size 28
                                                    bold True

                                            text "{}".format(_name):
                                                xpos 8
                                                ypos 76
                                                color "#88CCFF"
                                                size 10
                                                bold True

                                            text "HP: {}/{}".format(battle_fmt_num(_hp), battle_fmt_num(_mx)):
                                                xpos 8
                                                ypos 96
                                                color "#FFFFFF"
                                                size 8

                                            text "Rei: {}{}".format(
                                                battle_fmt_num(hud_ai_res_value(_res, "reiatsu")),
                                                " (-{})".format(battle_fmt_num(abs(_rei_diff))) if _rei_diff != 0 else ""
                                            ):
                                                xpos 8
                                                ypos 112
                                                color "#55FFFF"
                                                size 8

                                            text "Ene: {}{}".format(
                                                battle_fmt_num(hud_ai_res_value(_res, "energy")),
                                                " (-{})".format(battle_fmt_num(abs(_ene_diff))) if _ene_diff != 0 else ""
                                            ):
                                                xpos 8
                                                ypos 128
                                                color "#FFA500"
                                                size 8
                                    else:
                                        fixed at hud_fade_in:
                                            xsize int(_hud_layout.get("panel_w", 150) or 150)
                                            ysize int(_hud_layout.get("panel_h", 312) or 312)

                                            if _safe_mode:
                                                add Solid(hud_safe_panel_color(_hud_style)) xsize int(_hud_layout.get("panel_w", 150) or 150) ysize int(_hud_layout.get("panel_h", 312) or 312)
                                            elif _frame_path:
                                                add im.Scale(_frame_path, int(_hud_layout.get("panel_w", 150) or 150), int(_hud_layout.get("panel_h", 312) or 312)) xalign 0.5 yalign 0.5
                                            else:
                                                add Solid("#0008") xsize int(_hud_layout.get("panel_w", 150) or 150) ysize int(_hud_layout.get("panel_h", 312) or 312)

                                            if _hud_mode == "stat":
                                                if _portrait_path:
                                                    add _portrait_path xpos 16 ypos 18 xsize int(max(90, int(_hud_layout.get("panel_w", 150) or 150) - 32)) ysize int(max(120, int(_hud_layout.get("panel_h", 312) or 312) - 164))

                                                text "{}".format(_name):
                                                    xpos 18
                                                    ypos 170
                                                    color "#88CCFF"
                                                    size int((_hud_layout.get("name_size", 20) or 20) + 2)
                                                    bold True

                                                bar:
                                                    xpos 18
                                                    ypos 202
                                                    value (float(_hp) / max(1.0, float(_mx)))
                                                    range 1.0
                                                    xmaximum 112
                                                    ymaximum 14
                                                    left_bar "#00BFFF"
                                                    right_bar "#222222"

                                                text "{} / {}".format(battle_fmt_num(_hp), battle_fmt_num(_mx)):
                                                    xpos 18
                                                    ypos 229
                                                    color "#FFFFFF"
                                                    size int((_hud_layout.get("stat_size", 11) or 11) + 2)

                                                text "Reiatsu: {}{}".format(
                                                    battle_fmt_num(hud_ai_res_value(_res, "reiatsu")),
                                                    " (-{})".format(battle_fmt_num(abs(_rei_diff))) if _rei_diff != 0 else ""
                                                ):
                                                    xpos 18
                                                    ypos 247
                                                    color "#55FFFF"
                                                    size int((_hud_layout.get("stat_size", 11) or 11) + 2)

                                                text "Energía: {}{}".format(
                                                    battle_fmt_num(hud_ai_res_value(_res, "energy")),
                                                    " (-{})".format(battle_fmt_num(abs(_ene_diff))) if _ene_diff != 0 else ""
                                                ):
                                                    xpos 18
                                                    ypos 265
                                                    color "#FFA500"
                                                    size int((_hud_layout.get("stat_size", 11) or 11) + 2)
                                            else:
                                                text "{}".format(_name):
                                                    xpos 12
                                                    ypos 10
                                                    color "#88CCFF"
                                                    size int(max(13, int(_hud_layout.get("name_size", 20) or 20) - 3))
                                                    bold True

                                                vbox:
                                                    xpos 10
                                                    ypos 40
                                                    spacing 4

                                                    if _team == "enemy":
                                                        textbutton hud_safe_label_offense_force(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "offense_force")
                                                        textbutton hud_safe_label_offense_concat(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "offense_concat")
                                                        textbutton hud_safe_label_defense_force(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "defense_force")
                                                        textbutton hud_safe_label_defense_concat(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "defense_concat")
                                                        textbutton hud_safe_label_focus(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "focus")
                                                        textbutton hud_safe_label_target(_uk, _team):
                                                            xminimum int(max(118, int(_hud_layout.get("panel_w", 150) or 150) - 20))
                                                            text_size 10
                                                            action Function(hud_ai_option_cycle, _uk, _team, i, "target")
                                                    else:
                                                        text hud_safe_label_offense_force(_uk, _team) size 10 color "#F7C24D"
                                                        text hud_safe_label_offense_concat(_uk, _team) size 10 color "#66FF99"
                                                        text hud_safe_label_defense_force(_uk, _team) size 10 color "#6DBBFF"
                                                        text hud_safe_label_defense_concat(_uk, _team) size 10 color "#6DF0FF"
                                                        text hud_safe_label_focus(_uk, _team) size 10 color "#D68CFF"
                                                        text hud_safe_label_target(_uk, _team) size 10 color "#FFE15C"

                                            if _icon_style:
                                                imagebutton:
                                                    idle im.Scale(_icon_style, 28, 28)
                                                    hover im.Scale(_icon_style, 28, 28)
                                                    xpos 7
                                                    ypos 280
                                                    action Function(hud_ai_cycle_style, _uk)
                                            else:
                                                textbutton "<":
                                                    xpos 8
                                                    ypos 280
                                                    xsize 28
                                                    ysize 28
                                                    action Function(hud_ai_cycle_style, _uk)

                                            if _icon_swap:
                                                imagebutton:
                                                    idle im.Scale(_icon_swap, 34, 34)
                                                    hover im.Scale(_icon_swap, 34, 34)
                                                    xpos 112
                                                    ypos 277
                                                    action Function(hud_ai_toggle_panel_mode, _uk)
                                            elif _is_autonomous_unit:
                                                textbutton "S":
                                                    xpos 116
                                                    ypos 280
                                                    xsize 28
                                                    ysize 28
                                                    action Function(hud_ai_toggle_panel_mode, _uk)

                                            if _icon_close:
                                                imagebutton:
                                                    idle im.Scale(_icon_close, 30, 30)
                                                    hover im.Scale(_icon_close, 30, 30)
                                                    xpos 117
                                                    ypos 2
                                                    action Function(hud_ai_toggle_collapsed, _uk)
                                            else:
                                                textbutton "X":
                                                    xpos 121
                                                    ypos 6
                                                    xsize 24
                                                    ysize 24
                                                    action Function(hud_ai_toggle_collapsed, _uk)
                                else:
                                    fixed at hud_fade_in:
                                        xsize int(_hud_layout.get("panel_w", 150) or 150)
                                        ysize int(_hud_layout.get("panel_h", 312) or 312)

                                        if _frame_path:
                                            add im.Scale(_frame_path, int(_hud_layout.get("panel_w", 150) or 150), int(_hud_layout.get("panel_h", 312) or 312)) xalign 0.5 yalign 0.5
                                        else:
                                            add Solid("#0008") xsize int(_hud_layout.get("panel_w", 150) or 150) ysize int(_hud_layout.get("panel_h", 312) or 312)

                                        if _portrait_path:
                                            add _portrait_path xpos 16 ypos 18 xsize int(max(90, int(_hud_layout.get("panel_w", 150) or 150) - 32)) ysize int(max(120, int(_hud_layout.get("panel_h", 312) or 312) - 164))

                                        text "{}".format(_name):
                                            xpos 18
                                            ypos 173
                                            color "#88CCFF"
                                            size int(_hud_layout.get("name_size", 17) or 17)
                                            bold True

                                        bar:
                                            xpos 18
                                            ypos 203
                                            value (float(_hp) / max(1.0, float(_mx)))
                                            range 1.0
                                            xmaximum 112
                                            ymaximum 14
                                            left_bar "#00BFFF"
                                            right_bar "#222222"

                                        text "{} / {}".format(battle_fmt_num(_hp), battle_fmt_num(_mx)):
                                            xpos 18
                                            ypos 222
                                            color "#FFFFFF"
                                            size int(_hud_layout.get("stat_size", 9) or 9)

                                        text "Reiatsu: {}".format(battle_fmt_num(hud_ai_res_value(_res, "reiatsu"))):
                                            xpos 18
                                            ypos 240
                                            color "#55FFFF"
                                            size int(_hud_layout.get("stat_size", 9) or 9)

                                        text "Energía: {}".format(battle_fmt_num(hud_ai_res_value(_res, "energy"))):
                                            xpos 18
                                            ypos 258
                                            color "#FFA500"
                                            size int(_hud_layout.get("stat_size", 9) or 9)

                                        if _rei_diff != 0:
                                            text "-{}".format(battle_fmt_num(abs(_rei_diff))):
                                                xpos 104
                                                ypos 240
                                                size int(_hud_layout.get("stat_size", 9) or 9)
                                                color "#66CCFFAA"

                                        if _ene_diff != 0:
                                            text "-{}".format(battle_fmt_num(abs(_ene_diff))):
                                                xpos 104
                                                ypos 258
                                                size int(_hud_layout.get("stat_size", 9) or 9)
                                                color "#FFBB66AA"
            else:
                frame at hud_fade_in:
                    background "#0008"
                    xalign 0.0 yalign 0.0
                    xpadding 12 ypadding 8
                    vbox at hp_pulse_player:
                        spacing 2
                        text hud_player_name color "#88CCFF" size 22 bold True
                        bar:
                            value (float(battle_hp_player) / battle_hp_player_max)
                            range 1.0 xmaximum 280 ymaximum 16
                            left_bar "#00BFFF" right_bar "#222222"
                        text "{} / {}".format(battle_fmt_num(battle_hp_player), battle_fmt_num(battle_hp_player_max)) color "#FFFFFF" size 16

                        hbox:
                            spacing 6
                            text "Reiatsu: {}".format(battle_fmt_num(player_reiatsu)) size 15 color "#55FFFF"
                            $ _rei_diff_1v1 = (simulated_reiatsu - player_reiatsu) if (hasattr(store, "pending_tech_list") and store.pending_tech_list) else 0
                            if _rei_diff_1v1 != 0:
                                text "-{}".format(battle_fmt_num(abs(_rei_diff_1v1))) size 15 color "#66CCFFAA"

                        hbox:
                            spacing 6
                            text "Energía: {}".format(battle_fmt_num(player_energy)) size 15 color "#FFA500"
                            $ _ene_diff_1v1 = (simulated_energy - player_energy) if (hasattr(store, "pending_tech_list") and store.pending_tech_list) else 0
                            if _ene_diff_1v1 != 0:
                                text "-{}".format(battle_fmt_num(abs(_ene_diff_1v1))) size 15 color "#FFBB66AA"

                frame at hud_fade_in:
                    background "#0008"
                    xalign 1.0 yalign 0.0
                    xpadding 12 ypadding 8
                    vbox at hp_pulse_enemy:
                        spacing 2
                        text hud_enemy_name color "#FF7777" size 22 bold True
                        bar:
                            value (float(battle_hp_enemy) / battle_hp_enemy_max)
                            range 1.0 xmaximum 280 ymaximum 16
                            left_bar "#FF3333" right_bar "#222222"
                        text "{} / {}".format(battle_fmt_num(battle_hp_enemy), battle_fmt_num(battle_hp_enemy_max)) color "#FFFFFF" size 16
                        text "Reiatsu: {}".format(battle_fmt_num(enemy_reiatsu)) size 15 color "#55FFFF"
                        text "Energía: {}".format(battle_fmt_num(enemy_energy)) size 15 color "#FFA500"


        # ======================================================
        # 🧩 HUD 2v2 mínimo (slots + HP/KO + activo + turn owner)
        # ======================================================
        if ui_show_2v2_summary and str(getattr(store, "battle_team_mode", "1v1") or "1v1").strip().lower() == "2v2":
            $ _ctx = store.bs_get_turn_ctx() if hasattr(store, "bs_get_turn_ctx") else {"owner_team": "player", "owner_slot": 0}

            frame:
                background "#00131CCC"
                xalign 0.5
                yalign 0.0
                xpadding 10
                ypadding 8

                vbox:
                    spacing 4
                    text "2v2 · Turno: {} S{}".format(str(_ctx.get("owner_team", "player") or "player").upper(), int(_ctx.get("owner_slot", 0) or 0) + 1) color "#FFE082" size 15 bold True
                    text "Contador: T{}".format(int(getattr(store, "battle_turn_index", 0) or 0)) color "#B3E5FC" size 13
                    text "DEBUG actor={} defender={} idx={} order={}".format(
                        str(getattr(store, "current_actor_unit_key", "") or "-"),
                        str(getattr(store, "incoming_damage_target_key", "") or "-"),
                        int(getattr(store, "battle_turn_index", 0) or 0),
                        ",".join(getattr(store, "bs_get_turn_order_keys", lambda: [])() if hasattr(store, "bs_get_turn_order_keys") else []),
                    ) color "#80DEEA" size 11

                    $ _p1 = store.bs_get_unit_by_key(store.bs_unit_key("player", 0)) if hasattr(store, "bs_get_unit_by_key") and hasattr(store, "bs_unit_key") else None
                    $ _p2 = store.bs_get_unit_by_key(store.bs_unit_key("player", 1)) if hasattr(store, "bs_get_unit_by_key") and hasattr(store, "bs_unit_key") else None
                    $ _e1 = store.bs_get_unit_by_key(store.bs_unit_key("enemy", 0)) if hasattr(store, "bs_get_unit_by_key") and hasattr(store, "bs_unit_key") else None
                    $ _e2 = store.bs_get_unit_by_key(store.bs_unit_key("enemy", 1)) if hasattr(store, "bs_get_unit_by_key") and hasattr(store, "bs_unit_key") else None
                    $ _p1n = str((_p1.get("char_id", "P1") if isinstance(_p1, dict) else "P1") or "P1")
                    $ _p2n = str((_p2.get("char_id", "P2") if isinstance(_p2, dict) else "P2") or "P2")
                    $ _e1n = str((_e1.get("char_id", "E1") if isinstance(_e1, dict) else "E1") or "E1")
                    $ _e2n = str((_e2.get("char_id", "E2") if isinstance(_e2, dict) else "E2") or "E2")
                    $ _ord_parts = []
                    $ _ord_parts.append("1-{} (jugador)".format(_p1n))
                    $ _ord_parts.append("2-{} (ia)".format(_e1n))
                    if len(getattr(store, "battle_player_ids", []) or []) > 1:
                        $ _ord_parts.append("3-{} (jugador)".format(_p2n))
                    if len(getattr(store, "battle_enemy_ids", []) or []) > 1:
                        $ _ord_parts.append("4-{} (ia)".format(_e2n))
                    text "Orden: {}".format(", ".join(_ord_parts)) color "#C5E1A5" size 12
                    $ _ck = store.bs_current_actor_key() if hasattr(store, "bs_current_actor_key") else ""
                    $ _cinfo = store.bs_parse_unit_key(_ck, default_side="player", default_slot=0) if hasattr(store, "bs_parse_unit_key") else {"team":"player", "slot":0}
                    $ _cu = store.bs_get_unit_by_key(_ck) if hasattr(store, "bs_get_unit_by_key") else None
                    $ _cname = str((_cu.get("char_id", "Actor") if isinstance(_cu, dict) else "Actor") or "Actor")
                    $ _cteam = "PLAYER" if str(_cinfo.get("team", "player") or "player") == "player" else "ENEMY"
                    text "Turno actual: {} S{} · {}".format(_cname, int(_cinfo.get("slot", 0) or 0)+1, _cteam) color "#FFE082" size 13 bold True

                    hbox:
                        spacing 14

                        vbox:
                            spacing 2
                            text "PLAYER" color "#88CCFF" size 14 bold True
                            $ _pcount_dbg = min(2, max(1, len(getattr(store, "battle_player_ids", []) or [])))
                            for i in range(_pcount_dbg):
                                $ uk = store.bs_unit_key("player", i) if hasattr(store, "bs_unit_key") else "player:{}".format(i)
                                $ uu = store.bs_get_unit_by_key(uk) if hasattr(store, "bs_get_unit_by_key") else None
                                $ _name = str((uu.get("char_id", "P{}".format(i+1)) if isinstance(uu, dict) else "P{}".format(i+1)) or "P{}".format(i+1))
                                $ _hp = int((uu.get("hp", 0) if isinstance(uu, dict) else 0) or 0)
                                $ _mx = int((uu.get("max_hp", 1) if isinstance(uu, dict) else 1) or 1)
                                $ _alive = bool(_hp > 0)
                                $ _is_active = bool((_ctx.get("owner_team", "") == "player") and int(_ctx.get("owner_slot", 0) or 0) == i)
                                text "{} {} · S{} · {}/{}{}".format("▣" if _is_active else "▫", _name, i+1, battle_fmt_num(_hp), battle_fmt_num(_mx), " KO" if not _alive else "") color ("#66E0FF" if _alive else "#888888") size 13

                        vbox:
                            spacing 2
                            text "ENEMY" color "#FF7777" size 14 bold True
                            $ _ecount_dbg = min(2, max(1, len(getattr(store, "battle_enemy_ids", []) or [])))
                            for i in range(_ecount_dbg):
                                $ uk = store.bs_unit_key("enemy", i) if hasattr(store, "bs_unit_key") else "enemy:{}".format(i)
                                $ uu = store.bs_get_unit_by_key(uk) if hasattr(store, "bs_get_unit_by_key") else None
                                $ _name = str((uu.get("char_id", "E{}".format(i+1)) if isinstance(uu, dict) else "E{}".format(i+1)) or "E{}".format(i+1))
                                $ _hp = int((uu.get("hp", 0) if isinstance(uu, dict) else 0) or 0)
                                $ _mx = int((uu.get("max_hp", 1) if isinstance(uu, dict) else 1) or 1)
                                $ _alive = bool(_hp > 0)
                                $ _is_active = bool((_ctx.get("owner_team", "") == "enemy") and int(_ctx.get("owner_slot", 0) or 0) == i)
                                text "{} {} · S{} · {}/{}{}".format("▣" if _is_active else "▫", _name, i+1, battle_fmt_num(_hp), battle_fmt_num(_mx), " KO" if not _alive else "") color ("#FF8888" if _alive else "#888888") size 13


screen battle_ui_hotkeys():
    zorder 999
    modal False

    key "K_p" action ToggleField(store, "ui_show_options_panel")
    key "K_j" action ToggleField(store, "ui_show_unit_hud")
    key "K_v" action ToggleField(store, "ui_show_2v2_summary")
    key "K_o" action ToggleField(store, "ui_show_offensive_techniques")
    key "K_d" action ToggleField(store, "ui_show_defensive_techniques")


# ===========================================================
# 🔹 TRANSFORMS
# ===========================================================
transform hud_fade_in:
    alpha 0.0
    linear 0.35 alpha 1.0

transform hp_pulse_player:
    on show:
        linear 0.15 zoom 1.03
        linear 0.15 zoom 1.00

transform hp_pulse_enemy:
    on show:
        linear 0.15 zoom 1.03
        linear 0.15 zoom 1.00
