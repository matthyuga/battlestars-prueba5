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
            team_mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

            if team_mode == "2v2" and hasattr(S, "bs_current_actor_key") and callable(getattr(S, "bs_parse_unit_key", None)) and callable(getattr(S, "bs_set_turn_ctx", None)):
                actor_key = str(S.bs_current_actor_key() or "")
                info = S.bs_parse_unit_key(actor_key, default_side=owner, default_slot=0)
                owner_team = str(info.get("team", owner) or owner)
                owner_slot = int(info.get("slot", 0) or 0)
                S.bs_set_turn_ctx(owner_team=owner_team, owner_slot=owner_slot, phase="offensive", mirror_legacy=True)
                owner = owner_team
            else:
                if callable(fn_set):
                    owner = fn_set(owner, mirror_legacy=True)
                else:
                    # fallback mínimo legacy si facade aún no está cargado
                    S.battle_turn_owner = owner

                ctx = fn_ctx() if callable(fn_ctx) else {"owner_team": owner, "owner_slot": 0}
                owner_team = str(ctx.get("owner_team", owner) or owner)
                owner_slot = int(ctx.get("owner_slot", 0) or 0)

            fn_get = getattr(S, "bs_get_unit_by_key", None)
            actor_name = ""
            order_pos = 1
            _last_actor_key = str(getattr(S, "_last_turn_actor_key", "") or "")
            _cur_actor_key = ""
            if callable(fn_key):
                _cur_actor_key = str(fn_key(owner_team, owner_slot) or "")
            if _cur_actor_key and _cur_actor_key != _last_actor_key:
                turn_idx = int(getattr(S, "battle_turn_index", 0) or 0) + 1
                S.battle_turn_index = int(turn_idx)
                S._last_turn_actor_key = str(_cur_actor_key)
            else:
                turn_idx = int(getattr(S, "battle_turn_index", 0) or 0)

            if owner_team == "player":
                order_pos = (owner_slot * 2) + 1
            else:
                order_pos = (owner_slot * 2) + 2

            if callable(fn_key):
                S.current_actor_unit_key = str(fn_key(owner_team, owner_slot) or "")
                rival = "enemy" if owner_team == "player" else "player"
                rival_slot = None
                if team_mode == "2v2" and callable(getattr(S, "bs_get_active_slot", None)):
                    try:
                        rival_slot = int(S.bs_get_active_slot(rival) or 0)
                    except:
                        rival_slot = 0
                S.current_enemy_unit_key = str(fn_key(rival, rival_slot) or "")

                if callable(fn_get):
                    au = fn_get(getattr(S, "current_actor_unit_key", ""))
                    if isinstance(au, dict):
                        actor_name = str(au.get("char_id", "") or "")

            # Sincronizar recursos por unidad para HUD/selector
            try:
                fn_res = getattr(S, "bs_get_unit_resources", None)
                if callable(fn_res):
                    au_key = str(getattr(S, "current_actor_unit_key", "") or "")
                    rs = fn_res(au_key)
                    if owner_team == "player":
                        S.player_reiatsu = int(rs.get("reiatsu", getattr(S, "player_reiatsu", 0)) or 0)
                        S.player_energy = int(rs.get("energy", getattr(S, "player_energy", 0)) or 0)
                    else:
                        S.enemy_reiatsu = int(rs.get("reiatsu", getattr(S, "enemy_reiatsu", 0)) or 0)
                        S.enemy_energy = int(rs.get("energy", getattr(S, "enemy_energy", 0)) or 0)
            except:
                pass

            # Sincronizar HUD/legacy con unidades activas actuales
            try:
                fn_sync_hp = getattr(S, "bs_sync_to_legacy", None)
                if callable(fn_sync_hp):
                    fn_sync_hp()

                fn_get = getattr(S, "bs_get_unit_by_key", None)
                fn_char = getattr(S, "get_character", None)
                if callable(fn_get):
                    puk = str(fn_key("player", None) if callable(fn_key) else "")
                    euk = str(fn_key("enemy", None) if callable(fn_key) else "")
                    pu = fn_get(puk) if puk else None
                    eu = fn_get(euk) if euk else None

                    if isinstance(pu, dict):
                        pid = str(pu.get("char_id", getattr(S, "battle_player_id", "Harribel")) or "Harribel")
                        S.battle_player_id = pid
                        if callable(fn_char):
                            ch = fn_char(pid)
                            if isinstance(ch, dict):
                                S.battle_player = ch
                                S.hud_player_name = str(ch.get("name", pid) or pid)
                    if isinstance(eu, dict):
                        eid = str(eu.get("char_id", getattr(S, "battle_enemy_id", "Hollow")) or "Hollow")
                        S.battle_enemy_id = eid
                        if callable(fn_char):
                            ch = fn_char(eid)
                            if isinstance(ch, dict):
                                S.battle_enemy = ch
                                S.hud_enemy_name = str(ch.get("name", eid) or eid)
            except Exception as _e_sync:
                renpy.log("battle_turn_change sync warn: {}".format(_e_sync))

            slot_txt = " ({})".format(S.bs_slot_tag(owner_team, owner_slot) if callable(getattr(S, "bs_slot_tag", None)) else "S{}".format(owner_slot + 1)) if team_mode == "2v2" else ""

            if not actor_name:
                _disp = getattr(S, "bs_battle_display_name", None)
                if owner_team == "player":
                    _pid = str(getattr(S, "battle_player_id", "Jugador") or "Jugador")
                    actor_name = str(_disp(_pid, fallback=_pid) if callable(_disp) else _pid)
                else:
                    _eid = str(getattr(S, "battle_enemy_id", "Enemigo") or "Enemigo")
                    actor_name = str(_disp(_eid, fallback=_eid) if callable(_disp) else _eid)

            actor_team_txt = "PLAYER" if owner_team == "player" else "ENEMY"
            actor_full = "{}{} · {}".format(actor_name, slot_txt, actor_team_txt)

            if team_mode == "2v2":
                banner = u"T{} · #{} {}".format(turn_idx, order_pos, actor_full)
                try:
                    fn_log = getattr(S, "battle_log_add", None)
                    fn_get_u = getattr(S, "bs_get_unit_by_key", None)
                    hp_txt = ""
                    if callable(fn_get_u):
                        au = fn_get_u(getattr(S, "current_actor_unit_key", ""))
                        if isinstance(au, dict):
                            hp_txt = " HP {}/{}".format(int(au.get("hp", 0) or 0), int(au.get("max_hp", 0) or 0))
                    if callable(fn_log):
                        fn_log("{color=#FFE082}Turno {} | Orden {}: {} ({}){}{/color}".format(turn_idx, order_pos, actor_name, "jugador" if owner_team == "player" else "ia", hp_txt))
                except:
                    pass
            else:
                banner = u"T{} · {}".format(turn_idx, actor_name)

            try:
                fn_log = getattr(S, "battle_log_add", None)
                if callable(fn_log):
                    fn_log("{color=#80DEEA}[DEBUG] TURN_START actor_id=%s actor_name=%s team=%s{/color}" % (
                        str(getattr(S, "current_actor_unit_key", "") or ""),
                        str(actor_name or "?"),
                        str(owner_team or "?"),
                    ))
            except:
                pass

            if owner_team == "player":
                renpy.show_screen("battle_turn_change", text="🔹 TU TURNO · {}".format(banner), color="#00BFFF", side="left")
            else:
                renpy.show_screen("battle_turn_change", text="🔻 TURNO IA · {}".format(banner), color="#FF4444", side="right")
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
