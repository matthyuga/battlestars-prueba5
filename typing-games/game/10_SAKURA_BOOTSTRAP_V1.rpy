# Typing Legends / Sakura Sunshine Academy
# Arquitectura base (MVP):
# 1) Menú inicial Typing Legends (Epic bloqueado, Sakura activo)
# 2) Puerta/entrada Sakura
# 3) Registro de jugador (sexo + modo experiencia)
# 4) Hub de academia con módulos
# 5) Vista de lecciones (aula con desenfoque + oscurecido suave)

init -15 python:
    import re
    import renpy.store as S

    def tl_asset(path):
        """Retorna path si existe; si no, retorna None para fallback visual."""
        return path if renpy.loadable(path) else None

    def tl_set_mode_guard(gender, mode):
        """Regla actual definida por diseño:
        - si género = none -> solo modo 1
        """
        g = str(gender or "none")
        try:
            m = int(mode)
        except:
            m = 1
        if g == "none":
            return 1
        return 1 if m not in (1, 2, 3) else m

    def tl_progress_counts(progress):
        """Extrae done/total de forma segura para evitar KeyError en pantallas."""
        if not isinstance(progress, dict):
            return 0, 0
        try:
            done = int(progress.get("done", 0) or 0)
        except:
            done = 0
        try:
            total = int(progress.get("total", 0) or 0)
        except:
            total = 0
        return done, total

    def tl_get_lesson11_intro_slide_files():
        """Toma la lista oficial desde blueprint si está disponible en store."""
        blueprint_slides = getattr(S, "TL_SP7_LESSON1_INTRO_SLIDES", None)
        if isinstance(blueprint_slides, (list, tuple)) and len(blueprint_slides) > 0:
            return [unicode(x) for x in blueprint_slides]

        # Fallback seguro (misma lista oficial esperada para 1.1).
        return [
            u"msg_spa_sp7qwert_1_1_1.htm",
            u"msg_spa_sp7qwert_1_1_2.htm",
            u"msg_spa_sp7qwert_1_1_3.htm",
            u"msg_spa_sp7qwert_1_1_4.htm",
            u"msg_spa_sp7qwert_1_1_5.htm",
        ]

    def tl_extract_readable_text_from_html(html_text):
        """Limpieza mínima de HTML para texto legible (sin parser complejo)."""
        txt = unicode(html_text or u"")
        txt = re.sub(ur"(?is)<script.*?>.*?</script>", u" ", txt)
        txt = re.sub(ur"(?is)<style.*?>.*?</style>", u" ", txt)
        txt = re.sub(ur"(?is)<!--.*?-->", u" ", txt)
        txt = re.sub(ur"(?i)<br\s*/?>", u"\n", txt)
        txt = re.sub(ur"(?i)</p>|</li>|</tr>|</h[1-6]>", u"\n", txt)
        txt = re.sub(ur"(?s)<[^>]+>", u" ", txt)
        txt = tl_html_unescape_basic(txt)
        txt = re.sub(ur"[ \t\r\f\v]+", u" ", txt)
        txt = re.sub(ur"\n\s*\n+", u"\n\n", txt)
        return txt.strip()

    def tl_html_unescape_basic(text):
        """Unescape manual básico (sin dependencia de HTMLParser)."""
        s = unicode(text or u"")

        entity_map = {
            u"&nbsp;": u" ",
            u"&quot;": u"\"",
            u"&apos;": u"'",
            u"&amp;": u"&",
            u"&lt;": u"<",
            u"&gt;": u">",
            u"&iexcl;": u"¡",
            u"&iquest;": u"¿",
            u"&aacute;": u"á",
            u"&eacute;": u"é",
            u"&iacute;": u"í",
            u"&oacute;": u"ó",
            u"&uacute;": u"ú",
            u"&Aacute;": u"Á",
            u"&Eacute;": u"É",
            u"&Iacute;": u"Í",
            u"&Oacute;": u"Ó",
            u"&Uacute;": u"Ú",
            u"&ntilde;": u"ñ",
            u"&Ntilde;": u"Ñ",
            u"&uuml;": u"ü",
            u"&Uuml;": u"Ü",
            u"&deg;": u"°",
        }
        for k, v in entity_map.items():
            s = s.replace(k, v)

        # Entidades numéricas decimales: &#225;
        def _dec_entity(m):
            code = int(m.group(1))
            if 0 <= code <= 65535:
                return unichr(code)
            return m.group(0)

        # Entidades numéricas hexadecimales: &#xE1;
        def _hex_entity(m):
            code = int(m.group(1), 16)
            if 0 <= code <= 65535:
                return unichr(code)
            return m.group(0)

        s = re.sub(ur"&#([0-9]+);", _dec_entity, s)
        s = re.sub(ur"&#x([0-9A-Fa-f]+);", _hex_entity, s)
        return s

    def tl_load_tm_intro_slides_text():
        """Carga 1.1 real desde Typing Master (lesson14) con decode latin-1."""
        base = u"typing-master/lesson14/"
        slides = []
        for fname in tl_get_lesson11_intro_slide_files():
            rel = u"{}{}".format(base, unicode(fname))
            if renpy.loadable(rel):
                raw = renpy.file(rel).read()
                if isinstance(raw, unicode):
                    data = raw
                else:
                    data = raw.decode("latin-1", "replace")
                text = tl_extract_readable_text_from_html(data)
                slides.append({
                    "file": unicode(fname),
                    "text": text if len(text) > 0 else u"(Sin texto legible en la diapositiva)",
                })
            else:
                slides.append({
                    "file": unicode(fname),
                    "text": u"(Archivo no encontrado: {})".format(unicode(fname)),
                })
        return slides


default tl_player_name = ""
default tl_player_gender = "none"       # male | female | none
default tl_experience_mode = 1           # 1=lore off, 2=lore normal, 3=lore+romance
default tl_current_module = "Clases"
default tl_selected_academy = "sakura"  # epic | sakura
default tl_class_category = "basic"     # basic | intermediate | advanced
default tl_selected_teacher = ""        # haru | misaki
default tl_selected_lesson = "lesson_1" # lesson_1 ... lesson_11
default tl_selected_sublesson = ""      # 1_1_intro ... 1_7_phrases_exercise
default tl_intro_page = 0               # página de intro 1.1 persistente (save/load)

# Rutas de imagen recomendadas:
# typing-games/game/images/tl/
#   typing-games-menu.jpg
#   sakura-sunshine/sakura-sunshine-academy-entrada.jpg
#   sakura-sunshine/sakura-sunshine-academy-pasillo.jpg
#   sakura-sunshine/sakura-sunshine-academy-salon.jpg
#   tm_lesson_slide_01.png ...

