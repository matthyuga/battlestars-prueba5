# ui_hub_screens_prep.rpy
# Scaffold de división: screen de preparación y subcomponentes.

init -899 python:
    def bs_saga_ui_hub_prep_screen_split_status_v1():
        return {
            "module": "ui_hub_screens_prep",
            "status": "scaffold",
            "target_screens": [
                "bs_saga_preparation_room_screen",
                "bloques de roster/config/loadout/tech-pool"
            ]
        }
