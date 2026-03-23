# ============================================================
# 04I_PRECOMBAT_LOADOUT_SCREENV1.rpy
# Fase 1 — Sala pre-combate (v1)
# ============================================================

# Estado UI persistente por sesión
default precombat_mode = "slots"   # slots | free
default precombat_profile_id = "A"
default precombat_extra_spc_slots = 0
default precombat_selected_category = "atk"
default precombat_message = ""
default precombat_message_color = "#AAAAAA"
default precombat_slots = {"atk": 7, "def": 5, "spc": 1}
default precombat_loadout = {"atk": [], "def": []}
default precombat_confirmed_loadout = {}
default precombat_catalog_page = {"atk": 0, "def": 0}
default precombat_catalog_per_page = 4
default precombat_use_icons = True
default precombat_unit_loadouts = {"p1": {"atk": [], "def": []}, "p2": {"atk": [], "def": []}}
default precombat_resource_perks_v2 = {
    "stamina_perk_enabled": False,
    "shadow_perk_enabled": False,
    "shadow_target_mode": "local",
    "shadow_seed_ratio": 0.15,
}
default precombat_legacy_specials_fallback_enabled = False
default precombat_spa_profile_id = "A"
default precombat_diag_enabled = False
default precombat_diag_events = {}
default precombat_diag_started_ms = 0
default precombat_diag_frame_count = 0
default precombat_diag_last_report_ms = 0
default precombat_diag_overlay = True
default precombat_show_design_perks_panel = False

define PRECOMBAT_PROFILES_KEY = "precombat_profiles_v1"

