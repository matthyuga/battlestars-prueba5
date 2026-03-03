# ============================================================
# 06F_BATTLE_MANEUVER_SCREENS.rpy
# Sistema de selección de Maniobras
# v1.7.4 Persistent Pos + NoRenpyImport (Ren’Py 7.4.9)
# ------------------------------------------------------------
# - NO modal: no bloquea paneles (IDs/log/teclas)
# - Ventana movible (drag) + guarda posición (x/y)
# - Toggle show/hide con tecla Y + botón ✖
# - Clamp a pantalla (usa config.screen_width/height)
# - ⚠ Sin "import renpy" para evitar pisadas de módulo
# ============================================================

default show_maneuver_choice = True

# Posición persistente
default maneuver_choice_x = 320
default maneuver_choice_y = 180

init -990 python:
    import renpy.store as S
    import renpy.exports as R

    # Keymap para alternar esta ventanita
    config.keymap["toggle_maneuver_choice"] = ["K_y"]

    # Tamaño aproximado de la ventana (para clamp)
    MANEUVER_WIN_W = 640
    MANEUVER_WIN_H = 420

    def toggle_maneuver_choice():
        S.show_maneuver_choice = not getattr(S, "show_maneuver_choice", True)
        R.restart_interaction()

    def _clamp_int(v, lo, hi):
        try:
            v = int(v)
        except:
            v = lo
        if v < lo:
            return lo
        if v > hi:
            return hi
        return v

    class ManeuverChoiceDragged(object):
        """
        Action estable para dragged (Ren'Py 7.4.9).
        Ren'Py lo llama como action(drags, drop)
        """
        def __call__(self, drags, drop):
            try:
                d = drags[0]
                x = int(getattr(d, "x", S.maneuver_choice_x))
                y = int(getattr(d, "y", S.maneuver_choice_y))
            except Exception:
                return

            # Usar config (store) para evitar import renpy.config
            sw = int(getattr(S.config, "screen_width", 1280))
            sh = int(getattr(S.config, "screen_height", 720))

            max_x = max(0, sw - MANEUVER_WIN_W)
            max_y = max(0, sh - MANEUVER_WIN_H)

            S.maneuver_choice_x = _clamp_int(x, 0, max_x)
            S.maneuver_choice_y = _clamp_int(y, 0, max_y)

            R.restart_interaction()


screen battle_maneuver_choice(damage):

    modal False
    zorder 300

    key "toggle_maneuver_choice" action Function(toggle_maneuver_choice)

    default local_choice = "none"
    default show_submenu = False

    $ import renpy.store as S
    $ will_die = S.player_hp - damage <= 0
    $ is_dead  = S.player_hp <= 0

    if show_maneuver_choice:

        drag:
            draggable True
            dragged ManeuverChoiceDragged()

            xpos maneuver_choice_x
            ypos maneuver_choice_y

            frame:
                background "#1119"
                padding (22, 22)
                xmaximum 640

                vbox spacing 18:

                    hbox:
                        xfill True
                        text "Daño entrante: [damage]" size 40 color "#FFD700" bold True xalign 0.0
                        textbutton "✖":
                            action SetVariable("show_maneuver_choice", False)
                            text_size 26

                    if not show_submenu:

                        text "¿Qué deseas hacer?" size 28 color "#FFFFFF"

                        textbutton "Defender normalmente":
                            action SetScreenVariable("local_choice", "defense")
                            text_size 26

                        if will_die or is_dead:
                            textbutton "Ataque por defensa (no disponible)":
                                action NullAction()
                                text_size 26
                                text_color "#666666"
                        else:
                            textbutton "Ataque por defensa":
                                action SetScreenVariable("local_choice", "atk_from_def")
                                text_size 26

                        if is_dead:
                            textbutton "Defensa por ataque (no disponible)":
                                action NullAction()
                                text_size 26
                                text_color "#666666"
                        else:
                            textbutton "Defensa por ataque":
                                action SetScreenVariable("local_choice", "def_from_atk")
                                text_size 26

                        if will_die:
                            text "{color=#FF4444}No puedes contraatacar: este daño te matará.{/color}"
                        elif is_dead:
                            text "{color=#FF4444}Estás derrotada. No puedes contraatacar.{/color}"

                        textbutton "Ver maniobras…":
                            action SetScreenVariable("show_submenu", True)
                            text_size 26

                        if local_choice != "none":
                            textbutton "Confirmar decisión":
                                action [
                                    SetVariable("maneuver_selected", local_choice),
                                    Hide("battle_maneuver_choice"),
                                    SetVariable("show_maneuver_choice", True)
                                ]
                                text_size 30
                                xalign 0.5

                        text "Arrastrá para mover • Tecla Y: ocultar/mostrar" size 16 color "#BBBBBB" xalign 0.5

                    else:

                        text "Maniobras disponibles:" size 30 color "#FFD700" bold True

                        if will_die or is_dead:
                            textbutton "Ataque por defensa (no disponible)":
                                action NullAction()
                                text_size 26
                                text_color "#666666"
                        else:
                            textbutton "Ataque por defensa":
                                action [
                                    SetScreenVariable("local_choice", "atk_from_def"),
                                    SetScreenVariable("show_submenu", False)
                                ]
                                text_size 26

                        if is_dead:
                            textbutton "Defensa por ataque (no disponible)":
                                action NullAction()
                                text_size 26
                                text_color "#666666"
                        else:
                            textbutton "Defensa por ataque":
                                action [
                                    SetScreenVariable("local_choice", "def_from_atk"),
                                    SetScreenVariable("show_submenu", False)
                                ]
                                text_size 26

                        textbutton "Cancelar":
                            action SetScreenVariable("show_submenu", False)
                            text_size 26

                        text "Arrastrá para mover • Tecla Y: ocultar/mostrar" size 16 color "#BBBBBB" xalign 0.5
