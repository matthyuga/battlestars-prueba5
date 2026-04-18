# ui_hub_screens_lobby.rpy
# Fase 3 de split: pantallas de lobby/paneles principales.

screen bs_saga_lobby_screen():
    tag menu
    $ _acc = bs_saga_account()
    $ _tier_current = bs_saga_refresh_account_tier(reason="lobby_screen")
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _tier = str(_tier_current or "")
    $ _tier_txt = ("Tier " + _tier) if _tier else "Sin tier"
    $ _owned_count = bs_saga_owned_heroes_count()
    $ _last_msg = str(bs_saga_last_tx_message or "")
    $ _exp_ratio = bs_saga_exp_progress()

    add Solid("#101923")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1128
        ysize 96
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.08
        xsize 1116
        ysize 84
        ypadding 8
        xpadding 10
        background Solid("#1A2938")
        vbox:
            spacing 6
            hbox:
                spacing 14
                text "BATTLESTARS SAGA" size 30 color "#5FC6FF"
                text "Lobby táctico" size 22 color "#D7EEFF" yalign 0.7
                text _tier_txt size 20 color "#D7EEFF" yalign 0.7
                text ("Lv " + str(_lvl)) size 20 color "#D7EEFF" yalign 0.7
                text ("EXP " + str(_exp) + "/" + str(_next)) size 18 color "#B9D9F3" yalign 0.7
                text ("Oro: " + str(_gold)) size 22 color "#F7D774" yalign 0.7
                null width 8
                textbutton "Salir" action MainMenu()
            bar:
                value _exp_ratio
                xfill True
                ymaximum 8
                left_bar Solid("#4AD4FF")
                right_bar Solid("#2A3D4E")

    frame:
        xalign 0.5
        yalign 0.48
        xsize 680
        ysize 380
        padding (18, 18)
        background Solid("#142131")

        vbox:
            spacing 10
            text "Panel Jugar" size 28 color "#E9F5FF"

            textbutton "⚔ Duelo libre" action Jump("bs_saga_duelo_libre")

            textbutton ("▼ Torneo" if bs_saga_tournament_panel_open else "▶ Torneo"):
                action ToggleVariable("bs_saga_tournament_panel_open")

            if bs_saga_tournament_panel_open:
                frame:
                    xfill True
                    padding (10, 10)
                    background Solid("#22384D")
                    vbox:
                        spacing 8
                        textbutton "Tier C" action Jump("bs_saga_torneo_tier_c")
                        textbutton "Tier B (no disponible)" action Jump("bs_saga_torneo_tier_b_locked")
                        textbutton "Tier A (no disponible)" action Jump("bs_saga_torneo_tier_a_locked")

            textbutton "🗼 Torre del cielo (preview)" action Jump("bs_saga_torre_cielo")

    frame:
        xalign 0.5
        yalign 0.88
        xsize 1120
        ysize 120
        padding (12, 12)
        background Solid("#1A2A3C")

        vbox:
            spacing 8
            text "Panel Gestión" size 20 color "#CFE6FA"
            text ("Héroes adquiridos: " + str(_owned_count)) size 16 color "#9FC4E2"
            if _last_msg:
                text ("Última transacción: " + _last_msg) size 15 color "#CDE7FF"
            hbox:
                spacing 10
                textbutton "Perfil" action Jump("bs_saga_perfil")
                textbutton "Preparación":
                    action [SetVariable("bs_saga_prep_intent_duel", False), SetVariable("bs_saga_prep_context", "room"), Jump("bs_saga_preparacion")]
                textbutton "Héroes" action Jump("bs_saga_heroes")
                textbutton "Tienda" action Jump("bs_saga_tienda")
                textbutton "Inventario" action Jump("bs_saga_inventario")
                textbutton "Catálogo de itens" action Jump("bs_saga_catalogo_items")
                textbutton "Catálogo de técnicas" action Jump("bs_saga_catalogo_tecnicas")

