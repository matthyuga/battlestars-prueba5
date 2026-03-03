# ============================================================
# battle_turn_contract.rpy — Contrato público de turnos
# ============================================================
# SSOT de entradas públicas:
#   - battle_offensive_turn
#   - battle_enemy_turn
#   - battle_defensive_turn
#
# Regla:
# - Las labels públicas se declaran en `game/zz_battle_label_guard.rpy`
#   y SIEMPRE delegan a `*_router_entry`.
# - Las implementaciones legacy reales viven en:
#   - battle_offensive_turn_legacy_entry
#   - battle_enemy_turn_legacy_entry
#   - battle_defensive_turn_legacy_entry
# ============================================================

default battle_debug_routes = False


init -960 python:
    BATTLE_PUBLIC_TURN_LABELS = (
        "battle_offensive_turn",
        "battle_enemy_turn",
        "battle_defensive_turn",
    )

    BATTLE_LEGACY_TURN_LABELS = (
        "battle_offensive_turn_legacy_entry",
        "battle_enemy_turn_legacy_entry",
        "battle_defensive_turn_legacy_entry",
    )

    def bs_route_debug_enabled():
        try:
            import renpy.store as S
            return bool(getattr(S, "battle_debug_routes", False))
        except Exception:
            return False

    def bs_log_turn_contract(route_label, mode, owner=None, target=None, phase=None):
        """Log uniforme para trazabilidad de router por modo."""
        try:
            import renpy.store as S
            if not bs_route_debug_enabled():
                return
            if callable(getattr(S, "battle_log_add", None)):
                S.battle_log_add(
                    "{color=#80DEEA}[DEBUG] ROUTE mode=%s phase=%s owner=%s target=%s label=%s{/color}" % (
                        str(mode or "?"),
                        str(phase or "?"),
                        str(owner or "?"),
                        str(target or "auto"),
                        str(route_label or "?"),
                    )
                )
        except Exception:
            pass
