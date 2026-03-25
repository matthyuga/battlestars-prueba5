# =================================
# RUTA NEUTRAL
# =================================

# --- Acto 1: El Encuentro ---
label harribel_neutral:

    scene hollow1 with dissolve
    
    show h2 at center with dissolve
    Harribel "…¿Como te llamas? No pareces un enemigo… pero tampoco un aliado."

    menu:
        "Soy [player_name], como te explico? creo que me perdí.":
            jump neutral_opcion1

        "Si quieres luchar, lo lamento, pero no tengo intención.":
            jump neutral_opcion2


# --- Acto 2: La Decisión ---
label neutral_opcion1:

    show h2 at left with dissolve
    Harribel "Hmph… entonces mantente fuera de mi camino."
    jump neutral_acto2

label neutral_opcion2:

    show h2 at right with dissolve
    Harribel "Interesante… un humano que no huye ni ataca."
    jump neutral_acto2

label neutral_acto2:

    scene hollow2 with fade
    Harribel "…Puede que todavía vivas un poco más, veremos."

    menu:
        "Aceptar su advertencia y retirarse.":
            jump neutral_retirada

        "Permanecer cerca, observándola en silencio.":
            jump neutral_observar


# --- Acto 3: El Camino Intermedio ---
label neutral_retirada:

    scene hollow3 with dissolve
    "Te alejas lentamente, manteniendo la distancia. La tensión aún persiste."
    jump neutral_acto3

label neutral_observar:

    scene hollow3 with dissolve
    "Decides quedarte. Ella te lanza una mirada fría, pero no actúa en tu contra."
    jump neutral_acto3

label neutral_acto3:

    show h2 at center with dissolve
    Harribel "Quizás no seas tan inútil después de todo…"
    
    menu:
        "Responder con calma.":
            jump neutral_responder

        "Guardar silencio y seguirla.":
            jump neutral_seguir


# --- Acto 4: El Desenlace Neutral ---
label neutral_responder:

    scene hollow4 with fade
    Harribel "Tienes valor, pero también sabes mantener la cabeza fría. Eso podría salvarte."
    return

label neutral_seguir:

    scene hollow4 with fade
    Harribel "El silencio también es una respuesta… puede que aún tengas tu utilidad."
    return

    jump harribel_cierre