image tl_fallback_dark = Solid("#131321")
image tl_fallback_rose = Solid("#2A1D2D")

transform tl_soft_focus:
    blur 2.6
    alpha 0.96

screen tl_main_menu_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/typing-games-menu.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_dark"
        text "⚠ Falta asset: images/typing-games-menu.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    # Capa para contraste
    add Solid("#00000012")

    # Hotspots sobre puertas (coordenadas pensadas para 1280x720 aprox)
    # Epic: seleccionable pero bloqueado al iniciar (solo Sakura habilita START)
    button:
        xpos 120
        ypos 170
        xsize 420
        ysize 380
        background Solid("#FFFFFF00")
        action SetVariable("tl_selected_academy", "epic")

    # Sakura: seleccionable
    button:
        xpos 700
        ypos 170
        xsize 440
        ysize 380
        background Solid("#FFFFFF00")
        action SetVariable("tl_selected_academy", "sakura")

    # Indicadores visuales de selección (sin textos superpuestos)
    if tl_selected_academy == "epic":
        frame:
            xpos 112
            ypos 162
            xsize 436
            ysize 396
            background Solid("#5DA9FF22")

    if tl_selected_academy == "sakura":
        frame:
            xpos 692
            ypos 162
            xsize 456
            ysize 396
            background Solid("#FF8ACD22")

    # START en el botón central de la imagen
    button:
        xpos 430
        ypos 540
        xsize 420
        ysize 110
        background Solid("#FFFFFF00")
        action Return("goto_sakura_gate")
        sensitive (tl_selected_academy == "sakura")

    textbutton "SETTINGS" action ShowMenu("preferences") xpos 170 ypos 655

screen tl_sakura_gate_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura_intro.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"

    # Hotspot ENTER ajustado para el fondo sakura_intro (1280x720).
    button:
        xpos 450
        ypos 545
        xsize 420
        ysize 110
        background Solid("#FFFFFF00")
        action Return("register")

    textbutton "Volver" action Return("back") xpos 110 ypos 650

screen tl_registration_screen():
    tag menu
    modal True
    default _reg_step = 1

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1060
        ysize 600
        background Solid("#1B1524DD")

        vbox:
            spacing 18
            xalign 0.5
            yalign 0.5

            text "Registro de Jugador" xalign 0.5 size 52 color "#FFD7F1"
            text "Paso [_reg_step]/3" size 24 color "#D0BFD6" xalign 0.5

            if _reg_step == 1:
                hbox:
                    spacing 24
                    xalign 0.5
                    text "Nombre:" size 32
                    input value VariableInputValue("tl_player_name") length 20 allow " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúÁÉÍÓÚñÑ0123456789_-." xmaximum 520

                text "Debes ingresar un nombre para continuar." size 22 color "#D0BFD6"

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Siguiente" action SetScreenVariable("_reg_step", 2) sensitive (len((tl_player_name or "").strip()) > 0)
                    textbutton "Volver" action Return("back")

            elif _reg_step == 2:
                text "Sexo del jugador" size 32
                hbox:
                    spacing 18
                    xalign 0.5
                    textbutton "Masculino{}".format(" ✓" if tl_player_gender == "male" else "") action SetVariable("tl_player_gender", "male")
                    textbutton "Femenino{}".format(" ✓" if tl_player_gender == "female" else "") action SetVariable("tl_player_gender", "female")
                    textbutton "Ninguno{}".format(" ✓" if tl_player_gender == "none" else "") action SetVariable("tl_player_gender", "none")

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Siguiente" action SetScreenVariable("_reg_step", 3)
                    textbutton "Atrás" action SetScreenVariable("_reg_step", 1)

            else:
                text "Modo de experiencia" size 32
                hbox:
                    spacing 18
                    xalign 0.5
                    textbutton "1) Lore desactivado{}".format(" ✓" if tl_experience_mode == 1 else "") action SetVariable("tl_experience_mode", 1)
                    textbutton "2) Lore normal{}".format(" ✓" if tl_experience_mode == 2 else "") action SetVariable("tl_experience_mode", 2)
                    textbutton "3) Lore + romance{}".format(" ✓" if tl_experience_mode == 3 else "") action SetVariable("tl_experience_mode", 3)

                text "Regla activa: si eliges 'Ninguno', el modo se fuerza a 1 (sin lore ni romance)." size 22 color "#D0BFD6"
                text "Estado actual -> Nombre: [tl_player_name] | Sexo: [tl_player_gender] | Modo: [tl_experience_mode]" size 24 color "#F6E5FF"

                hbox:
                    spacing 20
                    xalign 0.5
                    textbutton "Continuar" action Return("continue") sensitive (len((tl_player_name or "").strip()) > 0)
                    textbutton "Atrás" action SetScreenVariable("_reg_step", 2)

screen tl_sakura_welcome_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"

    add Solid("#00000055")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 960
        ysize 420
        background Solid("#1B1524E8")

        vbox:
            spacing 24
            xalign 0.5
            yalign 0.5

            text "Bienvenido a la Academia Sakura Sunshine" xalign 0.5 size 52 color "#FFD7F1"
            text "Tu registro se completó correctamente." xalign 0.5 size 24 color "#E7DAEF"
            textbutton "Avanzar" action Return("to_hub") xalign 0.5

screen tl_sakura_hub_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#0000005F")

    text "Sakura Sunshine Academy" xalign 0.5 yalign 0.06 size 56 color "#FFD7F1" outlines [(2, "#5a1d4a", 0, 0)]

    if tl_player_name:
        text "Jugador: [tl_player_name]  |  Sexo: [tl_player_gender]  |  Modo: [tl_experience_mode]" xalign 0.5 yalign 0.13 size 22
    else:
        text "Jugador: Invitado  |  Sexo: [tl_player_gender]  |  Modo: [tl_experience_mode]" xalign 0.5 yalign 0.13 size 22

    # Opciones (tuerca) separado arriba a la derecha
    textbutton "⚙" action ShowMenu("preferences") xalign 0.965 yalign 0.05

    frame:
        xalign 0.14
        yalign 0.56
        xsize 350
        ysize 430
        background Solid("#1A1120D8")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.06

            text "Módulos" size 40 color "#FFD7F1" xalign 0.5

            textbutton "Clases" action Return("go_lessons")
            textbutton "Repaso / Práctica" action Return("go_practice")
            textbutton "Exámenes" action Return("go_exams")
            textbutton "Juegos / Actividades" action Return("go_activities")
            textbutton "Diario" action Return("go_diary")
            textbutton "Biblioteca" action Return("go_library")

    frame:
        xalign 0.50
        yalign 0.53
        xsize 560
        ysize 420
        background Solid("#251A2EDD")

        vbox:
            spacing 12
            xalign 0.5
            yalign 0.08

            text "Vista previa del módulo" size 36 color "#FFD7F1" xalign 0.5
            text "Módulo actual: [tl_current_module]" size 28 xalign 0.5
            $ _mod_progress = get_check_progress(tl_current_module)
            $ _mod_done, _mod_total = tl_progress_counts(_mod_progress)
            text "Progreso académico (checks): [_mod_done]/[_mod_total]" size 22 xalign 0.5
            text "En esta etapa construiremos primero Clases (lecciones)." size 20 xalign 0.5
            text "Luego conectamos Práctica, Exámenes y actividades." size 18 xalign 0.5

    frame:
        xalign 0.80
        yalign 0.82
        xsize 360
        ysize 260
        background Solid("#1A1120D8")

        vbox:
            spacing 12
            xalign 0.5
            yalign 0.08

            text "Lugares" size 34 color "#FFD7F1" xalign 0.5
            textbutton "Entrada (placeholder)" action Return("go_place_entrance")
            textbutton "Patio (placeholder)" action Return("go_place_patio")
            textbutton "QA técnico" action Return("go_qa_tech")
            textbutton "Salir al menú" action Return("to_main")

