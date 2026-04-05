# ===========================================================
# 99_AUTOCLEANER.RPY – Limpieza automática de .rpyc al cerrar
# ===========================================================
# Compatible con Ren'Py 7.4.9+
# -----------------------------------------------------------

init -990 python:
    import os

    def tg_cleanup_rpyc_on_quit():
        """Elimina .rpyc dentro de /game al cerrar el juego."""
        try:
            game_path = config.gamedir
            print("[AutoCleaner] Cerrando juego, limpiando .rpyc...")

            removed = 0
            for root, _dirs, files in os.walk(game_path):
                for file_name in files:
                    if file_name.endswith(".rpyc"):
                        file_path = os.path.join(root, file_name)
                        try:
                            os.remove(file_path)
                            removed += 1
                        except Exception as e:
                            print("[AutoCleaner] No se pudo borrar {} -> {}".format(file_path, e))

            print("[AutoCleaner] Limpieza finalizada. .rpyc borrados: {}".format(removed))
        except Exception as e:
            print("[AutoCleaner] Error general:", e)

    # Ejecutar al salir del juego
    if hasattr(config, "quit_callbacks"):
        config.quit_callbacks.append(tg_cleanup_rpyc_on_quit)
