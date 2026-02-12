# ============================================================
# 00_GLOBALS_OPERATION_COLORS.RPY – Colores para operación
# Versión: v1.2 StoreSafe + LateSync (Ren’Py 7.4.9)
# ============================================================

init -997 python:
    import renpy.store as S

    def op_colors_sync(force=False):
        """
        Sincroniza OP_COLOR_* con PALETTE si existe.
        - Si force=False: solo pisa si la variable no existe (o es None).
        - Si force=True: pisa siempre con PALETTE (si existe).
        """
        pal = getattr(S, "PALETTE", None)
        if not isinstance(pal, dict):
            return

        def _set(name, palette_key, fallback):
            if force or (not hasattr(S, name)) or (getattr(S, name) is None):
                setattr(S, name, pal.get(palette_key, fallback))

        _set("OP_COLOR_TEXT",    "white",  "#FFFFFF")
        _set("OP_COLOR_BORDER",  "white",  "#FFFFFF")
        _set("OP_COLOR_DAMAGE",  "red",    "#FF4444")
        _set("OP_COLOR_DEFENSE", "blue",   "#00BFFF")
        _set("OP_COLOR_REFLECT", "effect", "#55FFFF")  # o "cyan" si preferís
        _set("OP_COLOR_TOTAL",   "gold",   "#FFD700")

    # Defaults (para no crashear aunque no haya PALETTE)
    if not hasattr(S, "OP_COLOR_TEXT"):    S.OP_COLOR_TEXT    = "#FFFFFF"
    if not hasattr(S, "OP_COLOR_BORDER"):  S.OP_COLOR_BORDER  = "#FFFFFF"
    if not hasattr(S, "OP_COLOR_DAMAGE"):  S.OP_COLOR_DAMAGE  = "#FF4444"
    if not hasattr(S, "OP_COLOR_DEFENSE"): S.OP_COLOR_DEFENSE = "#00BFFF"
    if not hasattr(S, "OP_COLOR_REFLECT"): S.OP_COLOR_REFLECT = "#55FFFF"
    if not hasattr(S, "OP_COLOR_TOTAL"):   S.OP_COLOR_TOTAL   = "#FFD700"