init -925 python:
    import time
    import renpy.store as S
    import renpy.exports as R

    _PRECOMBAT_CATALOG_V1 = {
        "atk": [
            {"id": "extra_attack", "name": "Ataque extra", "kind": "offensive"},
            {"id": "extra_tech", "name": "Técnica extra", "kind": "offensive"},
            {"id": "stronger_attack", "name": "Ataque más fuerte", "kind": "offensive"},
            {"id": "attack_reducer", "name": "Ataque reductor", "kind": "offensive"},
            {"id": "direct_attack", "name": "Ataque directo", "kind": "offensive"},
            {"id": "noatk_attack", "name": "Ataque negador", "kind": "offensive"},
            {"id": "focus", "name": "Concentrar", "kind": "special_offensive"},
            {"id": "ladron_ofensivo", "name": "Ladrón ofensivo", "kind": "special_offensive"},
            {"id": "ladron_defensivo", "name": "Ladrón defensivo", "kind": "special_offensive"},
            {"id": "ladron_concentrar", "name": "Ladrón de concentrar", "kind": "special_offensive"},
        ],
        "def": [
            {"id": "defense_extra", "name": "Defensa extra", "kind": "defensive"},
            {"id": "defense_reducer", "name": "Defensa reductora", "kind": "defensive"},
            {"id": "defense_reflect", "name": "Defensa reflectora", "kind": "defensive"},
            {"id": "defense_strong_block", "name": "Defensa fuerte", "kind": "defensive"},
            {"id": "defense_boost", "name": "Potenciar", "kind": "special_defensive"},
            {"id": "salvaguarda_principiante", "name": "Salvaguarda principiante", "kind": "special_defensive"},
        ],
    }
    _PRECOMBAT_TECH_INDEX = {}
    for _item in list(_PRECOMBAT_CATALOG_V1.get("atk", [])) + list(_PRECOMBAT_CATALOG_V1.get("def", [])):
        _PRECOMBAT_TECH_INDEX[str(_item.get("id", ""))] = _item
    _PRECOMBAT_ICON_MAP = {
        "extra_attack": "game/gui/tech_buttons/atk_extra.png",
        "extra_tech": "game/gui/tech_buttons/tec_extra.png",
        "attack_reducer": "game/gui/tech_buttons/atk_reductor.png",
        "direct_attack": "game/gui/tech_buttons/atk_directo.png",
        "noatk_attack": "game/gui/tech_buttons/atk_negador.png",
        "stronger_attack": "game/gui/tech_buttons/atk_mas_fuerte.png",
        "defense_extra": "game/gui/tech_buttons/def_extra.png",
        "defense_reducer": "game/gui/tech_buttons/def_reductora.png",
        "defense_reflect": "game/gui/tech_buttons/def_reflectora.png",
        "defense_strong_block": "game/gui/tech_buttons/def_fuerte.png",
        "focus": "game/gui/tech_buttons/concentrar_x2.png",
        "defense_boost": "game/gui/tech_buttons/potenciar_x2.png",
        "ladron_ofensivo": "game/gui/tech_buttons/ladron_ofensivo.png",
        "ladron_defensivo": "game/gui/tech_buttons/ladron_defensivo.png",
        "ladron_concentrar": "game/gui/tech_buttons/ladron_concentrar.png",
        "salvaguarda_principiante": "game/gui/tech_buttons/salvaguarda_principiante.png",
    }
    _PRECOMBAT_ICON_LOADABLE_CACHE = {}

    def _precombat_now_ms():
        return int(time.time() * 1000.0)

    def _precombat_diag_record(tag, elapsed_ms):
        if not bool(getattr(S, "precombat_diag_enabled", False)):
            return None
        key = str(tag or "unknown")
        events = dict(getattr(S, "precombat_diag_events", {}) or {})
        row = dict(events.get(key, {}) or {})
        calls = int(row.get("calls", 0) or 0) + 1
        total_ms = float(row.get("total_ms", 0.0) or 0.0) + float(elapsed_ms or 0.0)
        max_ms = max(float(row.get("max_ms", 0.0) or 0.0), float(elapsed_ms or 0.0))
        row["calls"] = calls
        row["total_ms"] = total_ms
        row["max_ms"] = max_ms
        events[key] = row
        S.precombat_diag_events = events
        return None

    def precombat_diag_reset():
        S.precombat_diag_events = {}
        S.precombat_diag_started_ms = _precombat_now_ms()
        S.precombat_diag_frame_count = 0
        S.precombat_diag_last_report_ms = S.precombat_diag_started_ms
        return None

    def precombat_diag_set_enabled(v):
        S.precombat_diag_enabled = bool(v)
        precombat_diag_reset()
        precombat_set_message(
            "Diagnóstico pre-combate: {}".format("ON" if bool(v) else "OFF"),
            "#FFD966" if bool(v) else "#AAAAAA"
        )
        return None

    def precombat_diag_mark_frame():
        if not bool(getattr(S, "precombat_diag_enabled", False)):
            return None
        S.precombat_diag_frame_count = int(getattr(S, "precombat_diag_frame_count", 0) or 0) + 1
        return None

    def precombat_diag_report_text(limit=4):
        started = int(getattr(S, "precombat_diag_started_ms", 0) or 0)
        now = _precombat_now_ms()
        elapsed_sec = max(0.001, float(now - started) / 1000.0)
        frames = int(getattr(S, "precombat_diag_frame_count", 0) or 0)
        fps_ui = float(frames) / elapsed_sec
        events = dict(getattr(S, "precombat_diag_events", {}) or {})
        pairs = list(events.items())
        pairs.sort(key=lambda kv: float((kv[1] or {}).get("total_ms", 0.0) or 0.0), reverse=True)
        chunks = ["FPS_UI~{:.1f}".format(fps_ui)]
        for k, v in pairs[:max(1, int(limit or 4))]:
            calls = int((v or {}).get("calls", 0) or 0)
            total_ms = float((v or {}).get("total_ms", 0.0) or 0.0)
            avg_ms = (total_ms / float(calls)) if calls > 0 else 0.0
            max_ms = float((v or {}).get("max_ms", 0.0) or 0.0)
            chunks.append("{} c:{} avg:{:.2f} max:{:.2f}".format(k, calls, avg_ms, max_ms))
        return " | ".join(chunks)

    def precombat_diag_periodic_report():
        if not bool(getattr(S, "precombat_diag_enabled", False)):
            return None
        now = _precombat_now_ms()
        last = int(getattr(S, "precombat_diag_last_report_ms", 0) or 0)
        if now - last < 1000:
            return None
        S.precombat_diag_last_report_ms = now
        print("[PRECOMBAT_DIAG] {}".format(precombat_diag_report_text()))
        return None

    def precombat_catalog_v1():
        """Catálogo editable de Fase 1 (sin runtime profundo)."""
        return _PRECOMBAT_CATALOG_V1

    def precombat_kind_by_id(tech_id):
        tid = str(tech_id or "")
        item = _PRECOMBAT_TECH_INDEX.get(tid, {})
        return str(item.get("kind", ""))

    def precombat_label_by_id(tech_id):
        tid = str(tech_id or "")
        item = _PRECOMBAT_TECH_INDEX.get(tid, {})
        return str(item.get("name", tid))

    def precombat_special_ids_selected():
        t0 = _precombat_now_ms()
        out = []
        loadout = getattr(S, "precombat_loadout", {}) or {}
        for category in ("atk", "def"):
            for tid in list(loadout.get(category, []) or []):
                kind = precombat_kind_by_id(tid)
                if kind.startswith("special_") and tid not in out:
                    out.append(tid)
        _precombat_diag_record("special_ids_selected", _precombat_now_ms() - t0)
        return out

    def _precombat_special_ids_from_loadout(loadout_dict):
        out = []
        lo = dict(loadout_dict or {})
        for category in ("atk", "def"):
            for tid in list(lo.get(category, []) or []):
                kind = precombat_kind_by_id(tid)
                if kind.startswith("special_") and tid not in out:
                    out.append(str(tid))
        return out

    def _precombat_resource_perks_from_specials(special_ids):
        sids = set([str(x or "") for x in list(special_ids or [])])
        stamina_enabled = bool(
            ("focus" in sids) or
            ("ladron_concentrar" in sids) or
            ("ladron_ofensivo" in sids)
        )
        shadow_active = bool(
            ("salvaguarda_principiante" in sids) or
            ("defense_boost" in sids)
        )
        # Fase 5: Shadow persiste por defecto; seed inicial conservador.
        shadow_seed_ratio = 0.15 if shadow_active else 0.0
        return {
            "stamina_enabled": bool(stamina_enabled),
            "shadow_active": bool(shadow_active),
            "shadow_seed_ratio": float(shadow_seed_ratio),
        }

    def _precombat_resource_perks_v2_defaults():
        return {
            "stamina_perk_enabled": False,
            "shadow_perk_enabled": False,
            "shadow_target_mode": "local",
            "shadow_seed_ratio": 0.15,
        }

    def _precombat_resource_perks_v2_norm(raw):
        base = _precombat_resource_perks_v2_defaults()
        cfg = dict(raw or {})
        out = dict(base)
        out["stamina_perk_enabled"] = bool(cfg.get("stamina_perk_enabled", base["stamina_perk_enabled"]))
        out["shadow_perk_enabled"] = bool(cfg.get("shadow_perk_enabled", base["shadow_perk_enabled"]))
        mode = str(cfg.get("shadow_target_mode", base["shadow_target_mode"]) or "local").strip().lower()
        if mode not in ("local", "applied_to_enemy"):
            mode = "local"
        out["shadow_target_mode"] = mode
        try:
            ratio = float(cfg.get("shadow_seed_ratio", base["shadow_seed_ratio"]) or base["shadow_seed_ratio"])
        except Exception:
            ratio = float(base["shadow_seed_ratio"])
        out["shadow_seed_ratio"] = max(0.0, min(1.0, ratio))
        return out

    def precombat_resource_perks_v2_get():
        cur = getattr(S, "precombat_resource_perks_v2", None)
        norm = _precombat_resource_perks_v2_norm(cur)
        S.precombat_resource_perks_v2 = dict(norm)
        return dict(norm)

    def precombat_resource_perks_v2_set(toggle_key=None, value=None):
        cur = precombat_resource_perks_v2_get()
        k = str(toggle_key or "").strip().lower()
        if k == "stamina":
            cur["stamina_perk_enabled"] = bool(value)
        elif k == "shadow":
            cur["shadow_perk_enabled"] = bool(value)
        elif k == "mode":
            mode = str(value or "local").strip().lower()
            if mode not in ("local", "applied_to_enemy"):
                mode = "local"
            cur["shadow_target_mode"] = mode
        S.precombat_resource_perks_v2 = dict(_precombat_resource_perks_v2_norm(cur))
        return None

    def precombat_resource_perks_v2_snapshot():
        # MVP: perks v2 son independientes de técnicas.
        cur = precombat_resource_perks_v2_get()
        by_side = {
            "p1": dict(cur),
            "p2": dict(cur),
        }
        return {
            "current": dict(cur),
            "by_side": dict(by_side),
        }

    def precombat_design_perks_notes_text():
        return (
            "📘 Perks de Diseño (referencia rápida)\n"
            "1) Sombra Hostil (shadow_apply)\n"
            "   • Hace: bloquea free_space rival para reducir generación de estamina.\n"
            "   • Percepción código: debuff de espacio, no daño HP directo en versión base.\n"
            "   • Uso: on_hit (MVP) o aura por turnos (avanzado).\n"
            "   • Límites: cap por hit/turno, no aplicar en KO.\n\n"
            "2) Drenaje Vital (stamina_drain_target)\n"
            "   • Hace: consume estamina rival.\n"
            "   • Percepción código: control anti-colchón de estamina.\n"
            "   • Uso: skill de 1 turno, técnica especial o efecto mantenido.\n"
            "   • Límites: cap por hit/turno, opcional costo energía/dados.\n\n"
            "3) Transfusión de Estamina (stamina_target_to_hp_self)\n"
            "   • Hace: drena estamina rival y cura HP propio.\n"
            "   • Percepción código: sustain ofensivo con cap de curación.\n"
            "   • Uso: burst por skill o drenaje sostenido en baja proporción.\n"
            "   • Límites: no overheal, cap por turno.\n\n"
            "4) Conversión Forzada (hp_to_stamina_target)\n"
            "   • Hace: convierte HP rival en estamina rival.\n"
            "   • Percepción código: manipulación económica del objetivo.\n"
            "   • Uso: efecto puntual de control en turno clave.\n"
            "   • Límites: cap de HP convertido, opcional mínimo HP=1.\n\n"
            "5) Reserva de Impacto (stamina_target_to_damage_bank)\n"
            "   • Hace: transforma estamina rival en daño diferido.\n"
            "   • Percepción código: burst retrasado / bank de daño.\n"
            "   • Uso: 1 turno o acumulación temporal limitada.\n"
            "   • Límites: cap de bank, expiración, ratio < 100% recomendado.\n\n"
            "6) Refino Espiritual (stamina_target_to_reiatsu)\n"
            "   • Hace: convierte estamina rival en reiatsu.\n"
            "   • Percepción código: conversión de economía defensiva a recurso mágico.\n"
            "   • Uso: puntual o mantenido en baja proporción.\n"
            "   • Límites: cap por turno y por recurso máximo.\n"
        )

    def precombat_resource_perks_snapshot():
        if not bool(getattr(S, "precombat_legacy_specials_fallback_enabled", True)):
            return {}
        # Global editor actual (compat 1v1)
        current_specials = precombat_special_ids_selected()
        perks_current = _precombat_resource_perks_from_specials(current_specials)

        # Por unidad (p1/p2) para 2v2
        by_side = dict(getattr(S, "precombat_unit_loadouts", {}) or {})
        perks_by_side = {}
        for side_key in ("p1", "p2"):
            raw = dict(by_side.get(side_key, {"atk": [], "def": []}) or {"atk": [], "def": []})
            sids = _precombat_special_ids_from_loadout(raw)
            perks_by_side[side_key] = _precombat_resource_perks_from_specials(sids)

        return {
            "current": dict(perks_current),
            "by_side": dict(perks_by_side),
        }

    def precombat_spc_limit():
        slots = getattr(S, "precombat_slots", {}) or {}
        base = int(slots.get("spc", 1) or 1)
        perk = int(getattr(S, "precombat_extra_spc_slots", 0) or 0)
        return max(0, base + perk)

    def precombat_usage_snapshot():
        t0 = _precombat_now_ms()
        loadout = getattr(S, "precombat_loadout", {}) or {}
        atk_used = len(list(loadout.get("atk", []) or []))
        def_used = len(list(loadout.get("def", []) or []))
        spc_used = len(precombat_special_ids_selected())
        out = {
            "atk": atk_used,
            "def": def_used,
            "spc": spc_used,
            "spc_limit": precombat_spc_limit(),
        }
        _precombat_diag_record("usage_snapshot", _precombat_now_ms() - t0)
        return out

    def precombat_icon_path(tech_id):
        t0 = _precombat_now_ms()
        tid = str(tech_id or "").strip().lower()
        pth = _PRECOMBAT_ICON_MAP.get(tid, "")
        if not pth:
            _precombat_diag_record("icon_path", _precombat_now_ms() - t0)
            return ""
        cached = _PRECOMBAT_ICON_LOADABLE_CACHE.get(pth, None)
        if cached is None:
            cached = bool(R.loadable(pth))
            _PRECOMBAT_ICON_LOADABLE_CACHE[pth] = cached
        if cached:
            _precombat_diag_record("icon_path", _precombat_now_ms() - t0)
            return pth
        _precombat_diag_record("icon_path", _precombat_now_ms() - t0)
        return ""

    def precombat_set_use_icons(v):
        S.precombat_use_icons = bool(v)
        precombat_set_message("Vista {}".format("con íconos" if bool(v) else "simple"), "#66CCFF")

    def precombat_set_category(cat):
        c = str(cat or "atk").strip().lower()
        if c not in ("atk", "def"):
            c = "atk"
        S.precombat_selected_category = c
        pages = dict(getattr(S, "precombat_catalog_page", {}) or {})
        if c not in pages:
            pages[c] = 0
        S.precombat_catalog_page = pages

    def precombat_catalog_max_page(category):
        cat = str(category or "atk").strip().lower()
        items = list(precombat_catalog_v1().get(cat, []) or [])
        per_page = max(1, int(getattr(S, "precombat_catalog_per_page", 4) or 4))
        if len(items) <= 0:
            return 0
        return max(0, (len(items) - 1) // per_page)

    def precombat_catalog_page_items(category):
        t0 = _precombat_now_ms()
        cat = str(category or "atk").strip().lower()
        items = list(precombat_catalog_v1().get(cat, []) or [])
        per_page = max(1, int(getattr(S, "precombat_catalog_per_page", 4) or 4))
        pages = dict(getattr(S, "precombat_catalog_page", {}) or {})
        page = int(pages.get(cat, 0) or 0)
        maxp = precombat_catalog_max_page(cat)
        if page < 0:
            page = 0
        if page > maxp:
            page = maxp
        pages[cat] = page
        S.precombat_catalog_page = pages
        start = page * per_page
        end = start + per_page
        out = items[start:end]
        _precombat_diag_record("catalog_page_items", _precombat_now_ms() - t0)
        return out

    def precombat_catalog_change_page(category, delta):
        cat = str(category or "atk").strip().lower()
        pages = dict(getattr(S, "precombat_catalog_page", {}) or {})
        cur = int(pages.get(cat, 0) or 0)
        nxt = cur + int(delta or 0)
        maxp = precombat_catalog_max_page(cat)
        if nxt < 0:
            nxt = 0
        if nxt > maxp:
            nxt = maxp
        pages[cat] = nxt
        S.precombat_catalog_page = pages

    def precombat_set_message(msg, color="#AAAAAA"):
        S.precombat_message = str(msg or "")
        S.precombat_message_color = str(color or "#AAAAAA")
        R.restart_interaction()

    def precombat_set_mode(mode):
        m = str(mode or "slots").strip().lower()
        if m not in ("slots", "free"):
            m = "slots"
        S.precombat_mode = m
        precombat_set_message("Modo: {}".format("Por slots" if m == "slots" else "Libre"), "#66CCFF")

    def precombat_set_extra_spc(v):
        try:
            vv = int(v)
        except:
            vv = 0
        if vv < 0:
            vv = 0
        if vv > 1:
            vv = 1
        S.precombat_extra_spc_slots = vv
        precombat_set_message("Perk especiales: +{}".format(vv), "#66CCFF")

    def precombat_adjust_slot(slot_key, delta):
        key = str(slot_key or "").strip().lower()
        if key not in ("atk", "def", "spc"):
            return None
        slots = dict(getattr(S, "precombat_slots", {}) or {})
        cur = int(slots.get(key, 0) or 0)
        nxt = max(0, cur + int(delta or 0))
        slots[key] = nxt
        S.precombat_slots = slots
        precombat_set_message("Slots {} = {}".format(key.upper(), nxt), "#66CCFF")
        return None

    def precombat_add(category, tech_id):
        cat = str(category or "").strip().lower()
        tid = str(tech_id or "").strip()
        if cat not in ("atk", "def") or not tid:
            return None

        loadout = dict(getattr(S, "precombat_loadout", {}) or {})
        arr = list(loadout.get(cat, []) or [])
        if tid in arr:
            precombat_set_message("Ya estaba equipada: {}".format(precombat_label_by_id(tid)), "#AAAAAA")
            return None

        arr.append(tid)
        loadout[cat] = arr
        S.precombat_loadout = loadout

        ok, msg = precombat_validate_current()
        if not ok and str(getattr(S, "precombat_mode", "slots")) == "slots":
            arr.pop()
            loadout[cat] = arr
            S.precombat_loadout = loadout
            precombat_set_message(msg, "#FF8888")
            return None

        precombat_set_message("Equipada: {}".format(precombat_label_by_id(tid)), "#66DD66")
        return None

    def precombat_remove(category, tech_id):
        cat = str(category or "").strip().lower()
        tid = str(tech_id or "").strip()
        if cat not in ("atk", "def") or not tid:
            return None

        loadout = dict(getattr(S, "precombat_loadout", {}) or {})
        arr = list(loadout.get(cat, []) or [])
        if tid in arr:
            arr.remove(tid)
            loadout[cat] = arr
            S.precombat_loadout = loadout
            precombat_set_message("Quitada: {}".format(precombat_label_by_id(tid)), "#CCCC66")
        return None

    def precombat_validate_current():
        mode = str(getattr(S, "precombat_mode", "slots") or "slots")
        if mode == "free":
            return True, "OK (modo libre)"

        slots = getattr(S, "precombat_slots", {}) or {}
        snap = precombat_usage_snapshot()

        atk_max = int(slots.get("atk", 0) or 0)
        def_max = int(slots.get("def", 0) or 0)
        spc_max = int(snap.get("spc_limit", 0) or 0)

        if snap["atk"] > atk_max:
            return False, "Excede slots ATK ({} / {})".format(snap["atk"], atk_max)
        if snap["def"] > def_max:
            return False, "Excede slots DEF ({} / {})".format(snap["def"], def_max)
        if snap["spc"] > spc_max:
            return False, "Excede slots SPC ({} / {})".format(snap["spc"], spc_max)

        return True, "Loadout válido"

    def precombat_get_profiles_store():
        p = getattr(S, "persistent", None)
        if p is None:
            return {}
        data = getattr(p, PRECOMBAT_PROFILES_KEY, None)
        if not isinstance(data, dict):
            data = {}
            setattr(p, PRECOMBAT_PROFILES_KEY, data)
        return data

    def precombat_save_profile(profile_id=None):
        pid = str(profile_id or getattr(S, "precombat_profile_id", "A") or "A")
        data = precombat_get_profiles_store()
        data[pid] = {
            "mode": str(getattr(S, "precombat_mode", "slots") or "slots"),
            "extra_spc": int(getattr(S, "precombat_extra_spc_slots", 0) or 0),
            "slots": dict(getattr(S, "precombat_slots", {}) or {}),
            "loadout": dict(getattr(S, "precombat_loadout", {}) or {}),
            "by_side": dict(getattr(S, "precombat_unit_loadouts", {}) or {}),
        }
        S.persistent.precombat_profiles_v1 = data
        R.save_persistent()
        precombat_set_message("Perfil pre-combate guardado [{}]".format(pid), "#66DD66")

    def precombat_load_profile(profile_id=None):
        pid = str(profile_id or getattr(S, "precombat_profile_id", "A") or "A")
        data = precombat_get_profiles_store()
        cfg = data.get(pid, None)
        if not isinstance(cfg, dict):
            precombat_set_message("No existe perfil [{}]".format(pid), "#FF8888")
            return None

        S.precombat_mode = str(cfg.get("mode", "slots") or "slots")
        S.precombat_extra_spc_slots = int(cfg.get("extra_spc", 0) or 0)
        S.precombat_slots = dict(cfg.get("slots", {"atk": 7, "def": 5, "spc": 1}) or {"atk": 7, "def": 5, "spc": 1})
        lo = dict(cfg.get("loadout", {"atk": [], "def": []}) or {"atk": [], "def": []})
        lo.setdefault("atk", [])
        lo.setdefault("def", [])
        S.precombat_loadout = lo
        by_side = dict(cfg.get("by_side", {"p1": {"atk": [], "def": []}, "p2": {"atk": [], "def": []}}) or {})
        by_side.setdefault("p1", {"atk": [], "def": []})
        by_side.setdefault("p2", {"atk": [], "def": []})
        S.precombat_unit_loadouts = by_side
        precombat_set_message("Perfil pre-combate cargado [{}]".format(pid), "#66CCFF")

    def precombat_validate_feedback():
        ok, msg = precombat_validate_current()
        precombat_set_message(msg, "#66DD66" if ok else "#FF8888")
        return ok

    def _precombat_clean_loadout(raw):
        data = dict(raw or {})
        atk = list(data.get("atk", []) or [])
        deff = list(data.get("def", []) or [])
        return {"atk": [str(x) for x in atk], "def": [str(x) for x in deff]}

    def precombat_store_current_for_side(side_key):
        sk = str(side_key or "").strip().lower()
        if sk not in ("p1", "p2"):
            sk = "p1"
        by_side = dict(getattr(S, "precombat_unit_loadouts", {}) or {})
        by_side.setdefault("p1", {"atk": [], "def": []})
        by_side.setdefault("p2", {"atk": [], "def": []})
        by_side[sk] = _precombat_clean_loadout(getattr(S, "precombat_loadout", {}) or {})
        S.precombat_unit_loadouts = by_side
        precombat_set_message("Configuración actual guardada en {}.".format(sk.upper()), "#66DD66")
        return None

    def precombat_apply_side_to_current(side_key):
        sk = str(side_key or "").strip().lower()
        if sk not in ("p1", "p2"):
            sk = "p1"
        by_side = dict(getattr(S, "precombat_unit_loadouts", {}) or {})
        cfg = _precombat_clean_loadout(by_side.get(sk, {"atk": [], "def": []}))
        S.precombat_loadout = cfg
        precombat_set_message("Configuración {} cargada al editor.".format(sk.upper()), "#66CCFF")
        return None

    def precombat_copy_side_to_side(src_key, dst_key):
        src = str(src_key or "").strip().lower()
        dst = str(dst_key or "").strip().lower()
        if src not in ("p1", "p2") or dst not in ("p1", "p2"):
            precombat_set_message("Copia inválida: lado no reconocido.", "#FF8888")
            return None
        by_side = dict(getattr(S, "precombat_unit_loadouts", {}) or {})
        by_side.setdefault("p1", {"atk": [], "def": []})
        by_side.setdefault("p2", {"atk": [], "def": []})
        by_side[dst] = _precombat_clean_loadout(by_side.get(src, {"atk": [], "def": []}))
        S.precombat_unit_loadouts = by_side
        precombat_set_message("Configuración copiada {} -> {}.".format(src.upper(), dst.upper()), "#66DD66")
        return None

    def precombat_load_spa_profile(profile_id=None):
        pid = str(profile_id or getattr(S, "precombat_spa_profile_id", "A") or "A").strip().upper()
        if pid not in ("A", "B", "C"):
            pid = "A"
        S.precombat_spa_profile_id = pid
        fn_load = getattr(S, "spa_load_profile", None)
        if not callable(fn_load):
            precombat_set_message("Editor de puntos no disponible en esta sesión.", "#FF8888")
            return False
        ok = bool(fn_load(pid))
        if ok:
            precombat_set_message("Perfil de puntos [{}] cargado desde editor A/B/C.".format(pid), "#66DD66")
            return True
        precombat_set_message("No existe perfil de puntos [{}] guardado.".format(pid), "#FF8888")
        return False

    def precombat_confirm_selection():
        ok, msg = precombat_validate_current()
        if not ok:
            precombat_set_message(msg, "#FF8888")
            return False

        S.precombat_confirmed_loadout = {
            "mode": str(getattr(S, "precombat_mode", "slots") or "slots"),
            "extra_spc": int(getattr(S, "precombat_extra_spc_slots", 0) or 0),
            "slots": dict(getattr(S, "precombat_slots", {}) or {}),
            "loadout": dict(getattr(S, "precombat_loadout", {}) or {}),
            "specials": list(precombat_special_ids_selected()),
            "by_side": dict(getattr(S, "precombat_unit_loadouts", {}) or {}),
            "resource_perks_v2": dict(precombat_resource_perks_v2_snapshot() or {}),
            "resource_perks": dict(precombat_resource_perks_snapshot() or {}),
        }
        precombat_set_message("Loadout confirmado: {}".format(msg), "#66DD66")
        return True


screen precombat_loadout_editor():
    tag menu
    $ store.precombat_diag_mark_frame()
    timer 1.0 action Function(store.precombat_diag_periodic_report) repeat True

    default _slot_keys = ["atk", "def", "spc"]
    default _categories = ["atk", "def"]
    default _panel_w = min(1260, max(980, int(config.screen_width or 1280) - 40))

    key "mouseup_3" action ShowMenu("main_menu")
    key "K_ESCAPE" action ShowMenu("main_menu")
    key "game_menu" action ShowMenu("main_menu")

    frame:
        style_prefix "game_menu"
        xalign 0.53
        yalign 0.5
        xsize _panel_w
        ysize 740
        xpadding 18
        ypadding 12

        vbox:
            spacing 8
            text _("Pre-combate (Fase 1/2)") size 56 color "#00BFFF"
            text _("Configura loadout por slots con modo libre/por slots y persistencia de perfil.") size 14 color "#BBBBBB"
            text "[store.precombat_message]" size 12 color getattr(store, "precombat_message_color", "#AAAAAA")

            hbox:
                xfill True
                textbutton _("↩ Menú principal") action ShowMenu("main_menu") xalign 1.0

            hbox:
                spacing 8
                text _("Perfil:") size 14
                for pid in ("A", "B", "C"):
                    textbutton pid action SetVariable("precombat_profile_id", pid) text_color ("#66CCFF" if pid == getattr(store, "precombat_profile_id", "A") else "#FFFFFF")
                textbutton _("Guardar") action Function(store.precombat_save_profile, getattr(store, "precombat_profile_id", "A"))
                textbutton _("Cargar") action Function(store.precombat_load_profile, getattr(store, "precombat_profile_id", "A"))

            hbox:
                spacing 8
                text _("Puntos A/B/C:") size 14
                for pid in ("A", "B", "C"):
                    textbutton pid action SetVariable("precombat_spa_profile_id", pid) text_color ("#66CCFF" if pid == getattr(store, "precombat_spa_profile_id", "A") else "#FFFFFF")
                textbutton _("Cargar editor puntos") action Function(store.precombat_load_spa_profile, getattr(store, "precombat_spa_profile_id", "A"))

            hbox:
                spacing 10
                text _("Modo:") size 14
                textbutton _("Por slots") action Function(store.precombat_set_mode, "slots") text_color ("#66CCFF" if getattr(store, "precombat_mode", "slots") == "slots" else "#FFFFFF")
                textbutton _("Libre") action Function(store.precombat_set_mode, "free") text_color ("#66CCFF" if getattr(store, "precombat_mode", "slots") == "free" else "#FFFFFF")
                null width 10
                text _("Perk extra SPC:") size 14
                textbutton _("0") action Function(store.precombat_set_extra_spc, 0) text_color ("#66CCFF" if int(getattr(store, "precombat_extra_spc_slots", 0) or 0) == 0 else "#FFFFFF")
                textbutton _("+1") action Function(store.precombat_set_extra_spc, 1) text_color ("#66CCFF" if int(getattr(store, "precombat_extra_spc_slots", 0) or 0) == 1 else "#FFFFFF")
                null width 10
                text _("Vista:") size 14
                textbutton _("Íconos") action Function(store.precombat_set_use_icons, True) text_color ("#66CCFF" if bool(getattr(store, "precombat_use_icons", True)) else "#FFFFFF")
                textbutton _("Simple") action Function(store.precombat_set_use_icons, False) text_color ("#66CCFF" if not bool(getattr(store, "precombat_use_icons", True)) else "#FFFFFF")
                null width 10
                text _("Diag:") size 14
                textbutton _("ON") action Function(store.precombat_diag_set_enabled, True) text_color ("#FFD966" if bool(getattr(store, "precombat_diag_enabled", False)) else "#FFFFFF")
                textbutton _("OFF") action Function(store.precombat_diag_set_enabled, False) text_color ("#FFD966" if not bool(getattr(store, "precombat_diag_enabled", False)) else "#FFFFFF")
                textbutton _("Reset") action Function(store.precombat_diag_reset)
                textbutton _("Overlay") action ToggleVariable("precombat_diag_overlay")
                null width 10
                text _("Diseño perks:") size 14
                textbutton _("Mostrar") action SetVariable("precombat_show_design_perks_panel", True) text_color ("#9FE2FF" if bool(getattr(store, "precombat_show_design_perks_panel", False)) else "#FFFFFF")
                textbutton _("Ocultar") action SetVariable("precombat_show_design_perks_panel", False) text_color ("#9FE2FF" if not bool(getattr(store, "precombat_show_design_perks_panel", False)) else "#FFFFFF")

            if bool(getattr(store, "precombat_show_design_perks_panel", False)):
                frame:
                    xfill True
                    ymaximum 210
                    xpadding 8
                    ypadding 6
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 196
                        text "[store.precombat_design_perks_notes_text()]" size 11 color "#C7E9FF"

            if bool(getattr(store, "precombat_diag_enabled", False)) and bool(getattr(store, "precombat_diag_overlay", True)):
                frame:
                    xfill True
                    yminimum 42
                    xpadding 8
                    ypadding 6
                    $ _diag_text = store.precombat_diag_report_text()
                    text "[_diag_text]" size 11 color "#FFD966"

            frame:
                xfill True
                yminimum 84
                $ _slots_cfg = getattr(store, "precombat_slots", {}) or {}
                $ _usage_snapshot = store.precombat_usage_snapshot() or {}
                vbox:
                    spacing 4
                    text _("Límites de slots (modo por slots)") size 14
                    hbox:
                        spacing 8
                        for sk in _slot_keys:
                            $ lim = (store.precombat_spc_limit() if sk == "spc" else int(_slots_cfg.get(sk, 0) or 0))
                            $ used = int(_usage_snapshot.get(sk, 0) or 0)
                            $ sk_u = str(sk or "").upper()
                            frame:
                                xpadding 6
                                ypadding 4
                                vbox:
                                    text "[sk_u] [used]/[lim]" size 12
                                    if sk in ("atk", "def", "spc"):
                                        hbox:
                                            spacing 2
                                            textbutton "-" action Function(store.precombat_adjust_slot, sk, -1)
                                            textbutton "+" action Function(store.precombat_adjust_slot, sk, +1)

            hbox:
                spacing 8
                for c in _categories:
                    textbutton c.upper() action Function(store.precombat_set_category, c) text_color ("#66CCFF" if c == getattr(store, "precombat_selected_category", "atk") else "#FFFFFF")

            hbox:
                spacing 8
                text _("Config técnicas P1/P2:") size 14
                textbutton _("Guardar -> P1") action Function(store.precombat_store_current_for_side, "p1")
                textbutton _("Guardar -> P2") action Function(store.precombat_store_current_for_side, "p2")
                textbutton _("Cargar P1") action Function(store.precombat_apply_side_to_current, "p1")
                textbutton _("Cargar P2") action Function(store.precombat_apply_side_to_current, "p2")
                textbutton _("Copiar P1 -> P2") action Function(store.precombat_copy_side_to_side, "p1", "p2")
                textbutton _("Copiar P2 -> P1") action Function(store.precombat_copy_side_to_side, "p2", "p1")

            frame:
                xfill True
                yminimum 72
                xpadding 8
                ypadding 6
                $ _rp2 = store.precombat_resource_perks_v2_get()
                vbox:
                    spacing 4
                    text _("Perks de Recursos (v2)") size 14 color "#9FE2FF"
                    hbox:
                        spacing 8
                        text _("Perk Estamina:") size 12
                        textbutton _("ON") action Function(store.precombat_resource_perks_v2_set, "stamina", True) text_color ("#66CCFF" if bool(_rp2.get("stamina_perk_enabled", False)) else "#FFFFFF")
                        textbutton _("OFF") action Function(store.precombat_resource_perks_v2_set, "stamina", False) text_color ("#66CCFF" if not bool(_rp2.get("stamina_perk_enabled", False)) else "#FFFFFF")
                        null width 10
                        text _("Perk Shadow:") size 12
                        textbutton _("ON") action Function(store.precombat_resource_perks_v2_set, "shadow", True) text_color ("#66CCFF" if bool(_rp2.get("shadow_perk_enabled", False)) else "#FFFFFF")
                        textbutton _("OFF") action Function(store.precombat_resource_perks_v2_set, "shadow", False) text_color ("#66CCFF" if not bool(_rp2.get("shadow_perk_enabled", False)) else "#FFFFFF")
                    hbox:
                        spacing 8
                        text _("Shadow target mode:") size 12
                        textbutton _("local") action Function(store.precombat_resource_perks_v2_set, "mode", "local") text_color ("#66CCFF" if str(_rp2.get("shadow_target_mode", "local")) == "local" else "#FFFFFF")
                        textbutton _("applied_to_enemy") action Function(store.precombat_resource_perks_v2_set, "mode", "applied_to_enemy") text_color ("#66CCFF" if str(_rp2.get("shadow_target_mode", "local")) == "applied_to_enemy" else "#FFFFFF")

            hbox:
                spacing 10

                frame:
                    xfill True
                    yfill True
                    xmaximum 620
                    vbox:
                        spacing 4
                        text _("Catálogo disponible") size 14
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 420
                            vbox:
                                spacing 3
                                $ cat = getattr(store, "precombat_selected_category", "atk")
                                $ _page = int((getattr(store, "precombat_catalog_page", {}) or {}).get(cat, 0) or 0)
                                $ _maxp = int(store.precombat_catalog_max_page(cat) or 0)
                                $ _cat_page_items = store.precombat_catalog_page_items(cat)
                                $ _page_display = _page + 1
                                $ _maxp_display = _maxp + 1
                                hbox:
                                    spacing 8
                                    textbutton _("◀") action Function(store.precombat_catalog_change_page, cat, -1)
                                    text _("Página [_page_display]/[_maxp_display]") size 12 color "#BBBBBB"
                                    textbutton _("▶") action Function(store.precombat_catalog_change_page, cat, +1)
                                for item in _cat_page_items:
                                    $ tid = item.get("id", "")
                                    $ nm = item.get("name", tid)
                                    $ kind = item.get("kind", "")
                                    $ icon = store.precombat_icon_path(tid)
                                    hbox:
                                        spacing 4
                                        if bool(getattr(store, "precombat_use_icons", True)) and icon:
                                            add icon zoom 0.80
                                        text "[nm]" size 13
                                        text "([kind])" size 11 color "#999999"
                                        textbutton _("Equipar") action Function(store.precombat_add, cat, tid)

                frame:
                    xfill True
                    yfill True
                    vbox:
                        spacing 4
                        text _("Loadout actual") size 14
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 420
                            vbox:
                                spacing 3
                                $ _loadout = (getattr(store, "precombat_loadout", {}) or {})
                                $ _loadout_atk = _loadout.get("atk", [])
                                $ _loadout_def = _loadout.get("def", [])
                                $ _special_ids = store.precombat_special_ids_selected()
                                text _("ATK") size 13 color "#66CCFF"
                                for tid in _loadout_atk:
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    hbox:
                                        spacing 4
                                        text "[tid_label]" size 13
                                        textbutton _("Quitar") action Function(store.precombat_remove, "atk", tid)
                                if len(_loadout_atk) == 0:
                                    text "-" size 12 color "#777777"

                                text _("DEF") size 13 color "#66CCFF"
                                for tid in _loadout_def:
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    hbox:
                                        spacing 4
                                        text "[tid_label]" size 13
                                        textbutton _("Quitar") action Function(store.precombat_remove, "def", tid)
                                if len(_loadout_def) == 0:
                                    text "-" size 12 color "#777777"

                                text _("SPC (derivado)") size 13 color "#66CCFF"
                                for tid in _special_ids:
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    text "• [tid_label]" size 12
                                if len(_special_ids) == 0:
                                    text "-" size 12 color "#777777"

            hbox:
                spacing 8
                textbutton _("Validar") action Function(store.precombat_validate_feedback)
                textbutton _("Confirmar loadout") action Function(store.precombat_confirm_selection)
                textbutton _("Volver") action Return()
                textbutton _("Menú principal") action ShowMenu("main_menu")

            hbox:
                spacing 8
                textbutton _("Prueba 1v1 aleatoria (panel simple)") action [
                    Function(store.precombat_confirm_selection),
                    Function(store.bs_prepare_quick_random_1v1, getattr(store, "precombat_spa_profile_id", "A")),
                    Start()
                ]
                textbutton _("Prueba 2v2 aleatoria (panel simple)") action [
                    Function(store.precombat_confirm_selection),
                    Function(store.bs_prepare_quick_random_2v2, getattr(store, "precombat_spa_profile_id", "A")),
                    Start()
                ]
