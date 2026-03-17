# ============================================================
# 04H_SLOT_POINTS_EDITOR_SCREENV1.rpy
# Fase D — Menú principal + editor v1 de puntos por slot
# ============================================================

# selección UI (persistente por sesión)
default spa_editor_selected_unit_key = "player:0"
default spa_editor_step = 100
default spa_editor_message = ""
default spa_editor_message_color = "#AAAAAA"
default spa_editor_profile_id = "A"

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

    def spa_ui_pool_label(pool_key):
        pk = str(pool_key or "").strip().lower()
        if pk == "reiatsu":
            return "Reiatsu"
        if pk == "energy":
            return "Energía"
        if pk == "hp":
            return "HP"
        return str(pool_key or "")

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
        return None

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


    def spa_ui_set_message(msg, color="#AAAAAA"):
        S.spa_editor_message = str(msg or "")
        S.spa_editor_message_color = str(color or "#AAAAAA")
        try:
            import renpy
            renpy.notify(S.spa_editor_message)
        except:
            pass
        try:
            fn = getattr(S, "debug_log", None)
            if callable(fn):
                fn("[SPA_UI] " + S.spa_editor_message)
        except:
            pass

    def spa_ui_apply_delta_feedback(unit_key, tech_id, delta):
        r = spa_ui_apply_delta(unit_key, tech_id, delta)
        ok = bool(isinstance(r, dict) and r.get("ok", False))
        if ok:
            try:
                b = int(getattr(S, "spa_get_bonus", lambda a,b: 0)(unit_key, tech_id) or 0)
            except:
                b = 0
            spa_ui_set_message("{}: bonus = {}".format(spa_ui_tech_label(tech_id), b), "#66DD66")
            return None

        reason = "error"
        if isinstance(r, dict):
            reason = str(r.get("reason", "error") or "error")

        if reason == "over_budget":
            spa_ui_set_message("No alcanza presupuesto del slot.", "#FF8888")
        elif reason == "invalid_tech":
            spa_ui_set_message("Técnica inválida o no editable.", "#FF8888")
        elif reason == "allocator_missing":
            spa_ui_set_message("Allocator no disponible.", "#FF8888")
        else:
            spa_ui_set_message("No se pudo aplicar el cambio ({}).".format(reason), "#FF8888")
        return None

    def spa_ui_reset_tech_feedback(unit_key, tech_id):
        fn = getattr(S, "spa_set_bonus", None)
        if not callable(fn):
            spa_ui_set_message("Allocator no disponible.", "#FF8888")
            return None
        r = fn(unit_key, tech_id, 0, True)
        if isinstance(r, dict) and r.get("ok", False):
            spa_ui_set_message("{}: bonus reseteado".format(spa_ui_tech_label(tech_id)), "#66DD66")
            return None
        spa_ui_set_message("No se pudo resetear técnica.", "#FF8888")
        return None

    def spa_ui_reset_slot_feedback(unit_key):
        fn = getattr(S, "spa_reset_slot", None)
        if not callable(fn):
            spa_ui_set_message("Allocator no disponible.", "#FF8888")
            return None
        fn(unit_key, True)
        spa_ui_set_message("Slot {} reseteado.".format(spa_ui_unit_label(unit_key)), "#66DD66")
        return None

    def spa_ui_reset_all_feedback():
        fn = getattr(S, "spa_reset_all", None)
        if not callable(fn):
            spa_ui_set_message("Allocator no disponible.", "#FF8888")
            return None
        fn(True)
        S.spa_editor_selected_unit_key = "player:0"
        spa_ui_set_message("Todos los slots fueron reseteados.", "#66DD66")
        return None


    def spa_ui_add_available_feedback(unit_key, amount=1000):
        fn = getattr(S, "spa_add_available", None)
        if not callable(fn):
            spa_ui_set_message("No se pudo agregar disponible.", "#FF8888")
            return None
        fn(unit_key, int(amount or 0), save=True)
        spa_ui_set_message("Disponible +{} para {}".format(int(amount or 0), spa_ui_unit_label(unit_key)), "#66DD66")
        return None

    def spa_ui_reset_available_feedback(unit_key):
        fn = getattr(S, "spa_reset_available_base", None)
        if not callable(fn):
            spa_ui_set_message("No se pudo resetear disponible.", "#FF8888")
            return None
        slot = fn(unit_key, save=True)
        base = int(slot.get("available", 2000) if isinstance(slot, dict) else 2000)
        spa_ui_set_message("Disponible de {} reseteado a {}".format(spa_ui_unit_label(unit_key), base), "#66DD66")
        return None

    def spa_ui_add_pool_feedback(unit_key, pool_key, amount):
        fn = getattr(S, "spa_add_pool_bonus", None)
        if not callable(fn):
            spa_ui_set_message("No se pudo agregar {}.".format(spa_ui_pool_label(pool_key)), "#FF8888")
            return None
        r = fn(unit_key, pool_key, int(amount or 0), save=True)
        if isinstance(r, dict) and r.get("ok", False):
            val = int(getattr(S, "spa_get_pool_bonus", lambda a,b: 0)(unit_key, pool_key) or 0)
            spa_ui_set_message("{} +{} para {} (bonus={})".format(spa_ui_pool_label(pool_key), int(amount or 0), spa_ui_unit_label(unit_key), val), "#66DD66")
            return None
        spa_ui_set_message("No se pudo agregar {}.".format(spa_ui_pool_label(pool_key)), "#FF8888")
        return None

    def spa_ui_reset_pool_feedback(unit_key, pool_key):
        fn = getattr(S, "spa_reset_pool_bonus", None)
        if not callable(fn):
            spa_ui_set_message("No se pudo resetear {}.".format(spa_ui_pool_label(pool_key)), "#FF8888")
            return None
        r = fn(unit_key, pool_key, save=True)
        if isinstance(r, dict) and r.get("ok", False):
            spa_ui_set_message("{} reseteado para {}".format(spa_ui_pool_label(pool_key), spa_ui_unit_label(unit_key)), "#66DD66")
            return None
        spa_ui_set_message("No se pudo resetear {}.".format(spa_ui_pool_label(pool_key)), "#FF8888")
        return None

    def spa_ui_save_profile_feedback(profile_id):
        fn = getattr(S, "spa_save_profile", None)
        if not callable(fn):
            spa_ui_set_message("Guardado de perfil no disponible.", "#FF8888")
            return None
        ok = bool(fn(profile_id))
        if ok:
            spa_ui_set_message("Configuración guardada en perfil {}".format(str(profile_id)), "#66DD66")
        else:
            spa_ui_set_message("No se pudo guardar perfil {}".format(str(profile_id)), "#FF8888")
        return None

    def spa_ui_load_profile_feedback(profile_id):
        fn = getattr(S, "spa_load_profile", None)
        if not callable(fn):
            spa_ui_set_message("Carga de perfil no disponible.", "#FF8888")
            return None
        ok = bool(fn(profile_id))
        if ok:
            spa_ui_set_message("Perfil {} cargado".format(str(profile_id)), "#66DD66")
        else:
            spa_ui_set_message("No existe perfil {} guardado".format(str(profile_id)), "#FF8888")
        return None

