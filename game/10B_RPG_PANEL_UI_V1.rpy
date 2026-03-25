# ===============================================================
# 10B_RPG_PANEL_UI_V1.rpy
# Fase 2 — Pantalla mínima funcional panel RPG (Ren'Py)
# ===============================================================

init -870 python:
    import copy
    import renpy.store as S

    def rpgp_get_state():
        st = getattr(S, "rpg_panel_state_v1", None)
        if not isinstance(st, dict):
            st = rpgp_seed_new_player()
            S.rpg_panel_state_v1 = st
        return st

    def rpgp_recompute_state():
        st = rpgp_get_state()
        S.rpg_panel_state_v1 = compute_preview(st)
        return S.rpg_panel_state_v1

    def rpgp_open_panel(seed_name="new_player"):
        if seed_name == "reg10":
            S.rpg_panel_state_v1 = rpgp_seed_reg10_balanced()
            S.rpg_panel_state_seed_name = "reg10_balanced"
        elif seed_name == "reg35":
            S.rpg_panel_state_v1 = rpgp_seed_reg35_specialized()
            S.rpg_panel_state_seed_name = "reg35_specialized"
        else:
            S.rpg_panel_state_v1 = rpgp_seed_new_player()
            S.rpg_panel_state_seed_name = "new_player"

        S.rpg_panel_baseline_v1 = copy.deepcopy(S.rpg_panel_state_v1)
        S.rpg_panel_confirm_modal_open = False
        return S.rpg_panel_state_v1

    def rpgp_on_select_principal(attr):
        st = rpgp_get_state()
        if str(attr or "") in RPGP_MAIN_STATS:
            st.setdefault("principal", {})["selected"] = str(attr)
        return rpgp_recompute_state()

    def rpgp_on_change_distribution(bucket, value):
        st = rpgp_get_state()
        b = str(bucket or "")
        v = _rpgp_to_int(value, 0)
        if b in RPGP_PRINCIPAL_BUCKETS and v in RPGP_PRINCIPAL_ALLOWED_STEPS:
            st.setdefault("principal", {}).setdefault("distribution", {})[b] = v
        return rpgp_recompute_state()

    def rpgp_on_add_stat(attr):
        st = rpgp_get_state()
        a = str(attr or "")
        if a not in RPGP_ALL_STATS:
            return rpgp_recompute_state()

        pending = st.setdefault("pending", {}).get("stat_points", 0)
        if _rpgp_to_int(pending, 0) <= 0:
            return rpgp_recompute_state()

        hard_cap = _rpgp_to_int(st.get("limits", {}).get("stat_hard_cap", RPGP_STAT_HARD_CAP), RPGP_STAT_HARD_CAP)
        cur = _rpgp_to_int(st.setdefault("stats", {}).get(a, 0), 0)
        if cur < hard_cap:
            st["stats"][a] = cur + 1
            st["pending"]["stat_points"] = max(0, _rpgp_to_int(pending, 0) - 1)

        return rpgp_recompute_state()

    def rpgp_on_remove_stat(attr):
        st = rpgp_get_state()
        a = str(attr or "")
        if a not in RPGP_ALL_STATS:
            return rpgp_recompute_state()

        cur = _rpgp_to_int(st.setdefault("stats", {}).get(a, 0), 0)
        if cur > 0:
            st["stats"][a] = cur - 1
            st.setdefault("pending", {})["stat_points"] = _rpgp_to_int(st.get("pending", {}).get("stat_points", 0), 0) + 1

        return rpgp_recompute_state()

    def rpgp_on_add_pool(pool_type, amount):
        st = rpgp_get_state()
        t = str(pool_type or "").strip().lower()
        step = max(0, _rpgp_to_int(amount, 0))
        if step <= 0:
            return rpgp_recompute_state()

        pool = st.setdefault("pool", {})
        available = _rpgp_to_int(pool.get("available", 0), 0)
        if available <= 0:
            return rpgp_recompute_state()

        inc = step if step <= available else available
        if t in ("offense", "ofensiva", "offensive"):
            pool["offensive_spent"] = _rpgp_to_int(pool.get("offensive_spent", 0), 0) + inc
        elif t in ("defense", "defensa", "defensive"):
            pool["defensive_spent"] = _rpgp_to_int(pool.get("defensive_spent", 0), 0) + inc

        return rpgp_recompute_state()

    def rpgp_on_remove_pool(pool_type, amount):
        st = rpgp_get_state()
        t = str(pool_type or "").strip().lower()
        step = max(0, _rpgp_to_int(amount, 0))
        if step <= 0:
            return rpgp_recompute_state()

        pool = st.setdefault("pool", {})
        if t in ("offense", "ofensiva", "offensive"):
            cur = _rpgp_to_int(pool.get("offensive_spent", 0), 0)
            pool["offensive_spent"] = max(0, cur - step)
        elif t in ("defense", "defensa", "defensive"):
            cur = _rpgp_to_int(pool.get("defensive_spent", 0), 0)
            pool["defensive_spent"] = max(0, cur - step)

        return rpgp_recompute_state()

    def rpgp_on_toggle_mode(mode):
        st = rpgp_get_state()
        m = str(mode or "").strip().lower()
        st.setdefault("mode", {})["view"] = "pvp" if m == "pvp" else "pve"
        return rpgp_recompute_state()

    def rpgp_on_reset_changes():
        base = getattr(S, "rpg_panel_baseline_v1", None)
        if isinstance(base, dict):
            S.rpg_panel_state_v1 = copy.deepcopy(base)
        else:
            S.rpg_panel_state_v1 = rpgp_seed_new_player()
        return rpgp_recompute_state()

    def rpgp_on_confirm_open_modal():
        S.rpg_panel_confirm_modal_open = True

    def rpgp_on_confirm_close_modal():
        S.rpg_panel_confirm_modal_open = False

    def rpgp_on_confirm_apply():
        st = rpgp_recompute_state()
        if st.get("validation", {}).get("is_valid", False):
            S.rpg_panel_baseline_v1 = copy.deepcopy(st)
            S.rpg_panel_confirm_modal_open = False


