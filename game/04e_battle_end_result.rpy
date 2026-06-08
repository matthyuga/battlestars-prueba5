# ===========================================================
# 04E_BATTLE_END_RESULT.RPY – Fin del combate + popup resultado
# v2.5 NoRedFlash Stable Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Elimina el flash rojo y mantiene solo vibraciones
# - Limpieza total del HUD y FX
# - Corrige salto a battle_end
# ===========================================================

# ===========================================================
# 🔹 LABEL PRINCIPAL – Fin del combate
# ===========================================================
label battle_end:
    python:
        import renpy.store as S
        _player_defeated = False
        _enemy_defeated = False

        fn_team_def = getattr(S, "bs_is_team_defeated", None)
        if callable(fn_team_def):
            try:
                _player_defeated = bool(fn_team_def("player"))
                _enemy_defeated = bool(fn_team_def("enemy"))
            except:
                _player_defeated = (int(getattr(S, "player_hp", 0) or 0) <= 0)
                _enemy_defeated = (int(getattr(S, "enemy_hp", 0) or 0) <= 0)
        else:
            _player_defeated = (int(getattr(S, "player_hp", 0) or 0) <= 0)
            _enemy_defeated = (int(getattr(S, "enemy_hp", 0) or 0) <= 0)

    if _player_defeated and not _enemy_defeated:
        $ battle_set_atmosphere("void")
        $ battle_popup_turn("Has perdido…", "#FF5555", delay=0.9)
        "Has sido derrotada."
        $ S.story_pilot_last_result = "defeat"
    elif _enemy_defeated and not _player_defeated:
        $ battle_set_atmosphere("desert")
        $ battle_popup_turn("¡Victoria!", "#00FFAA", delay=0.9)
        "¡El enemigo ha sido eliminado!"
        $ S.story_pilot_last_result = "victory"
    elif _player_defeated and _enemy_defeated:
        $ battle_set_atmosphere("void")
        $ battle_popup_turn("Empate", "#CCCCCC", delay=0.9)
        "Ambos equipos han caído."
        $ S.story_pilot_last_result = "draw"
    else:
        "El combate ha terminado."
        $ S.story_pilot_last_result = "unknown"

    # --- C2: ejecutar simulador al cierre (sin aplicar todavía) ---
    python:
        import renpy.store as S

        # Estado base de runtime para el adaptador C1.
        runtime = {
            "source": "battle_end",
            "result": str(getattr(S, "story_pilot_last_result", "draw") or "draw"),
            "battle_id": str(getattr(S, "story_pilot_battle_id", "battle_runtime") or "battle_runtime"),
            "turn_index": int(getattr(S, "battle_turn_index", 0) or 0),
            "player_hp": int(getattr(S, "player_hp", 0) or 0),
            "enemy_hp": int(getattr(S, "enemy_hp", 0) or 0),
            "repetition_count": int(getattr(S, "story_pilot_repetition_count", 1) or 1),
            "preset": str(getattr(S, "story_pilot_reward_preset", "medium_v2") or "medium_v2"),
            "multi_factor_enabled": bool(getattr(S, "story_pilot_multi_factor_enabled", True)),
            "hp_reward_multiplier": int(getattr(S, "story_pilot_hp_reward_multiplier", 1) or 1),
            "reward_condition_exp_mult": float(getattr(S, "story_pilot_reward_exp_mult", 1.0) or 1.0),
            "reward_condition_oro_mult": float(getattr(S, "story_pilot_reward_oro_mult", 1.0) or 1.0),
            "reward_condition_probability_mult": float(getattr(S, "story_pilot_reward_probability_mult", 1.0) or 1.0),
            "reward_condition_tags": list(getattr(S, "story_pilot_reward_condition_tags", []) or []),
            "base_exp_real": int(getattr(S, "story_pilot_reward_base_exp_real", 35) or 35),
            "base_oro_real": int(getattr(S, "story_pilot_reward_base_oro_real", 15) or 15),
            "step_exp_real": float(getattr(S, "story_pilot_reward_step_exp", 3.5) or 3.5),
            "step_oro_real": float(getattr(S, "story_pilot_reward_step_oro", 2.0) or 2.0),
            "idempotency_registry": getattr(S, "sim_idempotency_registry_v1", {}),
        }

        # Bridge opcional con panel RPG si existe estado persistente.
        st = getattr(S, "rpg_panel_state_v1", None)
        if isinstance(st, dict):
            p = st.get("player", {}) if isinstance(st.get("player", {}), dict) else {}
            runtime["player_level"] = int(p.get("level", getattr(S, "player_level", 1)) or 1)
            runtime["player_register"] = int(p.get("register", getattr(S, "player_register", 0)) or 0)
            runtime["player_exp"] = int(p.get("exp_current", getattr(S, "player_exp", 0)) or 0)
            runtime["player_exp_max"] = int(p.get("exp_max", getattr(S, "player_exp_max", 100)) or 100)
            runtime["player_oro"] = int(p.get("oro_current", getattr(S, "player_oro", 0)) or 0)
        else:
            runtime["player_level"] = int(getattr(S, "player_level", 1) or 1)
            runtime["player_register"] = int(getattr(S, "player_register", 0) or 0)
            runtime["player_exp"] = int(getattr(S, "player_exp", 0) or 0)
            runtime["player_exp_max"] = int(getattr(S, "player_exp_max", 100) or 100)
            runtime["player_oro"] = int(getattr(S, "player_oro", 0) or 0)

        # Enemigo v1 (fallback simple 1v1). En C3/C4 se amplía a equipos múltiples runtime.
        runtime["enemy_level"] = int(getattr(S, "enemy_level", 1) or 1)
        runtime["enemy_register"] = int(getattr(S, "enemy_register", 0) or 0)
        runtime["enemy_exp"] = int(getattr(S, "enemy_exp", 0) or 0)
        runtime["enemy_exp_max"] = int(getattr(S, "enemy_exp_max", 100) or 100)
        runtime["enemy_oro"] = int(getattr(S, "enemy_oro", 0) or 0)

        fn_sim = getattr(S, "sim_run_battle_end_simulation", None)
        if callable(fn_sim):
            pack = fn_sim(runtime=runtime)
            S.sim_battle_end_last_request_v1 = pack.get("request", {})
            S.sim_battle_end_last_result_v1 = pack.get("result", {})
            fn_persist = getattr(S, "sim_persist_simulation_artifacts", None)
            if callable(fn_persist):
                try:
                    S.sim_battle_end_last_persist_v1 = fn_persist(pack)
                except Exception as ex:
                    S.sim_battle_end_last_persist_v1 = {
                        "ok": False,
                        "error": "persist_exception: %s" % ex,
                    }
            else:
                S.sim_battle_end_last_persist_v1 = {
                    "ok": False,
                    "error": "sim_persist_simulation_artifacts no disponible en store.",
                }
            fn_apply = getattr(S, "sim_apply_simulation_rewards_to_runtime", None)
            if callable(fn_apply):
                try:
                    S.sim_battle_end_last_apply_v1 = fn_apply(pack)
                except Exception as ex:
                    S.sim_battle_end_last_apply_v1 = {
                        "ok": False,
                        "error": "apply_exception: %s" % ex,
                    }
            else:
                S.sim_battle_end_last_apply_v1 = {
                    "ok": False,
                    "error": "sim_apply_simulation_rewards_to_runtime no disponible en store.",
                }
        else:
            # Fallback seguro: sin crash, deja evidencia en audit-like.
            S.sim_battle_end_last_request_v1 = {}
            S.sim_battle_end_last_result_v1 = {
                "results": [],
                "audit": {
                    "warnings": [],
                    "errors": ["sim_run_battle_end_simulation no disponible en store."],
                    "sim_contract_version": "v1",
                },
            }
            S.sim_battle_end_last_persist_v1 = {
                "ok": False,
                "error": "sim_run_battle_end_simulation no disponible en store.",
            }
            S.sim_battle_end_last_apply_v1 = {
                "ok": False,
                "error": "sim_run_battle_end_simulation no disponible en store.",
            }

    if renpy.has_screen("sim_battle_end_reward_summary_v1"):
        $ _sim_result = getattr(S, "sim_battle_end_last_result_v1", {})
        $ _sim_apply = getattr(S, "sim_battle_end_last_apply_v1", {})
        call screen sim_battle_end_reward_summary_v1(_sim_result, _sim_apply)

    # --- Limpieza global de efectos visuales y HUD ---
    if renpy.has_label("battle_hide_hud"):
        $ battle_hide_hud()
    if renpy.has_label("battle_clear_visual_fx"):
        $ battle_clear_visual_fx()
    $ battle_clear_turn_summary()
    python:
        # Cierre defensivo de screens runtime de combate para evitar
        # "fugas" visuales al volver al lobby.
        _runtime_battle_screens = [
            "battle_log_screen",
            "ai_difficulty_hud",
            "ai_tuning_panel",
            "technique_selector",
            "battle_command_menu",
            "battle_maneuver_choice",
            "battle_damage_overlay",
            "battle_popup_turn",
            "battle_popup_turn_legacy_visual",
            "debug_battle_identity",
            "dice_roll_result",
            "dice_roll_result_multi",
            "sim_battle_end_reward_summary_v1",
        ]
        for _scr in _runtime_battle_screens:
            try:
                if renpy.has_screen(_scr) and renpy.get_screen(_scr):
                    renpy.hide_screen(_scr)
            except:
                pass
        try:
            S.ui_show_battle_finish_panel = False
            S.ai_tuning_panel_visible = False
            S.incoming_damage = 0
            S.incoming_damage_target_key = ""
            S.incoming_damage_source_key = ""
            S.incoming_damage_sources = []
            S.show_maneuver_choice = True
        except:
            pass

    $ _clear_damage_overlay = getattr(S, "battle_clear_damage_overlay", None)
    if callable(_clear_damage_overlay):
        $ _clear_damage_overlay()
    else:
        $ renpy.hide_screen("battle_damage_overlay")

    if getattr(S, "story_mode_active", False) and renpy.has_label("story_phaseC_postbattle"):
        $ S.battle_active = False
        $ _clear_damage_overlay = getattr(S, "battle_clear_damage_overlay", None)
        if callable(_clear_damage_overlay):
            $ _clear_damage_overlay()
        else:
            $ renpy.hide_screen("battle_damage_overlay")
        jump story_phaseC_postbattle

    # --- Retorno al lobby (fase 3 UX v2) ---
    $ S.battle_active = False
    $ _clear_damage_overlay = getattr(S, "battle_clear_damage_overlay", None)
    if callable(_clear_damage_overlay):
        $ _clear_damage_overlay()
    else:
        $ renpy.hide_screen("battle_damage_overlay")
    if renpy.has_label("bs_saga_lobby"):
        jump bs_saga_lobby
    else:
        $ renpy.full_restart()
        return


