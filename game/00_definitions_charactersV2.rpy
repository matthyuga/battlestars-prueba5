# ===========================================================
# 00_DEFINITIONS_CHARACTERS.RPY – Personajes + Recursos
# Versión v3.2 Reiatsu/Energy Stable Edition (Safe Templates)
# -----------------------------------------------------------
# - Define HP, Reiatsu, Energía, Fuerza, Defensa y fondos
# - get_character() seguro: copia shallow + defaults + fallback a Hollow
# - Separación ID (sistema) vs NAME (display para jugador)
# - Background como string tag (usar con scene expression)
# - Compatible con REIATSU/ENERGY SYSTEM + GLOBALS CORE
# ===========================================================

init -995 python:

    # -------------------------------------------------------
    # ✅ DEFAULTS (para evitar KeyErrors cuando falten campos)
    # -------------------------------------------------------
    DEFAULT_CHARACTER = {
        "id": "Unknown",               # ID interno del sistema (clave estable)
        "name": "Unknown",             # Nombre visible para el jugador
        "HP": 5000,
        "Strength": 10,
        "Defense": 8,
        "Reiatsu": 300,
        "Energy": 60,
        "background": "bg_battle_base",  # tag de imagen Ren'Py (string)
        "color": "#FFFFFF"
    }

    # -------------------------------------------------------
    # 📘 BASE DE PERSONAJES
    # -------------------------------------------------------
    # Clave principal = ID del sistema (estable).
    # "name" = display name (puede ser alias/largo/cambio estético).
    CHARACTER_DATA = {

        "Harribel": {
            "id": "Harribel",
            "name": "Harribel",
            "HP": 11000,
            "Strength": 12,
            "Defense": 9,

            # ⭐ RECURSOS
            "Reiatsu": 2000,
            "Energy": 1000,

            # HUD
            "background": "bg_battle_desert",
            "color": "#00BFFF"
        },

        "Hollow": {
            "id": "Hollow",
            "name": "Hollow",
            "HP": 10000,
            "Strength": 10,
            "Defense": 8,

            "Reiatsu": 3000,
            "Energy": 600,

            "background": "bg_battle_base",
            "color": "#FF5555"
        },

        "Grimmjow": {
            "id": "Grimmjow",
            "name": "Grimmjow",
            "HP": 10000,
            "Strength": 14,
            "Defense": 9,

            "Reiatsu": 10000,
            "Energy": 900,

            "background": "bg_battle_desert",
            "color": "#3CC3FF"
        },

        "Nel": {
            "id": "Nel",
            "name": "Neliel",
            "HP": 9500,
            "Strength": 11,
            "Defense": 11,

            "Reiatsu": 5000,
            "Energy": 700,

            "background": "bg_battle_desert",
            "color": "#77FF77"
        },
    }

    # -------------------------------------------------------
    # ✔ FUNCIÓN SEGURA PARA OBTENER DATOS DEL PERSONAJE
    # -------------------------------------------------------
    def get_character(char_id):
        """
        Devuelve un dict SEGURO (copia shallow) del personaje.
        - Usa DEFAULT_CHARACTER para completar campos faltantes.
        - Si el ID no existe, devuelve Hollow por defecto.
        - No devuelve referencias vivas a CHARACTER_DATA (evita mutar plantillas).
        """
        base = CHARACTER_DATA.get(char_id, CHARACTER_DATA.get("Hollow", {}))

        # Normaliza con defaults (evita KeyError)
        out = dict(DEFAULT_CHARACTER)
        out.update(base)

        # Asegura que el id esté siempre seteado y coherente
        # (si alguien olvidó ponerlo dentro del dict del personaje)
        if not out.get("id") or out["id"] == "Unknown":
            out["id"] = char_id if char_id in CHARACTER_DATA else "Hollow"

        return out  # <- copia shallow (out es nuevo dict)

    # -------------------------------------------------------
    # 🔎 Helpers opcionales (no rompen nada si no los usás)
    # -------------------------------------------------------
    def get_character_name(char_id):
        """Nombre visible para el jugador (display)."""
        return get_character(char_id).get("name", DEFAULT_CHARACTER["name"])

    def get_character_bg(char_id):
        """
        Devuelve el tag de background (string).
        Para usarlo: scene expression get_character_bg(id)
        """
        return get_character(char_id).get("background", DEFAULT_CHARACTER["background"])


# -----------------------------------------------------------
# 📘 IMÁGENES DE ESCENARIOS
# -----------------------------------------------------------
image bg_battle_base   = "fondo3.png"
image bg_battle_desert = "hollow1.png"
