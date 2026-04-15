# ============================================================
# 12_BATTLESTARS_SAGA_UI_HUB_V1.rpy
# Lobby in-game Battlestars Saga (Wireframe funcional v1)
# ============================================================

default bs_saga_main_menu_enabled = True

default bs_saga_tournament_panel_open = False

default bs_saga_lobby_bottom_tab = "none"
default bs_saga_heroes_tier = "C"
default bs_saga_heroes_franchise = "all"
default bs_saga_catalog_category = "consumibles"
default bs_saga_catalog_group = "pociones"
default bs_saga_tech_catalog_tier = "C"
default bs_saga_tech_catalog_mode = ""
default bs_saga_tech_catalog_type = "ofensivas"
default bs_saga_tower_tier_filter = "ALL"
default bs_saga_tower_selected_floor = 1
default bs_saga_account_state = {
    "account_id": "local_player",
    "display_name": "Mistico",
    "level": 1,
    "exp": 0,
    "exp_to_next": 100,
    "tier": "",
    "gold": 5000,
    "gems": 0
}
default bs_saga_tier_hero_requirements = {
    "C": 20,
    "B": 15,
    "A": 10,
    "S": 5,
    "SS": 4,
    "SSS": 3,
    "IV": 1
}
default bs_saga_tier_level_requirements = {
    "C": 1,
    "B": 5,
    "A": 10,
    "S": 15,
    "SS": 20,
    "SSS": 25,
    "IV": 30
}
default bs_saga_tier_duel_pool = {
    "C": 1000,
    "B": 5000,
    "A": 10000,
    "S": 50000,
    "SS": 100000,
    "SSS": 500000,
    "IV": 1000000
}
default bs_saga_tier_core_stats = {
    "C": {"hp": 5000, "ep": 15000, "ec": 1000, "durability": 0, "cover": 0},
    "B": {"hp": 25000, "ep": 75000, "ec": 5000, "durability": 0, "cover": 0},
    # Nota de balance: para A/S se mantiene HP > durability > cover
    # y relación objetivo durability = cover * 10.
    "A": {"hp": 60000, "ep": 180000, "ec": 10000, "durability": 12000, "cover": 1200},
    "S": {"hp": 350000, "ep": 1000000, "ec": 50000, "durability": 50000, "cover": 5000},
    "SS": {"hp": 700000, "ep": 2000000, "ec": 100000, "durability": 60000, "cover": 60000},
    "SSS": {"hp": 3500000, "ep": 10000000, "ec": 500000, "durability": 300000, "cover": 300000},
    "IV": {"hp": 7000000, "ep": 20000000, "ec": 1000000, "durability": 600000, "cover": 600000}
}
default bs_saga_tier_combat_tuning = {
    "C": {"hp_factor": 5.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "B": {"hp_factor": 5.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "A": {"hp_factor": 6.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "S": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "SS": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "SSS": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "IV": {"hp_factor": 7.0, "rest_hp_pct": 0.03}
}
default bs_saga_damage_coherence_rules = {
    "normal_hit_min_pct": 0.08,
    "normal_hit_max_pct": 0.12,
    "combo_hit_min_pct": 0.18,
    "combo_hit_max_pct": 0.25
}
default bs_saga_heroes_owned = {}
default bs_saga_inventory_state = {
    "account_inventory": {
        "consumables": {},
        "equipables": {},
        "materials": {}
    },
    "hero_inventories": {}
}
default bs_saga_audit_log = []
default bs_saga_last_tx_message = ""
default bs_saga_rotation_hero_ids = []
default bs_saga_prep_duel_rotation_ids = []
default bs_saga_hero_usage_stats = {}
default bs_saga_prep_selected_hero = ""
default bs_saga_prep_selected_mode = "1v1"
default bs_saga_prep_enemy_mode = "random"
default bs_saga_prep_selected_enemy_hero = ""
default bs_saga_prep_selected_build = "balanceado"
default bs_saga_prep_selected_config = "cfg1"
default bs_saga_prep_selected_party_ids = []
default bs_saga_prep_filter_owned_only = False
default bs_saga_prep_flag_item_id = ""
default bs_saga_prep_flag_consumable_id = ""
default bs_saga_prep_intent_duel = False
default bs_saga_prep_context = "room"  # room | staging
default bs_saga_heroes_scroll_y = 0.0
default bs_saga_hero_tech_builds = {}
default bs_saga_dev_admin_enabled = True
default bs_saga_dev_infinite_gold = False
default bs_saga_dev_low_spec_mode = False

init -880 python:
    import renpy.store as S
    import re
    import time

    def bs_saga_slug(text):
        raw = str(text or "").strip().lower()
        raw = re.sub(r"[^a-z0-9]+", "_", raw)
        raw = re.sub(r"_+", "_", raw)
        return raw.strip("_") or "unknown"

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

    def bs_saga_dev_toggle_infinite_gold(enabled=None):
        if not bs_saga_dev_can_edit_account():
            return False
        if enabled is None:
            S.bs_saga_dev_infinite_gold = not bool(getattr(S, "bs_saga_dev_infinite_gold", False))
        else:
            S.bs_saga_dev_infinite_gold = bool(enabled)
        state = "ON" if bool(getattr(S, "bs_saga_dev_infinite_gold", False)) else "OFF"
        bs_saga_set_message("DEV infinite gold: {}.".format(state))
        return True

    def bs_saga_dev_apply_low_spec_mode(enabled=True):
        if not bs_saga_dev_can_edit_account():
            return False
        flag = bool(enabled)
        S.bs_saga_dev_low_spec_mode = flag
        S.ui_safe_mode = flag
        S.ui_safe_mode_prompted = True
        S.ai_difficulty_hud_visible = False
        S.bs_battle_low_spec_mode = flag
        bs_saga_set_message("DEV low-spec mode: {}.".format("ON" if flag else "OFF"))
        return True

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

    def bs_saga_hero_id(hero_row):
        if not isinstance(hero_row, dict):
            return "unknown_hero"
        if hero_row.get("hero_id"):
            return str(hero_row.get("hero_id"))
        return bs_saga_slug(hero_row.get("name", "hero"))

    def bs_saga_hero_price(hero_row):
        if not isinstance(hero_row, dict):
            return 0
        try:
            price = int(hero_row.get("price_gold", 0))
        except:
            price = 0
        if price > 0:
            return price
        tier = str(hero_row.get("tier", "C") or "C").upper()
        if tier == "B":
            return 2500
        if tier == "A":
            return 5000
        return 1200

    def bs_saga_hero_is_owned(hero_id):
        owned = getattr(S, "bs_saga_heroes_owned", {})
        if not isinstance(owned, dict):
            return False
        item = owned.get(str(hero_id), {})
        return bool(isinstance(item, dict) and item.get("owned", False))

    def bs_saga_owned_heroes_count():
        owned = getattr(S, "bs_saga_heroes_owned", {})
        if not isinstance(owned, dict):
            return 0
        count = 0
        for _, row in owned.items():
            if isinstance(row, dict) and row.get("owned", False):
                count += 1
        return count

    def bs_saga_owned_heroes_count_by_tier(tier):
        t = str(tier or "").upper().strip()
        if not t:
            return 0
        owned = getattr(S, "bs_saga_heroes_owned", {})
        if not isinstance(owned, dict):
            return 0
        count = 0
        for _, row in owned.items():
            if not isinstance(row, dict):
                continue
            if not bool(row.get("owned", False)):
                continue
            rt = str(row.get("tier", "C") or "C").upper().strip()
            if rt == t:
                count += 1
        return count

    def bs_saga_eval_account_tier():
        acc = bs_saga_account()
        try:
            lvl = int(acc.get("level", 1) or 1)
        except:
            lvl = 1
        req_h = getattr(S, "bs_saga_tier_hero_requirements", {}) or {}
        req_l = getattr(S, "bs_saga_tier_level_requirements", {}) or {}
        order = ["IV", "SSS", "SS", "S", "A", "B", "C"]
        for t in order:
            heroes_req = int(req_h.get(t, 999999) or 999999)
            level_req = int(req_l.get(t, 1) or 1)
            if lvl < level_req:
                continue
            if bs_saga_owned_heroes_count_by_tier(t) >= heroes_req:
                return t
        return ""

    def bs_saga_refresh_account_tier(reason="runtime"):
        acc = bs_saga_account()
        prev = str(acc.get("tier", "") or "").upper().strip()
        now = str(bs_saga_eval_account_tier() or "").upper().strip()
        if prev == now:
            return now
        acc["tier"] = now
        bs_saga_audit_push("account_tier_update", {
            "reason": str(reason or "runtime"),
            "tier_before": prev,
            "tier_after": now,
            "level": int(acc.get("level", 1) or 1),
        })
        return now

    def bs_saga_tier_progress_rows():
        req_h = getattr(S, "bs_saga_tier_hero_requirements", {}) or {}
        req_l = getattr(S, "bs_saga_tier_level_requirements", {}) or {}
        order = ["C", "B", "A", "S", "SS", "SSS", "IV"]
        acc = bs_saga_account()
        try:
            lvl = int(acc.get("level", 1) or 1)
        except:
            lvl = 1
        out = []
        for t in order:
            need_h = int(req_h.get(t, 999999) or 999999)
            need_l = int(req_l.get(t, 1) or 1)
            have_h = bs_saga_owned_heroes_count_by_tier(t)
            ok = bool(lvl >= need_l and have_h >= need_h)
            out.append({
                "tier": t,
                "need_heroes": need_h,
                "have_heroes": have_h,
                "need_level": need_l,
                "ok": ok,
            })
        return out

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

    def bs_saga_inventory_rows():
        if not bs_saga_inventory_contract_ok():
            return []
        inv = getattr(S, "bs_saga_inventory_state", {})
        account_inv = inv.get("account_inventory", {})
        rows = []
        for bucket in ("consumables", "equipables", "materials"):
            data = account_inv.get(bucket, {})
            if not isinstance(data, dict):
                continue
            for item_id, qty in data.items():
                try:
                    q = int(qty)
                except:
                    q = 0
                rows.append({
                    "bucket": bucket,
                    "item_id": str(item_id),
                    "qty": q
                })
        rows.sort(key=lambda r: (r.get("bucket", ""), r.get("item_id", "")))
        return rows

    def bs_saga_hero_inventory_slot_count():
        return 6

    def bs_saga_prep_config_keys():
        return ["cfg1", "cfg2", "cfg3"]

    def bs_saga_prep_build_keys():
        return ["balanceado", "ofensivo", "defensivo"]

    def bs_saga_inventory_bootstrap():
        inv = getattr(S, "bs_saga_inventory_state", None)
        if not isinstance(inv, dict):
            inv = {}
            S.bs_saga_inventory_state = inv
        chest = inv.get("account_inventory", None)
        if not isinstance(chest, dict):
            chest = {}
            inv["account_inventory"] = chest
        for k in ("consumables", "equipables", "materials"):
            if not isinstance(chest.get(k), dict):
                chest[k] = {}
        if not isinstance(inv.get("hero_inventories"), dict):
            inv["hero_inventories"] = {}
        return inv

    def bs_saga_hero_inventory_get(hero_id):
        hid = str(hero_id or "").strip()
        if not hid:
            return None
        inv = bs_saga_inventory_bootstrap()
        hero_inv = inv.get("hero_inventories", {})
        row = hero_inv.get(hid, None)
        if not isinstance(row, dict):
            row = {}
            hero_inv[hid] = row
        active_cfg = str(row.get("active_config", "cfg1") or "cfg1")
        if active_cfg not in bs_saga_prep_config_keys():
            active_cfg = "cfg1"
        row["active_config"] = active_cfg
        cfgs = row.get("configs", None)
        if not isinstance(cfgs, dict):
            cfgs = {}
        slot_count = bs_saga_hero_inventory_slot_count()
        for ck in bs_saga_prep_config_keys():
            cfg_row = cfgs.get(ck, None)
            if isinstance(cfg_row, list):
                # compat hacia atrás: lista directa => se replica en builds.
                base = []
                for v in cfg_row[:slot_count]:
                    base.append(str(v) if v else "")
                while len(base) < slot_count:
                    base.append("")
                cfgs[ck] = {"builds": {bk: list(base) for bk in bs_saga_prep_build_keys()}}
                continue
            if not isinstance(cfg_row, dict):
                cfg_row = {"builds": {}}
            builds = cfg_row.get("builds", {})
            if not isinstance(builds, dict):
                builds = {}
            for bk in bs_saga_prep_build_keys():
                slots = builds.get(bk, None)
                if not isinstance(slots, list):
                    slots = []
                clean = []
                for v in slots[:slot_count]:
                    clean.append(str(v) if v else "")
                while len(clean) < slot_count:
                    clean.append("")
                builds[bk] = clean
            cfg_row["builds"] = builds
            cfgs[ck] = cfg_row
        row["configs"] = cfgs
        hero_inv[hid] = row
        inv["hero_inventories"] = hero_inv
        return row

    def bs_saga_hero_loadout_slots(hero_id, config_id=None, build_id=None):
        row = bs_saga_hero_inventory_get(hero_id)
        if not isinstance(row, dict):
            return []
        cfg = str(config_id or row.get("active_config", "cfg1") or "cfg1")
        if cfg not in bs_saga_prep_config_keys():
            cfg = "cfg1"
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado").strip().lower()
        if bld not in bs_saga_prep_build_keys():
            bld = "balanceado"
        cfg_row = row.get("configs", {}).get(cfg, {})
        builds = cfg_row.get("builds", {}) if isinstance(cfg_row, dict) else {}
        slots = builds.get(bld, [])
        return list(slots) if isinstance(slots, list) else []

    def bs_saga_hero_set_loadout_slots(hero_id, slots, config_id=None, build_id=None):
        row = bs_saga_hero_inventory_get(hero_id)
        if not isinstance(row, dict):
            return False
        cfg = str(config_id or row.get("active_config", "cfg1") or "cfg1")
        if cfg not in bs_saga_prep_config_keys():
            cfg = "cfg1"
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado").strip().lower()
        if bld not in bs_saga_prep_build_keys():
            bld = "balanceado"
        cfgs = row.get("configs", {})
        cfg_row = cfgs.get(cfg, {})
        if not isinstance(cfg_row, dict):
            cfg_row = {"builds": {}}
        builds = cfg_row.get("builds", {})
        if not isinstance(builds, dict):
            builds = {}
        clean = []
        slot_count = bs_saga_hero_inventory_slot_count()
        for v in list(slots or [])[:slot_count]:
            clean.append(str(v) if v else "")
        while len(clean) < slot_count:
            clean.append("")
        builds[bld] = clean
        cfg_row["builds"] = builds
        cfgs[cfg] = cfg_row
        row["configs"] = cfgs
        row["active_config"] = cfg
        return True

    def bs_saga_set_prep_config(config_id):
        cfg = str(config_id or "").strip().lower()
        if cfg not in bs_saga_prep_config_keys():
            return False
        S.bs_saga_prep_selected_config = cfg
        hid = str(getattr(S, "bs_saga_prep_selected_hero", "") or "").strip()
        if hid:
            row = bs_saga_hero_inventory_get(hid)
            if isinstance(row, dict):
                row["active_config"] = cfg
        return True

    def bs_saga_set_prep_build(build_id):
        b = str(build_id or "").strip().lower()
        if b not in bs_saga_prep_build_keys():
            return False
        S.bs_saga_prep_selected_build = b
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

    def bs_saga_equip_item_to_hero(hero_id, item_id, slot_index=None, config_id=None, build_id=None):
        hid = str(hero_id or "").strip()
        iid = str(item_id or "").strip()
        if not hid or not iid:
            bs_saga_set_message("Equipar inválido: faltan héroe o item.")
            return False
        if bs_saga_account_bucket_qty("equipables", iid) <= 0:
            bs_saga_set_message("No tienes {} disponible en inventario de cuenta.".format(iid))
            return False
        row = bs_saga_hero_inventory_get(hid)
        if not isinstance(row, dict):
            return False
        cfg = str(config_id or row.get("active_config", "cfg1") or "cfg1")
        if cfg not in bs_saga_prep_config_keys():
            cfg = "cfg1"
        slots = bs_saga_hero_loadout_slots(hid, cfg, build_id)
        target = -1
        if slot_index is not None:
            try:
                idx = int(slot_index)
            except:
                idx = -1
            if 0 <= idx < len(slots):
                target = idx
        if target < 0:
            for i in range(len(slots)):
                if not str(slots[i] or "").strip():
                    target = i
                    break
        if target < 0:
            target = 0
        prev = str(slots[target] or "").strip()
        if prev:
            bs_saga_account_bucket_add("equipables", prev, 1)
        bs_saga_account_bucket_add("equipables", iid, -1)
        slots[target] = iid
        bs_saga_hero_set_loadout_slots(hid, slots, cfg, build_id)
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado")
        bs_saga_audit_push("equip_item", {"hero_id": hid, "config": cfg, "build": bld, "slot": target, "item_id": iid, "replaced": prev})
        bs_saga_set_message("Equipado {} en {} [{} · {} · slot {}].".format(iid, hid, cfg.upper(), bld, target + 1))
        return True

    def bs_saga_unequip_item_from_hero(hero_id, slot_index, config_id=None, build_id=None):
        hid = str(hero_id or "").strip()
        if not hid:
            return False
        row = bs_saga_hero_inventory_get(hid)
        if not isinstance(row, dict):
            return False
        cfg = str(config_id or row.get("active_config", "cfg1") or "cfg1")
        if cfg not in bs_saga_prep_config_keys():
            cfg = "cfg1"
        slots = bs_saga_hero_loadout_slots(hid, cfg, build_id)
        try:
            idx = int(slot_index)
        except:
            idx = -1
        if idx < 0 or idx >= len(slots):
            return False
        old = str(slots[idx] or "").strip()
        if not old:
            bs_saga_set_message("Slot vacío: no hay item para desequipar.")
            return False
        slots[idx] = ""
        bs_saga_account_bucket_add("equipables", old, 1)
        bs_saga_hero_set_loadout_slots(hid, slots, cfg, build_id)
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado")
        bs_saga_audit_push("unequip_item", {"hero_id": hid, "config": cfg, "build": bld, "slot": idx, "item_id": old})
        bs_saga_set_message("Desequipado {} de {} [{} · {} · slot {}].".format(old, hid, cfg.upper(), bld, idx + 1))
        return True

    def bs_saga_preparation_rows_filtered():
        rows = list(bs_saga_duel_combat_pool_rows() or [])
        only_owned = bool(getattr(S, "bs_saga_prep_filter_owned_only", False))
        if only_owned:
            rows = [r for r in rows if bool(r.get("owned", False))]
        return rows

    def bs_saga_hero_row(hero_id):
        hid = str(hero_id or "").strip()
        if not hid:
            return None
        for row in bs_saga_db_rows():
            if not isinstance(row, dict):
                continue
            rid = str(bs_saga_hero_id(row) or "").strip()
            if rid and rid.lower() == hid.lower():
                return row
        return None

    def bs_saga_hero_tier(hero_id, fallback="C"):
        row = bs_saga_hero_row(hero_id)
        if not isinstance(row, dict):
            return str(fallback or "C").upper()
        t = str(row.get("tier", fallback) or fallback).strip().upper()
        return t if t else str(fallback or "C").upper()

    def bs_saga_tier_pool_total(tier):
        t = str(tier or "C").strip().upper()
        table = getattr(S, "bs_saga_tier_duel_pool", {}) or {}
        try:
            return int(table.get(t, table.get("C", 1000)) or 1000)
        except:
            return 1000

    def bs_saga_tier_core_profile(tier):
        t = str(tier or "C").strip().upper()
        table = getattr(S, "bs_saga_tier_core_stats", {}) or {}
        base = table.get(t, table.get("C", {}))
        if not isinstance(base, dict):
            base = {}
        out = {
            "hp": int(base.get("hp", 1000) or 1000),
            "ep": int(base.get("ep", 1000) or 1000),
            "ec": int(base.get("ec", 1000) or 1000),
            "durability": int(base.get("durability", 0) or 0),
            "cover": int(base.get("cover", 0) or 0)
        }
        # Reglas actuales: C/B (y menores) sin durabilidad/cubre.
        if t in ("D", "C", "B"):
            out["durability"] = 0
            out["cover"] = 0
        # Reglas objetivo A/S: HP > durability > cover y ratio 1:10.
        elif t in ("A", "S"):
            if out["cover"] < 0:
                out["cover"] = 0
            if out["durability"] < 0:
                out["durability"] = 0

            # Evita armadura dominante: cap de cover ~15% HP.
            cover_cap = int(max(0, out["hp"]) * 0.15)
            if out["cover"] > cover_cap:
                out["cover"] = cover_cap

            # Durabilidad siempre al menos cover*10, pero nunca >= HP.
            min_dur = int(out["cover"] * 10)
            out["durability"] = max(int(out["durability"] or 0), min_dur)
            if out["durability"] >= out["hp"]:
                out["durability"] = max(0, int(out["hp"] - 1))
        return out

    def bs_saga_tier_combat_tuning_profile(tier):
        t = str(tier or "C").strip().upper()
        rows = getattr(S, "bs_saga_tier_combat_tuning", {}) or {}
        base = rows.get(t, rows.get("C", {}))
        if not isinstance(base, dict):
            base = {}
        try:
            hp_factor = float(base.get("hp_factor", 5.0) or 5.0)
        except:
            hp_factor = 5.0
        try:
            rest_hp_pct = float(base.get("rest_hp_pct", 0.05) or 0.05)
        except:
            rest_hp_pct = 0.05
        try:
            rest_ep_pct = float(base.get("rest_ep_pct", 0.20) or 0.20)
        except:
            rest_ep_pct = 0.20
        try:
            rest_ec_pct = float(base.get("rest_ec_pct", 0.20) or 0.20)
        except:
            rest_ec_pct = 0.20
        try:
            rest_ec_scales = int(base.get("rest_ec_scales", 2) or 2)
        except:
            rest_ec_scales = 2
        if hp_factor < 1.0:
            hp_factor = 1.0
        if rest_hp_pct < 0.0:
            rest_hp_pct = 0.0
        if rest_ep_pct < 0.0:
            rest_ep_pct = 0.0
        if rest_ec_pct < 0.0:
            rest_ec_pct = 0.0
        if rest_ec_scales < 0:
            rest_ec_scales = 0
        return {
            "hp_factor": hp_factor,
            "rest_hp_pct": rest_hp_pct,
            "rest_ep_pct": rest_ep_pct,
            "rest_ec_pct": rest_ec_pct,
            "rest_ec_scales": rest_ec_scales
        }

    def bs_saga_hero_tech_profile_get(hero_id, config_id=None, build_id=None):
        hid = str(hero_id or "").strip()
        if not hid:
            return None
        cfg = str(config_id or getattr(S, "bs_saga_prep_selected_config", "cfg1") or "cfg1")
        if cfg not in bs_saga_prep_config_keys():
            cfg = "cfg1"
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado").strip().lower()
        if bld not in bs_saga_prep_build_keys():
            bld = "balanceado"
        root = getattr(S, "bs_saga_hero_tech_builds", None)
        if not isinstance(root, dict):
            root = {}
            S.bs_saga_hero_tech_builds = root
        h = root.get(hid, None)
        if not isinstance(h, dict):
            h = {}
            root[hid] = h
        cfgs = h.get("configs", None)
        if not isinstance(cfgs, dict):
            cfgs = {}
        c = cfgs.get(cfg, None)
        if not isinstance(c, dict):
            c = {}
        builds = c.get("builds", None)
        if not isinstance(builds, dict):
            builds = {}
        item = builds.get(bld, None)
        if not isinstance(item, dict):
            tier = bs_saga_hero_tier(hid, "C")
            item = {
                "mode": "virgen",
                "tier": tier,
                "pool_total": bs_saga_tier_pool_total(tier),
                "pool_spent_off": 0,
                "pool_spent_def": 0,
                "tech_points": {}
            }
        if str(item.get("mode", "virgen") or "virgen") not in ("virgen", "preconfig"):
            item["mode"] = "virgen"
        if not isinstance(item.get("tech_points", {}), dict):
            item["tech_points"] = {}
        try:
            item["pool_total"] = int(item.get("pool_total", bs_saga_tier_pool_total(item.get("tier", "C"))) or bs_saga_tier_pool_total(item.get("tier", "C")))
        except:
            item["pool_total"] = bs_saga_tier_pool_total(item.get("tier", "C"))
        item["tier"] = str(item.get("tier", bs_saga_hero_tier(hid, "C")) or bs_saga_hero_tier(hid, "C")).upper()
        builds[bld] = item
        c["builds"] = builds
        cfgs[cfg] = c
        h["configs"] = cfgs
        root[hid] = h
        S.bs_saga_hero_tech_builds = root
        return item

    def bs_saga_resolve_hero_tech_profile(hero_id, config_id=None, build_id=None):
        """
        Resuelve perfil final para combate:
        - mode=virgen => tech_points vacíos.
        - mode=preconfig => intenta preset externo y cae a tech_points guardados.
        """
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return {}
        out = dict(item)
        mode = str(out.get("mode", "virgen") or "virgen").strip().lower()
        if mode == "virgen":
            out["tech_points"] = {}
            out["pool_spent_off"] = 0
            out["pool_spent_def"] = 0
            return out
        preset = None
        try:
            fn = getattr(S, "bs_get_hero_tech_preset_v1", None)
            if callable(fn):
                preset = fn(str(hero_id or ""), str(out.get("tier", "C") or "C"))
        except:
            preset = None
        if isinstance(preset, dict):
            tech_points = preset.get("tech_points", {})
            if isinstance(tech_points, dict):
                out["tech_points"] = dict(tech_points)
            try:
                out["pool_spent_off"] = int(preset.get("pool_spent_off", out.get("pool_spent_off", 0)) or 0)
            except:
                pass
            try:
                out["pool_spent_def"] = int(preset.get("pool_spent_def", out.get("pool_spent_def", 0)) or 0)
            except:
                pass
        return out

    def bs_saga_hero_tech_mode_set(hero_id, mode, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        m = str(mode or "").strip().lower()
        if m not in ("virgen", "preconfig"):
            return False
        item["mode"] = m
        bs_saga_set_message("Técnicas {}: modo {}.".format(str(hero_id or ""), m))
        return True

    def bs_saga_hero_tech_points_set(hero_id, tech_key, points, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        key = str(tech_key or "").strip().lower()
        if not key:
            return False
        try:
            val = int(points or 0)
        except:
            val = 0
        if val < 0:
            val = 0
        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}
        tp[key] = val
        item["tech_points"] = tp
        return True

    def bs_saga_exp_progress():
        acc = bs_saga_account()
        try:
            exp_now = float(acc.get("exp", 0) or 0)
        except:
            exp_now = 0.0
        try:
            exp_next = float(acc.get("exp_to_next", 100) or 100)
        except:
            exp_next = 100.0
        if exp_next <= 0:
            return 0.0
        ratio = exp_now / exp_next
        if ratio < 0.0:
            ratio = 0.0
        if ratio > 1.0:
            ratio = 1.0
        return ratio

    def bs_saga_now_ts():
        try:
            return int(time.time())
        except:
            return 0

    def bs_saga_register_hero_usage(hero_id):
        hid = str(hero_id or "").strip().lower()
        if not hid:
            return None
        rows = getattr(S, "bs_saga_hero_usage_stats", None)
        if not isinstance(rows, dict):
            rows = {}
            S.bs_saga_hero_usage_stats = rows
        item = rows.get(hid, {})
        if not isinstance(item, dict):
            item = {"total": 0, "last_used_ts": 0, "last24": 0}
        now_ts = bs_saga_now_ts()
        prev_ts = int(item.get("last_used_ts", 0) or 0)
        if prev_ts > 0 and (now_ts - prev_ts) > 86400:
            item["last24"] = 0
        item["total"] = int(item.get("total", 0) or 0) + 1
        item["last24"] = int(item.get("last24", 0) or 0) + 1
        item["last_used_ts"] = now_ts
        rows[hid] = item
        return None

    def bs_saga_top_heroes(limit=3, last24=False):
        rows = getattr(S, "bs_saga_hero_usage_stats", {})
        if not isinstance(rows, dict):
            return []
        out = []
        now_ts = bs_saga_now_ts()
        for hid, info in rows.items():
            if not isinstance(info, dict):
                continue
            total = int(info.get("total", 0) or 0)
            last_used_ts = int(info.get("last_used_ts", 0) or 0)
            last24_count = int(info.get("last24", 0) or 0)
            if last24 and last_used_ts > 0 and (now_ts - last_used_ts) > 86400:
                last24_count = 0
            score = last24_count if last24 else total
            if score <= 0:
                continue
            out.append({"hero_id": str(hid), "score": score})
        out.sort(key=lambda r: (-int(r.get("score", 0)), r.get("hero_id", "")))
        return out[:int(limit or 3)]

    def bs_saga_available_hero_rows():
        rot = getattr(S, "bs_saga_rotation_hero_ids", [])
        if not isinstance(rot, list):
            rot = []
        if len(rot) < 5:
            bs_saga_refresh_rotation_heroes(5)
            rot = getattr(S, "bs_saga_rotation_hero_ids", [])
        rows = []
        for r in bs_saga_db_rows():
            if not isinstance(r, dict):
                continue
            hid = bs_saga_hero_id(r)
            name = str(r.get("name", hid) or hid)
            tier = str(r.get("tier", "C") or "C").upper()
            in_rotation = hid.lower() in [str(x).lower() for x in (rot or [])]
            is_owned = bs_saga_hero_is_owned(hid)
            state = "disponible" if is_owned else ("para_probar" if in_rotation else "bloqueado")
            rows.append({
                "hero_id": hid,
                "name": name,
                "tier": tier,
                "owned": bool(is_owned),
                "in_rotation": bool(in_rotation),
                "available": bool(is_owned or in_rotation),
                "state": state
            })
        rows.sort(key=lambda x: (x.get("tier", "Z"), x.get("name", "")))
        return rows

    def bs_saga_combat_ready_ids():
        fn_pool = getattr(S, "get_combat_character_ids", None)
        if callable(fn_pool):
            out = list(fn_pool(True) or [])
            if out:
                return [str(x) for x in out if str(x)]
        out = []
        for row in bs_saga_db_rows():
            if not isinstance(row, dict):
                continue
            hid = str(bs_saga_hero_id(row) or "").strip()
            if hid:
                out.append(hid)
        # Asegurar que los héroes comprados aparezcan siempre en preparación,
        # aunque get_combat_character_ids() no los incluya todavía.
        owned = getattr(S, "bs_saga_heroes_owned", {}) or {}
        if isinstance(owned, dict):
            for hid, info in owned.items():
                if not isinstance(info, dict):
                    continue
                if not bool(info.get("owned", False)):
                    continue
                h = str(hid or "").strip()
                if h:
                    out.append(h)
        unique = []
        seen = {}
        for hid in out:
            k = hid.lower()
            if seen.get(k):
                continue
            seen[k] = True
            unique.append(hid)
        return unique

    def bs_saga_duel_combat_pool_rows():
        ready = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        rot = getattr(S, "bs_saga_prep_duel_rotation_ids", None)
        if not isinstance(rot, list) or not rot:
            rot = bs_saga_refresh_duel_rotation_heroes(min(5, len(ready)))
        rot_lc = {str(x).lower() for x in (rot or [])}

        out = []
        for cid in ready:
            is_owned = bs_saga_hero_is_owned(cid)
            in_rotation = cid.lower() in rot_lc
            state = "disponible" if is_owned else ("para_probar" if in_rotation else "bloqueado")
            row = bs_saga_hero_row(cid)
            if isinstance(row, dict):
                name = str(row.get("name", cid) or cid)
                tier = str(row.get("tier", "C") or "C").upper()
            else:
                name = str(cid)
                tier = "C"
            out.append({
                "hero_id": cid,
                "name": name,
                "tier": tier,
                "owned": bool(is_owned),
                "in_rotation": bool(in_rotation),
                "available": bool(is_owned or in_rotation),
                "state": state
            })
        return out

    def bs_saga_refresh_duel_rotation_heroes(count=4):
        pool = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        unique = []
        for hid in pool:
            if hid not in unique:
                unique.append(hid)
        if not unique:
            S.bs_saga_prep_duel_rotation_ids = []
            return []
        renpy.random.shuffle(unique)
        c = int(count or 4)
        if c < 1:
            c = 1
        if len(unique) < c:
            c = len(unique)
        S.bs_saga_prep_duel_rotation_ids = unique[:c]
        return list(S.bs_saga_prep_duel_rotation_ids)

    def bs_saga_resolve_combat_id(hero_id, fallback=""):
        hid = str(hero_id or "").strip()
        ready = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        if hid in ready:
            return hid
        fb = str(fallback or "").strip()
        if fb in ready:
            return fb
        return str(ready[0] if ready else "")

    def bs_saga_refresh_rotation_heroes(count=5):
        rows = []
        for r in bs_saga_db_rows():
            if not isinstance(r, dict):
                continue
            hid = bs_saga_hero_id(r)
            if hid:
                rows.append(str(hid))
        unique = []
        for hid in rows:
            if hid not in unique:
                unique.append(hid)
        if not unique:
            S.bs_saga_rotation_hero_ids = []
            return []
        renpy.random.shuffle(unique)
        c = int(count or 5)
        if c < 1:
            c = 1
        if len(unique) < c:
            while len(unique) < c:
                unique.append(unique[len(unique) % max(1, len(unique))])
        S.bs_saga_rotation_hero_ids = unique[:c]
        return list(S.bs_saga_rotation_hero_ids)

    def bs_saga_set_prep_hero(hero_id):
        hid = bs_saga_resolve_combat_id(hero_id, fallback="")
        rows = bs_saga_duel_combat_pool_rows()
        if not hid:
            bs_saga_set_message("Héroe no compatible todavía con runtime de combate.")
            return False
        for row in rows:
            if str(row.get("hero_id", "")) != hid:
                continue
            if not bool(row.get("available", False)):
                bs_saga_set_message("Héroe no disponible (sin compra ni rotación).")
                return False
            S.bs_saga_prep_selected_hero = hid
            inv = bs_saga_hero_inventory_get(hid)
            if isinstance(inv, dict):
                cfg = str(inv.get("active_config", "cfg1") or "cfg1")
                if cfg in bs_saga_prep_config_keys():
                    S.bs_saga_prep_selected_config = cfg
            bs_saga_set_message("Preparación: héroe activo = {}.".format(str(row.get("name", hid))))
            return True
        bs_saga_set_message("Héroe no encontrado para preparación.")
        return False

    def bs_saga_toggle_prep_party_hero(hero_id):
        hid = bs_saga_resolve_combat_id(hero_id, fallback="")
        if not hid:
            return False
        rows = bs_saga_duel_combat_pool_rows()
        allowed = False
        for row in rows:
            if str(row.get("hero_id", "")) == hid and bool(row.get("available", False)):
                allowed = True
                break
        if not allowed:
            bs_saga_set_message("No puedes agregar héroes bloqueados al equipo.")
            return False
        party = getattr(S, "bs_saga_prep_selected_party_ids", None)
        if not isinstance(party, list):
            party = []
        clean = []
        for v in party:
            vv = str(v or "").strip()
            if vv and vv not in clean:
                clean.append(vv)
        party = clean
        if hid in party:
            party = [x for x in party if x != hid]
            if str(getattr(S, "bs_saga_prep_selected_hero", "") or "") == hid:
                S.bs_saga_prep_selected_hero = str(party[0] if party else "")
            bs_saga_set_message("Equipo: removido {}.".format(hid))
        else:
            mode = str(getattr(S, "bs_saga_prep_selected_mode", "1v1") or "1v1")
            max_party = 2 if mode == "2v2" else 1
            if len(party) >= max_party:
                bs_saga_set_message("Equipo lleno para modo {} (máx {}).".format(mode, max_party))
                return False
            party.append(hid)
            if not str(getattr(S, "bs_saga_prep_selected_hero", "") or ""):
                S.bs_saga_prep_selected_hero = hid
            bs_saga_set_message("Equipo: agregado {}.".format(hid))
        S.bs_saga_prep_selected_party_ids = party
        return True

    def bs_saga_set_prep_mode(mode):
        m = str(mode or "").strip().lower()
        if m not in ("1v1", "2v2"):
            return False
        S.bs_saga_prep_selected_mode = m
        max_party = 2 if m == "2v2" else 1
        party = getattr(S, "bs_saga_prep_selected_party_ids", None)
        if not isinstance(party, list):
            party = []
        clean = []
        for hid in party:
            vv = bs_saga_resolve_combat_id(hid, fallback="")
            if vv and vv not in clean:
                clean.append(vv)
        S.bs_saga_prep_selected_party_ids = clean[:max_party]
        if S.bs_saga_prep_selected_party_ids:
            S.bs_saga_prep_selected_hero = str(S.bs_saga_prep_selected_party_ids[0])
        return True

    def bs_saga_set_prep_enemy(hero_id):
        hid = bs_saga_resolve_combat_id(hero_id, fallback="")
        if not hid:
            return False
        S.bs_saga_prep_selected_enemy_hero = hid
        bs_saga_set_message("Preparación: enemigo manual = {}.".format(hid))
        return True

    def bs_saga_prep_inventory_candidates(bucket_name):
        rows = bs_saga_inventory_rows()
        out = []
        target = str(bucket_name or "").strip().lower()
        for row in rows:
            if str(row.get("bucket", "")).lower() != target:
                continue
            qty = int(row.get("qty", 0) or 0)
            if qty <= 0:
                continue
            out.append({
                "item_id": str(row.get("item_id", "")),
                "qty": qty
            })
        return out

    def bs_saga_set_prep_flag(flag_type, item_id):
        ftype = str(flag_type or "").strip().lower()
        iid = str(item_id or "").strip()
        if ftype == "item":
            S.bs_saga_prep_flag_item_id = iid
            bs_saga_set_message("Preparación: item marcado = {}.".format(iid or "ninguno"))
            return True
        if ftype == "consumable":
            S.bs_saga_prep_flag_consumable_id = iid
            bs_saga_set_message("Preparación: consumible marcado = {}.".format(iid or "ninguno"))
            return True
        return False

    def bs_saga_precombat_contract_validate():
        """
        Contrato de validación final pre-duelo.
        Devuelve checks + estado bloqueante para staging/verify/launch.
        """
        mode = str(getattr(S, "bs_saga_prep_selected_mode", "1v1") or "1v1").strip().lower()
        if mode not in ("1v1", "2v2"):
            mode = "1v1"

        hero = str(getattr(S, "bs_saga_prep_selected_hero", "") or "").strip()
        enemy_mode = str(getattr(S, "bs_saga_prep_enemy_mode", "random") or "random").strip().lower()
        enemy_manual = str(getattr(S, "bs_saga_prep_selected_enemy_hero", "") or "").strip()
        cfg = str(getattr(S, "bs_saga_prep_selected_config", "cfg1") or "cfg1")
        bld = str(getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado")

        party = getattr(S, "bs_saga_prep_selected_party_ids", None)
        if not isinstance(party, list):
            party = []
        party = [str(x or "").strip() for x in party if str(x or "").strip()]
        # dedupe preserve order
        party_u = []
        for p in party:
            if p not in party_u:
                party_u.append(p)
        party = party_u

        required_party = 2 if mode == "2v2" else 1
        checks = []

        checks.append({
            "id": "hero_selected",
            "ok": bool(hero),
            "severity": "block",
            "label": "Héroe activo seleccionado",
            "detail": hero or "Falta seleccionar héroe."
        })

        checks.append({
            "id": "party_size",
            "ok": len(party) >= required_party,
            "severity": "block",
            "label": "Equipo completo para modo {}".format(mode),
            "detail": "Actual: {} / Requerido: {}".format(len(party), required_party)
        })

        checks.append({
            "id": "enemy_manual",
            "ok": (enemy_mode != "manual") or bool(enemy_manual),
            "severity": "block",
            "label": "Rival válido",
            "detail": "manual={}".format(enemy_manual or "sin seleccionar")
        })

        # warning: loadout mínimo recomendado (no bloquea)
        loadout = bs_saga_hero_loadout_slots(hero, cfg, bld) if hero else []
        equipped = len([x for x in (loadout or []) if str(x or "").strip()])
        checks.append({
            "id": "loadout_min",
            "ok": equipped >= 1,
            "severity": "warn",
            "label": "Loadout recomendado (>=1 slot equipado)",
            "detail": "Equipados: {}/6".format(int(equipped))
        })

        # warning: coherencia pool técnico si está en preconfig
        tp = bs_saga_hero_tech_profile_get(hero, cfg, bld) if hero else {}
        mode_tp = str((tp or {}).get("mode", "virgen") or "virgen").strip().lower()
        pool_total = int((tp or {}).get("pool_total", 0) or 0)
        spent_off = int((tp or {}).get("pool_spent_off", 0) or 0)
        spent_def = int((tp or {}).get("pool_spent_def", 0) or 0)
        spent_total = int(spent_off + spent_def)
        ok_pool = True if mode_tp != "preconfig" else (spent_total <= pool_total)
        checks.append({
            "id": "pool_consistency",
            "ok": ok_pool,
            "severity": "block" if mode_tp == "preconfig" else "warn",
            "label": "Pool técnico consistente",
            "detail": "Modo={} · Gastado {} / Total {}".format(mode_tp, spent_total, pool_total)
        })

        blocking = [c for c in checks if (str(c.get("severity", "warn")) == "block" and (not bool(c.get("ok", False))))]
        warnings = [c for c in checks if (str(c.get("severity", "warn")) == "warn" and (not bool(c.get("ok", False))))]
        return {
            "ok": len(blocking) == 0,
            "blocking": blocking,
            "warnings": warnings,
            "checks": checks,
            "mode": mode,
            "hero": hero,
            "party_count": len(party),
            "required_party": required_party
        }

    def bs_saga_apply_preparation_for_duel():
        mode = str(getattr(S, "bs_saga_prep_selected_mode", "1v1") or "1v1")
        party = getattr(S, "bs_saga_prep_selected_party_ids", None)
        if not isinstance(party, list):
            party = []
        party = [bs_saga_resolve_combat_id(x, fallback="") for x in party]
        party = [x for x in party if x]
        clean_party = []
        for hid in party:
            if hid not in clean_party:
                clean_party.append(hid)
        party = clean_party
        if not party:
            fallback_hero = bs_saga_resolve_combat_id(getattr(S, "bs_saga_prep_selected_hero", ""), fallback="")
            if fallback_hero:
                party = [fallback_hero]
        my_hero = str(party[0] if party else "")
        if not my_hero:
            bs_saga_set_message("Selecciona tu héroe antes de iniciar duelo.")
            return False

        # Inicializar identidad base siempre antes de calcular equipos.
        S.battle_player_id = my_hero
        S.battle_team_mode = mode if mode in ("1v1", "2v2") else "1v1"
        all_ids = [str(x.get("hero_id", "")) for x in bs_saga_duel_combat_pool_rows() if str(x.get("hero_id", ""))]
        if my_hero not in all_ids:
            all_ids.append(my_hero)
        enemy_mode = str(getattr(S, "bs_saga_prep_enemy_mode", "random") or "random")
        enemy_manual = bs_saga_resolve_combat_id(getattr(S, "bs_saga_prep_selected_enemy_hero", ""), fallback="")
        enemy_id = ""
        if enemy_mode == "manual" and enemy_manual:
            enemy_id = enemy_manual
        else:
            candidates = [x for x in all_ids if x != my_hero]
            if not candidates:
                bs_saga_set_message("No hay rival disponible en el roster de preparación.")
                return False
            enemy_id = str(candidates[renpy.random.randint(0, len(candidates) - 1)])
        if not enemy_id:
            bs_saga_set_message("No se pudo resolver rival de combate.")
            return False

        # Dual-write obligatorio: id activo + listas para evitar fallbacks legacy inconsistentes.
        S.battle_enemy_id = enemy_id
        S.battle_player_ids = [my_hero]
        S.battle_enemy_ids = [enemy_id]
        if S.battle_team_mode == "2v2":
            if len(party) >= 2:
                p2 = party[1]
            else:
                candidates = [x for x in all_ids if x not in (my_hero, enemy_id)]
                if len(candidates) < 1:
                    bs_saga_set_message("No hay suficientes héroes disponibles para iniciar 2v2.")
                    return False
                renpy.random.shuffle(candidates)
                p2 = candidates[0]
            candidates = [x for x in all_ids if x not in (my_hero, p2, enemy_id)]
            if len(candidates) < 1:
                bs_saga_set_message("No hay suficientes héroes rivales para iniciar 2v2.")
                return False
            renpy.random.shuffle(candidates)
            e2 = candidates[0]
            S.battle_player_ids = [my_hero, p2]
            S.battle_enemy_ids = [enemy_id, e2]
            S.battle_player_slot_0 = my_hero
            S.battle_player_slot_1 = p2
            S.battle_enemy_slot_0 = enemy_id
            S.battle_enemy_slot_1 = e2

        # Cierre defensivo de coherencia: IDs activos nunca vacíos antes de jump battle_start.
        if not (getattr(S, "battle_player_ids", None) or []):
            S.battle_player_ids = [my_hero]
        if not (getattr(S, "battle_enemy_ids", None) or []):
            S.battle_enemy_ids = [enemy_id]
        S.battle_player_id = str((S.battle_player_ids or [my_hero])[0] or my_hero)
        S.battle_enemy_id = str((S.battle_enemy_ids or [enemy_id])[0] or enemy_id)

        prep_cfg = str(getattr(S, "bs_saga_prep_selected_config", "cfg1") or "cfg1")
        if prep_cfg not in bs_saga_prep_config_keys():
            prep_cfg = "cfg1"
        prep_build = str(getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado").strip().lower()
        if prep_build not in bs_saga_prep_build_keys():
            prep_build = "balanceado"
        S.battle_prepared_config_id = prep_cfg
        S.battle_prepared_build_id = prep_build
        S.battle_prepared_player_loadouts = {}
        S.battle_prepared_player_tech_profiles = {}
        S.battle_prepared_combat_tuning = {}
        S.battle_prepared_damage_rules = dict(getattr(S, "bs_saga_damage_coherence_rules", {}) or {})
        S.bs_runtime_character_overrides = {}
        for pid in (S.battle_player_ids or []):
            S.battle_prepared_player_loadouts[str(pid)] = bs_saga_hero_loadout_slots(pid, prep_cfg, prep_build)
            S.battle_prepared_player_tech_profiles[str(pid)] = dict(bs_saga_resolve_hero_tech_profile(pid, prep_cfg, prep_build) or {})
        # También dejamos override de stats por tier para participantes del combate (player/enemy).
        for pid in (S.battle_player_ids or []) + (S.battle_enemy_ids or []):
            tier = bs_saga_hero_tier(pid, "C")
            prof = bs_saga_tier_core_profile(tier)
            tune = bs_saga_tier_combat_tuning_profile(tier)
            S.bs_runtime_character_overrides[str(pid)] = {
                "HP": int(prof.get("hp", 1000) or 1000),
                "Reiatsu": int(prof.get("ep", 1000) or 1000),
                "Energy": int(prof.get("ec", 1000) or 1000),
                "coating_durability": int(prof.get("durability", 0) or 0),
                "coating_cover": int(prof.get("cover", 0) or 0)
            }
            S.battle_prepared_combat_tuning[str(pid)] = dict(tune)

        S.battle_prepared_item_id = str(getattr(S, "bs_saga_prep_flag_item_id", "") or "")
        S.battle_prepared_consumable_id = str(getattr(S, "bs_saga_prep_flag_consumable_id", "") or "")
        bs_saga_register_hero_usage(my_hero)
        bs_saga_set_message("Preparación verificada. Duelo listo.")
        return True

    def bs_saga_db_rows():
        fn_v1 = getattr(S, "bs_get_hero_catalog_v1", None)
        if callable(fn_v1):
            rows_v1 = fn_v1()
            if isinstance(rows_v1, list) and rows_v1:
                return list(rows_v1)

        db_override = getattr(S, "bs_hero_catalog_v1", None)
        if isinstance(db_override, list) and db_override:
            return list(db_override)

        db = getattr(S, "CHARACTER_DB", []) or []
        if isinstance(db, list):
            return list(db)
        return []

    def bs_saga_heroes_by_tier(tier="C"):
        t = str(tier or "C").strip().upper()
        rows = bs_saga_db_rows()
        out = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            if str(r.get("tier", "")).upper() == t:
                out.append(r)
        return out

    def bs_saga_franchises_for_tier(tier="C"):
        items = bs_saga_heroes_by_tier(tier)
        names = {}
        for r in items:
            f = str(r.get("franchise", "") or "").strip()
            if f:
                names[f] = True
        arr = sorted(names.keys())
        return arr

    def bs_saga_heroes_filtered(tier="C", franchise="all"):
        ff = str(franchise or "all").strip().lower()
        items = bs_saga_heroes_by_tier(tier)
        if ff in ("all", "", "*"):
            return items
        out = []
        for r in items:
            fr = str(r.get("franchise", "") or "").strip().lower()
            if fr == ff:
                out.append(r)
        return out

    def bs_saga_item_schema():
        fn_v1 = getattr(S, "bs_get_item_catalog_v1", None)
        if callable(fn_v1):
            cat_v1 = fn_v1()
            if isinstance(cat_v1, dict) and cat_v1:
                return dict(cat_v1)

        cat_override = getattr(S, "bs_item_catalog_v1", None)
        if isinstance(cat_override, dict) and cat_override:
            return dict(cat_override)

        # Esquema fallback de catálogo para UI (v1 wireframe local).
        return {
            "consumibles": {
                "title": "Consumibles",
                "groups": {
                    "pociones": [
                        {"name": "Poción HP roja", "rarity": "", "tier_req": "", "meta": "+50% HP"},
                        {"name": "Poción HP naranja", "rarity": "", "tier_req": "", "meta": "+35% HP"},
                        {"name": "Poción HP amarilla", "rarity": "", "tier_req": "", "meta": "+25% HP"},

                        {"name": "Poción EP roja", "rarity": "", "tier_req": "", "meta": "+50% EP"},
                        {"name": "Poción EP naranja", "rarity": "", "tier_req": "", "meta": "+35% EP"},
                        {"name": "Poción EP amarilla", "rarity": "", "tier_req": "", "meta": "+25% EP"},

                        {"name": "Poción EC roja", "rarity": "", "tier_req": "", "meta": "+50% EC"},
                        {"name": "Poción EC naranja", "rarity": "", "tier_req": "", "meta": "+35% EC"},
                        {"name": "Poción EC amarilla", "rarity": "", "tier_req": "", "meta": "+25% EC"},

                        {"name": "Poción de durabilidad roja", "rarity": "", "tier_req": "", "meta": "+50% durabilidad"},
                        {"name": "Poción de durabilidad naranja", "rarity": "", "tier_req": "", "meta": "+35% durabilidad"},
                        {"name": "Poción de durabilidad amarilla", "rarity": "", "tier_req": "", "meta": "+25% durabilidad"},

                        {"name": "Poción de fuerza verde", "rarity": "", "tier_req": "", "meta": "+1 punto fuerza · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de fuerza celeste", "rarity": "", "tier_req": "", "meta": "+2 puntos fuerza · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de fuerza azul", "rarity": "", "tier_req": "", "meta": "+3 puntos fuerza · Solo Torre · dura 1 duelo"},

                        {"name": "Poción de agilidad verde", "rarity": "", "tier_req": "", "meta": "+1 punto agilidad · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de agilidad celeste", "rarity": "", "tier_req": "", "meta": "+2 puntos agilidad · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de agilidad azul", "rarity": "", "tier_req": "", "meta": "+3 puntos agilidad · Solo Torre · dura 1 duelo"},

                        {"name": "Poción de resistencia verde", "rarity": "", "tier_req": "", "meta": "+1 punto resistencia · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de resistencia celeste", "rarity": "", "tier_req": "", "meta": "+2 puntos resistencia · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de resistencia azul", "rarity": "", "tier_req": "", "meta": "+3 puntos resistencia · Solo Torre · dura 1 duelo"},

                        {"name": "Poción de inteligencia verde", "rarity": "", "tier_req": "", "meta": "+1 punto inteligencia · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de inteligencia celeste", "rarity": "", "tier_req": "", "meta": "+2 puntos inteligencia · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de inteligencia azul", "rarity": "", "tier_req": "", "meta": "+3 puntos inteligencia · Solo Torre · dura 1 duelo"},

                        {"name": "Poción de espíritu verde", "rarity": "", "tier_req": "", "meta": "+1 punto espíritu · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de espíritu celeste", "rarity": "", "tier_req": "", "meta": "+2 puntos espíritu · Solo Torre · dura 1 duelo"},
                        {"name": "Poción de espíritu azul", "rarity": "", "tier_req": "", "meta": "+3 puntos espíritu · Solo Torre · dura 1 duelo"},
                    ],
                    "amuletos": [
                        {"name": "Espejo reflector", "rarity": "rare", "tier_req": "B", "meta": "Refleja 30% daño (3 usos)"},
                        {"name": "Cilindro mágico", "rarity": "rare", "tier_req": "B", "meta": "Absorbe 30% daño (3 usos)"},
                        {"name": "Espada sagrada", "rarity": "epic", "tier_req": "A", "meta": "+30% daño (3 usos)"},
                        {"name": "Daga maldita", "rarity": "epic", "tier_req": "A", "meta": "30% a daño directo (3 usos)"},
                        {"name": "Daga envenenada", "rarity": "epic", "tier_req": "A", "meta": "30% directo a HP (3 usos)"},
                    ],
                },
            },
            "permanentes": {
                "title": "Permanentes",
                "groups": {
                    "anillos": [],
                    "pulseras": [],
                    "pendientes": [],
                    "collares": [],
                    "diademas": [],
                    "cinturones": [],
                    "tobilleras": [],
                    "tatuajes": [],
                },
            },
            "materiales": {
                "title": "Materiales",
                "groups": {
                    "basicos": [
                        {"name": "Chatarra común", "rarity": "common", "tier_req": "C", "meta": "Moneda de trueque"},
                        {"name": "Fragmento reciclado", "rarity": "common", "tier_req": "C", "meta": "Moneda de trueque"},
                    ],
                    "ascenso": [
                        {"name": "Material ascenso común", "rarity": "common", "tier_req": "C", "meta": "Ascenso C→B"},
                        {"name": "Material ascenso raro", "rarity": "rare", "tier_req": "B", "meta": "Ascenso B→A"},
                        {"name": "Material ascenso especial", "rarity": "special", "tier_req": "A", "meta": "Ascenso A→S"},
                        {"name": "Material ascenso épico", "rarity": "epic", "tier_req": "S", "meta": "Ascenso S→SS"},
                        {"name": "Material ascenso legendario", "rarity": "legendary", "tier_req": "SS", "meta": "Ascenso SS→SSS"},
                        {"name": "Material ascenso mítico", "rarity": "mythic", "tier_req": "SSS", "meta": "Ascenso SSS→IV"},
                        {"name": "Material ascenso infernal", "rarity": "infernal", "tier_req": "IV", "meta": "Reserva tier IV"},
                    ],
                },
            },
        }

    def bs_saga_inventory_contract_ok():
        inv = getattr(S, "bs_saga_inventory_state", None)
        if not isinstance(inv, dict):
            return False
        chest = inv.get("account_inventory", {})
        if not isinstance(chest, dict):
            return False
        for k in ("consumables", "equipables", "materials"):
            if not isinstance(chest.get(k, {}), dict):
                return False
        return isinstance(inv.get("hero_inventories", {}), dict)

    def bs_saga_catalog_category_keys():
        return ["consumibles", "permanentes", "materiales"]

    def bs_saga_catalog_groups(category):
        cat_key = str(category or "consumibles")
        schema = bs_saga_item_schema()
        cat = schema.get(cat_key, {})
        groups = cat.get("groups", {}) if isinstance(cat.get("groups", {}), dict) else {}
        preferred = {
            "consumibles": ["pociones", "amuletos"],
            "permanentes": ["anillos", "pulseras", "pendientes", "collares", "diademas", "cinturones", "tobilleras", "tatuajes"],
            "materiales": ["basicos", "ascenso"],
        }
        ordered = []
        for g in preferred.get(cat_key, []):
            if g in groups:
                ordered.append(g)
        for g in groups.keys():
            if g not in ordered:
                ordered.append(g)
        return ordered

    def bs_saga_catalog_items(category, group):
        schema = bs_saga_item_schema()
        cat = schema.get(str(category or "consumibles"), {})
        groups = cat.get("groups", {}) if isinstance(cat.get("groups", {}), dict) else {}
        items = groups.get(str(group or ""), [])
        if isinstance(items, list):
            return items
        return []

    def bs_saga_labelize(v):
        try:
            s = unicode(v)
        except:
            try:
                s = str(v)
            except:
                s = ""
        s = s.replace("_", " ").strip()
        if not s:
            return "—"
        return s[:1].upper() + s[1:]

    def bs_saga_catalog_set_category(category):
        cat = str(category or "consumibles")
        groups = bs_saga_catalog_groups(cat)
        S.bs_saga_catalog_category = cat
        S.bs_saga_catalog_group = groups[0] if groups else ""
        return None

    def bs_saga_catalog_set_group(group):
        S.bs_saga_catalog_group = str(group or "")
        return None

    def bs_saga_tower_block_size():
        # 1 bloque = 10 pisos (según propuesta Torre MVP: C 1-20, B 21-50, A 51-90).
        return 10

    def bs_saga_tower_tier_blocks():
        # Estructura creciente de bloques por tier (documentación de diseño).
        return [
            ("C", 2),
            ("B", 3),
            ("A", 4),
            ("S", 5),
            ("SS", 6),
            ("SSS", 7),
            ("IV", 8),
        ]

    def bs_saga_tower_tier_for_floor(floor_num):
        try:
            n = int(floor_num)
        except:
            n = 1
        if n < 1:
            n = 1
        block_size = bs_saga_tower_block_size()
        acc = 0
        rows = bs_saga_tower_tier_blocks()
        for tier, blocks in rows:
            acc += int(blocks) * block_size
            if n <= acc:
                return tier
        return "IV"

    def bs_saga_tower_floors(limit=100):
        try:
            max_floor = int(limit)
        except:
            max_floor = 100
        if max_floor < 1:
            max_floor = 1

        rows = []
        tier_rows = bs_saga_tower_tier_blocks()
        block_size = bs_saga_tower_block_size()
        for n in range(1, max_floor + 1):
            tier = bs_saga_tower_tier_for_floor(n)
            has_guardian = (n % 5 != 0)
            tier_start = 1
            tier_end = block_size
            for tier_key, tier_blocks in tier_rows:
                tier_len = int(tier_blocks) * block_size
                tier_end = tier_start + tier_len - 1
                if tier == tier_key:
                    break
                tier_start = tier_end + 1

            rows.append({
                "floor": n,
                "tier": tier,
                "tier_range_start": tier_start,
                "tier_range_end": tier_end,
                "slot_type": ("guardian" if has_guardian else "event"),
                "title": ("Guardián pendiente" if has_guardian else "Buff / Sorpresa pendiente"),
                "subtitle": ("NPC/Héroe por definir" if has_guardian else "Evento especial por definir"),
            })
        return rows

    def bs_saga_tower_filter_floors(tier_filter="ALL", limit=100):
        tf = str(tier_filter or "ALL").upper()
        rows = bs_saga_tower_floors(limit)
        if tf in ("ALL", "", "*"):
            return rows
        out = []
        for row in rows:
            if str(row.get("tier", "")).upper() == tf:
                out.append(row)
        return out

    def bs_saga_tower_selected_row(selected_floor=1, limit=100):
        try:
            target = int(selected_floor)
        except:
            target = 1
        rows = bs_saga_tower_floors(limit)
        for row in rows:
            if int(row.get("floor", 0) or 0) == target:
                return row
        return rows[0] if rows else {"floor": 1, "tier": "C", "slot_type": "guardian", "title": "—", "subtitle": "—"}

    def bs_saga_tech_tier_keys():
        return ["C", "B", "A", "S"]

    def bs_saga_tech_type_keys():
        return ["ofensivas", "defensivas", "neutras", "especiales"]

    def bs_saga_tech_catalog():
        return {
            "C": [
                {"name": "Ataque básico", "desc": "Ataque base. Escala con EP: a mayor potencia, mayor gasto de EP."},
                {"name": "Defensa básica", "desc": "Defensa base. Escala con EP: más protección implica mayor gasto de EP."},
                {"name": "Ataque directo", "desc": "Si sale 3/4 en dados, el golpe se vuelve indefendible; si no, se puede bloquear."},
                {"name": "Efecto especial", "desc": "Cada héroe tiene un efecto propio, aplicado en ataque o defensa según su kit."},
                {"name": "Concentrar", "desc": "Multiplica x2 un ataque elegido. No consume acción disponible."},
                {"name": "Descansar", "desc": "Recupera un porcentaje de HP, EP y EC."},
                {"name": "Dados de furia", "desc": "Se activa con 10% de HP o menos. Multiplica x2 una técnica elegida de ataque o defensa y no consume acción disponible."},
            ],
            "B": [
                {"name": "Ataque extra", "desc": "Otorga una acción ofensiva adicional en el turno."},
                {"name": "Defensa extra", "desc": "Otorga una acción defensiva adicional en el turno."},
                {"name": "Potenciar", "desc": "Multiplica x2 una defensa elegida y no consume acción disponible."},
            ],
            "A": [
                {"name": "Técnica extra", "desc": "Habilita una acción adicional de técnica en el turno. Puede usarse para ataque o defensa."},
                {"name": "Ataque reductor", "desc": "Reduce un porcentaje de la defensa general del enemigo."},
                {"name": "Defensa reductora", "desc": "Reduce un porcentaje del ataque general del enemigo."},
            ],
            "S": [
                {"name": "Ataque negador", "desc": "Con 3/4 dados exitosos, anula el siguiente turno enemigo."},
                {"name": "Defensa reflectora", "desc": "Refleja un porcentaje del daño de ataque enemigo."},
            ],
        }

    def bs_saga_tech_catalog_by_type():
        return {
            "ofensivas": [
                {"name": "Ataque básico", "desc": "Ataque base del turno ofensivo."},
                {"name": "Ataque extra", "desc": "Otorga una acción ofensiva adicional en el turno."},
                {"name": "Técnica extra", "desc": "Acción adicional de técnica usable también en defensa."},
                {"name": "Ataque reductor", "desc": "Reduce un porcentaje de la defensa general del enemigo."},
                {"name": "Ataque directo", "desc": "Con 3/4 en dados se vuelve indefendible."},
                {"name": "Ataque negador", "desc": "Con 3/4 dados exitosos, anula el siguiente turno enemigo."},
            ],
            "defensivas": [
                {"name": "Defensa básica", "desc": "Defensa base del turno defensivo."},
                {"name": "Defensa extra", "desc": "Otorga una acción defensiva adicional en el turno."},
                {"name": "Técnica extra", "desc": "Acción adicional de técnica usable también en defensa."},
                {"name": "Defensa reductora", "desc": "Reduce un porcentaje del ataque general del enemigo."},
                {"name": "Defensa reflectora", "desc": "Refleja un porcentaje del daño de ataque enemigo."},
            ],
            "neutras": [
                {"name": "Descansar", "desc": "Recupera un porcentaje de HP, EP y EC."},
                {"name": "Técnica extra", "desc": "Puede aplicarse para extender ataque o defensa según necesidad."},
                {"name": "Dados de furia", "desc": "Multiplica x2 una técnica de ataque o defensa sin consumir acción disponible."},
            ],
            "especiales": [
                {"name": "Concentrar", "desc": "Multiplica x2 un ataque elegido y no consume acción disponible."},
                {"name": "Potenciar", "desc": "Multiplica x2 una defensa elegida y no consume acción disponible."},
                {"name": "Efecto especial", "desc": "Efecto propio del héroe, aplicable en ataque o defensa."},
            ],
        }

    def bs_saga_tech_catalog_set_mode(mode):
        m = str(mode or "").strip().lower()
        current = str(getattr(S, "bs_saga_tech_catalog_mode", "") or "").strip().lower()
        # Toggle: si se vuelve a presionar el mismo modo, colapsa panel.
        if current == m:
            S.bs_saga_tech_catalog_mode = ""
            return None
        if m in ("tier", "type"):
            S.bs_saga_tech_catalog_mode = m
        else:
            S.bs_saga_tech_catalog_mode = ""
        return None

screen bs_saga_lobby_screen():
    tag menu
    $ _acc = bs_saga_account()
    $ _tier_current = bs_saga_refresh_account_tier(reason="lobby_screen")
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _tier = str(_tier_current or "")
    $ _tier_txt = ("Tier " + _tier) if _tier else "Sin tier"
    $ _owned_count = bs_saga_owned_heroes_count()
    $ _last_msg = str(bs_saga_last_tx_message or "")
    $ _exp_ratio = bs_saga_exp_progress()

    add Solid("#101923")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 96
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ysize 84
        ypadding 8
        xpadding 10
        background Solid("#1A2938")
        vbox:
            spacing 6
            hbox:
                spacing 14
                text "BATTLESTARS SAGA" size 30 color "#5FC6FF"
                text "Lobby táctico" size 22 color "#D7EEFF" yalign 0.7
                text _tier_txt size 20 color "#D7EEFF" yalign 0.7
                text ("Lv " + str(_lvl)) size 20 color "#D7EEFF" yalign 0.7
                text ("EXP " + str(_exp) + "/" + str(_next)) size 18 color "#B9D9F3" yalign 0.7
                text ("Oro: " + str(_gold)) size 22 color "#F7D774" yalign 0.7
                null width 8
                textbutton "Salir" action MainMenu()
            bar:
                value _exp_ratio
                xfill True
                ymaximum 8
                left_bar Solid("#4AD4FF")
                right_bar Solid("#2A3D4E")

    frame:
        xalign 0.5
        yalign 0.48
        xsize 680
        ysize 380
        padding (18, 18)
        background Solid("#142131")

        vbox:
            spacing 10
            text "Panel Jugar" size 28 color "#E9F5FF"

            textbutton "⚔ Duelo libre" action Jump("bs_saga_duelo_libre")

            textbutton ("▼ Torneo" if bs_saga_tournament_panel_open else "▶ Torneo"):
                action ToggleVariable("bs_saga_tournament_panel_open")

            if bs_saga_tournament_panel_open:
                frame:
                    xfill True
                    padding (10, 10)
                    background Solid("#22384D")
                    vbox:
                        spacing 8
                        textbutton "Tier C" action Jump("bs_saga_torneo_tier_c")
                        textbutton "Tier B (no disponible)" action Jump("bs_saga_torneo_tier_b_locked")
                        textbutton "Tier A (no disponible)" action Jump("bs_saga_torneo_tier_a_locked")

            textbutton "🗼 Torre del cielo (preview)" action Jump("bs_saga_torre_cielo")

    frame:
        xalign 0.5
        yalign 0.88
        xsize 1120
        ysize 120
        padding (12, 12)
        background Solid("#1A2A3C")

        vbox:
            spacing 8
            text "Panel Gestión" size 20 color "#CFE6FA"
            text ("Héroes adquiridos: " + str(_owned_count)) size 16 color "#9FC4E2"
            if _last_msg:
                text ("Última transacción: " + _last_msg) size 15 color "#CDE7FF"
            hbox:
                spacing 10
                textbutton "Perfil" action Jump("bs_saga_perfil")
                textbutton "Preparación" action Jump("bs_saga_preparacion")
                textbutton "Héroes" action Jump("bs_saga_heroes")
                textbutton "Tienda" action Jump("bs_saga_tienda")
                textbutton "Inventario" action Jump("bs_saga_inventario")
                textbutton "Catálogo de itens" action Jump("bs_saga_catalogo_items")
                textbutton "Catálogo de técnicas" action Jump("bs_saga_catalogo_tecnicas")

screen bs_saga_section_shell(title="Sección", subtitle="Panel", back_action=NullAction()):
    tag menu
    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "[subtitle]" size 22 color "#D7EEFF" yalign 0.7
            null width 220
            textbutton "Volver al lobby" action back_action

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (22, 22)
        background Solid("#152437")
        vbox:
            spacing 10
            text "[title]" size 34 color "#E9F5FF"
            text "Territorio: [title]" size 20 color "#A8C9E4"

screen bs_saga_heroes_screen():
    tag menu

    $ _tier = str(bs_saga_heroes_tier or "C").upper()
    $ _frs = bs_saga_franchises_for_tier(_tier)
    $ _heroes = bs_saga_heroes_filtered(_tier, bs_saga_heroes_franchise)
    $ _ff = str(bs_saga_heroes_franchise or "all").lower()
    $ _filter_label = _ff if _ff != "all" else "todas"
    $ _gold = bs_saga_gold()
    $ _owned_count = bs_saga_owned_heroes_count()

    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Territorio: Héroes" size 22 color "#D7EEFF" yalign 0.7
            null width 150
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (18, 18)
        background Solid("#14273B")

        hbox:
            spacing 16

            frame:
                xsize 220
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Franquicias" size 22 color "#DDEEFF"
                    textbutton "Todas" action SetVariable("bs_saga_heroes_franchise", "all")
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 420
                        vbox:
                            spacing 6
                            for fr in _frs:
                                textbutton "[fr]" action SetVariable("bs_saga_heroes_franchise", fr)

            frame:
                xfill True
                yfill True
                padding (14, 14)
                background Solid("#11253A")
                vbox:
                    spacing 10

                    hbox:
                        spacing 8
                        text "Tiers" size 20 color "#DCEEFF"
                        textbutton "Tier C" action [SetVariable("bs_saga_heroes_tier", "C"), SetVariable("bs_saga_heroes_franchise", "all")]
                        textbutton "Tier B" action [SetVariable("bs_saga_heroes_tier", "B"), SetVariable("bs_saga_heroes_franchise", "all")]
                        text ("Oro: " + str(_gold)) size 18 color "#F7D774"
                        text ("Roster: " + str(_owned_count)) size 16 color "#9FC4E2"
                        text "Filtro: [_filter_label]" size 16 color "#9FC4E2"

                    hbox:
                        spacing 20
                        frame:
                            xsize 290
                            ysize 360
                            background Solid("#0D1A2A")
                            padding (12, 12)
                            vbox:
                                spacing 8
                                text "Panel visual héroe" size 18 color "#CDE7FF"
                                null height 260
                                text "(Sin imágenes por ahora)" size 16 color "#8EABC5"

                        frame:
                            xfill True
                            ysize 360
                            padding (10, 10)
                            background Solid("#1A3044")
                            vbox:
                                spacing 8
                                text "Nombres disponibles (Tier [_tier])" size 20 color "#E5F4FF"
                                viewport:
                                    draggable True
                                    mousewheel True
                                    scrollbars "vertical"
                                    ymaximum 300
                                    yinitial float(bs_saga_heroes_scroll_y or 0.0)
                                    vbox:
                                        spacing 5
                                        if _heroes:
                                            for i, h in enumerate(_heroes):
                                                $ _hn = str(h.get("name", "?") or "?")
                                                $ _hf = str(h.get("franchise", "?") or "?")
                                                $ _hid = bs_saga_hero_id(h)
                                                $ _price = bs_saga_hero_price(h)
                                                $ _owned = bs_saga_hero_is_owned(_hid)
                                                frame:
                                                    xfill True
                                                    background Solid("#1B3348")
                                                    padding (8, 6)
                                                    hbox:
                                                        spacing 8
                                                        text "• [_hn]" size 17 color "#D0E9FF" xminimum 240
                                                        text "—" size 17 color "#9FC4E2"
                                                        text "[_hf]" size 17 color "#D0E9FF" xminimum 180
                                                        text ("Oro: " + str(_price)) size 16 color "#F7D774" xminimum 120
                                                        if _owned:
                                                            text "Adquirido" size 16 color "#8BD6A7"
                                                        else:
                                                            textbutton "Comprar":
                                                                action [
                                                                    SetVariable("bs_saga_heroes_scroll_y", (float(i) / float(max(1, len(_heroes) - 1)))),
                                                                    Function(bs_saga_buy_hero, h),
                                                                    Jump("bs_saga_heroes")
                                                                ]
                                        else:
                                            text "No hay héroes para ese filtro." size 18 color "#9FB9D1"

screen bs_saga_catalog_screen():
    tag menu
    $ _cat = str(bs_saga_catalog_category or "consumibles")
    $ _groups = bs_saga_catalog_groups(_cat)
    $ _grp = str(bs_saga_catalog_group or "")
    if _grp not in _groups:
        $ _grp = _groups[0] if _groups else ""
        $ bs_saga_catalog_group = _grp
    $ _grp_label = _grp.capitalize() if _grp else "—"
    $ _items = bs_saga_catalog_items(_cat, _grp)
    $ _cats = bs_saga_catalog_category_keys()
    $ _cat_label = bs_saga_labelize(_cat)
    $ _gold = bs_saga_gold()

    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Territorio: Catálogo de itens" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        vbox:
            spacing 10
            text "Catálogo de itens" size 34 color "#EAF6FF"

            hbox:
                spacing 8
                for ck in _cats:
                    $ lbl = "Consumibles" if ck == "consumibles" else ("Permanentes" if ck == "permanentes" else "Materiales")
                    textbutton "[lbl]":
                        action Function(bs_saga_catalog_set_category, ck)
                null width 16
                text ("Oro disponible: " + str(_gold)) size 18 color "#F7D774"

            hbox:
                spacing 14

                frame:
                    xsize 260
                    yfill True
                    padding (10, 10)
                    background Solid("#1F3348")
                    vbox:
                        spacing 8
                        text "Grupos" size 22 color "#DDEEFF"
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 360
                            vbox:
                                spacing 6
                                for g in _groups:
                                    $ _g_label = bs_saga_labelize(g)
                                    textbutton "[_g_label]":
                                        action Function(bs_saga_catalog_set_group, g)

                frame:
                    xfill True
                    yfill True
                    padding (12, 12)
                    background Solid("#102438")
                    vbox:
                        spacing 8
                        text "Listado central · [_cat_label] / [_grp_label]" size 20 color "#DCEEFF"
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 360
                            vbox:
                                spacing 6
                                if _items:
                                    for it in _items:
                                        $ _n = str(it.get("name", "?") or "?")
                                        $ _r = str(it.get("rarity", "-") or "-")
                                        $ _t = str(it.get("tier_req", "-") or "-")
                                        $ _m = str(it.get("meta", "") or "")
                                        $ _r_show = "-" if _r in ("", "-") else _r
                                        $ _t_show = "-" if _t in ("", "-") else _t
                                        $ _p = bs_saga_item_price(it)
                                        frame:
                                            xfill True
                                            background Solid("#173048")
                                            padding (8, 6)
                                            hbox:
                                                spacing 8
                                                text "• [_n]" size 17 color "#D0E9FF" xminimum 290
                                                text "Rareza: [_r_show]" size 16 color "#A9CAE6" xminimum 150
                                                text "Tier: [_t_show]" size 16 color "#A9CAE6" xminimum 120
                                                text ("Precio: " + str(_p)) size 16 color "#F7D774" xminimum 120
                                                text "[_m]" size 16 color "#D0E9FF" xminimum 220
                                                textbutton "Comprar x1":
                                                    action [Function(bs_saga_buy_item, it, 1), Jump("bs_saga_catalogo_items")]
                                else:
                                    text "Sin itens cargados todavía para este grupo." size 18 color "#9FB9D1"

screen bs_saga_inventory_screen():
    tag menu
    $ _rows = bs_saga_inventory_rows()
    $ _gold = bs_saga_gold()

    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Territorio: Inventario" size 22 color "#D7EEFF" yalign 0.7
            text ("Oro: " + str(_gold)) size 20 color "#F7D774" yalign 0.7
            null width 120
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        vbox:
            spacing 8
            text "Inventario de cuenta" size 32 color "#EAF6FF"
            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                ymaximum 390
                vbox:
                    spacing 6
                    if _rows:
                        for row in _rows:
                            $ _b = bs_saga_labelize(row.get("bucket", ""))
                            $ _id = str(row.get("item_id", "?") or "?")
                            $ _q = int(row.get("qty", 0) or 0)
                            frame:
                                xfill True
                                background Solid("#173048")
                                padding (8, 6)
                                hbox:
                                    spacing 8
                                    text ("Bucket: " + _b) size 17 color "#A9CAE6" xminimum 180
                                    text ("Item: " + _id) size 17 color "#D0E9FF" xminimum 520
                                    text ("Qty: " + str(_q)) size 17 color "#8BD6A7"
                    else:
                        text "Inventario vacío todavía." size 18 color "#9FB9D1"

screen bs_saga_profile_screen():
    tag menu
    $ _acc = bs_saga_account()
    $ _tier_current = bs_saga_refresh_account_tier(reason="profile_screen")
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _tier = str(_tier_current or "")
    $ _tier_txt = (_tier if _tier else "Sin tier")
    $ _top_total = bs_saga_top_heroes(3, False)
    $ _top_24 = bs_saga_top_heroes(3, True)
    $ _tier_rows = bs_saga_tier_progress_rows()

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Perfil de usuario" size 22 color "#D7EEFF" yalign 0.7
            null width 180
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 520
                yfill True
                background Solid("#1A3044")
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Resumen de cuenta" size 28 color "#EAF6FF"
                    text ("Tier: " + _tier_txt) size 18 color "#D0E9FF"
                    text ("Nivel: " + str(_lvl)) size 18 color "#D0E9FF"
                    text ("EXP: " + str(_exp) + "/" + str(_next)) size 18 color "#D0E9FF"
                    text ("Oro: " + str(_gold)) size 18 color "#F7D774"
                    null height 4
                    if bool(getattr(store, "bs_saga_dev_admin_enabled", False)):
                        text "DEV Admin (QA rápido)" size 16 color "#FFD166"
                        hbox:
                            spacing 6
                            textbutton "+50k oro" action [Function(bs_saga_dev_set_account_state, gold=_gold + 50000), Jump("bs_saga_perfil")]
                            textbutton "Lv 99" action [Function(bs_saga_dev_set_account_state, level=99), Jump("bs_saga_perfil")]
                            textbutton "EXP 0" action [Function(bs_saga_dev_set_account_state, exp=0), Jump("bs_saga_perfil")]
                        hbox:
                            spacing 6
                            textbutton ("Infinite Gold: " + ("ON" if bool(getattr(store, "bs_saga_dev_infinite_gold", False)) else "OFF")):
                                action [Function(bs_saga_dev_toggle_infinite_gold, None), Jump("bs_saga_perfil")]
                            textbutton ("Low-spec combate: " + ("ON" if bool(getattr(store, "bs_saga_dev_low_spec_mode", False)) else "OFF")):
                                action [Function(bs_saga_dev_apply_low_spec_mode, not bool(getattr(store, "bs_saga_dev_low_spec_mode", False))), Jump("bs_saga_perfil")]
                    null height 4
                    text "Progreso de tier (nivel + héroes por tier)" size 16 color "#9FC4E2"
                    for row in _tier_rows:
                        $ _tt = str(row.get("tier", "?"))
                        $ _hv = int(row.get("have_heroes", 0) or 0)
                        $ _nh = int(row.get("need_heroes", 0) or 0)
                        $ _nl = int(row.get("need_level", 0) or 0)
                        $ _ok = bool(row.get("ok", False))
                        text ("• " + _tt + ": Lv " + str(_lvl) + "/" + str(_nl) + " · Héroes " + str(_hv) + "/" + str(_nh)) size 14 color ("#8BD6A7" if _ok else "#9FC4E2")
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Top héroes más usados" size 24 color "#EAF6FF"
                    text "Global" size 18 color "#CFE6FA"
                    if _top_total:
                        for row in _top_total:
                            text ("• " + str(row.get("hero_id", "?")) + " · " + str(row.get("score", 0)) + " usos") size 16 color "#D0E9FF"
                    else:
                        text "Sin datos todavía." size 16 color "#9FB9D1"
                    null height 10
                    text "Últimas 24h" size 18 color "#CFE6FA"
                    if _top_24:
                        for row in _top_24:
                            text ("• " + str(row.get("hero_id", "?")) + " · " + str(row.get("score", 0)) + " usos") size 16 color "#D0E9FF"
                    else:
                        text "Sin datos de 24h todavía." size 16 color "#9FB9D1"

screen bs_saga_preparation_room_screen():
    tag menu
    $ _rows = bs_saga_preparation_rows_filtered()
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy_hero = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _party = [str(x) for x in (bs_saga_prep_selected_party_ids or []) if str(x)]
    $ _party_txt = ", ".join(_party) if _party else "sin equipo"
    $ _owned_only = bool(bs_saga_prep_filter_owned_only)
    $ _equipables = bs_saga_prep_inventory_candidates("equipables")
    $ _slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _hero_tier = bs_saga_hero_tier(_hero, "C") if _hero else ""
    $ _tier_pool = bs_saga_tier_pool_total(_hero_tier) if _hero else 0
    $ _tier_stats = bs_saga_tier_core_profile(_hero_tier) if _hero else {"hp":0,"ep":0,"ec":0,"durability":0,"cover":0}
    $ _tier_tuning = bs_saga_tier_combat_tuning_profile(_hero_tier) if _hero else {"hp_factor":0.0,"rest_hp_pct":0.0,"rest_ep_pct":0.0,"rest_ec_pct":0.0,"rest_ec_scales":0}
    $ _dmg_rules = dict(bs_saga_damage_coherence_rules or {})
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _rotation_preview = ", ".join([str(x) for x in (bs_saga_prep_duel_rotation_ids or [])[:5]])
    $ _is_staging = False

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Sala de preparación" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 620
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Roster disponible (rotación o adquirido)" size 22 color "#EAF6FF"
                    text ("Héroes listados: " + str(len(_rows))) size 14 color "#9FC4E2"
                    text ("Rotación actual (5): " + (_rotation_preview if _rotation_preview else "sin generar")) size 14 color "#9FC4E2"
                    textbutton ("Filtro adquiridos: " + ("ON" if _owned_only else "OFF")):
                        action [ToggleVariable("bs_saga_prep_filter_owned_only"), Jump("bs_saga_preparacion")]
                    textbutton "Aleatorizar rotación":
                        action [Function(bs_saga_refresh_duel_rotation_heroes, 5), Jump("bs_saga_preparacion")]
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 390
                        vbox:
                            spacing 6
                            if _rows:
                                for row in _rows:
                                    $ _hid = str(row.get("hero_id", ""))
                                    $ _name = str(row.get("name", _hid) or _hid)
                                    $ _is_av = bool(row.get("available", False))
                                    $ _state = str(row.get("state", "bloqueado"))
                                    $ _tag = "Disponible" if _state == "disponible" else ("Para probar" if _state == "para_probar" else "Bloqueado")
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (8, 6)
                                        hbox:
                                            spacing 8
                                            text (_name + " (" + str(row.get("tier", "C")) + ")") size 17 color "#D0E9FF" xminimum 300
                                            text _tag size 16 color ("#8BD6A7" if _state == "disponible" else ("#FFD166" if _state == "para_probar" else "#FF9F9F")) xminimum 120
                                            if _hero == _hid:
                                                text "Activo" size 16 color "#F7D774"
                                            elif _is_av:
                                                textbutton "Elegir":
                                                    action [Function(bs_saga_set_prep_hero, _hid), Jump("bs_saga_preparacion")]
                                            if _is_av:
                                                textbutton ("Quitar" if _hid in _party else "Equipo"):
                                                    action [Function(bs_saga_toggle_prep_party_hero, _hid), Jump("bs_saga_preparacion")]
                            else:
                                text "No hay roster cargado." size 18 color "#9FB9D1"
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 468
                    vbox:
                        spacing 8
                        text "Configuración de entrada" size 22 color "#EAF6FF"
                        text ("Héroe activo: " + (_hero if _hero else "sin seleccionar")) size 16 color "#CFE6FA"
                        if _is_staging:
                            text "Modo de juego" size 16 color "#D0E9FF"
                            hbox:
                                spacing 6
                                textbutton "1v1" action [Function(bs_saga_set_prep_mode, "1v1"), Jump("bs_saga_preparacion")]
                                textbutton "2v2" action [Function(bs_saga_set_prep_mode, "2v2"), Jump("bs_saga_preparacion")]
                        text ("Equipo seleccionado: " + _party_txt) size 14 color "#9FC4E2"
                        text ("Config activa: " + _cfg.upper()) size 14 color "#9FC4E2"
                        text ("Build activa: " + _build) size 14 color "#9FC4E2"
                        if _hero:
                            text ("Tier héroe: " + _hero_tier + " · Pool duelo: " + str(_tier_pool)) size 14 color "#9FC4E2"
                            text ("HP " + str(_tier_stats.get("hp", 0)) + " · EP " + str(_tier_stats.get("ep", 0)) + " · EC " + str(_tier_stats.get("ec", 0))) size 14 color "#9FC4E2"
                            text ("Durabilidad " + str(_tier_stats.get("durability", 0)) + " · Cubre " + str(_tier_stats.get("cover", 0))) size 14 color "#9FC4E2"
                            text ("Factor HP/Pool x" + str(_tier_tuning.get("hp_factor", 0.0)) + " · Descansar HP " + str(int(float(_tier_tuning.get("rest_hp_pct", 0.0)) * 100)) + "%") size 14 color "#9FC4E2"
                            text ("Descansar EP " + str(int(float(_tier_tuning.get("rest_ep_pct", 0.0)) * 100)) + "% · EC " + str(int(float(_tier_tuning.get("rest_ec_pct", 0.0)) * 100)) + "% (+ " + str(int(_tier_tuning.get("rest_ec_scales", 0) or 0)) + " escalas)") size 14 color "#9FC4E2"
                            text ("Daño normal objetivo " + str(int(float(_dmg_rules.get("normal_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("normal_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Daño combo objetivo " + str(int(float(_dmg_rules.get("combo_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("combo_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Técnicas: " + str(_tech_prof.get("mode", "virgen")) + " · Pool técnico " + str(_tech_prof.get("pool_total", 0))) size 14 color "#9FC4E2"
                            hbox:
                                spacing 6
                                textbutton "Téc. Virgen" action [Function(bs_saga_hero_tech_mode_set, _hero, "virgen", _cfg, _build), Jump("bs_saga_preparacion")]
                                textbutton "Téc. Preconfig" action [Function(bs_saga_hero_tech_mode_set, _hero, "preconfig", _cfg, _build), Jump("bs_saga_preparacion")]
                        hbox:
                            spacing 6
                            textbutton "CFG1" action [Function(bs_saga_set_prep_config, "cfg1"), Jump("bs_saga_preparacion")]
                            textbutton "CFG2" action [Function(bs_saga_set_prep_config, "cfg2"), Jump("bs_saga_preparacion")]
                            textbutton "CFG3" action [Function(bs_saga_set_prep_config, "cfg3"), Jump("bs_saga_preparacion")]
                        text "Loadout del héroe (6 slots equipables)" size 15 color "#D0E9FF"
                        if _hero:
                            for i in range(6):
                                $ _slot_item = str(_slots[i] if i < len(_slots) else "")
                                hbox:
                                    spacing 6
                                    text ("Slot " + str(i + 1) + ": " + (_slot_item if _slot_item else "vacío")) size 14 color "#CFE6FA" xminimum 270
                                    if _slot_item:
                                        textbutton "Desequipar":
                                            action [Function(bs_saga_unequip_item_from_hero, _hero, i, _cfg, _build), Jump("bs_saga_preparacion")]
                        else:
                            text "Selecciona héroe para administrar equipables." size 14 color "#9FB9D1"
                        if _hero:
                            text "Equipar desde inventario de cuenta" size 15 color "#D0E9FF"
                            if _equipables:
                                for row in _equipables[:8]:
                                    $ _iid = str(row.get("item_id", ""))
                                    textbutton (_iid + " x" + str(row.get("qty", 0))):
                                        action [Function(bs_saga_equip_item_to_hero, _hero, _iid, None, _cfg, _build), Jump("bs_saga_preparacion")]
                            else:
                                text "No hay equipables en inventario de cuenta." size 14 color "#9FB9D1"
                        if _is_staging:
                            text "Modo de enemigo" size 16 color "#D0E9FF"
                            hbox:
                                spacing 6
                                textbutton "Aleatorio" action SetVariable("bs_saga_prep_enemy_mode", "random")
                                textbutton "Manual" action SetVariable("bs_saga_prep_enemy_mode", "manual")
                            if _enemy_mode == "manual":
                                text "Enemigo manual" size 16 color "#D0E9FF"
                                viewport:
                                    draggable True
                                    mousewheel True
                                    scrollbars "vertical"
                                    ymaximum 120
                                    vbox:
                                        spacing 4
                                        for row in _rows:
                                            $ _eh = str(row.get("hero_id", ""))
                                            textbutton _eh:
                                                action [Function(bs_saga_set_prep_enemy, _eh), Jump("bs_saga_preparacion")]
                                text ("Enemigo activo: " + (_enemy_hero if _enemy_hero else "sin seleccionar")) size 14 color "#9FC4E2"
                        text "Build base (sala)" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Balanceado" action [Function(bs_saga_set_prep_build, "balanceado"), Jump("bs_saga_preparacion")]
                            textbutton "Ofensivo" action [Function(bs_saga_set_prep_build, "ofensivo"), Jump("bs_saga_preparacion")]
                            textbutton "Defensivo" action [Function(bs_saga_set_prep_build, "defensivo"), Jump("bs_saga_preparacion")]
                        null height 12
                        text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"
                        text "Chequear técnicas/pool por tier: pendiente de integración detallada." size 15 color "#9FC4E2"
                        textbutton "Pasar a pre-combate":
                            action [SetVariable("bs_saga_prep_context", "staging"), Jump("bs_saga_preparacion")]

screen bs_saga_duel_staging_screen():
    tag menu
    $ _rows = bs_saga_preparation_rows_filtered()
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy_hero = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _party = [str(x) for x in (bs_saga_prep_selected_party_ids or []) if str(x)]
    $ _party_txt = ", ".join(_party) if _party else "sin equipo"
    $ _tier = bs_saga_hero_tier(_hero, "C") if _hero else "C"
    $ _pool = bs_saga_tier_pool_total(_tier) if _hero else 0
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _loadout = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _loadout_count = len([x for x in _loadout if str(x or "").strip()])
    $ _contract = bs_saga_precombat_contract_validate()
    $ _checks = list((_contract or {}).get("checks", []) or [])
    $ _block_n = len((_contract or {}).get("blocking", []) or [])
    $ _warn_n = len((_contract or {}).get("warnings", []) or [])

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Pre-combate (duelo)" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 620
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Roster para duelo (selección rápida)" size 22 color "#EAF6FF"
                    text ("Héroe activo: " + (_hero if _hero else "sin seleccionar")) size 15 color "#CFE6FA"
                    text ("Equipo: " + _party_txt) size 14 color "#9FC4E2"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 390
                        vbox:
                            spacing 6
                            if _rows:
                                for row in _rows:
                                    $ _hid = str(row.get("hero_id", ""))
                                    $ _state = str(row.get("state", "bloqueado"))
                                    $ _is_av = bool(row.get("available", False))
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (8, 6)
                                        hbox:
                                            spacing 8
                                            text (str(row.get("name", _hid) or _hid) + " (" + str(row.get("tier", "C")) + ")") size 17 color "#D0E9FF" xminimum 320
                                            text ("Disponible" if _state == "disponible" else ("Para probar" if _state == "para_probar" else "Bloqueado")) size 15 color ("#8BD6A7" if _state == "disponible" else ("#FFD166" if _state == "para_probar" else "#FF9F9F")) xminimum 120
                                            if _is_av:
                                                textbutton ("Activo" if _hero == _hid else "Elegir"):
                                                    action [Function(bs_saga_set_prep_hero, _hid), Jump("bs_saga_preparacion")]
                                                textbutton ("Quitar" if _hid in _party else "Equipo"):
                                                    action [Function(bs_saga_toggle_prep_party_hero, _hid), Jump("bs_saga_preparacion")]
                            else:
                                text "No hay roster cargado." size 18 color "#9FB9D1"

            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 468
                    vbox:
                        spacing 8
                        text "Checklist pre-duelo" size 22 color "#EAF6FF"
                        text ("Bloqueantes: " + str(int(_block_n)) + " · Warnings: " + str(int(_warn_n))) size 14 color ("#FF9F9F" if _block_n > 0 else ("#FFD166" if _warn_n > 0 else "#8BD6A7"))
                        for c in _checks:
                            $ _ok = bool(c.get("ok", False))
                            $ _sev = str(c.get("severity", "warn"))
                            $ _icon = "✅" if _ok else ("⛔" if _sev == "block" else "⚠")
                            $ _col = "#8BD6A7" if _ok else ("#FF9F9F" if _sev == "block" else "#FFD166")
                            text (_icon + " " + str(c.get("label", "")) + " · " + str(c.get("detail", ""))) size 14 color _col
                        text ("• Técnicas: " + str(_tech_prof.get("mode", "virgen")) + " · Pool " + str(_tech_prof.get("pool_total", 0))) size 14 color "#9FC4E2"
                        text ("• Loadout equipado: " + str(_loadout_count) + "/6") size 14 color "#9FC4E2"
                        null height 6

                        text "Modo de juego" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "1v1" action [Function(bs_saga_set_prep_mode, "1v1"), Jump("bs_saga_preparacion")]
                            textbutton "2v2" action [Function(bs_saga_set_prep_mode, "2v2"), Jump("bs_saga_preparacion")]

                        text "Rival de duelo" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Aleatorio" action SetVariable("bs_saga_prep_enemy_mode", "random")
                            textbutton "Manual" action SetVariable("bs_saga_prep_enemy_mode", "manual")
                        if _enemy_mode == "manual":
                            text ("Enemigo activo: " + (_enemy_hero if _enemy_hero else "sin seleccionar")) size 14 color "#9FC4E2"
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                ymaximum 120
                                vbox:
                                    spacing 4
                                    for row in _rows:
                                        $ _eh = str(row.get("hero_id", ""))
                                        textbutton _eh:
                                            action [Function(bs_saga_set_prep_enemy, _eh), Jump("bs_saga_preparacion")]

                        text "Build duelo" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Balanceado" action [Function(bs_saga_set_prep_build, "balanceado"), Jump("bs_saga_preparacion")]
                            textbutton "Ofensivo" action [Function(bs_saga_set_prep_build, "ofensivo"), Jump("bs_saga_preparacion")]
                            textbutton "Defensivo" action [Function(bs_saga_set_prep_build, "defensivo"), Jump("bs_saga_preparacion")]

                        text ("Config: " + _cfg.upper() + " · Tier: " + _tier + " · Pool duelo: " + str(_pool)) size 14 color "#9FC4E2"
                        text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"

                        textbutton "Verificar preparación e iniciar duelo":
                            action Jump("bs_saga_preparation_verify")
                        textbutton "Volver a sala de preparación":
                            action [SetVariable("bs_saga_prep_context", "room"), Jump("bs_saga_preparacion")]

screen bs_saga_preparation_verify_screen():
    tag menu
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _hero_slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _cons = bs_saga_prep_inventory_candidates("consumables")
    $ _items = bs_saga_prep_inventory_candidates("equipables")
    $ _flag_cons = str(bs_saga_prep_flag_consumable_id or "")
    $ _flag_item = str(bs_saga_prep_flag_item_id or "")

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Verificar preparación" size 22 color "#D7EEFF" yalign 0.7
            null width 140
            textbutton "Volver" action Jump("bs_saga_preparacion")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (14, 14)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 450
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Resumen previo al duelo" size 24 color "#EAF6FF"
                    text ("Tu héroe: " + (_hero if _hero else "sin seleccionar")) size 16 color "#D0E9FF"
                    text ("Modo: " + _mode) size 16 color "#D0E9FF"
                    text ("Enemigo: " + (_enemy if _enemy_mode == "manual" else "aleatorio")) size 16 color "#D0E9FF"
                    text ("Build: " + _build) size 16 color "#D0E9FF"
                    text ("Config: " + _cfg.upper()) size 16 color "#D0E9FF"
                    text ("Item flag: " + (_flag_item if _flag_item else "ninguno")) size 14 color "#9FC4E2"
                    text ("Consumible flag: " + (_flag_cons if _flag_cons else "ninguno")) size 14 color "#9FC4E2"
                    text ("Slots equipados: " + ", ".join([s for s in _hero_slots if str(s)]) if _hero_slots else "Slots equipados: ninguno") size 14 color "#9FC4E2"
                    textbutton "Iniciar duelo":
                        action Jump("bs_saga_launch_prepared_duel")
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Marcar item/consumible para combate (flag)" size 20 color "#EAF6FF"
                    text "Consumibles" size 16 color "#CFE6FA"
                    if _cons:
                        for row in _cons[:8]:
                            $ _cid = str(row.get("item_id", ""))
                            textbutton (_cid + " x" + str(row.get("qty", 0))):
                                action [Function(bs_saga_set_prep_flag, "consumable", _cid), Jump("bs_saga_preparation_verify")]
                    else:
                        text "Sin consumibles en inventario." size 14 color "#9FB9D1"
                    null height 6
                    text "Items equipables" size 16 color "#CFE6FA"
                    if _items:
                        for row in _items[:8]:
                            $ _iid = str(row.get("item_id", ""))
                            textbutton (_iid + " x" + str(row.get("qty", 0))):
                                action [Function(bs_saga_set_prep_flag, "item", _iid), Jump("bs_saga_preparation_verify")]
                    else:
                        text "Sin equipables en inventario." size 14 color "#9FB9D1"

screen bs_saga_tech_catalog_screen():
    tag menu
    $ _mode = str(bs_saga_tech_catalog_mode or "").lower()
    $ _tier = str(bs_saga_tech_catalog_tier or "C").upper()
    $ _tiers = bs_saga_tech_tier_keys()
    $ _ttype = str(bs_saga_tech_catalog_type or "ofensivas").lower()
    $ _types = bs_saga_tech_type_keys()
    $ _rows = bs_saga_tech_catalog().get(_tier, []) if _mode == "tier" else (bs_saga_tech_catalog_by_type().get(_ttype, []) if _mode == "type" else [])

    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Territorio: Catálogo de técnicas" size 22 color "#D7EEFF" yalign 0.7
            null width 70
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")

        hbox:
            spacing 14

            frame:
                xsize 240
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Modo de listado" size 24 color "#DDEEFF"
                    textbutton "Por tier":
                        action Function(bs_saga_tech_catalog_set_mode, "tier")
                    textbutton "Por tipo":
                        action Function(bs_saga_tech_catalog_set_mode, "type")
                    null height 8

                    if _mode == "tier":
                        text "Tiers" size 24 color "#DDEEFF"
                        for tt in _tiers:
                            textbutton "Tier [tt]":
                                action SetVariable("bs_saga_tech_catalog_tier", tt)
                    elif _mode == "type":
                        text "Tipos" size 24 color "#DDEEFF"
                        for tp in _types:
                            $ _tp_label = bs_saga_labelize(tp)
                            textbutton _tp_label:
                                action SetVariable("bs_saga_tech_catalog_type", tp)

            frame:
                xfill True
                yfill True
                padding (12, 12)
                background Solid("#102438")
                vbox:
                    spacing 8
                    if _mode == "tier":
                        text "Técnicas liberadas · Tier [_tier]" size 22 color "#EAF6FF"
                    elif _mode == "type":
                        $ _type_label = bs_saga_labelize(_ttype)
                        text "Técnicas liberadas · Tipo [_type_label]" size 22 color "#EAF6FF"
                    else:
                        text "Selecciona \"Por tier\" o \"Por tipo\" para desplegar categorías." size 20 color "#AFCFE8"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 410
                        vbox:
                            spacing 8
                            if _rows:
                                for row in _rows:
                                    $ _n = str(row.get("name", "?") or "?")
                                    $ _d = str(row.get("desc", "") or "")
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (10, 8)
                                        vbox:
                                            spacing 4
                                            text _n size 20 color "#CDE7FF"
                                            text _d size 16 color "#AFCFE8"
                            else:
                                text ("Sin técnicas configuradas para este tier." if _mode == "tier" else ("Sin técnicas configuradas para este tipo." if _mode == "type" else "")) size 18 color "#9FB9D1"

screen bs_saga_tower_screen():
    tag menu

    $ _tf = str(bs_saga_tower_tier_filter or "ALL").upper()
    $ _selected_floor = int(bs_saga_tower_selected_floor or 1)
    $ _rows = bs_saga_tower_filter_floors(_tf, 100)
    $ _selected = bs_saga_tower_selected_row(_selected_floor, 100)
    $ _selected_tier = str(_selected.get("tier", "C") or "C").upper()
    $ _selected_tier_start = int(_selected.get("tier_range_start", 1) or 1)
    $ _selected_tier_end = int(_selected.get("tier_range_end", 10) or 10)
    $ _selected_slot_type = str(_selected.get("slot_type", "guardian") or "guardian")
    $ _selected_title = str(_selected.get("title", "—") or "—")
    $ _selected_subtitle = str(_selected.get("subtitle", "—") or "—")
    $ _selected_floor_label = int(_selected.get("floor", 1) or 1)
    $ _filter_label = ("todas" if _tf == "ALL" else ("tier " + _tf))

    add Solid("#0E1A28")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Territorio: Torre del cielo" size 22 color "#D7EEFF" yalign 0.7
            null width 40
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (18, 18)
        background Solid("#14273B")

        hbox:
            spacing 16

            frame:
                xsize 240
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Pisos (1-100)" size 22 color "#DDEEFF"
                    text "Filtro: [_filter_label]" size 16 color "#9FC4E2"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 420
                        vbox:
                            spacing 6
                            for row in _rows:
                                $ _f = int(row.get("floor", 1) or 1)
                                $ _tier = str(row.get("tier", "C") or "C").upper()
                                textbutton ("Piso %03d · Tier %s" % (_f, _tier)):
                                    action SetVariable("bs_saga_tower_selected_floor", _f)

            frame:
                xfill True
                yfill True
                padding (14, 14)
                background Solid("#11253A")
                vbox:
                    spacing 10

                    hbox:
                        spacing 8
                        text "Tiers" size 20 color "#DCEEFF"
                        textbutton "Todos" action SetVariable("bs_saga_tower_tier_filter", "ALL")
                        textbutton "Tier C" action SetVariable("bs_saga_tower_tier_filter", "C")
                        textbutton "Tier B" action SetVariable("bs_saga_tower_tier_filter", "B")
                        textbutton "Tier A" action SetVariable("bs_saga_tower_tier_filter", "A")
                        textbutton "Tier S" action SetVariable("bs_saga_tower_tier_filter", "S")

                    hbox:
                        spacing 20
                        frame:
                            xsize 290
                            ysize 360
                            background Solid("#0D1A2A")
                            padding (12, 12)
                            vbox:
                                spacing 8
                                text ("Panel visual · Piso %03d" % _selected_floor_label) size 18 color "#CDE7FF"
                                null height 240
                                text "Placeholder visual (héroe / NPC / evento)." size 16 color "#8EABC5"

                        frame:
                            xfill True
                            ysize 360
                            padding (10, 10)
                            background Solid("#1A3044")
                            vbox:
                                spacing 8
                                text ("Información del piso %03d" % _selected_floor_label) size 20 color "#E5F4FF"
                                frame:
                                    xfill True
                                    background Solid("#1B3348")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text ("Tier asignado: " + _selected_tier) size 18 color "#D0E9FF"
                                        text ("Rango tier: pisos %03d-%03d" % (_selected_tier_start, _selected_tier_end)) size 17 color "#B8D9F2"
                                        text ("Tipo de nodo: " + ("Guardián" if _selected_slot_type == "guardian" else "Buff / Sorpresa")) size 18 color "#D0E9FF"
                                        text ("Estado: " + _selected_title) size 17 color "#B8D9F2"
                                        text ("Detalle: " + _selected_subtitle) size 17 color "#B8D9F2"
                                frame:
                                    xfill True
                                    background Solid("#173048")
                                    padding (10, 8)
                                    text "Placeholder de stats/loot/requisitos del piso (por completar)." size 16 color "#AFCFE8"

# ---------- flujo de entrada ----------

label bs_saga_intro_splash:
    scene black
    with dissolve
    centered "BATTLESTARS SAGA"
    pause 0.9
    jump bs_saga_lobby

label bs_saga_lobby:
    call screen bs_saga_lobby_screen
    return

# ---------- rutas panel jugar ----------

label bs_saga_duelo_libre:
    $ bs_saga_prep_intent_duel = True
    $ bs_saga_prep_context = "staging"
    jump bs_saga_preparacion

label bs_saga_preparation_verify:
    call screen bs_saga_preparation_verify_screen
    return

label bs_saga_launch_prepared_duel:
    $ _contract = bs_saga_precombat_contract_validate()
    if not bool((_contract or {}).get("ok", False)):
        $ _block = list((_contract or {}).get("blocking", []) or [])
        if _block:
            $ _first = _block[0]
            $ bs_saga_set_message("No puedes iniciar duelo: " + str(_first.get("label", "check bloqueante")) + ".")
        else:
            $ bs_saga_set_message("No puedes iniciar duelo: validación pre-combate incompleta.")
        jump bs_saga_preparacion
    $ _ok = bs_saga_apply_preparation_for_duel()
    if not _ok:
        jump bs_saga_preparacion
    $ bs_saga_prep_intent_duel = False
    $ bs_saga_prep_context = "room"
    jump battle_start

label bs_saga_torneo_tier_c:
    scene black
    centered "[Battlestars Saga] Torneo Tier C\n\nRuta provisional lista para implementación."
    jump bs_saga_lobby

label bs_saga_torneo_tier_b_locked:
    scene black
    centered "[Battlestars Saga] Torneo Tier B\n\nNo disponible en esta fase."
    jump bs_saga_lobby

label bs_saga_torneo_tier_a_locked:
    scene black
    centered "[Battlestars Saga] Torneo Tier A\n\nNo disponible en esta fase."
    jump bs_saga_lobby

label bs_saga_torre_cielo_locked:
    scene black
    centered "Battlestars Saga · Torre del cielo\n\nNo disponible en esta fase."
    jump bs_saga_lobby

label bs_saga_torre_cielo:
    call screen bs_saga_tower_screen
    return

# ---------- rutas panel gestión ----------

label bs_saga_preparacion:
    if bool(getattr(store, "bs_saga_prep_intent_duel", False)):
        $ bs_saga_prep_context = "staging"
    elif str(getattr(store, "bs_saga_prep_context", "") or "") not in ("room", "staging"):
        $ bs_saga_prep_context = "room"
    if not (bs_saga_prep_duel_rotation_ids or []):
        $ bs_saga_refresh_duel_rotation_heroes(5)
    if not (bs_saga_prep_selected_party_ids or []):
        if bs_saga_prep_selected_hero:
            $ bs_saga_prep_selected_party_ids = [str(bs_saga_prep_selected_hero)]
    if str(getattr(store, "bs_saga_prep_context", "room") or "room").strip().lower() == "staging":
        call screen bs_saga_duel_staging_screen
    else:
        call screen bs_saga_preparation_room_screen
    return

label bs_saga_perfil:
    call screen bs_saga_profile_screen
    return

label bs_saga_heroes:
    call screen bs_saga_heroes_screen
    return

label bs_saga_tienda:
    call screen bs_saga_catalog_screen
    return

label bs_saga_inventario:
    call screen bs_saga_inventory_screen
    return

label bs_saga_catalogo_items:
    call screen bs_saga_catalog_screen
    return

label bs_saga_catalogo_tecnicas:
    call screen bs_saga_tech_catalog_screen
    return
