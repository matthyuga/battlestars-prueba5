# ============================================================
# 04Z_REFLECT_HELPERS.rpy – Helpers unificados de Reflect
# v1.0 – Centraliza target/source + store-safe
# ------------------------------------------------------------
# - Nadie fuera de acá debe llamar reflect.add() directamente.
# - API:
#     reflect_queue(attacker_id, defender_id, value)
#     reflect_consume_for(actor_id) -> (value, source_id)
#     reflect_peek_for(actor_id)    -> (value, source_id)
#     reflect_clear_for(actor_id)
# ============================================================

init -998 python:
    import renpy.store as S

    # --------------------------------------------------------
    # Obtener manager real (S.reflect preferido)
    # --------------------------------------------------------
    def _get_reflect_manager():
        r = getattr(S, "reflect", None)
        if r is not None:
            return r
        # fallback: variable global "reflect" si existiera
        try:
            return globals().get("reflect", None)
        except:
            return None

    # --------------------------------------------------------
    # API: encolar reflect (TARGET = attacker, SOURCE = defender)
    # --------------------------------------------------------
    def reflect_queue(attacker_id, defender_id, value):
        """
        attacker_id: quien RECIBIRÁ el reflect (target)
        defender_id: quien lo GENERÓ (source)
        value: int daño reflejado
        """
        r = _get_reflect_manager()
        if r is None:
            return 0

        try:
            v = int(value or 0)
        except:
            v = 0
        if v <= 0:
            return 0

        t = attacker_id
        s = defender_id

        # Intentar API moderna con source_id; fallback si es viejo
        try:
            return r.add(t, v, source_id=s)
        except TypeError:
            try:
                return r.add(t, v)
            except:
                return 0
        except:
            return 0

    # --------------------------------------------------------
    # API: consumir reflect para un actor
    # --------------------------------------------------------
    def reflect_consume_for(actor_id):
        """
        Devuelve (valor, source_id). Si no hay, (0, None).
        """
        r = _get_reflect_manager()
        if r is None:
            return 0, None

        # preferir consume_info si existe
        try:
            fn = getattr(r, "consume_info", None)
            if callable(fn):
                return fn(actor_id)
        except:
            pass

        # fallback legacy consume()
        try:
            v = r.consume(actor_id)
            return int(v or 0), None
        except:
            return 0, None

    # --------------------------------------------------------
    # API: mirar sin consumir
    # --------------------------------------------------------
    def reflect_peek_for(actor_id):
        r = _get_reflect_manager()
        if r is None:
            return 0, None
        try:
            v = int(r.get(actor_id) or 0)
        except:
            v = 0
        try:
            s = r.get_source(actor_id)
        except:
            s = None
        return v, s

    # --------------------------------------------------------
    # API: limpiar reflect de un actor
    # --------------------------------------------------------
    def reflect_clear_for(actor_id):
        r = _get_reflect_manager()
        if r is None:
            return
        try:
            r.clear(actor_id)
        except:
            pass

    # --------------------------------------------------------
    # Export opcional al store (para usar S.reflect_queue, etc.)
    # --------------------------------------------------------
    try:
        S.reflect_queue = reflect_queue
        S.reflect_consume_for = reflect_consume_for
        S.reflect_peek_for = reflect_peek_for
        S.reflect_clear_for = reflect_clear_for
    except:
        pass