screen bs_saga_section_shell(title="Sección", subtitle="Panel", back_action=NullAction()):
    tag menu
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
            text "[subtitle]" size 22 color "#D7EEFF" yalign 0.7
            null width 220
            textbutton "Volver al lobby" action back_action

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (22, 22)
        background Solid("#152437")
        vbox:
            spacing 10
            text "[title]" size 34 color "#E9F5FF"
            text "Territorio: [title]" size 20 color "#A8C9E4"

screen bs_saga_heroes_screen():
    tag menu

    $ _tier = str(bs_saga_heroes_tier or "C").upper()
    $ _frs = bs_saga_franchises_for_tier(_tier)
    $ _heroes = bs_saga_heroes_filtered(_tier, bs_saga_heroes_franchise)
    $ _ff = str(bs_saga_heroes_franchise or "all").lower()
    $ _filter_label = _ff if _ff != "all" else "todas"
    $ _gold = bs_saga_gold()
    $ _owned_count = bs_saga_owned_heroes_count()

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
            text "Territorio: Héroes" size 22 color "#D7EEFF" yalign 0.7
            null width 150
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (18, 18)
        background Solid("#14273B")

        hbox:
            spacing 16

            frame:
                xsize 220
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Franquicias" size 22 color "#DDEEFF"
                    textbutton "Todas" action SetVariable("bs_saga_heroes_franchise", "all")
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 420
                        vbox:
                            spacing 6
                            for fr in _frs:
                                textbutton "[fr]" action SetVariable("bs_saga_heroes_franchise", fr)

            frame:
                xfill True
                yfill True
                padding (14, 14)
                background Solid("#11253A")
                vbox:
                    spacing 10

                    hbox:
                        spacing 8
                        text "Tiers" size 20 color "#DCEEFF"
                        textbutton "Tier C" action [SetVariable("bs_saga_heroes_tier", "C"), SetVariable("bs_saga_heroes_franchise", "all")]
                        textbutton "Tier B" action [SetVariable("bs_saga_heroes_tier", "B"), SetVariable("bs_saga_heroes_franchise", "all")]
                        text ("Oro: " + str(_gold)) size 18 color "#F7D774"
                        text ("Roster: " + str(_owned_count)) size 16 color "#9FC4E2"
                        text "Filtro: [_filter_label]" size 16 color "#9FC4E2"

                    hbox:
                        spacing 20
                        frame:
                            xsize 290
                            ysize 360
                            background Solid("#0D1A2A")
                            padding (12, 12)
                            vbox:
                                spacing 8
                                text "Panel visual héroe" size 18 color "#CDE7FF"
                                null height 260
                                text "(Sin imágenes por ahora)" size 16 color "#8EABC5"

                        frame:
                            xfill True
                            ysize 360
                            padding (10, 10)
                            background Solid("#1A3044")
                            vbox:
                                spacing 8
                                text "Nombres disponibles (Tier [_tier])" size 20 color "#E5F4FF"
                                viewport:
                                    draggable True
                                    mousewheel True
                                    scrollbars "vertical"
                                    ymaximum 300
                                    yinitial float(bs_saga_heroes_scroll_y or 0.0)
                                    vbox:
                                        spacing 5
                                        if _heroes:
                                            for i, h in enumerate(_heroes):
                                                $ _hn = str(h.get("name", "?") or "?")
                                                $ _hf = str(h.get("franchise", "?") or "?")
                                                $ _hid = bs_saga_hero_id(h)
                                                $ _price = bs_saga_hero_price(h)
                                                $ _owned = bs_saga_hero_is_owned(_hid)
                                                frame:
                                                    xfill True
                                                    background Solid("#1B3348")
                                                    padding (8, 6)
                                                    hbox:
                                                        spacing 8
                                                        text "• [_hn]" size 17 color "#D0E9FF" xminimum 240
                                                        text "—" size 17 color "#9FC4E2"
                                                        text "[_hf]" size 17 color "#D0E9FF" xminimum 180
                                                        text ("Oro: " + str(_price)) size 16 color "#F7D774" xminimum 120
                                                        if _owned:
                                                            text "Adquirido" size 16 color "#8BD6A7"
                                                        else:
                                                            textbutton "Comprar":
                                                                action Function(bs_saga_buy_hero_from_ui, h)
                                        else:
                                            text "No hay héroes para ese filtro." size 18 color "#9FB9D1"

