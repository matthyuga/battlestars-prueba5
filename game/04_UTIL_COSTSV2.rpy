# ===========================================================
# 04_UTIL_COSTS.RPY – Utilidades de costos (SSoT-friendly)
# ===========================================================
# - NO usa TECH_COSTS (legacy)
# - Usa get_tech_costs / get_tech_costs_final si existe
# - mult se usa para Focus (x2/x4/x8)
# ===========================================================

init python:
    import renpy.store as store

    def get_final_rei_cost(tech_id, mult=1):
        """
        Devuelve el costo FINAL de Reiatsu.
        - Si existe get_tech_costs_final: la usa.
        - Si no existe, usa get_tech_costs + aplica mult.
        - Energía NO se aplica aquí (solo Reiatsu).
        """
        # Normalizar mult
        try:
            mult = int(mult or 1)
        except:
            mult = 1
        if mult < 1:
            mult = 1

        # Preferir función final si existe
        fn_final = getattr(store, "get_tech_costs_final", None)
        if fn_final:
            try:
                data = fn_final(tech_id, mult=mult) or {}
                return int(data.get("reiatsu", 0))
            except:
                return 0

        # Fallback: base + mult
        fn_base = getattr(store, "get_tech_costs", None)
        if not fn_base:
            return 0

        try:
            base = fn_base(tech_id) or {}
            rei = int(base.get("reiatsu", 0))
            return rei * mult
        except:
            return 0
