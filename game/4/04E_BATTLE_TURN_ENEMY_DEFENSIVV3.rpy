# ============================================================
# 04E_BATTLE_TURN_ENEMY_DEFENSIV.rpy – Wrapper (NO OVERRIDE)
# v12.2.1 – Safe Wrapper (NO STORE CLobber) ✅
# ------------------------------------------------------------
# ✔ Mantiene compatibilidad con llamados antiguos.
# ✅ IMPORTANTE: NO pisa enemy_compute_reactive_defense().
# ✅ Si alguien necesita legacy: use enemy_compute_reactive_defense_legacy().
# ============================================================

init -984 python:
    import renpy.store as S

    def enemy_compute_reactive_defense_legacy(total_damage):
        """
        Wrapper legacy:
        - Llama a la función REAL si existe en store.
        - Si no está disponible, devuelve fallback seguro.
        """
        # 1) Preferir función real del store (la del orchestrator)
        fn = getattr(S, "enemy_compute_reactive_defense", None)

        # ⚠️ Si fn es ESTE wrapper (por cualquier motivo), ignorarlo
        try:
            if callable(fn) and getattr(fn, "__name__", "") == "enemy_compute_reactive_defense_legacy":
                fn = None
        except:
            fn = None

        if callable(fn):
            try:
                return fn(total_damage)
            except:
                pass

        # 2) Fallback: no romper
        try:
            dmg = int(total_damage or 0)
        except:
            dmg = 0
        return {"final_damage": dmg, "reflected": 0}

    # Export opcional por nombre distinto (para debug / llamadas explícitas)
    try:
        S.enemy_compute_reactive_defense_legacy = enemy_compute_reactive_defense_legacy
    except:
        pass
