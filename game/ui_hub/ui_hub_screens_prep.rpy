# ui_hub_screens_prep.rpy
# Fase 3 de split: pantallas de preparación/pre-combate.

screen bs_saga_preparation_room_screen():
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
    $ _owned_only = bool(bs_saga_prep_filter_owned_only)
    $ _equipables = bs_saga_prep_inventory_candidates("equipables")
    $ _slots = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _hero_tier = bs_saga_hero_tier(_hero, "C") if _hero else ""
    $ _tier_pool = bs_saga_tier_pool_total(_hero_tier) if _hero else 0
    $ _tier_stats = bs_saga_tier_core_profile(_hero_tier) if _hero else {"hp":0,"ep":0,"ec":0,"durability":0,"cover":0}
    $ _tier_tuning = bs_saga_tier_combat_tuning_profile(_hero_tier) if _hero else {"hp_factor":0.0,"rest_hp_pct":0.0,"rest_ep_pct":0.0,"rest_ec_pct":0.0,"rest_ec_scales":0}
    $ _dmg_rules = dict(bs_saga_damage_coherence_rules or {})
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _tier_allowed = bs_saga_tier_allowed_tech_ids(_hero_tier) if _hero else []
    $ _tp_map = dict(_tech_prof.get("tech_points", {}) or {}) if _hero else {}
    $ _pool_total_cfg = int(_tech_prof.get("pool_total", 0) or 0) if _hero else 0
    $ _spent_cfg = int(_tech_prof.get("pool_spent_off", 0) or 0) + int(_tech_prof.get("pool_spent_def", 0) or 0) if _hero else 0
    $ _pool_left_cfg = max(0, _pool_total_cfg - _spent_cfg)
    $ _rotation_preview = ", ".join([str(x) for x in (bs_saga_prep_duel_rotation_ids or [])[:5]])
    $ _is_staging = False

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
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

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
                    text "Roster disponible (rotación o adquirido)" size 22 color "#EAF6FF"
                    text ("Héroes listados: " + str(len(_rows))) size 14 color "#9FC4E2"
                    text ("Rotación actual (5): " + (_rotation_preview if _rotation_preview else "sin generar")) size 14 color "#9FC4E2"
                    textbutton ("Filtro adquiridos: " + ("ON" if _owned_only else "OFF")):
                        action [ToggleVariable("bs_saga_prep_filter_owned_only"), Jump("bs_saga_preparacion")]
                    textbutton "Aleatorizar rotación":
                        action [Function(bs_saga_refresh_duel_rotation_heroes, 5), Jump("bs_saga_preparacion")]
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
                                                text "Activo" size 16 color "#F7D774"
                                            elif _is_av:
                                                textbutton "Elegir":
                                                    action [Function(bs_saga_set_prep_hero, _hid), Jump("bs_saga_preparacion")]
                                            if _is_av:
                                                textbutton ("Quitar" if _hid in _party else "Equipo"):
                                                    action [Function(bs_saga_toggle_prep_party_hero, _hid), Jump("bs_saga_preparacion")]
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
                    ymaximum 468
                    vbox:
                        spacing 8
                        text "Configuración de entrada" size 22 color "#EAF6FF"
                        text ("Héroe activo: " + (_hero if _hero else "sin seleccionar")) size 16 color "#CFE6FA"
                        if _is_staging:
                            text "Modo de juego" size 16 color "#D0E9FF"
                            hbox:
                                spacing 6
                                textbutton "1v1" action [Function(bs_saga_set_prep_mode, "1v1"), Jump("bs_saga_preparacion")]
                                textbutton "2v2" action [Function(bs_saga_set_prep_mode, "2v2"), Jump("bs_saga_preparacion")]
                        text ("Equipo seleccionado: " + _party_txt) size 14 color "#9FC4E2"
                        text ("Config activa: " + _cfg.upper()) size 14 color "#9FC4E2"
                        text ("Build activa: " + _build) size 14 color "#9FC4E2"
                        if _hero:
                            text ("Tier héroe: " + _hero_tier + " · Pool duelo: " + str(_tier_pool)) size 14 color "#9FC4E2"
                            text ("HP " + str(_tier_stats.get("hp", 0)) + " · EP " + str(_tier_stats.get("ep", 0)) + " · EC " + str(_tier_stats.get("ec", 0))) size 14 color "#9FC4E2"
                            text ("Durabilidad " + str(_tier_stats.get("durability", 0)) + " · Cubre " + str(_tier_stats.get("cover", 0))) size 14 color "#9FC4E2"
                            text ("Factor HP/Pool x" + str(_tier_tuning.get("hp_factor", 0.0)) + " · Descansar HP " + str(int(float(_tier_tuning.get("rest_hp_pct", 0.0)) * 100)) + "%") size 14 color "#9FC4E2"
                            text ("Descansar EP " + str(int(float(_tier_tuning.get("rest_ep_pct", 0.0)) * 100)) + "% · EC " + str(int(float(_tier_tuning.get("rest_ec_pct", 0.0)) * 100)) + "% (+ " + str(int(_tier_tuning.get("rest_ec_scales", 0) or 0)) + " escalas)") size 14 color "#9FC4E2"
                            text ("Daño normal objetivo " + str(int(float(_dmg_rules.get("normal_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("normal_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Daño combo objetivo " + str(int(float(_dmg_rules.get("combo_hit_min_pct", 0.0)) * 100)) + "-" + str(int(float(_dmg_rules.get("combo_hit_max_pct", 0.0)) * 100)) + "% HP") size 14 color "#9FC4E2"
                            text ("Técnicas: " + str(_tech_prof.get("mode", "virgen")) + " · Pool técnico " + str(_tech_prof.get("pool_total", 0))) size 14 color "#9FC4E2"
                            hbox:
                                spacing 6
                                textbutton "Téc. Virgen" action [Function(bs_saga_hero_tech_mode_set, _hero, "virgen", _cfg, _build), Jump("bs_saga_preparacion")]
                                textbutton "Téc. Preconfig" action [Function(bs_saga_hero_tech_mode_set, _hero, "preconfig", _cfg, _build), Jump("bs_saga_preparacion")]
                            null height 4
                            text ("Pool técnico cfg/build: " + str(_spent_cfg) + "/" + str(_pool_total_cfg) + " · Libre: " + str(_pool_left_cfg)) size 14 color "#9FC4E2"
                            text "Asignación de técnicas (tier actual)" size 15 color "#D0E9FF"
                            viewport:
                                draggable True
                                mousewheel True
                                scrollbars "vertical"
                                ymaximum 160
                                vbox:
                                    spacing 4
                                    if _tier_allowed:
                                        for _tid in _tier_allowed:
                                            $ _pts = int(_tp_map.get(_tid, 0) or 0)
                                            hbox:
                                                spacing 6
                                                text (bs_saga_tech_display_name(_tid) + " [" + str(_pts) + "]") size 14 color "#CFE6FA" xminimum 300
                                                textbutton "+25":
                                                    action [Function(bs_saga_hero_tech_points_add, _hero, _tid, +25, _cfg, _build), Jump("bs_saga_preparacion")]
                                                textbutton "-25":
                                                    action [Function(bs_saga_hero_tech_points_add, _hero, _tid, -25, _cfg, _build), Jump("bs_saga_preparacion")]
                                    else:
                                        text "Sin técnicas habilitadas para este tier." size 14 color "#9FB9D1"
                        hbox:
                            spacing 6
                            textbutton "CFG1" action [Function(bs_saga_set_prep_config, "cfg1"), Jump("bs_saga_preparacion")]
                            textbutton "CFG2" action [Function(bs_saga_set_prep_config, "cfg2"), Jump("bs_saga_preparacion")]
                            textbutton "CFG3" action [Function(bs_saga_set_prep_config, "cfg3"), Jump("bs_saga_preparacion")]
                        text "Loadout del héroe (6 slots equipables)" size 15 color "#D0E9FF"
                        if _hero:
                            for i in range(6):
                                $ _slot_item = str(_slots[i] if i < len(_slots) else "")
                                hbox:
                                    spacing 6
                                    text ("Slot " + str(i + 1) + ": " + (_slot_item if _slot_item else "vacío")) size 14 color "#CFE6FA" xminimum 270
                                    if _slot_item:
                                        textbutton "Desequipar":
                                            action [Function(bs_saga_unequip_item_from_hero, _hero, i, _cfg, _build), Jump("bs_saga_preparacion")]
                        else:
                            text "Selecciona héroe para administrar equipables." size 14 color "#9FB9D1"
                        if _hero:
                            text "Equipar desde inventario de cuenta" size 15 color "#D0E9FF"
                            if _equipables:
                                for row in _equipables[:8]:
                                    $ _iid = str(row.get("item_id", ""))
                                    textbutton (_iid + " x" + str(row.get("qty", 0))):
                                        action [Function(bs_saga_equip_item_to_hero, _hero, _iid, None, _cfg, _build), Jump("bs_saga_preparacion")]
                            else:
                                text "No hay equipables en inventario de cuenta." size 14 color "#9FB9D1"
                        if _is_staging:
                            text "Modo de enemigo" size 16 color "#D0E9FF"
                            hbox:
                                spacing 6
                                textbutton "Aleatorio" action SetVariable("bs_saga_prep_enemy_mode", "random")
                                textbutton "Manual" action SetVariable("bs_saga_prep_enemy_mode", "manual")
                            if _enemy_mode == "manual":
                                text "Enemigo manual" size 16 color "#D0E9FF"
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
                                                action [Function(bs_saga_set_prep_enemy, _eh), Jump("bs_saga_preparacion")]
                                text ("Enemigo activo: " + (_enemy_hero if _enemy_hero else "sin seleccionar")) size 14 color "#9FC4E2"
                        text "Build base (sala)" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Balanceado" action [Function(bs_saga_set_prep_build, "balanceado"), Jump("bs_saga_preparacion")]
                            textbutton "Ofensivo" action [Function(bs_saga_set_prep_build, "ofensivo"), Jump("bs_saga_preparacion")]
                            textbutton "Defensivo" action [Function(bs_saga_set_prep_build, "defensivo"), Jump("bs_saga_preparacion")]
                        null height 12
                        text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"
                        text "Chequear técnicas/pool por tier: pendiente de integración detallada." size 15 color "#9FC4E2"
                        textbutton "Pasar a pre-combate":
                            action [SetVariable("bs_saga_prep_context", "staging"), Jump("bs_saga_preparacion")]

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
    $ _tier = bs_saga_hero_tier(_hero, "C") if _hero else "C"
    $ _pool = bs_saga_tier_pool_total(_tier) if _hero else 0
    $ _tech_prof = bs_saga_hero_tech_profile_get(_hero, _cfg, _build) if _hero else {}
    $ _loadout = bs_saga_hero_loadout_slots(_hero, _cfg, _build) if _hero else []
    $ _loadout_count = len([x for x in _loadout if str(x or "").strip()])
    $ _contract = bs_saga_precombat_contract_validate()
    $ _checks = list((_contract or {}).get("checks", []) or [])
    $ _block_n = len((_contract or {}).get("blocking", []) or [])
    $ _warn_n = len((_contract or {}).get("warnings", []) or [])

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
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

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
                    text "Roster para duelo (selección rápida)" size 22 color "#EAF6FF"
                    text ("Héroe activo: " + (_hero if _hero else "sin seleccionar")) size 15 color "#CFE6FA"
                    text ("Equipo: " + _party_txt) size 14 color "#9FC4E2"
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
                                    $ _state = str(row.get("state", "bloqueado"))
                                    $ _is_av = bool(row.get("available", False))
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (8, 6)
                                        hbox:
                                            spacing 8
                                            text (str(row.get("name", _hid) or _hid) + " (" + str(row.get("tier", "C")) + ")") size 17 color "#D0E9FF" xminimum 320
                                            text ("Disponible" if _state == "disponible" else ("Para probar" if _state == "para_probar" else "Bloqueado")) size 15 color ("#8BD6A7" if _state == "disponible" else ("#FFD166" if _state == "para_probar" else "#FF9F9F")) xminimum 120
                                            if _is_av:
                                                textbutton ("Activo" if _hero == _hid else "Elegir"):
                                                    action [Function(bs_saga_set_prep_hero, _hid), Jump("bs_saga_preparacion")]
                                                textbutton ("Quitar" if _hid in _party else "Equipo"):
                                                    action [Function(bs_saga_toggle_prep_party_hero, _hid), Jump("bs_saga_preparacion")]
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
                    ymaximum 468
                    vbox:
                        spacing 8
                        text "Checklist pre-duelo" size 22 color "#EAF6FF"
                        text ("Bloqueantes: " + str(int(_block_n)) + " · Warnings: " + str(int(_warn_n))) size 14 color ("#FF9F9F" if _block_n > 0 else ("#FFD166" if _warn_n > 0 else "#8BD6A7"))
                        for c in _checks:
                            $ _ok = bool(c.get("ok", False))
                            $ _sev = str(c.get("severity", "warn"))
                            $ _icon = "✅" if _ok else ("⛔" if _sev == "block" else "⚠")
                            $ _col = "#8BD6A7" if _ok else ("#FF9F9F" if _sev == "block" else "#FFD166")
                            text (_icon + " " + str(c.get("label", "")) + " · " + str(c.get("detail", ""))) size 14 color _col
                        text ("• Técnicas: " + str(_tech_prof.get("mode", "virgen")) + " · Pool " + str(_tech_prof.get("pool_total", 0))) size 14 color "#9FC4E2"
                        text ("• Loadout equipado: " + str(_loadout_count) + "/6") size 14 color "#9FC4E2"
                        null height 6

                        text "Modo de juego" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "1v1" action [Function(bs_saga_set_prep_mode, "1v1"), Jump("bs_saga_preparacion")]
                            textbutton "2v2" action [Function(bs_saga_set_prep_mode, "2v2"), Jump("bs_saga_preparacion")]

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
                                            action [Function(bs_saga_set_prep_enemy, _eh), Jump("bs_saga_preparacion")]

                        text "Build duelo" size 16 color "#D0E9FF"
                        hbox:
                            spacing 6
                            textbutton "Balanceado" action [Function(bs_saga_set_prep_build, "balanceado"), Jump("bs_saga_preparacion")]
                            textbutton "Ofensivo" action [Function(bs_saga_set_prep_build, "ofensivo"), Jump("bs_saga_preparacion")]
                            textbutton "Defensivo" action [Function(bs_saga_set_prep_build, "defensivo"), Jump("bs_saga_preparacion")]

                        text ("Config: " + _cfg.upper() + " · Tier: " + _tier + " · Pool duelo: " + str(_pool)) size 14 color "#9FC4E2"
                        text ("Resumen: modo " + _mode + " | enemigo " + _enemy_mode + " | build " + _build) size 15 color "#9FC4E2"

                        textbutton "Verificar preparación e iniciar duelo":
                            action Jump("bs_saga_preparation_verify")
                        textbutton "Volver a sala de preparación":
                            action [SetVariable("bs_saga_prep_context", "room"), Jump("bs_saga_preparacion")]

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
            textbutton "Volver" action Jump("bs_saga_preparacion")

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
                    text "Resumen previo al duelo" size 24 color "#EAF6FF"
                    text ("Tu héroe: " + (_hero if _hero else "sin seleccionar")) size 16 color "#D0E9FF"
                    text ("Modo: " + _mode) size 16 color "#D0E9FF"
                    text ("Enemigo: " + (_enemy if _enemy_mode == "manual" else "aleatorio")) size 16 color "#D0E9FF"
                    text ("Build: " + _build) size 16 color "#D0E9FF"
                    text ("Config: " + _cfg.upper()) size 16 color "#D0E9FF"
                    text ("Item flag: " + (_flag_item if _flag_item else "ninguno")) size 14 color "#9FC4E2"
                    text ("Consumible flag: " + (_flag_cons if _flag_cons else "ninguno")) size 14 color "#9FC4E2"
                    text ("Slots equipados: " + ", ".join([s for s in _hero_slots if str(s)]) if _hero_slots else "Slots equipados: ninguno") size 14 color "#9FC4E2"
                    textbutton "Iniciar duelo":
                        action Jump("bs_saga_launch_prepared_duel")
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
                                action [Function(bs_saga_set_prep_flag, "consumable", _cid), Jump("bs_saga_preparation_verify")]
                    else:
                        text "Sin consumibles en inventario." size 14 color "#9FB9D1"
                    null height 6
                    text "Items equipables" size 16 color "#CFE6FA"
                    if _items:
                        for row in _items[:8]:
                            $ _iid = str(row.get("item_id", ""))
                            textbutton (_iid + " x" + str(row.get("qty", 0))):
                                action [Function(bs_saga_set_prep_flag, "item", _iid), Jump("bs_saga_preparation_verify")]
                    else:
                        text "Sin equipables en inventario." size 14 color "#9FB9D1"

init -899 python:
    def bs_saga_ui_hub_prep_screen_split_status_v1():
        return {
            "module": "ui_hub_screens_prep",
            "status": "phase_3_done",
            "migrated_screens": [
                "bs_saga_preparation_room_screen",
                "bs_saga_duel_staging_screen",
                "bs_saga_preparation_verify_screen"
            ]
        }
