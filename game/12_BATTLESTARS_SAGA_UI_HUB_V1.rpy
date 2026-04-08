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

init -880 python:
    import renpy.store as S

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

screen bs_saga_lobby_screen():
    tag menu

    add Solid("#101923")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1120
        ypadding 10
        background Solid("#1A2938")

        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Lobby táctico" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Salir al menú principal" action MainMenu()

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

            textbutton "🗼 Torre del cielo (no disponible)" action Jump("bs_saga_torre_cielo_locked")

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
            hbox:
                spacing 10
                textbutton "Preparación" action Jump("bs_saga_preparacion")
                textbutton "Héroes" action Jump("bs_saga_heroes")
                textbutton "Tienda" action Jump("bs_saga_tienda")
                textbutton "Catálogo de itens" action Jump("bs_saga_catalogo_items")

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
                                                text "• [_hn]  —  [_hf]" size 18 color "#D0E9FF"
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
                                        if _r in ("", "-") and _t in ("", "-"):
                                            text "• [_n]  |  [_m]" size 17 color "#D0E9FF"
                                        else:
                                            text "• [_n]  |  Rareza: [_r]  |  Tier: [_t]  |  [_m]" size 17 color "#D0E9FF"
                                else:
                                    text "Sin itens cargados todavía para este grupo." size 18 color "#9FB9D1"

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
    $ renpy.jump("start")

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
    centered "[Battlestars Saga] Torre del cielo\n\nNo disponible en esta fase."
    jump bs_saga_lobby

# ---------- rutas panel gestión ----------

label bs_saga_preparacion:
    call screen bs_saga_section_shell(
        title="Preparación",
        subtitle="Territorio: Preparación",
        back_action=Jump("bs_saga_lobby")
    )
    return

label bs_saga_heroes:
    call screen bs_saga_heroes_screen
    return

label bs_saga_tienda:
    call screen bs_saga_section_shell(
        title="Tienda",
        subtitle="Territorio: Tienda",
        back_action=Jump("bs_saga_lobby")
    )
    return

label bs_saga_catalogo_items:
    call screen bs_saga_catalog_screen
    return
