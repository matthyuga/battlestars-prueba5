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

            textbutton "⚔ Duelo libre" action Return("nav:duelo_libre")

            textbutton ("▼ Torneo" if bs_saga_tournament_panel_open else "▶ Torneo"):
                action ToggleVariable("bs_saga_tournament_panel_open")

            if bs_saga_tournament_panel_open:
                frame:
                    xfill True
                    padding (10, 10)
                    background Solid("#22384D")
                    vbox:
                        spacing 8
                        textbutton "Tier C" action Return("nav:torneo_tier_c")
                        textbutton "Tier B (no disponible)" action Return("nav:torneo_tier_b_locked")
                        textbutton "Tier A (no disponible)" action Return("nav:torneo_tier_a_locked")

            textbutton "🗼 Torre del cielo (preview)" action Return("nav:torre_cielo")

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
                textbutton "Perfil" action Return("nav:perfil")
                textbutton "Preparación":
                    action [SetVariable("bs_saga_prep_intent_duel", False), SetVariable("bs_saga_prep_context", "room"), Return("nav:preparacion")]
                textbutton "Héroes" action Return("nav:heroes")
                textbutton "Tienda" action Return("nav:tienda")
                textbutton "Inventario" action Return("nav:inventario")
                textbutton "Catálogo de itens" action Return("nav:catalogo_items")
                textbutton "Catálogo de técnicas" action Return("nav:catalogo_tecnicas")

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
            textbutton "Volver al lobby" action Return("nav:lobby")

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
    default _selected_idx = 0
    default _qty = 1
    default _filter_rarity = "all"
    default _filter_tier = "all"
    default _search_query = ""
    default _show_rarity_menu = False
    default _show_tier_menu = False
    $ _cat = str(bs_saga_catalog_category or "consumibles")
    $ _groups = bs_saga_catalog_groups(_cat)
    $ _grp = str(bs_saga_catalog_group or "")
    if _grp not in _groups:
        $ _grp = _groups[0] if _groups else ""
        $ bs_saga_catalog_group = _grp
    $ _grp_label = _grp.capitalize() if _grp else "—"
    $ _items_all = bs_saga_catalog_items(_cat, _grp)
    $ _rarity_opts = ["all", "common", "rare", "special", "epic", "legendary", "mythic", "infernal"]
    $ _tier_opts = ["all", "C", "B", "A", "S", "SS", "SSS", "IV"]
    if _filter_rarity not in _rarity_opts:
        $ _filter_rarity = "all"
    if _filter_tier not in _tier_opts:
        $ _filter_tier = "all"
    $ _search_norm = str(_search_query or "").strip().lower()
    $ _items = [i for i in _items_all if ((_filter_rarity == "all") or (str(i.get("rarity", "") or "").strip().lower() == _filter_rarity)) and ((_filter_tier == "all") or (str(i.get("tier_req", "") or "").strip().upper() == _filter_tier)) and ((_search_norm == "") or (_search_norm in str(i.get("name", "") or "").lower()) or (_search_norm in str(i.get("meta", "") or "").lower()))]
    $ _cats = bs_saga_catalog_category_keys()
    $ _cat_label = bs_saga_labelize(_cat)
    $ _gold = bs_saga_gold()
    $ _last_msg = str(bs_saga_last_tx_message or "")
    if _selected_idx < 0 or _selected_idx >= len(_items):
        $ _selected_idx = 0
    $ _selected_item = _items[_selected_idx] if _items else {}
    $ _sel_name = str(_selected_item.get("name", "Sin selección") or "Sin selección")
    $ _sel_rarity = str(_selected_item.get("rarity", "-") or "-")
    $ _sel_tier = str(_selected_item.get("tier_req", "-") or "-")
    $ _sel_meta = str(_selected_item.get("meta", "Selecciona un ítem del listado central.") or "Selecciona un ítem del listado central.")
    $ _sel_price = bs_saga_item_price(_selected_item) if _selected_item else 0
    $ _total_price = int(_sel_price) * int(_qty)
    $ _inf_gold = bool(getattr(store, "bs_saga_dev_infinite_gold", False))
    $ _can_buy = bool(_items) and (_inf_gold or (int(_gold) >= int(_total_price)))
    $ _buy_action = Function(bs_saga_ui_call, bs_saga_buy_item, _selected_item, _qty) if _items else NullAction()
    $ _main_left = int((config.screen_width * 0.5) - (980 * 0.5))
    $ _main_top = int((config.screen_height * 0.56) - (560 * 0.56))
    $ _popup_y = _main_top + 86
    $ _has_active_filters = (_filter_rarity != "all") or (_filter_tier != "all") or (_search_norm != "")
    $ _last_msg_lc = _last_msg.lower() if _last_msg else ""
    $ _last_msg_color = "#8BD6A7" if ("compraste" in _last_msg_lc or "ok" in _last_msg_lc or "éxito" in _last_msg_lc) else ("#FF9A9A" if ("insuficiente" in _last_msg_lc or "inválida" in _last_msg_lc or "error" in _last_msg_lc) else "#BFDDF5")

    add Solid("#0E1A28")

    # Header (Fase 0: estructura principal)
    frame:
        xalign 0.5
        yalign 0.07
        xsize 990
        ysize 82
        background Solid("#66C8FF")

    frame:
        xalign 0.5
        yalign 0.07
        xsize 978
        ypadding 12
        background Solid("#2C4963")
        hbox:
            spacing 10
            text "BATTLESTARS SAGA" size 30 color "#5FC6FF"
            text "Territorio · Catálogo de itens" size 18 color "#D7EEFF" yalign 0.7
            text ("Oro: " + str(_gold)) size 18 color "#F7D774" yalign 0.7
            null width 20
            textbutton "Volver" action Return("nav:lobby")

    # Contenedor principal por módulos (Fase 0)
    frame:
        xalign 0.5
        yalign 0.56
        xsize 980
        ysize 560
        padding (16, 16)
        background Solid("#13273A")
        vbox:
            spacing 10
            text "Catálogo de itens" size 32 color "#EAF6FF"

            # Barra superior de categorías + filtros (estructura, sin lógica completa aún)
            hbox:
                spacing 8
                for ck in _cats:
                    $ lbl = "Consumibles" if ck == "consumibles" else ("Permanentes" if ck == "permanentes" else "Materiales")
                    textbutton "[lbl]":
                        action [
                            Function(bs_saga_catalog_set_category, ck),
                            SetScreenVariable("_selected_idx", 0),
                            SetScreenVariable("_qty", 1),
                            SetScreenVariable("_filter_rarity", "all"),
                            SetScreenVariable("_filter_tier", "all"),
                            SetScreenVariable("_search_query", ""),
                            SetScreenVariable("_show_rarity_menu", False),
                            SetScreenVariable("_show_tier_menu", False),
                        ]
                        selected (ck == _cat)
                null width 20
                fixed:
                    xsize 130
                    ysize 40
                    frame:
                        xfill True
                        yfill True
                        xpadding 8
                        ypadding 5
                        background Solid("#1A3349")
                        hbox:
                            spacing 4
                            text "Rareza:" size 16 color "#9ED9FF"
                            textbutton ("Todas" if _filter_rarity == "all" else _filter_rarity.upper()):
                                action [
                                    ToggleScreenVariable("_show_rarity_menu", True, False),
                                    SetScreenVariable("_show_tier_menu", False),
                                ]
                fixed:
                    xsize 120
                    ysize 40
                    frame:
                        xfill True
                        yfill True
                        xpadding 8
                        ypadding 5
                        background Solid("#1A3349")
                        hbox:
                            spacing 4
                            text "Tier:" size 16 color "#9ED9FF"
                            textbutton ("Todos" if _filter_tier == "all" else _filter_tier):
                                action [
                                    ToggleScreenVariable("_show_tier_menu", True, False),
                                    SetScreenVariable("_show_rarity_menu", False),
                                ]
                frame:
                    xsize 230
                    xpadding 10
                    ypadding 5
                    background Solid("#1A3349")
                    input value ScreenVariableInputValue("_search_query") length 32 allow " abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ0123456789_-áéíóúÁÉÍÓÚ" size 16 color "#D6EEFF"
                if _has_active_filters:
                    textbutton "Limpiar filtros":
                        action [
                            SetScreenVariable("_filter_rarity", "all"),
                            SetScreenVariable("_filter_tier", "all"),
                            SetScreenVariable("_search_query", ""),
                            SetScreenVariable("_selected_idx", 0),
                            SetScreenVariable("_qty", 1),
                            SetScreenVariable("_show_rarity_menu", False),
                            SetScreenVariable("_show_tier_menu", False),
                        ]

            hbox:
                spacing 8

                # Panel lateral: subcategorías (grupos)
                frame:
                    xsize 150
                    yfill True
                    padding (10, 10)
                    background Solid("#1F3348")
                    vbox:
                        spacing 8
                        text ("Categorías · " + _cat_label) size 24 color "#DDEEFF"
                        viewport:
                            draggable True
                            mousewheel True
                            scrollbars "vertical"
                            ymaximum 420
                            vbox:
                                spacing 6
                                for g in _groups:
                                    $ _g_label = "Stats (Torre del cielo)" if g == "stats_torre" else bs_saga_labelize(g)
                                    textbutton "[_g_label]":
                                        action [
                                            Function(bs_saga_catalog_set_group, g),
                                            SetScreenVariable("_selected_idx", 0),
                                            SetScreenVariable("_qty", 1),
                                            SetScreenVariable("_filter_rarity", "all"),
                                            SetScreenVariable("_filter_tier", "all"),
                                            SetScreenVariable("_search_query", ""),
                                            SetScreenVariable("_show_rarity_menu", False),
                                            SetScreenVariable("_show_tier_menu", False),
                                        ]
                                        selected (g == _grp)
                # Panel central: listado de ítems
                frame:
                    xsize 520
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
                            ymaximum 420
                            vbox:
                                spacing 6
                                if _items:
                                    for idx, it in enumerate(_items):
                                        $ _n = str(it.get("name", "?") or "?")
                                        $ _r = str(it.get("rarity", "-") or "-")
                                        $ _t = str(it.get("tier_req", "-") or "-")
                                        $ _r_show = "-" if _r in ("", "-") else _r
                                        $ _t_show = "-" if _t in ("", "-") else _t
                                        $ _p = bs_saga_item_price(it)
                                        $ _row_bg = "#334A64" if idx == _selected_idx else "#173048"
                                        frame:
                                            xfill True
                                            background Solid(_row_bg)
                                            padding (8, 6)
                                            button:
                                                xfill True
                                                action [
                                                    SetScreenVariable("_selected_idx", idx),
                                                    SetScreenVariable("_qty", 1),
                                                ]
                                                hbox:
                                                    spacing 8
                                                    text "• [_n]" size 17 color "#D0E9FF" xminimum 320
                                                    text ("Precio: " + str(_p)) size 16 color "#F7D774" xminimum 80
                                else:
                                    if _has_active_filters:
                                        text "No hay resultados para los filtros actuales." size 18 color "#FFB3B3"
                                    else:
                                        text "Sin itens cargados todavía para este grupo." size 18 color "#9FB9D1"
                        text ("Total en lista: " + str(len(_items)) + " ítem(s)") size 15 color "#8FB6D6"
                        if _has_active_filters:
                            $ _r_txt = ("Todas" if _filter_rarity == "all" else _filter_rarity.upper())
                            $ _t_txt = ("Todos" if _filter_tier == "all" else _filter_tier)
                            text ("Filtros activos · Rareza: " + _r_txt + " · Tier: " + _t_txt + " · Buscar: " + (_search_query if _search_query else "—")) size 14 color "#9ED9FF"

                # Panel derecho: detalle + compra
                frame:
                    xsize 250
                    yfill True
                    padding (12, 12)
                    background Solid("#1A2C42")
                    vbox:
                        spacing 10
                        text "Detalle del ítem" size 22 color "#EAF6FF"
                        frame:
                            xfill True
                            ypadding 8
                            xpadding 8
                            background Solid("#173048")
                            text "[_sel_name]" size 24 color "#D6EEFF"
                        text ("Rareza: " + ("-" if _sel_rarity in ("", "-") else _sel_rarity)) size 17 color "#BFDCF4"
                        text ("Tier: " + ("-" if _sel_tier in ("", "-") else _sel_tier)) size 17 color "#BFDCF4"
                        text ("Precio unitario: " + str(_sel_price)) size 18 color "#F7D774"
                        frame:
                            xfill True
                            ypadding 8
                            xpadding 8
                            background Solid("#173048")
                            text "[_sel_meta]" size 16 color "#D0E9FF"
                        text "Cantidad" size 18 color "#9ED9FF"
                        hbox:
                            spacing 8
                            textbutton "-":
                                action SetScreenVariable("_qty", max(1, int(_qty) - 1))
                            text "[_qty]" size 20 color "#EAF6FF" yalign 0.5
                            textbutton "+":
                                action SetScreenVariable("_qty", min(99, int(_qty) + 1))
                        text ("Total: " + str(_total_price)) size 18 color "#F7D774"
                        if _items:
                            if _can_buy:
                                text "Compra disponible" size 15 color "#8BD6A7"
                            else:
                                text "Oro insuficiente para esta cantidad" size 15 color "#FF9A9A"
                        textbutton ("Comprar x" + str(_qty)):
                            action _buy_action
                            sensitive _can_buy
                        text ("Costo total: " + str(_total_price)) size 15 color "#D6EEFF"
                        if _last_msg:
                            frame:
                                xfill True
                                xpadding 8
                                ypadding 8
                                background Solid("#173048")
                                text "[_last_msg]" size 14 color _last_msg_color

    # Popups flotantes (dibujados al final del screen, por encima de paneles)
    if _show_rarity_menu:
        frame:
            xpos (_main_left + 470)
            ypos _popup_y
            xpadding 2
            ypadding 2
            background Solid("#0B1D2E88")
            frame:
                xpadding 8
                ypadding 8
                background Solid("#1A3349B8")
                vbox:
                    spacing 4
                    text "Rareza" size 15 color "#9ED9FF"
                    for r in _rarity_opts:
                        $ _r_lbl = "Todas" if r == "all" else r.upper()
                        textbutton "[_r_lbl]":
                            action [
                                SetScreenVariable("_filter_rarity", r),
                                SetScreenVariable("_selected_idx", 0),
                                SetScreenVariable("_qty", 1),
                                SetScreenVariable("_show_rarity_menu", False),
                            ]
    if _show_tier_menu:
        frame:
            xpos (_main_left + 610)
            ypos _popup_y
            xpadding 2
            ypadding 2
            background Solid("#0B1D2E88")
            frame:
                xpadding 8
                ypadding 8
                background Solid("#1A3349B8")
                vbox:
                    spacing 4
                    text "Tier" size 15 color "#9ED9FF"
                    for t in _tier_opts:
                        $ _t_lbl = "Todos" if t == "all" else t
                        textbutton "[_t_lbl]":
                            action [
                                SetScreenVariable("_filter_tier", t),
                                SetScreenVariable("_selected_idx", 0),
                                SetScreenVariable("_qty", 1),
                                SetScreenVariable("_show_tier_menu", False),
                            ]

