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

define PRECOMBAT_PROFILES_KEY = "precombat_profiles_v1"

init -925 python:
    import renpy.store as S
    import renpy.exports as R

    def precombat_catalog_v1():
        """Catálogo editable de Fase 1 (sin runtime profundo)."""
        return {
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

    def precombat_kind_by_id(tech_id):
        tid = str(tech_id or "")
        cat = precombat_catalog_v1()
        for item in list(cat.get("atk", [])) + list(cat.get("def", [])):
            if str(item.get("id", "")) == tid:
                return str(item.get("kind", ""))
        return ""

    def precombat_label_by_id(tech_id):
        tid = str(tech_id or "")
        cat = precombat_catalog_v1()
        for item in list(cat.get("atk", [])) + list(cat.get("def", [])):
            if str(item.get("id", "")) == tid:
                return str(item.get("name", tid))
        return tid

    def precombat_special_ids_selected():
        out = []
        loadout = getattr(S, "precombat_loadout", {}) or {}
        for category in ("atk", "def"):
            for tid in list(loadout.get(category, []) or []):
                kind = precombat_kind_by_id(tid)
                if kind.startswith("special_") and tid not in out:
                    out.append(tid)
        return out

    def precombat_spc_limit():
        slots = getattr(S, "precombat_slots", {}) or {}
        base = int(slots.get("spc", 1) or 1)
        perk = int(getattr(S, "precombat_extra_spc_slots", 0) or 0)
        return max(0, base + perk)

    def precombat_usage_snapshot():
        loadout = getattr(S, "precombat_loadout", {}) or {}
        atk_used = len(list(loadout.get("atk", []) or []))
        def_used = len(list(loadout.get("def", []) or []))
        spc_used = len(precombat_special_ids_selected())
        return {
            "atk": atk_used,
            "def": def_used,
            "spc": spc_used,
            "spc_limit": precombat_spc_limit(),
        }

    def precombat_icon_path(tech_id):
        tid = str(tech_id or "").strip().lower()
        mapping = {
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
        pth = mapping.get(tid, "")
        if pth and R.loadable(pth):
            return pth
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
        return items[start:end]

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
        precombat_set_message("Perfil pre-combate cargado [{}]".format(pid), "#66CCFF")

    def precombat_validate_feedback():
        ok, msg = precombat_validate_current()
        precombat_set_message(msg, "#66DD66" if ok else "#FF8888")
        return ok

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
        }
        precombat_set_message("Loadout confirmado: {}".format(msg), "#66DD66")
        return True


screen precombat_loadout_editor():
    tag menu

    default _slot_keys = ["atk", "def", "spc"]
    default _categories = ["atk", "def"]
    default _panel_w = min(1260, max(980, int(config.screen_width or 1280) - 40))

    key "mouseup_3" action MainMenu(confirm=False)
    key "K_ESCAPE" action MainMenu(confirm=False)

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
                textbutton _("↩ Menú principal") action MainMenu(confirm=False) xalign 1.0

            hbox:
                spacing 8
                text _("Perfil:") size 14
                for pid in ("A", "B", "C"):
                    textbutton pid action SetVariable("precombat_profile_id", pid) text_color ("#66CCFF" if pid == getattr(store, "precombat_profile_id", "A") else "#FFFFFF")
                textbutton _("Guardar") action Function(store.precombat_save_profile, getattr(store, "precombat_profile_id", "A"))
                textbutton _("Cargar") action Function(store.precombat_load_profile, getattr(store, "precombat_profile_id", "A"))

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

            frame:
                xfill True
                yminimum 84
                vbox:
                    spacing 4
                    text _("Límites de slots (modo por slots)") size 14
                    hbox:
                        spacing 8
                        for sk in _slot_keys:
                            $ lim = (store.precombat_spc_limit() if sk == "spc" else int((getattr(store, "precombat_slots", {}) or {}).get(sk, 0) or 0))
                            $ used = int((store.precombat_usage_snapshot() or {}).get(sk, 0) or 0)
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
                                $ _page_display = _page + 1
                                $ _maxp_display = _maxp + 1
                                hbox:
                                    spacing 8
                                    textbutton _("◀") action Function(store.precombat_catalog_change_page, cat, -1)
                                    text _("Página [_page_display]/[_maxp_display]") size 12 color "#BBBBBB"
                                    textbutton _("▶") action Function(store.precombat_catalog_change_page, cat, +1)
                                for item in store.precombat_catalog_page_items(cat):
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
                                text _("ATK") size 13 color "#66CCFF"
                                for tid in (getattr(store, "precombat_loadout", {}) or {}).get("atk", []):
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    hbox:
                                        spacing 4
                                        text "[tid_label]" size 13
                                        textbutton _("Quitar") action Function(store.precombat_remove, "atk", tid)
                                if len((getattr(store, "precombat_loadout", {}) or {}).get("atk", [])) == 0:
                                    text "-" size 12 color "#777777"

                                text _("DEF") size 13 color "#66CCFF"
                                for tid in (getattr(store, "precombat_loadout", {}) or {}).get("def", []):
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    hbox:
                                        spacing 4
                                        text "[tid_label]" size 13
                                        textbutton _("Quitar") action Function(store.precombat_remove, "def", tid)
                                if len((getattr(store, "precombat_loadout", {}) or {}).get("def", [])) == 0:
                                    text "-" size 12 color "#777777"

                                text _("SPC (derivado)") size 13 color "#66CCFF"
                                for tid in store.precombat_special_ids_selected():
                                    $ tid_label = store.precombat_label_by_id(tid)
                                    text "• [tid_label]" size 12
                                if len(store.precombat_special_ids_selected()) == 0:
                                    text "-" size 12 color "#777777"

            hbox:
                spacing 8
                textbutton _("Validar") action Function(store.precombat_validate_feedback)
                textbutton _("Confirmar loadout") action Function(store.precombat_confirm_selection)
                textbutton _("Volver") action Return()
                textbutton _("Menú principal") action MainMenu(confirm=False)
