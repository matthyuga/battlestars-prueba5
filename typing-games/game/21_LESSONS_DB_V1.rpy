# ===========================================================
# 21_LESSONS_DB_V1.rpy
# Capa de Data (Fase 1B): base declarativa de lecciones
# ===========================================================

init -125 python:
    LESSON_DB_V1 = {
        "lesson_1": {
            "id": "lesson_1",
            "title": "Lección 1 · Fila central",
            "module": "clases",
            "enabled": True,
            "sublessons": {
                "1_1_intro": {
                    "id": "1_1_intro",
                    "title": "1.1 Introducción",
                    "state": "real",
                    "scene_type": "intro_dialogue",
                    "objective": "Introducir postura, precisión y ritmo base.",
                    "steps": [
                        {
                            "title": "Introducción a la escritura al tacto",
                            "points": [
                                "Escribir sin mirar el teclado.",
                                "Construir memoria muscular paso a paso.",
                                "Priorizar precisión antes que velocidad.",
                            ],
                            "teacher_line": "Comenzamos con base sólida: postura, ritmo y control.",
                        },
                        {
                            "title": "Postura inicial",
                            "points": [
                                "Espalda recta y hombros relajados.",
                                "Dedos base en A S D F y J K L Ñ.",
                                "Pulgares preparados para la barra espaciadora.",
                            ],
                            "teacher_line": "Una buena postura evita fatiga y mejora tu estabilidad al teclear.",
                        },
                        {
                            "title": "Técnica de práctica",
                            "points": [
                                "Pulsa suave y vuelve al punto base.",
                                "Mantén respiración y ritmo constante.",
                                "No aceleres hasta dominar los movimientos.",
                            ],
                            "teacher_line": "Si mantienes ritmo, cada repetición te hará más preciso.",
                        },
                        {
                            "title": "Errores comunes",
                            "points": [
                                "Mirar el teclado en cada pulsación.",
                                "Tensionar manos, brazos u hombros.",
                                "Golpear teclas con fuerza innecesaria.",
                            ],
                            "teacher_line": "Los errores son parte del proceso; lo importante es corregir con calma.",
                        },
                        {
                            "title": "Listo para empezar",
                            "points": [
                                "Objetivo inmediato: constancia y exactitud.",
                                "Haz pausas breves durante la práctica.",
                                "Al final revisaremos avance y hábitos.",
                            ],
                            "teacher_line": "Excelente, ya estás listo. Avancemos a la primera práctica guiada.",
                        },
                    ],
                },
                "1_2_home_row": {
                    "id": "1_2_home_row",
                    "title": "1.2 Fila central",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
                "1_3_results": {
                    "id": "1_3_results",
                    "title": "1.3 Ver resultados",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
                "1_4_keys_exercise": {
                    "id": "1_4_keys_exercise",
                    "title": "1.4 Ejercicio teclas",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
                "1_5_exam_help": {
                    "id": "1_5_exam_help",
                    "title": "1.5 Ayuda exámenes",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
                "1_6_words_exercise": {
                    "id": "1_6_words_exercise",
                    "title": "1.6 Ejercicio palabras",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
                "1_7_phrases_exercise": {
                    "id": "1_7_phrases_exercise",
                    "title": "1.7 Ejercicio frases",
                    "state": "placeholder",
                    "scene_type": "placeholder",
                    "objective": "Placeholder temporal para implementación manual.",
                    "steps": [],
                },
            },
        },
    }

    LESSON_DB_ORDER_V1 = {
        "lesson_1": [
            "1_1_intro",
            "1_2_home_row",
            "1_3_results",
            "1_4_keys_exercise",
            "1_5_exam_help",
            "1_6_words_exercise",
            "1_7_phrases_exercise",
        ],
    }

    def lesson_db_get_lesson(lesson_id):
        lid = str(lesson_id or "").strip().lower()
        return dict(LESSON_DB_V1.get(lid, {}))

    def lesson_db_get_sublesson(lesson_id, sublesson_id):
        lid = str(lesson_id or "").strip().lower()
        sid = str(sublesson_id or "").strip().lower()
        lesson = LESSON_DB_V1.get(lid, {})
        sub = lesson.get("sublessons", {}).get(sid, {})
        return dict(sub) if isinstance(sub, dict) else {}

    def lesson_db_list_sublessons(lesson_id):
        lid = str(lesson_id or "").strip().lower()
        ids = LESSON_DB_ORDER_V1.get(lid, [])
        return list(ids)

