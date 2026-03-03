# ===========================================================
# 00_GLOBALS_TURNSTATE.rpy – Estado global de turno/fase
# Versión: v1.1 Stable Default + Constants Edition
# -----------------------------------------------------------
# - Usa `default` (save/rollback safe)
# - Evita `global` usando `renpy.store`
# - Constantes para evitar typos ("offensive"/"defensive")
# - Normalización de estado (anti-valores inválidos)
# ===========================================================

# ------------------------------
# Defaults (persisten en saves)
# ------------------------------
default battle_turn_no = 1               # 1,2,3...
default battle_actor   = "player"        # "player" | "enemy"
default battle_phase   = "offensive"     # "offensive" | "defensive"

init -995 python:
    import renpy.store as store

    # ------------------------------
    # Constantes (evitan typos)
    # ------------------------------
    ACTOR_PLAYER = "player"
    ACTOR_ENEMY  = "enemy"

    PHASE_OFFENSIVE = "offensive"
    PHASE_DEFENSIVE = "defensive"

    store.ACTOR_PLAYER = ACTOR_PLAYER
    store.ACTOR_ENEMY  = ACTOR_ENEMY
    store.PHASE_OFFENSIVE = PHASE_OFFENSIVE
    store.PHASE_DEFENSIVE = PHASE_DEFENSIVE

    # ------------------------------
    # Normalización (robustez)
    # ------------------------------
    def battle_turnstate_normalize():
        """
        Corrige valores inválidos si vienen de un save viejo
        o si algún bug los dejó en un estado no permitido.
        """
        if store.battle_actor not in (ACTOR_PLAYER, ACTOR_ENEMY):
            store.battle_actor = ACTOR_PLAYER

        if store.battle_phase not in (PHASE_OFFENSIVE, PHASE_DEFENSIVE):
            store.battle_phase = PHASE_OFFENSIVE

        try:
            store.battle_turn_no = max(1, int(store.battle_turn_no))
        except:
            store.battle_turn_no = 1

    store.battle_turnstate_normalize = battle_turnstate_normalize

    # ------------------------------
    # Avanzar fase/turno
    # ------------------------------
    def battle_next_phase():
        """
        Alterna entre:
        offensive -> defensive (reacción del rival)
        defensive -> offensive (nuevo turno del otro actor)
        """
        battle_turnstate_normalize()

        if store.battle_phase == PHASE_OFFENSIVE:
            store.battle_phase = PHASE_DEFENSIVE
        else:
            store.battle_phase = PHASE_OFFENSIVE
            store.battle_actor = ACTOR_ENEMY if store.battle_actor == ACTOR_PLAYER else ACTOR_PLAYER
            store.battle_turn_no += 1

    store.battle_next_phase = battle_next_phase

    # ------------------------------
    # Consultas
    # ------------------------------
    def battle_phase_is(actor, phase):
        battle_turnstate_normalize()
        return store.battle_actor == actor and store.battle_phase == phase

    store.battle_phase_is = battle_phase_is
