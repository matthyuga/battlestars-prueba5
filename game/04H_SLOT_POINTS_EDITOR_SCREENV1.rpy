# ============================================================
# 04H_SLOT_POINTS_EDITOR_SCREENV1.rpy
# Fase D — Menú principal + editor v1 de puntos por slot
# ============================================================

# selección UI (persistente por sesión)
default spa_editor_selected_unit_key = "player:0"
default spa_editor_step = 100

init -930 python:
    import renpy.store as S

    def spa_ui_unit_keys_v1():
        """
        V1: slots objetivo iniciales para cimientos.
        Extensible a futuro con equipos dinámicos.
        """
        return ["player:0", "player:1", "enemy:0", "enemy:1"]

    def spa_ui_unit_label(unit_key):
        try:
            fn_parse = getattr(S, "bs_parse_unit_key", None)
            if callable(fn_parse):
                info = fn_parse(unit_key, default_side="player", default_slot=0)
                side = str(info.get("team", "player") or "player")
                slot = int(info.get("slot", 0) or 0)
                fn_tag = getattr(S, "bs_slot_tag", None)
                if callable(fn_tag):
                    return str(fn_tag(side, slot))
                return ("P{}".format(slot + 1) if side == "player" else "E{}".format(slot + 1))
        except:
            pass

        raw = str(unit_key or "player:0")
        if raw.startswith("enemy"):
            try:
                idx = int(raw.split(":", 1)[1] or 0)
            except:
                idx = 0
            return "E{}".format(idx + 1)
        try:
            idx = int(raw.split(":", 1)[1] or 0)
        except:
            idx = 0
        return "P{}".format(idx + 1)

    def spa_ui_tech_label(tech_id):
        labels = {
            "extra_attack": "Ataque Extra",
            "extra_tech": "Técnica Extra",
            "attack_reducer": "Ataque Reductor",
            "direct_attack": "Ataque Directo",
            "noatk_attack": "Ataque Negador",
            "stronger_attack": "Ataque más fuerte",
            "defense_extra": "Defensa Extra",
            "defense_reducer": "Defensa Reductora",
            "defense_reflect": "Defensa Reflectora",
            "defense_strong_block": "Defensa Fuerte",
        }
        return labels.get(str(tech_id or ""), str(tech_id or ""))

    def spa_ui_tech_ids_v1():
        order = [
            "extra_attack",
            "extra_tech",
            "attack_reducer",
            "direct_attack",
            "noatk_attack",
            "stronger_attack",
            "defense_extra",
            "defense_reducer",
            "defense_reflect",
            "defense_strong_block",
        ]
        # filtrar por existencia real en TECH_STATS
        stats = getattr(S, "TECH_STATS", {}) or {}
        out = []
        for tid in order:
            if isinstance(stats, dict) and tid in stats:
                out.append(tid)
        if out:
            return out
        # fallback si no está cargado TECH_STATS todavía
        return order

    def spa_ui_set_step(v):
        try:
            vv = int(v)
        except:
            vv = 100
        if vv not in (10, 50, 100):
            vv = 100
        S.spa_editor_step = vv
        return vv

    def spa_ui_apply_delta(unit_key, tech_id, delta):
        fn = getattr(S, "spa_add_bonus", None)
        if not callable(fn):
            return {"ok": False, "reason": "allocator_missing"}
        d = 0
        try:
            d = int(delta)
        except:
            d = 0
        if d >= 0:
            return fn(unit_key, tech_id, d, save=True)

        fn_sub = getattr(S, "spa_sub_bonus", None)
        if callable(fn_sub):
            return fn_sub(unit_key, tech_id, abs(d), save=True)

        # fallback robusto
        fn_get = getattr(S, "spa_get_bonus", None)
        fn_set = getattr(S, "spa_set_bonus", None)
        if callable(fn_get) and callable(fn_set):
            cur = int(fn_get(unit_key, tech_id) or 0)
            return fn_set(unit_key, tech_id, max(0, cur + d), save=True)

        return {"ok": False, "reason": "allocator_missing"}