screen bs_saga_catalog_screen():
    tag menu
    $ _cat = str(bs_saga_catalog_category or "consumibles")
    $ _groups = bs_saga_catalog_groups(_cat)
    $ _grp = str(bs_saga_catalog_group or "")
    if _grp not in _groups:
        $ _grp = _groups[0] if _groups else ""
        $ bs_saga_catalog_group = _grp
    $ _grp_label = _grp.capitalize() if _grp else "—"
    $ _items = bs_saga_catalog_items(_cat, _grp)
    $ _cats = bs_saga_catalog_category_keys()
    $ _cat_label = bs_saga_labelize(_cat)
    $ _gold = bs_saga_gold()

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
            text "Territorio: Catálogo de itens" size 22 color "#D7EEFF" yalign 0.7
            null width 90
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        vbox:
            spacing 10
            text "Catálogo de itens" size 34 color "#EAF6FF"

            hbox:
                spacing 8
                for ck in _cats:
                    $ lbl = "Consumibles" if ck == "consumibles" else ("Permanentes" if ck == "permanentes" else "Materiales")
                    textbutton "[lbl]":
                        action Function(bs_saga_catalog_set_category, ck)
                null width 16
                text ("Oro disponible: " + str(_gold)) size 18 color "#F7D774"

            hbox:
                spacing 14

                frame:
                    xsize 260
                    yfill True
                    padding (10, 10)
                    background Solid("#1F3348")
                    vbox:
                        spacing 8
                        text "Grupos" size 22 color "#DDEEFF"
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 360
                            vbox:
                                spacing 6
                                for g in _groups:
                                    $ _g_label = bs_saga_labelize(g)
                                    textbutton "[_g_label]":
                                        action Function(bs_saga_catalog_set_group, g)

                frame:
                    xfill True
                    yfill True
                    padding (12, 12)
                    background Solid("#102438")
                    vbox:
                        spacing 8
                        text "Listado central · [_cat_label] / [_grp_label]" size 20 color "#DCEEFF"
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 360
                            vbox:
                                spacing 6
                                if _items:
                                    for it in _items:
                                        $ _n = str(it.get("name", "?") or "?")
                                        $ _r = str(it.get("rarity", "-") or "-")
                                        $ _t = str(it.get("tier_req", "-") or "-")
                                        $ _m = str(it.get("meta", "") or "")
                                        $ _r_show = "-" if _r in ("", "-") else _r
                                        $ _t_show = "-" if _t in ("", "-") else _t
                                        $ _p = bs_saga_item_price(it)
                                        frame:
                                            xfill True
                                            background Solid("#173048")
                                            padding (8, 6)
                                            hbox:
                                                spacing 8
                                                text "• [_n]" size 17 color "#D0E9FF" xminimum 290
                                                text "Rareza: [_r_show]" size 16 color "#A9CAE6" xminimum 150
                                                text "Tier: [_t_show]" size 16 color "#A9CAE6" xminimum 120
                                                text ("Precio: " + str(_p)) size 16 color "#F7D774" xminimum 120
                                                text "[_m]" size 16 color "#D0E9FF" xminimum 220
                                                textbutton "Comprar x1":
                                                    action [Function(bs_saga_buy_item, it, 1), Jump("bs_saga_catalogo_items")]
                                else:
                                    text "Sin itens cargados todavía para este grupo." size 18 color "#9FB9D1"