screen bs_saga_inventory_screen():
    tag menu
    default _bucket_filter = "all"
    default _selected_idx = 0
    $ _rows = bs_saga_inventory_rows()
    $ _gold = bs_saga_gold()
    $ _bucket_labels = {
        "all": "Todos",
        "consumables": "Consumibles",
        "equipables": "Equipo",
        "materials": "Materiales",
        "key_items": "Objetos clave",
    }
    $ _bucket_keys = ["all", "consumables", "equipables", "materials", "key_items"]
    $ _rows_filtered = [r for r in _rows if (_bucket_filter == "all") or (str(r.get("bucket", "") or "").strip().lower() == _bucket_filter)]
    if _selected_idx < 0 or _selected_idx >= len(_rows_filtered):
        $ _selected_idx = 0
    $ _selected_row = _rows_filtered[_selected_idx] if _rows_filtered else {}
    $ _selected_bucket = bs_saga_labelize(_selected_row.get("bucket", ""))
    $ _selected_item = str(_selected_row.get("item_id", "Sin selección") or "Sin selección")
    $ _selected_qty = int(_selected_row.get("qty", 0) or 0)

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
            textbutton "Volver al lobby" action Return("nav:lobby")

    frame:
        xalign 0.5
        yalign 0.56
        xsize 1120
        ysize 560
        padding (16, 16)
        background Solid("#13273A")
        hbox:
            spacing 10

            # Panel izquierdo: categorías/buckets (Fase 1 layout base)
            frame:
                xsize 230
                yfill True
                padding (10, 10)
                background Solid("#1A3044")
                vbox:
                    spacing 8
                    text "Categorías" size 24 color "#DDEEFF"
                    for k in _bucket_keys:
                        $ _lbl = str(_bucket_labels.get(k, bs_saga_labelize(k)) or bs_saga_labelize(k))
                        textbutton "[_lbl]":
                            action [
                                SetScreenVariable("_bucket_filter", k),
                                SetScreenVariable("_selected_idx", 0),
                            ]
                            selected (_bucket_filter == k)
                    null height 10
                    text ("Filtro: " + str(_bucket_labels.get(_bucket_filter, "Todos"))) size 14 color "#9FC4E2"

            # Panel central: listado de inventario (Fase 1 layout base)
            frame:
                xsize 560
                yfill True
                padding (10, 10)
                background Solid("#102438")
                vbox:
                    spacing 8
                    text "Inventario de cuenta" size 28 color "#EAF6FF"
                    text ("Total visibles: " + str(len(_rows_filtered))) size 14 color "#9FC4E2"
                    viewport:
                        draggable True
                        mousewheel True
                        scrollbars "vertical"
                        ymaximum 450
                        vbox:
                            spacing 6
                            if _rows_filtered:
                                for idx, row in enumerate(_rows_filtered):
                                    $ _b = bs_saga_labelize(row.get("bucket", ""))
                                    $ _id = str(row.get("item_id", "?") or "?")
                                    $ _q = int(row.get("qty", 0) or 0)
                                    $ _row_bg = "#334A64" if idx == _selected_idx else "#173048"
                                    frame:
                                        xfill True
                                        background Solid(_row_bg)
                                        padding (8, 7)
                                        button:
                                            xfill True
                                            action SetScreenVariable("_selected_idx", idx)
                                            hbox:
                                                spacing 8
                                                text ("• " + _id) size 17 color "#D0E9FF" xminimum 370
                                                text ("Bucket: " + _b) size 15 color "#A9CAE6" xminimum 120
                                                text ("Qty: " + str(_q)) size 16 color "#8BD6A7"
                            else:
                                text "No hay ítems para esta categoría." size 18 color "#9FB9D1"

            # Panel derecho: detalle seleccionado (Fase 1 layout base)
            frame:
                xsize 280
                yfill True
                padding (12, 12)
                background Solid("#1A2C42")
                vbox:
                    spacing 10
                    text "Detalle del objeto" size 22 color "#EAF6FF"
                    frame:
                        xfill True
                        ypadding 8
                        xpadding 8
                        background Solid("#173048")
                        text "[_selected_item]" size 22 color "#D6EEFF"
                    text ("Bucket: " + (_selected_bucket if _selected_bucket else "-")) size 17 color "#BFDCF4"
                    text ("Cantidad en posesión: " + str(_selected_qty)) size 17 color "#8BD6A7"
                    frame:
                        xfill True
                        xpadding 8
                        ypadding 8
                        background Solid("#173048")
                        if _rows_filtered:
                            text "Vista base Fase 1: en siguientes fases agregamos rareza, descripción larga e iconografía." size 14 color "#AFCFE8"
                        else:
                            text "Selecciona una categoría con ítems para ver detalles." size 14 color "#AFCFE8"