# ===========================================================
# 🔹 C4 - Resumen visual post-combate (simulador)
# ===========================================================
screen sim_battle_end_reward_summary_v1(sim_result=None, apply_report=None):
    modal True
    zorder 300

    default _sr = sim_result if isinstance(sim_result, dict) else {}
    default _ap = apply_report if isinstance(apply_report, dict) else {}
    default _audit = _sr.get("audit", {}) if isinstance(_sr.get("audit", {}), dict) else {}
    default _warnings = _audit.get("warnings", []) if isinstance(_audit.get("warnings", []), list) else []
    default _errors = _audit.get("errors", []) if isinstance(_audit.get("errors", []), list) else []
    default _warnings_count = len(_warnings)
    default _errors_count = len(_errors)
    default _rows = _sr.get("results", []) if isinstance(_sr.get("results", []), list) else []
    default _sim_id = _sr.get("simulation_id", "sim_unknown")
    default _sim_mode = _sr.get("mode", "custom")
    default _sim_winner = _sr.get("winner_team", "DRAW")
    default _ap_ok = _ap.get("ok", False)
    default _ap_count = _ap.get("applied_count", 0)
    default _ap_exp = _ap.get("total_exp", 0)
    default _ap_oro = _ap.get("total_oro", 0)
    default _show_tech = False
    default _show_all_rows = False

    python:
        _reward_rows = []
        _all_rows = []
        for _rr in _rows:
            if not isinstance(_rr, dict):
                continue
            _ff = _rr.get("final", {}) if isinstance(_rr.get("final", {}), dict) else {}
            _exp = int(_ff.get("exp_gain", 0) or 0)
            _oro = int(_ff.get("oro_gain", 0) or 0)
            _eligible = bool(_rr.get("eligible", False))
            _all_rows.append(_rr)
            if _eligible and (_exp > 0 or _oro > 0):
                _reward_rows.append(_rr)

        _visible_rows = list(_all_rows if _show_all_rows else _reward_rows)
        _main_row = _reward_rows[0] if len(_reward_rows) > 0 else None
        _main_final = _main_row.get("final", {}) if isinstance(_main_row, dict) and isinstance(_main_row.get("final", {}), dict) else {}
        _main_base = _main_row.get("base", {}) if isinstance(_main_row, dict) and isinstance(_main_row.get("base", {}), dict) else {}
        _main_mult = _main_row.get("multipliers", {}) if isinstance(_main_row, dict) and isinstance(_main_row.get("multipliers", {}), dict) else {}
        _main_actor = str(_main_row.get("actor_id", "player") or "player") if isinstance(_main_row, dict) else "player"
        _main_exp = int(_main_final.get("exp_gain", _ap_exp) or _ap_exp)
        _main_oro = int(_main_final.get("oro_gain", _ap_oro) or _ap_oro)
        _main_stars = int(_main_row.get("stars_total", 0) or 0) if isinstance(_main_row, dict) else 0
        _main_delta = int(_main_row.get("delta_register", 0) or 0) if isinstance(_main_row, dict) else 0
        _main_base_exp = int(_main_base.get("exp", 0) or 0)
        _main_base_oro = int(_main_base.get("oro", 0) or 0)
        _main_m_risk_exp = float(_main_mult.get("risk_exp", 1.0) or 1.0)
        _main_m_result_exp = float(_main_mult.get("result_exp", 1.0) or 1.0)
        _main_m_perf_exp = float(_main_mult.get("performance_exp", 1.0) or 1.0)
        _main_m_risk_oro = float(_main_mult.get("risk_oro", 1.0) or 1.0)
        _main_m_result_oro = float(_main_mult.get("result_oro", 1.0) or 1.0)
        _main_m_perf_oro = float(_main_mult.get("performance_oro", 1.0) or 1.0)
        _main_m_anti = float(_main_mult.get("antiabuso", 1.0) or 1.0)
        _main_m_multi = float(_main_mult.get("multi_factor", 1.0) or 1.0)
        _main_m_hp = int(_main_mult.get("hp_reward_multiplier", 1) or 1)
        _main_m_cond_exp = float(_main_mult.get("reward_condition_exp_mult", 1.0) or 1.0)
        _main_m_cond_oro = float(_main_mult.get("reward_condition_oro_mult", 1.0) or 1.0)
        _main_m_cond_prob = float(_main_mult.get("reward_condition_probability_mult", 1.0) or 1.0)

    add Solid("#000000AA")

    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 1220
        ymaximum 660
        padding (26, 22)

        vbox:
            spacing 12

            hbox:
                xfill True
                spacing 14
                text "Resumen de recompensas (C4)" size 34 color "#FFFFFF"
                null xfill True
                textbutton "▶ Continuar":
                    xalign 1.0
                    text_size 24
                    text_color "#FFFFFF"
                    left_padding 18
                    right_padding 18
                    top_padding 8
                    bottom_padding 8
                    background "#1E90FFFF"
                    hover_background "#39A4FFFF"
                    action Return(True)

            text "sim_id=[_sim_id]  |  mode=[_sim_mode]  |  winner=[_sim_winner]" size 18 color "#CFE8FF"

            hbox:
                spacing 12
                xfill True
                yfill True

                frame:
                    xsize 700
                    yfill True
                    padding (12, 10)
                    background Solid("#10263A")
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        vbox:
                            spacing 10
                            text "Recompensa obtenida" size 28 color "#FFFFFF"
                            text "Actor: [_main_actor]" size 18 color "#CFE8FF"
                            text "EXP +[_main_exp]  |  Oro +[_main_oro]" size 34 color "#A6FFCC"
                            text "Aplicación: ok=[_ap_ok]  |  count=[_ap_count]  |  EXP=[_ap_exp]  |  Oro=[_ap_oro]" size 17 color "#A6FFCC"
                            text "Resumen cálculo: Base -> Multiplicadores -> Resultado final" size 15 color "#9FC4E2"

                            if _main_row:
                                text "Parámetros de rendimiento" size 22 color "#D0E9FF"
                                text "Base: EXP [_main_base_exp] | Oro [_main_base_oro] | Stars [_main_stars] | ΔRegister [_main_delta]" size 16 color "#9FC4E2"
                                text "EXP: risk x[_main_m_risk_exp] | result x[_main_m_result_exp] | perf x[_main_m_perf_exp]" size 15 color "#9FC4E2"
                                text "Oro: risk x[_main_m_risk_oro] | result x[_main_m_result_oro] | perf x[_main_m_perf_oro]" size 15 color "#9FC4E2"
                                text "Globales: anti x[_main_m_anti] | multi x[_main_m_multi] | hp x[_main_m_hp]" size 15 color "#9FC4E2"
                                text "Condiciones: exp x[_main_m_cond_exp] | oro x[_main_m_cond_oro] | prob x[_main_m_cond_prob]" size 15 color "#9FC4E2"
                                text "Fórmula EXP: base_exp * risk_exp * result_exp * performance_exp * antiabuso * multi_factor * hp_reward_multiplier * reward_condition_exp_mult" size 13 color "#8CB8DB"
                                text "Fórmula Oro: base_oro * risk_oro * result_oro * performance_oro * antiabuso * multi_factor * hp_reward_multiplier * reward_condition_oro_mult" size 13 color "#8CB8DB"
                            elif _ap_count > 0 or _ap_exp > 0 or _ap_oro > 0:
                                text "Parámetros no disponibles en fila principal; se muestra agregado de aplicación." size 15 color "#FFD27A"
                            else:
                                text "No hay recompensas aplicadas para mostrar." size 17 color "#FFAAAA"

                frame:
                    xfill True
                    yfill True
                    padding (12, 10)
                    background Solid("#0E2030")
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        vbox:
                            spacing 9
                            text "Panel técnico / QA" size 22 color "#D0E9FF"
                            text "Audit: warnings=[_warnings_count]  |  errors=[_errors_count]" size 16 color "#FFD27A"
                            hbox:
                                spacing 8
                                textbutton ("Detalle técnico: " + ("ON" if _show_tech else "OFF")):
                                    action SetScreenVariable("_show_tech", not _show_tech)
                                textbutton ("Mostrar todos los actores: " + ("ON" if _show_all_rows else "OFF")):
                                    action SetScreenVariable("_show_all_rows", not _show_all_rows)

                            if len(_visible_rows) == 0:
                                text "Sin filas visibles (activa 'Mostrar todos los actores' para inspección completa)." size 15 color "#FFAAAA"

                            if _show_tech:
                                for rr in _visible_rows:
                                    $ _ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
                                    $ _actor = rr.get("actor_id", "unknown")
                                    $ _out = rr.get("outcome", "unknown")
                                    $ _exp = _ff.get("exp_gain", 0)
                                    $ _oro = _ff.get("oro_gain", 0)
                                    $ _eligible = rr.get("eligible", False)
                                    text "[_actor] | outcome=[_out] | eligible=[_eligible] | EXP +[_exp] | Oro +[_oro]" size 16 color "#FFFFFF"

                            if len(_warnings) > 0:
                                text "Warnings:" size 17 color "#FFD27A"
                                for w in _warnings:
                                    text " - [w]" size 15 color "#FFD27A"

                            if len(_errors) > 0:
                                text "Errores:" size 17 color "#FF8A8A"
                                for e in _errors:
                                    text " - [e]" size 15 color "#FF8A8A"