screen tl_place_placeholder_screen(place_name="Lugar"):
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 920
        ysize 420
        background Solid("#151019DE")

        vbox:
            spacing 20
            xalign 0.5
            yalign 0.5

            text "[place_name]" size 44 color "#FFD7F1" xalign 0.5
            text "Zona en construcción (placeholder)." size 24 color "#E8D9F0" xalign 0.5
            textbutton "Volver al hub" action Return("back") xalign 0.5

screen tl_classes_category_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 560
        background Solid("#151019DE")

        vbox:
            spacing 18
            xalign 0.5
            yalign 0.08

            text "Clases · Selección académica" size 42 color "#FFD7F1" xalign 0.5
            text "Elige categoría para iniciar el curso." size 24 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Básica{}".format(" ✓" if tl_class_category == "basic" else "") action SetVariable("tl_class_category", "basic")
                textbutton "Intermedia (próximamente)" action NullAction() sensitive False
                textbutton "Avanzada (próximamente)" action NullAction() sensitive False

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Continuar" action Return("continue_basic") sensitive (tl_class_category == "basic")
                textbutton "Volver al hub" action Return("back")

            if tl_class_category != "basic":
                text "Selecciona 'Básica' para continuar en esta versión." size 20 color "#FFD7C1" xalign 0.5

screen tl_classes_teacher_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1100
        ysize 620
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.06

            text "Clases Básica · Selección docente" size 40 color "#FFD7F1" xalign 0.5
            text "Selecciona docente para continuar." size 22 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 28
                xalign 0.5

                button:
                    background Solid("#00000000")
                    action SetVariable("tl_selected_teacher", "haru")
                    frame:
                        xsize 360
                        ysize 380
                        background Solid("#FFFFFF00")
                        if tl_selected_teacher == "haru":
                            add Solid("#FFD7F133")
                        $ _haru = tl_asset("gui/characters-sakura-sunshine/male/teachers/Haru.png")
                        if not _haru:
                            $ _haru = tl_asset("gui/characters-sakura-sunshine/female/teachers/Ayame.png")
                        if _haru:
                            add _haru fit "contain" xalign 0.5 yalign 0.5
                        else:
                            frame:
                                xalign 0.5
                                yalign 0.45
                                xsize 280
                                ysize 270
                                background Solid("#2A2230")
                                text "Retrato no disponible" xalign 0.5 yalign 0.5 size 24
                        text "Haru" xalign 0.5 yalign 0.92 size 30 color "#F7E8FF"

                button:
                    background Solid("#00000000")
                    action SetVariable("tl_selected_teacher", "misaki")
                    frame:
                        xsize 360
                        ysize 380
                        background Solid("#FFFFFF00")
                        if tl_selected_teacher == "misaki":
                            add Solid("#FFD7F133")
                        $ _misaki = tl_asset("gui/characters-sakura-sunshine/female/teachers/Misaki.png")
                        if not _misaki:
                            $ _misaki = tl_asset("gui/characters-sakura-sunshine/male/teachers/Masato.png")
                        if _misaki:
                            add _misaki fit "contain" xalign 0.5 yalign 0.5
                        else:
                            frame:
                                xalign 0.5
                                yalign 0.45
                                xsize 280
                                ysize 270
                                background Solid("#2A2230")
                                text "Retrato no disponible" xalign 0.5 yalign 0.5 size 24
                        text "Misaki" xalign 0.5 yalign 0.92 size 30 color "#F7E8FF"

            $ _teacher_label = tl_selected_teacher.title() if tl_selected_teacher else "—"
            text "Docente elegida/o: [_teacher_label]" xalign 0.5 size 22 color "#E8D9F0"

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Continuar" action Return("continue") sensitive (len((tl_selected_teacher or "").strip()) > 0)
                textbutton "Atrás" action Return("back")

            if len((tl_selected_teacher or "").strip()) == 0:
                text "Debes seleccionar Haru o Misaki para habilitar 'Continuar'." size 20 color "#FFD7C1" xalign 0.5

