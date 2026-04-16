# ===========================================================
# 00_DEFINITIONS_CHARACTERS.RPY – Personajes + Recursos
# Versión v3.2 Reiatsu/Energy Stable Edition (Safe Templates)
# -----------------------------------------------------------
# - Define HP, Reiatsu, Energía, Fuerza, Defensa y fondos
# - get_character() seguro: copia shallow + defaults + plantilla para IDs dinámicos
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
        "race": "human",
        "HP": 100,
        "Strength": 10,
        "Defense": 8,
        "Reiatsu": 100,
        "Energy": 100,
        "coating_type": "fullbring",
        "coating_cover": 0,
        "coating_durability": 0,
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
            "race": "arrancar",
            "HP": 100,
            "Strength": 12,
            "Defense": 9,

            # ⭐ RECURSOS
            "Reiatsu": 100,
            "Energy": 100,
            "coating_type": "hierro",
            "coating_cover": 500,
            "coating_durability": 2000,

            # HUD
            "background": "bg_battle_desert",
            "color": "#00BFFF"
        },

        "Hollow": {
            "id": "Hollow",
            "name": "Hollow",
            "race": "hollow",
            "HP": 100,
            "Strength": 10,
            "Defense": 8,

            "Reiatsu": 100,
            "Energy": 100,
            "coating_type": "hierro",
            "coating_cover": 500,
            "coating_durability": 2000,

            "background": "bg_battle_base",
            "color": "#FF5555"
        },

        "Grimmjow": {
            "id": "Grimmjow",
            "name": "Grimmjow",
            "race": "arrancar",
            "HP": 100,
            "Strength": 14,
            "Defense": 9,

            "Reiatsu": 100,
            "Energy": 100,
            "coating_type": "hierro",
            "coating_cover": 500,
            "coating_durability": 2000,

            "background": "bg_battle_desert",
            "color": "#3CC3FF"
        },

        "Nel": {
            "id": "Nel",
            "name": "Neliel",
            "race": "arrancar",
            "HP": 100,
            "Strength": 11,
            "Defense": 11,

            "Reiatsu": 100,
            "Energy": 100,
            "coating_type": "hierro",
            "coating_cover": 500,
            "coating_durability": 2000,

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
        - Si el ID no existe, genera plantilla segura con ese ID/nombre.
        - No devuelve referencias vivas a CHARACTER_DATA (evita mutar plantillas).
        """
        key = str(char_id or "").strip()
        base = CHARACTER_DATA.get(key, None)
        if not isinstance(base, dict):
            fallback = dict(DEFAULT_CHARACTER)
            fallback["id"] = key or "Unknown"
            fallback["name"] = key or "Unknown"
            fallback["race"] = "unknown"
            base = fallback

        # Normaliza con defaults (evita KeyError)
        out = dict(DEFAULT_CHARACTER)
        out.update(base)

        # Override runtime inyectado desde preparación/lobby (si existe).
        try:
            import renpy.store as S
            ov_root = getattr(S, "bs_runtime_character_overrides", {})
            if isinstance(ov_root, dict):
                ov = ov_root.get(key, None)
                if isinstance(ov, dict):
                    out.update(dict(ov))
        except:
            pass

        # Asegura que el id esté siempre seteado y coherente
        # (si alguien olvidó ponerlo dentro del dict del personaje)
        if not out.get("id") or out["id"] == "Unknown":
            out["id"] = key or "Unknown"

        return out  # <- copia shallow (out es nuevo dict)

    # -------------------------------------------------------
    # 🔎 Helpers opcionales (no rompen nada si no los usás)
    # -------------------------------------------------------
    def get_character_name(char_id):
        """Nombre visible para el jugador (display)."""
        return get_character(char_id).get("name", DEFAULT_CHARACTER["name"])

    def get_combat_character_ids(include_hollow=True):
        """
        IDs disponibles en el runtime de combate.
        Orden de prioridad:
        1) Catálogo inyectado/activo del Hub Saga.
        2) CHARACTER_DATA local.
        """
        try:
            import renpy.store as S
        except:
            S = None

        ids = []
        rows = []
        if S is not None:
            try:
                fn = getattr(S, "bs_get_hero_catalog_v1", None)
                if callable(fn):
                    rows = list(fn() or [])
            except:
                rows = []
            if not rows:
                try:
                    rows = list(getattr(S, "bs_hero_catalog_v1", []) or [])
                except:
                    rows = []
            if not rows:
                try:
                    rows = list(getattr(S, "CHARACTER_DB", []) or [])
                except:
                    rows = []

        for row in rows:
            if not isinstance(row, dict):
                continue
            raw = row.get("hero_id", None) or row.get("id", None) or row.get("name", None)
            hid = str(raw or "").strip()
            if hid:
                ids.append(hid)

        if not ids:
            ids = [str(k) for k in CHARACTER_DATA.keys() if str(k)]

        unique = []
        seen = {}
        for hid in ids:
            k = str(hid).strip().lower()
            if not k or seen.get(k):
                continue
            seen[k] = True
            unique.append(str(hid).strip())

        if include_hollow:
            if "hollow" not in [x.lower() for x in unique] and "Hollow" in CHARACTER_DATA:
                unique.append("Hollow")
        else:
            unique = [x for x in unique if x.lower() != "hollow"]

        return unique


    def get_character_stat(char_id, stat_key, fallback=None):
        """
        Helper seguro para leer cualquier stat numérico desde CHARACTER_DATA.
        """
        char = get_character(char_id)
        if fallback is None:
            fallback = DEFAULT_CHARACTER.get(stat_key, 0)
        return char.get(stat_key, fallback)

    def get_character_hp(char_id):
        """HP base del personaje definido en CHARACTER_DATA."""
        return int(get_character_stat(char_id, "HP", DEFAULT_CHARACTER["HP"]))

    def get_character_bg(char_id):
        """
        Devuelve el tag de background (string).
        Para usarlo: scene expression get_character_bg(id)
        """
        return get_character(char_id).get("background", DEFAULT_CHARACTER["background"])


# -----------------------------------------------------------
# 📘 IMÁGENES DE ESCENARIOS
# -----------------------------------------------------------
image bg_battle_base   = "images/fondo3.png"
image bg_battle_desert = "images/hollow1.png"

init -994 python:
    import renpy.store as S
    S.get_combat_character_ids = get_combat_character_ids
