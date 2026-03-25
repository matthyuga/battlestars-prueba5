# ===========================================================
# 04B_BATTLE_START.RPY – Inicio y preparación del combate
# ===========================================================
# Versión: v5.2 Resource+Identity+ID Selection + Safe Resets (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Inicializa Reiatsu/Energía del jugador y enemigo
# - Carga fichas desde CHARACTER_DATA (get_character)
# - Selección de enemigo por ID (battle_enemy_id)
# - Identidad dinámica (usa IDs del sistema)
# - Limpieza total de reflejos (store-safe)
# - Resets: focus/boost/costos/logs/operación/tech sequence
# - Sync: battle_turn_owner
# ===========================================================

# ===========================================================
# 🔹 Declaración de fondos de batalla
# ===========================================================
image black    = "images/black.png"
image black2   = "images/black2.png"
image fondo3   = "images/fondo3.png"
image hollow1  = "images/hollow1.png"
image hollow12 = "images/hollow12.png"

# ===========================================================
# 🔹 Desactivar rollback, skip y rueda del ratón
# ===========================================================
init -900 python:
    config.keymap['rollback'] = []
    config.keymap['hide_windows'] = []
    config.keymap['skip'] = []
    config.keymap['fast_skip'] = []
    config.keymap['stop_skipping'] = []
    config.keymap['toggle_skip'] = []
    config.keymap['toggle_afm'] = []


    def bs_prepare_quick_random_1v1(profile_id=None):
        import renpy.store as S
        import renpy.exports as R
        chars = ["Harribel", "Grimmjow", "Nel", "Hollow"]
        try:
            p = R.random.choice(chars)
            e_pool = [c for c in chars if c != p] or chars
            e = R.random.choice(e_pool)
        except Exception:
            p, e = "Harribel", "Hollow"

        S.battle_team_mode = "1v1"
        S.battle_multiplayer_manual = False
        S.battle_player_count = 1
        S.battle_enemy_count = 1
        S.battle_enemy_pick_mode = "random"
        S.battle_player_id = p
        S.battle_enemy_id = e
        S.battle_player_ids = [p]
        S.battle_enemy_ids = [e]
        S.battle_player_slot_0 = p
        S.battle_player_slot_1 = ""
        S.battle_enemy_slot_0 = e
        S.battle_enemy_slot_1 = ""
        S.quick_start_random_1v1 = True
        S.quick_start_random_2v2 = False
        S.ui_safe_mode = True
        S.ui_safe_mode_prompted = True

        pid = str(profile_id or getattr(S, "spa_editor_profile_id", "A") or "A")
        fn_load = getattr(S, "spa_load_profile", None)
        if callable(fn_load):
            try:
                fn_load(pid)
            except Exception:
                pass

    def bs_prepare_quick_random_2v2(profile_id=None):
        import renpy.store as S
        import renpy.exports as R
        chars = ["Harribel", "Grimmjow", "Nel", "Hollow"]
        try:
            pool = list(chars)
            R.random.shuffle(pool)
            p_team = pool[:2]
            e_team = pool[2:4]
            if len(e_team) < 2:
                e_team = list(chars[:2])
        except Exception:
            p_team = ["Harribel", "Grimmjow"]
            e_team = ["Nel", "Hollow"]

        S.battle_team_mode = "2v2"
        S.battle_multiplayer_manual = False
        S.battle_player_count = 2
        S.battle_enemy_count = 2
        S.battle_enemy_pick_mode = "random"
        S.battle_player_id = p_team[0]
        S.battle_enemy_id = e_team[0]
        S.battle_player_ids = list(p_team)
        S.battle_enemy_ids = list(e_team)
        S.battle_player_slot_0 = p_team[0]
        S.battle_player_slot_1 = p_team[1]
        S.battle_enemy_slot_0 = e_team[0]
        S.battle_enemy_slot_1 = e_team[1]
        S.quick_start_random_1v1 = False
        S.quick_start_random_2v2 = True
        S.ui_safe_mode = True
        S.ui_safe_mode_prompted = True

        pid = str(profile_id or getattr(S, "spa_editor_profile_id", "A") or "A")
        fn_load = getattr(S, "spa_load_profile", None)
        if callable(fn_load):
            try:
                fn_load(pid)
            except Exception:
                pass


    config.rollback_enabled = False
    config.hard_rollback_limit = 0

