# ==========================
# Definir personajes
# ==========================


define Mordelon = Character("Creador", color="#ff9999") 
define Harribel = Character("Tier Harribel", color="#ffe600")




# ==========================
# Definir el mapa o los escenarios
# ==========================
#image fondo_video = Movie(play="images/choice1a.webm", loop=True)
#image choice1a_video = Movie(play="images/choice1a.webm", loop=True)


image bg inicio1 = "inicio1.png"
image bg map1    = "map1.png"
image bg choice1 = "choice1.png"
image bg ghoul1    = "ghoul1.png"
image bg hollow1 = "hollow1.png"
image bg white = "hollow1.png"
# ==========================
# Definir avatares para el dialogo dialogo
# ==========================

image h1 = "h1.png"
image h2 = "h2.png"
image h3 = "h3.png"

# ==========================
# Definir estados
# ==========================
# default confianza_harribel = 0
#romantica_harribel= 0
#neutral_harribel= 0
#Dominante_harribel= 0


# ==========================
# Definir rutas desbloqueadas
# ==========================
default complete_romantica = False
default complete_neutral = False
default complete_dominante = False
default desbloqueo_total = False
 
 
#define movie = Movie(channel="movie")


# >>>>>>>>>>FRASES <<<<<<<<<
# frase de inicio
default harribel_phrase = None
init python:
    # Lista de frases posibles para Harribel (modifícalas si quieres)
    import random
    harribel_lines1 = [
        ("¡Alto ahí, ¿quién eres?!", "frase1"),
        ( "No eres un Hollow ni un Shinigami, ¿qué haces aquí, forastero?.", "frase1"),
        ( "Ese olor... ¿un humano en estas tierras? Imposible!", "frase1"),
        ( "Será mejor que te identifiques si no quieres que te corte la cabeza ahora mismo.", "frase1"),
    ]




## VARIABLES GLOBALES
# =======================================================
default afecto_harribel = 0
default mostrar_barra = False

# =======================================================
# BARRA DE AFECTO — versión toggle
# =======================================================

init python:
    renpy.image("barra_harribel", ConditionSwitch(
        "afecto_harribel <= 0", "gui/barra/c0.png",
        "afecto_harribel == 1", "gui/barra/c1.png",
        "afecto_harribel == 2", "gui/barra/c2.png",
        "afecto_harribel == 3", "gui/barra/c3.png",
        "afecto_harribel == 4", "gui/barra/c4.png",
        "afecto_harribel == 5", "gui/barra/c5.png",
        "afecto_harribel == 6", "gui/barra/c6.png",
        "afecto_harribel == 7", "gui/barra/c7.png",
        "afecto_harribel == 8", "gui/barra/c8.png",
        "afecto_harribel == 9", "gui/barra/c9.png",
        "afecto_harribel >= 10", "gui/barra/c10.png",
    ))


default tutorial_completado = False