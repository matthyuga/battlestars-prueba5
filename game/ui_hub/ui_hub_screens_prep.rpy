# ui_hub_screens_prep.rpy
# Fase 3 de split: pantallas de preparación/pre-combate.

screen bs_saga_preparation_room_screen():
    tag menu
    $ _rows = bs_saga_preparation_rows_filtered()
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _party = [str(x) for x in (bs_saga_prep_selected_party_ids or []) if str(x)]
    $ _party_txt = ", ".join(_party) if _party else "sin equipo"
    $ _j1 = str(_party[0] if len(_party) > 0 else (_hero if _hero else ""))
    $ _j2 = str(_party[1] if len(_party) > 1 else "")
    $ _owned_only = bool(bs_saga_prep_filter_owned_only)
    $ _slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _hero_tier = bs_saga_hero_tier(_hero, "C") if _hero else ""
    $ _pool_tier = bs_saga_prep_pool_tier_for_hero(_hero) if _hero else "C"
    $ _rotation_tier = bs_saga_rotation_tier_current() if _hero else "C"
    $ _pool_gate = bs_saga_pool_gate_status_for_hero(_hero) if _hero else {"pool_locked_by_collection": False}
    $ _pool_locked = bool(_pool_gate.get("pool_locked_by_collection", False)) if _hero else False
    $ _gate_smoke = bs_saga_tier_gate_smoke_report(_hero) if _hero else {"checks": [], "ok": True}
    $ _tier_pool = bs_saga_tier_pool_total(_pool_tier) if _hero else 0
    $ _tier_stats = bs_saga_tier_core_profile(_pool_tier) if _hero else {"hp":0,"ep":0,"ec":0,"durability":0,"cover":0}
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _pool_total_cfg = int(_tech_prof.get("pool_total", 0) or 0) if _hero else 0
    $ _spent_cfg = int(_tech_prof.get("pool_spent_off", 0) or 0) + int(_tech_prof.get("pool_spent_def", 0) or 0) if _hero else 0
    $ _pool_left_cfg = max(0, _pool_total_cfg - _spent_cfg)
    $ _loadout_count = len([x for x in _slots if str(x or "").strip()]) if _hero else 0
    $ _rotation_preview = ", ".join([str(x) for x in (bs_saga_prep_duel_rotation_ids or [])[:5]])

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Sala de preparación" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Return("nav:lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 560
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 620
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Roster disponible (rotación o adquirido)" size 22 color "#EAF6FF"
                    text ("Héroes listados: " + str(len(_rows))) size 14 color "#9FC4E2"
                    text ("Rotación actual (5): " + (_rotation_preview if _rotation_preview else "sin generar")) size 14 color "#9FC4E2"
                    textbutton ("Filtro adquiridos: " + ("ON" if _owned_only else "OFF")):
                        action ToggleVariable("bs_saga_prep_filter_owned_only")
                    textbutton "Aleatorizar rotación":
                        action Function(bs_saga_ui_call, bs_saga_refresh_duel_rotation_heroes, 5)
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 390
                        vbox:
                            spacing 6
                            if _rows:
                                for row in _rows:
                                    $ _hid = str(row.get("hero_id", ""))
                                    $ _name = str(row.get("name", _hid) or _hid)
                                    $ _is_av = bool(row.get("available", False))
                                    $ _state = str(row.get("state", "bloqueado"))
                                    $ _tag = "Disponible" if _state == "disponible" else ("Para probar" if _state == "para_probar" else "Bloqueado")
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (8, 6)
                                        hbox:
                                            spacing 8
                                            text (_name + " (" + str(row.get("tier", "C")) + ")") size 17 color "#D0E9FF" xminimum 300
                                            text _tag size 16 color ("#8BD6A7" if _state == "disponible" else ("#FFD166" if _state == "para_probar" else "#FF9F9F")) xminimum 120
                                            if _hero == _hid:
                                                text "J1 activo" size 16 color "#F7D774"
                                            elif _is_av:
                                                textbutton "Asignar J1":
                                                    action Function(bs_saga_ui_call, bs_saga_set_prep_hero, _hid)
                                            if _is_av and _mode == "2v2" and _hid != _hero:
                                                textbutton ("Quitar J2" if _hid == _j2 else "Asignar J2"):
                                                    action Function(bs_saga_ui_call, bs_saga_toggle_prep_party_hero, _hid)
                            else:
                                text "No hay roster cargado." size 18 color "#9FB9D1"
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 528
                    vbox:
                        spacing 8
                        text "Configuración de entrada" size 22 color "#EAF6FF"
                        text ("Jugador 1 (activo): " + (_hero if _hero else "sin seleccionar")) size 16 color "#CFE6FA"
                        text ("Alineación del duelo: " + _party_txt) size 14 color "#9FC4E2"
                        if _mode == "2v2":
                            text ("Casillas · J1: " + (_j1 if _j1 else "—") + " · J2: " + (_j2 if _j2 else "—")) size 14 color "#A9CAE6"
                            frame:
                                xfill True
                                background Solid("#173048")
                                padding (8, 6)
                                vbox:
                                    spacing 6
                                    text ("Jugador 1: " + (_j1 if _j1 else "vacío")) size 14 color "#D0E9FF"
                                    text ("Jugador 2: " + (_j2 if _j2 else "vacío")) size 14 color "#D0E9FF"
                                    hbox:
                                        spacing 6
                                        textbutton "Promover J2 → J1":
                                            action Function(bs_saga_ui_call, bs_saga_promote_prep_j2_to_j1)
                                        textbutton "Quitar J2":
                                            action Function(bs_saga_ui_call, bs_saga_clear_prep_j2_slot)
                        text ("Config activa: " + _cfg.upper()) size 14 color "#9FC4E2"
                        text ("Build activa: " + _build) size 14 color "#9FC4E2"
                        if _hero:
                            text ("Tier héroe: " + _hero_tier + " · Tier rotación (nivel): " + _rotation_tier + " · Tier cuenta/pool: " + _pool_tier + " · Pool duelo: " + str(_tier_pool)) size 14 color "#9FC4E2"
                            if _pool_locked:
                                text ("⚠ Pool bloqueado por colección: puedes usar rotación de tier " + _rotation_tier + ", pero el pool sigue en tier cuenta " + _pool_tier + ".") size 13 color "#FFD166"
                            text ("HP " + str(_tier_stats.get("hp", 0)) + " · EP " + str(_tier_stats.get("ep", 0)) + " · EC " + str(_tier_stats.get("ec", 0))) size 14 color "#9FC4E2"
                            text ("Durabilidad " + str(_tier_stats.get("durability", 0)) + " · Cubre " + str(_tier_stats.get("cover", 0))) size 14 color "#9FC4E2"
                            text ("Modo técnico: " + str(_tech_prof.get("mode", "virgen")) + " · Pool técnico " + str(_pool_total_cfg)) size 14 color "#9FC4E2"
                            text ("Pool técnico usado/libre: " + str(_spent_cfg) + "/" + str(_pool_total_cfg) + " · Libre " + str(_pool_left_cfg)) size 14 color "#9FC4E2"
                            text ("Loadout: " + str(_loadout_count) + "/6 slots equipados") size 14 color "#9FC4E2"
                            if bool(getattr(store, "bs_saga_dev_admin_enabled", False)):
                                text ("QA gates: " + ("OK" if bool(_gate_smoke.get("ok", False)) else "WARN")) size 13 color ("#8BD6A7" if bool(_gate_smoke.get("ok", False)) else "#FFD166")
                            null height 6
                            text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"
                            textbutton "Configurar héroe":
                                action Return("nav:config")
                            textbutton "Ir a pre-combate":
                                action Return("nav:staging")
                        else:
                            text "Selecciona un héroe para ver el resumen y continuar." size 14 color "#9FB9D1"

    frame:
        xalign 0.5
        yalign 0.96
        xsize 1120
        ypadding 8
        background Solid("#13273A")
        hbox:
            xfill True
            textbutton "Ir a sala de pre-combate":
                xalign 1.0
                action Return("nav:staging")

