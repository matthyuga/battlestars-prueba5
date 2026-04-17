# ui_hub_screens_lobby.rpy
# Scaffold de división: lobby principal y paneles.

init -899 python:
    def bs_saga_ui_hub_lobby_screen_split_status_v1():
        return {
            "module": "ui_hub_screens_lobby",
            "status": "scaffold",
            "target_screens": [
                "bs_saga_lobby",
                "paneles de perfil/tienda/inventario/catálogo"
            ]
        }
