# ===========================================================
# 00_LOG_HELPERS.rpy – Helpers de Log + Formato
# Versión: v1.1 Safe Battle Log + Canon fmt Edition
# -----------------------------------------------------------
# - blog() seguro: usa renpy.store.battle_log_add si existe
# - fallback: renpy.say si el log aún no está disponible
# - fmt() alias del formateador canónico battle_fmt_num
# ===========================================================

init -992 python:
    import renpy.store as S

    # 0 = mínimo, 1 = normal, 2 = detallado
    battle_log_detail = 1
    S.battle_log_detail = battle_log_detail

    def blog(text, color="#DDD", level=1):
        """
        Log seguro:
        - Si existe battle_log_add -> lo usa.
        - Si no existe -> fallback a renpy.say.
        - Si falla por cualquier razón -> loggea el error y cae al fallback.
        """
        try:
            detail = getattr(S, "battle_log_detail", battle_log_detail)
        except Exception:
            detail = battle_log_detail

        if level <= detail:
            try:
                if hasattr(S, "battle_log_add"):
                    S.battle_log_add(str(text), color)
                else:
                    renpy.say(None, str(text))
            except Exception as e:
                try:
                    renpy.log("blog error: {}".format(e))
                except Exception:
                    pass
                renpy.say(None, str(text))

    S.blog = blog

    def blog_result(text):
        blog("→ " + str(text), "#FFD35A", level=1)

    S.blog_result = blog_result

    def fmt(n):
        """
        Formato canónico:
        - Usa battle_fmt_num si existe (definido en tu core).
        - Si no existe todavía, fallback a str(n).
        """
        try:
            if hasattr(S, "battle_fmt_num"):
                return S.battle_fmt_num(n)
        except Exception:
            pass
        return str(n)

    S.fmt = fmt
