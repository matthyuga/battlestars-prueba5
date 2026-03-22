# ===========================================================
# 01B_BATTLE_STATE_FACADE.RPY – HP Facade (Phase 1)
# ===========================================================
# Alcance:
# - Introduce store.battle_state mínimo (HP + MaxHP)
# - Helpers HP + sync legado
# - Turn owner SSOT + mirrors legacy (Phase 1.1)
# ===========================================================

init -989 python:
    import renpy.store as S

    BS_RACE_COATING_MAP = {
        "shinigami": "reishi",
        "humano": "fullbring",
        "human": "fullbring",
        "quincy": "blut vene",
        "hollow": "hierro",
        "arrancar": "hierro",
        "infernal": "coraza",
        "ghoul": "aura",
        "guoul": "aura",
    }

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

    def _bs_log_battle_line(text, color=None):
        try:
            fn_safe = getattr(S, "safe_battle_log_add", None)
            if callable(fn_safe):
                if color is None:
                    fn_safe(str(text))
                else:
                    fn_safe(str(text), color=str(color))
                return
        except:
            pass

        try:
            fn_log = getattr(S, "battle_log_add", None)
            if callable(fn_log):
                if color is None:
                    fn_log(str(text))
                else:
                    fn_log(str(text), str(color))
                return
        except:
            pass

    def _bs_emit_stamina_shadow_log(
        stamina_before,
        incoming_after_coating,
        stamina_after,
        overflow_to_hp,
        hp_before,
        hp_after,
        stamina_gain,
        blocked_by_shadow,
    ):
        # 1) Resultado estamina (consumo / overflow)
        if overflow_to_hp > 0:
            _bs_log_battle_line("Estamina: {} - {} = -{}".format(int(stamina_before), int(incoming_after_coating), int(overflow_to_hp)))
        else:
            _bs_log_battle_line("Estamina: {} - {} = {}".format(int(stamina_before), int(incoming_after_coating), int(stamina_after)))

        # 2) Resultado HP
        _bs_log_battle_line("HP: {} - {} = {}".format(int(hp_before), int(overflow_to_hp), int(hp_after)))

        # 3) Generación de estamina (si aplica)
        if int(stamina_gain) > 0:
            _bs_log_battle_line("HP genera {} de estamina".format(int(stamina_gain)))

        # 4) Bloqueo por shadow (si limitó)
        if int(blocked_by_shadow) > 0:
            _bs_log_battle_line("Shadow bloquea {} de espacio para estamina".format(int(blocked_by_shadow)))

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

    def _bs_default_char_id(side):
        side = _bs_side_key(side)
        if side == "player":
            return str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
        return str(getattr(S, "battle_enemy_id", "Hollow") or "Hollow")

    def _bs_get_character_template(char_id):
        try:
            fn = getattr(S, "get_character", None)
            if callable(fn):
                c = fn(char_id)
                if isinstance(c, dict):
                    return dict(c)
        except:
            pass
        return {}

    def _bs_coating_type_for_race(race, fallback="fullbring"):
        rk = str(race or "").strip().lower()
        return str(BS_RACE_COATING_MAP.get(rk, fallback) or fallback)

    def _bs_with_coating_fields(unit, char_id=None):
        u = dict(unit) if isinstance(unit, dict) else {}
        cid = str(char_id or u.get("char_id", "") or "")
        ch = _bs_get_character_template(cid)

        race = str(u.get("race", ch.get("race", "human")) or "human").strip().lower()
        coating_type = str(u.get("coating_type", ch.get("coating_type", "")) or "").strip().lower()
        if not coating_type:
            coating_type = _bs_coating_type_for_race(race)

        cover = max(0, _bs_to_int(u.get("coating_cover", ch.get("coating_cover", 0)), 0))
        dura_max = max(0, _bs_to_int(u.get("coating_durability_max", u.get("coating_durability", ch.get("coating_durability", 0))), 0))
        dura_cur = max(0, _bs_to_int(u.get("coating_durability_current", dura_max), dura_max))
        if dura_cur > dura_max:
            dura_cur = dura_max

        active = bool(u.get("coating_active", True)) and dura_cur > 0 and cover > 0

        u["race"] = race
        u["coating_type"] = coating_type
        u["coating_cover"] = cover
        u["coating_durability_max"] = dura_max
        u["coating_durability_current"] = dura_cur
        u["coating_active"] = bool(active)
        return u

    def _bs_with_stamina_shadow_fields(unit):
        u = dict(unit) if isinstance(unit, dict) else {}

        hp = max(0, _bs_to_int(u.get("hp", 0), 0))
        mx = max(1, _bs_to_int(u.get("max_hp", 1), 1))
        missing_hp = max(0, mx - hp)

        st_cap = max(0, _bs_to_int(u.get("stamina_cap", mx), mx))
        sh_cap = max(0, _bs_to_int(u.get("shadow_cap", mx), mx))

        st_cur = max(0, _bs_to_int(u.get("stamina_current", 0), 0))
        sh_cur = max(0, _bs_to_int(u.get("shadow_current", 0), 0))
        st_cur = min(st_cur, st_cap)
        sh_cur = min(sh_cur, sh_cap)

        # Invariante espacial Fase 1:
        # stamina_current + shadow_current <= missing_hp
        total = st_cur + sh_cur
        if total > missing_hp:
            sh_cur = min(sh_cur, missing_hp)
            st_cur = min(st_cur, max(0, missing_hp - sh_cur))

        u["stamina_cap"] = st_cap
        u["shadow_cap"] = sh_cap
        u["stamina_current"] = st_cur
        u["shadow_current"] = sh_cur
        u["stamina_enabled"] = bool(u.get("stamina_enabled", False))
        u["shadow_active"] = bool(u.get("shadow_active", False))
        u["missing_hp"] = missing_hp
        u["free_space"] = max(0, missing_hp - st_cur - sh_cur)
        return u

    def _bs_sync_active_unit_from_units(bs, side):
        side = _bs_side_key(side)
        units = bs.setdefault("units", {})
        teams = bs.setdefault("teams", {})
        active = bs.setdefault("active", {})

        su = units.get(side) or {}
        hp = max(0, _bs_to_int(su.get("hp", _bs_legacy_hp(side)), _bs_legacy_hp(side)))
        mx = max(1, _bs_to_int(su.get("max_hp", _bs_legacy_max_hp(side)), _bs_legacy_max_hp(side)))
        if hp > mx:
            hp = mx

        team = teams.get(side)
        if not isinstance(team, list):
            team = []

        uid = str(active.get(side, "") or "").strip()
        idx = -1
        for i, unit in enumerate(team):
            if isinstance(unit, dict) and str(unit.get("uid", "") or "") == uid:
                idx = i
                break

        if idx < 0:
            idx = 0
            uid = "{}_1".format(side)
            if not team:
                team = [{
                    "uid": uid,
                    "char_id": _bs_default_char_id(side),
                    "hp": hp,
                    "max_hp": mx,
                    "alive": bool(hp > 0),
                }]
            else:
                u0 = team[0] if isinstance(team[0], dict) else {}
                uid = str(u0.get("uid", uid) or uid)
                team[0] = dict(u0)

        unit = dict(team[idx] if isinstance(team[idx], dict) else {})
        unit["uid"] = str(unit.get("uid", uid) or uid)
        unit["char_id"] = str(unit.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side))
        unit["max_hp"] = mx
        unit["hp"] = hp
        unit["alive"] = bool(hp > 0)
        unit = _bs_with_coating_fields(unit, unit.get("char_id", _bs_default_char_id(side)))
        unit = _bs_with_stamina_shadow_fields(unit)
        team[idx] = unit

        teams[side] = team
        active[side] = unit["uid"]
        units[side] = {
            "uid": unit["uid"],
            "char_id": unit["char_id"],
            "hp": hp,
            "max_hp": mx,
            "race": str(unit.get("race", "human") or "human"),
            "coating_type": str(unit.get("coating_type", "fullbring") or "fullbring"),
            "coating_cover": max(0, _bs_to_int(unit.get("coating_cover", 0), 0)),
            "coating_durability_max": max(0, _bs_to_int(unit.get("coating_durability_max", 0), 0)),
            "coating_durability_current": max(0, _bs_to_int(unit.get("coating_durability_current", 0), 0)),
            "coating_active": bool(unit.get("coating_active", False)),
            "stamina_current": max(0, _bs_to_int(unit.get("stamina_current", 0), 0)),
            "stamina_cap": max(0, _bs_to_int(unit.get("stamina_cap", mx), mx)),
            "stamina_enabled": bool(unit.get("stamina_enabled", False)),
            "shadow_current": max(0, _bs_to_int(unit.get("shadow_current", 0), 0)),
            "shadow_cap": max(0, _bs_to_int(unit.get("shadow_cap", mx), mx)),
            "shadow_active": bool(unit.get("shadow_active", False)),
            "missing_hp": max(0, _bs_to_int(unit.get("missing_hp", max(0, mx - hp)), max(0, mx - hp))),
            "free_space": max(0, _bs_to_int(unit.get("free_space", 0), 0)),
        }

        bs["teams"] = teams
        bs["active"] = active
        bs["units"] = units
        return bs

    def battle_state_ensure():
        bs = getattr(S, "battle_state", None)
        if not isinstance(bs, dict):
            bs = {}

        bs["version"] = 3

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
            u = _bs_with_coating_fields(u, u.get("char_id", _bs_default_char_id(side)))
            u = _bs_with_stamina_shadow_fields(u)
            units[side] = u

        bs["units"] = units

        teams = bs.get("teams")
        if not isinstance(teams, dict):
            teams = {}
        bs["teams"] = teams

        active = bs.get("active")
        if not isinstance(active, dict):
            active = {}
        bs["active"] = active

        for side in ("player", "enemy"):
            _bs_sync_active_unit_from_units(bs, side)

        dp = bs.get("direct_pending")
        if not isinstance(dp, dict):
            dp = {}
        dp["player"] = max(0, _bs_to_int(dp.get("player", 0), 0))
        dp["enemy"] = max(0, _bs_to_int(dp.get("enemy", 0), 0))
        bs["direct_pending"] = dp

        turn = bs.get("turn")
        if not isinstance(turn, dict):
            turn = {}

        owner = _bs_side_key(turn.get("owner", getattr(S, "battle_turn_owner", "player")))
        turn["owner"] = owner

        owner_team = _bs_side_key(turn.get("owner_team", owner))
        turn["owner_team"] = owner_team

        owner_slot = _bs_to_int(turn.get("owner_slot", 0), 0)
        if owner_slot < 0:
            owner_slot = 0
        turn["owner_slot"] = owner_slot

        phase = str(turn.get("phase", "offensive") or "offensive").strip().lower()
        if phase not in ("offensive", "defensive"):
            phase = "offensive"
        turn["phase"] = phase

        round_n = _bs_to_int(turn.get("round", 1), 1)
        if round_n < 1:
            round_n = 1
        turn["round"] = round_n

        bs["turn"] = turn

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
        _bs_sync_active_unit_from_units(bs, side)
        S.battle_state = bs

        # A4.2: si cayó la unidad activa, intentar avanzar al siguiente vivo.
        try:
            bs_ensure_active_progress(side)
        except:
            pass

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
        _bs_sync_active_unit_from_units(bs, side)
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
            _bs_sync_active_unit_from_units(bs, side)

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

    def bs_get_team(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        out = []
        for u in (bs.get("teams", {}).get(side, []) or []):
            if isinstance(u, dict):
                out.append(dict(u))
        return out

    def bs_get_active_unit(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        uid = str(bs.get("active", {}).get(side, "") or "")
        for u in (bs.get("teams", {}).get(side, []) or []):
            if isinstance(u, dict) and str(u.get("uid", "") or "") == uid:
                return dict(u)
        return None

    def _bs_get_char_resource(char_id, key, default=0):
        try:
            fn = getattr(S, "get_character", None)
            if callable(fn):
                ch = fn(str(char_id or ""))
                if isinstance(ch, dict):
                    if key in ch:
                        return max(0, _bs_to_int(ch.get(key, default), default))
                    alt = "Energy" if key == "Energía" else key
                    if alt in ch:
                        return max(0, _bs_to_int(ch.get(alt, default), default))
        except:
            pass
        return max(0, _bs_to_int(default, 0))

    def bs_ensure_unit_resources():
        bs = battle_state_ensure()
        teams = bs.get("teams", {}) if isinstance(bs.get("teams", {}), dict) else {}
        touched = False
        for side in ("player", "enemy"):
            arr = list(teams.get(side, []) or [])
            for i, u in enumerate(arr):
                if not isinstance(u, dict):
                    continue
                cid = str(u.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side))
                if "reiatsu" not in u:
                    u["reiatsu"] = _bs_get_char_resource(cid, "Reiatsu", 0)
                    touched = True
                if "energy" not in u:
                    u["energy"] = _bs_get_char_resource(cid, "Energy", _bs_get_char_resource(cid, "Energía", 0))
                    touched = True
                arr[i] = u
            teams[side] = arr
        if touched:
            bs["teams"] = teams
            S.battle_state = bs
        return bs

    def bs_get_unit_resources(unit_key):
        bs_ensure_unit_resources()
        info = bs_parse_unit_key(unit_key)
        side = info.get("team", "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        u = bs_get_unit_by_key(bs_unit_key(side, slot))
        if not isinstance(u, dict):
            return {"reiatsu": 0, "energy": 0}
        return {
            "reiatsu": max(0, _bs_to_int(u.get("reiatsu", 0), 0)),
            "energy": max(0, _bs_to_int(u.get("energy", 0), 0)),
        }

    def bs_set_unit_resources(unit_key, reiatsu=None, energy=None):
        bs = bs_ensure_unit_resources()
        info = bs_parse_unit_key(unit_key)
        side = info.get("team", "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        teams = bs.get("teams", {}) if isinstance(bs.get("teams", {}), dict) else {}
        arr = list(teams.get(side, []) or [])
        if slot >= len(arr) or not isinstance(arr[slot], dict):
            return {"ok": False, "reason": "invalid_unit", "reiatsu": 0, "energy": 0}

        u = dict(arr[slot])
        if reiatsu is not None:
            u["reiatsu"] = max(0, _bs_to_int(reiatsu, u.get("reiatsu", 0)))
        if energy is not None:
            u["energy"] = max(0, _bs_to_int(energy, u.get("energy", 0)))
        arr[slot] = u
        teams[side] = arr
        bs["teams"] = teams
        S.battle_state = bs

        return {
            "ok": True,
            "reason": "ok",
            "reiatsu": max(0, _bs_to_int(u.get("reiatsu", 0), 0)),
            "energy": max(0, _bs_to_int(u.get("energy", 0), 0)),
        }

    def bs_get_unit_stamina_shadow(unit_key):
        info = bs_parse_unit_key(unit_key)
        side = info.get("team", "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        u = bs_get_unit_by_key(bs_unit_key(side, slot))
        if not isinstance(u, dict):
            return {
                "ok": False,
                "reason": "invalid_unit",
                "stamina_current": 0,
                "stamina_cap": 0,
                "stamina_enabled": False,
                "shadow_current": 0,
                "shadow_cap": 0,
                "shadow_active": False,
                "missing_hp": 0,
                "free_space": 0,
            }

        uu = _bs_with_stamina_shadow_fields(u)
        return {
            "ok": True,
            "reason": "ok",
            "stamina_current": max(0, _bs_to_int(uu.get("stamina_current", 0), 0)),
            "stamina_cap": max(0, _bs_to_int(uu.get("stamina_cap", uu.get("max_hp", 1)), uu.get("max_hp", 1))),
            "stamina_enabled": bool(uu.get("stamina_enabled", False)),
            "shadow_current": max(0, _bs_to_int(uu.get("shadow_current", 0), 0)),
            "shadow_cap": max(0, _bs_to_int(uu.get("shadow_cap", uu.get("max_hp", 1)), uu.get("max_hp", 1))),
            "shadow_active": bool(uu.get("shadow_active", False)),
            "missing_hp": max(0, _bs_to_int(uu.get("missing_hp", 0), 0)),
            "free_space": max(0, _bs_to_int(uu.get("free_space", 0), 0)),
        }

    def bs_set_unit_stamina_shadow(
        unit_key,
        stamina_current=None,
        stamina_cap=None,
        stamina_enabled=None,
        shadow_current=None,
        shadow_cap=None,
        shadow_active=None,
    ):
        bs = battle_state_ensure()
        info = bs_parse_unit_key(unit_key)
        side = info.get("team", "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        teams = bs.get("teams", {}) if isinstance(bs.get("teams", {}), dict) else {}
        arr = list(teams.get(side, []) or [])
        if slot >= len(arr) or not isinstance(arr[slot], dict):
            return {"ok": False, "reason": "invalid_unit"}

        u = dict(arr[slot])
        if stamina_current is not None:
            u["stamina_current"] = max(0, _bs_to_int(stamina_current, u.get("stamina_current", 0)))
        if stamina_cap is not None:
            u["stamina_cap"] = max(0, _bs_to_int(stamina_cap, u.get("max_hp", 1)))
        if stamina_enabled is not None:
            u["stamina_enabled"] = bool(stamina_enabled)
        if shadow_current is not None:
            u["shadow_current"] = max(0, _bs_to_int(shadow_current, u.get("shadow_current", 0)))
        if shadow_cap is not None:
            u["shadow_cap"] = max(0, _bs_to_int(shadow_cap, u.get("max_hp", 1)))
        if shadow_active is not None:
            u["shadow_active"] = bool(shadow_active)

        u = _bs_with_stamina_shadow_fields(u)
        arr[slot] = u
        teams[side] = arr
        bs["teams"] = teams

        active_slot = bs_get_active_slot(side)
        if active_slot == slot:
            mirror = dict(bs.get("units", {}).get(side, {}) or {})
            mirror.update({
                "uid": str(u.get("uid", mirror.get("uid", "{}_{}".format(side, slot + 1))) or "{}_{}".format(side, slot + 1)),
                "char_id": str(u.get("char_id", mirror.get("char_id", _bs_default_char_id(side))) or _bs_default_char_id(side)),
                "hp": max(0, _bs_to_int(u.get("hp", mirror.get("hp", 0)), mirror.get("hp", 0))),
                "max_hp": max(1, _bs_to_int(u.get("max_hp", mirror.get("max_hp", 1)), mirror.get("max_hp", 1))),
                "stamina_current": max(0, _bs_to_int(u.get("stamina_current", 0), 0)),
                "stamina_cap": max(0, _bs_to_int(u.get("stamina_cap", u.get("max_hp", 1)), u.get("max_hp", 1))),
                "stamina_enabled": bool(u.get("stamina_enabled", False)),
                "shadow_current": max(0, _bs_to_int(u.get("shadow_current", 0), 0)),
                "shadow_cap": max(0, _bs_to_int(u.get("shadow_cap", u.get("max_hp", 1)), u.get("max_hp", 1))),
                "shadow_active": bool(u.get("shadow_active", False)),
            })
            bs.setdefault("units", {})[side] = _bs_with_stamina_shadow_fields(mirror)

        S.battle_state = bs
        out = bs_get_unit_stamina_shadow(bs_unit_key(side, slot))
        out["unit_key"] = bs_unit_key(side, slot)
        return out

    def bs_consume_unit_resources(unit_key, reiatsu_cost=0, energy_cost=0):
        bs = bs_ensure_unit_resources()
        info = bs_parse_unit_key(unit_key)
        side = info.get("team", "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        teams = bs.get("teams", {}) if isinstance(bs.get("teams", {}), dict) else {}
        arr = list(teams.get(side, []) or [])
        if slot >= len(arr) or not isinstance(arr[slot], dict):
            return {"reiatsu_spent": 0, "energy_spent": 0, "reiatsu_after": 0, "energy_after": 0}

        u = dict(arr[slot])
        cur_r = max(0, _bs_to_int(u.get("reiatsu", 0), 0))
        cur_e = max(0, _bs_to_int(u.get("energy", 0), 0))
        use_r = min(cur_r, max(0, _bs_to_int(reiatsu_cost, 0)))
        use_e = min(cur_e, max(0, _bs_to_int(energy_cost, 0)))
        u["reiatsu"] = cur_r - use_r
        u["energy"] = cur_e - use_e
        arr[slot] = u
        teams[side] = arr
        bs["teams"] = teams
        S.battle_state = bs
        return {"reiatsu_spent": use_r, "energy_spent": use_e, "reiatsu_after": u["reiatsu"], "energy_after": u["energy"]}

    def bs_init_single_teams(
        player_char_id=None,
        enemy_char_id=None,
        player_hp=None,
        player_max_hp=None,
        enemy_hp=None,
        enemy_max_hp=None,
        player_coating_cover=None,
        player_coating_durability=None,
        enemy_coating_cover=None,
        enemy_coating_durability=None,
    ):
        bs = battle_state_ensure()

        p_char = str(player_char_id or _bs_default_char_id("player"))
        e_char = str(enemy_char_id or _bs_default_char_id("enemy"))

        p_hp = max(0, _bs_to_int(player_hp, bs_hp("player")))
        p_mx = max(1, _bs_to_int(player_max_hp, bs_max_hp("player")))
        if p_hp > p_mx:
            p_hp = p_mx

        e_hp = max(0, _bs_to_int(enemy_hp, bs_hp("enemy")))
        e_mx = max(1, _bs_to_int(enemy_max_hp, bs_max_hp("enemy")))
        if e_hp > e_mx:
            e_hp = e_mx

        p_tpl = _bs_get_character_template(p_char)
        e_tpl = _bs_get_character_template(e_char)
        p_cover = _bs_to_int(player_coating_cover, p_tpl.get("coating_cover", 0))
        p_dura = _bs_to_int(player_coating_durability, p_tpl.get("coating_durability", 0))
        e_cover = _bs_to_int(enemy_coating_cover, e_tpl.get("coating_cover", 0))
        e_dura = _bs_to_int(enemy_coating_durability, e_tpl.get("coating_durability", 0))
        p_cover = max(0, p_cover)
        p_dura = max(0, p_dura)
        e_cover = max(0, e_cover)
        e_dura = max(0, e_dura)

        bs.setdefault("teams", {})["player"] = [{
            "uid": "player_1",
            "char_id": p_char,
            "hp": p_hp,
            "max_hp": p_mx,
            "alive": bool(p_hp > 0),
            "reiatsu": _bs_get_char_resource(p_char, "Reiatsu", getattr(S, "player_reiatsu", 0)),
            "energy": _bs_get_char_resource(p_char, "Energy", getattr(S, "player_energy", 0)),
            "stamina_current": 0,
            "stamina_cap": p_mx,
            "stamina_enabled": False,
            "shadow_current": 0,
            "shadow_cap": p_mx,
            "shadow_active": False,
            "coating_cover": p_cover,
            "coating_durability_current": p_dura,
            "coating_durability_max": p_dura,
        }]
        bs["teams"]["player"][0] = _bs_with_stamina_shadow_fields(bs["teams"]["player"][0])
        bs.setdefault("teams", {})["enemy"] = [{
            "uid": "enemy_1",
            "char_id": e_char,
            "hp": e_hp,
            "max_hp": e_mx,
            "alive": bool(e_hp > 0),
            "reiatsu": _bs_get_char_resource(e_char, "Reiatsu", getattr(S, "enemy_reiatsu", 0)),
            "energy": _bs_get_char_resource(e_char, "Energy", getattr(S, "enemy_energy", 0)),
            "stamina_current": 0,
            "stamina_cap": e_mx,
            "stamina_enabled": False,
            "shadow_current": 0,
            "shadow_cap": e_mx,
            "shadow_active": False,
            "coating_cover": e_cover,
            "coating_durability_current": e_dura,
            "coating_durability_max": e_dura,
        }]
        bs["teams"]["enemy"][0] = _bs_with_stamina_shadow_fields(bs["teams"]["enemy"][0])
        bs.setdefault("active", {})["player"] = "player_1"
        bs.setdefault("active", {})["enemy"] = "enemy_1"

        bs.setdefault("units", {})["player"] = {
            "uid": "player_1",
            "char_id": p_char,
            "hp": p_hp,
            "max_hp": p_mx,
            "coating_cover": p_cover,
            "coating_durability_current": p_dura,
            "coating_durability_max": p_dura,
        }
        bs["units"]["player"] = _bs_with_coating_fields(bs["units"]["player"], p_char)
        bs["units"]["player"] = _bs_with_stamina_shadow_fields(bs["units"]["player"])
        bs.setdefault("units", {})["enemy"] = {
            "uid": "enemy_1",
            "char_id": e_char,
            "hp": e_hp,
            "max_hp": e_mx,
            "coating_cover": e_cover,
            "coating_durability_current": e_dura,
            "coating_durability_max": e_dura,
        }
        bs["units"]["enemy"] = _bs_with_coating_fields(bs["units"]["enemy"], e_char)
        bs["units"]["enemy"] = _bs_with_stamina_shadow_fields(bs["units"]["enemy"])

        S.battle_state = bs
        return bs

    def bs_init_teams(player_units=None, enemy_units=None):
        bs = battle_state_ensure()

        def _normalize(side, units, fallback_char):
            out = []
            raw = list(units or [])
            if not raw:
                raw = [{"char_id": fallback_char}]

            for i, it in enumerate(raw[:2]):
                if isinstance(it, dict):
                    cid = str(it.get("char_id", fallback_char) or fallback_char)
                    hp_i = _bs_to_int(it.get("hp", _bs_legacy_hp(side)), _bs_legacy_hp(side))
                    mx_i = _bs_to_int(it.get("max_hp", _bs_legacy_max_hp(side)), _bs_legacy_max_hp(side))
                    rei_i = _bs_to_int(it.get("reiatsu", _bs_get_char_resource(cid, "Reiatsu", 0)), _bs_get_char_resource(cid, "Reiatsu", 0))
                    ene_i = _bs_to_int(it.get("energy", _bs_get_char_resource(cid, "Energy", _bs_get_char_resource(cid, "Energía", 0))), _bs_get_char_resource(cid, "Energy", _bs_get_char_resource(cid, "Energía", 0)))
                    st_i = _bs_to_int(it.get("stamina_current", 0), 0)
                    st_cap_i = _bs_to_int(it.get("stamina_cap", mx_i), mx_i)
                    st_enabled_i = bool(it.get("stamina_enabled", False))
                    sh_i = _bs_to_int(it.get("shadow_current", 0), 0)
                    sh_cap_i = _bs_to_int(it.get("shadow_cap", mx_i), mx_i)
                    sh_active_i = bool(it.get("shadow_active", False))
                else:
                    cid = str(it or fallback_char)
                    hp_i = _bs_legacy_hp(side)
                    mx_i = _bs_legacy_max_hp(side)
                    rei_i = _bs_get_char_resource(cid, "Reiatsu", 0)
                    ene_i = _bs_get_char_resource(cid, "Energy", _bs_get_char_resource(cid, "Energía", 0))
                    st_i = 0
                    st_cap_i = mx_i
                    st_enabled_i = False
                    sh_i = 0
                    sh_cap_i = mx_i
                    sh_active_i = False

                mx_i = max(1, mx_i)
                hp_i = max(0, min(hp_i, mx_i))

                out.append({
                    "uid": "{}_{}".format(side, i + 1),
                    "char_id": cid,
                    "hp": hp_i,
                    "max_hp": mx_i,
                    "alive": bool(hp_i > 0),
                    "reiatsu": max(0, _bs_to_int(rei_i, 0)),
                    "energy": max(0, _bs_to_int(ene_i, 0)),
                    "stamina_current": max(0, _bs_to_int(st_i, 0)),
                    "stamina_cap": max(0, _bs_to_int(st_cap_i, mx_i)),
                    "stamina_enabled": bool(st_enabled_i),
                    "shadow_current": max(0, _bs_to_int(sh_i, 0)),
                    "shadow_cap": max(0, _bs_to_int(sh_cap_i, mx_i)),
                    "shadow_active": bool(sh_active_i),
                })
                out[-1] = _bs_with_coating_fields(out[-1], cid)
                out[-1] = _bs_with_stamina_shadow_fields(out[-1])

            while len(out) < 2:
                i = len(out)
                out.append({
                    "uid": "{}_{}".format(side, i + 1),
                    "char_id": str(fallback_char),
                    "hp": 0,
                    "max_hp": max(1, _bs_legacy_max_hp(side)),
                    "alive": False,
                    "stamina_current": 0,
                    "stamina_cap": max(1, _bs_legacy_max_hp(side)),
                    "stamina_enabled": False,
                    "shadow_current": 0,
                    "shadow_cap": max(1, _bs_legacy_max_hp(side)),
                    "shadow_active": False,
                })
                out[-1] = _bs_with_coating_fields(out[-1], str(fallback_char))
                out[-1] = _bs_with_stamina_shadow_fields(out[-1])
            return out

        p_fallback = _bs_default_char_id("player")
        e_fallback = _bs_default_char_id("enemy")

        p_team = _normalize("player", player_units, p_fallback)
        e_team = _normalize("enemy", enemy_units, e_fallback)

        bs.setdefault("teams", {})["player"] = p_team
        bs.setdefault("teams", {})["enemy"] = e_team

        def _first_alive_slot(team):
            for i, u in enumerate(team):
                if isinstance(u, dict) and max(0, _bs_to_int(u.get("hp", 0), 0)) > 0:
                    return i
            return 0

        p_slot = _first_alive_slot(p_team)
        e_slot = _first_alive_slot(e_team)

        bs.setdefault("active", {})["player"] = str(p_team[p_slot].get("uid", "player_1"))
        bs.setdefault("active", {})["enemy"] = str(e_team[e_slot].get("uid", "enemy_1"))

        p_u = p_team[p_slot]
        e_u = e_team[e_slot]
        bs.setdefault("units", {})["player"] = {
            "uid": str(p_u.get("uid", "player_1")),
            "char_id": str(p_u.get("char_id", p_fallback) or p_fallback),
            "hp": max(0, _bs_to_int(p_u.get("hp", 0), 0)),
            "max_hp": max(1, _bs_to_int(p_u.get("max_hp", 1), 1)),
        }
        bs["units"]["player"] = _bs_with_coating_fields(bs["units"]["player"], bs["units"]["player"].get("char_id", p_fallback))
        bs["units"]["player"] = _bs_with_stamina_shadow_fields(bs["units"]["player"])
        bs.setdefault("units", {})["enemy"] = {
            "uid": str(e_u.get("uid", "enemy_1")),
            "char_id": str(e_u.get("char_id", e_fallback) or e_fallback),
            "hp": max(0, _bs_to_int(e_u.get("hp", 0), 0)),
            "max_hp": max(1, _bs_to_int(e_u.get("max_hp", 1), 1)),
        }
        bs["units"]["enemy"] = _bs_with_coating_fields(bs["units"]["enemy"], bs["units"]["enemy"].get("char_id", e_fallback))
        bs["units"]["enemy"] = _bs_with_stamina_shadow_fields(bs["units"]["enemy"])

        bs.setdefault("turn", {})["scheduler"] = "round_robin_slots"
        bs.setdefault("turn", {})["rr_last_slot"] = {"player": -1, "enemy": -1}
        bs.setdefault("turn", {})["order_keys"] = ["player:0", "enemy:0", "player:1", "enemy:1"]
        bs.setdefault("turn", {})["order_index"] = 0
        bs.setdefault("turn", {})["current_actor_key"] = "player:0"

        S.battle_state = bs
        return bs

    def bs_get_active_slot(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        uid = str(bs.get("active", {}).get(side, "") or "")
        team = bs.get("teams", {}).get(side, []) or []
        for i, u in enumerate(team):
            if isinstance(u, dict) and str(u.get("uid", "") or "") == uid:
                return i
        return 0

    def bs_unit_key(side, slot=None):
        team = _bs_side_key(side)
        idx = bs_get_active_slot(team) if slot is None else _bs_to_int(slot, bs_get_active_slot(team))
        if idx < 0:
            idx = 0
        return "{}:{}".format(team, idx)

    def bs_parse_unit_key(key, default_side="player", default_slot=0):
        d_side = _bs_side_key(default_side)
        d_slot = _bs_to_int(default_slot, 0)
        if d_slot < 0:
            d_slot = 0

        if isinstance(key, dict):
            side = _bs_side_key(key.get("team", key.get("side", d_side)))
            slot = _bs_to_int(key.get("slot", d_slot), d_slot)
            if slot < 0:
                slot = 0
            return {"team": side, "slot": slot, "key": bs_unit_key(side, slot)}

        raw = str(key or "").strip().lower()
        if not raw:
            return {"team": d_side, "slot": d_slot, "key": bs_unit_key(d_side, d_slot)}

        if ":" in raw:
            side_s, slot_s = raw.split(":", 1)
            side = _bs_side_key(side_s)
            slot = _bs_to_int(slot_s, d_slot)
            if slot < 0:
                slot = 0
            return {"team": side, "slot": slot, "key": bs_unit_key(side, slot)}

        side = _bs_side_key(raw)
        return {"team": side, "slot": d_slot, "key": bs_unit_key(side, d_slot)}

    def bs_get_active_unit_key(side):
        return bs_unit_key(side, bs_get_active_slot(side))

    def bs_get_unit_by_key(key):
        parsed = bs_parse_unit_key(key)
        side = parsed.get("team", "player")
        slot = max(0, _bs_to_int(parsed.get("slot", 0), 0))
        team = bs_get_team(side)
        if slot >= len(team):
            return None
        u = team[slot]
        if not isinstance(u, dict):
            return None
        out = _bs_with_stamina_shadow_fields(dict(u))
        out["team"] = side
        out["slot"] = slot
        out["unit_key"] = parsed.get("key", bs_unit_key(side, slot))
        return out

    def bs_slot_tag(team, slot):
        side = _bs_side_key(team)
        idx = max(0, _bs_to_int(slot, 0))
        prefix = "P" if side == "player" else "E"
        return "{}{}".format(prefix, idx + 1)

    def bs_describe_unit_key(key, default_side="player", default_slot=0):
        info = bs_parse_unit_key(key, default_side=default_side, default_slot=default_slot)
        side = str(info.get("team", "player") or "player")
        slot = max(0, _bs_to_int(info.get("slot", 0), 0))
        unit = bs_get_unit_by_key(info.get("key", ""))

        role = "player" if side == "player" else "enemy"
        slot_txt = str(slot + 1)

        name = ""
        if isinstance(unit, dict):
            name = str(unit.get("char_id", "") or "")
        if not name:
            name = ("P{}".format(slot + 1) if side == "player" else "E{}".format(slot + 1))

        return "{} {} {}".format(role, slot_txt, name)


    def bs_set_active_by_key(key, mirror_units=True):
        parsed = bs_parse_unit_key(key)
        return bs_set_active_slot(parsed.get("team", "player"), parsed.get("slot", 0), mirror_units=mirror_units)

    def bs_set_active_slot(side, slot, mirror_units=True):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        team = bs.get("teams", {}).get(side, []) or []
        if not team:
            _bs_sync_active_unit_from_units(bs, side)
            team = bs.get("teams", {}).get(side, []) or []

        idx = _bs_to_int(slot, 0)
        if idx < 0:
            idx = 0
        if idx >= len(team):
            idx = max(0, len(team) - 1)

        unit = team[idx] if (0 <= idx < len(team) and isinstance(team[idx], dict)) else None
        if unit is None:
            return None

        bs.setdefault("active", {})[side] = str(unit.get("uid", "") or "{}_{}".format(side, idx + 1))

        if mirror_units:
            hp = max(0, _bs_to_int(unit.get("hp", _bs_legacy_hp(side)), _bs_legacy_hp(side)))
            mx = max(1, _bs_to_int(unit.get("max_hp", _bs_legacy_max_hp(side)), _bs_legacy_max_hp(side)))
            if hp > mx:
                hp = mx
            mirror = {
                "uid": str(unit.get("uid", "") or "{}_{}".format(side, idx + 1)),
                "char_id": str(unit.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side)),
                "hp": hp,
                "max_hp": mx,
            }
            mirror = _bs_with_coating_fields(mirror, mirror.get("char_id", _bs_default_char_id(side)))
            mirror["stamina_current"] = max(0, _bs_to_int(unit.get("stamina_current", 0), 0))
            mirror["stamina_cap"] = max(0, _bs_to_int(unit.get("stamina_cap", mx), mx))
            mirror["stamina_enabled"] = bool(unit.get("stamina_enabled", False))
            mirror["shadow_current"] = max(0, _bs_to_int(unit.get("shadow_current", 0), 0))
            mirror["shadow_cap"] = max(0, _bs_to_int(unit.get("shadow_cap", mx), mx))
            mirror["shadow_active"] = bool(unit.get("shadow_active", False))
            bs.setdefault("units", {})[side] = _bs_with_stamina_shadow_fields(mirror)

        S.battle_state = bs
        return bs_get_active_unit(side)

    def bs_get_team_alive(side):
        side = _bs_side_key(side)
        out = []
        for u in bs_get_team(side):
            hp = max(0, _bs_to_int(u.get("hp", 0), 0))
            alive = bool(u.get("alive", hp > 0)) and hp > 0
            if alive:
                uu = dict(u)
                uu["alive"] = True
                out.append(uu)
        return out

    def bs_team_alive_count(side):
        return len(bs_get_team_alive(side))

    def bs_is_team_defeated(side):
        return (bs_team_alive_count(side) <= 0)

    def bs_get_battle_winner_team():
        p_def = bs_is_team_defeated("player")
        e_def = bs_is_team_defeated("enemy")
        if p_def and not e_def:
            return "enemy"
        if e_def and not p_def:
            return "player"
        return None

    def bs_ensure_active_progress(side):
        side = _bs_side_key(side)
        cur_key = bs_get_active_unit_key(side)
        nxt = bs_auto_advance_active_if_ko(side)
        new_key = bs_get_active_unit_key(side)
        switched = bool(cur_key != new_key)
        return {
            "side": side,
            "active_switched": switched,
            "active_key_before": cur_key,
            "active_key_after": new_key,
            "active_unit": (dict(nxt) if isinstance(nxt, dict) else None),
            "team_defeated": bs_is_team_defeated(side),
        }

    def bs_is_unit_alive(key):
        u = bs_get_unit_by_key(key)
        if not isinstance(u, dict):
            return False
        hp = max(0, _bs_to_int(u.get("hp", 0), 0))
        return bool(u.get("alive", hp > 0)) and hp > 0

    def bs_get_alive_unit_keys(side):
        side = _bs_side_key(side)
        team = bs_get_team(side)
        out = []
        for i, u in enumerate(team):
            if not isinstance(u, dict):
                continue
            hp = max(0, _bs_to_int(u.get("hp", 0), 0))
            alive = bool(u.get("alive", hp > 0)) and hp > 0
            if alive:
                out.append(bs_unit_key(side, i))
        return out

    def bs_get_turn_order_keys():
        bs = battle_state_ensure()
        turn = bs.get("turn", {}) if isinstance(bs.get("turn", {}), dict) else {}
        order = turn.get("order_keys", []) if isinstance(turn.get("order_keys", []), list) else []
        out = []
        for k in order:
            kk = bs_parse_unit_key(k).get("key", "")
            if kk:
                out.append(kk)
        if out:
            return out
        return ["player:0", "enemy:0", "player:1", "enemy:1"]

    def bs_set_turn_order_keys(order_keys=None, start_index=0, mirror_legacy=True):
        bs = battle_state_ensure()
        turn = bs.setdefault("turn", {})

        order = []
        for k in (order_keys or []):
            kk = bs_parse_unit_key(k).get("key", "")
            if kk and kk not in order:
                order.append(kk)
        if not order:
            order = ["player:0", "enemy:0", "player:1", "enemy:1"]

        idx = _bs_to_int(start_index, 0)
        if idx < 0:
            idx = 0
        if idx >= len(order):
            idx = idx % max(1, len(order))

        # saltar muertos al inicializar
        for step in range(len(order)):
            cand = order[(idx + step) % len(order)]
            if bs_is_unit_alive(cand):
                idx = (idx + step) % len(order)
                break

        actor_key = order[idx]
        info = bs_parse_unit_key(actor_key)

        turn["order_keys"] = list(order)
        turn["order_index"] = int(idx)
        turn["current_actor_key"] = str(actor_key)
        bs["turn"] = turn
        S.battle_state = bs

        bs_set_turn_ctx(
            owner_team=info.get("team", "player"),
            owner_slot=int(info.get("slot", 0) or 0),
            phase="offensive",
            mirror_legacy=mirror_legacy,
        )
        return str(actor_key)

    def bs_current_actor_key():
        bs = battle_state_ensure()
        turn = bs.get("turn", {}) if isinstance(bs.get("turn", {}), dict) else {}
        actor_key = str(turn.get("current_actor_key", "") or "")
        if actor_key:
            return bs_parse_unit_key(actor_key).get("key", actor_key)

        order = bs_get_turn_order_keys()
        idx = _bs_to_int(turn.get("order_index", 0), 0)
        if idx < 0:
            idx = 0
        if idx >= len(order):
            idx = 0
        return str(order[idx]) if order else "player:0"

    def bs_current_team():
        info = bs_parse_unit_key(bs_current_actor_key())
        return str(info.get("team", "player") or "player")

    def bs_is_player_turn():
        return bool(bs_current_team() == "player")

    def bs_turn_advance(mirror_legacy=True):
        bs = battle_state_ensure()
        turn = bs.get("turn", {}) if isinstance(bs.get("turn", {}), dict) else {}
        order = bs_get_turn_order_keys()
        if not order:
            return bs_set_turn_order_keys(["player:0", "enemy:0", "player:1", "enemy:1"], 0, mirror_legacy=mirror_legacy)

        idx = _bs_to_int(turn.get("order_index", 0), 0)
        if idx < 0:
            idx = 0
        idx = idx % len(order)

        next_idx = idx
        for step in range(1, len(order) + 1):
            cand_idx = (idx + step) % len(order)
            cand = order[cand_idx]
            if bs_is_unit_alive(cand):
                next_idx = cand_idx
                break

        turn["order_index"] = int(next_idx)
        actor_key = str(order[next_idx])
        turn["current_actor_key"] = actor_key
        bs["turn"] = turn
        S.battle_state = bs

        info = bs_parse_unit_key(actor_key)
        bs_set_turn_ctx(
            owner_team=info.get("team", "player"),
            owner_slot=int(info.get("slot", 0) or 0),
            phase="offensive",
            mirror_legacy=mirror_legacy,
        )
        return actor_key

    def bs_get_valid_target_keys(target_team, exclude_unit_key=None):
        team = _bs_side_key(target_team)
        keys = bs_get_alive_unit_keys(team)
        if exclude_unit_key is None:
            return list(keys)
        ex = bs_parse_unit_key(exclude_unit_key)
        ex_key = ex.get("key", "")
        return [k for k in keys if k != ex_key]

    def bs_resolve_target_keys(mode="single_target", target_team="enemy", selected_target_key=None, manual_target_keys=None, source_unit_key=None):
        md = str(mode or "single_target").strip().lower()
        valid = bs_get_valid_target_keys(target_team)
        if not valid:
            return []

        if md == "single_target":
            if selected_target_key:
                st = bs_parse_unit_key(selected_target_key, default_side=_bs_side_key(target_team), default_slot=0)
                sk = st.get("key", "")
                if sk in valid:
                    return [sk]
            return [valid[0]]

        if md == "split_equal":
            return list(valid)

        if md == "split_manual":
            out = []
            seen = set()
            src_key = None
            if source_unit_key is not None:
                src_key = bs_parse_unit_key(source_unit_key).get("key", "")

            if isinstance(manual_target_keys, dict):
                iterable = manual_target_keys.keys()
            elif isinstance(manual_target_keys, (list, tuple)):
                iterable = manual_target_keys
            else:
                iterable = []

            for it in iterable:
                k = bs_parse_unit_key(it, default_side=_bs_side_key(target_team), default_slot=0).get("key", "")
                if not k or k in seen:
                    continue
                if k not in valid:
                    continue
                if src_key and k == src_key:
                    continue
                seen.add(k)
                out.append(k)

            if out:
                return out
            return list(valid)

        _bs_warn("bs_resolve_target_keys mode inválido: {!r}; fallback='single_target'".format(mode))
        return [valid[0]]

    def _bs_apply_unit_hp(team, slot, new_hp, mirror_units=True):
        side = _bs_side_key(team)
        idx = max(0, _bs_to_int(slot, 0))
        bs = battle_state_ensure()
        t = bs.get("teams", {}).get(side, []) or []
        if idx >= len(t) or not isinstance(t[idx], dict):
            return None

        unit = dict(t[idx])
        mx = max(1, _bs_to_int(unit.get("max_hp", _bs_legacy_max_hp(side)), _bs_legacy_max_hp(side)))
        hp = max(0, min(_bs_to_int(new_hp, 0), mx))
        unit["max_hp"] = mx
        unit["hp"] = hp
        unit["alive"] = bool(hp > 0)
        unit = _bs_with_coating_fields(unit, unit.get("char_id", _bs_default_char_id(side)))
        unit = _bs_with_stamina_shadow_fields(unit)
        t[idx] = unit
        bs.setdefault("teams", {})[side] = t

        active_slot = bs_get_active_slot(side)
        if mirror_units and idx == active_slot:
            bs.setdefault("units", {})[side] = {
                "uid": str(unit.get("uid", "") or "{}_{}".format(side, idx + 1)),
                "char_id": str(unit.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side)),
                "hp": hp,
                "max_hp": mx,
                "race": str(unit.get("race", "human") or "human"),
                "coating_type": str(unit.get("coating_type", "fullbring") or "fullbring"),
                "coating_cover": max(0, _bs_to_int(unit.get("coating_cover", 0), 0)),
                "coating_durability_max": max(0, _bs_to_int(unit.get("coating_durability_max", 0), 0)),
                "coating_durability_current": max(0, _bs_to_int(unit.get("coating_durability_current", 0), 0)),
                "coating_active": bool(unit.get("coating_active", False)),
                "stamina_current": max(0, _bs_to_int(unit.get("stamina_current", 0), 0)),
                "stamina_cap": max(0, _bs_to_int(unit.get("stamina_cap", mx), mx)),
                "stamina_enabled": bool(unit.get("stamina_enabled", False)),
                "shadow_current": max(0, _bs_to_int(unit.get("shadow_current", 0), 0)),
                "shadow_cap": max(0, _bs_to_int(unit.get("shadow_cap", mx), mx)),
                "shadow_active": bool(unit.get("shadow_active", False)),
                "missing_hp": max(0, _bs_to_int(unit.get("missing_hp", max(0, mx - hp)), max(0, mx - hp))),
                "free_space": max(0, _bs_to_int(unit.get("free_space", 0), 0)),
            }

        S.battle_state = bs
        out = dict(unit)
        out["team"] = side
        out["slot"] = idx
        out["unit_key"] = bs_unit_key(side, idx)
        return out

    def bs_apply_damage_to_unit_key(target_key, dmg, source_key=None, reason=None, tags=None):
        trg = bs_parse_unit_key(target_key)
        side = trg.get("team", "player")
        slot = max(0, _bs_to_int(trg.get("slot", 0), 0))

        cur_unit = bs_get_unit_by_key(bs_unit_key(side, slot))
        if not isinstance(cur_unit, dict):
            return {
                "ok": False,
                "target_key": bs_unit_key(side, slot),
                "error": "target_not_found",
            }

        hp_before = max(0, _bs_to_int(cur_unit.get("hp", 0), 0))
        mx = max(1, _bs_to_int(cur_unit.get("max_hp", 1), 1))
        dmg_i = max(0, _bs_to_int(dmg, 0))

        cur_unit = _bs_with_coating_fields(cur_unit, cur_unit.get("char_id", _bs_default_char_id(side)))
        cur_unit = _bs_with_stamina_shadow_fields(cur_unit)
        cover = max(0, _bs_to_int(cur_unit.get("coating_cover", 0), 0))
        dura_before = max(0, _bs_to_int(cur_unit.get("coating_durability_current", 0), 0))
        coating_active_before = bool(cur_unit.get("coating_active", False)) and cover > 0 and dura_before > 0

        after_cover = max(0, dmg_i - cover) if coating_active_before else dmg_i
        absorbed_by_cover = max(0, dmg_i - after_cover) if coating_active_before else 0

        absorbed_by_durability = 0
        spill_to_hp = after_cover
        dura_after = dura_before
        if coating_active_before and after_cover > 0:
            absorbed_by_durability = min(dura_before, after_cover)
            dura_after = max(0, dura_before - after_cover)
            spill_to_hp = max(0, after_cover - dura_before)

        # Fase 2 (contrato): coating -> estamina -> HP -> KO gate -> generación de estamina
        incoming_after_coating = max(0, _bs_to_int(spill_to_hp, 0))
        stamina_before = max(0, _bs_to_int(cur_unit.get("stamina_current", 0), 0))
        stamina_cap = max(0, _bs_to_int(cur_unit.get("stamina_cap", mx), mx))
        stamina_enabled = bool(cur_unit.get("stamina_enabled", False))
        shadow_before = max(0, _bs_to_int(cur_unit.get("shadow_current", 0), 0))
        shadow_cap = max(0, _bs_to_int(cur_unit.get("shadow_cap", mx), mx))
        shadow_active = bool(cur_unit.get("shadow_active", False))

        stamina_absorbed = min(stamina_before, incoming_after_coating)
        stamina_after_consume = max(0, stamina_before - stamina_absorbed)
        overflow_to_hp = max(0, incoming_after_coating - stamina_absorbed)

        hp_after = max(0, min(mx, hp_before - overflow_to_hp))
        hp_damage_real = max(0, hp_before - hp_after)
        ko_now = (hp_after <= 0)

        shadow_effective = shadow_before if shadow_active else 0
        missing_after_hp = max(0, mx - hp_after)
        free_space_after = max(0, missing_after_hp - stamina_after_consume - shadow_effective)
        stamina_gain = 0
        if (not ko_now) and hp_damage_real > 0 and stamina_enabled and free_space_after > 0:
            stamina_gain = min(
                hp_damage_real,
                free_space_after,
                max(0, stamina_cap - stamina_after_consume),
            )
            stamina_gain = max(0, _bs_to_int(stamina_gain, 0))

        stamina_after = max(0, stamina_after_consume + stamina_gain)
        gain_without_shadow = 0
        if (not ko_now) and hp_damage_real > 0 and stamina_enabled:
            free_without_shadow = max(0, missing_after_hp - stamina_after_consume)
            gain_without_shadow = min(
                hp_damage_real,
                free_without_shadow,
                max(0, stamina_cap - stamina_after_consume),
            )
            gain_without_shadow = max(0, _bs_to_int(gain_without_shadow, 0))
        blocked_by_shadow = max(0, gain_without_shadow - stamina_gain)

        cur_unit["coating_durability_current"] = int(dura_after)
        cur_unit["coating_active"] = bool(cover > 0 and dura_after > 0)

        try:
            bs = battle_state_ensure()
            t = bs.get("teams", {}).get(side, []) or []
            if slot < len(t) and isinstance(t[slot], dict):
                uu = dict(t[slot])
                uu["coating_durability_current"] = int(dura_after)
                uu["coating_active"] = bool(cover > 0 and dura_after > 0)
                uu["stamina_current"] = int(stamina_after)
                uu["stamina_cap"] = int(stamina_cap)
                uu["stamina_enabled"] = bool(stamina_enabled)
                uu["shadow_current"] = int(max(0, min(shadow_before, shadow_cap)))
                uu["shadow_cap"] = int(shadow_cap)
                uu["shadow_active"] = bool(shadow_active)
                t[slot] = uu
                bs.setdefault("teams", {})[side] = t
                active_uid = str(bs.get("active", {}).get(side, "") or "")
                target_uid = str(uu.get("uid", "") or "")
                if active_uid and target_uid and active_uid == target_uid:
                    mu = dict(bs.get("units", {}).get(side, {}) or {})
                    mu["hp"] = int(max(0, min(mx, hp_after)))
                    mu["max_hp"] = int(mx)
                    mu["stamina_current"] = int(stamina_after)
                    mu["stamina_cap"] = int(stamina_cap)
                    mu["stamina_enabled"] = bool(stamina_enabled)
                    mu["shadow_current"] = int(max(0, min(shadow_before, shadow_cap)))
                    mu["shadow_cap"] = int(shadow_cap)
                    mu["shadow_active"] = bool(shadow_active)
                    bs.setdefault("units", {})[side] = mu
                S.battle_state = bs
        except:
            pass

        updated = _bs_apply_unit_hp(side, slot, hp_after, mirror_units=True)
        died = (hp_after <= 0 and hp_before > 0)

        switched = False
        new_active = None
        if died:
            try:
                info = bs_ensure_active_progress(side)
                switched = bool(info.get("active_switched", False))
                new_active = info.get("active_key_after", None)
            except:
                pass

        _bs_emit_stamina_shadow_log(
            stamina_before=stamina_before,
            incoming_after_coating=incoming_after_coating,
            stamina_after=stamina_after,
            overflow_to_hp=overflow_to_hp,
            hp_before=hp_before,
            hp_after=hp_after,
            stamina_gain=stamina_gain,
            blocked_by_shadow=blocked_by_shadow,
        )

        return {
            "ok": True,
            "target": side,
            "target_slot": slot,
            "target_key": bs_unit_key(side, slot),
            "source_key": bs_parse_unit_key(source_key).get("key", "") if source_key is not None else "",
            "reason": reason,
            "tags": list(tags) if isinstance(tags, (list, tuple)) else ([] if tags is None else [str(tags)]),
            "damage": dmg_i,
            "coating": {
                "type": str(cur_unit.get("coating_type", "") or ""),
                "active_before": bool(coating_active_before),
                "active_after": bool((updated or {}).get("coating_active", False)) if isinstance(updated, dict) else bool(cover > 0 and dura_after > 0),
                "cover": int(cover),
                "cover_absorbed": int(absorbed_by_cover),
                "after_cover": int(after_cover),
                "durability_before": int(dura_before),
                "durability_absorbed": int(absorbed_by_durability),
                "durability_after": int(dura_after),
                "hp_spill": int(spill_to_hp),
            },
            "stamina": {
                "before": int(stamina_before),
                "absorbed": int(stamina_absorbed),
                "after_consume": int(stamina_after_consume),
                "gain": int(stamina_gain),
                "after": int(stamina_after),
                "cap": int(stamina_cap),
                "enabled": bool(stamina_enabled),
                "overflow_to_hp": int(overflow_to_hp),
            },
            "shadow": {
                "before": int(shadow_before),
                "cap": int(shadow_cap),
                "active": bool(shadow_active),
                "effective_for_block": int(shadow_effective),
            },
            "space": {
                "missing_hp_after": int(missing_after_hp),
                "free_space_after": int(max(0, missing_after_hp - stamina_after - shadow_effective)),
                "blocked_by_shadow": int(blocked_by_shadow),
            },
            "hp_before": hp_before,
            "hp_after": hp_after,
            "hp_damage_real": int(hp_damage_real),
            "died": died,
            "auto_switched": switched,
            "new_active_key": new_active,
            "team_defeated": bs_is_team_defeated(side),
            "unit": updated,
        }

    def bs_make_damage_plan(source_key=None, entries=None, mode="single_target", skill_id=None, effect_scope="primary", meta=None):
        src = bs_parse_unit_key(source_key).get("key", "") if source_key is not None else ""
        out_entries = []

        for e in (entries or []):
            if not isinstance(e, dict):
                continue
            tk = bs_parse_unit_key(e.get("target_key", e.get("target")), default_side="enemy", default_slot=0).get("key", "")
            amount = max(0, _bs_to_int(e.get("amount", 0), 0))
            tags = e.get("tags", [])
            if not isinstance(tags, (list, tuple)):
                tags = [str(tags)] if tags is not None else []
            if tk:
                out_entries.append({"target_key": tk, "amount": amount, "tags": list(tags)})

        m = dict(meta) if isinstance(meta, dict) else {}
        m.setdefault("mode", str(mode or "single_target"))
        eff = str(effect_scope or "primary").strip().lower()
        if eff not in ("primary", "all", "none", "all_if_buff"):
            eff = "primary"
        m.setdefault("effect_scope", eff)
        if skill_id is not None:
            m.setdefault("skill_id", skill_id)

        total = 0
        for e in out_entries:
            total += max(0, _bs_to_int(e.get("amount", 0), 0))

        return {
            "source_key": src,
            "entries": out_entries,
            "meta": m,
            "total_amount": total,
        }

    def bs_apply_damage_plan(plan, reason=None):
        p = dict(plan) if isinstance(plan, dict) else {}
        src = bs_parse_unit_key(p.get("source_key", ""), default_side="player", default_slot=0).get("key", "")
        entries = p.get("entries", []) if isinstance(p.get("entries", []), list) else []
        meta = dict(p.get("meta", {})) if isinstance(p.get("meta", {}), dict) else {}

        results = []
        total_applied = 0
        for e in entries:
            if not isinstance(e, dict):
                continue
            tk = bs_parse_unit_key(e.get("target_key", e.get("target")), default_side="enemy", default_slot=0).get("key", "")
            if not tk:
                continue
            amount = max(0, _bs_to_int(e.get("amount", 0), 0))
            if amount <= 0:
                continue
            rr = bs_apply_damage_to_unit_key(
                tk,
                amount,
                source_key=src,
                reason=(reason if reason is not None else meta.get("skill_id", meta.get("mode", "damage_plan"))),
                tags=e.get("tags", []),
            )
            if rr.get("ok", False):
                total_applied += max(0, _bs_to_int(rr.get("damage", 0), 0))
            results.append(rr)

        return {
            "source_key": src,
            "meta": meta,
            "results": results,
            "total_applied": total_applied,
            "entries_count": len(results),
            "winner_team": bs_get_battle_winner_team(),
        }


    def bs_effect_targets_from_plan(plan, buff_allow_split_effects=False):
        p = dict(plan) if isinstance(plan, dict) else {}
        entries = p.get("entries", []) if isinstance(p.get("entries", []), list) else []
        meta = dict(p.get("meta", {})) if isinstance(p.get("meta", {}), dict) else {}
        scope = str(meta.get("effect_scope", "primary") or "primary").strip().lower()

        ordered = []
        for e in entries:
            if not isinstance(e, dict):
                continue
            tk = bs_parse_unit_key(e.get("target_key", e.get("target")), default_side="enemy", default_slot=0).get("key", "")
            if tk and tk not in ordered:
                ordered.append(tk)

        if scope == "none":
            return []
        if scope == "all":
            return ordered
        if scope == "all_if_buff" and bool(buff_allow_split_effects):
            return ordered
        if ordered:
            return [ordered[0]]
        return []

    def bs_reflect_policy_get():
        bs = battle_state_ensure()
        rp = bs.get("reflect_policy")
        if not isinstance(rp, dict):
            rp = {}
        # Política explícita A3b.4:
        # - reflect guardado por target_key/source_key
        # - consume al inicio del turno ofensivo del target_key
        # - expira al finalizar ese mismo turno ofensivo si no se consumió
        out = {
            "key_scope": str(rp.get("key_scope", "unit_key") or "unit_key"),
            "consume_on": str(rp.get("consume_on", "offensive_start") or "offensive_start"),
            "expire_on": str(rp.get("expire_on", "offensive_end") or "offensive_end"),
        }
        return out

    def bs_reflect_policy_set(consume_on="offensive_start", expire_on="offensive_end", key_scope="unit_key"):
        bs = battle_state_ensure()
        rp = {
            "key_scope": str(key_scope or "unit_key"),
            "consume_on": str(consume_on or "offensive_start"),
            "expire_on": str(expire_on or "offensive_end"),
        }
        bs["reflect_policy"] = rp
        S.battle_state = bs
        return dict(rp)

    def bs_reflect_queue(target_key, source_key, amount):
        t = bs_parse_unit_key(target_key).get("key", "")
        s_key = bs_parse_unit_key(source_key).get("key", "") if source_key is not None else ""
        val = max(0, _bs_to_int(amount, 0))
        if not t or val <= 0:
            return 0

        fn = getattr(S, "reflect_queue", None) or globals().get("reflect_queue", None)
        if callable(fn):
            try:
                fn(t, s_key, val)
                return val
            except:
                pass

        rman = getattr(S, "reflect", None) or globals().get("reflect", None)
        if rman is not None and hasattr(rman, "add"):
            try:
                rman.add(t, val, source_id=s_key)
                return val
            except:
                try:
                    rman.add(t, val)
                    return val
                except:
                    pass

        _bs_warn("bs_reflect_queue: no reflect backend disponible")
        return 0

    def bs_reflect_peek_for(target_key):
        t = bs_parse_unit_key(target_key).get("key", "")
        if not t:
            return (0, "")

        fn = getattr(S, "reflect_peek_for", None) or globals().get("reflect_peek_for", None)
        if callable(fn):
            try:
                val, src = fn(t)
                return (max(0, _bs_to_int(val, 0)), str(src or ""))
            except:
                try:
                    val = fn(t)
                    return (max(0, _bs_to_int(val, 0)), "")
                except:
                    pass

        rman = getattr(S, "reflect", None) or globals().get("reflect", None)
        if rman is not None:
            try:
                if hasattr(rman, "peek_info"):
                    val, src = rman.peek_info(t)
                    return (max(0, _bs_to_int(val, 0)), str(src or ""))
                if hasattr(rman, "peek"):
                    return (max(0, _bs_to_int(rman.peek(t), 0)), "")
            except:
                pass

        return (0, "")

    def bs_reflect_consume_for(target_key):
        t = bs_parse_unit_key(target_key).get("key", "")
        if not t:
            return (0, "")

        fn = getattr(S, "reflect_consume_for", None) or globals().get("reflect_consume_for", None)
        if callable(fn):
            try:
                val, src = fn(t)
                return (max(0, _bs_to_int(val, 0)), str(src or ""))
            except:
                try:
                    val = fn(t)
                    return (max(0, _bs_to_int(val, 0)), "")
                except:
                    pass

        rman = getattr(S, "reflect", None) or globals().get("reflect", None)
        if rman is not None:
            try:
                if hasattr(rman, "consume_info"):
                    val, src = rman.consume_info(t)
                    return (max(0, _bs_to_int(val, 0)), str(src or ""))
                if hasattr(rman, "consume"):
                    return (max(0, _bs_to_int(rman.consume(t), 0)), "")
            except:
                pass

        return (0, "")

    def bs_reflect_clear_for(target_key):
        t = bs_parse_unit_key(target_key).get("key", "")
        if not t:
            return 0

        fn = getattr(S, "reflect_clear_for", None) or globals().get("reflect_clear_for", None)
        if callable(fn):
            try:
                return max(0, _bs_to_int(fn(t), 0))
            except:
                pass

        rman = getattr(S, "reflect", None) or globals().get("reflect", None)
        if rman is not None:
            try:
                if hasattr(rman, "clear_for"):
                    return max(0, _bs_to_int(rman.clear_for(t), 0))
            except:
                pass

        return 0

    def bs_reflect_consume_for_current_turn(ctx=None):
        c = dict(ctx) if isinstance(ctx, dict) else bs_get_turn_ctx()
        key = bs_unit_key(c.get("owner_team", "player"), c.get("owner_slot", 0))
        return bs_reflect_consume_for(key)

    def bs_reflect_expire_for_current_turn(ctx=None):
        c = dict(ctx) if isinstance(ctx, dict) else bs_get_turn_ctx()
        key = bs_unit_key(c.get("owner_team", "player"), c.get("owner_slot", 0))
        return bs_reflect_clear_for(key)

    def bs_get_active_name(side):
        u = bs_get_active_unit(side)
        if isinstance(u, dict):
            nm = str(u.get("name", "") or "").strip()
            if nm:
                return nm
            cid = str(u.get("char_id", "") or "").strip()
            if cid:
                try:
                    ch = getattr(S, "get_character", None)
                    if callable(ch):
                        d = ch(cid)
                        if isinstance(d, dict):
                            nm2 = str(d.get("name", "") or "").strip()
                            if nm2:
                                return nm2
                except:
                    pass
                return cid
        sidek = _bs_side_key(side)
        if sidek == "player":
            bp = getattr(S, "battle_player", None)
            if isinstance(bp, dict):
                n = str(bp.get("name", "") or "").strip()
                if n:
                    return n
            return str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
        be = getattr(S, "battle_enemy", None)
        if isinstance(be, dict):
            n = str(be.get("name", "") or "").strip()
            if n:
                return n
        return str(getattr(S, "battle_enemy_id", "Hollow") or "Hollow")

    def bs_get_player_display_name():
        return bs_get_active_name("player")

    def bs_auto_advance_active_if_ko(side):
        side = _bs_side_key(side)
        bs = battle_state_ensure()
        team = bs.get("teams", {}).get(side, []) or []
        cur = bs_get_active_unit(side)
        cur_hp = max(0, _bs_to_int((cur or {}).get("hp", 0), 0))

        if cur and cur_hp > 0:
            return dict(cur)

        for i, u in enumerate(team):
            if not isinstance(u, dict):
                continue
            hp = max(0, _bs_to_int(u.get("hp", 0), 0))
            if hp > 0:
                return bs_set_active_slot(side, i, mirror_units=True)

        return None

    def bs_get_turn_ctx():
        bs = battle_state_ensure()
        turn = bs.get("turn", {}) if isinstance(bs.get("turn", {}), dict) else {}
        owner = _bs_side_key(turn.get("owner", "player"))
        owner_team = _bs_side_key(turn.get("owner_team", owner))
        owner_slot = _bs_to_int(turn.get("owner_slot", bs_get_active_slot(owner_team)), bs_get_active_slot(owner_team))
        if owner_slot < 0:
            owner_slot = 0
        phase = str(turn.get("phase", "offensive") or "offensive").strip().lower()
        if phase not in ("offensive", "defensive"):
            phase = "offensive"
        round_n = _bs_to_int(turn.get("round", 1), 1)
        if round_n < 1:
            round_n = 1
        return {
            "owner": owner,
            "owner_team": owner_team,
            "owner_slot": owner_slot,
            "phase": phase,
            "round": round_n,
        }

    def bs_set_turn_ctx(owner_team=None, owner_slot=None, phase=None, round_n=None, mirror_legacy=True):
        bs = battle_state_ensure()
        cur = bs_get_turn_ctx()

        team = _bs_side_key(owner_team if owner_team is not None else cur.get("owner_team", "player"))
        slot = _bs_to_int(owner_slot if owner_slot is not None else cur.get("owner_slot", bs_get_active_slot(team)), bs_get_active_slot(team))
        if slot < 0:
            slot = 0

        ph = str(phase if phase is not None else cur.get("phase", "offensive") or "offensive").strip().lower()
        if ph not in ("offensive", "defensive"):
            ph = "offensive"

        rnd = _bs_to_int(round_n if round_n is not None else cur.get("round", 1), 1)
        if rnd < 1:
            rnd = 1

        bs.setdefault("turn", {})["owner"] = team
        bs.setdefault("turn", {})["owner_team"] = team
        bs.setdefault("turn", {})["owner_slot"] = slot
        bs.setdefault("turn", {})["phase"] = ph
        bs.setdefault("turn", {})["round"] = rnd
        S.battle_state = bs

        # al setear ctx, intentar alinear activo de ese team con owner_slot
        try:
            bs_set_active_slot(team, slot, mirror_units=True)
        except:
            pass

        if mirror_legacy:
            try:
                S.battle_turn_owner = team
            except:
                pass
            try:
                S.battle_actor = team
            except:
                pass
            try:
                S.battle_phase = ph
            except:
                pass

        return bs_get_turn_ctx()

    def bs_get_turn_owner():
        return bs_get_turn_ctx().get("owner_team", "player")

    def bs_next_alive_slot(side, after_slot=None):
        side = _bs_side_key(side)
        team = bs_get_team(side)
        if not team:
            return 0
        start = _bs_to_int(after_slot, -1)
        n = len(team)
        for step in range(1, n + 1):
            idx = (start + step) % n
            u = team[idx] if idx < n else None
            if isinstance(u, dict) and max(0, _bs_to_int(u.get("hp", 0), 0)) > 0:
                return idx
        return max(0, bs_get_active_slot(side))

    def bs_set_turn_owner(owner, mirror_legacy=True):
        side = _bs_side_key(owner)
        slot = bs_get_active_slot(side)

        try:
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        except:
            mode = "1v1"

        if mode == "2v2":
            bs = battle_state_ensure()
            turn = bs.setdefault("turn", {})
            rr = turn.get("rr_last_slot", {}) if isinstance(turn.get("rr_last_slot", {}), dict) else {}
            last_slot = _bs_to_int(rr.get(side, -1), -1)

            if last_slot < 0:
                alive_keys = bs_get_alive_unit_keys(side)
                if alive_keys:
                    try:
                        import renpy
                        pick_key = str(renpy.random.choice(alive_keys) or alive_keys[0])
                    except:
                        pick_key = str(alive_keys[0])
                    info = bs_parse_unit_key(pick_key, default_side=side, default_slot=0)
                    slot = max(0, _bs_to_int(info.get("slot", 0), 0))
                else:
                    slot = 0
            else:
                slot = bs_next_alive_slot(side, after_slot=last_slot)

            rr[side] = slot
            turn["rr_last_slot"] = rr
            bs["turn"] = turn
            S.battle_state = bs

        ctx = bs_set_turn_ctx(
            owner_team=side,
            owner_slot=slot,
            phase="offensive",
            mirror_legacy=mirror_legacy,
        )
        return ctx.get("owner_team", side)

    def bs_advance_turn(mirror_legacy=True):
        cur = bs_get_turn_owner()
        nxt = "enemy" if cur == "player" else "player"
        cur_ctx = bs_get_turn_ctx()
        next_round = cur_ctx.get("round", 1)
        if nxt == "player":
            next_round = next_round + 1
        ctx = bs_set_turn_ctx(
            owner_team=nxt,
            owner_slot=bs_get_active_slot(nxt),
            phase="offensive",
            round_n=next_round,
            mirror_legacy=mirror_legacy,
        )
        return ctx.get("owner_team", nxt)

    def bs_sync_turn_to_legacy():
        owner = bs_get_turn_owner()
        return bs_set_turn_owner(owner, mirror_legacy=True)

    def bs_sync_turn_from_legacy():
        owner = _bs_side_key(getattr(S, "battle_turn_owner", "player"))
        return bs_set_turn_owner(owner, mirror_legacy=False)

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
    S.bs_get_team = bs_get_team
    S.bs_get_active_unit = bs_get_active_unit
    S.bs_init_single_teams = bs_init_single_teams
    S.bs_init_teams = bs_init_teams
    S.bs_get_active_slot = bs_get_active_slot
    S.bs_unit_key = bs_unit_key
    S.bs_parse_unit_key = bs_parse_unit_key
    S.bs_get_active_unit_key = bs_get_active_unit_key
    S.bs_get_unit_by_key = bs_get_unit_by_key
    S.bs_describe_unit_key = bs_describe_unit_key
    S.bs_slot_tag = bs_slot_tag
    S.bs_set_active_by_key = bs_set_active_by_key
    S.bs_set_active_slot = bs_set_active_slot
    S.bs_get_team_alive = bs_get_team_alive
    S.bs_team_alive_count = bs_team_alive_count
    S.bs_is_team_defeated = bs_is_team_defeated
    S.bs_get_battle_winner_team = bs_get_battle_winner_team
    S.bs_ensure_active_progress = bs_ensure_active_progress
    S.bs_is_unit_alive = bs_is_unit_alive
    S.bs_get_alive_unit_keys = bs_get_alive_unit_keys
    S.bs_get_turn_order_keys = bs_get_turn_order_keys
    S.bs_set_turn_order_keys = bs_set_turn_order_keys
    S.bs_current_actor_key = bs_current_actor_key
    S.bs_current_team = bs_current_team
    S.bs_is_player_turn = bs_is_player_turn
    S.bs_turn_advance = bs_turn_advance
    S.bs_get_valid_target_keys = bs_get_valid_target_keys
    S.bs_ensure_unit_resources = bs_ensure_unit_resources
    S.bs_get_unit_resources = bs_get_unit_resources
    S.bs_set_unit_resources = bs_set_unit_resources
    S.bs_consume_unit_resources = bs_consume_unit_resources
    S.bs_get_unit_stamina_shadow = bs_get_unit_stamina_shadow
    S.bs_set_unit_stamina_shadow = bs_set_unit_stamina_shadow
    S.bs_resolve_target_keys = bs_resolve_target_keys
    S.bs_apply_damage_to_unit_key = bs_apply_damage_to_unit_key
    S.bs_make_damage_plan = bs_make_damage_plan
    S.bs_apply_damage_plan = bs_apply_damage_plan
    S.bs_effect_targets_from_plan = bs_effect_targets_from_plan
    S.bs_reflect_policy_get = bs_reflect_policy_get
    S.bs_reflect_policy_set = bs_reflect_policy_set
    S.bs_reflect_queue = bs_reflect_queue
    S.bs_reflect_peek_for = bs_reflect_peek_for
    S.bs_reflect_consume_for = bs_reflect_consume_for
    S.bs_reflect_clear_for = bs_reflect_clear_for
    S.bs_reflect_consume_for_current_turn = bs_reflect_consume_for_current_turn
    S.bs_reflect_expire_for_current_turn = bs_reflect_expire_for_current_turn
    S.bs_get_active_name = bs_get_active_name
    S.bs_get_player_display_name = bs_get_player_display_name
    S.bs_auto_advance_active_if_ko = bs_auto_advance_active_if_ko
    S.bs_get_turn_ctx = bs_get_turn_ctx
    S.bs_set_turn_ctx = bs_set_turn_ctx
    S.bs_get_turn_owner = bs_get_turn_owner
    S.bs_set_turn_owner = bs_set_turn_owner
    S.bs_next_alive_slot = bs_next_alive_slot
    S.bs_advance_turn = bs_advance_turn
    S.bs_sync_turn_to_legacy = bs_sync_turn_to_legacy
    S.bs_sync_turn_from_legacy = bs_sync_turn_from_legacy
