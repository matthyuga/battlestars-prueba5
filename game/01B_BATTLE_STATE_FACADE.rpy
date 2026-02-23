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

    def _bs_default_char_id(side):
        side = _bs_side_key(side)
        if side == "player":
            return str(getattr(S, "battle_player_id", "Harribel") or "Harribel")
        return str(getattr(S, "battle_enemy_id", "Hollow") or "Hollow")

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
        team[idx] = unit

        teams[side] = team
        active[side] = unit["uid"]
        units[side] = {
            "uid": unit["uid"],
            "char_id": unit["char_id"],
            "hp": hp,
            "max_hp": mx,
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

    def bs_init_single_teams(player_char_id=None, enemy_char_id=None, player_hp=None, player_max_hp=None, enemy_hp=None, enemy_max_hp=None):
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

        bs.setdefault("teams", {})["player"] = [{
            "uid": "player_1",
            "char_id": p_char,
            "hp": p_hp,
            "max_hp": p_mx,
            "alive": bool(p_hp > 0),
        }]
        bs.setdefault("teams", {})["enemy"] = [{
            "uid": "enemy_1",
            "char_id": e_char,
            "hp": e_hp,
            "max_hp": e_mx,
            "alive": bool(e_hp > 0),
        }]
        bs.setdefault("active", {})["player"] = "player_1"
        bs.setdefault("active", {})["enemy"] = "enemy_1"

        bs.setdefault("units", {})["player"] = {
            "uid": "player_1",
            "char_id": p_char,
            "hp": p_hp,
            "max_hp": p_mx,
        }
        bs.setdefault("units", {})["enemy"] = {
            "uid": "enemy_1",
            "char_id": e_char,
            "hp": e_hp,
            "max_hp": e_mx,
        }

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
        out = dict(u)
        out["team"] = side
        out["slot"] = slot
        out["unit_key"] = parsed.get("key", bs_unit_key(side, slot))
        return out

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
            bs.setdefault("units", {})[side] = {
                "uid": str(unit.get("uid", "") or "{}_{}".format(side, idx + 1)),
                "char_id": str(unit.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side)),
                "hp": hp,
                "max_hp": mx,
            }

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
        t[idx] = unit
        bs.setdefault("teams", {})[side] = t

        active_slot = bs_get_active_slot(side)
        if mirror_units and idx == active_slot:
            bs.setdefault("units", {})[side] = {
                "uid": str(unit.get("uid", "") or "{}_{}".format(side, idx + 1)),
                "char_id": str(unit.get("char_id", _bs_default_char_id(side)) or _bs_default_char_id(side)),
                "hp": hp,
                "max_hp": mx,
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
        hp_after = max(0, min(mx, hp_before - dmg_i))

        updated = _bs_apply_unit_hp(side, slot, hp_after, mirror_units=True)
        died = (hp_after <= 0 and hp_before > 0)

        return {
            "ok": True,
            "target": side,
            "target_slot": slot,
            "target_key": bs_unit_key(side, slot),
            "source_key": bs_parse_unit_key(source_key).get("key", "") if source_key is not None else "",
            "reason": reason,
            "tags": list(tags) if isinstance(tags, (list, tuple)) else ([] if tags is None else [str(tags)]),
            "damage": dmg_i,
            "hp_before": hp_before,
            "hp_after": hp_after,
            "died": died,
            "unit": updated,
        }

    def bs_make_damage_plan(source_key=None, entries=None, mode="single_target", skill_id=None, meta=None):
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
        }

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

    def bs_set_turn_owner(owner, mirror_legacy=True):
        side = _bs_side_key(owner)
        ctx = bs_set_turn_ctx(
            owner_team=side,
            owner_slot=bs_get_active_slot(side),
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
    S.bs_get_active_slot = bs_get_active_slot
    S.bs_unit_key = bs_unit_key
    S.bs_parse_unit_key = bs_parse_unit_key
    S.bs_get_active_unit_key = bs_get_active_unit_key
    S.bs_get_unit_by_key = bs_get_unit_by_key
    S.bs_set_active_by_key = bs_set_active_by_key
    S.bs_set_active_slot = bs_set_active_slot
    S.bs_get_team_alive = bs_get_team_alive
    S.bs_is_unit_alive = bs_is_unit_alive
    S.bs_get_alive_unit_keys = bs_get_alive_unit_keys
    S.bs_get_valid_target_keys = bs_get_valid_target_keys
    S.bs_resolve_target_keys = bs_resolve_target_keys
    S.bs_apply_damage_to_unit_key = bs_apply_damage_to_unit_key
    S.bs_make_damage_plan = bs_make_damage_plan
    S.bs_apply_damage_plan = bs_apply_damage_plan
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
    S.bs_advance_turn = bs_advance_turn
    S.bs_sync_turn_to_legacy = bs_sync_turn_to_legacy
    S.bs_sync_turn_from_legacy = bs_sync_turn_from_legacy
