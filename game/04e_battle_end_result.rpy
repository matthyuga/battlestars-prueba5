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

    # --- Limpieza global de efectos visuales y HUD ---
    if renpy.has_label("battle_hide_hud"):
        $ battle_hide_hud()
    if renpy.has_label("battle_clear_visual_fx"):
        $ battle_clear_visual_fx()
    $ battle_clear_turn_summary()

    if getattr(S, "story_mode_active", False) and renpy.has_label("story_phaseC_postbattle"):
        jump story_phaseC_postbattle

    # --- Retorno al menú principal ---
    $ renpy.full_restart()
    return


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