screen bs_saga_hero_config_screen():
    tag menu
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _tab = str(bs_saga_prep_config_tab or "resumen")
    $ _equipables = bs_saga_prep_inventory_candidates("equipables")
    $ _slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _loadout_count = len([x for x in _slots if str(x or "").strip()]) if _hero else 0
    $ _party = [str(x) for x in (bs_saga_prep_selected_party_ids or []) if str(x)]
    $ _j1 = str(_party[0] if len(_party) > 0 else (_hero if _hero else ""))
    $ _j2 = str(_party[1] if len(_party) > 1 else "")
    $ _hero_tier = bs_saga_hero_tier(_hero, "C") if _hero else "C"
    $ _pool_tier = bs_saga_prep_pool_tier_for_hero(_hero) if _hero else "C"
    $ _rotation_tier = bs_saga_rotation_tier_current() if _hero else "C"
    $ _pool_gate = bs_saga_pool_gate_status_for_hero(_hero) if _hero else {"pool_locked_by_collection": False}
    $ _pool_locked = bool(_pool_gate.get("pool_locked_by_collection", False)) if _hero else False
    $ _gate_smoke = bs_saga_tier_gate_smoke_report(_hero) if _hero else {"checks": [], "ok": True}
    $ _tier_pool = bs_saga_tier_pool_total(_pool_tier) if _hero else 0
    $ _tier_stats = bs_saga_tier_core_profile(_hero_tier) if _hero else {"hp":0,"ep":0,"ec":0,"durability":0,"cover":0}
    $ _tier_tuning = bs_saga_tier_combat_tuning_profile(_hero_tier) if _hero else {"hp_factor":0.0,"rest_hp_pct":0.0,"rest_ep_pct":0.0,"rest_ec_pct":0.0,"rest_ec_scales":0}
    $ _dmg_rules = dict(bs_saga_damage_coherence_rules or {})
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _tier_allowed = bs_saga_tier_allowed_tech_ids(_hero_tier) if _hero else []
    $ _tier_point_alloc = [tid for tid in _tier_allowed if bs_saga_is_point_alloc_tech(tid)]
    $ _tier_special = [tid for tid in _tier_allowed if tid not in _tier_point_alloc]
    $ _tp_map = dict(_tech_prof.get("tech_points", {}) or {}) if _hero else {}
    $ _tech_step = bs_saga_clamp_prep_tech_step(getattr(store, "bs_saga_prep_tech_step", 25))
    $ _pool_total_cfg = int(_tech_prof.get("pool_total", 0) or 0) if _hero else 0
    $ _spent_cfg = int(_tech_prof.get("pool_spent_off", 0) or 0) + int(_tech_prof.get("pool_spent_def", 0) or 0) if _hero else 0
    $ _pool_left_cfg = max(0, _pool_total_cfg - _spent_cfg)

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Configurar héroe" size 22 color "#D7EEFF" yalign 0.7
            null width 140
            textbutton "Volver al lobby" action Return("nav:lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (14, 14)
        background Solid("#13273A")
        vbox:
            spacing 10
            text ("Jugador 1: " + (_hero if _hero else "sin seleccionar") + " · Tier héroe " + _hero_tier + " · Tier rotación " + _rotation_tier + " · Pool tier cuenta " + _pool_tier + " (" + str(_tier_pool) + ")") size 18 color "#CFE6FA"
            if _mode == "2v2":
                text ("Casillas · J1: " + (_j1 if _j1 else "—") + " · J2: " + (_j2 if _j2 else "—")) size 14 color "#A9CAE6"
                hbox:
                    spacing 6
                    textbutton "Promover J2 → J1":
                        action Function(bs_saga_ui_call, bs_saga_promote_prep_j2_to_j1)
                    textbutton "Quitar J2":
                        action Function(bs_saga_ui_call, bs_saga_clear_prep_j2_slot)
            if _hero and _pool_locked:
                text ("⚠ Pool bloqueado por colección mínima del tier. Rotación desbloqueada por nivel, pool aún en " + _pool_tier + ".") size 14 color "#FFD166"
            if _hero and bool(getattr(store, "bs_saga_dev_admin_enabled", False)):
                text ("QA gates: " + ("OK" if bool(_gate_smoke.get("ok", False)) else "WARN")) size 13 color ("#8BD6A7" if bool(_gate_smoke.get("ok", False)) else "#FFD166")
            hbox:
                spacing 6
                textbutton "Resumen" action SetVariable("bs_saga_prep_config_tab", "resumen")
                textbutton "Técnicas" action SetVariable("bs_saga_prep_config_tab", "tecnicas")
                textbutton "Equipamiento" action SetVariable("bs_saga_prep_config_tab", "equipamiento")
                textbutton "Build" action SetVariable("bs_saga_prep_config_tab", "build")
                textbutton "CFG" action SetVariable("bs_saga_prep_config_tab", "cfg")

            frame:
                xfill True
                ysize 360
                background Solid("#102438")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 340
                    vbox:
                        spacing 8
                        if not _hero:
                            text "Selecciona un héroe en Sala de preparación para editar configuración." size 16 color "#9FB9D1"
                        elif _tab == "resumen":
                            text "Resumen de configuración" size 21 color "#EAF6FF"
                            text ("Config: " + _cfg.upper() + " · Build: " + _build + " · Modo: " + _mode) size 14 color "#9FC4E2"
                            text ("HP " + str(_tier_stats.get("hp", 0)) + " · EP " + str(_tier_stats.get("ep", 0)) + " · EC " + str(_tier_stats.get("ec", 0))) size 14 color "#9FC4E2"
                            text ("Durabilidad " + str(_tier_stats.get("durability", 0)) + " · Cubre " + str(_tier_stats.get("cover", 0))) size 14 color "#9FC4E2"
                            text ("Factor HP/Pool x" + str(_tier_tuning.get("hp_factor", 0.0)) + " · Descansar HP " + str(int(float(_tier_tuning.get("rest_hp_pct", 0.0)) * 100)) + "%") size 14 color "#9FC4E2"
                            text ("Descansar EP " + str(int(float(_tier_tuning.get("rest_ep_pct", 0.0)) * 100)) + "% · EC " + str(int(float(_tier_tuning.get("rest_ec_pct", 0.0)) * 100)) + "% (+ " + str(int(_tier_tuning.get("rest_ec_scales", 0) or 0)) + " escalas)") size 14 color "#9FC4E2"
                            text ("Daño normal objetivo " + str(int(float(_dmg_rules.get("normal_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("normal_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Daño combo objetivo " + str(int(float(_dmg_rules.get("combo_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("combo_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Pool técnico usado/libre: " + str(_spent_cfg) + "/" + str(_pool_total_cfg) + " · Libre " + str(_pool_left_cfg)) size 14 color "#9FC4E2"
                            text ("Loadout equipado: " + str(_loadout_count) + "/6") size 14 color "#9FC4E2"
                        elif _tab == "tecnicas":
                            text "Técnicas y pool técnico" size 21 color "#EAF6FF"
                            hbox:
                                spacing 6
                                textbutton "Téc. Preconfig" action Function(bs_saga_ui_call, bs_saga_hero_tech_mode_set, _hero, "preconfig", _cfg, _build)
                            text ("Paso asignación: +" + str(_tech_step) + " / -" + str(_tech_step)) size 14 color "#9FC4E2"
                            hbox:
                                spacing 4
                                textbutton "25" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 25)
                                textbutton "50" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 50)
                                textbutton "100" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 100)
                                textbutton "150" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 150)
                                textbutton "200" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 200)
                                textbutton "500" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 500)
                                textbutton "1000" action Function(bs_saga_ui_call, bs_saga_set_prep_tech_step, 1000)
                            text ("Pool técnico cfg/build: " + str(_spent_cfg) + "/" + str(_pool_total_cfg) + " · Libre: " + str(_pool_left_cfg)) size 14 color "#9FC4E2"
                            if _tier_point_alloc:
                                text "Técnicas con puntos (ofensivas/defensivas)" size 15 color "#D0E9FF"
                                for _tid in _tier_point_alloc:
                                    $ _pts = int(_tp_map.get(_tid, 0) or 0)
                                    hbox:
                                        spacing 6
                                        text (bs_saga_tech_display_name(_tid) + " [" + str(_pts) + "]") substitute False size 14 color "#CFE6FA" xminimum 320
                                        textbutton ("+" + str(_tech_step)):
                                            action Function(bs_saga_ui_call, bs_saga_hero_tech_points_add, _hero, _tid, +_tech_step, _cfg, _build)
                                        textbutton ("-" + str(_tech_step)):
                                            action Function(bs_saga_ui_call, bs_saga_hero_tech_points_add, _hero, _tid, -_tech_step, _cfg, _build)
                            else:
                                text "Sin técnicas ofensivas/defensivas asignables para este tier." size 14 color "#9FB9D1"
                            if _tier_special:
                                null height 6
                                text "Técnicas especiales (sin asignación de puntos)" size 15 color "#D0E9FF"
                                for _tid in _tier_special:
                                    text ("• " + bs_saga_tech_display_name(_tid)) size 14 color "#9FC4E2"
                        elif _tab == "equipamiento":
                            text "Equipamiento y loadout" size 21 color "#EAF6FF"
                            for i in range(6):
                                $ _slot_item = str(_slots[i] if i < len(_slots) else "")
                                hbox:
                                    spacing 6
                                    text ("Slot " + str(i + 1) + ": " + (_slot_item if _slot_item else "vacío")) size 14 color "#CFE6FA" xminimum 300
                                    if _slot_item:
                                        textbutton "Desequipar":
                                            action Function(bs_saga_ui_call, bs_saga_unequip_item_from_hero, _hero, i, _cfg, _build)
                            text "Equipar desde inventario de cuenta" size 15 color "#D0E9FF"
                            if _equipables:
                                for row in _equipables[:8]:
                                    $ _iid = str(row.get("item_id", ""))
                                    textbutton (_iid + " x" + str(row.get("qty", 0))):
                                        action Function(bs_saga_ui_call, bs_saga_equip_item_to_hero, _hero, _iid, None, _cfg, _build)
                            else:
                                text "No hay equipables en inventario de cuenta." size 14 color "#9FB9D1"
                        elif _tab == "build":
                            text "Build de entrada" size 21 color "#EAF6FF"
                            text ("Build actual: " + _build) size 15 color "#9FC4E2"
                            hbox:
                                spacing 8
                                textbutton "Balanceado" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "balanceado")
                                textbutton "Ofensivo" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "ofensivo")
                                textbutton "Defensivo" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "defensivo")
                        else:
                            text "Configuraciones (CFG)" size 21 color "#EAF6FF"
                            text ("CFG activa: " + _cfg.upper()) size 15 color "#9FC4E2"
                            hbox:
                                spacing 8
                                textbutton "CFG1" action Function(bs_saga_ui_call, bs_saga_set_prep_config, "cfg1")
                                textbutton "CFG2" action Function(bs_saga_ui_call, bs_saga_set_prep_config, "cfg2")
                                textbutton "CFG3" action Function(bs_saga_ui_call, bs_saga_set_prep_config, "cfg3")
                            text ("Pool técnico usado/libre: " + str(_spent_cfg) + "/" + str(_pool_total_cfg) + " · Libre " + str(_pool_left_cfg)) size 14 color "#9FC4E2"
                            text ("Loadout: " + str(_loadout_count) + "/6 slots equipados") size 14 color "#9FC4E2"

            hbox:
                spacing 10
                textbutton "Volver a sala":
                    action Return("nav:room")
                textbutton "Continuar a pre-combate":
                    action Return("nav:staging")

