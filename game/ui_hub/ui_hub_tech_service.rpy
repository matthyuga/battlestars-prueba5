# ui_hub_tech_service.rpy
# Fase 2 de split: helpers puros de técnicas/pool.

init -880 python:
    import renpy.store as S

    def bs_saga_tier_allowed_tech_ids(tier):
        t = str(tier or "C").strip().upper()
        table = {
            "C": ["stronger_attack", "defense_strong_block", "direct_attack", "focus", "defense_boost", "fury_dice"],
            "B": ["extra_attack", "defense_extra", "focus", "defense_boost", "fury_dice"],
            "A": ["extra_tech", "attack_reducer", "defense_reducer", "focus", "defense_boost", "fury_dice"],
            "S": ["noatk_attack", "defense_reflect", "focus", "defense_boost", "fury_dice"],
        }
        ids = list(table.get(t, table.get("C", [])))
        out = []
        for x in ids:
            k = str(x or "").strip()
            if k and k not in out:
                out.append(k)
        return out

    def bs_saga_tech_display_name(tech_id):
        key = str(tech_id or "").strip()
        bt = getattr(S, "battle_techniques", {}) or {}
        row = bt.get(key, {}) if isinstance(bt, dict) else {}
        if isinstance(row, dict):
            nm = str(row.get("name", "") or "").strip()
            if nm:
                return nm.replace("{", "{{").replace("}", "}}")
        return key.replace("{", "{{").replace("}", "}}")

    def bs_saga_is_point_alloc_tech(tech_id):
        key = str(tech_id or "").strip().lower()
        if not key:
            return False
        bt = getattr(S, "battle_techniques", {}) or {}
        row = bt.get(key, {}) if isinstance(bt, dict) else {}
        if not isinstance(row, dict):
            return False
        ttype = str(row.get("type", "") or "").strip().lower()
        # Fase 2: solo ofensivas/defensivas consumen puntos.
        return ttype in ("offensive", "defensive")

    def bs_saga_ui_hub_tech_split_status_v1():
        return {
            "module": "ui_hub_tech_service",
            "status": "phase_2_done",
            "migrated_symbols": [
                "bs_saga_tier_allowed_tech_ids",
                "bs_saga_tech_display_name",
                "bs_saga_is_point_alloc_tech"
            ],
            "next_symbols": [
                "bs_saga_recalc_tech_pool_spent",
                "bs_saga_hero_tech_profile_get",
                "bs_saga_resolve_hero_tech_profile"
            ]
        }
