# ===========================================================
# 01B_BATTLE_STATE_FACADE.RPY – Fachada mínima (B1-A.1)
# Ren'Py 7.4.9 compatible
# -----------------------------------------------------------
# Objetivo: helpers finos para acceso consistente a HP/MaxHP y
# sync UI, sin cambiar lógica existente (zero-risk).
# ===========================================================

init -980 python:
    import renpy.store as store

    # ---------------------------
    # HP (lógico)
    # ---------------------------
    def bs_get_hp(actor):
        """
        actor: 'player' | 'enemy'
        """
        if actor == "player":
            return int(getattr(store, "player_hp", 0) or 0)
        elif actor == "enemy":
            return int(getattr(store, "enemy_hp", 0) or 0)
        raise Exception("bs_get_hp: actor inválido: %r" % actor)

    def bs_set_hp(actor, value):
        """
        Setea HP lógico (no toca UI salvo que se llame bs_sync_hp_ui).
        """
        v = int(value or 0)
        if actor == "player":
            store.player_hp = v
        elif actor == "enemy":
            store.enemy_hp = v
        else:
            raise Exception("bs_set_hp: actor inválido: %r" % actor)
        return v

    def bs_get_hp_max(actor):
        """
        Lee máximos desde variables HUD actuales.
        """
        if actor == "player":
            return int(getattr(store, "battle_hp_player_max", 0) or 0)
        elif actor == "enemy":
            return int(getattr(store, "battle_hp_enemy_max", 0) or 0)
        raise Exception("bs_get_hp_max: actor inválido: %r" % actor)

    def bs_sync_hp_ui():
        """
        Sincroniza espejos HUD desde HP lógico.
        Mantiene compat: si existe battle_update_hp_bars, la llama.
        """
        try:
            store.battle_hp_player = bs_get_hp("player")
        except:
            store.battle_hp_player = int(getattr(store, "player_hp", 0) or 0)

        try:
            store.battle_hp_enemy = bs_get_hp("enemy")
        except:
            store.battle_hp_enemy = int(getattr(store, "enemy_hp", 0) or 0)

        # Si existe función de actualización de HUD, usarla
        try:
            fn = getattr(store, "battle_update_hp_bars", None)
            if fn:
                fn(store.battle_hp_player, store.battle_hp_enemy)
        except:
            pass

    # Export explícito en store (por si algún módulo no ve scope)
    store.bs_get_hp = bs_get_hp
    store.bs_set_hp = bs_set_hp
    store.bs_get_hp_max = bs_get_hp_max
    store.bs_sync_hp_ui = bs_sync_hp_ui