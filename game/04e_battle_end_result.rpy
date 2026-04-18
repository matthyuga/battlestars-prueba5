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
            "player_hp": int(getattr(S, "player_hp", 0) or 0),
            "enemy_hp": int(getattr(S, "enemy_hp", 0) or 0),
            "repetition_count": int(getattr(S, "story_pilot_repetition_count", 1) or 1),
            "preset": str(getattr(S, "story_pilot_reward_preset", "medium_v2") or "medium_v2"),
            "multi_factor_enabled": bool(getattr(S, "story_pilot_multi_factor_enabled", True)),
            "hp_reward_multiplier": int(getattr(S, "story_pilot_hp_reward_multiplier", 1) or 1),
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

    if getattr(S, "story_mode_active", False) and renpy.has_label("story_phaseC_postbattle"):
        $ S.battle_active = False
        jump story_phaseC_postbattle

    # --- Retorno al lobby (fase 3 UX v2) ---
    $ S.battle_active = False
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

            text "sim_id=[_sim_id]  |  mode=[_sim_mode]  |  winner=[_sim_winner]" size 20 color "#CFE8FF"
            text "Aplicación: ok=[_ap_ok]  |  count=[_ap_count]  |  EXP=[_ap_exp]  |  Oro=[_ap_oro]" size 20 color "#A6FFCC"
            text "Audit: warnings=[_warnings_count]  |  errors=[_errors_count]" size 18 color "#FFD27A"

            frame:
                xfill True
                yfill True
                padding (12, 10)

                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"

                    vbox:
                        spacing 8

                        for rr in _rows:
                            $ _ff = rr.get("final", {}) if isinstance(rr.get("final", {}), dict) else {}
                            $ _actor = rr.get("actor_id", "unknown")
                            $ _out = rr.get("outcome", "unknown")
                            $ _exp = _ff.get("exp_gain", 0)
                            $ _oro = _ff.get("oro_gain", 0)
                            $ _eligible = rr.get("eligible", False)
                            text "[_actor] | outcome=[_out] | eligible=[_eligible] | EXP +[_exp] | Oro +[_oro]" size 20 color "#FFFFFF"

                        if len(_rows) == 0:
                            text "Sin filas de resultado para mostrar." size 20 color "#FFAAAA"

                        if len(_warnings) > 0:
                            text "Warnings:" size 20 color "#FFD27A"
                            for w in _warnings:
                                text " - [w]" size 18 color "#FFD27A"

                        if len(_errors) > 0:
                            text "Errores:" size 20 color "#FF8A8A"
                            for e in _errors:
                                text " - [e]" size 18 color "#FF8A8A"

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