# ===========================================================
# 🔹 Defaults
# ===========================================================
# battle_enemy_id / battle_player_id y modo 2v2 se definen en
# 04A_BATTLE_CHARACTER_SELECTV3.rpy para evitar defaults duplicados.
# (Opcional, recomendado si no los tenés como default en otro lado)
# default battle_player = None
# default battle_enemy  = None


# Inicio rápido para QA: carga 1v1 aleatorio y salta selección.
default quick_start_random_1v1 = False
default quick_start_random_2v2 = False


# ===========================================================
# 🔹 INICIO DEL JUEGO
# ===========================================================
label start:
    scene fondo3 with fade

    # Mostrar log UNA sola vez (evita redundancia/“parpadeo”)
    show screen battle_log_screen

    if quick_start_random_1v1:
        $ quick_start_random_1v1 = False
        jump battle_start
    if quick_start_random_2v2:
        $ quick_start_random_2v2 = False
        jump battle_start

    "Sistema cargado correctamente."

    if not ui_safe_mode_prompted:
        menu:
            "¿Activar modo seguro del HUD?"
            "Sí (panel simple sin PNG)":
                $ ui_safe_mode = True
            "No (HUD visual con PNG)":
                $ ui_safe_mode = False
        $ ui_safe_mode_prompted = True

    call battle_select_player