screen bs_saga_duel_staging_screen():
    tag menu
    $ _rows = bs_saga_preparation_rows_filtered()
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy_hero = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _party = [str(x) for x in (bs_saga_prep_selected_party_ids or []) if str(x)]
    $ _party_txt = ", ".join(_party) if _party else "sin equipo"
    $ _j1 = str(_party[0] if len(_party) > 0 else (_hero if _hero else ""))
    $ _j2 = str(_party[1] if len(_party) > 1 else "")
    $ _tier = bs_saga_hero_tier(_hero, "C") if _hero else "C"
    $ _pool = bs_saga_tier_pool_total(_tier) if _hero else 0
    $ _hp_reward_mult = bs_saga_clamp_hp_reward_multiplier(getattr(store, "bs_saga_prep_hp_reward_multiplier", 1))
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _loadout = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _loadout_count = len([x for x in _loadout if str(x or "").strip()])
    $ _contract = bs_saga_precombat_contract_validate()
    $ _checks = list((_contract or {}).get("checks", []) or [])
    $ _block_n = len((_contract or {}).get("blocking", []) or [])
    $ _warn_n = len((_contract or {}).get("warnings", []) or [])
    $ _diag = bs_saga_capture_prep_diag(_hero, _cfg, _build) if _hero else {}
    $ _cons = bs_saga_prep_inventory_candidates("consumables")
    $ _items = bs_saga_prep_inventory_candidates("equipables")
    $ _flag_cons = str(bs_saga_prep_flag_consumable_id or "")
    $ _flag_item = str(bs_saga_prep_flag_item_id or "")
    $ _rc = bs_saga_get_prep_reward_conditions()
    $ _reward_prof = bs_saga_build_reward_condition_profile()
    $ _r_exp_mult = float(_reward_prof.get("exp_mult", 1.0) or 1.0)
    $ _r_oro_mult = float(_reward_prof.get("oro_mult", 1.0) or 1.0)
    $ _r_prob_mult = float(_reward_prof.get("probability_mult", 1.0) or 1.0)
    $ _r_base_exp = int(getattr(store, "bs_saga_reward_base_exp_real", 35) or 35)
    $ _r_base_oro = int(getattr(store, "bs_saga_reward_base_oro_real", 15) or 15)
    $ _r_step_exp = float(getattr(store, "bs_saga_reward_step_exp", 3.5) or 3.5)
    $ _r_step_oro = float(getattr(store, "bs_saga_reward_step_oro", 2.0) or 2.0)
    $ _status = "listo" if _block_n <= 0 and _warn_n <= 0 else ("warnings" if _block_n <= 0 else "bloqueado")

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Pre-combate (duelo)" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Return("nav:lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 620
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Resumen de entrada" size 22 color "#EAF6FF"
                    if _hero:
                        text ("Héroe: " + _hero + " · Tier " + _tier) size 16 color "#CFE6FA"
                    else:
                        text "Héroe: sin seleccionar" size 16 color "#FF9F9F"
                    text ("Alineación: " + _party_txt) size 14 color "#9FC4E2"
                    if _mode == "2v2":
                        text ("Casillas · J1: " + (_j1 if _j1 else "—") + " · J2: " + (_j2 if _j2 else "—")) size 14 color "#A9CAE6"
                        text ("Estado slots: " + ("completo" if _j1 and _j2 else "incompleto")) size 13 color ("#8BD6A7" if _j1 and _j2 else "#FFD166")
                    text ("Modo: " + _mode + " · Rival: " + ("manual" if _enemy_mode == "manual" else "aleatorio")) size 14 color "#9FC4E2"
                    text ("Build: " + _build + " · Config: " + _cfg.upper()) size 14 color "#9FC4E2"
                    text ("Pool duelo: " + str(_pool) + " · Loadout equipado: " + str(_loadout_count) + "/6") size 14 color "#9FC4E2"
                    text ("Condición HP seleccionada: x" + str(_hp_reward_mult) + " · Escala HP de combate y recompensa EXP/Oro.") size 14 color "#9FC4E2"
                    textbutton "Configurar héroe":
                        action Return("nav:config")
                    null height 12
                    text "Esta vista está orientada a validación final previa al combate." size 14 color "#9FC4E2"
                    text "Puedes volver a configuración de héroe o regresar a preparación." size 14 color "#9FC4E2"
                    null height 8
                    textbutton "Preparación":
                        action Return("nav:room")

            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 468
                    vbox:
                        spacing 8
                        text "Checklist pre-duelo" size 22 color "#EAF6FF"
                        text ("Estado: " + _status.upper()) size 16 color ("#FF9F9F" if _block_n > 0 else ("#FFD166" if _warn_n > 0 else "#8BD6A7"))
                        text ("Bloqueantes: " + str(int(_block_n)) + " · Warnings: " + str(int(_warn_n))) size 14 color ("#FF9F9F" if _block_n > 0 else ("#FFD166" if _warn_n > 0 else "#8BD6A7"))
                        for c in _checks:
                            $ _ok = bool(c.get("ok", False))
                            $ _sev = str(c.get("severity", "warn"))
                            $ _icon = "✅" if _ok else ("⛔" if _sev == "block" else "⚠")
                            $ _col = "#8BD6A7" if _ok else ("#FF9F9F" if _sev == "block" else "#FFD166")
                            text (_icon + " " + str(c.get("label", "")) + " · " + str(c.get("detail", ""))) size 14 color _col
                        text ("• Técnicas: " + str(_tech_prof.get("mode", "virgen")) + " · Pool " + str(_tech_prof.get("pool_total", 0))) size 14 color "#9FC4E2"
                        text ("• Loadout equipado: " + str(_loadout_count) + "/6") size 14 color "#9FC4E2"
                        if _diag:
                            text ("• Diag modo raw/resuelto: " + str(_diag.get("raw_mode", "virgen")) + " / " + str(_diag.get("resolved_mode", "virgen"))) size 13 color "#9FC4E2"
                            text ("• Diag puntos raw/resuelto: " + str(int(_diag.get("raw_points_positive", 0) or 0)) + " / " + str(int(_diag.get("resolved_points_positive", 0) or 0))) size 13 color "#9FC4E2"
                            text ("• Diag preset externo: " + ("SI" if bool(_diag.get("preset_applied", False)) else "NO")) size 13 color "#9FC4E2"
                            if bool(_diag.get("suspicious", False)):
                                text "⚠ Diag: posible sobreescritura de puntos al resolver preconfig." size 13 color "#FFD166"
                        null height 6

                        text "Modo de juego" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "1v1" action Function(bs_saga_ui_call, bs_saga_set_prep_mode, "1v1")
                            textbutton "2v2" action Function(bs_saga_ui_call, bs_saga_set_prep_mode, "2v2")

                        text "Condición HP / Reward" size 16 color "#D0E9FF"
                        text ("Multiplicador activo: x" + str(_hp_reward_mult) + " (mín x1 · máx x5)") size 14 color "#9FC4E2"
                        hbox:
                            spacing 6
                            textbutton "x1" action Function(bs_saga_ui_call, bs_saga_set_prep_hp_reward_multiplier, 1)
                            textbutton "x2" action Function(bs_saga_ui_call, bs_saga_set_prep_hp_reward_multiplier, 2)
                            textbutton "x3" action Function(bs_saga_ui_call, bs_saga_set_prep_hp_reward_multiplier, 3)
                            textbutton "x4" action Function(bs_saga_ui_call, bs_saga_set_prep_hp_reward_multiplier, 4)
                            textbutton "x5" action Function(bs_saga_ui_call, bs_saga_set_prep_hp_reward_multiplier, 5)

                        text "Condiciones de recompensa (misiones de batalla)" size 16 color "#D0E9FF"
                        text ("Multiplicadores actuales -> EXP x" + str(_r_exp_mult) + " · Oro x" + str(_r_oro_mult) + " · Prob x" + str(_r_prob_mult)) size 13 color "#9FC4E2"
                        hbox:
                            spacing 6
                            textbutton ("Concentrar: " + ("ON" if bool(_rc.get("use_concentrar", False)) else "OFF")):
                                action Function(bs_saga_ui_call, bs_saga_toggle_prep_reward_condition, "use_concentrar")
                            textbutton ("Sin ataque directo: " + ("ON" if bool(_rc.get("no_direct_attack", False)) else "OFF")):
                                action Function(bs_saga_ui_call, bs_saga_toggle_prep_reward_condition, "no_direct_attack")
                        hbox:
                            spacing 6
                            textbutton ("Sin swap Atq/Def: " + ("ON" if bool(_rc.get("no_stance_swap", False)) else "OFF")):
                                action Function(bs_saga_ui_call, bs_saga_toggle_prep_reward_condition, "no_stance_swap")
                            textbutton ("Recibir poco daño: " + ("ON" if bool(_rc.get("low_damage_taken", False)) else "OFF")):
                                action Function(bs_saga_ui_call, bs_saga_toggle_prep_reward_condition, "low_damage_taken")
                        hbox:
                            spacing 6
                            textbutton ("Misión diaria: " + ("ON" if bool(_rc.get("daily_mission", False)) else "OFF")):
                                action Function(bs_saga_ui_call, bs_saga_toggle_prep_reward_condition, "daily_mission")

                        text "Base real de recompensa (para emulación/economía)" size 16 color "#D0E9FF"
                        text ("Base EXP " + str(_r_base_exp) + " · Step EXP " + str(_r_step_exp)) size 13 color "#9FC4E2"
                        hbox:
                            spacing 6
                            textbutton "EXP base -5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "base_exp", -5)
                            textbutton "EXP base +5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "base_exp", 5)
                        hbox:
                            spacing 6
                            textbutton "Step EXP -0.5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "step_exp", -0.5)
                            textbutton "Step EXP +0.5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "step_exp", 0.5)
                        text ("Base Oro " + str(_r_base_oro) + " · Step Oro " + str(_r_step_oro)) size 13 color "#9FC4E2"
                        hbox:
                            spacing 6
                            textbutton "Oro base -5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "base_oro", -5)
                            textbutton "Oro base +5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "base_oro", 5)
                        hbox:
                            spacing 6
                            textbutton "Step Oro -0.5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "step_oro", -0.5)
                            textbutton "Step Oro +0.5" action Function(bs_saga_ui_call, bs_saga_adjust_reward_base_param, "step_oro", 0.5)

                        text "Rival de duelo" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Aleatorio" action SetVariable("bs_saga_prep_enemy_mode", "random")
                            textbutton "Manual" action SetVariable("bs_saga_prep_enemy_mode", "manual")
                        if _enemy_mode == "manual":
                            text ("Enemigo activo: " + (_enemy_hero if _enemy_hero else "sin seleccionar")) size 14 color "#9FC4E2"
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                ymaximum 120
                                vbox:
                                    spacing 4
                                    for row in _rows:
                                        $ _eh = str(row.get("hero_id", ""))
                                        textbutton _eh:
                                            action Function(bs_saga_ui_call, bs_saga_set_prep_enemy, _eh)

                        text "Build duelo" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Balanceado" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "balanceado")
                            textbutton "Ofensivo" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "ofensivo")
                            textbutton "Defensivo" action Function(bs_saga_ui_call, bs_saga_set_prep_build, "defensivo")

                        text ("Config: " + _cfg.upper() + " · Tier: " + _tier + " · Pool duelo: " + str(_pool)) size 14 color "#9FC4E2"
                        text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"
                        null height 8
                        text "Flags opcionales (item/consumible)" size 16 color "#D0E9FF"
                        text ("Item flag: " + (_flag_item if _flag_item else "ninguno")) size 14 color "#9FC4E2"
                        text ("Consumible flag: " + (_flag_cons if _flag_cons else "ninguno")) size 14 color "#9FC4E2"
                        if _cons:
                            text "Consumibles" size 14 color "#CFE6FA"
                            hbox:
                                spacing 6
                                for row in _cons[:3]:
                                    $ _cid = str(row.get("item_id", ""))
                                    textbutton (_cid + " x" + str(row.get("qty", 0))):
                                        action Function(bs_saga_ui_call, bs_saga_set_prep_flag, "consumable", _cid)
                        if _items:
                            text "Equipables" size 14 color "#CFE6FA"
                            hbox:
                                spacing 6
                                for row in _items[:3]:
                                    $ _iid = str(row.get("item_id", ""))
                                    textbutton (_iid + " x" + str(row.get("qty", 0))):
                                        action Function(bs_saga_ui_call, bs_saga_set_prep_flag, "item", _iid)
                        if _flag_item or _flag_cons:
                            textbutton "Limpiar flags":
                                action [Function(bs_saga_ui_call, bs_saga_set_prep_flag, "item", ""), Function(bs_saga_ui_call, bs_saga_set_prep_flag, "consumable", "")]
                        null height 6

                        textbutton ("Iniciar duelo" if _block_n <= 0 else "Iniciar duelo (bloqueado por validación)"):
                            action Return("nav:launch_duel")
                        textbutton "Volver a sala de preparación":
                            action Return("nav:room")

