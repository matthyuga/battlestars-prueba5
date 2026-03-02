# ===========================================================
# 06D_BATTLE_POPUP_TURN.RPY – Popup de Inicio / Turno
# ===========================================================
# v1.2 Silent Cinematic Sync Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Muestra textos tipo “¡Preparados!” / “¡Fight!” / “Turno enemigo”
# - Sin sonido (para uso en intros visuales)
# - Compatible con Core 1.95, HUD y FX activos
# ===========================================================

init -968 python:
    import renpy.store as S

    def _ui_call_safe(primary_name, export_name, *args, **kwargs):
        """Gateway runtime-safe para APIs UI (store -> renpy -> exports)."""
        try:
            fn_primary = getattr(S, primary_name, None)
            if callable(fn_primary):
                return fn_primary(*args, **kwargs)
        except Exception:
            pass

        try:
            fn = getattr(renpy, export_name, None)
            if callable(fn):
                return fn(*args, **kwargs)
        except Exception:
            pass

        try:
            exp = getattr(renpy, "exports", None)
            fn_exp = getattr(exp, export_name, None) if exp else None
            if callable(fn_exp):
                return fn_exp(*args, **kwargs)
        except Exception:
            pass

        return None

    # -------------------------------------------------------
    # 🔹 Popup animado (sin sonido)
    # -------------------------------------------------------
    def battle_popup_turn(text, color="#FFD700", delay=0.8):
        """
        Muestra un mensaje central animado.
        Puede usarse para '¡Preparados!', '¡Fight!' o avisos de turno.
        """
        try:
            _ui_call_safe("ui_show_screen_safe", "show_screen", "battle_popup_turn", text=text, color=color)
            renpy.pause(delay)
            _ui_call_safe("ui_hide_screen_safe", "hide_screen", "battle_popup_turn")
        except Exception as e:
            renpy.log("battle_popup_turn error: {}".format(e))


    def bs_show_incoming_notice(text, color="#00BFFF", delay=0.85, hard=True):
        """
        Aviso unificado de daño entrante para 1v1/2v2.
        Retorna True si se intentó mostrar sin error.
        """
        try:
            _ui_call_safe("ui_show_screen_safe", "show_screen", "battle_popup_turn", text=text, color=color)
            try:
                renpy.pause(float(delay or 0.85), hard=bool(hard))
            except:
                renpy.pause(float(delay or 0.85))
            _ui_call_safe("ui_hide_screen_safe", "hide_screen", "battle_popup_turn")
            return True
        except Exception as e:
            try:
                renpy.log("bs_show_incoming_notice error: {}".format(e))
            except:
                pass
            try:
                battle_popup_turn(text, color=color, delay=delay)
                return True
            except:
                return False

    renpy.store.bs_show_incoming_notice = bs_show_incoming_notice


# -----------------------------------------------------------
# 🔹 SCREEN – Popup centrado cinematográfico
# -----------------------------------------------------------
screen battle_popup_turn(text="", color="#FFD700"):
    zorder 300
    modal False

    # Leve aura de fondo, mejora la visibilidad sin fade
    add Solid("#FFFFFF18") at popup_glow_aura

    text text:
        color color
        size 64
        bold True
        outlines [(4, "#FFFFFF40", 0, 0)]
        xalign 0.5
        yalign 0.5
        at popup_turn_anim


# -----------------------------------------------------------
# 🔹 ANIMACIÓN – Entrada / salida suave
# -----------------------------------------------------------
transform popup_turn_anim:
    alpha 0.0 zoom 0.7
    linear 0.25 alpha 1.0 zoom 1.0
    linear 0.35 alpha 1.0
    linear 0.25 alpha 0.0

transform popup_glow_aura:
    alpha 0.0 zoom 1.0
    linear 0.25 alpha 0.25 zoom 1.05
    linear 0.25 alpha 0.15 zoom 1.0
    repeat 2
