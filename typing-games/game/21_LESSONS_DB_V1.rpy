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
                            "title": "¿Qué es la mecanografía?",
                            "points_haru": [
                                "La mecanografía es la técnica de escribir usando todos los dedos y sin depender de mirar cada tecla.",
                                "Escribir mirando letra por letra corta el ritmo y vuelve más lento el movimiento.",
                                "Con posiciones fijas y recorridos concretos, escribir se vuelve más seguro y con menos esfuerzo.",
                                "Beneficios: mayor precisión, menos dependencia de mirar el teclado, mejor postura y más fluidez.",
                            ],
                            "points_misaki": [
                                "La mecanografía es una forma de escribir usando todos los dedos sin buscar cada tecla con la vista.",
                                "Mirar el teclado a cada momento es normal al inicio, pero corta el ritmo y aumenta el esfuerzo.",
                                "Con práctica, las manos reconocen el teclado poco a poco y aparece una sensación más natural.",
                                "Beneficios: más precisión, menos dependencia visual y mayor comodidad para estudiar o trabajar.",
                            ],
                            "teacher_lines": {
                                "haru": "Vamos a empezar por la base. Si tus manos entienden el teclado, escribir se vuelve mucho más estable.",
                                "misaki": "Iremos despacio. Cuando entiendas la base, escribir empezará a sentirse mucho más natural.",
                            },
                        },
                        {
                            "title": "Posición inicial de los dedos",
                            "points_haru": [
                                "La fila central es el punto de partida: mano izquierda A S D F, mano derecha J K L Ñ, pulgares en barra espaciadora.",
                                "Cada dedo atiende un grupo cercano de teclas; al principio se piensa, luego se vuelve natural.",
                                "Repetir bien la base hace que las manos reconozcan el teclado por costumbre.",
                            ],
                            "points_misaki": [
                                "La fila central es donde descansan los dedos al comenzar: A S D F / J K L Ñ / pulgares en espacio.",
                                "Cada dedo tiene un grupo pequeño de teclas y la práctica vuelve familiar ese recorrido.",
                                "No es solo un ejercicio del momento: es una habilidad que te acompaña siempre.",
                            ],
                            "teacher_lines": {
                                "haru": "No intentes memorizar todo de golpe. Primero ubica la fila central y deja que la repetición haga su trabajo.",
                                "misaki": "No te preocupes si al inicio parece mucho. En cuanto repitas unas cuantas veces, la posición se vuelve más familiar.",
                            },
                        },
                        {
                            "title": "Teclas guía y ejemplo de movimiento",
                            "points_haru": [
                                "Las teclas F y J tienen relieve: son referencias táctiles para volver a la fila central sin mirar.",
                                "Ejemplo: H con índice derecho y R con índice izquierdo.",
                                "Después de cada pulsación, el dedo regresa a su posición inicial.",
                            ],
                            "points_misaki": [
                                "F y J tienen un pequeño relieve que ayuda a encontrar la fila central por tacto.",
                                "Ejemplo: M con índice derecho y S con anular izquierdo.",
                                "Después de pulsar, el dedo vuelve a su posición base.",
                            ],
                            "teacher_lines": {
                                "haru": "Busca siempre la referencia en F y J. Desde ahí, el movimiento sale con más orden y menos duda.",
                                "misaki": "Si encuentras F y J con el tacto, te será mucho más fácil acomodarte sin perderte.",
                            },
                        },
                        {
                            "title": "Ayudas para aprender mejor",
                            "points_haru": [
                                "Mantén los ojos en la pantalla y evita apoyar el peso en las muñecas.",
                                "Da prioridad al acierto antes que a la rapidez.",
                                "Practica con ritmo cómodo y constante.",
                                "La memoria de los dedos se construye con repetición correcta y calma.",
                            ],
                            "points_misaki": [
                                "Mira la pantalla siempre que puedas y mantén muñecas levantadas y relajadas.",
                                "Concéntrate en acertar y practica con ritmo tranquilo y parejo.",
                                "Con el tiempo, las manos empiezan a recorrer palabras casi por costumbre.",
                            ],
                            "teacher_lines": {
                                "haru": "Cuando el movimiento se repite bien, deja de sentirse forzado. Ahí es cuando empieza a volverse automático.",
                                "misaki": "Tus manos también aprenden. Al principio lo notarás poco, pero después cada movimiento sale con más confianza.",
                            },
                        },
                        {
                            "title": "Últimas ayudas antes de comenzar",
                            "points_haru": [
                                "Mantén postura relajada y haz pausas breves entre ejercicios.",
                                "Si notas tensión en manos u hombros, detente un momento.",
                                "Descansar también forma parte del aprendizaje.",
                                "Éxitos en tu aprendizaje: paso a paso notarás el avance.",
                            ],
                            "points_misaki": [
                                "Mantén el cuerpo relajado y descansa entre ejercicios.",
                                "Si sientes cansancio, pausa la práctica y retoma con calma.",
                                "No hace falta hacerlo perfecto en la primera sesión: importa la constancia.",
                                "Mucho ánimo: con paciencia y práctica el cambio se nota.",
                            ],
                            "teacher_lines": {
                                "haru": "Trabajaremos con orden y sin apuro. Si mantienes la constancia, los resultados llegan.",
                                "misaki": "Hazlo con calma. Si practicas de forma constante, vas a sorprenderte de lo mucho que puedes avanzar.",
                            },
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
                            "points_haru": [
                                "Coloca tus dedos en A-S-D-F y J-K-L-Ñ antes de iniciar cada serie.",
                                "Mantén hombros sueltos y muñecas sin tensión para conservar precisión.",
                                "Tras cada pulsación, vuelve a la fila central para no perder referencia.",
                            ],
                            "points_misaki": [
                                "Empieza siempre desde A-S-D-F y J-K-L-Ñ para que las manos tengan una base clara.",
                                "Respira y relaja brazos y muñecas: escribir cómodo ayuda a acertar más.",
                                "Después de cada tecla, regresa al centro; ese hábito evita que te desordenen los dedos.",
                            ],
                            "teacher_lines": {
                                "haru": "La fila central es tu ancla. Si vuelves siempre ahí, vas a cometer menos errores.",
                                "misaki": "Piensa en la fila central como tu casa: cada dedo sale y vuelve con calma.",
                            },
                        },
                        {
                            "title": "Memoria muscular inicial",
                            "points_haru": [
                                "Practica secuencias breves sin mirar el teclado para activar memoria táctil.",
                                "Sostén un ritmo parejo: primero control, después velocidad.",
                                "Si aparece tensión, corrige postura antes de seguir repitiendo.",
                            ],
                            "points_misaki": [
                                "Haz repeticiones cortas y tranquilas, enfocándote en sentir el recorrido de cada dedo.",
                                "No busques correr: un ritmo estable enseña más que una ráfaga con errores.",
                                "Cuando notes rigidez, suelta manos y retoma con técnica limpia.",
                            ],
                            "teacher_lines": {
                                "haru": "Tu objetivo aquí es consistencia. Si cada intento se parece al anterior, estás avanzando.",
                                "misaki": "Vas muy bien si mantienes un ritmo parejo. La velocidad llega sola después.",
                            },
                        },
                        {
                            "title": "Siguiente paso: ejercicio guiado",
                            "points_haru": [
                                "Con la base lista, en el siguiente tramo pasarás a un ejercicio aplicado (placeholder).",
                                "Mantén la misma técnica: regreso a fila central y control del movimiento.",
                            ],
                            "points_misaki": [
                                "Ahora iremos al ejercicio aplicado (placeholder) para practicar esta base en contexto.",
                                "Llévate la misma idea: calma, precisión y vuelta al centro en cada tecla.",
                            ],
                            "teacher_lines": {
                                "haru": "Perfecto. Cerramos teoría y pasamos al ejercicio placeholder.",
                                "misaki": "Genial. Ya tienes la base, continuemos con el ejercicio placeholder.",
                            },
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
