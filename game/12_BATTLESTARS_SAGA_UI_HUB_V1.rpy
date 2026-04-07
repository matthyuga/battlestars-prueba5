# ============================================================
# 12_BATTLESTARS_SAGA_UI_HUB_V1.rpy
# Hub principal Battlestars Saga (provisional)
# ============================================================

default bs_saga_main_menu_enabled = True

screen bs_saga_hub_screen():
    tag menu

    add Solid("#101923")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1140
        ypadding 12
        background Solid("#1C2B3A")

        hbox:
            spacing 20
            text "Battlestars Saga" size 42 color "#5FC6FF"
            text "Hub táctico" size 24 color "#C7E8FF" yalign 0.7

    frame:
        xalign 0.5
        yalign 0.53
        xsize 1140
        ysize 520
        padding (20, 20)
        background Solid("#132131")

        vbox:
            spacing 12
            text "Rutas principales" size 26 color "#E6F4FF"

            style_prefix "bs_saga_hub"

            grid 2 5:
                spacing 12

                textbutton "⚔ Duelo libre" action Start("bs_saga_duelo_libre")
                textbutton "🏆 Torneo Tier C" action Start("bs_saga_torneo_tier_c")

                textbutton "🔒 Torneo Tier B (no disponible)" action Start("bs_saga_torneo_tier_b_locked")
                textbutton "🔒 Torneo Tier A (no disponible)" action Start("bs_saga_torneo_tier_a_locked")

                textbutton "🔒 Torre del cielo (no disponible)" action Start("bs_saga_torre_cielo_locked")
                textbutton "🧪 Preparación" action Start("bs_saga_preparacion")

                textbutton "🧬 Héroes" action Start("bs_saga_heroes")
                textbutton "🛒 Tienda" action Start("bs_saga_tienda")

                textbutton "📦 Catálogo de itens" action Start("bs_saga_catalogo_items")
                textbutton "↩ Volver al menú principal" action MainMenu()

    frame:
        xalign 0.5
        yalign 0.95
        xsize 1140
        ypadding 8
        background Solid("#1A2A3B")

        text "UI estilo lobby moderna (tipo MOBA): pre-juego separado del combate. Las rutas bloqueadas se habilitan por fases." size 16 color "#B9D8EE" xalign 0.5

style bs_saga_hub_button is navigation_button
style bs_saga_hub_button_text is navigation_button_text

style bs_saga_hub_button:
    xminimum 540
    yminimum 58
    background Solid("#20384E")
    hover_background Solid("#2C4F6E")

style bs_saga_hub_button_text:
    size 22
    color "#EAF6FF"

label bs_saga_hub:
    call screen bs_saga_hub_screen
    return

label bs_saga_duelo_libre:
    $ renpy.jump("start")

label bs_saga_torneo_tier_c:
    scene black
    centered "[Battlestars Saga] Torneo Tier C\n\nRuta provisional lista para implementar brackets y recompensas."
    return

label bs_saga_torneo_tier_b_locked:
    scene black
    centered "[Battlestars Saga] Torneo Tier B\n\nNo disponible en esta fase."
    return

label bs_saga_torneo_tier_a_locked:
    scene black
    centered "[Battlestars Saga] Torneo Tier A\n\nNo disponible en esta fase."
    return

label bs_saga_torre_cielo_locked:
    scene black
    centered "[Battlestars Saga] Torre del cielo\n\nNo disponible en esta fase."
    return

label bs_saga_preparacion:
    scene black
    centered "[Battlestars Saga] Preparación\n\nAquí irá la asignación de pool, técnicas e itens por héroe."
    return

label bs_saga_heroes:
    scene black
    centered "[Battlestars Saga] Héroes\n\nAquí irá el roster, ascensión y gestión individual."
    return

label bs_saga_tienda:
    scene black
    centered "[Battlestars Saga] Tienda\n\nAquí irá compra de materiales, oro y canjes."
    return

label bs_saga_catalogo_items:
    scene black
    centered "[Battlestars Saga] Catálogo de itens\n\nAquí irá enciclopedia/índice de materiais e itens."
    return