default rpg_panel_baseline_v1 = None

default rpg_panel_confirm_modal_open = False


screen rpg_panel_v1():
    tag menu

    $ st = rpg_panel_state_v1 if isinstance(rpg_panel_state_v1, dict) else rpgp_seed_new_player()
    $ player = st.get("player", {})
    $ stats = st.get("stats", {})
    $ principal = st.get("principal", {})
    $ pool = st.get("pool", {})
    $ preview = st.get("preview", {})
    $ valid = st.get("validation", {})
    $ mode = st.get("mode", {}).get("view", "pve")
    $ caps = compute_caps_for_register(player.get("register", 0), mode)
    $ consume = compute_consumption_at_cap(player.get("register", 0), mode)

    frame:
        xfill True
        yfill True
        padding (20, 20)

        vbox:
            spacing 12

            text "Panel RPG v1 — Asignación de puntos" size 34
            text "Seed: [rpg_panel_state_seed_name] | Nivel [player.get('level', 1)] | Registro [player.get('register', 0)] | EXP [player.get('exp_current', 0)]/[player.get('exp_max', 100)]" size 20

            hbox:
                spacing 16

                # Panel A
                frame:
                    xsize 560
                    yfill True
                    padding (12, 12)
                    vbox:
                        spacing 10
                        text "Panel A — Identidad y Stats" size 24
                        text "Principal: [principal.get('selected', 'None')]" size 18
                        text "Puntos de stat pendientes: [st.get('pending', {}).get('stat_points', 0)]" size 18

                        hbox:
                            spacing 8
                            text "Elegir principal:" size 18
                            for key in RPGP_MAIN_STATS:
                                textbutton "[key]" action Function(rpgp_on_select_principal, key)

                        null height 4
                        for s in RPGP_ALL_STATS:
                            hbox:
                                spacing 8
                                xfill True
                                text "[s]" xsize 170
                                text "[stats.get(s, 0)]" xsize 40
                                textbutton "+" action Function(rpgp_on_add_stat, s)
                                textbutton "-" action Function(rpgp_on_remove_stat, s)

                # Panel B
                frame:
                    xfill True
                    yfill True
                    padding (12, 12)
                    vbox:
                        spacing 10
                        text "Panel B — Principal + Pool técnico" size 24
                        text "Distribución principal: [principal.get('distribution_total', 0)]/100 | Slots activos: [principal.get('active_slots', 0)]/[principal.get('max_slots', 4)]" size 18

                        for bucket in RPGP_PRINCIPAL_BUCKETS:
                            hbox:
                                spacing 8
                                text "[bucket]" xsize 120
                                text "Actual: [principal.get('distribution', {}).get(bucket, 0)]" xsize 120
                                for step in RPGP_PRINCIPAL_ALLOWED_STEPS:
                                    if step > 0:
                                        textbutton "[step]" action Function(rpgp_on_change_distribution, bucket, step)
                                textbutton "0" action Function(rpgp_on_change_distribution, bucket, 0)

                        null height 6
                        text "Modo de vista caps: [mode.upper()] | Tier [caps.get('tier', 'D')] | Cap Of [caps.get('offensive_cap', 0)] | Cap Def [caps.get('defensive_cap', 0)]" size 18
                        hbox:
                            spacing 8
                            textbutton "PVE" action Function(rpgp_on_toggle_mode, "pve")
                            textbutton "PVP" action Function(rpgp_on_toggle_mode, "pvp")

                        text "Pool total: [pool.get('total', 0)] | Of gastado: [pool.get('offensive_spent', 0)] | Def gastado: [pool.get('defensive_spent', 0)] | Disponible: [pool.get('available', 0)]" size 18
                        hbox:
                            spacing 8
                            textbutton "+Of 25" action Function(rpgp_on_add_pool, "ofensiva", 25)
                            textbutton "-Of 25" action Function(rpgp_on_remove_pool, "ofensiva", 25)
                            textbutton "+Def 25" action Function(rpgp_on_add_pool, "defensiva", 25)
                            textbutton "-Def 25" action Function(rpgp_on_remove_pool, "defensiva", 25)

                        null height 6
                        text "Preview antes/después" size 20
                        text "HP: [preview.get('hp_before', 0)] -> [preview.get('hp_after', 0)]" size 17
                        text "Energía: [preview.get('energia_before', 0)] -> [preview.get('energia_after', 0)]" size 17
                        text "Reiatsu: [preview.get('reiatsu_before', 0)] -> [preview.get('reiatsu_after', 0)]" size 17
                        text "Ataque: [preview.get('atk_before', 0)] -> [preview.get('atk_after', 0)]" size 17
                        text "Defensa: [preview.get('def_before', 0)] -> [preview.get('def_after', 0)]" size 17

                        null height 6
                        text "Consumo al cap (integración Fase 3)" size 20
                        text "Ofensiva cap/reiatsu: [consume.get('offensive', {}).get('cap', 0)] / [consume.get('offensive', {}).get('reiatsu', 0)]" size 16
                        text "Ofensiva energía — Esc9 [consume.get('offensive', {}).get('energy_scale9', 0)] | TecExtra [consume.get('offensive', {}).get('energy_tecnica_extra', 0)] | Red [consume.get('offensive', {}).get('energy_reductor', 0)] | Dir/Neg [consume.get('offensive', {}).get('energy_directo_negador', 0)] | Esp [consume.get('offensive', {}).get('energy_efecto_especial', 0)]" size 15
                        text "Defensiva cap/reiatsu: [consume.get('defensive', {}).get('cap', 0)] / [consume.get('defensive', {}).get('reiatsu', 0)]" size 16
                        text "Defensiva energía — Esc9 [consume.get('defensive', {}).get('energy_scale9', 0)] | Red [consume.get('defensive', {}).get('energy_reductora', 0)] | Reflect [consume.get('defensive', {}).get('energy_reflectora', 0)] | Esp [consume.get('defensive', {}).get('energy_efecto_especial', 0)]" size 15

            frame:
                xfill True
                padding (12, 12)
                vbox:
                    spacing 6
                    text "Validación" size 22
                    if valid.get("is_valid", False):
                        text "Estado: OK" color "#76ff76" size 18
                    else:
                        text "Estado: INVÁLIDO" color "#ff7676" size 18
                    if valid.get("errors", []):
                        for e in valid.get("errors", []):
                            text "• [e]" color "#ff9090" size 16
                    if valid.get("warnings", []):
                        for w in valid.get("warnings", []):
                            text "• [w]" color "#ffd27f" size 16

            hbox:
                spacing 10
                textbutton "Recalcular" action Function(rpgp_recompute_state)
                textbutton "Reiniciar cambios" action Function(rpgp_on_reset_changes)
                textbutton "Confirmar" action Function(rpgp_on_confirm_open_modal) sensitive valid.get("is_valid", False)
                textbutton "Salir" action Return()

    if rpg_panel_confirm_modal_open:
        use rpg_panel_confirm_modal_v1


