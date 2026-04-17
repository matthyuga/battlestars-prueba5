# ui_hub_state.rpy
# Scaffold de división: estado global / defaults / flags.
#
# Nota: por ahora las variables `default` siguen en
# `12_BATTLESTARS_SAGA_UI_HUB_V1.rpy` para no romper compatibilidad.

init -899 python:
    import renpy.store as S

    def bs_saga_ui_hub_state_split_status_v1():
        return {
            "module": "ui_hub_state",
            "status": "scaffold",
            "source_of_truth": "game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy",
            "next_step": "mover defaults/flags en bloque controlado"
        }