screen slot_points_editor():
    tag menu

    use game_menu(_("Editor de puntos por slot"), scroll="viewport"):

        vbox:
            spacing 18

            label _("Configuración persistente de bonus por técnica")
            text _("Base de técnica no se modifica; aquí editas BONUS por slot. Reiatsu/Energía se recalculan automáticamente.") size 18

            $ allocator_ok = callable(getattr(store, "spa_ensure_state", None))

            if not allocator_ok:
                text _("Allocator no disponible. Verifica que 04Y_SLOT_POINT_ALLOCATOR_V1.rpy esté cargado.") color "#FF8888"
            else:
                $ _ = store.spa_ensure_state()
                $ selected = getattr(store, "spa_editor_selected_unit_key", "player:0") or "player:0"

                hbox:
                    spacing 10
                    text _("Slot:") size 20
                    for uk in store.spa_ui_unit_keys_v1():
                        textbutton "[store.spa_ui_unit_label(uk)]":
                            action SetVariable("spa_editor_selected_unit_key", uk)

                hbox:
                    spacing 20
                    $ av = store.spa_get_available(selected)
                    $ sp = store.spa_get_spent(selected)
                    $ rm = store.spa_get_remaining(selected)
                    text "Disponible: [av]" size 19
                    text "Gastado: [sp]" size 19
                    text "Restante: [rm]" size 19 color ("#66DD66" if rm >= 0 else "#FF6666")

                hbox:
                    spacing 10
                    text _("Paso:") size 18
                    textbutton "10" action Function(store.spa_ui_set_step, 10)
                    textbutton "50" action Function(store.spa_ui_set_step, 50)
                    textbutton "100" action Function(store.spa_ui_set_step, 100)
                    text "Actual: [store.spa_editor_step]" size 17 color "#AAAAAA"

                hbox:
                    spacing 12
                    textbutton _("Reset slot") action Function(store.spa_reset_slot, selected, True)
                    textbutton _("Reset TODO") action [
                        Function(store.spa_reset_all, True),
                        SetVariable("spa_editor_selected_unit_key", "player:0")
                    ]

                null height 8

                for tech_id in store.spa_ui_tech_ids_v1():
                    $ lbl = store.spa_ui_tech_label(tech_id)
                    $ base = store.spa_get_base_value(tech_id)
                    $ bonus = store.spa_get_bonus(selected, tech_id)
                    $ total = store.spa_get_final_value(selected, tech_id)
                    $ c = store.reiatsu_energy_dynamic_cost(tech_id, store, unit_key=selected)
                    $ rei = int(c.get("reiatsu_cost", 0) or 0)
                    $ ene = int(c.get("energy_cost", 0) or 0)

                    frame:
                        has vbox
                        spacing 6

                        hbox:
                            spacing 14
                            text "[lbl]" size 20
                            text "Base [base]" size 16 color "#AAAAAA"
                            text "Bonus [bonus]" size 16 color "#66CCFF"
                            text "Total [total]" size 16 color "#FFFFFF"
                            text "R [rei]" size 16 color "#C586C0"
                            text "E [ene]" size 16 color "#80CBC4"

                        hbox:
                            spacing 8
                            textbutton "-100" action Function(store.spa_ui_apply_delta, selected, tech_id, -100)
                            textbutton "-50" action Function(store.spa_ui_apply_delta, selected, tech_id, -50)
                            textbutton "-10" action Function(store.spa_ui_apply_delta, selected, tech_id, -10)
                            textbutton "+10" action Function(store.spa_ui_apply_delta, selected, tech_id, 10)
                            textbutton "+50" action Function(store.spa_ui_apply_delta, selected, tech_id, 50)
                            textbutton "+100" action Function(store.spa_ui_apply_delta, selected, tech_id, 100)
                            textbutton "+Paso" action Function(store.spa_ui_apply_delta, selected, tech_id, int(getattr(store, "spa_editor_step", 100) or 100))
                            textbutton "Reset técnica" action Function(store.spa_set_bonus, selected, tech_id, 0, True)