screen bs_saga_profile_screen():
    tag menu
    $ _acc = bs_saga_account()
    $ _tier_current = bs_saga_refresh_account_tier(reason="profile_screen")
    $ _rotation_tier_current = bs_saga_refresh_rotation_tier(reason="profile_screen")
    $ _gold = int(_acc.get("gold", 0) or 0)
    $ _lvl = int(_acc.get("level", 1) or 1)
    $ _exp = int(_acc.get("exp", 0) or 0)
    $ _next = int(_acc.get("exp_to_next", 100) or 100)
    $ _exp_ratio = bs_saga_exp_progress()
    $ _tier = str(_tier_current or "")
    $ _rotation_tier = str(_rotation_tier_current or "C")
    $ _tier_txt = (_tier if _tier else "Sin tier")
    $ _rotation_tier_txt = (_rotation_tier if _rotation_tier else "C")
    $ _top_total = bs_saga_top_heroes(3, False)
    $ _top_24 = bs_saga_top_heroes(3, True)
    $ _tier_rows = bs_saga_tier_progress_rows()
    $ _exp_base = int(getattr(store, "bs_saga_dev_gain_exp_base", 90) or 90)
    $ _gold_base = int(getattr(store, "bs_saga_dev_gain_gold_base", 150) or 150)
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
                xsize 520
                yfill True
                background Solid("#1A3044")
                padding (12, 12)
                viewport:
                    draggable True
                    mousewheel True
                    scrollbars "vertical"
                    ymaximum 430
                    vbox:
                        spacing 8
                        text "Resumen de cuenta" size 28 color "#EAF6FF"
                        text ("Tier cuenta/pool: " + _tier_txt) size 18 color "#D0E9FF"
                        text ("Tier rotación (por nivel): " + _rotation_tier_txt) size 16 color "#A9CAE6"
                        if _tier_txt != _rotation_tier_txt:
                            text ("⚠ Desfase esperado: ya desbloqueaste rotación tier " + _rotation_tier_txt + " por nivel, pero el pool sigue en tier " + _tier_txt + " hasta completar héroes mínimos.") size 13 color "#FFD166"
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
                                textbutton "+50k oro" action Function(bs_saga_ui_call, bs_saga_dev_set_account_state, _gold + 50000, None, None, None)
                                textbutton "Lv 99" action Function(bs_saga_ui_call, bs_saga_dev_set_account_state, None, 99, None, None)
                                textbutton "EXP 0" action Function(bs_saga_ui_call, bs_saga_dev_set_account_state, None, None, 0, None)
                            text ("Tool semi-random · base EXP " + str(_exp_base) + " · base Oro " + str(_gold_base) + " · var " + str(_var_pct) + "% · runs " + str(_runs)) size 13 color "#F6E6A9"
                            hbox:
                                spacing 6
                                textbutton "EXP -10" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, _exp_base - 10, None, None, None)
                                textbutton "EXP +10" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, _exp_base + 10, None, None, None)
                                textbutton "Oro -10" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, _gold_base - 10, None, None)
                                textbutton "Oro +10" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, _gold_base + 10, None, None)
                            hbox:
                                spacing 6
                                textbutton "Var -5%" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, None, _var_pct - 5, None)
                                textbutton "Var +5%" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, None, _var_pct + 5, None)
                                textbutton "Runs x1" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, None, None, 1)
                                textbutton "Runs x5" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, None, None, 5)
                                textbutton "Runs x20" action Function(bs_saga_ui_call, bs_saga_dev_set_gain_profile, None, None, None, 20)
                            hbox:
                                spacing 6
                                textbutton "Ganar ahora" action Function(bs_saga_ui_call, bs_saga_dev_apply_semirandom_gain, _runs)
                                textbutton "Estimación 1k EXP / 5k oro" action Function(bs_saga_ui_call, bs_saga_set_message, "Estimado: " + str(_est.get("duels_needed", 0)) + " duelo(s). EXP: " + str(_est.get("duels_for_exp", 0)) + " · Oro: " + str(_est.get("duels_for_gold", 0)))
                            hbox:
                                spacing 6
                                textbutton ("Infinite Gold: " + ("ON" if bool(getattr(store, "bs_saga_dev_infinite_gold", False)) else "OFF")):
                                    action Function(bs_saga_ui_call, bs_saga_dev_toggle_infinite_gold, None)
                                textbutton ("Low-spec combate: " + ("ON" if bool(getattr(store, "bs_saga_dev_low_spec_mode", False)) else "OFF")):
                                    action Function(bs_saga_ui_call, bs_saga_dev_apply_low_spec_mode, not bool(getattr(store, "bs_saga_dev_low_spec_mode", False)))
                        null height 4
                        text "Progreso de tier (nivel + héroes por tier)" size 16 color "#9FC4E2"
                        for row in _tier_rows:
                            $ _tt = str(row.get("tier", "?"))
                            $ _hv = int(row.get("have_heroes", 0) or 0)
                            $ _nh = int(row.get("need_heroes", 0) or 0)
                            $ _nl = int(row.get("need_level", 0) or 0)
                            $ _ok = bool(row.get("ok", False))
                            $ _rot_unlock = bool(row.get("rotation_unlocked_by_level", False))
                            text ("• " + _tt + ": Lv " + str(_lvl) + "/" + str(_nl) + " · Héroes " + str(_hv) + "/" + str(_nh) + " · Rotación " + ("✅" if _rot_unlock else "⛔") + " · Pool " + ("✅" if _ok else "⛔")) size 14 color ("#8BD6A7" if _ok else ("#A9CAE6" if _rot_unlock else "#9FC4E2"))
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
            textbutton "Volver al lobby" action Return("nav:lobby")

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