screen bs_saga_inventory_screen():
    tag menu
    $ _rows = bs_saga_inventory_rows()
    $ _gold = bs_saga_gold()

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
            text "Territorio: Inventario" size 22 color "#D7EEFF" yalign 0.7
            text ("Oro: " + str(_gold)) size 20 color "#F7D774" yalign 0.7
            null width 120
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (16, 16)
        background Solid("#13273A")
        vbox:
            spacing 8
            text "Inventario de cuenta" size 32 color "#EAF6FF"
            viewport:
                draggable True
                mousewheel True
                scrollbars "vertical"
                ymaximum 390
                vbox:
                    spacing 6
                    if _rows:
                        for row in _rows:
                            $ _b = bs_saga_labelize(row.get("bucket", ""))
                            $ _id = str(row.get("item_id", "?") or "?")
                            $ _q = int(row.get("qty", 0) or 0)
                            frame:
                                xfill True
                                background Solid("#173048")
                                padding (8, 6)
                                hbox:
                                    spacing 8
                                    text ("Bucket: " + _b) size 17 color "#A9CAE6" xminimum 180
                                    text ("Item: " + _id) size 17 color "#D0E9FF" xminimum 520
                                    text ("Qty: " + str(_q)) size 17 color "#8BD6A7"
                    else:
                        text "Inventario vacío todavía." size 18 color "#9FB9D1"