# ===========================================================
# 🔹 FUNCIÓN LOG RESULT – Resultado y popup de daño (sin flash rojo)
# ===========================================================
init python:
    def battle_log_result(name, damage, hp):
        """
        Registra los resultados del daño sin usar flash rojo.
        Mantiene vibración y popup.
        """
        try:
            if name == "Hollow":
                # 💥 Daño infligido al enemigo
                color = "#55FF99"
                popup_color = "#55FF99"
                popup_text = "{0} recibe {1} de daño".format(
                    name, battle_fmt_num(damage)
                )
                renpy.with_statement(vpunch)

            else:
                # 💢 Daño recibido por el jugador
                color = "#FF7777"
                popup_color = "#FF4444"
                popup_text = "{0} recibe {1} de daño".format(
                    name, battle_fmt_num(damage)
                )
                # 🔕 Flash rojo eliminado, mantiene vibración
                renpy.with_statement(hpunch)

            # 🧾 Registro en log
            battle_log_add(
                "[RESULTADO] {0} recibe {1} de daño (HP: {2})".format(
                    name,
                    battle_fmt_num(damage),
                    battle_fmt_num(hp),
                ),
                color,
            )

            # 💬 Popup visual con texto del daño
            battle_popup_turn(
                popup_text, color=popup_color, delay=0.7, glow=True
            )

        except Exception as e:
            renpy.log("⚠️ Error en battle_log_result: {}".format(e))
