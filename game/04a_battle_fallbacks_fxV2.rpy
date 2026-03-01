# ===========================================================
# 04A_BATTLE_FALLBACKS_FX.RPY – Fallbacks seguros + FX utilitarios
# v2.22 StoreSafe + PopupDelay Sync (Ren'Py 7.4.9)
# -----------------------------------------------------------
# - Store-safe: no usa globals() para detectar funciones
# - battle_popup_turn: sincronizado con screen que maneja delay por timer
# - Helpers safe para restart_interaction
# - FX faseados y sincronizados
# ===========================================================

init -990 python:
    import renpy.store as S

    # -------------------------------------------------------
    # Helpers internos
    # -------------------------------------------------------
    def _safe_log(msg):
        try:
            renpy.log(str(msg))
        except:
            pass

    def _safe_restart_interaction():
        try:
            # En algunos momentos (transiciones), restart puede fallar o ser innecesario
            renpy.restart_interaction()
        except:
            pass

    def _ensure_noop(name, fn):
        """
        Si S.<name> no existe, lo define como fallback no-op.
        """
        if not hasattr(S, name):
            setattr(S, name, fn)

    # -------------------------------------------------------
    # Compat Ren'Py 7.4.x: side-image helper faltante
    # -------------------------------------------------------
    if not hasattr(renpy, "get_side_image"):
        def _compat_get_side_image(*args, **kwargs):
            return None
        renpy.get_side_image = _compat_get_side_image
        _safe_log("[Compat] injected renpy.get_side_image shim")

    # -------------------------------------------------------
    # Compat Ren'Py 7.4.x: wrappers UI en módulo renpy
    # -------------------------------------------------------
    try:
        _exp = getattr(renpy, "exports", None)
    except:
        _exp = None

    def _wire_renpy_fn(name):
        try:
            if callable(getattr(renpy, name, None)):
                return True
            if _exp and callable(getattr(_exp, name, None)):
                setattr(renpy, name, getattr(_exp, name))
                _safe_log("[Compat] wired renpy.{} from renpy.exports".format(name))
                return True
        except Exception as e:
            _safe_log("[Compat] failed wiring renpy.{}: {}".format(name, e))
        return False

    _wire_renpy_fn("get_screen")
    _wire_renpy_fn("show_screen")
    _wire_renpy_fn("hide_screen")
    _wire_renpy_fn("restart_interaction")
    _wire_renpy_fn("has_screen")

    # -------------------------------------------------------
    # Fallback: battle_popup_turn (bloque corto + hide explícito)
    # -------------------------------------------------------
    if not hasattr(S, "battle_popup_turn"):
        def battle_popup_turn(text, color="#FFD700", delay=0.8, glow=True):
            """
            Fallback seguro y autocontenido:
            - Muestra popup, espera breve y oculta explícitamente.
            - Evita pantallas "pegadas" si el screen no trae timer.
            """
            try:
                if renpy.has_screen("battle_popup_turn"):
                    renpy.show_screen("battle_popup_turn", text=text, color=color, glow=glow)
                    try:
                        renpy.pause(float(delay or 0.8), hard=True)
                    except:
                        renpy.pause(float(delay or 0.8))
                    renpy.hide_screen("battle_popup_turn")
                else:
                    _safe_log("[Fallback popup] {}".format(text))
            except Exception as e:
                _safe_log("battle_popup_turn fallback error: {}".format(e))

        S.battle_popup_turn = battle_popup_turn

    # -------------------------------------------------------
    # Fallbacks seguros (no-ops si falta algo)
    # -------------------------------------------------------
    _ensure_noop("battle_update_hp_bars", lambda player_hp, enemy_hp: None)
    _ensure_noop("battle_show_hud", lambda sync_fade=True: None)
    _ensure_noop("battle_hide_hud", lambda : None)
    _ensure_noop("battle_visual_float", lambda target="enemy", value=0, color="#FF4444": None)
    _ensure_noop("battle_visual_flash", lambda target="enemy", color="#FF5555": None)
    _ensure_noop("battle_camera_shake", lambda source="player": None)
    _ensure_noop("battle_glitch_effect", lambda : None)
    _ensure_noop("battle_motion_trail", lambda target="player": None)
    _ensure_noop("battle_clear_visual_fx", lambda : None)
    _ensure_noop("battle_save_turn_summary", lambda hits=0, damage=0: None)
    _ensure_noop("battle_clear_turn_summary", lambda : None)
    _ensure_noop("battle_set_atmosphere", lambda name="off": None)
    _ensure_noop("battle_flash_overlay", lambda color="#FFF", intensity=0.5: None)
    _ensure_noop("battle_update_damage_overlay", lambda player_hp, max_hp: None)
    _ensure_noop("battle_update_atmosphere_by_hp", lambda player_hp, enemy_hp: None)
    _ensure_noop("battle_turn_change", lambda owner="player": None)

    # battle_visual_on_attack: fallback útil
    if not hasattr(S, "battle_visual_on_attack"):
        def battle_visual_on_attack(target="enemy", damage=0):
            try:
                S.battle_visual_flash(target, "#FFFFFF")
            except:
                pass
        S.battle_visual_on_attack = battle_visual_on_attack

    # -------------------------------------------------------
    # FX utilitarios (faseados y sincronizados)
    # -------------------------------------------------------

    def fx_hit_red(value=0, color="#FF6666", intensity=0.32):
        """
        Fase 2: daño flotante + glitch + flash en simultáneo.
        El número aparece en el mismo frame que el glitch.
        """
        try:
            if int(value or 0) > 0:
                S.battle_visual_float("enemy", int(value), color)
            S.battle_flash_overlay("#FF2A2A", intensity)
            S.battle_visual_on_attack("enemy", 0)
            S.battle_glitch_effect()
            _safe_restart_interaction()
        except Exception as e:
            _safe_log("fx_hit_red error: {}".format(e))

    def fx_slash_strong():
        """
        Fase 3: impacto visual (slash/choque) previo a la baja de HP.
        """
        try:
            S.battle_visual_flash("enemy", "#FFAAAA")
            S.battle_motion_trail("player")
            S.battle_camera_shake("enemy")
            S.battle_flash_overlay("#FFFFFF", 0.22)
            renpy.pause(0.10, hard=True)
        except Exception as e:
            _safe_log("fx_slash_strong error: {}".format(e))

    def fx_apply_combo(color="#FFFFFF", intensity=0.45, snake=True, final_value=0):
        """
        Fase 4: resolución del combo (flash + snake + flotante final).
        """
        try:
            S.battle_flash_overlay(color, intensity)
            if snake:
                S.battle_glitch_effect()
                S.battle_camera_shake("enemy")
            renpy.pause(0.05, hard=True)

            if int(final_value or 0) > 0:
                S.battle_visual_float("enemy", int(final_value), color)
            _safe_restart_interaction()
        except Exception as e:
            _safe_log("fx_apply_combo error: {}".format(e))

    def fx_reflect_snake(intensity=0.35):
        """Reflejo sin ataques: snake suave azul-verde."""
        try:
            S.battle_flash_overlay("#55FFFF", intensity)
            S.battle_visual_on_attack("enemy", 0)
            S.battle_glitch_effect()
        except Exception as e:
            _safe_log("fx_reflect_snake error: {}".format(e))

    # Alias retrocompatibles
    fx_slash = fx_slash_strong

    # Exportar en store por consistencia (opcional pero útil)
    S.fx_hit_red = fx_hit_red
    S.fx_slash_strong = fx_slash_strong
    S.fx_apply_combo = fx_apply_combo
    S.fx_reflect_snake = fx_reflect_snake
    S.fx_slash = fx_slash