screen bs_saga_profile_screen():
    tag menu
    $ _acc = bs_saga_account()
    $ _tier_current = bs_saga_refresh_account_tier(reason="profile_screen")
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _exp_ratio = bs_saga_exp_progress()
    $ _tier = str(_tier_current or "")
    $ _tier_txt = (_tier if _tier else "Sin tier")
    $ _top_total = bs_saga_top_heroes(3, False)
    $ _top_24 = bs_saga_top_heroes(3, True)
    $ _tier_rows = bs_saga_tier_progress_rows()
    $ _exp_base = int(getattr(store, "bs_saga_dev_gain_exp_base", 120) or 120)
    $ _gold_base = int(getattr(store, "bs_saga_dev_gain_gold_base", 90) or 90)
    $ _var_pct = int(getattr(store, "bs_saga_dev_gain_variance_pct", 35) or 35)
    $ _runs = int(getattr(store, "bs_saga_dev_gain_runs", 1) or 1)
    $ _est = bs_saga_estimate_duels_to_targets(1000, 5000) if bool(getattr(store, "bs_saga_dev_admin_enabled", False)) else {"duels_needed": 0}

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
            text "Perfil de usuario" size 22 color "#D7EEFF" yalign 0.7
            null width 180
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
                xsize 520
                yfill True
                background Solid("#1A3044")
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Resumen de cuenta" size 28 color "#EAF6FF"
                    text ("Tier: " + _tier_txt) size 18 color "#D0E9FF"
                    text ("Nivel: " + str(_lvl)) size 18 color "#D0E9FF"
                    text ("EXP: " + str(_exp) + "/" + str(_next)) size 18 color "#D0E9FF"
                    bar:
                        value _exp_ratio
                        xfill True
                        ymaximum 9
                        left_bar Solid("#4AD4FF")
                        right_bar Solid("#2A3D4E")
                    text ("Oro: " + str(_gold)) size 18 color "#F7D774"
                    null height 4
                    if bool(getattr(store, "bs_saga_dev_admin_enabled", False)):
                        text "DEV Admin (QA rápido)" size 16 color "#FFD166"
                        hbox:
                            spacing 6
                            textbutton "+50k oro" action [Function(bs_saga_dev_set_account_state, gold=_gold + 50000), Jump("bs_saga_perfil")]
                            textbutton "Lv 99" action [Function(bs_saga_dev_set_account_state, level=99), Jump("bs_saga_perfil")]
                            textbutton "EXP 0" action [Function(bs_saga_dev_set_account_state, exp=0), Jump("bs_saga_perfil")]
                        text ("Tool semi-random · base EXP " + str(_exp_base) + " · base Oro " + str(_gold_base) + " · var " + str(_var_pct) + "% · runs " + str(_runs)) size 13 color "#F6E6A9"
                        hbox:
                            spacing 6
                            textbutton "EXP -10" action [Function(bs_saga_dev_set_gain_profile, _exp_base - 10, None, None, None), Jump("bs_saga_perfil")]
                            textbutton "EXP +10" action [Function(bs_saga_dev_set_gain_profile, _exp_base + 10, None, None, None), Jump("bs_saga_perfil")]
                            textbutton "Oro -10" action [Function(bs_saga_dev_set_gain_profile, None, _gold_base - 10, None, None), Jump("bs_saga_perfil")]
                            textbutton "Oro +10" action [Function(bs_saga_dev_set_gain_profile, None, _gold_base + 10, None, None), Jump("bs_saga_perfil")]
                        hbox:
                            spacing 6
                            textbutton "Var -5%" action [Function(bs_saga_dev_set_gain_profile, None, None, _var_pct - 5, None), Jump("bs_saga_perfil")]
                            textbutton "Var +5%" action [Function(bs_saga_dev_set_gain_profile, None, None, _var_pct + 5, None), Jump("bs_saga_perfil")]
                            textbutton "Runs x1" action [Function(bs_saga_dev_set_gain_profile, None, None, None, 1), Jump("bs_saga_perfil")]
                            textbutton "Runs x5" action [Function(bs_saga_dev_set_gain_profile, None, None, None, 5), Jump("bs_saga_perfil")]
                            textbutton "Runs x20" action [Function(bs_saga_dev_set_gain_profile, None, None, None, 20), Jump("bs_saga_perfil")]
                        hbox:
                            spacing 6
                            textbutton "Ganar ahora" action [Function(bs_saga_dev_apply_semirandom_gain, _runs), Jump("bs_saga_perfil")]
                            textbutton "Estimación 1k EXP / 5k oro" action [Function(bs_saga_set_message, "Estimado: " + str(_est.get("duels_needed", 0)) + " duelo(s). EXP: " + str(_est.get("duels_for_exp", 0)) + " · Oro: " + str(_est.get("duels_for_gold", 0))), Jump("bs_saga_perfil")]
                        hbox:
                            spacing 6
                            textbutton ("Infinite Gold: " + ("ON" if bool(getattr(store, "bs_saga_dev_infinite_gold", False)) else "OFF")):
                                action [Function(bs_saga_dev_toggle_infinite_gold, None), Jump("bs_saga_perfil")]
                            textbutton ("Low-spec combate: " + ("ON" if bool(getattr(store, "bs_saga_dev_low_spec_mode", False)) else "OFF")):
                                action [Function(bs_saga_dev_apply_low_spec_mode, not bool(getattr(store, "bs_saga_dev_low_spec_mode", False))), Jump("bs_saga_perfil")]
                    null height 4
                    text "Progreso de tier (nivel + héroes por tier)" size 16 color "#9FC4E2"
                    for row in _tier_rows:
                        $ _tt = str(row.get("tier", "?"))
                        $ _hv = int(row.get("have_heroes", 0) or 0)
                        $ _nh = int(row.get("need_heroes", 0) or 0)
                        $ _nl = int(row.get("need_level", 0) or 0)
                        $ _ok = bool(row.get("ok", False))
                        text ("• " + _tt + ": Lv " + str(_lvl) + "/" + str(_nl) + " · Héroes " + str(_hv) + "/" + str(_nh)) size 14 color ("#8BD6A7" if _ok else "#9FC4E2")
            frame:
                xfill True
                yfill True
                background Solid("#102438")
                padding (12, 12)
                vbox:
                    spacing 8
                    text "Top héroes más usados" size 24 color "#EAF6FF"
                    text "Global" size 18 color "#CFE6FA"
                    if _top_total:
                        for row in _top_total:
                            text ("• " + str(row.get("hero_id", "?")) + " · " + str(row.get("score", 0)) + " usos") size 16 color "#D0E9FF"
                    else:
                        text "Sin datos todavía." size 16 color "#9FB9D1"
                    null height 10
                    text "Últimas 24h" size 18 color "#CFE6FA"
                    if _top_24:
                        for row in _top_24:
                            text ("• " + str(row.get("hero_id", "?")) + " · " + str(row.get("score", 0)) + " usos") size 16 color "#D0E9FF"
                    else:
                        text "Sin datos de 24h todavía." size 16 color "#9FB9D1"

