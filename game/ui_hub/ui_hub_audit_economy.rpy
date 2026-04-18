# ui_hub_audit_economy.rpy
# Fase 4 de split: economía, cuenta y auditoría.

init -880 python:
    import math
    import random
    import renpy.store as S

    def bs_saga_account():
        state = getattr(S, "bs_saga_account_state", None)
        if isinstance(state, dict):
            return state
        state = {
            "account_id": "local_player",
            "display_name": "Mistico",
            "level": 1,
            "exp": 0,
            "exp_to_next": 100,
            "tier": "",
            "gold": 5000,
            "gems": 0
        }
        S.bs_saga_account_state = state
        return state

    def bs_saga_gold():
        acc = bs_saga_account()
        try:
            return int(acc.get("gold", 0))
        except:
            return 0

    def bs_saga_set_message(msg):
        S.bs_saga_last_tx_message = str(msg or "")
        return None

    def bs_saga_dev_can_edit_account():
        return bool(getattr(S, "bs_saga_dev_admin_enabled", False))

    def bs_saga_dev_set_account_state(gold=None, level=None, exp=None, exp_to_next=None):
        if not bs_saga_dev_can_edit_account():
            return False
        acc = bs_saga_account()
        if gold is not None:
            try:
                acc["gold"] = max(0, int(gold))
            except:
                pass
        if level is not None:
            try:
                acc["level"] = max(1, int(level))
            except:
                pass
        if exp is not None:
            try:
                acc["exp"] = max(0, int(exp))
            except:
                pass
        if exp_to_next is not None:
            try:
                acc["exp_to_next"] = max(1, int(exp_to_next))
            except:
                pass
        bs_saga_refresh_account_tier(reason="dev_set_account_state")
        return True

    def bs_saga_exp_required_for_level(level):
        try:
            lvl = int(level or 1)
        except:
            lvl = 1
        if lvl < 1:
            lvl = 1
        base = 100.0
        growth = 1.12
        need = int(round(base * (growth ** float(max(0, lvl - 1)))))
        return max(100, need)

    def bs_saga_gain_account_rewards(exp_gain=0, gold_gain=0, source="runtime_reward"):
        acc = bs_saga_account()
        try:
            eg = max(0, int(exp_gain or 0))
        except:
            eg = 0
        try:
            gg = max(0, int(gold_gain or 0))
        except:
            gg = 0
        if gg > 0:
            acc["gold"] = max(0, int(acc.get("gold", 0) or 0) + gg)
        lvl_before = int(acc.get("level", 1) or 1)
        lvl = max(1, lvl_before)
        exp = max(0, int(acc.get("exp", 0) or 0) + eg)
        levels_gained = 0
        exp_to_next = bs_saga_exp_required_for_level(lvl)
        while exp >= exp_to_next:
            exp -= exp_to_next
            lvl += 1
            levels_gained += 1
            exp_to_next = bs_saga_exp_required_for_level(lvl)
            if levels_gained > 500:
                break
        acc["level"] = int(lvl)
        acc["exp"] = int(exp)
        acc["exp_to_next"] = int(exp_to_next)
        bs_saga_refresh_account_tier(reason=str(source or "runtime_reward"))
        bs_saga_audit_push("account_rewards_gain", {
            "source": str(source or "runtime_reward"),
            "exp_gain": int(eg),
            "gold_gain": int(gg),
            "level_before": int(lvl_before),
            "level_after": int(lvl),
            "levels_gained": int(levels_gained),
            "exp_to_next": int(exp_to_next),
        })
        return {
            "ok": True,
            "exp_gain": int(eg),
            "gold_gain": int(gg),
            "level_after": int(lvl),
            "levels_gained": int(levels_gained),
            "exp_after": int(exp),
            "exp_to_next": int(exp_to_next),
        }

    def bs_saga_dev_set_gain_profile(exp_base=None, gold_base=None, variance_pct=None, runs=None):
        if not bs_saga_dev_can_edit_account():
            return {"ok": False, "error": "admin_disabled"}
        if exp_base is not None:
            try:
                S.bs_saga_dev_gain_exp_base = max(1, min(20000, int(exp_base)))
            except:
                pass
        if gold_base is not None:
            try:
                S.bs_saga_dev_gain_gold_base = max(1, min(500000, int(gold_base)))
            except:
                pass
        if variance_pct is not None:
            try:
                S.bs_saga_dev_gain_variance_pct = max(0, min(95, int(variance_pct)))
            except:
                pass
        if runs is not None:
            try:
                S.bs_saga_dev_gain_runs = max(1, min(500, int(runs)))
            except:
                pass
        return {
            "ok": True,
            "exp_base": int(getattr(S, "bs_saga_dev_gain_exp_base", 120) or 120),
            "gold_base": int(getattr(S, "bs_saga_dev_gain_gold_base", 90) or 90),
            "variance_pct": int(getattr(S, "bs_saga_dev_gain_variance_pct", 35) or 35),
            "runs": int(getattr(S, "bs_saga_dev_gain_runs", 1) or 1),
        }

    def bs_saga_dev_apply_semirandom_gain(runs=None):
        if not bs_saga_dev_can_edit_account():
            return {"ok": False, "error": "admin_disabled"}
        base_exp = max(1, int(getattr(S, "bs_saga_dev_gain_exp_base", 120) or 120))
        base_gold = max(1, int(getattr(S, "bs_saga_dev_gain_gold_base", 90) or 90))
        var_pct = max(0, min(95, int(getattr(S, "bs_saga_dev_gain_variance_pct", 35) or 35)))
        rr = int(getattr(S, "bs_saga_dev_gain_runs", 1) or 1) if runs is None else int(runs or 1)
        rr = max(1, min(500, rr))
        variance = float(var_pct) / 100.0
        exp_sum = 0
        gold_sum = 0
        for _ in range(rr):
            exp_roll = 1.0 + random.uniform(-variance, variance)
            gold_roll = 1.0 + random.uniform(-variance, variance)
            exp_sum += max(0, int(round(float(base_exp) * exp_roll)))
            gold_sum += max(0, int(round(float(base_gold) * gold_roll)))
        report = bs_saga_gain_account_rewards(exp_sum, gold_sum, source="dev_semirandom_gain")
        bs_saga_set_message(
            "Ganancia semi-random: +{} EXP, +{} oro en {} duelo(s).".format(exp_sum, gold_sum, rr)
        )
        report["runs"] = int(rr)
        report["variance_pct"] = int(var_pct)
        return report

    def bs_saga_estimate_duels_to_targets(target_exp=1000, target_gold=5000):
        base_exp = max(1, int(getattr(S, "bs_saga_dev_gain_exp_base", 120) or 120))
        base_gold = max(1, int(getattr(S, "bs_saga_dev_gain_gold_base", 90) or 90))
        try:
            need_exp = max(0, int(target_exp or 0))
        except:
            need_exp = 0
        try:
            need_gold = max(0, int(target_gold or 0))
        except:
            need_gold = 0
        duels_for_exp = int(math.ceil(float(need_exp) / float(base_exp))) if need_exp > 0 else 0
        duels_for_gold = int(math.ceil(float(need_gold) / float(base_gold))) if need_gold > 0 else 0
        duels_needed = max(duels_for_exp, duels_for_gold)
        return {
            "ok": True,
            "target_exp": int(need_exp),
            "target_gold": int(need_gold),
            "expected_exp_per_duel": int(base_exp),
            "expected_gold_per_duel": int(base_gold),
            "duels_for_exp": int(duels_for_exp),
            "duels_for_gold": int(duels_for_gold),
            "duels_needed": int(duels_needed),
        }

    def bs_saga_audit_push(event_name, payload):
        rows = getattr(S, "bs_saga_audit_log", None)
        if not isinstance(rows, list):
            rows = []
            S.bs_saga_audit_log = rows
        rows.append({
            "event": str(event_name or ""),
            "payload": payload if isinstance(payload, dict) else {}
        })
        if len(rows) > 120:
            del rows[:-120]
        return None

    def bs_saga_buy_hero(hero_row):
        if not isinstance(hero_row, dict):
            bs_saga_set_message("Compra inválida: héroe no encontrado.")
            return False
        acc = bs_saga_account()
        heroes_owned = getattr(S, "bs_saga_heroes_owned", {})
        if not isinstance(heroes_owned, dict):
            heroes_owned = {}
            S.bs_saga_heroes_owned = heroes_owned

        hero_id = bs_saga_hero_id(hero_row)
        hero_name = str(hero_row.get("name", hero_id) or hero_id)
        price = bs_saga_hero_price(hero_row)
        gold_before = bs_saga_gold()
        inf_gold = bool(getattr(S, "bs_saga_dev_infinite_gold", False)) and bs_saga_dev_can_edit_account()

        if bs_saga_hero_is_owned(hero_id):
            bs_saga_set_message("Ya posees a {}.".format(hero_name))
            return False
        if (not inf_gold) and gold_before < price:
            bs_saga_set_message("Oro insuficiente para {} ({}).".format(hero_name, price))
            return False

        gold_after = gold_before if inf_gold else (gold_before - price)
        acc["gold"] = gold_after
        heroes_owned[hero_id] = {
            "hero_id": hero_id,
            "owned": True,
            "level": 1,
            "exp": 0,
            "is_rotation_free": False,
            "name": hero_name,
            "tier": str(hero_row.get("tier", "C") or "C").upper()
        }
        _tier_now = bs_saga_refresh_account_tier(reason="buy_hero")
        bs_saga_audit_push("buy_hero", {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "price_gold": price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        bs_saga_audit_push("gold_delta", {
            "reason": "buy_hero",
            "delta": 0 if inf_gold else -price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        if _tier_now:
            bs_saga_set_message("Compraste a {} por {} oro. Tier actual: {}.".format(hero_name, price, _tier_now))
        else:
            bs_saga_set_message("Compraste a {} por {} oro. Aún sin tier (sigue coleccionando).".format(hero_name, price))
        return True

    def bs_saga_buy_hero_from_ui(hero_row):
        # Wrapper para acciones de botón en screens:
        # evita que el retorno bool de bs_saga_buy_hero
        # interfiera con el flujo de navegación del screen.
        bs_saga_buy_hero(hero_row)
        return None

    def bs_saga_item_id(item_row):
        if not isinstance(item_row, dict):
            return "unknown_item"
        if item_row.get("item_id"):
            return str(item_row.get("item_id"))
        return bs_saga_slug(item_row.get("name", "item"))

    def bs_saga_item_price(item_row):
        if not isinstance(item_row, dict):
            return 0
        try:
            price = int(item_row.get("price_gold", 0))
        except:
            price = 0
        if price > 0:
            return price
        rarity = str(item_row.get("rarity", "") or "").strip().lower()
        if rarity in ("epic", "legendary", "mythic", "infernal"):
            return 900
        if rarity in ("rare", "special"):
            return 600
        return 300

    def bs_saga_item_bucket(item_row):
        cat = str(getattr(S, "bs_saga_catalog_category", "consumibles") or "consumibles").lower()
        if cat == "materiales":
            return "materials"
        if cat == "permanentes":
            return "equipables"
        return "consumables"

    def bs_saga_buy_item(item_row, qty=1):
        if not isinstance(item_row, dict):
            bs_saga_set_message("Compra inválida: item no encontrado.")
            return False
        acc = bs_saga_account()
        inv = getattr(S, "bs_saga_inventory_state", {})
        if not isinstance(inv, dict):
            inv = {"account_inventory": {"consumables": {}, "equipables": {}, "materials": {}}, "hero_inventories": {}}
            S.bs_saga_inventory_state = inv
        account_inv = inv.get("account_inventory", {})
        if not isinstance(account_inv, dict):
            account_inv = {"consumables": {}, "equipables": {}, "materials": {}}
            inv["account_inventory"] = account_inv
        for bucket in ("consumables", "equipables", "materials"):
            if not isinstance(account_inv.get(bucket), dict):
                account_inv[bucket] = {}

        try:
            q = int(qty)
        except:
            q = 1
        if q < 1:
            q = 1

        item_id = bs_saga_item_id(item_row)
        item_name = str(item_row.get("name", item_id) or item_id)
        unit_price = bs_saga_item_price(item_row)
        total_price = unit_price * q
        gold_before = bs_saga_gold()
        inf_gold = bool(getattr(S, "bs_saga_dev_infinite_gold", False)) and bs_saga_dev_can_edit_account()
        if (not inf_gold) and gold_before < total_price:
            bs_saga_set_message("Oro insuficiente para {} x{}.".format(item_name, q))
            return False

        bucket = bs_saga_item_bucket(item_row)
        bucket_data = account_inv.get(bucket, {})
        before_qty = int(bucket_data.get(item_id, 0) or 0)
        after_qty = before_qty + q
        bucket_data[item_id] = after_qty
        account_inv[bucket] = bucket_data

        gold_after = gold_before if inf_gold else (gold_before - total_price)
        acc["gold"] = gold_after

        bs_saga_audit_push("buy_item", {
            "item_id": item_id,
            "item_name": item_name,
            "qty": q,
            "bucket": bucket,
            "unit_price_gold": unit_price,
            "price_gold": total_price,
            "gold_before": gold_before,
            "gold_after": gold_after,
            "qty_before": before_qty,
            "qty_after": after_qty
        })
        bs_saga_audit_push("gold_delta", {
            "reason": "buy_item",
            "delta": 0 if inf_gold else -total_price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        bs_saga_set_message("Compraste {} x{} por {} oro.".format(item_name, q, total_price))
        return True

    def bs_saga_account_bucket_qty(bucket, item_id):
        inv = bs_saga_inventory_bootstrap()
        chest = inv.get("account_inventory", {})
        data = chest.get(str(bucket or ""), {})
        if not isinstance(data, dict):
            return 0
        try:
            return int(data.get(str(item_id or ""), 0) or 0)
        except:
            return 0

    def bs_saga_account_bucket_add(bucket, item_id, delta):
        inv = bs_saga_inventory_bootstrap()
        chest = inv.get("account_inventory", {})
        b = str(bucket or "").strip().lower()
        if b not in ("consumables", "equipables", "materials"):
            return 0
        data = chest.get(b, {})
        if not isinstance(data, dict):
            data = {}
        iid = str(item_id or "").strip()
        try:
            d = int(delta or 0)
        except:
            d = 0
        before = int(data.get(iid, 0) or 0)
        after = before + d
        if after <= 0:
            if iid in data:
                del data[iid]
            after = 0
        else:
            data[iid] = after
        chest[b] = data
        inv["account_inventory"] = chest
        return after

    def bs_saga_ui_hub_economy_split_status_v1():
        return {
            "module": "ui_hub_audit_economy",
            "status": "phase_4_done",
            "migrated_symbols": [
                "bs_saga_account",
                "bs_saga_gold",
                "bs_saga_set_message",
                "bs_saga_dev_can_edit_account",
                "bs_saga_dev_set_account_state",
                "bs_saga_exp_required_for_level",
                "bs_saga_gain_account_rewards",
                "bs_saga_dev_set_gain_profile",
                "bs_saga_dev_apply_semirandom_gain",
                "bs_saga_estimate_duels_to_targets",
                "bs_saga_audit_push",
                "bs_saga_buy_hero",
                "bs_saga_buy_hero_from_ui",
                "bs_saga_item_id",
                "bs_saga_item_price",
                "bs_saga_item_bucket",
                "bs_saga_buy_item",
                "bs_saga_account_bucket_qty",
                "bs_saga_account_bucket_add"
            ]
        }
