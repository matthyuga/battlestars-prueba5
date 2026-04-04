# Typing Legends - Paso 1
# Blueprint Ren'Py para mapear la Lección 1 de Typing Master (SP7QWERT)
# y presentarla con skin dual de academias (Epic / Sakura).

init -20 python:
    # IDs estables para no acoplar UI con archivos externos.
    TL_EVENT_KIND_INTRO_HTML = "intro_html"
    TL_EVENT_KIND_KEYINTRO = "keyintro"
    TL_EVENT_KIND_KEYDRILL = "keydrill"
    TL_EVENT_KIND_WORDDRILL = "worddrill"
    TL_EVENT_KIND_PARAGRAPH = "paragraph"

    # Catálogo de pantallas intro de la subclase 1.1
    TL_SP7_LESSON1_INTRO_SLIDES = [
        "msg_spa_sp7qwert_1_1_1.htm",
        "msg_spa_sp7qwert_1_1_2.htm",
        "msg_spa_sp7qwert_1_1_3.htm",
        "msg_spa_sp7qwert_1_1_4.htm",
        "msg_spa_sp7qwert_1_1_5.htm",
    ]

    TL_SP7_LESSON1_RESULTS_SLIDES = [
        "msg_spa_sp7qwert_1_2_1.htm",
        "msg_spa_sp7qwert_1_2_3.htm",
        "msg_spa_sp7qwert_1_2_4.htm",
        "msg_spa_sp7qwert_1_2_2.htm",
        "msg_spa_sp7qwert_1_2_5.htm",
    ]

    TL_SP7_LESSON1_BLUEPRINT = {
        "course_id": "sp7qwert",
        "chapter_id": "1",
        "chapter_name": "La fila central",
        "estimated_total_minutes": 22,
        "subclasses": [
            {
                "id": "1.1",
                "name": "Introducción",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_INTRO_HTML,
                        "slides": list(TL_SP7_LESSON1_INTRO_SLIDES),
                    },
                ],
            },
            {
                "id": "1.2",
                "name": "Teclas de la Fila Central",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_KEYINTRO,
                        "files": [
                            "sp7qwert01021keyintro7141.txt",
                            "sp7qwert01021keyintro.txt",
                            "sp7qwert01023keyintro.txt",
                            "sp7qwert01024keyintro.txt",
                            "sp7qwert01025keyintro3433.txt",
                            "sp7qwert01022keyintro4155.txt",
                            "sp7qwert01028keyintro.txt",
                            "sp7qwert01029keyintro.txt",
                        ],
                    },
                    {
                        "kind": TL_EVENT_KIND_KEYDRILL,
                        "files": ["sp7qwert01013key2.txt"],
                    },
                ],
            },
            {
                "id": "1.3",
                "name": "Ver resultados",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_INTRO_HTML,
                        "slides": list(TL_SP7_LESSON1_RESULTS_SLIDES),
                    },
                ],
            },
            {
                "id": "1.4",
                "name": "Ejercicio de Teclas",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_KEYDRILL,
                        "files": ["sp7qwert01031key2.txt"],
                    },
                ],
            },
            {
                "id": "1.5",
                "name": "Ayuda: Exámenes",
                "minutes": 0,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_INTRO_HTML,
                        "slides": ["msg_spa_sp7qwert_1_6_1.htm"],
                    },
                ],
            },
            {
                "id": "1.6",
                "name": "Ejercicio de Palabras",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_INTRO_HTML,
                        "slides": ["sp7qwert01061htmlmessage.htm"],
                    },
                    {
                        "kind": TL_EVENT_KIND_WORDDRILL,
                        "files": ["sp7qwert01031word2.txt"],
                    },
                ],
            },
            {
                "id": "1.7",
                "name": "Ejercicio de Párrafos",
                "minutes": 3,
                "events": [
                    {
                        "kind": TL_EVENT_KIND_INTRO_HTML,
                        "slides": ["msg_spa_sp7qwert_1_7_1.htm"],
                    },
                    {
                        "kind": TL_EVENT_KIND_PARAGRAPH,
                        "files": ["sp7qwert01052text2.txt"],
                    },
                ],
            },
        ],
    }

    TL_ACADEMY_SKIN = {
        "epic_spell": {
            "module_labels": {
                "course": "Academia",
                "satellite": "Forja",
                "review": "Práctica",
                "exams": "Pruebas",
                "games": "Arena",
                "stats": "Crónica",
                "settings": "Codex",
                "info": "Codex",
            },
            "lesson_title_prefix": "Grimorio",
        },
        "sakura_sunshine": {
            "module_labels": {
                "course": "Clases",
                "satellite": "Práctica Guiada",
                "review": "Repaso",
                "exams": "Exámenes",
                "games": "Actividades",
                "stats": "Diario",
                "settings": "Biblioteca",
                "info": "Biblioteca",
            },
            "lesson_title_prefix": "Lección",
        },
    }

    def tl_get_lesson1_blueprint(academy="epic_spell"):
        """Devuelve un dict listo para UI de Ren'Py con skin por academia."""
        skin = TL_ACADEMY_SKIN.get(academy, TL_ACADEMY_SKIN["epic_spell"])
        data = dict(TL_SP7_LESSON1_BLUEPRINT)
        data["academy"] = academy
        data["module_labels"] = dict(skin["module_labels"])
        data["display_lesson_title"] = "{} 1: {}".format(
            skin["lesson_title_prefix"],
            TL_SP7_LESSON1_BLUEPRINT["chapter_name"],
        )
        return data

label typing_legends_lesson1_blueprint_preview:
    $ bp = tl_get_lesson1_blueprint("epic_spell")
    "[bp['display_lesson_title']]"
    python:
        for s in bp["subclasses"]:
            renpy.say(None, "{} {} ({} min)".format(s["id"], s["name"], s["minutes"]))
    return
