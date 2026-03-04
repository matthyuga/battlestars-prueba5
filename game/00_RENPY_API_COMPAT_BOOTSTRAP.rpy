# ============================================================
# 00_RENPY_API_COMPAT_BOOTSTRAP.rpy — Compat API bootstrap
# ============================================================
# Ensure minimal Ren'Py API compatibility before gui/layout init.
# This runs very early so common/gui code can safely call methods
# expected by project scripts across runtime variants.
# ============================================================

init -2000 python:
    import renpy

    if not hasattr(renpy, "has_screen"):
        def _bs_has_screen(name):
            getter = getattr(renpy, "get_screen", None)
            if callable(getter):
                try:
                    return getter(name) is not None
                except Exception:
                    return False
            return False
        renpy.has_screen = _bs_has_screen
