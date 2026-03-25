# =================================
# RUTA ROMÁNTICA
# =================================

# --- Acto 1: El Encuentro --->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
label harribel_romantica:

    scene hollow1 with dissolve  
    
    show h2 at center with dissolve
    Harribel "…¿Belleza? Palabras vacías, dichas por alguien que no comprende dónde está."
    hide h2 with dissolve  

    # Primeras respuestas del jugador
    menu:
        "La verdad… tu presencia me intimida, pero aún así no puedo apartar los ojos de ti.":
            # $ affection_harribel += 1
            jump harribel_romantica_1

        "Si debo morir aquí, prefiero hacerlo contemplando algo tan hermoso.":
            # $ affection_harribel += 2
            jump harribel_romantica_2


label harribel_romantica_1:
    # Aquí continúa el Acto 1 versión "sincera"
    # Ejemplo:
    scene hollow1 with dissolve
    show h2 at center with dissolve
    Harribel "Tienes osadía... veremos si sobrevives a tus propias palabras."
    jump harribel_romantica_act2


label harribel_romantica_2:
    scene hollow1 with dissolve
    show h2 at center with dissolve
    # Aquí continúa el Acto 1 versión "arriesgada"
    Harribel "Insensato. Tu lengua es más rápida que tu instinto de supervivencia."
    jump harribel_romantica_act2


# --- Acto 2: Las Pruebas --->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
label harribel_romantica_act2:

    scene hollow2 with dissolve
    "Harribel, contra toda expectativa, decide no acabar contigo."
    show h2 at center with dissolve
    Harribel "Si vas a seguirme… tendrás que demostrar que no eres un estorbo."
    hide h2 with dissolve

    # Ejemplo de combate/encuentro
    "Hollows menores emergen de las dunas."
    menu:
        "Luchar a su lado.":
            # $ affection_harribel += 1
            jump harribel_romantica_act2a

        "Protegerla, aunque no lo necesite.":
            # $ affection_harribel += 2
            jump harribel_romantica_act2b


label harribel_romantica_act2a:
    # Luchar a su lado
    scene hollow2 with dissolve
    show h2 at center with dissolve
    Harribel "Al menos sabes blandir un arma… eso ya es algo."
    jump harribel_romantica_act3


label harribel_romantica_act2b:
    # Intentar protegerla
    scene hollow2 with dissolve
    show h2 at center with dissolve
    Harribel "…¿Protegerme? Qué ingenuo… aunque tu valor es digno de notar."
    jump harribel_romantica_act3


# --- Acto 3: El Vínculo --->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
label harribel_romantica_act3:

    scene hollow2 with dissolve
    "Con el tiempo, la fría fachada de Harribel comienza a resquebrajarse."
    show h2 at center with dissolve
    Harribel "No confío en palabras… solo en actos. Pero empiezo a ver algo en ti."

    # Conversación íntima
    menu:
        "Escucharla con respeto.":
            # $ affection_harribel += 1
            jump harribel_romantica_act3a

        "Responder con otra confesión atrevida.":
            # $ affection_harribel += 2
            jump harribel_romantica_act3b


label harribel_romantica_act3a:
    scene hollow2 with dissolve
    show h2 at center with dissolve
    Harribel "…Hacía tiempo que nadie me escuchaba sin miedo o ambición."
    jump harribel_romantica_act4


label harribel_romantica_act3b:
    scene hollow2 with dissolve
    show h2 at center with dissolve
    Harribel "¿Aún tienes fuerzas para hablar así frente a mí? Eres un necio…"
    hide h2 with dissolve
    show h2 at center with dissolve
    Harribel "…pero un necio que no puedo ignorar."
    jump harribel_romantica_act4


# --- Acto 4: Resolución --->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
label harribel_romantica_act4:

    scene hollow2 with dissolve

    "El viaje llega a su fin. Harribel te observa en silencio bajo la luna eterna."

    # if affection_harribel >= 5:
    jump harribel_romantica_final_bueno
    # elif affection_harribel >= 3:
    #     jump harribel_romantica_final_ambiguo
    # else:
    #     jump harribel_romantica_final_malo


# --- Finales ---
label harribel_romantica_final_bueno:

    scene hollow2 with dissolve
    show h2 at center with dissolve
    Harribel "Quizás seas un necio… pero uno al que no quiero perder."
    hide h2 with dissolve
    "Por primera vez, la frialdad en sus ojos se suaviza."
    "Has conquistado el corazón de Harribel."
    jump harribel_cierre


# label harribel_romantica_final_ambiguo:
#     Harribel "Has sobrevivido… y me has intrigado.  
#     Pero no confundas respeto con algo más."
#     narrador "Ella se aleja, dejándote con la sensación de que algo quedó inconcluso."
#     jump cierre

# label harribel_romantica_final_malo:
#     Harribel "Tus palabras no fueron suficientes.  
#     Aquí termina tu camino."
#     narrador "La arena del desierto se tiñe con tu derrota."
#     jump cierre
