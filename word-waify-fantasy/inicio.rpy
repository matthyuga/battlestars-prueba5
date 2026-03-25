# =================================
# INICIO
# =================================
default player_name = "Jugador"

label start:
    scene fondo3 with fade
    $ player_name = renpy.input("Como te llamas?:", length=20)
    if player_name == "" or player_name is None:
        $ player_name = "Jugador"

    # Ahora defino al protagonista con el nombre ya capturado
    $ Prota = Character(player_name, color="#fff9c4")

    "Gracias por probar Word Waifu Fantasy, [player_name]."
    
    jump escena1


label escena1:
    
    
    scene trama1 with fade
    Prota "Hmm... otro día aburrido..."
    
    Prota "Tal vez debería revisar mi celular."
    


    # Segunda diapositiva
    scene trama2 with fade
    Prota "¡Un nuevo juego! Lo voy a instalar."
  
     # Transición a lo oscuro
    scene bgnegro1 with fade
    #play sound "pasos_cercanos.ogg"  # opcional

    # Aparición del creador
    



    "De repente todo se vuelve negro, no logras ver nada a tu alrededor, sin embargo oyes unos pasos acercándose."
    show c1 at center with fade
    Mordelon "Hola, [player_name] déjame darte la bienvenida a Word Waifu Fantasy, la aventura te espera pero antes déjame darte algunas indicaciones." 
    Mordelon "Este juego es solo una version demo para ich io, las actualizaciones las subiré a mi discord, cualquier consulta la puedes hacer allí."

    Mordelon "Revisa tu pantalla y ve al punto que te marca en el mapa"
    hide c1 with dissolve
    show cellmap1 at center with fade
    "Observas un mapa en tu teléfono que indica el punto de partida…"

 
    menu:
        "Iniciar Partida.":
            jump escena2
    label escena2:
    #scene bgnegro1 with fade
    hide c1 with dissolve
    hide cellmap1 with dissolve
    show c1 at center with fade
    Mordelon "En fin, espero que lo disfrutes, nos veremos pronto, [player_name]"
    $ tutorial_completado = True
    hide c1 with dissolve
   # play movie "portal1.webm"
   # show movie
   # $ renpy.pause(5)  # Duración en segundos, o hasta que termines el video
   # stop movie
    window hide
    $ renpy.movie_cutscene("portal1.webm")

   # hide movie with dissolve
    scene white 
    # Todo se pone blanco
    
    "La luz se apodera del ambiente y todo se cubre de blanco a tu alrededor."

   # pause 1.0

    # Aparece en hueco mundo
    scene hollow1 with fade
    "Un instante despues las primeras imagenes del mundo aparecen ante ti."
    Prota "esto es..."
    
    #escena de rol1 harribel en el desierto hollow
    scene inicio1 with dissolve #PONER OTRO ESCENARIO
    "La inmensidad del decierto hollow se extiende hasta donde la vista alcanza."
    "Todo parece estar en calma hasta que la correinte cambia y te percatas de una presencia muy poderosa."
    "Sin embargo ya es demasiado tarde para correr o reaccionar."

    scene map1 with dissolve
    show h4 at center with dissolve

    # Elegir una frase al azar
   # $ chosen_line = renpy.random.choice(harribel_lines1)

    #Harribel "[chosen_line]" 
    

    
    $ harribel_phrase, frase_id = random.choice(harribel_lines1)

    Harribel "«[harribel_phrase]»"

    jump harribel_menu
    
    label harribel_menu:
    scene choice1 with dissolve
    

    if frase_id == "frase1":#¡Alto ahí, ¿quién eres?!
        menu:
            "Soy [player_name], y tú debes ser Harribel... ¿no es así?":
            # Ruta formal, neutra con un toque de romance
                jump ruta1a
            "Te quedas sin palabras al verla... su belleza te deja paralizado.":
            # Ruta romántica pura
                jump ruta1b

            "¿Qué mierda es este lugar?":
            # Ruta desagradable o final prematuro
                jump ruta1c

    elif frase_id == "frase2":#No eres un Hollow ni un Shinigami, ¿qué haces aquí, forastero?.
        menu:
            "Explicar quién eres":
                jump ruta2a
            "Mentir sobre tu origen":
                jump ruta2b
            "Ignorarla y retroceder":
                jump ruta2c

    elif frase_id == "frase3":#Ese olor... ¿un humano en estas tierras? Imposible!
        menu:
            "Negar ser humano":
                jump ruta3a
            "Admitirlo con orgullo":
                jump ruta3b
            "Quedarte en silencio":
                jump ruta3c

    elif frase_id == "frase4":#Será mejor que te identifiques si no quieres que te corte la cabeza ahora mismo.
        menu:
            "Identificarte":
                jump ruta4a
            "Desafiarla":
                jump ruta4b
            "Pedir tiempo":
                jump ruta4c



   

   # =================================
# eleccion primera
# =================================


    #menu:
    #"No lo sé… pero tu belleza me hace olvidar el miedo.":
          #  jump harribel_romantica
            
    #
      #  "Solo estoy perdido, no quiero problemas.":
      #      jump harribel_neutral

      #  "Si quieres luchar, estoy listo.":
         #   jump harribel_dominante
            
    
    return