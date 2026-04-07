# ============================================================
# 12_BATTLESTARS_SAGA_UI_HUB_V1.rpy
# Lobby in-game Battlestars Saga (Wireframe funcional v1)
# ============================================================

default bs_saga_main_menu_enabled = True

default bs_saga_tournament_panel_open = False

default bs_saga_lobby_bottom_tab = "none"

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
    scene black
    centered "[Battlestars Saga] Preparación\n\nAquí irá la asignación de pool, perks e itens."
    jump bs_saga_lobby

label bs_saga_heroes:
    scene black
    centered "[Battlestars Saga] Héroes\n\nAquí irá el roster, ascensión y gestión individual."
    jump bs_saga_lobby

label bs_saga_tienda:
    scene black
    centered "[Battlestars Saga] Tienda\n\nAquí irá la compra de materiales/canjes."
    jump bs_saga_lobby

label bs_saga_catalogo_items:
    scene black
    centered "[Battlestars Saga] Catálogo de itens\n\nAquí irá la enciclopedia de materiales e itens."
    jump bs_saga_lobby
