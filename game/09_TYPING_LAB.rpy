# Typing Lab ultra simple (aislado):
# - Pantalla negra
# - Letra "h" al centro
# - Sin tiempo, sin marcadores, sin perder
# - Al presionar h: se pone verde, desaparece y luego muestra GANASTE

default typing_lab_phase = "idle"   # idle | hit | hide

screen typing_lab_qte_simple():
    modal True
    zorder 260

    add Solid("#000000")

    key "h" action If(
        typing_lab_phase == "idle",
        true=[SetVariable("typing_lab_phase", "hit")],
        false=NullAction()
    )

    if typing_lab_phase == "hit":
        timer 0.20 action SetVariable("typing_lab_phase", "hide")

    if typing_lab_phase == "hide":
        timer 0.12 action Return("win")

    if typing_lab_phase == "idle":
        text "h":
            xalign 0.5
            yalign 0.5
            size 140
            bold True
            color "#FFFFFF"

    elif typing_lab_phase == "hit":
        text "h":
            xalign 0.5
            yalign 0.5
            size 140
            bold True
            color "#66FF99"


screen typing_lab_win_popup():
    modal True
    zorder 270

    add Solid("#000000")

    frame:
        background "#0000"
        xalign 0.5
        yalign 0.5
        padding (24, 20)

        vbox:
            spacing 18

            text "GANASTE":
                size 78
                bold True
                color "#66FF99"
                xalign 0.5

            textbutton "Volver al menú":
                xalign 0.5
                action Return("menu")


label typing_lab_start:
    $ typing_lab_phase = "idle"
    $ _typing_lab_simple_result = renpy.call_screen("typing_lab_qte_simple")

    if _typing_lab_simple_result == "win":
        $ _typing_lab_popup_action = renpy.call_screen("typing_lab_win_popup")
        return

    return
