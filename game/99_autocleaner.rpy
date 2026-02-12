# ===========================================================
# 99_AUTOCLEANER.RPY – Limpieza automática al iniciar el juego
# ===========================================================
# Compatible con Ren'Py 7.4.9+
# Limpia: .rpyc, /cache y /saves
# ===========================================================

init -990 python:
    import os, shutil

    def limpiar_entorno():
        """Elimina .rpyc, cache y saves al iniciar el juego."""
        try:
            game_path = config.gamedir
            base_path = config.basedir
            cache_folder = os.path.join(base_path, "cache")
            saves_folder = os.path.join(base_path, "saves")

            print("[AutoCleaner] Iniciando limpieza...")

            # --- 1. Eliminar archivos .rpyc ---
            for root, dirs, files in os.walk(game_path):
                for file in files:
                    if file.endswith(".rpyc"):
                        try:
                            os.remove(os.path.join(root, file))
                        except Exception as e:
                            print("[AutoCleaner] Error al borrar", file, "->", e)

            # --- 2. Eliminar carpeta cache ---
            if os.path.exists(cache_folder):
                shutil.rmtree(cache_folder, ignore_errors=True)
                print("[AutoCleaner] Carpeta 'cache' eliminada.")

            # --- 3. Eliminar carpeta saves ---
            if os.path.exists(saves_folder):
                shutil.rmtree(saves_folder, ignore_errors=True)
                print("[AutoCleaner] Carpeta 'saves' eliminada.")

            print("[AutoCleaner] Limpieza completada.")

        except Exception as e:
            print("[AutoCleaner] Error general:", e)


# -----------------------------------------------------------
# Ejecutar limpieza apenas se inicia el juego (una sola vez)
# -----------------------------------------------------------
label before_main_menu:
    $ limpiar_entorno()
    return
