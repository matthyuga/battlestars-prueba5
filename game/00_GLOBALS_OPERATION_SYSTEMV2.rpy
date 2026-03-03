# ============================================================
# 00_GLOBALS_OPERATION_SYSTEM.RPY – Sistema de Operación Final
# Versión: v3.3 StoreSafe + BorderAware (Ren’Py 7.4.9)
# ------------------------------------------------------------
# - operation_clear / operation_add / operation_dump_to_battle_log
# - No revienta si battle_log_add aún no existe (orden de init)
# - Usa battle_log_add_ex si existe (soporta border)
# ============================================================

init -996 python:

    import renpy.store as S

    # Lista temporal donde se guardan las líneas de OPERACIÓN.
    # Puede contener:
    #   - dict: {"text": "...", "border": "#RRGGBB"}
    #   - (opcional) strings si algún sistema viejo hace append directo
    debug_operation_log = []

    # --------------------------------------------------------
    # LIMPIAR OPERACIÓN (sin re-asignar: limpia in-place)
    # --------------------------------------------------------
    def operation_clear():
        try:
            debug_operation_log[:] = []
        except Exception:
            # Si alguien la pisó, intentamos recuperar sin crashear
            try:
                while debug_operation_log:
                    debug_operation_log.pop()
            except Exception:
                pass

    # --------------------------------------------------------
    # AÑADIR UNA LÍNEA A LA OPERACIÓN
    # --------------------------------------------------------
    def operation_add(text, border=None):
        """
        Guarda una línea de operación.
        border: color sugerido para borde/estilo (si el log lo soporta).
        """
        try:
            debug_operation_log.append({
                "text": str(text),
                "border": border
            })
        except Exception:
            # Fallback mínimo: al menos guardar el texto
            try:
                debug_operation_log.append({"text": str(text), "border": None})
            except Exception:
                pass

    # --------------------------------------------------------
    # DUMP → Pasar TODAS las líneas al battle_log
    # --------------------------------------------------------
    def operation_dump_to_battle_log():
        if not debug_operation_log:
            return

        # Sink principal y extendido (si existe)
        bl = getattr(S, "battle_log_add", None)
        blex = getattr(S, "battle_log_add_ex", None)

        # Si no hay ningún sink, limpiamos y salimos (no crashea)
        if not callable(bl) and not callable(blex):
            operation_clear()
            return

        # -----------------------------
        # Encabezado estético
        # -----------------------------
        header = "OPERACIÓN FINAL"
        try:
            if hasattr(S, "fmt_white"):
                header = S.fmt_white(header)
        except Exception:
            header = "OPERACIÓN FINAL"

        try:
            if callable(blex):
                # Si tenés OP_COLOR_BORDER, lo pasa como border del encabezado
                blex(header, border=getattr(S, "OP_COLOR_BORDER", "#FFFFFF"))
            elif callable(bl):
                bl(header)
        except Exception:
            # Si falla el encabezado por cualquier motivo, seguimos
            pass

        # -----------------------------
        # Líneas
        # -----------------------------
        for row in debug_operation_log:
            try:
                # Soporta dicts (nuevo formato)
                if isinstance(row, dict):
                    t = row.get("text", "")
                    b = row.get("border", None)

                    if callable(blex):
                        blex(t, border=b)
                    elif callable(bl):
                        bl(t)

                # Soporta strings (por compatibilidad)
                else:
                    if callable(blex):
                        blex(str(row), border=None)
                    elif callable(bl):
                        bl(str(row))

            except Exception:
                # Nunca dejes que el log rompa el turno
                pass

        # Limpiar para el siguiente turno
        operation_clear()
