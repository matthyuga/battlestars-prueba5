# ===========================================================
# 06F_BATTLE_TURN_CHANGE.RPY – Indicador de Cambio de Turno
# ===========================================================
# v1.0 Silent Transition Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Muestra “Tu turno” / “Turno enemigo” con resplandor lateral
# - Sin sonido ni pausa dura
# - Compatible con HUD y Core actual
# ===========================================================

init -966 python:
    def battle_turn_change(owner="player"):
        """
        Muestra el efecto visual al cambiar de turno.
        owner puede ser 'player' o 'enemy'.
        También sincroniza Turn SSOT/legacy durante transición.
        """
        try:
            import renpy.store as S

            fn_set = getattr(S, "bs_set_turn_owner", None)
            fn_ctx = getattr(S, "bs_get_turn_ctx", None)
            fn_key = getattr(S, "bs_unit_key", None)

            owner = "enemy" if str(owner or "").strip().lower() == "enemy" else "player"
            if callable(fn_set):
                owner = fn_set(owner, mirror_legacy=True)
            else:
                # fallback mínimo legacy si facade aún no está cargado
                S.battle_turn_owner = owner

            ctx = fn_ctx() if callable(fn_ctx) else {"owner_team": owner, "owner_slot": 0}
            owner_team = str(ctx.get("owner_team", owner) or owner)
            owner_slot = int(ctx.get("owner_slot", 0) or 0)

            if callable(fn_key):
                S.current_actor_unit_key = str(fn_key(owner_team, owner_slot) or "")
                rival = "enemy" if owner_team == "player" else "player"
                S.current_enemy_unit_key = str(fn_key(rival, None) or "")

            team_mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            slot_txt = " [S{}]".format(owner_slot + 1) if team_mode == "2v2" else ""

            if owner_team == "player":
                renpy.show_screen("battle_turn_change", text="🔹 TU TURNO{}".format(slot_txt), color="#00BFFF", side="left")
            else:
                renpy.show_screen("battle_turn_change", text="🔻 TURNO ENEMIGO{}".format(slot_txt), color="#FF4444", side="right")
            renpy.pause(1.0)
            renpy.hide_screen("battle_turn_change")
        except Exception as e:
            renpy.log("battle_turn_change error: {}".format(e))


# -----------------------------------------------------------
# 🔹 SCREEN – Texto + resplandor lateral
# -----------------------------------------------------------
screen battle_turn_change(text="", color="#00BFFF", side="left"):
    zorder 310
    modal False

    if side == "left":
        add Solid(color + "22") xalign 0.0 yalign 0.5 at turn_flash_left
    else:
        add Solid(color + "22") xalign 1.0 yalign 0.5 at turn_flash_right

    text text:
        size 52
        bold True
        color color
        outlines [(3, "#FFFFFF40", 0, 0)]
        xalign 0.5
        yalign 0.5
        at turn_text_anim


# -----------------------------------------------------------
# 🔹 TRANSFORMS
# -----------------------------------------------------------
transform turn_text_anim:
    alpha 0.0 zoom 0.9
    linear 0.25 alpha 1.0 zoom 1.0
    linear 0.30 alpha 1.0
    linear 0.25 alpha 0.0

transform turn_flash_left:
    alpha 0.0 zoom 1.0 xanchor 0.0
    linear 0.25 alpha 0.3 xoffset 60
    linear 0.25 alpha 0.1 xoffset 0
    linear 0.25 alpha 0.0

transform turn_flash_right:
    alpha 0.0 zoom 1.0 xanchor 1.0
    linear 0.25 alpha 0.3 xoffset -60
    linear 0.25 alpha 0.1 xoffset 0
    linear 0.25 alpha 0.0
