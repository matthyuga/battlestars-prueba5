# ============================================================
# 12_BATTLESTARS_SAGA_UI_HUB_V1.rpy
# Lobby in-game Battlestars Saga (Wireframe funcional v1)
# ============================================================

# Fase 1 de split: defaults/flags movidos a `game/ui_hub/ui_hub_state.rpy`.

init -880 python:
    import renpy.store as S
    import json
    import re
    import time

    def bs_saga_ui_hub_bootstrap_status_v1():
        return {
            "module": "12_BATTLESTARS_SAGA_UI_HUB_V1",
            "status": "phase_5_bootstrap",
            "purpose": "labels/flow + compat bridge",
            "split_modules": [
                "game/ui_hub/ui_hub_state.rpy",
                "game/ui_hub/ui_hub_roster_service.rpy",
                "game/ui_hub/ui_hub_tech_service.rpy",
                "game/ui_hub/ui_hub_screens_lobby.rpy",
                "game/ui_hub/ui_hub_screens_prep.rpy",
                "game/ui_hub/ui_hub_audit_economy.rpy"
            ]
        }

    def bs_saga_slug(text):
        raw = str(text or "").strip().lower()
        raw = re.sub(r"[^a-z0-9]+", "_", raw)
        raw = re.sub(r"_+", "_", raw)
        return raw.strip("_") or "unknown"

    # Fase 4 de split:
    # - bs_saga_account
    # - bs_saga_gold
    # - bs_saga_set_message
    # - bs_saga_dev_can_edit_account
    # - bs_saga_dev_set_account_state
    # ahora viven en `game/ui_hub/ui_hub_audit_economy.rpy`.

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

    # Fase 4 de split:
    # - bs_saga_audit_push
    # ahora vive en `game/ui_hub/ui_hub_audit_economy.rpy`.

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

    # Fase 2 de split:
    # - bs_saga_hero_is_owned
    # - bs_saga_owned_hero_entry
    # ahora viven en `game/ui_hub/ui_hub_roster_service.rpy`.

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

    # Fase 4 de split:
    # - bs_saga_buy_hero
    # ahora vive en `game/ui_hub/ui_hub_audit_economy.rpy`.

    # Fase 4 de split:
    # - bs_saga_item_id
    # - bs_saga_item_price
    # - bs_saga_item_bucket
    # - bs_saga_buy_item
    # ahora viven en `game/ui_hub/ui_hub_audit_economy.rpy`.

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

    def bs_saga_clamp_hp_reward_multiplier(value):
        try:
            m = int(value or 1)
        except:
            m = 1
        if m < 1:
            m = 1
        if m > 5:
            m = 5
        return int(m)

    def bs_saga_set_prep_hp_reward_multiplier(value):
        m = bs_saga_clamp_hp_reward_multiplier(value)
        S.bs_saga_prep_hp_reward_multiplier = int(m)
        return int(m)

    def bs_saga_reward_conditions_defaults():
        return {
            "use_concentrar": False,
            "no_direct_attack": False,
            "no_stance_swap": False,
            "low_damage_taken": False,
            "daily_mission": False,
        }

    def bs_saga_get_prep_reward_conditions():
        raw = getattr(S, "bs_saga_prep_reward_conditions", None)
        out = bs_saga_reward_conditions_defaults()
        if isinstance(raw, dict):
            for k in out.keys():
                out[k] = bool(raw.get(k, out[k]))
        S.bs_saga_prep_reward_conditions = dict(out)
        return dict(out)

    def bs_saga_set_prep_reward_condition(key, enabled):
        kk = str(key or "").strip().lower()
        out = bs_saga_get_prep_reward_conditions()
        if kk not in out:
            return False
        out[kk] = bool(enabled)
        S.bs_saga_prep_reward_conditions = dict(out)
        return True

    def bs_saga_toggle_prep_reward_condition(key):
        kk = str(key or "").strip().lower()
        out = bs_saga_get_prep_reward_conditions()
        if kk not in out:
            return False
        out[kk] = not bool(out[kk])
        S.bs_saga_prep_reward_conditions = dict(out)
        return True

    def bs_saga_adjust_reward_base_param(field, delta):
        ff = str(field or "").strip().lower()
        try:
            dd = float(delta or 0)
        except:
            dd = 0.0
        if ff == "base_exp":
            cur = float(getattr(S, "bs_saga_reward_base_exp_real", 35) or 35)
            cur = max(1.0, min(10000.0, cur + dd))
            S.bs_saga_reward_base_exp_real = int(round(cur))
            return int(getattr(S, "bs_saga_reward_base_exp_real", 35) or 35)
        if ff == "base_oro":
            cur = float(getattr(S, "bs_saga_reward_base_oro_real", 15) or 15)
            cur = max(1.0, min(20000.0, cur + dd))
            S.bs_saga_reward_base_oro_real = int(round(cur))
            return int(getattr(S, "bs_saga_reward_base_oro_real", 15) or 15)
        if ff == "step_exp":
            cur = float(getattr(S, "bs_saga_reward_step_exp", 3.5) or 3.5)
            cur = max(0.1, min(50.0, cur + dd))
            S.bs_saga_reward_step_exp = float(round(cur, 2))
            return float(getattr(S, "bs_saga_reward_step_exp", 3.5) or 3.5)
        if ff == "step_oro":
            cur = float(getattr(S, "bs_saga_reward_step_oro", 2.0) or 2.0)
            cur = max(0.1, min(50.0, cur + dd))
            S.bs_saga_reward_step_oro = float(round(cur, 2))
            return float(getattr(S, "bs_saga_reward_step_oro", 2.0) or 2.0)
        return None

    def bs_saga_build_reward_condition_profile():
        cc = bs_saga_get_prep_reward_conditions()
        exp_mult = 1.0
        oro_mult = 1.0
        prob_mult = 1.0
        tags = []

        if bool(cc.get("use_concentrar", False)):
            exp_mult *= 1.12
            oro_mult *= 1.08
            tags.append("use_concentrar")
        if bool(cc.get("no_direct_attack", False)):
            exp_mult *= 1.18
            oro_mult *= 1.15
            tags.append("no_direct_attack")
        if bool(cc.get("no_stance_swap", False)):
            exp_mult *= 1.10
            oro_mult *= 1.10
            tags.append("no_stance_swap")
        if bool(cc.get("low_damage_taken", False)):
            exp_mult *= 1.14
            oro_mult *= 1.12
            tags.append("low_damage_taken")
        if bool(cc.get("daily_mission", False)):
            exp_mult *= 1.25
            oro_mult *= 1.30
            prob_mult *= 1.15
            tags.append("daily_mission")

        exp_mult = max(0.50, min(3.00, float(exp_mult)))
        oro_mult = max(0.50, min(3.00, float(oro_mult)))
        prob_mult = max(0.50, min(2.00, float(prob_mult)))
        return {
            "conditions": dict(cc),
            "exp_mult": float(round(exp_mult, 4)),
            "oro_mult": float(round(oro_mult, 4)),
            "probability_mult": float(round(prob_mult, 4)),
            "tags": list(tags),
            "base_exp_real": int(getattr(S, "bs_saga_reward_base_exp_real", 35) or 35),
            "base_oro_real": int(getattr(S, "bs_saga_reward_base_oro_real", 15) or 15),
            "step_exp": float(getattr(S, "bs_saga_reward_step_exp", 3.5) or 3.5),
            "step_oro": float(getattr(S, "bs_saga_reward_step_oro", 2.0) or 2.0),
        }

    def bs_saga_clamp_prep_tech_step(value):
        allowed = (25, 50, 100, 150, 200, 500, 1000)
        try:
            raw = int(value or 25)
        except:
            raw = 25
        if raw in allowed:
            return int(raw)
        # fallback al valor permitido más cercano.
        best = 25
        best_diff = abs(raw - best)
        for x in allowed:
            d = abs(raw - int(x))
            if d < best_diff:
                best = int(x)
                best_diff = d
        return int(best)

    def bs_saga_set_prep_tech_step(value):
        step = bs_saga_clamp_prep_tech_step(value)
        S.bs_saga_prep_tech_step = int(step)
        return int(step)

    # Fase 4 de split:
    # - bs_saga_account_bucket_qty
    # - bs_saga_account_bucket_add
    # ahora viven en `game/ui_hub/ui_hub_audit_economy.rpy`.

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

    def bs_saga_account_tier_current():
        acc = getattr(S, "bs_saga_account_state", {}) or {}
        t = str(acc.get("tier", "") or "").strip().upper()
        if not t:
            t = str(bs_saga_refresh_account_tier(reason="prep_pool_eval") or "").strip().upper()
        return t if t else "C"

    def bs_saga_prep_pool_tier_for_hero(hero_id):
        hid = str(hero_id or "").strip()
        hero_tier = bs_saga_hero_tier(hid, "C")
        account_tier = bs_saga_account_tier_current()
        rank_fn = getattr(S, "bs_saga_tier_rank_value", None)
        if not callable(rank_fn):
            return account_tier
        # Héroes de rotación/prueba no pueden usar pool superior al tier de cuenta.
        # Para héroes propios, también se respeta el tier de cuenta como tope.
        if int(rank_fn(hero_tier)) > int(rank_fn(account_tier)):
            return account_tier
        return hero_tier

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
            pool_tier = bs_saga_prep_pool_tier_for_hero(hid)
            item = {
                "mode": "preconfig",
                "tier": tier,
                "pool_tier": pool_tier,
                "pool_total": bs_saga_tier_pool_total(pool_tier),
                "pool_spent_off": 0,
                "pool_spent_def": 0,
                "tech_points": {}
            }
        mode_norm = str(item.get("mode", "preconfig") or "preconfig").strip().lower()
        # Fase 1 UX v2: se elimina "virgen" como modo operativo.
        # Compatibilidad: perfiles legacy en virgen se migran a preconfig.
        if mode_norm != "preconfig":
            mode_norm = "preconfig"
        item["mode"] = mode_norm
        if not isinstance(item.get("tech_points", {}), dict):
            item["tech_points"] = {}
        item["tier"] = str(item.get("tier", bs_saga_hero_tier(hid, "C")) or bs_saga_hero_tier(hid, "C")).upper()
        pool_tier_now = bs_saga_prep_pool_tier_for_hero(hid)
        item["pool_tier"] = str(pool_tier_now or "C").upper()
        item["pool_total"] = bs_saga_tier_pool_total(item["pool_tier"])
        builds[bld] = item
        c["builds"] = builds
        cfgs[cfg] = c
        h["configs"] = cfgs
        root[hid] = h
        S.bs_saga_hero_tech_builds = root
        return item

    # Fase 2 de split:
    # - bs_saga_tier_allowed_tech_ids
    # - bs_saga_tech_display_name
    # ahora viven en `game/ui_hub/ui_hub_tech_service.rpy`.

    def bs_saga_recalc_tech_pool_spent(hero_id, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}

        bt = getattr(S, "battle_techniques", {}) or {}
        off = 0
        deff = 0
        for k, v in tp.items():
            key = str(k or "").strip().lower()
            if not key:
                continue
            try:
                pts = int(v or 0)
            except:
                pts = 0
            if pts < 0:
                pts = 0
            ttype = ""
            row = bt.get(key, {}) if isinstance(bt, dict) else {}
            if isinstance(row, dict):
                ttype = str(row.get("type", "") or "").strip().lower()
            if ttype == "defensive":
                deff += pts
            elif ttype == "offensive":
                off += pts
            else:
                # Fase 2: specials/neutras no consumen pool de asignación.
                continue
        item["pool_spent_off"] = int(off)
        item["pool_spent_def"] = int(deff)
        return True

    def bs_saga_hero_tech_points_add(hero_id, tech_key, delta, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        key = str(tech_key or "").strip().lower()
        if not key:
            return False

        try:
            d = int(delta or 0)
        except:
            d = 0
        if d == 0:
            return False

        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}
        try:
            cur = int(tp.get(key, 0) or 0)
        except:
            cur = 0
        nxt = cur + d
        if nxt < 0:
            nxt = 0

        # Validar que la técnica esté permitida por tier
        tier = str(item.get("tier", bs_saga_hero_tier(hero_id, "C")) or "C").upper()
        allowed = bs_saga_tier_allowed_tech_ids(tier)
        if key not in allowed:
            bs_saga_set_message("Técnica no permitida para tier {}: {}.".format(tier, key))
            return False
        fn_point_alloc = getattr(S, "bs_saga_is_point_alloc_tech", None)
        if callable(fn_point_alloc) and (not bool(fn_point_alloc(key))):
            bs_saga_set_message("Técnica especial sin asignación de puntos: {}.".format(bs_saga_tech_display_name(key)))
            return False

        # Aplicación tentativa + control pool total
        old = dict(tp)
        tp[key] = int(nxt)
        item["tech_points"] = tp
        bs_saga_recalc_tech_pool_spent(hero_id, config_id, build_id)
        total = int(item.get("pool_total", 0) or 0)
        spent = int(item.get("pool_spent_off", 0) or 0) + int(item.get("pool_spent_def", 0) or 0)
        if spent > total:
            item["tech_points"] = old
            bs_saga_recalc_tech_pool_spent(hero_id, config_id, build_id)
            bs_saga_set_message("Pool excedido ({}/{}).".format(spent, total))
            return False
        return True

    def bs_saga_hero_tech_reset_one(hero_id, tech_key, config_id=None, build_id=None):
        return bs_saga_hero_tech_points_set(hero_id, tech_key, 0, config_id, build_id)

    def bs_saga_hero_tech_reset_build(hero_id, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        item["tech_points"] = {}
        item["pool_spent_off"] = 0
        item["pool_spent_def"] = 0
        bs_saga_set_message("Editor técnico: build reseteada para {}.".format(str(hero_id or "")))
        return True

    def bs_saga_hero_tech_toggle_enabled(hero_id, tech_key, config_id=None, build_id=None):
        item = bs_saga_hero_tech_profile_get(hero_id, config_id, build_id)
        if not isinstance(item, dict):
            return False
        key = str(tech_key or "").strip().lower()
        if not key:
            return False
        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}
        cur = int(tp.get(key, 0) or 0)
        if cur > 0:
            return bs_saga_hero_tech_points_set(hero_id, key, 0, config_id, build_id)
        return bs_saga_hero_tech_points_add(hero_id, key, +25, config_id, build_id)

    def bs_saga_tech_editor_rows(hero_id, config_id=None, build_id=None, tab="offensive"):
        hid = str(hero_id or "").strip()
        if not hid:
            return []
        item = bs_saga_hero_tech_profile_get(hid, config_id, build_id)
        if not isinstance(item, dict):
            return []
        tier = str(item.get("tier", bs_saga_hero_tier(hid, "C")) or "C").upper()
        allowed = bs_saga_tier_allowed_tech_ids(tier)
        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}
        bt = getattr(S, "battle_techniques", {}) or {}
        ttab = str(tab or "offensive").strip().lower()
        out = []
        for tid in allowed:
            key = str(tid or "").strip().lower()
            row = bt.get(key, {}) if isinstance(bt, dict) else {}
            if not isinstance(row, dict):
                row = {}
            ttype = str(row.get("type", "") or "").strip().lower()
            if ttab == "offensive" and ttype != "offensive":
                continue
            if ttab == "defensive" and ttype != "defensive":
                continue
            if ttab == "special" and ttype not in ("special",):
                continue
            pts = int(tp.get(key, 0) or 0)
            out.append({
                "tech_id": key,
                "name": bs_saga_tech_display_name(key),
                "type": ttype or "special",
                "points": pts,
                "enabled": bool(pts > 0)
            })
        out.sort(key=lambda r: (r.get("type", ""), r.get("name", "")))
        return out

    def bs_saga_allowed_tech_ids_for_combat(hero_id=None):
        hid = str(hero_id or getattr(S, "battle_player_id", "") or "").strip()
        if not hid:
            return []
        # Fallback por tier
        tier = bs_saga_hero_tier(hid, "C")
        base_allowed = bs_saga_tier_allowed_tech_ids(tier)

        profiles = getattr(S, "battle_prepared_player_tech_profiles", {}) or {}
        prof = profiles.get(hid, {}) if isinstance(profiles, dict) else {}
        if not isinstance(prof, dict):
            return list(base_allowed)
        mode = str(prof.get("mode", "preconfig") or "preconfig").strip().lower()
        tp = prof.get("tech_points", {})
        if (not isinstance(tp, dict)):
            return list(base_allowed)

        chosen = []
        for k, v in tp.items():
            key = str(k or "").strip().lower()
            if not key:
                continue
            try:
                pts = int(v or 0)
            except:
                pts = 0
            if pts > 0 and key in base_allowed and key not in chosen:
                chosen.append(key)

        # Si no hay asignación válida, cae al set tier.
        return chosen if chosen else list(base_allowed)

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
        mode = str(out.get("mode", "preconfig") or "preconfig").strip().lower()
        if mode != "preconfig":
            mode = "preconfig"
        out["mode"] = mode
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
        if m != "preconfig":
            m = "preconfig"
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
        tier = str(item.get("tier", bs_saga_hero_tier(hero_id, "C")) or "C").upper()
        if key not in bs_saga_tier_allowed_tech_ids(tier):
            return False
        fn_point_alloc = getattr(S, "bs_saga_is_point_alloc_tech", None)
        if callable(fn_point_alloc) and (not bool(fn_point_alloc(key))):
            return False
        tp = item.get("tech_points", {})
        if not isinstance(tp, dict):
            tp = {}
        prev = dict(tp)
        tp[key] = val
        item["tech_points"] = tp
        bs_saga_recalc_tech_pool_spent(hero_id, config_id, build_id)
        total = int(item.get("pool_total", 0) or 0)
        spent = int(item.get("pool_spent_off", 0) or 0) + int(item.get("pool_spent_def", 0) or 0)
        if spent > total:
            item["tech_points"] = prev
            bs_saga_recalc_tech_pool_spent(hero_id, config_id, build_id)
            return False
        return True

    def bs_saga_apply_prep_points_to_runtime_slots():
        """
        Fase 3: puente de puntos de preparación -> allocator runtime por slot.
        Solo aplica a técnicas ofensivas/defensivas en modo preconfig.
        """
        fn_set_bonus = getattr(S, "spa_set_bonus", None)
        fn_set_available = getattr(S, "spa_set_available", None)
        fn_reset_slot = getattr(S, "spa_reset_slot", None)
        if not callable(fn_set_bonus):
            return False

        player_ids = [str(x) for x in (getattr(S, "battle_player_ids", []) or []) if str(x or "").strip()]
        profiles = getattr(S, "battle_prepared_player_tech_profiles", {}) or {}
        fn_unit_key = getattr(S, "bs_unit_key", None)
        fn_point_alloc = getattr(S, "bs_saga_is_point_alloc_tech", None)

        for idx, pid in enumerate(player_ids):
            unit_key = "player:{}".format(int(idx))
            if callable(fn_unit_key):
                try:
                    unit_key = str(fn_unit_key("player", idx) or unit_key)
                except:
                    pass

            if callable(fn_reset_slot):
                try:
                    fn_reset_slot(unit_key, save=False)
                except:
                    pass

            prof = profiles.get(pid, {}) if isinstance(profiles, dict) else {}
            if not isinstance(prof, dict):
                continue
            if callable(fn_set_available):
                try:
                    fn_set_available(unit_key, int(prof.get("pool_total", 0) or 0), save=False)
                except:
                    pass

            mode = str(prof.get("mode", "virgen") or "virgen").strip().lower()
            if mode != "preconfig":
                continue
            tp = prof.get("tech_points", {})
            if not isinstance(tp, dict):
                continue

            for tid, raw_pts in tp.items():
                tech_id = str(tid or "").strip().lower()
                if not tech_id:
                    continue
                try:
                    pts = int(raw_pts or 0)
                except:
                    pts = 0
                if pts <= 0:
                    continue
                if callable(fn_point_alloc) and (not bool(fn_point_alloc(tech_id))):
                    continue
                try:
                    fn_set_bonus(unit_key, tech_id, int(pts), save=False)
                except:
                    pass

        return True

    def bs_saga_capture_prep_diag(hero_id, config_id=None, build_id=None):
        """
        Barrido A+B (instrumentación):
        - A: visibilidad de modo/points raw vs perfil resuelto para combate.
        - B: detección de preset externo potencialmente sobrescribiendo.
        """
        hid = str(hero_id or "").strip()
        if not hid:
            return {}
        cfg = str(config_id or getattr(S, "bs_saga_prep_selected_config", "cfg1") or "cfg1")
        bld = str(build_id or getattr(S, "bs_saga_prep_selected_build", "balanceado") or "balanceado")

        raw = bs_saga_hero_tech_profile_get(hid, cfg, bld)
        resolved = bs_saga_resolve_hero_tech_profile(hid, cfg, bld)
        if not isinstance(raw, dict):
            raw = {}
        if not isinstance(resolved, dict):
            resolved = {}

        raw_mode = str(raw.get("mode", "virgen") or "virgen").strip().lower()
        res_mode = str(resolved.get("mode", "virgen") or "virgen").strip().lower()
        raw_tp = raw.get("tech_points", {}) if isinstance(raw.get("tech_points", {}), dict) else {}
        res_tp = resolved.get("tech_points", {}) if isinstance(resolved.get("tech_points", {}), dict) else {}
        raw_positive = 0
        for _, v in raw_tp.items():
            try:
                if int(v or 0) > 0:
                    raw_positive += 1
            except:
                pass
        res_positive = 0
        for _, v in res_tp.items():
            try:
                if int(v or 0) > 0:
                    res_positive += 1
            except:
                pass

        preset_callable = bool(callable(getattr(S, "bs_get_hero_tech_preset_v1", None)))
        preset_applied = False
        try:
            fn_preset = getattr(S, "bs_get_hero_tech_preset_v1", None)
            if callable(fn_preset):
                p = fn_preset(hid, str(raw.get("tier", "C") or "C"))
                preset_applied = bool(isinstance(p, dict))
        except:
            preset_applied = False

        points_changed_by_resolve = (raw_tp != res_tp)
        suspicious = bool(
            raw_mode == "preconfig" and (
                (res_mode != "preconfig") or
                (raw_positive > 0 and res_positive <= 0) or
                points_changed_by_resolve
            )
        )

        return {
            "hero_id": hid,
            "cfg": cfg,
            "build": bld,
            "raw_mode": raw_mode,
            "resolved_mode": res_mode,
            "raw_points_positive": int(raw_positive),
            "resolved_points_positive": int(res_positive),
            "preset_callable": bool(preset_callable),
            "preset_applied": bool(preset_applied),
            "points_changed_by_resolve": bool(points_changed_by_resolve),
            "suspicious": bool(suspicious),
        }

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

    # Fase 2 de split:
    # - bs_saga_available_hero_rows
    # - bs_saga_resolve_roster_v1
    # - bs_saga_combat_ready_ids
    # - bs_saga_duel_combat_pool_rows
    # - bs_saga_refresh_duel_rotation_heroes
    # ahora viven en `game/ui_hub/ui_hub_roster_service.rpy`.
    # Compat guard QA: def bs_saga_resolve_roster_v1 (symbol migrated to module file).

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
        mode_tp = str((tp or {}).get("mode", "preconfig") or "preconfig").strip().lower()
        if mode_tp != "preconfig":
            mode_tp = "preconfig"
        pool_total = int((tp or {}).get("pool_total", 0) or 0)
        spent_off = int((tp or {}).get("pool_spent_off", 0) or 0)
        spent_def = int((tp or {}).get("pool_spent_def", 0) or 0)
        spent_total = int(spent_off + spent_def)
        ok_pool = (spent_total <= pool_total)
        checks.append({
            "id": "pool_consistency",
            "ok": ok_pool,
            "severity": "block",
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
        hp_reward_mult = bs_saga_clamp_hp_reward_multiplier(getattr(S, "bs_saga_prep_hp_reward_multiplier", 1))
        S.bs_saga_prep_hp_reward_multiplier = int(hp_reward_mult)
        S.story_pilot_hp_reward_multiplier = int(hp_reward_mult)
        reward_profile = bs_saga_build_reward_condition_profile()
        S.story_pilot_reward_condition_profile = dict(reward_profile)
        S.story_pilot_reward_conditions = dict(reward_profile.get("conditions", {}))
        S.story_pilot_reward_condition_tags = list(reward_profile.get("tags", []))
        S.story_pilot_reward_exp_mult = float(reward_profile.get("exp_mult", 1.0) or 1.0)
        S.story_pilot_reward_oro_mult = float(reward_profile.get("oro_mult", 1.0) or 1.0)
        S.story_pilot_reward_probability_mult = float(reward_profile.get("probability_mult", 1.0) or 1.0)
        S.story_pilot_reward_base_exp_real = int(reward_profile.get("base_exp_real", 35) or 35)
        S.story_pilot_reward_base_oro_real = int(reward_profile.get("base_oro_real", 15) or 15)
        S.story_pilot_reward_step_exp = float(reward_profile.get("step_exp", 3.5) or 3.5)
        S.story_pilot_reward_step_oro = float(reward_profile.get("step_oro", 2.0) or 2.0)
        S.battle_prepared_config_id = prep_cfg
        S.battle_prepared_build_id = prep_build
        S.battle_prepared_player_loadouts = {}
        S.battle_prepared_player_tech_profiles = {}
        S.bs_saga_last_prep_diag_by_player = {}
        S.battle_prepared_combat_tuning = {}
        S.battle_prepared_damage_rules = dict(getattr(S, "bs_saga_damage_coherence_rules", {}) or {})
        S.bs_runtime_character_overrides = {}
        for pid in (S.battle_player_ids or []):
            S.battle_prepared_player_loadouts[str(pid)] = bs_saga_hero_loadout_slots(pid, prep_cfg, prep_build)
            S.battle_prepared_player_tech_profiles[str(pid)] = dict(bs_saga_resolve_hero_tech_profile(pid, prep_cfg, prep_build) or {})
            S.bs_saga_last_prep_diag_by_player[str(pid)] = dict(bs_saga_capture_prep_diag(pid, prep_cfg, prep_build) or {})
        # Fase 3: conectar puntos de preparación con valores runtime por slot.
        bs_saga_apply_prep_points_to_runtime_slots()
        # También dejamos override de stats por tier para participantes del combate (player/enemy).
        for pid in (S.battle_player_ids or []) + (S.battle_enemy_ids or []):
            tier = bs_saga_hero_tier(pid, "C")
            prof = bs_saga_tier_core_profile(tier)
            tune = bs_saga_tier_combat_tuning_profile(tier)
            base_hp = int(prof.get("hp", 1000) or 1000)
            # Regla de condición HP:
            # - x5 mantiene el HP base del tier (comportamiento legacy),
            # - x1 representa 20% del HP base (ej: 5000 -> 1000).
            hp_scaled = max(1, int(round((float(base_hp) / 5.0) * float(hp_reward_mult))))
            S.bs_runtime_character_overrides[str(pid)] = {
                "HP": int(hp_scaled),
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

    def bs_saga_load_json_contract(rel_path, default_obj=None):
        path_raw = str(rel_path or "").strip()
        if not path_raw:
            return default_obj

        candidates = [path_raw]
        if path_raw.startswith("game/"):
            candidates.append(path_raw[len("game/"):])
        else:
            candidates.append("game/" + path_raw)

        for p in candidates:
            try:
                f = renpy.loader.load(str(p or ""))
                raw = f.read()
                try:
                    f.close()
                except:
                    pass
                if raw is None:
                    continue
                try:
                    txt = raw.decode("utf-8")
                except:
                    txt = str(raw)
                obj = json.loads(txt)
                if isinstance(obj, dict):
                    return obj
            except:
                pass
        return default_obj

    def bs_saga_item_schema():
        fn_v1 = getattr(S, "bs_get_item_catalog_v1", None)
        if callable(fn_v1):
            cat_v1 = fn_v1()
            if isinstance(cat_v1, dict) and cat_v1:
                return dict(cat_v1)

        cat_override = getattr(S, "bs_item_catalog_v1", None)
        if isinstance(cat_override, dict) and cat_override:
            return dict(cat_override)

        contract = bs_saga_load_json_contract("data/item_catalog_v1.json", {})
        if isinstance(contract, dict) and contract:
            return contract

        # Fallback funcional completo (si falta contrato externo).
        return {
            "consumibles": {
                "title": "Consumibles",
                "groups": {
                    "pociones": [
                        {"name": "Poción HP roja", "rarity": "", "tier_req": "", "meta": "+50% HP"},
                        {"name": "Poción EP roja", "rarity": "", "tier_req": "", "meta": "+50% EP"},
                        {"name": "Poción EC roja", "rarity": "", "tier_req": "", "meta": "+50% EC"},
                        {"name": "Poción de durabilidad roja", "rarity": "", "tier_req": "", "meta": "+50% durabilidad"},
                    ],
                    "amuletos": [
                        {"name": "Espejo reflector", "rarity": "rare", "tier_req": "B", "meta": "Refleja 30% daño (3 usos)"},
                        {"name": "Cilindro mágico", "rarity": "rare", "tier_req": "B", "meta": "Absorbe 30% daño (3 usos)"},
                        {"name": "Espada sagrada", "rarity": "epic", "tier_req": "A", "meta": "+30% daño (3 usos)"},
                    ],
                }
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
                }
            },
            "materiales": {
                "title": "Materiales",
                "groups": {
                    "basicos": [
                        {"name": "Chatarra común", "rarity": "common", "tier_req": "C", "meta": "Material de cambio/trueque"},
                        {"name": "Fragmento reciclado", "rarity": "common", "tier_req": "C", "meta": "Material de cambio/trueque"},
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
                }
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
        fn_v1 = getattr(S, "bs_get_tech_catalog_v1", None)
        if callable(fn_v1):
            out = fn_v1()
            if isinstance(out, dict) and out:
                return dict(out)

        cat_override = getattr(S, "bs_tech_catalog_v1", None)
        if isinstance(cat_override, dict) and cat_override:
            return dict(cat_override)

        contract = bs_saga_load_json_contract("data/tech_catalog_v1.json", {})
        tier = contract.get("tier", {}) if isinstance(contract, dict) else {}
        if isinstance(tier, dict) and tier:
            return tier
        return {
            "C": [
                {"name": "Ataque básico", "desc": "Ataque base. Escala con EP: a mayor potencia, mayor gasto de EP."},
                {"name": "Defensa básica", "desc": "Defensa base. Escala con EP: más protección implica mayor gasto de EP."},
                {"name": "Ataque directo", "desc": "Si sale 3/4 en dados, el golpe se vuelve indefendible; si no, se puede bloquear."},
                {"name": "Efecto especial", "desc": "Cada héroe tiene un efecto propio, aplicado en ataque o defensa según su kit."},
                {"name": "Concentrar", "desc": "Multiplica x2 un ataque elegido. No consume acción disponible."},
                {"name": "Descansar", "desc": "Recupera un porcentaje de HP, EP y EC."},
                {"name": "Dados de furia", "desc": "Se activa con 10% de HP o menos. Multiplica x2 una técnica elegida."},
            ],
            "B": [
                {"name": "Ataque extra", "desc": "Otorga una acción ofensiva adicional en el turno."},
                {"name": "Defensa extra", "desc": "Otorga una acción defensiva adicional en el turno."},
                {"name": "Potenciar", "desc": "Multiplica x2 una defensa elegida y no consume acción disponible."},
            ],
            "A": [
                {"name": "Técnica extra", "desc": "Habilita una acción adicional de técnica en el turno."},
                {"name": "Ataque reductor", "desc": "Reduce un porcentaje de la defensa general del enemigo."},
                {"name": "Defensa reductora", "desc": "Reduce un porcentaje del ataque general del enemigo."},
            ],
            "S": [
                {"name": "Ataque negador", "desc": "Con 3/4 dados exitosos, anula el siguiente turno enemigo."},
                {"name": "Defensa reflectora", "desc": "Refleja un porcentaje del daño de ataque enemigo."},
            ],
        }

    def bs_saga_tech_catalog_by_type():
        contract = bs_saga_load_json_contract("data/tech_catalog_v1.json", {})
        by_type = contract.get("type", {}) if isinstance(contract, dict) else {}
        if isinstance(by_type, dict) and by_type:
            return by_type
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
                {"name": "Dados de furia", "desc": "Multiplica x2 una técnica de ataque o defensa sin consumir acción."},
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

# Fase 3 de split:
# - bs_saga_lobby_screen
# - bs_saga_section_shell
# - bs_saga_heroes_screen
# - bs_saga_catalog_screen
# - bs_saga_inventory_screen
# - bs_saga_profile_screen
# ahora viven en `game/ui_hub/ui_hub_screens_lobby.rpy`.

# Fase 5 de split:
# - bs_saga_preparation_room_screen
# - bs_saga_hero_config_screen
# - bs_saga_duel_staging_screen
# - bs_saga_preparation_verify_screen
# ahora viven en `game/ui_hub/ui_hub_screens_prep.rpy`.

# Fase 5 de split:
# - bs_saga_tech_catalog_screen
# - bs_saga_tower_screen
# ahora viven en `game/ui_hub/ui_hub_screens_lobby.rpy`.

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
    # Ruta legacy: se mantiene por compatibilidad, pero el flujo principal
    # de validación/inicio quedó consolidado en staging.
    $ bs_saga_prep_context = "staging"
    jump bs_saga_preparacion

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
        $ bs_saga_prep_intent_duel = False
    elif str(getattr(store, "bs_saga_prep_context", "") or "") not in ("room", "config", "staging"):
        $ bs_saga_prep_context = "room"
    if not (bs_saga_prep_duel_rotation_ids or []):
        $ bs_saga_refresh_duel_rotation_heroes(5)
    if not (bs_saga_prep_selected_party_ids or []):
        if bs_saga_prep_selected_hero:
            $ bs_saga_prep_selected_party_ids = [str(bs_saga_prep_selected_hero)]

    $ _prep_ctx = str(getattr(store, "bs_saga_prep_context", "room") or "room").strip().lower()
    if _prep_ctx == "staging":
        $ _prep_nav = renpy.call_screen("bs_saga_duel_staging_screen")
    elif _prep_ctx == "config":
        $ _prep_nav = renpy.call_screen("bs_saga_hero_config_screen")
    else:
        $ _prep_nav = renpy.call_screen("bs_saga_preparation_room_screen")

    if _prep_nav in ("to_staging", "nav:staging"):
        $ bs_saga_prep_context = "staging"
        jump bs_saga_preparacion
    if _prep_nav in ("to_config", "nav:config"):
        $ bs_saga_prep_context = "config"
        jump bs_saga_preparacion
    if _prep_nav in ("to_room", "nav:room"):
        $ bs_saga_prep_context = "room"
        jump bs_saga_preparacion
    if _prep_nav in ("to_lobby", "nav:lobby"):
        jump bs_saga_lobby
    if isinstance(_prep_nav, str) and _prep_nav.startswith("nav:"):
        jump bs_saga_preparacion
    jump bs_saga_preparacion

label bs_saga_perfil:
    $ _perfil_nav = renpy.call_screen("bs_saga_profile_screen")
    if _perfil_nav in ("to_lobby", "nav:lobby"):
        jump bs_saga_lobby
    jump bs_saga_perfil

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