screen bs_saga_tech_catalog_screen():
    tag menu
    $ _mode = str(bs_saga_tech_catalog_mode or "").lower()
    $ _tier = str(bs_saga_tech_catalog_tier or "C").upper()
    $ _tiers = bs_saga_tech_tier_keys()
    $ _ttype = str(bs_saga_tech_catalog_type or "ofensivas").lower()
    $ _types = bs_saga_tech_type_keys()
    $ _rows = bs_saga_tech_catalog().get(_tier, []) if _mode == "tier" else (bs_saga_tech_catalog_by_type().get(_ttype, []) if _mode == "type" else [])

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
            text "Territorio: Catálogo de técnicas" size 22 color "#D7EEFF" yalign 0.7
            null width 70
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
                xsize 240
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Modo de listado" size 24 color "#DDEEFF"
                    textbutton "Por tier":
                        action Function(bs_saga_tech_catalog_set_mode, "tier")
                    textbutton "Por tipo":
                        action Function(bs_saga_tech_catalog_set_mode, "type")
                    null height 8

                    if _mode == "tier":
                        text "Tiers" size 24 color "#DDEEFF"
                        for tt in _tiers:
                            textbutton "Tier [tt]":
                                action SetVariable("bs_saga_tech_catalog_tier", tt)
                    elif _mode == "type":
                        text "Tipos" size 24 color "#DDEEFF"
                        for tp in _types:
                            $ _tp_label = bs_saga_labelize(tp)
                            textbutton _tp_label:
                                action SetVariable("bs_saga_tech_catalog_type", tp)

            frame:
                xfill True
                yfill True
                padding (12, 12)
                background Solid("#102438")
                vbox:
                    spacing 8
                    if _mode == "tier":
                        text "Técnicas liberadas · Tier [_tier]" size 22 color "#EAF6FF"
                    elif _mode == "type":
                        $ _type_label = bs_saga_labelize(_ttype)
                        text "Técnicas liberadas · Tipo [_type_label]" size 22 color "#EAF6FF"
                    else:
                        text "Selecciona \"Por tier\" o \"Por tipo\" para desplegar categorías." size 20 color "#AFCFE8"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 410
                        vbox:
                            spacing 8
                            if _rows:
                                for row in _rows:
                                    $ _n = str(row.get("name", "?") or "?")
                                    $ _d = str(row.get("desc", "") or "")
                                    frame:
                                        xfill True
                                        background Solid("#173048")
                                        padding (10, 8)
                                        vbox:
                                            spacing 4
                                            text _n size 20 color "#CDE7FF"
                                            text _d size 16 color "#AFCFE8"
                            else:
                                text ("Sin técnicas configuradas para este tier." if _mode == "tier" else ("Sin técnicas configuradas para este tipo." if _mode == "type" else "")) size 18 color "#9FB9D1"

