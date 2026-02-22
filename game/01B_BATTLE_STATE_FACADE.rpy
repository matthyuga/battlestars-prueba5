# ===========================================================
# 01B_BATTLE_STATE_FACADE.RPY – HP Facade (Phase 1)
# ===========================================================
# Alcance:
# - Introduce store.battle_state mínimo (HP + MaxHP)
# - Helpers HP + sync legado
# - Sin tocar reflect/turn owner/lógica de combate
# ===========================================================

init -989 python:
    import renpy.store as S

    def _bs_to_int(v, default=0):
        try:
            return int(v)
        except:
            try:
                return int(default)
            except:
                return 0

    def _bs_warn(msg):
        try:
            fn = getattr(S, "debug_log", None)
            if callable(fn):
                fn(msg)
                return
        except:
            pass

        try:
            import renpy
            renpy.log("[BS_HP_FACADE] " + str(msg))
        except:
            pass

    def _bs_side_key(side):
        s = str(side or "").strip().lower()
        if s in ("player", "actor"):
            return "player"
        if s in ("enemy",):
            return "enemy"

        _bs_warn("_bs_side_key inválido: {!r}; fallback='player'".format(side))
        return "player"

    def _bs_legacy_hp(side):
        if side == "player":
            return _bs_to_int(getattr(S, "player_hp", 0), 0)
        return _bs_to_int(getattr(S, "enemy_hp", 0), 0)

    def _bs_legacy_max_hp(side):
        if side == "player":
            v = getattr(S, "battle_hp_player_max", None)
            if v is None:
                v = getattr(S, "player_hp", 1)
            return max(1, _bs_to_int(v, 1))

        v = getattr(S, "battle_hp_enemy_max", None)
        if v is None:
            v = getattr(S, "enemy_hp", 1)
        return max(1, _bs_to_int(v, 1))

    def battle_state_ensure():
        bs = getattr(S, "battle_state", None)
        if not isinstance(bs, dict):
            bs = {}

        bs["version"] = 1

        units = bs.get("units")
        if not isinstance(units, dict):
            units = {}

        for side in ("player", "enemy"):
            u = units.get(side)
            if not isinstance(u, dict):
                u = {}

            hp = _bs_to_int(u.get("hp", _bs_legacy_hp(side)), _bs_legacy_hp(side))
            mx = _bs_to_int(u.get("max_hp", _bs_legacy_max_hp(side)), _bs_legacy_max_hp(side))
            mx = max(1, mx)
            hp = max(0, min(hp, mx))

            u["hp"] = hp
            u["max_hp"] = mx
            units[side] = u

        bs["units"] = units

        dp = bs.get("direct_pending")
        if not isinstance(dp, dict):
            dp = {}
        dp["player"] = max(0, _bs_to_int(dp.get("player", 0), 0))
        dp["enemy"] = max(0, _bs_to_int(dp.get("enemy", 0), 0))
        bs["direct_pending"] = dp

        S.battle_state = bs
        return bs

    def bs_hp(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        return _bs_to_int(bs.get("units", {}).get(side, {}).get("hp", 0), 0)

    def bs_max_hp(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        return max(1, _bs_to_int(bs.get("units", {}).get(side, {}).get("max_hp", 1), 1))

    def bs_set_hp(side, value):
        side = _bs_side_key(side)
        bs = battle_state_ensure()

        hp = _bs_to_int(value, 0)
        mx = bs_max_hp(side)
        hp = max(0, min(hp, mx))

        bs["units"][side]["hp"] = hp
        S.battle_state = bs
        return hp

    def bs_set_max_hp(side, value, keep_ratio=False):
        side = _bs_side_key(side)
        bs = battle_state_ensure()

        old_max = bs_max_hp(side)
        old_hp = bs_hp(side)
        new_max = max(1, _bs_to_int(value, old_max))

        if keep_ratio:
            ratio = 0.0
            try:
                ratio = float(old_hp) / float(old_max or 1)
            except:
                ratio = 0.0
            new_hp = int(round(ratio * float(new_max)))
        else:
            new_hp = min(old_hp, new_max)

        new_hp = max(0, min(new_hp, new_max))

        bs["units"][side]["max_hp"] = new_max
        bs["units"][side]["hp"] = new_hp
        S.battle_state = bs
        return new_max

    def bs_apply_damage(target, dmg, source=None, reason=None):
        side = _bs_side_key(target)
        cur = bs_hp(side)

        try:
            dmg_i = int(dmg)
        except:
            dmg_i = 0
        if dmg_i < 0:
            dmg_i = 0

        nxt = max(0, cur - dmg_i)
        bs_set_hp(side, nxt)

        return {
            "target": side,
            "source": source,
            "reason": reason,
            "damage": dmg_i,
            "hp_before": cur,
            "hp_after": nxt,
            "died": (nxt <= 0 and cur > 0),
        }

    def bs_get_direct_pending(target):
        side = _bs_side_key(target)
        bs = battle_state_ensure()
        return max(0, _bs_to_int(bs.get("direct_pending", {}).get(side, 0), 0))

    def bs_set_direct_pending(target, value, mirror_legacy=True):
        side = _bs_side_key(target)
        bs = battle_state_ensure()
        v = max(0, _bs_to_int(value, 0))
        bs.setdefault("direct_pending", {})[side] = v
        S.battle_state = bs

        if mirror_legacy:
            try:
                if side == "player":
                    S.enemy_direct_pending_damage = v
                else:
                    S._last_player_direct_damage = v
            except:
                pass
        return v

    def bs_add_direct_pending(target, amount, mirror_legacy=True):
        side = _bs_side_key(target)
        cur = bs_get_direct_pending(side)
        inc = max(0, _bs_to_int(amount, 0))
        return bs_set_direct_pending(side, cur + inc, mirror_legacy=mirror_legacy)

    def bs_consume_direct_pending(target, mirror_legacy=True):
        side = _bs_side_key(target)
        cur = bs_get_direct_pending(side)
        bs_set_direct_pending(side, 0, mirror_legacy=mirror_legacy)
        return cur

    def bs_sync_from_legacy():
        bs = battle_state_ensure()

        for side in ("player", "enemy"):
            hp = _bs_legacy_hp(side)
            mx = _bs_legacy_max_hp(side)
            hp = max(0, min(hp, mx))

            bs["units"][side]["max_hp"] = mx
            bs["units"][side]["hp"] = hp

        S.battle_state = bs
        return bs

    def bs_sync_to_legacy():
        battle_state_ensure()

        p_hp = bs_hp("player")
        e_hp = bs_hp("enemy")
        p_max = bs_max_hp("player")
        e_max = bs_max_hp("enemy")

        # Canonical HP runtime
        S.player_hp = p_hp
        S.enemy_hp = e_hp

        # Max HP runtime usados por HUD/FX
        S.battle_hp_player_max = p_max
        S.battle_hp_enemy_max = e_max

        # Espejo legacy HUD
        S.battle_hp_player = p_hp
        S.battle_hp_enemy = e_hp

        # Sync visual centralizado (si existe)
        try:
            fn = getattr(S, "battle_update_hp_bars", None)
            if callable(fn):
                fn(p_hp, e_hp)
        except:
            pass

        return {
            "player": {"hp": p_hp, "max_hp": p_max},
            "enemy": {"hp": e_hp, "max_hp": e_max},
        }

    # -------------------------------------------------------
    # Legacy-friendly wrappers (API pública de transición)
    # -------------------------------------------------------
    def bs_get_hp(actor):
        return bs_hp(actor)

    def bs_get_hp_max(actor):
        return bs_max_hp(actor)

    def bs_set_hp_legacy(actor, value):
        return bs_set_hp(actor, value)

    def bs_sync_hp_ui():
        return bs_sync_to_legacy()

    S.battle_state_ensure = battle_state_ensure
    S.bs_hp = bs_hp
    S.bs_max_hp = bs_max_hp
    S.bs_set_hp = bs_set_hp
    S.bs_set_max_hp = bs_set_max_hp
    S.bs_apply_damage = bs_apply_damage
    S.bs_get_direct_pending = bs_get_direct_pending
    S.bs_set_direct_pending = bs_set_direct_pending
    S.bs_add_direct_pending = bs_add_direct_pending
    S.bs_consume_direct_pending = bs_consume_direct_pending
    S.bs_sync_from_legacy = bs_sync_from_legacy
    S.bs_sync_to_legacy = bs_sync_to_legacy
    S.bs_get_hp = bs_get_hp
    S.bs_get_hp_max = bs_get_hp_max
    S.bs_set_hp_legacy = bs_set_hp_legacy
    S.bs_sync_hp_ui = bs_sync_hp_ui
