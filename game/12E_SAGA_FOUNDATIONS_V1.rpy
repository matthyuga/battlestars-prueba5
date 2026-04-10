# ===============================================================
# 12E_SAGA_FOUNDATIONS_V1.rpy
# Fase 1 — Fundaciones (rápida)
# - Canon de tipos para Battlestars Saga
# - Esquema mínimo de inventario de cuenta y héroe
# ===============================================================

default bs_account_inventory_v1 = {
    # Oro global de cuenta (única fuente de verdad económica).
    "oro": 0,
    # Baúl general: ítems no asignados a héroe.
    "chest": {
        "consumables": {},   # item_id -> qty
        "equipables": {},    # item_id -> qty
        "materials": {},     # item_id -> qty
    },
}

# hero_id -> {"consumables": {...}, "equipables": {...}}
default bs_hero_inventories_v1 = {}


init -850 python:
    import copy
    import renpy.store as S

    # Canon Battlestars Saga v1.
    BS_SAGA_CANON_ACTOR_TYPES_V1 = ("PLAYER", "BETA", "GAMMA")

    def bs_saga_actor_type_or_default(actor_type, default="BETA"):
        at = str(actor_type or "").upper().strip()
        if at in BS_SAGA_CANON_ACTOR_TYPES_V1:
            return at
        dd = str(default or "BETA").upper().strip()
        return dd if dd in BS_SAGA_CANON_ACTOR_TYPES_V1 else "BETA"

    def bs_get_account_inventory_v1():
        inv = getattr(S, "bs_account_inventory_v1", None)
        if not isinstance(inv, dict):
            inv = {
                "oro": 0,
                "chest": {
                    "consumables": {},
                    "equipables": {},
                    "materials": {},
                },
            }
            S.bs_account_inventory_v1 = inv

        inv.setdefault("oro", 0)
        chest = inv.get("chest", {}) if isinstance(inv.get("chest", {}), dict) else {}
        chest.setdefault("consumables", {})
        chest.setdefault("equipables", {})
        chest.setdefault("materials", {})
        inv["chest"] = chest
        return inv

    def bs_get_hero_inventory_v1(hero_id):
        hid = str(hero_id or "").strip()
        all_inv = getattr(S, "bs_hero_inventories_v1", None)
        if not isinstance(all_inv, dict):
            all_inv = {}
            S.bs_hero_inventories_v1 = all_inv

        if hid == "":
            return {"consumables": {}, "equipables": {}}

        row = all_inv.get(hid, {}) if isinstance(all_inv.get(hid, {}), dict) else {}
        row.setdefault("consumables", {})
        row.setdefault("equipables", {})
        # Regla Saga v1: el héroe no almacena oro.
        row.pop("oro", None)
        all_inv[hid] = row
        return row

    def bs_set_hero_inventory_v1(hero_id, payload):
        hid = str(hero_id or "").strip()
        if hid == "":
            return False

        data = copy.deepcopy(payload if isinstance(payload, dict) else {})
        data.setdefault("consumables", {})
        data.setdefault("equipables", {})
        data.pop("oro", None)

        all_inv = getattr(S, "bs_hero_inventories_v1", None)
        if not isinstance(all_inv, dict):
            all_inv = {}
        all_inv[hid] = data
        S.bs_hero_inventories_v1 = all_inv
        return True

    def _bs_inv_item_bucket_or_none(bucket):
        b = str(bucket or "").strip().lower()
        return b if b in ("consumables", "equipables") else None

    def _bs_inv_norm_item_id(item_id):
        return str(item_id or "").strip()

    def _bs_inv_norm_qty(qty, default=0):
        try:
            return int(qty)
        except Exception:
            return int(default or 0)

    def bs_account_add_item_v1(bucket, item_id, qty=1):
        """
        Añade ítems al baúl de cuenta.
        bucket: consumables | equipables | materials
        """
        b = str(bucket or "").strip().lower()
        if b not in ("consumables", "equipables", "materials"):
            return {"ok": False, "error": "invalid_bucket"}

        iid = _bs_inv_norm_item_id(item_id)
        q = _bs_inv_norm_qty(qty, 0)
        if iid == "" or q <= 0:
            return {"ok": False, "error": "invalid_item_or_qty"}

        inv = bs_get_account_inventory_v1()
        chest = inv.get("chest", {})
        rows = chest.get(b, {}) if isinstance(chest.get(b, {}), dict) else {}
        rows[iid] = max(0, _bs_inv_norm_qty(rows.get(iid, 0), 0) + q)
        chest[b] = rows
        inv["chest"] = chest
        S.bs_account_inventory_v1 = inv
        return {"ok": True, "bucket": b, "item_id": iid, "qty_after": rows[iid]}

    def bs_transfer_chest_to_hero_v1(hero_id, bucket, item_id, qty=1):
        """
        Transfiere ítems desde baúl de cuenta -> inventario del héroe.
        Solo buckets: consumables/equipables.
        No mueve oro (regla Saga v1).
        """
        hid = str(hero_id or "").strip()
        b = _bs_inv_item_bucket_or_none(bucket)
        iid = _bs_inv_norm_item_id(item_id)
        q = _bs_inv_norm_qty(qty, 0)

        if hid == "":
            return {"ok": False, "error": "invalid_hero_id"}
        if b is None:
            return {"ok": False, "error": "invalid_bucket"}
        if iid == "" or q <= 0:
            return {"ok": False, "error": "invalid_item_or_qty"}

        inv = bs_get_account_inventory_v1()
        chest = inv.get("chest", {})
        src = chest.get(b, {}) if isinstance(chest.get(b, {}), dict) else {}
        src_qty = _bs_inv_norm_qty(src.get(iid, 0), 0)
        if src_qty < q:
            return {"ok": False, "error": "insufficient_qty", "available": src_qty}

        hero_inv = bs_get_hero_inventory_v1(hid)
        dst = hero_inv.get(b, {}) if isinstance(hero_inv.get(b, {}), dict) else {}
        dst[iid] = max(0, _bs_inv_norm_qty(dst.get(iid, 0), 0) + q)
        hero_inv[b] = dst
        hero_inv.pop("oro", None)

        left = src_qty - q
        if left > 0:
            src[iid] = left
        else:
            src.pop(iid, None)

        chest[b] = src
        inv["chest"] = chest
        S.bs_account_inventory_v1 = inv
        bs_set_hero_inventory_v1(hid, hero_inv)

        return {
            "ok": True,
            "hero_id": hid,
            "bucket": b,
            "item_id": iid,
            "moved_qty": q,
            "chest_qty_after": left,
            "hero_qty_after": dst[iid],
        }

    # Exponer helpers en store para uso desde otros módulos.
    S.BS_SAGA_CANON_ACTOR_TYPES_V1 = BS_SAGA_CANON_ACTOR_TYPES_V1
    S.bs_saga_actor_type_or_default = bs_saga_actor_type_or_default
    S.bs_get_account_inventory_v1 = bs_get_account_inventory_v1
    S.bs_get_hero_inventory_v1 = bs_get_hero_inventory_v1
    S.bs_set_hero_inventory_v1 = bs_set_hero_inventory_v1
    S.bs_account_add_item_v1 = bs_account_add_item_v1
    S.bs_transfer_chest_to_hero_v1 = bs_transfer_chest_to_hero_v1
