# =================================
# RUTA DOMINANTE
# =================================
# --- Acto 1: El Encuentro ---
label harribel_dominante:

    scene hollow1 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Veo en ti un espíritu que no se doblega fácilmente…"
    Harribel "Pero, ¿podrás soportar lo que te espera si te enfrentas a mí?"

    menu:
        "Lucharé, no me rendiré.":
            jump dominante_acto2_pelea

        "Me dejo vencer… quiero ver a dónde me llevará.":
            jump dominante_acto2_masoquista

# --- Acto 2: Confrontación o Rendición ---
label dominante_acto2_pelea:

    scene hollow2 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Ah, así que buscas desafiarme…"
    Harribel "Veremos si tu fuerza está a la altura de mis expectativas."

    menu:
        "Seguir luchando.":
            jump dominante_acto3_pelea

        "Ceder y dejar que ella me controle.":
            jump dominante_acto3_masoquista

label dominante_acto2_masoquista:

    scene hollow2 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Oh, ¿te rindes tan rápido? Qué interesante…"
    Harribel "Me pregunto qué haré contigo ahora…"

    menu:
        "Permitir que haga lo que quiera.":
            jump dominante_acto3_masoquista

        "Intentar pelear de todas formas.":
            jump dominante_acto3_pelea

# --- Acto 3: Juego de Poder ---
label dominante_acto3_pelea:

    scene hollow3 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Tu resistencia me divierte… pero no lo suficiente para dejarte libre."
    Harribel "Ahora comienza mi juego contigo, y no habrá segundas oportunidades."

    menu:
        "Seguir resistiendo.":
            jump dominante_acto4_pelea

        "Aceptar su control momentáneamente.":
            jump dominante_acto4_masoquista

label dominante_acto3_masoquista:

    scene hollow3 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Qué delicioso… te dejo a mi merced."
    Harribel "Jugaré contigo, te empujaré y provocaré… todo a mi gusto."

    menu:
        "Dejarse llevar completamente.":
            jump dominante_acto4_masoquista

        "Intentar rebelarse un poco.":
            jump dominante_acto4_pelea

# --- Acto 4: Resultado ---
label dominante_acto4_pelea:

    scene hollow4 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Hmm… valiente, pero aún no eres rival para mí."
    Harribel "Tal vez la próxima vez seas más fuerte… o más sumiso."

    "Fin de la demo - Ruta Dominante (Resistencia)"
    return

label dominante_acto4_masoquista:

    scene hollow4 with dissolve  
    
    show h3 at center with dissolve
    Harribel "Perfecto… me diviertes mucho así."
    Harribel "Te encierro, te provoco, y juego contigo a mi antojo."

    "Fin de la demo - Ruta Dominante (Masoquista)"
    return
