# ============================================================
# 12_BATTLESTARS_SAGA_UI_HUB_V1.rpy
# Lobby in-game Battlestars Saga (Wireframe funcional v1)
# ============================================================

default bs_saga_main_menu_enabled = True

default bs_saga_tournament_panel_open = False

default bs_saga_lobby_bottom_tab = "none"
default bs_saga_heroes_tier = "C"
default bs_saga_heroes_franchise = "all"

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
    call screen bs_saga_section_shell(
        title="Catálogo de itens",
        subtitle="Territorio: Catálogo",
        back_action=Jump("bs_saga_lobby")
    )
    return