screen rpg_panel_confirm_modal_v1():
    modal True
    zorder 200

    frame:
        xalign 0.5
        yalign 0.5
        xsize 780
        ysize 420
        padding (16, 16)

        vbox:
            spacing 12
            text "Confirmación final" size 30
            text "¿Aplicar cambios de stats, principal y pool técnico?" size 20

            $ st = rpg_panel_state_v1 if isinstance(rpg_panel_state_v1, dict) else rpgp_seed_new_player()
            $ preview = st.get("preview", {})
            text "HP: [preview.get('hp_before', 0)] -> [preview.get('hp_after', 0)]"
            text "Energía: [preview.get('energia_before', 0)] -> [preview.get('energia_after', 0)]"
            text "Reiatsu: [preview.get('reiatsu_before', 0)] -> [preview.get('reiatsu_after', 0)]"
            text "Ataque: [preview.get('atk_before', 0)] -> [preview.get('atk_after', 0)]"
            text "Defensa: [preview.get('def_before', 0)] -> [preview.get('def_after', 0)]"

            hbox:
                spacing 10
                textbutton "Cancelar" action Function(rpgp_on_confirm_close_modal)
                textbutton "Aplicar" action Function(rpgp_on_confirm_apply)


label rpgp_panel_v1:
    $ rpgp_open_panel("new_player")
    call screen rpg_panel_v1
    return

label rpgp_panel_v1_reg10:
    $ rpgp_open_panel("reg10")
    call screen rpg_panel_v1
    return

label rpgp_panel_v1_reg35:
    $ rpgp_open_panel("reg35")
    call screen rpg_panel_v1
    return
