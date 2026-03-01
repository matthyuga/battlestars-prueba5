# ============================================================
# 00_BATTLE_MODE_1V1_ENTRY.rpy – Entry points dedicados 1v1
# ============================================================
# Fase 1 (plan maestro): línea de vida 1v1 explícita.
# Mantiene labels públicas/routing estables y evita acoplar
# accidentalmente decisiones 1v1 a estado 2v2.
# ============================================================

label battle_offensive_turn_1v1_entry:
    python:
        import renpy.store as S
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=player label=battle_offensive_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_offensive_turn_legacy_entry


label battle_enemy_turn_1v1_entry:
    python:
        import renpy.store as S
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=enemy label=battle_enemy_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_enemy_turn_legacy_entry


label battle_defensive_turn_1v1_entry:
    python:
        import renpy.store as S
        try:
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add("{color=#80DEEA}[DEBUG] ROUTE mode=1v1 owner=player label=battle_defensive_turn_legacy_entry{/color}")
        except:
            pass
    jump battle_defensive_turn_legacy_entry