screen slot_points_editor():
    tag menu

    use game_menu(_("Editor de puntos por slot"), scroll="viewport"):

        vbox:
            spacing 18

            label _("Configuración persistente de bonus por técnica")
            text _("Editas bonus por slot para técnicas, recursos y HP. Todo queda persistente por perfil.") size 18
            text "[store.spa_editor_message]" size 16 color getattr(store, "spa_editor_message_color", "#AAAAAA")

            $ allocator_ok = callable(getattr(store, "spa_ensure_state", None))

            if not allocator_ok:
                text _("Allocator no disponible. Verifica que 04Y_SLOT_POINT_ALLOCATOR_V1.rpy esté cargado.") color "#FF8888"
            else:
                $ _spa_state = store.spa_ensure_state()
                $ selected = getattr(store, "spa_editor_selected_unit_key", "player:0") or "player:0"

                hbox:
                    spacing 10
                    text _("Perfil:") size 18
                    for pid in ("A", "B", "C"):
                        textbutton "[pid]":
                            action SetVariable("spa_editor_profile_id", pid)
                            text_color ("#66CCFF" if pid == getattr(store, "spa_editor_profile_id", "A") else "#FFFFFF")
                    textbutton _("Guardar configuración") action Function(store.spa_ui_save_profile_feedback, getattr(store, "spa_editor_profile_id", "A"))
                    textbutton _("Cargar configuración") action Function(store.spa_ui_load_profile_feedback, getattr(store, "spa_editor_profile_id", "A"))

                hbox:
                    spacing 10
                    text _("Slot:") size 20
                    for uk in store.spa_ui_unit_keys_v1():
                        $ uk_label = store.spa_ui_unit_label(uk)
                        textbutton "[uk_label]":
                            action SetVariable("spa_editor_selected_unit_key", uk)
                            text_color ("#66CCFF" if uk == selected else "#FFFFFF")

                hbox:
                    spacing 20
                    $ av = store.spa_get_available(selected)
                    $ sp = store.spa_get_spent(selected)
                    $ rm = store.spa_get_remaining(selected)
                    text "Disponible: [av]" size 19
                    text "Gastado: [sp]" size 19
                    text "Restante: [rm]" size 19 color ("#66DD66" if rm >= 0 else "#FF6666")
                    textbutton "+1000 disp" action Function(store.spa_ui_add_available_feedback, selected, 1000)
                    textbutton "Reset disp" action Function(store.spa_ui_reset_available_feedback, selected)

                hbox:
                    spacing 10
                    text _("Paso:") size 18
                    textbutton "10" action Function(store.spa_ui_set_step, 10)
                    textbutton "50" action Function(store.spa_ui_set_step, 50)
                    textbutton "100" action Function(store.spa_ui_set_step, 100)
                    text "Actual: [store.spa_editor_step]" size 17 color "#AAAAAA"

                hbox:
                    spacing 12
                    textbutton _("Reset slot") action Function(store.spa_ui_reset_slot_feedback, selected)
                    textbutton _("Reset TODO") action Confirm(_("¿Resetear TODOS los slots?"), yes=Function(store.spa_ui_reset_all_feedback))

                frame:
                    has vbox
                    spacing 6

                    text "Puntos de recursos" size 20 color "#C586C0"

                    hbox:
                        spacing 16
                        $ rei_bonus = int(store.spa_get_pool_bonus(selected, "reiatsu") if hasattr(store, "spa_get_pool_bonus") else 0)
                        $ ene_bonus = int(store.spa_get_pool_bonus(selected, "energy") if hasattr(store, "spa_get_pool_bonus") else 0)
                        text "Reiatsu bonus: [rei_bonus]" size 17
                        textbutton "+1000 Reiatsu" action Function(store.spa_ui_add_pool_feedback, selected, "reiatsu", 1000)
                        textbutton "Reset Reiatsu" action Function(store.spa_ui_reset_pool_feedback, selected, "reiatsu")

                    hbox:
                        spacing 16
                        text "Energía bonus: [ene_bonus]" size 17
                        textbutton "+100 Energía" action Function(store.spa_ui_add_pool_feedback, selected, "energy", 100)
                        textbutton "Reset Energía" action Function(store.spa_ui_reset_pool_feedback, selected, "energy")

                frame:
                    has vbox
                    spacing 6

                    text "Puntos de salud" size 20 color "#80CBC4"
                    hbox:
                        spacing 16
                        $ hp_bonus_local = int(store.spa_get_pool_bonus(selected, "hp") if hasattr(store, "spa_get_pool_bonus") else 0)
                        text "HP bonus: [hp_bonus_local]" size 17
                        textbutton "+1000 HP" action Function(store.spa_ui_add_pool_feedback, selected, "hp", 1000)
                        textbutton "Reset HP" action Function(store.spa_ui_reset_pool_feedback, selected, "hp")

                frame:
                    has vbox
                    spacing 6

                    text "Puntos de hierro" size 20 color "#6EC1FF"
                    hbox:
                        spacing 16
                        $ hierro_cover_bonus = int(store.spa_get_pool_bonus(selected, "coating_cover") if hasattr(store, "spa_get_pool_bonus") else 0)
                        text "Cubre bonus: [hierro_cover_bonus]" size 17
                        textbutton "+100 Cubre" action Function(store.spa_ui_add_pool_feedback, selected, "coating_cover", 100)
                        textbutton "Reset Cubre" action Function(store.spa_ui_reset_pool_feedback, selected, "coating_cover")

                    hbox:
                        spacing 16
                        $ hierro_dura_bonus = int(store.spa_get_pool_bonus(selected, "coating_durability") if hasattr(store, "spa_get_pool_bonus") else 0)
                        text "Durabilidad bonus: [hierro_dura_bonus]" size 17
                        textbutton "+1000 Durabilidad" action Function(store.spa_ui_add_pool_feedback, selected, "coating_durability", 1000)
                        textbutton "Reset Durabilidad" action Function(store.spa_ui_reset_pool_feedback, selected, "coating_durability")

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
                            textbutton "-100" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, -100)
                            textbutton "-50" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, -50)
                            textbutton "-10" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, -10)
                            textbutton "+10" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, 10)
                            textbutton "+50" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, 50)
                            textbutton "+100" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, 100)
                            textbutton "+Paso" action Function(store.spa_ui_apply_delta_feedback, selected, tech_id, int(getattr(store, "spa_editor_step", 100) or 100))
                            textbutton "Reset técnica" action Function(store.spa_ui_reset_tech_feedback, selected, tech_id)
