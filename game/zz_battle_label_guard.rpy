# ============================================================
# zz_battle_label_guard.rpy – Guard final de labels públicas
# ============================================================
# Se carga al final para garantizar que las labels públicas
# apunten siempre al router, incluso si existen definiciones
# legacy residuales en builds/cache antiguos.
# ============================================================

init 999 python:
    def _zz_is_2v2_mode():
        try:
            import renpy.store as S
            return str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower() == "2v2"
        except:
            return False


label battle_offensive_turn:
    jump battle_public_offensive_adapter


label battle_enemy_turn:
    jump battle_public_enemy_adapter


label battle_defensive_turn:
    jump battle_public_defensive_adapter
