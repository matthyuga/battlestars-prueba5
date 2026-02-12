# ===========================================================
# 04_BATTLE_CORE_INIT.RPY – Índice central del sistema de batalla
# ===========================================================
# Carga y orden de los módulos principales:
#  - 04a_BATTLE_FALLBACKS_FX.RPY   → funciones y efectos globales
#  - 04b_BATTLE_START.RPY          → inicio y preparación
#  - 04c_BATTLE_TURN_OFFENSIVE.RPY → turno ofensivo del jugador
#  - 04d_BATTLE_TURN_DEFENSIVE.RPY → turno defensivo del enemigo
#  - 04e_BATTLE_END_RESULT.RPY     → cierre del combate
# -----------------------------------------------------------
# Ren'Py 7.4.9 Compatible
# ===========================================================

init -990 python:
    import renpy.store as store

    battle_version = "v2.17 Modular Phase Sync Edition"
    store.battle_version = battle_version

    # Log seguro (no crashea si renpy.log cambia)
    try:
        renpy.exports.log("[Battle System] Cargado correctamente ({}).".format(battle_version))
    except:
        try:
            renpy.log("[Battle System] Cargado correctamente ({}).".format(battle_version))
        except:
            pass

