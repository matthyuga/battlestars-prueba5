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
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Dominar posición base y retorno a fila central.",
                    "steps": [
                        {
                            "title": "Fila central: punto de control",
                            "points": [
                                "Ubica dedos en A-S-D-F y J-K-L-Ñ.",
                                "Relaja manos y evita rigidez.",
                                "Vuelve siempre al punto base tras cada pulsación.",
                            ],
                            "teacher_line": "Si dominas la fila central, todo el teclado se vuelve más predecible.",
                        },
                        {
                            "title": "Memoria muscular inicial",
                            "points": [
                                "Repite secuencias cortas sin mirar.",
                                "Mantén ritmo estable, no velocidad máxima.",
                                "Corrige postura antes de corregir tiempo.",
                            ],
                            "teacher_line": "La consistencia vale más que un intento rápido e inestable.",
                        },
                    ],
                },
                "1_3_results": {
                    "id": "1_3_results",
                    "title": "1.3 Ver resultados",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Interpretar precisión y errores para mejorar técnica.",
                    "steps": [
                        {
                            "title": "Leer resultados con criterio",
                            "points": [
                                "Prioriza precisión sobre velocidad.",
                                "Observa dónde se concentran los errores.",
                                "Usa resultados para ajustar postura y ritmo.",
                            ],
                            "teacher_line": "Los resultados no son castigo; son mapa de mejora.",
                        },
                        {
                            "title": "Plan de ajuste",
                            "points": [
                                "Si hay muchos errores: baja ritmo.",
                                "Si hay tensión: revisa hombros y muñecas.",
                                "Si dudas de teclas: vuelve a la base.",
                            ],
                            "teacher_line": "Un buen análisis reduce errores futuros y acelera aprendizaje.",
                        },
                    ],
                },
                "1_4_keys_exercise": {
                    "id": "1_4_keys_exercise",
                    "title": "1.4 Ejercicio teclas",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Consolidar precisión en teclas individuales.",
                    "steps": [
                        {
                            "title": "Ejercicio por teclas",
                            "points": [
                                "Pulsa una tecla objetivo y regresa al centro.",
                                "Mantén dedos cercanos al teclado.",
                                "No sacrifiques exactitud por rapidez.",
                            ],
                            "teacher_line": "Cada tecla bien ejecutada refuerza tu confianza.",
                        },
                        {
                            "title": "Control de movimiento",
                            "points": [
                                "Mínimo desplazamiento por dedo.",
                                "Pulso suave, sin golpear fuerte.",
                                "Respiración constante durante práctica.",
                            ],
                            "teacher_line": "Control fino de movimiento = menos fatiga y más precisión.",
                        },
                    ],
                },
                "1_5_exam_help": {
                    "id": "1_5_exam_help",
                    "title": "1.5 Ayuda exámenes",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Preparar criterios de evaluación para examen.",
                    "steps": [
                        {
                            "title": "Cómo afrontar el examen",
                            "points": [
                                "Empieza en ritmo cómodo.",
                                "Concéntrate en errores repetidos.",
                                "Mantén postura incluso con presión.",
                            ],
                            "teacher_line": "En examen, estabilidad mental y técnica ganan al apuro.",
                        },
                        {
                            "title": "Antes de iniciar",
                            "points": [
                                "Revisa posición de manos.",
                                "Define objetivo: precisión primero.",
                                "Respira profundo y comienza.",
                            ],
                            "teacher_line": "Entrar con método reduce el estrés y mejora el resultado.",
                        },
                    ],
                },
                "1_6_words_exercise": {
                    "id": "1_6_words_exercise",
                    "title": "1.6 Ejercicio palabras",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Aplicar técnica en palabras completas.",
                    "steps": [
                        {
                            "title": "De teclas a palabras",
                            "points": [
                                "Agrupa letras sin perder ritmo.",
                                "Mantén ojos en pantalla.",
                                "Corrige de inmediato errores de digitación.",
                            ],
                            "teacher_line": "Las palabras conectan técnica con lectura real.",
                        },
                        {
                            "title": "Fluidez inicial",
                            "points": [
                                "No cortes el ritmo por una sola falla.",
                                "Recupera postura tras cada palabra.",
                                "Busca consistencia entre intentos.",
                            ],
                            "teacher_line": "Fluidez no es correr: es sostener calidad en cada palabra.",
                        },
                    ],
                },
                "1_7_phrases_exercise": {
                    "id": "1_7_phrases_exercise",
                    "title": "1.7 Ejercicio frases",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Integrar precisión y ritmo en frases largas.",
                    "steps": [
                        {
                            "title": "Trabajo por frases",
                            "points": [
                                "Mantén continuidad entre palabras.",
                                "Cuida signos y espacios.",
                                "Evita tensión al aumentar longitud.",
                            ],
                            "teacher_line": "Las frases evalúan tu control completo, no solo reflejos.",
                        },
                        {
                            "title": "Cierre de la lección 1",
                            "points": [
                                "Revisa precisión total de la sesión.",
                                "Detecta patrón principal de error.",
                                "Define foco para la siguiente lección.",
                            ],
                            "teacher_line": "Excelente avance: ya tienes base sólida para progresar.",
                        },
                    ],
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