screen bs_saga_tower_screen():
    tag menu

    $ _tf = str(bs_saga_tower_tier_filter or "ALL").upper()
    $ _selected_floor = int(bs_saga_tower_selected_floor or 1)
    $ _rows = bs_saga_tower_filter_floors(_tf, 100)
    $ _selected = bs_saga_tower_selected_row(_selected_floor, 100)
    $ _selected_tier = str(_selected.get("tier", "C") or "C").upper()
    $ _selected_tier_start = int(_selected.get("tier_range_start", 1) or 1)
    $ _selected_tier_end = int(_selected.get("tier_range_end", 10) or 10)
    $ _selected_slot_type = str(_selected.get("slot_type", "guardian") or "guardian")
    $ _selected_title = str(_selected.get("title", "—") or "—")
    $ _selected_subtitle = str(_selected.get("subtitle", "—") or "—")
    $ _selected_floor_label = int(_selected.get("floor", 1) or 1)
    $ _filter_label = ("todas" if _tf == "ALL" else ("tier " + _tf))

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
            text "Territorio: Torre del cielo" size 22 color "#D7EEFF" yalign 0.7
            null width 40
            textbutton "Volver al lobby" action Jump("bs_saga_lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 500
        padding (18, 18)
        background Solid("#14273B")

        hbox:
            spacing 16

            frame:
                xsize 240
                yfill True
                padding (10, 10)
                background Solid("#1F3348")
                vbox:
                    spacing 8
                    text "Pisos (1-100)" size 22 color "#DDEEFF"
                    text "Filtro: [_filter_label]" size 16 color "#9FC4E2"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 420
                        vbox:
                            spacing 6
                            for row in _rows:
                                $ _f = int(row.get("floor", 1) or 1)
                                $ _tier = str(row.get("tier", "C") or "C").upper()
                                textbutton ("Piso %03d · Tier %s" % (_f, _tier)):
                                    action SetVariable("bs_saga_tower_selected_floor", _f)

            frame:
                xfill True
                yfill True
                padding (14, 14)
                background Solid("#11253A")
                vbox:
                    spacing 10

                    hbox:
                        spacing 8
                        text "Tiers" size 20 color "#DCEEFF"
                        textbutton "Todos" action SetVariable("bs_saga_tower_tier_filter", "ALL")
                        textbutton "Tier C" action SetVariable("bs_saga_tower_tier_filter", "C")
                        textbutton "Tier B" action SetVariable("bs_saga_tower_tier_filter", "B")
                        textbutton "Tier A" action SetVariable("bs_saga_tower_tier_filter", "A")
                        textbutton "Tier S" action SetVariable("bs_saga_tower_tier_filter", "S")

                    hbox:
                        spacing 20
                        frame:
                            xsize 290
                            ysize 360
                            background Solid("#0D1A2A")
                            padding (12, 12)
                            vbox:
                                spacing 8
                                text ("Panel visual · Piso %03d" % _selected_floor_label) size 18 color "#CDE7FF"
                                null height 240
                                text "Placeholder visual (héroe / NPC / evento)." size 16 color "#8EABC5"

                        frame:
                            xfill True
                            ysize 360
                            padding (10, 10)
                            background Solid("#1A3044")
                            vbox:
                                spacing 8
                                text ("Información del piso %03d" % _selected_floor_label) size 20 color "#E5F4FF"
                                frame:
                                    xfill True
                                    background Solid("#1B3348")
                                    padding (10, 8)
                                    vbox:
                                        spacing 6
                                        text ("Tier asignado: " + _selected_tier) size 18 color "#D0E9FF"
                                        text ("Rango tier: pisos %03d-%03d" % (_selected_tier_start, _selected_tier_end)) size 17 color "#B8D9F2"
                                        text ("Tipo de nodo: " + ("Guardián" if _selected_slot_type == "guardian" else "Buff / Sorpresa")) size 18 color "#D0E9FF"
                                        text ("Estado: " + _selected_title) size 17 color "#B8D9F2"
                                        text ("Detalle: " + _selected_subtitle) size 17 color "#B8D9F2"
                                frame:
                                    xfill True
                                    background Solid("#173048")
                                    padding (10, 8)
                                    text "Placeholder de stats/loot/requisitos del piso (por completar)." size 16 color "#AFCFE8"

init -899 python:
    def bs_saga_ui_hub_lobby_screen_split_status_v1():
        return {
            "module": "ui_hub_screens_lobby",
            "status": "phase_5_done",
            "migrated_screens": [
                "bs_saga_lobby_screen",
                "bs_saga_section_shell",
                "bs_saga_heroes_screen",
                "bs_saga_catalog_screen",
                "bs_saga_inventory_screen",
                "bs_saga_profile_screen",
                "bs_saga_tech_catalog_screen",
                "bs_saga_tower_screen"
            ]
        }
