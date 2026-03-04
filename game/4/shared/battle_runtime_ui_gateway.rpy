# ============================================================
# battle_runtime_ui_gateway.rpy — Gateway UI runtime-safe (T4)
# ============================================================
# API canónica para combate:
#   - bs_ui_show(name, **kwargs)
#   - bs_ui_hide(name)
#   - bs_ui_get(name)
#   - bs_ui_restart()
#   - bs_ui_pause(delay, hard=False)
#   - bs_ui_with(trans)
#   - bs_ui_random_int(a, b)
#   - bs_ui_has_label(name)
#
# Compat:
#   - ensure_renpy_ui_apis() se mantiene como alias estable.
# ============================================================

init -980 python:
    import random

    # Use the store-provided Ren'Py API object; do not `import renpy` here.
    _renpy_api = renpy

    def bs_ui_show(name, **kwargs):
        fn = getattr(_renpy_api, "show_screen", None)
        if callable(fn):
            return fn(name, **kwargs)
        return None

    def bs_ui_hide(name):
        fn = getattr(_renpy_api, "hide_screen", None)
        if callable(fn):
            return fn(name)
        return None

    def bs_ui_get(name):
        fn = getattr(_renpy_api, "get_screen", None)
        if callable(fn):
            return fn(name)
        return None

    def bs_ui_restart():
        fn = getattr(_renpy_api, "restart_interaction", None)
        if callable(fn):
            return fn()
        return None

    def bs_ui_pause(delay=0.0, hard=False):
        fn = getattr(_renpy_api, "pause", None)
        if callable(fn):
            return fn(delay, hard=hard)
        return None

    def bs_ui_with(trans):
        fn = getattr(_renpy_api, "with_statement", None)
        if callable(fn):
            return fn(trans)
        return None

    def bs_ui_random_int(a, b):
        fn_rand = getattr(_renpy_api, "random", None)
        if fn_rand is not None and hasattr(fn_rand, "randint"):
            return fn_rand.randint(a, b)
        return random.randint(a, b)

    def bs_ui_has_label(name):
        fn = getattr(_renpy_api, "has_label", None)
        if callable(fn):
            return bool(fn(name))
        return False

    def bs_ui_gateway_ensure():
        return True

    # Alias de compat para código legacy existente.
    def ensure_renpy_ui_apis():
        return bs_ui_gateway_ensure()
