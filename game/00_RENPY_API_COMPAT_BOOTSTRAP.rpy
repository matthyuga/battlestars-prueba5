# ============================================================
# 00_RENPY_API_COMPAT_BOOTSTRAP.rpy — Compat API bootstrap
# ============================================================
# Ensure minimal Ren'Py API compatibility before gui/layout init.
# This runs very early so common/gui code can safely call methods
# expected by project scripts across runtime variants.
# NOTE: do NOT `import renpy` here because that can shadow the
# store-provided Ren'Py API object used by common scripts.
# ============================================================

init -2000 python:
    _renpy_api = renpy

    if not hasattr(_renpy_api, "has_screen"):
        def _bs_has_screen(name):
            getter = getattr(_renpy_api, "get_screen", None)
            if callable(getter):
                try:
                    return getter(name) is not None
                except Exception:
                    return False
            return False
        _renpy_api.has_screen = _bs_has_screen

    if not hasattr(_renpy_api, "pure"):
        def _bs_pure(func):
            return func
        _renpy_api.pure = _bs_pure