screen tl_classes_course_intro_screen():
    tag menu
    modal True
    default _dialog_step = 0

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")
    $ _teacher_name = tl_selected_teacher.title() if tl_selected_teacher else "Docente"
    if tl_selected_teacher == "haru":
        $ _teacher_intro_1 = "Soy Haru, vamos a construir precisión desde la base."
        $ _teacher_intro_2 = "Te recomiendo iniciar por Introducción y Fila central."
        $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/male/teachers/Haru.png")
        if not _teacher_portrait:
            $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/female/teachers/Ayame.png")
    elif tl_selected_teacher == "misaki":
        $ _teacher_intro_1 = "Soy Misaki, avanzaremos paso a paso con buena postura."
        $ _teacher_intro_2 = "Empezaremos por Introducción y luego ejercicios guiados."
        $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/female/teachers/Misaki.png")
        if not _teacher_portrait:
            $ _teacher_portrait = tl_asset("gui/characters-sakura-sunshine/male/teachers/Masato.png")
    else:
        $ _teacher_intro_1 = "Vamos a comenzar con el plan básico de mecanografía."
        $ _teacher_intro_2 = "Elige una sublección y avanzamos."
        $ _teacher_portrait = None
    $ _dialog_line = _teacher_intro_1 if _dialog_step == 0 else _teacher_intro_2

    frame:
        xalign 0.5
        yalign 0.38
        xsize 980
        ysize 360
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Curso de Escritura al Tacto" size 44 color "#FFD7F1" xalign 0.5
            text "Qué aprenderás con este curso:" size 24 color "#E8D9F0" xalign 0.5
            text "• Postura y posición de manos en fila central." size 22 xalign 0.5
            text "• Precisión antes que velocidad, con práctica progresiva." size 22 xalign 0.5
            text "• Técnica para escribir sin mirar el teclado." size 22 xalign 0.5
            text "Docente actual: [_teacher_name]" size 22 color "#E8D9F0" xalign 0.5
            if tl_experience_mode == 1:
                text "Modo 1: aprendizaje puro (sin lore ni romance)." size 20 color "#E8D9F0" xalign 0.5

    frame:
        xalign 0.5
        yalign 0.80
        xsize 980
        ysize 230
        background Solid("#17121EEC")

        hbox:
            spacing 16
            xalign 0.5
            yalign 0.5

            frame:
                xsize 190
                ysize 190
                background Solid("#241D2C")
                if _teacher_portrait:
                    add _teacher_portrait fit "contain" xalign 0.5 yalign 0.5
                else:
                    text "Sin retrato" xalign 0.5 yalign 0.5 size 22 color "#E8D9F0"

            vbox:
                spacing 10
                xsize 730
                yalign 0.5

                frame:
                    xsize 220
                    ysize 42
                    background Solid("#2A2230")
                    text "[_teacher_name]" xalign 0.5 yalign 0.5 size 24 color "#FFD7F1"

                frame:
                    xsize 730
                    ysize 92
                    background Solid("#211A29")
                    text "[_dialog_line]" xalign 0.02 yalign 0.5 size 24 color "#F7E8FF"

                hbox:
                    spacing 14
                    textbutton "Continuar" action SetScreenVariable("_dialog_step", 1) sensitive (_dialog_step == 0)
                    textbutton "Avanzar" action Return("continue") sensitive (_dialog_step == 1)
                    textbutton "Atrás" action Return("back")

screen tl_classes_course_lessons_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1040
        ysize 620
        background Solid("#151019DE")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.06

            text "Curso básico · Lecciones disponibles" size 40 color "#FFD7F1" xalign 0.5
            text "Selecciona una de las 11 lecciones de Typing Master." size 22 color "#E8D9F0" xalign 0.5

            viewport:
                draggable True
                mousewheel True
                ymaximum 400

                vbox:
                    spacing 8
                    xalign 0.5

                    textbutton "Lección 1 · La fila central{}".format(" ✓" if tl_selected_lesson == "lesson_1" else "") action SetVariable("tl_selected_lesson", "lesson_1")
                    textbutton "Lección 2 · Teclas E e I (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 3 · Teclas R y N (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 4 · Teclas C y O (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 5 · Teclas T U y Q (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 6 · Mayúsculas, punto y tilde (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 7 · Teclas G y P (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 8 · Teclas B M y coma (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 9 · Teclas V Y y ¿ ? (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 10 · Teclas Z H y ¡ ! (próximamente)" action NullAction() sensitive False
                    textbutton "Lección 11 · Teclas W y X (próximamente)" action NullAction() sensitive False

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Ver submódulos de la lección" action Return("open_selected") sensitive (tl_selected_lesson == "lesson_1")
                textbutton "Volver a clase" action Return("back_class")
                textbutton "Atrás" action Return("back")

            if tl_selected_lesson != "lesson_1":
                text "Por ahora solo está habilitada la Lección 1 en esta versión." size 20 color "#FFD7C1" xalign 0.5

screen tl_classes_lesson_panel_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _s11 = get_check("clases", "lesson_1", "1_1_intro")
    $ _s12 = get_check("clases", "lesson_1", "1_2_home_row")
    $ _s13 = get_check("clases", "lesson_1", "1_3_results")
    $ _s14 = get_check("clases", "lesson_1", "1_4_keys_exercise")
    $ _s15 = get_check("clases", "lesson_1", "1_5_exam_help")
    $ _s16 = get_check("clases", "lesson_1", "1_6_words_exercise")
    $ _s17 = get_check("clases", "lesson_1", "1_7_phrases_exercise")
    $ _lesson_done = sum([1 for _v in [_s11, _s12, _s13, _s14, _s15, _s16, _s17] if _v])

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 650
        background Solid("#151019DE")

        hbox:
            spacing 20
            xalign 0.5
            yalign 0.06

            vbox:
                spacing 8
                xsize 620
                text "Lección 1 · Panel de submódulos" size 40 color "#FFD7F1"
                text "Progreso: [_lesson_done]/7 checks" size 24 color "#E8D9F0"

                textbutton "1.1 Introducción {}".format("✓" if _s11 else "□") action SetVariable("tl_selected_sublesson", "1_1_intro")
                textbutton "1.2 Fila central {}".format("✓" if _s12 else "□") action SetVariable("tl_selected_sublesson", "1_2_home_row")
                textbutton "1.3 Ver resultados {}".format("✓" if _s13 else "□") action SetVariable("tl_selected_sublesson", "1_3_results")
                textbutton "1.4 Ejercicio teclas {}".format("✓" if _s14 else "□") action SetVariable("tl_selected_sublesson", "1_4_keys_exercise")
                textbutton "1.5 Ayuda exámenes {}".format("✓" if _s15 else "□") action SetVariable("tl_selected_sublesson", "1_5_exam_help")
                textbutton "1.6 Ejercicio palabras {}".format("✓" if _s16 else "□") action SetVariable("tl_selected_sublesson", "1_6_words_exercise")
                textbutton "1.7 Ejercicio frases {}".format("✓" if _s17 else "□") action SetVariable("tl_selected_sublesson", "1_7_phrases_exercise")

            vbox:
                spacing 14
                xsize 420
                text "Sublección seleccionada" size 30 color "#FFD7F1" xalign 0.5
                frame:
                    xsize 400
                    ysize 210
                    background Solid("#241D2C")
                    $ _selected_label = tl_selected_sublesson if tl_selected_sublesson else "Ninguna"
                    text "[_selected_label]" xalign 0.5 yalign 0.5 size 24

                textbutton "Iniciar sublección" action Return("start_selected") sensitive (len((tl_selected_sublesson or "").strip()) > 0) xalign 0.5
                textbutton "Volver a curso" action Return("back_course") xalign 0.5
                textbutton "Volver al hub" action Return("back_hub") xalign 0.5
                textbutton "Guardar partida" action ShowMenu("save") xalign 0.5
                textbutton "Cargar partida" action ShowMenu("load") xalign 0.5

                if len((tl_selected_sublesson or "").strip()) == 0:
                    text "Selecciona un submódulo para habilitar 'Iniciar sublección'." size 18 color "#FFD7C1" xalign 0.5