# ===========================================================
# 🔹 INICIO DEL COMBATE
# ===========================================================
label battle_start:
    $ import random
    $ import renpy.store as S
    $ S.battle_active = True

    # =======================================================
    # 🎯 Selección del enemigo (ID del sistema)
    # =======================================================
    $ enemy_id = getattr(S, "battle_enemy_id", "Hollow")
    $ player_id = getattr(S, "battle_player_id", "Harribel")
    $ battle_team_mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

    # Normalización: el sistema usa "Nel" (Neliel solo display)
    if enemy_id == "Neliel":
        $ enemy_id = "Nel"
        $ S.battle_enemy_id = "Nel"

    # Mantener coherencia con tu core (si existe como default)
    $ battle_reflected_pending = 0

    # -------------------------------------------------------
    # 🧹 Limpieza segura de reflejos previos (STORE-SAFE)
    # -------------------------------------------------------
    if hasattr(S, "reflected_buffer") and hasattr(S.reflected_buffer, "clear"):
        $ S.reflected_buffer.clear()

    if hasattr(S, "enemy_reflect_buffer") and hasattr(S.enemy_reflect_buffer, "clear"):
        $ S.enemy_reflect_buffer.clear()

    # -------------------------------------------------------
    # 🧼 Resets de estado temporal (FOCUS/BOOST/COSTOS/SECUENCIA/OPERACIÓN)
    # -------------------------------------------------------
    # Reseteo oficial de focus/boost + focus_cost_active
    if hasattr(S, "reset_focus_multipliers"):
        $ S.reset_focus_multipliers()

    # Por compatibilidad extra: nunca entrar a combate con costo duplicado
    if hasattr(S, "focus_cost_active"):
        $ S.focus_cost_active = False

    # Reset secuencia de técnicas del turno (si existe)
    if hasattr(S, "battle_reset_tech_sequence"):
        $ S.battle_reset_tech_sequence()
    elif hasattr(S, "battle_turn_tech_sequence"):
        $ S.battle_turn_tech_sequence = []

    # Reset de operación final (si existe)
    if hasattr(S, "operation_clear"):
        $ S.operation_clear()

    # Limpieza de resumen del turno (si existe)
    if hasattr(S, "battle_clear_turn_summary"):
        $ S.battle_clear_turn_summary()

    # Log
    $ battle_log_clear()
    $ battle_log_phase("COMIENZA EL COMBATE")

    # Contador de turnos ofensivos (global por combate)
    $ S.battle_turn_index = 0
    $ S._last_turn_actor_key = ""
    $ S.enemy_pending_damage_by_key = {}
    $ S.player_pending_damage_by_key = {}
    $ S.enemy_pending_def_reduction_by_key = {}
    $ S.player_skip_attack_by_key = {}
    $ S.enemy_skip_attack_by_key = {}
    $ S.counterattack_used_in_battle = False
    $ S.sacrifice_used_in_battle = False
    $ S.sacrifice_receiver_key = ""
    $ S.counterattack_resolution_mode = "dice"


    # =======================================================
    # 🌆 Fondo de batalla aleatorio
    # =======================================================
    $ fondo_random = renpy.random.choice(["black", "black2", "fondo3", "hollow1", "hollow12"])
    scene expression fondo_random

    # =======================================================
    # 👤 Cargar fichas desde CHARACTER_DATA
    # =======================================================
    # IMPORTANTE: get_character debe devolver COPIA (dict) para no contaminar plantillas.
    $ battle_player = get_character(player_id)
    $ battle_enemy  = get_character(enemy_id)

    # Nombre visible (solo UI/logs)
    $ enemy_name = battle_enemy.get("name", enemy_id)
    $ player_name = battle_player.get("name", player_id)

    # =======================================================
    # ⚙️ Variables base (HP inicial) desde CHARACTER_DATA + editor de slots
    # =======================================================
    $ player_hp = get_character_hp(player_id)
    $ enemy_hp  = get_character_hp(enemy_id)

    python:
        import renpy.store as S
        fn_pool = getattr(S, "spa_get_pool_final", None)
        player_coating_cover = int(battle_player.get("coating_cover", 0) or 0)
        enemy_coating_cover = int(battle_enemy.get("coating_cover", 0) or 0)
        player_coating_durability = int(battle_player.get("coating_durability", 0) or 0)
        enemy_coating_durability = int(battle_enemy.get("coating_durability", 0) or 0)
        if callable(fn_pool):
            player_hp = int(fn_pool("player:0", "hp", player_hp) or player_hp)
            enemy_hp = int(fn_pool("enemy:0", "hp", enemy_hp) or enemy_hp)
            player_coating_cover = int(fn_pool("player:0", "coating_cover", player_coating_cover) or player_coating_cover)
            enemy_coating_cover = int(fn_pool("enemy:0", "coating_cover", enemy_coating_cover) or enemy_coating_cover)
            player_coating_durability = int(fn_pool("player:0", "coating_durability", player_coating_durability) or player_coating_durability)
            enemy_coating_durability = int(fn_pool("enemy:0", "coating_durability", enemy_coating_durability) or enemy_coating_durability)

        if bool(getattr(S, "story_mode_active", False)):
            player_coating_cover = 0
            enemy_coating_cover = 0
            player_coating_durability = 0
            enemy_coating_durability = 0

        try:
            battle_player["HP"] = int(player_hp)
            battle_enemy["HP"] = int(enemy_hp)
            battle_player["coating_cover"] = int(player_coating_cover)
            battle_enemy["coating_cover"] = int(enemy_coating_cover)
            battle_player["coating_durability"] = int(player_coating_durability)
            battle_enemy["coating_durability"] = int(enemy_coating_durability)
        except:
            pass

    # Sincronizar máximos globales para HUD, FX y overlays
    $ battle_hp_player_max = player_hp
    $ battle_hp_enemy_max  = enemy_hp
    $ battle_hp_player = player_hp
    $ battle_hp_enemy  = enemy_hp

    # Modelo de equipos/unidades (1v1 compat / 2v2 real)
    python:
        import renpy.store as S
        mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()

        if mode == "2v2" and callable(getattr(S, "bs_init_teams", None)):
            p_ids = list(getattr(S, "battle_player_ids", []) or [])
            e_ids = list(getattr(S, "battle_enemy_ids", []) or [])
            if len(p_ids) < 1:
                p_ids = [str(getattr(S, "battle_player_slot_0", player_id) or player_id)]
            if len(e_ids) < 1:
                e_ids = [str(getattr(S, "battle_enemy_slot_0", enemy_id) or enemy_id)]

            p_units = []
            e_units = []
            fn_pool = getattr(S, "spa_get_pool_final", None)
            for idx, cid in enumerate(p_ids[:2]):
                hp = get_character_hp(cid)
                rei = int(get_character(cid).get("Reiatsu", 0) or 0)
                ene = int(get_character(cid).get("Energy", 0) or 0)
                if callable(fn_pool):
                    ukey = "player:{}".format(idx)
                    hp = int(fn_pool(ukey, "hp", hp) or hp)
                    rei = int(fn_pool(ukey, "reiatsu", rei) or rei)
                    ene = int(fn_pool(ukey, "energy", ene) or ene)
                ccover = int(get_character(cid).get("coating_cover", 0) or 0)
                cdura = int(get_character(cid).get("coating_durability", 0) or 0)
                if callable(fn_pool):
                    ccover = int(fn_pool(ukey, "coating_cover", ccover) or ccover)
                    cdura = int(fn_pool(ukey, "coating_durability", cdura) or cdura)
                if bool(getattr(S, "story_mode_active", False)):
                    ccover = 0
                    cdura = 0
                p_units.append({"char_id": cid, "hp": hp, "max_hp": hp, "reiatsu": rei, "energy": ene, "max_reiatsu": rei, "max_energy": ene, "base_reiatsu": rei, "base_energy": ene, "coating_cover": ccover, "coating_durability_current": cdura, "coating_durability_max": cdura})
            for idx, cid in enumerate(e_ids[:2]):
                hp = get_character_hp(cid)
                rei = int(get_character(cid).get("Reiatsu", 0) or 0)
                ene = int(get_character(cid).get("Energy", 0) or 0)
                if callable(fn_pool):
                    ukey = "enemy:{}".format(idx)
                    hp = int(fn_pool(ukey, "hp", hp) or hp)
                    rei = int(fn_pool(ukey, "reiatsu", rei) or rei)
                    ene = int(fn_pool(ukey, "energy", ene) or ene)
                ccover = int(get_character(cid).get("coating_cover", 0) or 0)
                cdura = int(get_character(cid).get("coating_durability", 0) or 0)
                if callable(fn_pool):
                    ccover = int(fn_pool(ukey, "coating_cover", ccover) or ccover)
                    cdura = int(fn_pool(ukey, "coating_durability", cdura) or cdura)
                if bool(getattr(S, "story_mode_active", False)):
                    ccover = 0
                    cdura = 0
                e_units.append({"char_id": cid, "hp": hp, "max_hp": hp, "reiatsu": rei, "energy": ene, "max_reiatsu": rei, "max_energy": ene, "base_reiatsu": rei, "base_energy": ene, "coating_cover": ccover, "coating_durability_current": cdura, "coating_durability_max": cdura})

            S.bs_init_teams(player_units=p_units, enemy_units=e_units)

            # compat legacy/UI usa unidad activa por lado
            fn_sync = getattr(S, "bs_sync_to_legacy", None)
            if callable(fn_sync):
                fn_sync()

            p_active = getattr(S, "bs_get_active_unit", lambda x: None)("player")
            e_active = getattr(S, "bs_get_active_unit", lambda x: None)("enemy")
            if isinstance(p_active, dict):
                S.battle_player_id = str(p_active.get("char_id", player_id) or player_id)
            if isinstance(e_active, dict):
                S.battle_enemy_id = str(e_active.get("char_id", enemy_id) or enemy_id)
        else:
            fn_init_teams = getattr(S, "bs_init_single_teams", None)
            if callable(fn_init_teams):
                fn_init_teams(
                    player_char_id=player_id,
                    enemy_char_id=enemy_id,
                    player_hp=player_hp,
                    player_max_hp=battle_hp_player_max,
                    enemy_hp=enemy_hp,
                    enemy_max_hp=battle_hp_enemy_max,
                    player_coating_cover=player_coating_cover,
                    player_coating_durability=player_coating_durability,
                    enemy_coating_cover=enemy_coating_cover,
                    enemy_coating_durability=enemy_coating_durability,
                )

        # -------------------------------------------------------
        # Fase 5 — Activación Estamina/Shadow por perks de pre-combate
        # -------------------------------------------------------
        cfg = dict(getattr(S, "precombat_confirmed_loadout", {}) or {})
        perks_v2 = dict(cfg.get("resource_perks_v2", {}) or {})
        perks_v1 = dict(cfg.get("resource_perks", {}) or {})
        perks = dict(perks_v2 or perks_v1)
        if not perks:
            # Compat de migración: snapshots viejos pueden traer solo `specials`.
            specials = [str(x or "") for x in list(cfg.get("specials", []) or [])]
            sset = set(specials)
            perks = {
                "current": {
                    "stamina_enabled": bool(("focus" in sset) or ("ladron_concentrar" in sset) or ("ladron_ofensivo" in sset)),
                    "shadow_active": bool(("salvaguarda_principiante" in sset) or ("defense_boost" in sset)),
                    "shadow_seed_ratio": 0.15 if bool(("salvaguarda_principiante" in sset) or ("defense_boost" in sset)) else 0.0,
                },
                "by_side": {},
            }
        perks_current = dict(perks.get("current", {}) or {})
        perks_by_side = dict(perks.get("by_side", {}) or {})
        mode_now = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
        fn_set_layers = getattr(S, "bs_set_unit_stamina_shadow", None)
        fn_get_unit = getattr(S, "bs_get_unit_by_key", None)
        fn_log = getattr(S, "battle_log_add", None)

        def _norm_perk_cfg(perk_cfg):
            p = dict(perk_cfg or {})
            has_v2 = ("stamina_perk_enabled" in p) or ("shadow_perk_enabled" in p) or ("shadow_target_mode" in p)
            if has_v2:
                stamina_enabled = bool(p.get("stamina_perk_enabled", False))
                shadow_active = bool(p.get("shadow_perk_enabled", False))
                shadow_target_mode = str(p.get("shadow_target_mode", "local") or "local").strip().lower()
                if shadow_target_mode not in ("local", "applied_to_enemy"):
                    shadow_target_mode = "local"
                seed_ratio = float(p.get("shadow_seed_ratio", 0.15 if shadow_active else 0.0) or 0.0)
            else:
                stamina_enabled = bool(p.get("stamina_enabled", False))
                shadow_active = bool(p.get("shadow_active", False))
                shadow_target_mode = "local"
                seed_ratio = float(p.get("shadow_seed_ratio", 0.15 if shadow_active else 0.0) or 0.0)
            return {
                "stamina_enabled": bool(stamina_enabled),
                "shadow_active": bool(shadow_active),
                "shadow_target_mode": shadow_target_mode,
                "shadow_seed_ratio": max(0.0, min(1.0, seed_ratio)),
            }

        def _apply_layer_flags(unit_key, perk_cfg, enemy_unit_key=None):
            if not callable(fn_set_layers):
                return
            p = _norm_perk_cfg(perk_cfg)
            try:
                u = fn_get_unit(unit_key) if callable(fn_get_unit) else None
            except Exception:
                u = None
            mx = 1
            if isinstance(u, dict):
                try:
                    mx = max(1, int(u.get("max_hp", 1) or 1))
                except Exception:
                    mx = 1
            seed_ratio = float(p.get("shadow_seed_ratio", 0.0) or 0.0)
            if seed_ratio < 0.0:
                seed_ratio = 0.0
            if seed_ratio > 1.0:
                seed_ratio = 1.0
            shadow_seed = int(mx * seed_ratio) if bool(p.get("shadow_active", False)) else 0
            shadow_mode = str(p.get("shadow_target_mode", "local") or "local").strip().lower()
            fn_set_layers(
                unit_key,
                stamina_enabled=bool(p.get("stamina_enabled", False)),
                shadow_active=bool(p.get("shadow_active", False)),
                shadow_current=max(0, shadow_seed),
                shadow_cap=mx,
                shadow_target_mode=shadow_mode,
            )

        if mode_now == "2v2":
            _apply_layer_flags("player:0", perks_by_side.get("p1", perks_current), "enemy:0")
            _apply_layer_flags("player:1", perks_by_side.get("p2", perks_current), "enemy:1")
        else:
            _apply_layer_flags("player:0", perks_current, "enemy:0")

        if callable(fn_log):
            try:
                if mode_now == "2v2":
                    p1 = _norm_perk_cfg(perks_by_side.get("p1", perks_current))
                    p2 = _norm_perk_cfg(perks_by_side.get("p2", perks_current))
                    fn_log("{color=#A5D6A7}[PRECOMBAT] Recursos P1(stamina={}, shadow={}, mode={}) | P2(stamina={}, shadow={}, mode={}){/color}".format(
                        int(bool(p1.get("stamina_enabled", False))),
                        int(bool(p1.get("shadow_active", False))),
                        str(p1.get("shadow_target_mode", "local")),
                        int(bool(p2.get("stamina_enabled", False))),
                        int(bool(p2.get("shadow_active", False))),
                        str(p2.get("shadow_target_mode", "local")),
                    ))
                else:
                    pc = _norm_perk_cfg(perks_current)
                    fn_log("{color=#A5D6A7}[PRECOMBAT] Recursos stamina={} shadow={} mode={}{/color}".format(
                        int(bool(pc.get("stamina_enabled", False))),
                        int(bool(pc.get("shadow_active", False))),
                        str(pc.get("shadow_target_mode", "local")),
                    ))
            except Exception:
                pass

    # =======================================================
    # 🏜️ Configuración inicial de ambiente y HUD
    # =======================================================
    $ battle_set_background("harribel")
    $ battle_set_atmosphere("desert")
    $ battle_update_damage_overlay(player_hp, battle_hp_player_max)
    $ battle_update_hp_bars(player_hp, enemy_hp)
    $ battle_show_hud(True)

    # =======================================================
    # 🔋 Inicializar Recursos — Reiatsu/Energía (+ editor por slot)
    # =======================================================
    $ player_reiatsu = battle_player.get("Reiatsu", 0)
    $ player_energy  = battle_player.get("Energy", 0)

    $ enemy_reiatsu  = battle_enemy.get("Reiatsu", 0)
    $ enemy_energy   = battle_enemy.get("Energy", 0)

    $ player_reiatsu_base = player_reiatsu
    $ player_energy_base  = player_energy
    $ enemy_reiatsu_base  = enemy_reiatsu
    $ enemy_energy_base   = enemy_energy

    python:
        import renpy.store as S
        fn_pool = getattr(S, "spa_get_pool_final", None)
        if callable(fn_pool):
            player_reiatsu = int(fn_pool("player:0", "reiatsu", player_reiatsu) or player_reiatsu)
            player_energy = int(fn_pool("player:0", "energy", player_energy) or player_energy)
            enemy_reiatsu = int(fn_pool("enemy:0", "reiatsu", enemy_reiatsu) or enemy_reiatsu)
            enemy_energy = int(fn_pool("enemy:0", "energy", enemy_energy) or enemy_energy)

        # Modo historia piloto: calibración explícita de recursos para tutorial Lv1.
        if bool(getattr(S, "story_mode_active", False)):
            ovr = getattr(S, "story_pilot_resource_override", {}) or {}
            if isinstance(ovr, dict):
                player_hp = int(ovr.get("player_hp", player_hp) or player_hp)
                enemy_hp = int(ovr.get("enemy_hp", enemy_hp) or enemy_hp)
                player_reiatsu = int(ovr.get("player_reiatsu", player_reiatsu) or player_reiatsu)
                player_energy = int(ovr.get("player_energy", player_energy) or player_energy)
                enemy_reiatsu = int(ovr.get("enemy_reiatsu", enemy_reiatsu) or enemy_reiatsu)
                enemy_energy = int(ovr.get("enemy_energy", enemy_energy) or enemy_energy)

        S.player_reiatsu_base = int(player_reiatsu or 0)
        S.player_energy_base = int(player_energy or 0)
        S.enemy_reiatsu_base = int(enemy_reiatsu or 0)
        S.enemy_energy_base = int(enemy_energy or 0)

        try:
            battle_player["Reiatsu"] = int(player_reiatsu)
            battle_player["Energy"] = int(player_energy)
            battle_enemy["Reiatsu"] = int(enemy_reiatsu)
            battle_enemy["Energy"] = int(enemy_energy)
        except:
            pass

        # Mantener battle_state sincronizado (fuente SSOT de consumo).
        fn_set_res = getattr(S, "bs_set_unit_resources", None)
        if callable(fn_set_res):
            fn_set_res("player:0", player_reiatsu, player_energy)
            fn_set_res("enemy:0", enemy_reiatsu, enemy_energy)

    # Re-sincronizar máximos/overlays después de overrides de tutorial.
    $ battle_hp_player_max = max(1, int(player_hp or 1))
    $ battle_hp_enemy_max = max(1, int(enemy_hp or 1))
    $ battle_update_hp_bars(player_hp, enemy_hp)
    $ battle_update_damage_overlay(player_hp, battle_hp_player_max)

    # ⭐ Sincronizar simulación del enemigo
    $ simulated_enemy_reiatsu = enemy_reiatsu
    $ simulated_enemy_energy  = enemy_energy

    $ simulated_reiatsu = player_reiatsu
    $ simulated_energy  = player_energy
    $ simulated_enemy_reiatsu = enemy_reiatsu
    $ simulated_enemy_energy  = enemy_energy

    # ⭐ Sincronizar simulación del jugador
    $ simulated_reiatsu = player_reiatsu
    $ simulated_energy  = player_energy

    python:
        import renpy.store as S

        fn_log = getattr(S, "battle_log_add", None)
        fn_fmt = getattr(S, "battle_fmt_num", None)
        fn_get_unit = getattr(S, "bs_get_unit_by_key", None)
        fn_desc = getattr(S, "bs_describe_unit_key", None)
        fn_slot = getattr(S, "bs_slot_tag", None)

        if not callable(fn_log):
            fn_log = globals().get("battle_log_add", None)

        if not callable(fn_fmt):
            fn_fmt = lambda n: str(int(n or 0))

        def _fmt_res(n):
            try:
                return fn_fmt(int(n or 0))
            except:
                return str(n)

        def _unit_line(unit_key, side, default_name):
            name_txt = str(default_name or unit_key)
            slot_txt = ""
            rei = 0
            ene = 0

            try:
                if callable(fn_desc):
                    name_txt = str(fn_desc(unit_key, default_side=side, default_slot=0) or name_txt)
            except:
                pass

            try:
                if callable(fn_get_unit):
                    u = fn_get_unit(unit_key)
                    if isinstance(u, dict):
                        nm = str(u.get("char_id", "") or "")
                        if nm:
                            name_txt = nm
                        rei = int(u.get("reiatsu", 0) or 0)
                        ene = int(u.get("energy", 0) or 0)
                        if callable(fn_slot):
                            slot_txt = " ({})".format(fn_slot(side, int(u.get("slot", 0) or 0)))
            except:
                pass

            side_lbl = "Equipo Jugador" if str(side) == "player" else "Equipo Enemigo"
            return "{}{} [{}]  Reiatsu {} / Energía {}".format(name_txt, slot_txt, side_lbl, _fmt_res(rei), _fmt_res(ene))

        if callable(fn_log):
            mode = str(getattr(S, "battle_team_mode", "1v1") or "1v1").strip().lower()
            fn_log("{color=#FFFFFF}▸ Recursos iniciales:{/color}", "#FFFFFF")

            if mode == "2v2":
                for key in ("player:0", "player:1", "enemy:0", "enemy:1"):
                    side = "player" if key.startswith("player") else "enemy"
                    fn_log("   {}".format(_unit_line(key, side, key)), "#DDDDDD")
            else:
                fn_log("   {}".format(_unit_line("player:0", "player", str(getattr(S, "battle_player_id", "Jugador") or "Jugador"))), "#DDDDDD")
                fn_log("   {}".format(_unit_line("enemy:0", "enemy", str(getattr(S, "battle_enemy_id", "Enemigo") or "Enemigo"))), "#DDDDDD")

    # =======================================================
    # 🧩 Asignar identidades dinámicas (usar ID, no display)
    # =======================================================
    if hasattr(S, "set_battle_identity"):
        $ S.set_battle_identity(player_id, enemy_id)

    # =======================================================
    # 🧠 Inicializar IA según enemigo elegido (usar ID)
    # =======================================================
    if enemy_id == "Grimmjow":
        $ enemy_ai = BattleAI_Grimmjow("Grimmjow", battle_techniques)
        $ battle_set_atmosphere("arena")

    elif enemy_id == "Nel":
        $ enemy_ai = BattleAI_Nel("Nel", battle_techniques)
        $ battle_set_atmosphere("forest")

    else:
        $ enemy_ai = BattleAI_Hollow("Hollow", battle_techniques)
        $ battle_set_atmosphere("desert")

    # =======================================================
    # 🧩 Panel debug (toggle “T”)
    # =======================================================
    show screen debug_battle_identity

    # =======================================================
    # 🌀 Aparición visual del enemigo (display)
    # =======================================================
    $ battle_popup_turn("¡{} aparece en el campo de batalla!".format(enemy_name), "#FF5555", delay=0.8)

    # =======================================================
    # 🎲 Determinar primer actor del combate
    # =======================================================
    if battle_team_mode == "2v2" and hasattr(S, "bs_set_turn_order_keys"):
        $ _order = ["player:0", "enemy:0", "player:1", "enemy:1"]
        $ _actor_key = S.bs_set_turn_order_keys(_order, start_index=0, mirror_legacy=True)
        $ _ctx_now = S.bs_get_turn_ctx() if hasattr(S, "bs_get_turn_ctx") else {"owner_team": "player", "owner_slot": 0}
        $ _owner_now = str(_ctx_now.get("owner_team", "player") or "player")
    else:
        $ _first_owner = random.choice(["player", "enemy"])
        if hasattr(S, "bs_set_turn_owner"):
            $ S.bs_set_turn_owner(_first_owner, mirror_legacy=True)
        else:
            $ battle_turn_owner = _first_owner
        $ _ctx_now = S.bs_get_turn_ctx() if hasattr(S, "bs_get_turn_ctx") else {"owner_team": getattr(S, "battle_turn_owner", _first_owner), "owner_slot": 0}
        $ _owner_now = _ctx_now.get("owner_team", _first_owner)

    if _owner_now == "player":
        $ battle_popup_turn("¡{} ataca primero!".format(player_name), "#00BFFF", delay=0.8)
        jump battle_offensive_turn

    else:
        if enemy_id == "Grimmjow":
            $ battle_log_add("Grimmjow se prepara para pelear...", "#FF6666")
        elif enemy_id == "Nel":
            $ battle_log_add("Nel sonríe con calma... lista para combatir.", "#99FFFF")
        else:
            $ battle_log_add("Un Hollow salvaje aparece en la Zona.", "#FF8888")

        $ battle_popup_turn("¡{} ataca primero!".format(enemy_name), "#FF5555", delay=0.8)
        jump battle_enemy_turn
