# ui_hub_tech_service.rpy
# Scaffold de división: pool técnico, técnicas permitidas y display names.

init -899 python:
    def bs_saga_ui_hub_tech_split_status_v1():
        return {
            "module": "ui_hub_tech_service",
            "status": "scaffold",
            "target_symbols": [
                "bs_saga_tier_allowed_tech_ids",
                "bs_saga_tech_display_name",
                "bs_saga_recalc_tech_pool_spent",
                "bs_saga_hero_tech_profile_get",
                "bs_saga_resolve_hero_tech_profile"
            ]
        }