screen tl_sublesson_intro_screen():
    tag menu
    modal True

    $ _slides = tl_load_tm_intro_slides_text()
    $ _last = max(0, len(_slides) - 1)
    $ _safe_page = max(0, min(_last, int(tl_intro_page if tl_intro_page is not None else 0)))
    $ _slide_entry = _slides[_safe_page] if len(_slides) > 0 else {"file": "n/a", "text": "Contenido de introducción no disponible."}
    $ _slide_text = unicode(_slide_entry.get("text", "Contenido de introducción no disponible."))
    $ _slide_file = unicode(_slide_entry.get("file", "n/a"))

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 580
        background Solid("#151019EE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Lección 1.1 · Introducción real" size 40 color "#FFD7F1" xalign 0.5

            frame:
                xsize 860
                ysize 300
                background Solid("#221A2CEB")
                viewport:
                    draggable True
                    mousewheel True
                    xmaximum 820
                    ymaximum 260
                    xalign 0.5
                    yalign 0.5
                    text "[_slide_text]" size 24 text_align 0.0

            text "Página [(_safe_page + 1)]/[max(1, len(_slides))]" size 22 color "#E8D9F0" xalign 0.5
            text "Fuente: [_slide_file]" size 17 color "#C9B8D5" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Anterior" action SetVariable("tl_intro_page", max(0, _safe_page - 1)) sensitive (_safe_page > 0)
                textbutton "Siguiente" action SetVariable("tl_intro_page", min(_last, _safe_page + 1)) sensitive (_safe_page < _last)
                textbutton "Completar introducción" action [SetVariable("tl_intro_page", 0), Return("complete")] sensitive (_safe_page == _last)
                textbutton "Volver a clase" action [SetVariable("tl_intro_page", 0), Return("back_class")]

screen tl_sublesson_content_screen(sub_id="", sub_title="", objective="", summary="", next_hint=""):
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000099")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 580
        background Solid("#151019EE")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.08

            text "Lección 1 · [sub_title]" size 40 color "#FFD7F1" xalign 0.5
            text "Submódulo: [sub_id]" size 22 color "#E8D9F0" xalign 0.5

            frame:
                xsize 860
                ysize 230
                background Solid("#221A2CEB")
                vbox:
                    spacing 10
                    xalign 0.5
                    yalign 0.5
                    text "Objetivo: [objective]" size 24 xalign 0.5 text_align 0.5
                    text "[summary]" size 22 xalign 0.5 text_align 0.5
                    if len((next_hint or "").strip()) > 0:
                        text "Siguiente paso recomendado: [next_hint]" size 20 color "#DCCEE6" xalign 0.5 text_align 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Completar subsección" action Return("complete")
                textbutton "Volver a clase" action Return("back_class")

screen tl_qa_tech_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _a_gate = tl_asset("images/sakura-sunshine/sakura_intro.jpg")
    $ _a_reg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-entrada.jpg")
    $ _a_hub = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    $ _a_cls = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1080
        ysize 620
        background Solid("#151019DE")

        vbox:
            spacing 12
            xalign 0.5
            yalign 0.05

            text "QA técnico y UX · Fase 5" size 42 color "#FFD7F1" xalign 0.5
            text "Checklist rápido para pruebas externas." size 22 color "#E8D9F0" xalign 0.5

            text "P5-1 Ruta clases: Inicio -> Gate -> Registro -> Bienvenida -> Hub -> Clases -> retorno Hub" size 20
            text "P5-2 Save/Load: usar botones Guardar/Cargar en panel de sublecciones" size 20
            text "P5-3 Fallback assets no bloqueante:" size 20
            text "  • gate (sakura_intro): {}".format("OK" if _a_gate else "Fallback activo") size 18 color ("#BEECC6" if _a_gate else "#FFE5B1")
            text "  • registro (entrada): {}".format("OK" if _a_reg else "Fallback activo") size 18 color ("#BEECC6" if _a_reg else "#FFE5B1")
            text "  • hub (pasillo): {}".format("OK" if _a_hub else "Fallback activo") size 18 color ("#BEECC6" if _a_hub else "#FFE5B1")
            text "  • clases (salón): {}".format("OK" if _a_cls else "Fallback activo") size 18 color ("#BEECC6" if _a_cls else "#FFE5B1")
            text "P5-4 Botones sensibles: siempre muestran feedback textual cuando están bloqueados." size 20
            text "P5-5 Ruta final: Hub -> Clases -> Docente -> Curso -> Lecciones -> 1.1 -> retorno." size 20
            text "P5-6 Save/Load en 1.1 conserva página con tl_intro_page." size 20

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Abrir Guardar" action ShowMenu("save")
                textbutton "Abrir Cargar" action ShowMenu("load")
                textbutton "Volver al hub" action Return("back")

label tl_classes_basic_flow:
    $ tl_current_module = "Clases"
    $ tl_selected_sublesson = ""
    call screen tl_classes_category_screen
    if _return == "back":
        jump tl_sakura_hub
    if _return != "continue_basic":
        jump tl_classes_basic_flow

label tl_classes_teacher_flow:
    call screen tl_classes_teacher_screen
    if _return == "back":
        jump tl_classes_basic_flow
    if _return != "continue":
        jump tl_classes_teacher_flow

label tl_classes_course_intro_flow:
    call screen tl_classes_course_intro_screen
    if _return == "back":
        jump tl_classes_teacher_flow
    if _return == "continue":
        jump tl_classes_course_lessons_flow
    jump tl_classes_course_intro_flow

label tl_classes_course_lessons_flow:
    call screen tl_classes_course_lessons_screen
    if _return == "back":
        jump tl_classes_course_intro_flow
    if _return == "back_class":
        jump tl_classes_course_intro_flow
    if _return == "open_selected":
        if tl_selected_lesson == "lesson_1":
            jump tl_classes_lesson_panel_flow
    jump tl_classes_course_lessons_flow

label tl_classes_lesson_panel_flow:
    call screen tl_classes_lesson_panel_screen
    if _return == "back_hub":
        jump tl_sakura_hub
    if _return == "back_course":
        jump tl_classes_course_lessons_flow
    if _return == "start_selected":
        $ _selected = str(tl_selected_sublesson or "")
        $ _sub_return = "back_class"

        # Flujo académico puro:
        # - En sublecciones de Clases NO se llama Typing Lab.
        # - Typing Lab queda para Práctica/Exámenes fuera de este panel.
        if _selected == "1_1_intro":
            call screen tl_sublesson_intro_screen
            $ _sub_return = _return
        elif _selected == "1_2_home_row":
            call screen tl_sublesson_content_screen(
                sub_id="1.2",
                sub_title="Fila central",
                objective="Ubicar dedos en A-S-D-F y J-K-L-Ñ sin mirar.",
                summary="Practica pulsaciones controladas y ritmo constante en fila central.",
                next_hint="Continúa con 1.3 para revisar resultados y control de errores."
            )
            $ _sub_return = _return
        elif _selected == "1_3_results":
            call screen tl_sublesson_content_screen(
                sub_id="1.3",
                sub_title="Ver resultados",
                objective="Interpretar precisión, errores y consistencia.",
                summary="Aprender a leer resultados permite corregir técnica antes de acelerar.",
                next_hint="Pasa a 1.4 para reforzar precisión de teclas."
            )
            $ _sub_return = _return
        elif _selected == "1_4_keys_exercise":
            call screen tl_sublesson_content_screen(
                sub_id="1.4",
                sub_title="Ejercicio de teclas",
                objective="Consolidar control de dedos en secuencias de teclas.",
                summary="Ejercicio académico enfocado en precisión y postura, sin modo libre.",
                next_hint="Luego revisa 1.5 para guía de exámenes."
            )
            $ _sub_return = _return
        elif _selected == "1_5_exam_help":
            call screen tl_sublesson_content_screen(
                sub_id="1.5",
                sub_title="Ayuda exámenes",
                objective="Conocer criterios de evaluación y preparación.",
                summary="Revisa consejos para gestionar errores, tiempo y consistencia.",
                next_hint="Sigue con 1.6 para estructura de palabras."
            )
            $ _sub_return = _return
        elif _selected == "1_6_words_exercise":
            call screen tl_sublesson_content_screen(
                sub_id="1.6",
                sub_title="Ejercicio de palabras",
                objective="Aplicar técnica de fila central en palabras completas.",
                summary="Prioriza exactitud de cada palabra antes de aumentar velocidad.",
                next_hint="Finaliza en 1.7 con frases completas."
            )
            $ _sub_return = _return
        else:
            call screen tl_sublesson_content_screen(
                sub_id="1.7",
                sub_title="Ejercicio de frases",
                objective="Mantener precisión en secuencias largas.",
                summary="Integra postura, ritmo y corrección consciente al escribir frases.",
                next_hint="Al completar, tendrás cerrada la base de Lección 1."
            )
            $ _sub_return = _return

        if _sub_return == "complete":
            $ set_check("clases", "lesson_1", _selected, True)
            "Subsección completada: [_selected]. Contenido académico registrado."
        elif _sub_return == "back_class":
            pass
        else:
            "Subsección no completada. Vuelve cuando quieras continuar."
        jump tl_classes_lesson_panel_flow

    jump tl_classes_lesson_panel_flow

screen tl_lessons_mock_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-salon.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    # Oscurecido para que la UI se lea mejor
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 640
        background Solid("#151019DE")

        hbox:
            spacing 24
            xalign 0.5
            yalign 0.05

            vbox:
                spacing 10
                xsize 560
                $ _c11 = get_check("clases", "lesson_1", "1_1_intro")
                $ _c12 = get_check("clases", "lesson_1", "1_2_home_row")
                $ _c13 = get_check("clases", "lesson_1", "1_3_results")
                $ _c14 = get_check("clases", "lesson_1", "1_4_keys_exercise")
                $ _c15 = get_check("clases", "lesson_1", "1_5_exam_help")
                $ _c16 = get_check("clases", "lesson_1", "1_6_words_exercise")
                $ _c17 = get_check("clases", "lesson_1", "1_7_phrases_exercise")
                $ _lesson_done = sum([1 for _v in [_c11, _c12, _c13, _c14, _c15, _c16, _c17] if _v])

                text "Clases · Lección 1 (mock)" size 38 color "#FFD7F1"
                text "Progreso Lección 1: [_lesson_done]/7" size 24 color "#EADAF2"
                textbutton "1.1 Introducción{}".format("  ✓" if _c11 else "") action Function(set_check, "clases", "lesson_1", "1_1_intro", True)
                textbutton "1.2 Teclas de la Fila Central{}".format("  ✓" if _c12 else "") action Function(set_check, "clases", "lesson_1", "1_2_home_row", True)
                textbutton "1.3 Ver resultados{}".format("  ✓" if _c13 else "") action Function(set_check, "clases", "lesson_1", "1_3_results", True)
                textbutton "1.4 Ejercicio de Teclas{}".format("  ✓" if _c14 else "") action Function(set_check, "clases", "lesson_1", "1_4_keys_exercise", True)
                textbutton "1.5 Ayuda: Exámenes{}".format("  ✓" if _c15 else "") action Function(set_check, "clases", "lesson_1", "1_5_exam_help", True)
                textbutton "1.6 Ejercicio de Palabras{}".format("  ✓" if _c16 else "") action Function(set_check, "clases", "lesson_1", "1_6_words_exercise", True)
                textbutton "1.7 Ejercicio de Párrafos{}".format("  ✓" if _c17 else "") action Function(set_check, "clases", "lesson_1", "1_7_phrases_exercise", True)

                null height 18
                text "Puedes usar capturas de Typing Master en esta etapa (sí, totalmente)." size 20 color "#DCCEE6"

                hbox:
                    spacing 18
                    textbutton "Probar Typing Lab" action Return("open_typing_lab")
                    textbutton "Marcar todo Lección 1" action [
                        Function(set_check, "clases", "lesson_1", "1_1_intro", True),
                        Function(set_check, "clases", "lesson_1", "1_2_home_row", True),
                        Function(set_check, "clases", "lesson_1", "1_3_results", True),
                        Function(set_check, "clases", "lesson_1", "1_4_keys_exercise", True),
                        Function(set_check, "clases", "lesson_1", "1_5_exam_help", True),
                        Function(set_check, "clases", "lesson_1", "1_6_words_exercise", True),
                        Function(set_check, "clases", "lesson_1", "1_7_phrases_exercise", True),
                    ]
                    textbutton "Finalizar Lección 1" action Return("complete_lesson_1") sensitive (_lesson_done >= 7)
                    textbutton "Volver al hub" action Return("back")

            vbox:
                spacing 10
                text "Preview de apoyo" size 30 color "#FFD7F1"

                $ slide = tl_asset("images/tl/tm_lesson_slide_01.png")
                if slide:
                    add slide fit "contain" xsize 480 ysize 360
                else:
                    frame:
                        xsize 480
                        ysize 360
                        background Solid("#2A2230")
                        text "Sube aquí: images/tl/tm_lesson_slide_01.png" xalign 0.5 yalign 0.5 size 22

screen tl_diary_checklist_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")
    $ _checks = _academic_ensure_store()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1120
        ysize 640
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Diario académico · Checklist" size 42 color "#FFD7F1" xalign 0.5

            viewport:
                draggable True
                mousewheel True
                ymaximum 470

                vbox:
                    spacing 8
                    for _module_id, _lessons in _checks.items():
                        $ _mod_prog = get_check_progress(_module_id)
                        $ _mod_done, _mod_total = tl_progress_counts(_mod_prog)
                        text "[_module_id.title()]  [_mod_done]/[_mod_total]" size 28 color "#F7E8FF"
                        for _lesson_id, _steps in _lessons.items():
                            $ _lesson_done = sum([1 for _v in _steps.values() if _v])
                            $ _lesson_total = len(_steps)
                            text "  - [_lesson_id]  [_lesson_done]/[_lesson_total]" size 22 color "#DDD0E7"
                            for _step_id, _done in _steps.items():
                                text "      {} {}".format("✓" if _done else "□", _step_id) size 19 color ("#8FFFAD" if _done else "#D2C6DE")

            hbox:
                spacing 16
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_social_profile_screen():
    tag menu
    modal True

    default _aff_tip = "Pasa el cursor por una barra para ver la afinidad actual."

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
        text "⚠ Falta asset: images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg (usando fallback)" xalign 0.5 yalign 0.985 size 18 color "#FFD6D6"

    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1160
        ysize 660
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Ficha social · Afinidad por personaje" size 42 color "#FFD7F1" xalign 0.5
            text "Sistema social separado del académico (solo barras c0..c10)." size 20 color "#E5D5EE" xalign 0.5
            if tl_experience_mode == 1:
                text "Modo 1 activo: romance oculto para foco total en mecanografía." size 18 color "#E8D9F0" xalign 0.5

            viewport:
                draggable True
                mousewheel True
                ymaximum 470

                vbox:
                    spacing 8
                    for _cid in AFFINITY_CHARACTER_IDS:
                        $ _pts = get_affinity(_cid)
                        $ _rom_enabled = is_romance_enabled(tl_experience_mode, tl_player_gender, _cid)
                        $ _rom_msg = get_romance_lock_message(tl_experience_mode, tl_player_gender, _cid)
                        hbox:
                            spacing 12
                            xalign 0.5

                            text "[_cid.title()]" size 24 xminimum 160

                            frame:
                                xsize 220
                                ysize 30
                                background Solid("#00000000")
                                add get_affinity_bar_image(_cid) xalign 0.0 yalign 0.5

                                button:
                                    xfill True
                                    yfill True
                                    background Solid("#00000000")
                                    hovered SetScreenVariable("_aff_tip", "Afinidad actual {} / 10 ({})".format(_pts, _cid))
                                    unhovered SetScreenVariable("_aff_tip", "Pasa el cursor por una barra para ver la afinidad actual.")
                                    action NullAction()

                            textbutton "+ Interacción" action Function(award_affinity_event, _cid, "interaction_success")
                            textbutton "+ Misión" action Function(award_affinity_event, _cid, "social_mission_success")

                            if tl_experience_mode == 1:
                                null width 280
                            elif _rom_enabled:
                                frame:
                                    xsize 48
                                    ysize 48
                                    background Solid("#00000000")
                                    add get_romance_heart_image(_cid) fit "contain" xalign 0.5 yalign 0.5
                                textbutton "+ Romance" action Function(add_romance, _cid, 1)
                            else:
                                text _rom_msg size 16 color "#FFB9D5" xmaximum 220

            text "[_aff_tip]" size 19 color "#FFD7F1" xalign 0.5

            hbox:
                spacing 16
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_practice_mode_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 880
        ysize 520
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Práctica · Modo libre" size 42 color "#FFD7F1" xalign 0.5
            text "Selecciona modo de práctica para Typing Lab" size 22 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Letras" action SetVariable("typing_lab_selected_mode", "letters")
                textbutton "Palabras" action SetVariable("typing_lab_selected_mode", "words")
                textbutton "Frases" action SetVariable("typing_lab_selected_mode", "phrases")

            text "Modo actual: [typing_lab_selected_mode]" size 24 xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Iniciar práctica" action Return("start_practice")
                textbutton "Volver al hub" action Return("back")

screen tl_exam_entry_screen():
    tag menu
    modal True

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 900
        ysize 520
        background Solid("#151019DE")

        vbox:
            spacing 16
            xalign 0.5
            yalign 0.08

            text "Examen académico · Intento 1" size 42 color "#FFD7F1" xalign 0.5
            text "Umbral de aprobación: 50 puntos" size 26 color "#FFE5B1" xalign 0.5
            text "Modo del examen: frases" size 22 color "#E8D9F0" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Rendir examen" action Return("start_exam")
                textbutton "Volver al hub" action Return("back")

screen tl_activities_quest_screen():
    tag menu
    modal True

    default _msg = "Completa la quest social para subir afinidad."

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _quest_done = get_check("actividades", "activity_1", "quest_1")
    $ _airi_aff = get_affinity("airi")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 980
        ysize 580
        background Solid("#151019DE")

        vbox:
            spacing 14
            xalign 0.5
            yalign 0.08

            text "Actividades · Quest social 1" size 42 color "#FFD7F1" xalign 0.5
            text "Quest: Ayuda a Airi a ordenar notas para la clase." size 24 color "#E8D9F0" xalign 0.5
            text "Estado: {}".format("Completada ✓" if _quest_done else "Pendiente") size 24 xalign 0.5
            text "Afinidad Airi: [_airi_aff]/10" size 24 color "#FFD7F1" xalign 0.5

            if not _quest_done:
                textbutton "Completar quest (+1 afinidad Airi)" action [
                    Function(set_check, "actividades", "activity_1", "quest_1", True),
                    Function(award_affinity_event, "airi", "social_mission_success"),
                    SetScreenVariable("_msg", "Quest completada. +1 afinidad para Airi."),
                ] xalign 0.5
            else:
                text "Ya completaste esta quest en esta partida." size 20 color "#BEECC6" xalign 0.5

            text "[_msg]" size 20 color "#FFE5B1" xalign 0.5

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Ver ficha social" action [Hide("tl_activities_quest_screen"), Show("tl_social_profile_screen")]
                textbutton "Volver al hub" action Return("back")

screen tl_diary_tabs_screen():
    tag menu
    modal True

    default _tab = "academic"

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-pasillo.jpg")
    if bg:
        add bg
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    $ _checks = _academic_ensure_store()

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1160
        ysize 660
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Diario" size 42 color "#FFD7F1" xalign 0.5

            hbox:
                spacing 12
                xalign 0.5
                textbutton "Académico (checks)" action SetScreenVariable("_tab", "academic")
                textbutton "Social (barras/corazón)" action SetScreenVariable("_tab", "social")

            if _tab == "academic":
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _module_id, _lessons in _checks.items():
                            $ _mod_prog = get_check_progress(_module_id)
                            $ _mod_done, _mod_total = tl_progress_counts(_mod_prog)
                            text "[_module_id.title()]  [_mod_done]/[_mod_total]" size 28 color "#F7E8FF"
                            for _lesson_id, _steps in _lessons.items():
                                $ _lesson_done = sum([1 for _v in _steps.values() if _v])
                                $ _lesson_total = len(_steps)
                                text "  - [_lesson_id]  [_lesson_done]/[_lesson_total]" size 22 color "#DDD0E7"
            else:
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _cid in AFFINITY_CHARACTER_IDS:
                            $ _pts = get_affinity(_cid)
                            $ _rom_enabled = is_romance_enabled(tl_experience_mode, tl_player_gender, _cid)
                            hbox:
                                spacing 12
                                text "[_cid.title()]" size 24 xminimum 160
                                add get_affinity_bar_image(_cid) xsize 220 ysize 30
                                text "[_pts]/10" size 20 color "#FFD7F1"
                                if tl_experience_mode == 1:
                                    text "Romance oculto (Modo 1)" size 16 color "#E8D9F0"
                                elif _rom_enabled:
                                    add get_romance_heart_image(_cid) xsize 38 ysize 38
                                    text "[get_romance(_cid)]/24" size 18 color "#FFB9D5"
                                else:
                                    text "[get_romance_lock_message(tl_experience_mode, tl_player_gender, _cid)]" size 16 color "#FFB9D5"

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

screen tl_library_index_screen():
    tag menu
    modal True

    default _tab = "courses"

    $ bg = tl_asset("images/sakura-sunshine/sakura-sunshine-academy-salon.jpg")
    if bg:
        add bg at tl_soft_focus
    else:
        add "tl_fallback_rose"
    add Solid("#00000088")

    frame:
        xalign 0.5
        yalign 0.5
        xsize 1140
        ysize 650
        background Solid("#151019DE")

        vbox:
            spacing 10
            xalign 0.5
            yalign 0.04

            text "Biblioteca" size 42 color "#FFD7F1" xalign 0.5
            hbox:
                spacing 12
                xalign 0.5
                textbutton "Cursos" action SetScreenVariable("_tab", "courses")
                textbutton "Personajes" action SetScreenVariable("_tab", "characters")

            if _tab == "courses":
                vbox:
                    spacing 8
                    $ _cl = get_check_progress("clases")
                    $ _pr = get_check_progress("practica")
                    $ _ex = get_check_progress("examenes")
                    $ _ac = get_check_progress("actividades")
                    $ _cl_done, _cl_total = tl_progress_counts(_cl)
                    $ _pr_done, _pr_total = tl_progress_counts(_pr)
                    $ _ex_done, _ex_total = tl_progress_counts(_ex)
                    $ _ac_done, _ac_total = tl_progress_counts(_ac)
                    text "Clases · Desbloqueado · [_cl_done]/[_cl_total]" size 24
                    text "Práctica · Desbloqueado · [_pr_done]/[_pr_total]" size 24
                    text "Exámenes · Desbloqueado · [_ex_done]/[_ex_total]" size 24
                    text "Actividades · Desbloqueado · [_ac_done]/[_ac_total]" size 24
            else:
                viewport:
                    draggable True
                    mousewheel True
                    ymaximum 470

                    vbox:
                        spacing 8
                        for _cid in AFFINITY_CHARACTER_IDS:
                            $ _aff = get_affinity(_cid)
                            $ _unlocked = (_aff >= 1)
                            text "[_cid.title()] · {} · Afinidad: [_aff]/10".format("Desbloqueado" if _unlocked else "Bloqueado") size 22

            hbox:
                spacing 14
                xalign 0.5
                textbutton "Volver al hub" action Return("back")

label tl_boot_start:
    $ quick_menu = False
    $ _academic_ensure_store()
    $ _affinity_ensure_store()
    $ _romance_ensure_store()
    call screen tl_main_menu_screen
    if _return == "goto_sakura_gate":
        jump tl_sakura_gate
    jump tl_boot_start

label tl_sakura_gate:
    call screen tl_sakura_gate_screen
    if _return == "register":
        jump tl_player_registration
    if _return == "back":
        jump tl_boot_start
    jump tl_sakura_gate

label tl_player_registration:
    call screen tl_registration_screen
    if _return == "continue":
        $ tl_experience_mode = tl_set_mode_guard(tl_player_gender, tl_experience_mode)
        jump tl_sakura_welcome
    if _return == "back":
        jump tl_sakura_gate
    jump tl_player_registration

label tl_sakura_welcome:
    call screen tl_sakura_welcome_screen
    if _return == "to_hub":
        jump tl_sakura_hub
    jump tl_sakura_welcome

label tl_sakura_hub:
    call screen tl_sakura_hub_screen

    if _return == "go_lessons":
        jump tl_classes_basic_flow

    if _return == "go_practice":
        $ tl_current_module = "Práctica"
        call screen tl_practice_mode_screen
        if _return == "start_practice":
            call typing_lab_start
        jump tl_sakura_hub

    if _return == "go_exams":
        $ tl_current_module = "Exámenes"
        call screen tl_exam_entry_screen
        if _return == "start_exam":
            $ typing_lab_selected_mode = "phrases"
            call typing_lab_start
            $ _exam_score = int(typing_lab_state.get("total_score", 0) if isinstance(typing_lab_state, dict) else 0)
            if _exam_score >= 50:
                $ set_check("examenes", "exam_1", "attempt_1", True)
                "Examen aprobado. Puntaje: [_exam_score]"
            else:
                "Examen no aprobado. Puntaje: [_exam_score] (mínimo 50)."
        jump tl_sakura_hub

    if _return == "go_activities":
        $ tl_current_module = "Actividades"
        call screen tl_activities_quest_screen
        jump tl_sakura_hub

    if _return == "go_diary":
        $ tl_current_module = "Diario"
        call screen tl_diary_tabs_screen
        jump tl_sakura_hub

    if _return == "go_library":
        $ tl_current_module = "Biblioteca"
        call screen tl_library_index_screen
        jump tl_sakura_hub

    if _return == "go_place_entrance":
        $ tl_current_module = "Lugar · Entrada"
        call screen tl_place_placeholder_screen("Entrada")
        jump tl_sakura_hub

    if _return == "go_place_patio":
        $ tl_current_module = "Lugar · Patio"
        call screen tl_place_placeholder_screen("Patio")
        jump tl_sakura_hub

    if _return == "go_qa_tech":
        $ tl_current_module = "QA técnico"
        call screen tl_qa_tech_screen
        jump tl_sakura_hub

    if _return == "to_main":
        jump tl_boot_start

    jump tl_sakura_hub
