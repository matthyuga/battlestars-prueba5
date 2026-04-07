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
                    "title": "Lección 2 — Fila central",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Aprender posición base de manos en fila central y cierre previo al ejercicio.",
                    "steps": [
                        {
                            "title": "Presentación de la lección",
                            "points_haru": [
                                "En esta lección aprenderás la fila central.",
                                "Aquí comenzaremos con la posición base de las manos.",
                                "Esta fila será tu referencia para escribir con orden y precisión.",
                            ],
                            "points_misaki": [
                                "En esta lección aprenderás la fila central.",
                                "Esta es la posición de partida para escribir con todos los dedos.",
                                "Con práctica, se volverá una referencia natural para tus manos.",
                            ],
                            "teacher_lines": {
                                "haru": "Vamos a fijar bien esta base. Si la fila central queda clara, el resto del teclado se entiende mucho mejor.",
                                "misaki": "Empezaremos por la base, con calma. Cuando la fila central se vuelve familiar, escribir resulta mucho más cómodo.",
                            },
                        },
                        {
                            "title": "Mano izquierda sobre la fila central",
                            "points_haru": [
                                "Comenzando con el meñique, sitúa los dedos de tu mano izquierda sobre el teclado.",
                                "Coloca los dedos en A, S, D y F.",
                                "Cada dedo debe descansar en su tecla correspondiente.",
                            ],
                            "points_misaki": [
                                "Comenzando con el meñique, sitúa los dedos de tu mano izquierda sobre el teclado.",
                                "Apoya los dedos en A, S, D y F.",
                                "Procura colocarlos con suavidad, sin tensión.",
                            ],
                            "teacher_lines": {
                                "haru": "No hace falta apurarse. Primero ubica bien cada dedo y deja la mano estable sobre la fila central.",
                                "misaki": "Solo acomoda la mano izquierda y tómate un momento para reconocer la posición. Lo importante ahora es ubicarse bien.",
                            },
                        },
                        {
                            "title": "Mano derecha sobre la fila central",
                            "points_haru": [
                                "Comenzando con el índice, sitúa los dedos de tu mano derecha sobre el teclado.",
                                "Coloca los dedos en J, K, L y Ñ.",
                                "Mantén la mano relajada y alineada con la fila central.",
                            ],
                            "points_misaki": [
                                "Comenzando con el índice, sitúa los dedos de tu mano derecha sobre el teclado.",
                                "Apoya los dedos en J, K, L y Ñ.",
                                "Intenta que la mano quede cómoda y sin rigidez.",
                            ],
                            "teacher_lines": {
                                "haru": "Ahora completa la posición base con la mano derecha. Ambas manos deben quedar listas para volver siempre a esta fila.",
                                "misaki": "Muy bien. Cuando las dos manos encuentran su lugar, el teclado empieza a sentirse mucho más claro.",
                            },
                        },
                        {
                            "title": "Pulgares en la barra espaciadora",
                            "points_haru": [
                                "Deja tus pulgares descansar sobre la tecla Espacio.",
                                "Los pulgares deben quedar preparados para pulsarla sin mover el resto de la posición base.",
                            ],
                            "points_misaki": [
                                "Deja tus pulgares descansar sobre la tecla Espacio.",
                                "Apóyalos de forma natural, sin presionar más de lo necesario.",
                            ],
                            "teacher_lines": {
                                "haru": "La barra espaciadora también forma parte de la postura correcta. Deja los pulgares listos desde el principio.",
                                "misaki": "Deja los pulgares sobre Espacio con suavidad. Esa pequeña costumbre también ayuda a que la posición se vuelva estable.",
                            },
                        },
                        {
                            "title": "Posición de partida completa",
                            "points_haru": [
                                "Así quedan tus manos en la posición de partida.",
                                "La fila central será tu punto de referencia.",
                                "Después de pulsar una tecla, los dedos deben regresar aquí.",
                            ],
                            "points_misaki": [
                                "Así quedan tus manos en la posición de partida.",
                                "Esta será tu base para comenzar a escribir.",
                                "Con el tiempo, tus manos volverán aquí casi sin pensarlo.",
                            ],
                            "teacher_lines": {
                                "haru": "Esta es la posición que debes recordar. Cada movimiento parte de aquí y aquí debe terminar.",
                                "misaki": "Quédate un instante con esta imagen en mente. Esta posición será tu apoyo durante toda la práctica.",
                            },
                        },
                        {
                            "title": "Primer ejemplo: pulsar una letra",
                            "points_haru": [
                                "Ahora pulsa A con el meñique izquierdo.",
                                "Haz un movimiento corto y vuelve después a la posición base.",
                                "No levantes la mano más de lo necesario.",
                            ],
                            "points_misaki": [
                                "Ahora pulsa A con el meñique izquierdo.",
                                "Hazlo con un movimiento simple y vuelve luego a la posición inicial.",
                                "No necesitas fuerza, solo precisión.",
                            ],
                            "teacher_lines": {
                                "haru": "Pulsa y regresa. Ese detalle es importante: tocar la tecla y volver al punto de partida.",
                                "misaki": "Prueba despacio. Lo importante es que el dedo encuentre la tecla y luego vuelva a su lugar.",
                            },
                        },
                        {
                            "title": "Uso del pulgar para espacio",
                            "points_haru": [
                                "Utiliza siempre el mismo pulgar para pulsar Espacio.",
                                "Mantener esa costumbre ayuda a dar continuidad al movimiento y evita confusiones innecesarias.",
                            ],
                            "points_misaki": [
                                "Utiliza siempre el mismo pulgar para pulsar Espacio.",
                                "Repetir el mismo gesto ayuda a que la mano se acostumbre y mantenga el orden.",
                            ],
                            "teacher_lines": {
                                "haru": "La regularidad también se practica. Si eliges un mismo pulgar para Espacio, el movimiento se vuelve más consistente.",
                                "misaki": "Ese pequeño hábito te va a ayudar más de lo que parece. Cuando repites el mismo movimiento, todo se vuelve más natural.",
                            },
                        },
                        {
                            "title": "Cierre antes del ejercicio",
                            "points_haru": [
                                "Muy bien. Ya puedes comenzar el primer ejercicio.",
                                "En esta práctica trabajarás la posición de la fila central y el movimiento básico de los dedos.",
                                "Concéntrate en acertar y mantener la postura.",
                            ],
                            "points_misaki": [
                                "Muy bien. Ya puedes comenzar el primer ejercicio.",
                                "En esta práctica empezarás a reconocer la fila central y a mover los dedos con más seguridad.",
                                "Ve paso a paso y mantén la calma.",
                            ],
                            "teacher_lines": {
                                "haru": "Ahora toca practicar. Hazlo con atención y deja que la repetición empiece a fijar el recorrido de tus dedos.",
                                "misaki": "Ya estás listo para empezar. No hace falta correr; con práctica tranquila irás notando el avance.",
                            },
                        },
                    ],
                },
                "1_3_results": {
                    "id": "1_3_results",
                    "title": "Lección 3: Resultados de escritura",
                    "state": "real",
                    "scene_type": "lesson_dialogue",
                    "objective": "Entender e interpretar resultados de práctica para mejorar técnica.",
                    "steps": [
                        {
                            "title": "Resultados de escritura",
                            "points_haru": [
                                "Resultados de escritura",
                                "Después de cada ejercicio, la academia registrará tu rendimiento para que puedas ver cómo vas avanzando.",
                                "En cada práctica podrás revisar estos datos:",
                                "Tiempo usado",
                                "Velocidad",
                                "Porcentaje de acierto",
                                "Rendimiento ajustado",
                                "Teclas que te dieron más dificultad",
                                "En las siguientes pantallas veremos qué significa cada uno.",
                            ],
                            "points_misaki": [
                                "Resultados de escritura",
                                "Cada vez que completes un ejercicio, la academia guardará un pequeño resumen de tu práctica.",
                                "En él podrás ver:",
                                "Tiempo usado",
                                "Velocidad",
                                "Porcentaje de acierto",
                                "Rendimiento ajustado",
                                "Teclas que te costaron más",
                                "Estos datos te ayudarán a notar tu avance poco a poco.",
                            ],
                            "teacher_lines": {
                                "haru": "No se trata solo de terminar un ejercicio. También conviene entender qué estás haciendo bien y qué parte todavía necesita práctica.",
                                "misaki": "A veces el progreso no se siente enseguida, pero al mirar tus resultados puedes darte cuenta de cuánto has ido mejorando.",
                            },
                        },
                        {
                            "title": "Velocidad de escritura",
                            "points_haru": [
                                "Velocidad de escritura",
                                "La velocidad indica cuántas letras o palabras puedes escribir en un tiempo determinado.",
                                "Es una medida útil para seguir tu progreso, pero no conviene mirarla de forma aislada. Escribir rápido sirve cuando el movimiento se mantiene claro y controlado.",
                                "Con la práctica, la velocidad suele mejorar de manera gradual.",
                            ],
                            "points_misaki": [
                                "Velocidad de escritura",
                                "La velocidad muestra cuántas letras o palabras puedes escribir en un cierto tiempo.",
                                "Es una referencia útil para comparar tu avance entre una práctica y otra. Aun así, no conviene obsesionarse con ella desde el principio.",
                                "La velocidad crece mejor cuando las manos ya se sienten cómodas con el teclado.",
                            ],
                            "teacher_lines": {
                                "haru": "Al principio, este valor solo te da una referencia. Lo importante es que la rapidez aparezca junto con una escritura estable.",
                                "misaki": "No hace falta perseguir este número todo el tiempo. Cuando escribes con más seguridad, la velocidad suele subir por sí sola.",
                            },
                        },
                        {
                            "title": "Velocidad bruta y rendimiento ajustado",
                            "points_haru": [
                                "Velocidad bruta y rendimiento ajustado",
                                "La velocidad bruta muestra el ritmo al que pulsaste las teclas durante el ejercicio.",
                                "El rendimiento ajustado tiene en cuenta los errores cometidos. Por eso ofrece una visión más real del resultado final.",
                                "Ambos datos son útiles: uno muestra el ritmo, el otro muestra cuánto de ese ritmo fue realmente aprovechable.",
                            ],
                            "points_misaki": [
                                "Velocidad bruta y rendimiento ajustado",
                                "La velocidad bruta refleja el ritmo general al pulsar las teclas.",
                                "El rendimiento ajustado considera también los errores, así que muestra con más claridad cómo fue realmente el ejercicio.",
                                "Por eso ambos valores se complementan y ayudan a leer mejor el resultado.",
                            ],
                            "teacher_lines": {
                                "haru": "Si la velocidad bruta es alta pero el ajuste baja mucho, entonces todavía falta precisión. Por eso conviene mirar ambas cifras juntas.",
                                "misaki": "Puedes verlo así: uno te muestra cuánto te moviste, y el otro cuánto de ese movimiento salió bien.",
                            },
                        },
                        {
                            "title": "Porcentaje de acierto",
                            "points_haru": [
                                "Porcentaje de acierto",
                                "El porcentaje de acierto muestra cuántas teclas pulsaste correctamente en relación con el total del ejercicio.",
                                "Un valor alto indica que mantuviste buen control sobre los movimientos.",
                                "Un valor bajo señala que todavía hay teclas o recorridos que necesitan más atención.",
                                "Este dato es clave en las primeras etapas del aprendizaje.",
                            ],
                            "points_misaki": [
                                "Porcentaje de acierto",
                                "El porcentaje de acierto señala qué parte del ejercicio resolviste correctamente.",
                                "Cuanto más alto sea, más control estás teniendo sobre las teclas y los recorridos de tus dedos.",
                                "En las primeras lecciones, este valor suele ser una referencia muy importante para saber si te estás adaptando bien.",
                            ],
                            "teacher_lines": {
                                "haru": "En esta fase, el acierto dice más que la rapidez. Si primero escribes bien, después podrás escribir mejor y más suelto.",
                                "misaki": "Si tu acierto mejora, ya estás avanzando, aunque todavía no te sientas rápido. La confianza empieza por escribir con cuidado.",
                            },
                        },
                        {
                            "title": "Teclas con dificultad",
                            "points_haru": [
                                "Teclas con dificultad",
                                "La academia también puede señalar qué letras o teclas te costaron más durante el ejercicio.",
                                "Eso te permite detectar:",
                                "movimientos poco firmes",
                                "confusiones entre dedos",
                                "zonas del teclado que todavía no se sienten naturales",
                                "Reconocer esas dificultades ayuda a practicar con más intención.",
                            ],
                            "points_misaki": [
                                "Teclas con dificultad",
                                "Después de practicar, la academia puede mostrarte qué teclas se te hicieron más difíciles.",
                                "Eso sirve para descubrir:",
                                "qué movimientos todavía te cuestan",
                                "qué dedos necesitan más práctica",
                                "qué letras conviene repasar con más calma",
                                "Observar esas pequeñas trabas ayuda a seguir mejor.",
                            ],
                            "teacher_lines": {
                                "haru": "No veas esas teclas como un problema, sino como una guía. Si sabes dónde fallas, sabes exactamente dónde conviene insistir.",
                                "misaki": "Todos tenemos teclas que tardan un poco más en salir bien. Lo bueno es que, cuando las identificas, ya sabes dónde poner más atención.",
                            },
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
