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

    # Exponer helpers en store para uso desde otros módulos.
    S.BS_SAGA_CANON_ACTOR_TYPES_V1 = BS_SAGA_CANON_ACTOR_TYPES_V1
    S.bs_saga_actor_type_or_default = bs_saga_actor_type_or_default
    S.bs_get_account_inventory_v1 = bs_get_account_inventory_v1
    S.bs_get_hero_inventory_v1 = bs_get_hero_inventory_v1
    S.bs_set_hero_inventory_v1 = bs_set_hero_inventory_v1
