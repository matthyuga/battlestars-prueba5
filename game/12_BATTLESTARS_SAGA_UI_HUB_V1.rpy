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
    "tier": "C",
    "gold": 5000,
    "gems": 0
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
default bs_saga_prep_flag_item_id = ""
default bs_saga_prep_flag_consumable_id = ""
default bs_saga_prep_intent_duel = False

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
            "tier": "C",
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

        if bs_saga_hero_is_owned(hero_id):
            bs_saga_set_message("Ya posees a {}.".format(hero_name))
            return False
        if gold_before < price:
            bs_saga_set_message("Oro insuficiente para {} ({}).".format(hero_name, price))
            return False

        gold_after = gold_before - price
        acc["gold"] = gold_after
        heroes_owned[hero_id] = {
            "hero_id": hero_id,
            "owned": True,
            "level": 1,
            "exp": 0,
            "is_rotation_free": False,
            "name": hero_name
        }
        bs_saga_audit_push("buy_hero", {
            "hero_id": hero_id,
            "hero_name": hero_name,
            "price_gold": price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        bs_saga_audit_push("gold_delta", {
            "reason": "buy_hero",
            "delta": -price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        bs_saga_set_message("Compraste a {} por {} oro.".format(hero_name, price))
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
        if gold_before < total_price:
            bs_saga_set_message("Oro insuficiente para {} x{}.".format(item_name, q))
            return False

        bucket = bs_saga_item_bucket(item_row)
        bucket_data = account_inv.get(bucket, {})
        before_qty = int(bucket_data.get(item_id, 0) or 0)
        after_qty = before_qty + q
        bucket_data[item_id] = after_qty
        account_inv[bucket] = bucket_data

        gold_after = gold_before - total_price
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
            "delta": -total_price,
            "gold_before": gold_before,
            "gold_after": gold_after
        })
        bs_saga_set_message("Compraste {} x{} por {} oro.".format(item_name, q, total_price))
        return True

    def bs_saga_inventory_rows():
        inv = getattr(S, "bs_saga_inventory_state", {})
        if not isinstance(inv, dict):
            return []
        account_inv = inv.get("account_inventory", {})
        if not isinstance(account_inv, dict):
            return []
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
        data = getattr(S, "CHARACTER_DATA", None)
        if isinstance(data, dict):
            out = [str(k) for k in data.keys() if str(k)]
            if out:
                return out
        return ["Harribel", "Grimmjow", "Nel", "Hollow"]

    def bs_saga_duel_combat_pool_rows():
        ready = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        if not ready:
            ready = ["Harribel", "Grimmjow", "Nel", "Hollow"]
        rot = getattr(S, "bs_saga_prep_duel_rotation_ids", None)
        if not isinstance(rot, list) or not rot:
            rot = bs_saga_refresh_duel_rotation_heroes(min(5, len(ready)))
        rot_lc = {str(x).lower() for x in (rot or [])}

        out = []
        for cid in ready:
            is_owned = bs_saga_hero_is_owned(cid)
            in_rotation = cid.lower() in rot_lc
            state = "disponible" if is_owned else ("para_probar" if in_rotation else "bloqueado")
            out.append({
                "hero_id": cid,
                "name": cid,
                "tier": "C",
                "owned": bool(is_owned),
                "in_rotation": bool(in_rotation),
                "available": bool(is_owned or in_rotation),
                "state": state
            })
        return out

    def bs_saga_refresh_duel_rotation_heroes(count=4):
        pool = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        if not pool:
            pool = ["Harribel", "Grimmjow", "Nel", "Hollow"]
        unique = []
        for hid in pool:
            if hid not in unique:
                unique.append(hid)
        renpy.random.shuffle(unique)
        c = int(count or 4)
        if c < 1:
            c = 1
        if len(unique) < c:
            c = len(unique)
        S.bs_saga_prep_duel_rotation_ids = unique[:c]
        return list(S.bs_saga_prep_duel_rotation_ids)

    def bs_saga_resolve_combat_id(hero_id, fallback="Harribel"):
        hid = str(hero_id or "").strip()
        ready = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        if hid in ready:
            return hid
        fb = str(fallback or "").strip()
        if fb in ready:
            return fb
        return str(ready[0] if ready else "Harribel")

    def bs_saga_refresh_rotation_heroes(count=5):
        rows = []
        for r in bs_saga_db_rows():
            if not isinstance(r, dict):
                continue
            hid = bs_saga_hero_id(r)
            if hid:
                rows.append(str(hid))
        if not rows:
            rows = ["Harribel", "Grimmjow", "Nel", "Hollow", "Harribel"]
        unique = []
        for hid in rows:
            if hid not in unique:
                unique.append(hid)
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
            bs_saga_set_message("Preparación: héroe activo = {}.".format(str(row.get("name", hid))))
            return True
        bs_saga_set_message("Héroe no encontrado para preparación.")
        return False

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

    def bs_saga_apply_preparation_for_duel():
        mode = str(getattr(S, "bs_saga_prep_selected_mode", "1v1") or "1v1")
        my_hero = bs_saga_resolve_combat_id(getattr(S, "bs_saga_prep_selected_hero", ""), fallback="")
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
                candidates = ["Hollow"]
            enemy_id = str(candidates[renpy.random.randint(0, len(candidates) - 1)])
        if not enemy_id:
            enemy_id = "Hollow"

        # Dual-write obligatorio: id activo + listas para evitar fallbacks legacy inconsistentes.
        S.battle_enemy_id = enemy_id
        S.battle_player_ids = [my_hero]
        S.battle_enemy_ids = [enemy_id]
        if S.battle_team_mode == "2v2":
            candidates = [x for x in all_ids if x not in (my_hero, enemy_id)]
            if len(candidates) < 2:
                candidates = ["Grimmjow", "Nel", "Hollow", "Harribel"]
            renpy.random.shuffle(candidates)
            p2 = candidates[0]
            e2 = candidates[1] if len(candidates) > 1 else "Hollow"
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

        S.battle_prepared_item_id = str(getattr(S, "bs_saga_prep_flag_item_id", "") or "")
        S.battle_prepared_consumable_id = str(getattr(S, "bs_saga_prep_flag_consumable_id", "") or "")
        bs_saga_register_hero_usage(my_hero)
        bs_saga_set_message("Preparación verificada. Duelo listo.")
        return True

    def bs_saga_db_rows():
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
        # Esquema inicial del catálogo para UI (v1 wireframe)
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
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _tier = str(_acc.get("tier", "C") or "C")
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
                text ("Tier " + _tier) size 20 color "#D7EEFF" yalign 0.7
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
                                    vbox:
                                        spacing 5
                                        if _heroes:
                                            for h in _heroes:
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
                                                                action [Function(bs_saga_buy_hero, h), Jump("bs_saga_heroes")]
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
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _tier = str(_acc.get("tier", "C") or "C")
    $ _top_total = bs_saga_top_heroes(3, False)
    $ _top_24 = bs_saga_top_heroes(3, True)

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
                    text ("Tier: " + _tier) size 18 color "#D0E9FF"
                    text ("Nivel: " + str(_lvl)) size 18 color "#D0E9FF"
                    text ("EXP: " + str(_exp) + "/" + str(_next)) size 18 color "#D0E9FF"
                    text ("Oro: " + str(_gold)) size 18 color "#F7D774"
                    text "Historial de combate: pendiente de integración detallada." size 16 color "#9FC4E2"
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

screen bs_saga_preparation_screen():
    tag menu
    $ _rows = bs_saga_duel_combat_pool_rows()
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy_hero = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _rotation_preview = ", ".join([str(x) for x in (bs_saga_prep_duel_rotation_ids or [])[:5]])

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
            text "Preparación pre-combate" size 22 color "#D7EEFF" yalign 0.7
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
                    text ("Rotación actual (5): " + (_rotation_preview if _rotation_preview else "sin generar")) size 14 color "#9FC4E2"
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
                            else:
                                text "No hay roster cargado." size 18 color "#9FB9D1"
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Configuración de entrada" size 22 color "#EAF6FF"
                    text ("Héroe activo: " + (_hero if _hero else "sin seleccionar")) size 16 color "#CFE6FA"
                    text "Modo de juego" size 16 color "#D0E9FF"
                    hbox:
                        spacing 6
                        textbutton "1v1" action SetVariable("bs_saga_prep_selected_mode", "1v1")
                        textbutton "2v2" action SetVariable("bs_saga_prep_selected_mode", "2v2")
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
                    text "Build rápida" size 16 color "#D0E9FF"
                    hbox:
                        spacing 6
                        textbutton "Balanceado" action SetVariable("bs_saga_prep_selected_build", "balanceado")
                        textbutton "Ofensivo" action SetVariable("bs_saga_prep_selected_build", "ofensivo")
                        textbutton "Defensivo" action SetVariable("bs_saga_prep_selected_build", "defensivo")
                    null height 12
                    text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"
                    text "Chequear técnicas/pool por tier: pendiente de integración detallada." size 15 color "#9FC4E2"
                    textbutton "Verificar preparación e iniciar duelo":
                        action Jump("bs_saga_preparation_verify")

screen bs_saga_preparation_verify_screen():
    tag menu
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
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
                    text ("Item flag: " + (_flag_item if _flag_item else "ninguno")) size 14 color "#9FC4E2"
                    text ("Consumible flag: " + (_flag_cons if _flag_cons else "ninguno")) size 14 color "#9FC4E2"
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
    jump bs_saga_preparacion

label bs_saga_preparation_verify:
    call screen bs_saga_preparation_verify_screen
    return

label bs_saga_launch_prepared_duel:
    $ _ok = bs_saga_apply_preparation_for_duel()
    if not _ok:
        jump bs_saga_preparacion
    $ bs_saga_prep_intent_duel = False
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
    if not (bs_saga_prep_duel_rotation_ids or []):
        $ bs_saga_refresh_duel_rotation_heroes(5)
    call screen bs_saga_preparation_screen
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
