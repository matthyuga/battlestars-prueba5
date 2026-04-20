# ui_hub_roster_service.rpy
# Fase 2 de split: ownership, rotación, resolver roster.

init -880 python:
    import renpy.store as S

    def bs_saga_hero_is_owned(hero_id):
        item = bs_saga_owned_hero_entry(hero_id)
        return bool(isinstance(item, dict) and item.get("owned", False))

    def bs_saga_owned_hero_entry(hero_id):
        owned = getattr(S, "bs_saga_heroes_owned", {})
        if not isinstance(owned, dict):
            return {}
        target = str(hero_id or "").strip()
        if not target:
            return {}

        # Ruta rápida: key exacta.
        item = owned.get(target, None)
        if isinstance(item, dict):
            return item

        # Compatibilidad: comparar de forma case-insensitive tanto por key
        # como por hero_id persistido dentro de cada fila.
        target_lc = target.lower()
        for k, row in owned.items():
            if not isinstance(row, dict):
                continue
            key_lc = str(k or "").strip().lower()
            row_hid_lc = str(row.get("hero_id", "") or "").strip().lower()
            if key_lc == target_lc or row_hid_lc == target_lc:
                return row
        return {}

    def bs_saga_available_hero_rows():
        rot = getattr(S, "bs_saga_rotation_hero_ids", [])
        if not isinstance(rot, list):
            rot = []
        if len(rot) < 5:
            bs_saga_refresh_rotation_heroes(5)
            rot = getattr(S, "bs_saga_rotation_hero_ids", [])
        fn_rot_ok = getattr(S, "bs_saga_rotation_allows_hero_id", None)
        rows = []
        for r in bs_saga_db_rows():
            if not isinstance(r, dict):
                continue
            hid = bs_saga_hero_id(r)
            name = str(r.get("name", hid) or hid)
            tier = str(r.get("tier", "C") or "C").upper()
            is_owned = bs_saga_hero_is_owned(hid)
            in_rotation = hid.lower() in [str(x).lower() for x in (rot or [])]
            if not is_owned and callable(fn_rot_ok):
                in_rotation = bool(in_rotation and fn_rot_ok(hid, include_owned=True))
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

    def bs_saga_resolve_roster_v1(include_hollow=True, include_owned=True):
        """
        Fuente única de roster para Lobby/Preparación/Runtime.
        Prioriza catálogo externo, luego overlays en store y finalmente DB local.
        """
        rows = []
        out = []

        fn_cat = getattr(S, "bs_get_hero_catalog_v1", None)
        if callable(fn_cat):
            try:
                rows = list(fn_cat() or [])
            except:
                rows = []
        if not rows:
            rows = list(getattr(S, "bs_hero_catalog_v1", []) or [])
        if not rows:
            rows = list(getattr(S, "CHARACTER_DB", []) or [])

        for row in rows:
            if not isinstance(row, dict):
                continue
            raw = row.get("hero_id", None) or row.get("id", None) or row.get("name", None)
            hid = str(raw or "").strip()
            if hid:
                out.append(hid)

        # Completar con DB local de Saga para cubrir entradas no publicadas arriba.
        for row in bs_saga_db_rows():
            if not isinstance(row, dict):
                continue
            hid = str(bs_saga_hero_id(row) or "").strip()
            if hid:
                out.append(hid)

        if include_owned:
            owned = getattr(S, "bs_saga_heroes_owned", {}) or {}
            if isinstance(owned, dict):
                for hid, info in owned.items():
                    if not isinstance(info, dict):
                        continue
                    if not bool(info.get("owned", False)):
                        continue
                    h = str(info.get("hero_id", hid) or hid).strip()
                    if h:
                        out.append(h)

        unique = []
        seen = {}
        for hid in out:
            k = str(hid or "").strip().lower()
            if not k or seen.get(k):
                continue
            seen[k] = True
            if (not include_hollow) and k == "hollow":
                continue
            unique.append(str(hid).strip())
        return unique

    def bs_saga_combat_ready_ids():
        return bs_saga_resolve_roster_v1(include_hollow=True, include_owned=True)

    def bs_saga_duel_combat_pool_rows():
        ready = [str(x) for x in (bs_saga_combat_ready_ids() or [])]
        rot = getattr(S, "bs_saga_prep_duel_rotation_ids", None)
        if not isinstance(rot, list) or not rot:
            rot = bs_saga_refresh_duel_rotation_heroes(min(5, len(ready)))
        rot_lc = {str(x).lower() for x in (rot or [])}
        fn_rot_ok = getattr(S, "bs_saga_rotation_allows_hero_id", None)

        out = []
        for cid in ready:
            is_owned = bs_saga_hero_is_owned(cid)
            in_rotation = cid.lower() in rot_lc
            if not is_owned and callable(fn_rot_ok):
                in_rotation = bool(in_rotation and fn_rot_ok(cid, include_owned=True))
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
        fn_rot_ok = getattr(S, "bs_saga_rotation_allows_hero_id", None)
        unique = []
        for hid in pool:
            if callable(fn_rot_ok) and (not bs_saga_hero_is_owned(hid)):
                if not bool(fn_rot_ok(hid, include_owned=True)):
                    continue
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

    def bs_saga_ui_hub_roster_split_status_v1():
        return {
            "module": "ui_hub_roster_service",
            "status": "phase_2_done",
            "migrated_symbols": [
                "bs_saga_hero_is_owned",
                "bs_saga_owned_hero_entry",
                "bs_saga_available_hero_rows",
                "bs_saga_resolve_roster_v1",
                "bs_saga_combat_ready_ids",
                "bs_saga_duel_combat_pool_rows",
                "bs_saga_refresh_duel_rotation_heroes"
            ]
        }
