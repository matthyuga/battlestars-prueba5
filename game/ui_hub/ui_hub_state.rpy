# ui_hub_state.rpy
# Fase 1 de split: estado global / defaults / flags.

default bs_saga_main_menu_enabled = True

default bs_saga_tournament_panel_open = False

default bs_saga_lobby_bottom_tab = "none"
default bs_saga_heroes_tier = "C"
default bs_saga_heroes_franchise = "all"
default bs_saga_catalog_category = "consumibles"
default bs_saga_catalog_group = "pociones"
default bs_saga_tech_catalog_tier = "C"
default bs_saga_tech_catalog_mode = ""
default bs_saga_tech_catalog_type = "ofensivas"
default bs_saga_tower_tier_filter = "ALL"
default bs_saga_tower_selected_floor = 1
default bs_saga_account_state = {
    "account_id": "local_player",
    "display_name": "Mistico",
    "level": 1,
    "exp": 0,
    "exp_to_next": 100,
    "tier": "",
    "gold": 5000,
    "gems": 0
}
default bs_saga_tier_hero_requirements = {
    "C": 9,
    "B": 13,
    "A": 17,
    "S": 13,
    "SS": 9,
    "SSS": 6,
    "IV": 3
}
default bs_saga_tier_level_requirements = {
    "C": 10,
    "B": 20,
    "A": 30,
    "S": 50,
    "SS": 60,
    "SSS": 70,
    "IV": 80
}
default bs_saga_tier_duel_pool = {
    "C": 1000,
    "B": 5000,
    "A": 10000,
    "S": 50000,
    "SS": 100000,
    "SSS": 500000,
    "IV": 1000000
}
default bs_saga_tier_core_stats = {
    "C": {"hp": 5000, "ep": 15000, "ec": 1000, "durability": 0, "cover": 0},
    "B": {"hp": 25000, "ep": 75000, "ec": 5000, "durability": 0, "cover": 0},
    # Nota de balance: para A/S se mantiene HP > durability > cover
    # y relación objetivo durability = cover * 10.
    "A": {"hp": 60000, "ep": 180000, "ec": 10000, "durability": 12000, "cover": 1200},
    "S": {"hp": 350000, "ep": 1000000, "ec": 50000, "durability": 50000, "cover": 5000},
    "SS": {"hp": 700000, "ep": 2000000, "ec": 100000, "durability": 60000, "cover": 60000},
    "SSS": {"hp": 3500000, "ep": 10000000, "ec": 500000, "durability": 300000, "cover": 300000},
    "IV": {"hp": 7000000, "ep": 20000000, "ec": 1000000, "durability": 600000, "cover": 600000}
}
default bs_saga_tier_combat_tuning = {
    "C": {"hp_factor": 5.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "B": {"hp_factor": 5.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "A": {"hp_factor": 6.0, "rest_hp_pct": 0.03, "rest_ep_pct": 0.20, "rest_ec_pct": 0.20, "rest_ec_scales": 2},
    "S": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "SS": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "SSS": {"hp_factor": 7.0, "rest_hp_pct": 0.03},
    "IV": {"hp_factor": 7.0, "rest_hp_pct": 0.03}
}
default bs_saga_damage_coherence_rules = {
    "normal_hit_min_pct": 0.08,
    "normal_hit_max_pct": 0.12,
    "combo_hit_min_pct": 0.18,
    "combo_hit_max_pct": 0.25
}
default bs_saga_heroes_owned = {}
default bs_saga_inventory_state = {
    "account_inventory": {
        "consumables": {},
        "equipables": {},
        "materials": {}
    },
    "hero_inventories": {}
}
default bs_saga_audit_log = []
default bs_saga_last_tx_message = ""
default bs_saga_rotation_hero_ids = []
default bs_saga_prep_duel_rotation_ids = []
default bs_saga_hero_usage_stats = {}
default bs_saga_prep_selected_hero = ""
default bs_saga_prep_selected_mode = "1v1"
default bs_saga_prep_enemy_mode = "random"
default bs_saga_prep_selected_enemy_hero = ""
default bs_saga_prep_selected_build = "balanceado"
default bs_saga_prep_selected_config = "cfg1"
default bs_saga_prep_hp_reward_multiplier = 1
default bs_saga_prep_tech_step = 25
default bs_saga_prep_selected_party_ids = []
default bs_saga_prep_filter_owned_only = False
default bs_saga_prep_flag_item_id = ""
default bs_saga_prep_flag_consumable_id = ""
default bs_saga_prep_intent_duel = False
default bs_saga_prep_context = "room"  # room | config | staging
default bs_saga_prep_config_tab = "resumen"
default bs_saga_heroes_scroll_y = 0.0
default bs_saga_prep_tech_tab = "offensive"
default bs_saga_hero_tech_builds = {}
default bs_saga_dev_admin_enabled = True
default bs_saga_dev_infinite_gold = False
default bs_saga_dev_low_spec_mode = False
default bs_saga_matchmaking_tier_preference = "C"
default bs_saga_dev_gain_exp_base = 90
default bs_saga_dev_gain_gold_base = 150
default bs_saga_dev_gain_variance_pct = 35
default bs_saga_dev_gain_runs = 1

init -899 python:
    def bs_saga_ui_hub_state_split_status_v1():
        return {
            "module": "ui_hub_state",
            "status": "phase_1_done",
            "source_of_truth": "game/ui_hub/ui_hub_state.rpy",
            "next_step": "migrar helpers puros de roster/tech (fase 2)"
        }
