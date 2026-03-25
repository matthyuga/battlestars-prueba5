# =================================
#  ruta1a "frase1":#¡Alto ahí, ¿quién eres?!
# "Soy [player_name], y tú debes ser Harribel... ¿no es así?":

# --- Acto 1:  ---
    
   

label ruta1a:
    #show screen barra_afecto_harribel_toggleable
    scene hollow1 with fade
    show h2 at center with dissolve
    Harribel "¿Cómo sabes mi nombre?" #COMENTARIO

    "Su mirada se endurece. Por un instante, parece lista para atacarte, pero algo en tu tono la hace dudar."#NARRACIÓN

    
    menu: #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DESICION 1
        "Bueno... es una historia curiosa. ¿Quieres que te la cuente?":
            $ afecto_harribel += 5
            jump harribel_historia

        "Te quedas pensativo y no sabes qué decir. Poco a poco, los nervios te dominan.":
            $ afecto_harribel -= 1
            jump harribel_silencio


# ---------------------------------------------------
# Opción 1: El jugador habla (versión seria y meta)
# ---------------------------------------------------
label harribel_historia:
    #si tiene 1 punto 
    if afecto_harribel >= 2:
        "Un buen comienzo marca la diferencia. Ella se queda en silencio, intrigada... tienes su atención."#NARRACIÓN
    
    else:
        "Respiras hondo y das un paso al frente. Su energía espiritual te oprime el pecho, pero decides hablar igual."#NARRACIÓN

    Prota "No estoy seguro de cómo explicarlo... simplemente, sabía tu nombre. Como si ya te conociera desde antes."#COMENTARIO

    Harribel "Eso no tiene sentido. Nunca te he visto, y si lo hubiera hecho... lo recordaría."#COMENTARIO 

    "Su tono se vuelve más suave, aunque sus ojos siguen fijos en ti. Parece debatirse entre creerte o eliminarte."#NARRACIÓN

    menu:#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>DESICION 2
        "Digamos que... te vi en otro mundo. En una historia que se contaba donde yo vivía.":
            $ afecto_harribel += 5
            jump harribel_meta

        "Supongo que fue una intuición. Algo... familiar en ti.":
            $ afecto_harribel += 1
            jump harribel_seria


# -------------------------
# Versión meta (fuera del universo)
# -------------------------
label harribel_meta:

    Prota "Verás, en mi mundo existe algo llamado *anime*. Una especie de historia animada... y tú eras parte de ella."#COMENTARIO

    "Por un instante, Harribel no responde. Su expresión cambia: desconcierto puro."

    Harribel "...¿Me estás diciendo que soy un personaje de ficción en tu mundo?"#COMENTARIO

    Prota "Lo sé, suena ridículo... pero todo aquí parece sacado de un sueño. O de un error."#COMENTARIO

    "Ella te observa largo rato. No parece enojada, sino más bien... confundida."

    Harribel "Hmph. Si eso fuera cierto... entonces tú tampoco deberías existir aquí."#COMENTARIO

    "Un silencio extraño se instala. Sientes que, de alguna manera, ambos están fuera de lugar."

    jump harribel_acto1_final


# -------------------------
# Versión seria (in-universe)
# -------------------------
label harribel_seria:

    Harribel "¿Familiar? No entiendo de qué hablas."#COMENTARIO

    Prota "No sé... hay algo en ti. Tu presencia, tu forma de mirar... me resulta conocida."#COMENTARIO

    "Ella parece dudar por un segundo. Sus ojos, antes fríos, se suavizan apenas."

    Harribel "No es prudente hablar de ese modo con un Arrancar. Pero... seguiré escuchando."#COMENTARIO

    "Su voz suena menos distante. Algo en tu sinceridad parece haber despertado su curiosidad."

    jump harribel_acto1_final


# ---------------------------------------------------
# Opción 2: El jugador se queda callado
# ---------------------------------------------------
label harribel_silencio:

    "El silencio se hace pesado. Intentas responder, pero las palabras se atascan en tu garganta."

    Harribel "¿Nada que decir? Hmph... un humano débil y torpe."#COMENTARIO

    "A pesar de sus palabras, no se mueve para atacarte. Hay algo en tu confusión que le causa intriga."

    Harribel "Habla, antes de que cambie de opinión."#COMENTARIO

    Prota "Solo... no entiendo qué está pasando. Siento que te conozco, pero no sé de dónde."#COMENTARIO

    "Ella frunce el ceño, dudando entre la amenaza y la curiosidad."

    Harribel "¿Que me conoces? Explica eso."#COMENTARIO

    jump harribel_historia


# ---------------------------------------------------
# Punto de unión del Acto 1
# ---------------------------------------------------
label harribel_acto1_final:

    "El aire entre ambos se vuelve denso, cargado de energía.  
    No hay odio en sus ojos... solo una pregunta sin respuesta."

    Harribel "Sea lo que sea que creas saber de mí... espero que no te arrepientas."

    "Por primera vez, notas un leve brillo en su mirada.  
    No es furia... es interés."

    "El Acto 1 concluye con la sensación de que algo impredecible está por comenzar."

    jump harribel_acto2