screen bs_saga_preparation_verify_screen():
    tag menu
    $ _hero = str(bs_saga_prep_selected_hero or "")
    $ _mode = str(bs_saga_prep_selected_mode or "1v1")
    $ _enemy_mode = str(bs_saga_prep_enemy_mode or "random")
    $ _enemy = str(bs_saga_prep_selected_enemy_hero or "")
    $ _build = str(bs_saga_prep_selected_build or "balanceado")
    $ _cfg = str(bs_saga_prep_selected_config or "cfg1")
    $ _hero_slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _cons = bs_saga_prep_inventory_candidates("consumables")
    $ _items = bs_saga_prep_inventory_candidates("equipables")
    $ _flag_cons = str(bs_saga_prep_flag_consumable_id or "")
    $ _flag_item = str(bs_saga_prep_flag_item_id or "")

    add Solid("#0E1A28")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 78
        background Solid("#66C8FF")
    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ypadding 10
        background Solid("#2C4963")
        hbox:
            spacing 16
            text "BATTLESTARS SAGA" size 40 color "#5FC6FF"
            text "Verificar preparación" size 22 color "#D7EEFF" yalign 0.7
            null width 140
            textbutton "Volver" action Return("nav:room")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (14, 14)
        background Solid("#13273A")
        hbox:
            spacing 14
            frame:
                xsize 450
                yfill True
                background Solid("#1A3044")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Resumen previo al duelo (ruta legacy)" size 24 color "#EAF6FF"
                    text ("Tu héroe: " + (_hero if _hero else "sin seleccionar")) size 16 color "#D0E9FF"
                    text ("Modo: " + _mode) size 16 color "#D0E9FF"
                    text ("Enemigo: " + (_enemy if _enemy_mode == "manual" else "aleatorio")) size 16 color "#D0E9FF"
                    text ("Build: " + _build) size 16 color "#D0E9FF"
                    text ("Config: " + _cfg.upper()) size 16 color "#D0E9FF"
                    text ("Item flag: " + (_flag_item if _flag_item else "ninguno")) size 14 color "#9FC4E2"
                    text ("Consumible flag: " + (_flag_cons if _flag_cons else "ninguno")) size 14 color "#9FC4E2"
                    text ("Slots equipados: " + ", ".join([s for s in _hero_slots if str(s)]) if _hero_slots else "Slots equipados: ninguno") size 14 color "#9FC4E2"
                    text "Esta pantalla se conserva por compatibilidad. El flujo principal inicia duelo desde Pre-combate." size 13 color "#9FC4E2"
                    textbutton "Iniciar duelo":
                        action Return("nav:launch_duel")
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (10, 10)
                vbox:
                    spacing 8
                    text "Marcar item/consumible para combate (flag)" size 20 color "#EAF6FF"
                    text "Consumibles" size 16 color "#CFE6FA"
                    if _cons:
                        for row in _cons[:8]:
                            $ _cid = str(row.get("item_id", ""))
                            textbutton (_cid + " x" + str(row.get("qty", 0))):
                                action Function(bs_saga_ui_call, bs_saga_set_prep_flag, "consumable", _cid)
                    else:
                        text "Sin consumibles en inventario." size 14 color "#9FB9D1"
                    null height 6
                    text "Items equipables" size 16 color "#CFE6FA"
                    if _items:
                        for row in _items[:8]:
                            $ _iid = str(row.get("item_id", ""))
                            textbutton (_iid + " x" + str(row.get("qty", 0))):
                                action Function(bs_saga_ui_call, bs_saga_set_prep_flag, "item", _iid)
                    else:
                        text "Sin equipables en inventario." size 14 color "#9FB9D1"

init -899 python:
    def bs_saga_ui_hub_prep_screen_split_status_v1():
        return {
            "module": "ui_hub_screens_prep",
            "status": "phase_5_done",
            "migrated_screens": [
                "bs_saga_preparation_room_screen",
                "bs_saga_hero_config_screen",
                "bs_saga_duel_staging_screen",
                "bs_saga_preparation_verify_screen"
            ]
        }
