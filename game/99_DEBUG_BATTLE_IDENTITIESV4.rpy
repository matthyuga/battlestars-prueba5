# ===========================================================
# 99_DEBUG_BATTLE_IDENTITIES.RPY – Panel de depuración de identidades
# ===========================================================
# Versión: v2.1 ReflectManager PendingCharge View ✅ (Ren’Py 7.4.9)
# -----------------------------------------------------------
# - Tecla “T” alterna visibilidad del panel
# - Lee IDs SIEMPRE desde renpy.store (evita desync globals)
# - ✅ REFLECT (paradigma nuevo):
#     Muestra reflect PENDIENTE por identidad (se cobra en su próximo turno ofensivo)
#     - Actor = current_actor_id
#     - Enemigo = current_enemy_id
# - Fallback legacy: reflected_buffer / enemy_reflect_buffer si no existe S.reflect
# - Muestra Concentrar/Potenciar (mult total)
# - Detecta si hay Focus/Boost en cola y muestra la técnica OBJETIVO
# ===========================================================

init -990 python:
    import renpy.store as S

    if not hasattr(S, "debug_identity_panel"):
        S.debug_identity_panel = False

    config.keymap['toggle_identity_panel'] = ['K_t']

    def toggle_debug_identity():
        import renpy.exports as renpy_exports
        S.debug_identity_panel = not getattr(S, "debug_identity_panel", False)
        renpy_exports.restart_interaction()


screen debug_battle_identity():

    key "toggle_identity_panel" action Function(toggle_debug_identity)

    if renpy.store.debug_identity_panel:

        frame:
            align (0.5, 0.05)
            xpadding 20
            ypadding 12
            background "#000C"
            xmaximum 620
            at debug_fade

            vbox:
                spacing 4
                xalign 0.5

                text "🧩 Debug Identidades de Batalla" size 22 color "#00FFFF" xalign 0.5

                # -------------------------------------------------
                # IDs (store)
                # -------------------------------------------------
                $ aid = getattr(renpy.store, "current_actor_id", None)
                $ eid = getattr(renpy.store, "current_enemy_id", None)

                text "Actor: {}".format(aid or "None") color "#CCCCCC" size 16 xalign 0.5
                text "Enemigo: {}".format(eid or "None") color "#CCCCCC" size 16 xalign 0.5
                null height 8

                # -------------------------------------------------
                # REFLECT PENDIENTE (nuevo + fallback legacy)
                # Paradigma: se cobra en el PRÓXIMO TURNO OFENSIVO de esa identidad
                # -------------------------------------------------
                $ rman = getattr(renpy.store, "reflect", None)

                # defaults
                $ a_val = 0
                $ a_src = None
                $ e_val = 0
                $ e_src = None

                if rman and (aid or eid):
                    python:
                        import renpy.store as S
                        # Actor
                        try:
                            if aid:
                                a_val = int(rman.get(aid) or 0)
                                a_src = rman.get_source(aid)
                            else:
                                a_val = 0
                                a_src = None
                        except:
                            a_val = 0
                            a_src = None

                        # Enemigo
                        try:
                            if eid:
                                e_val = int(rman.get(eid) or 0)
                                e_src = rman.get_source(eid)
                            else:
                                e_val = 0
                                e_src = None
                        except:
                            e_val = 0
                            e_src = None
                else:
                    # fallback legacy (por si ReflectManager no está cargado)
                    $ p_buf = getattr(renpy.store, "reflected_buffer", None)
                    $ e_buf = getattr(renpy.store, "enemy_reflect_buffer", None)

                    # legacy: asumimos que reflected_buffer pertenece al jugador/actor
                    $ a_val = p_buf.value if p_buf else 0
                    $ a_src = p_buf.source_id if p_buf else None

                    $ e_val = e_buf.value if e_buf else 0
                    $ e_src = e_buf.source_id if e_buf else None

                text "Reflejo Actor (pendiente): {}".format(a_val) color "#00BFFF" size 15 xalign 0.5
                text "→ Fuente: {}".format(a_src or "None") color "#88CCFF" size 13 xalign 0.5

                text "Reflejo Enemigo (pendiente): {}".format(e_val) color "#FF6666" size 15 xalign 0.5
                text "→ Fuente: {}".format(e_src or "None") color "#FFAAAA" size 13 xalign 0.5

                null height 6
                text "Nota: el reflect pendiente se cobra al INICIO del turno ofensivo de esa identidad." color "#AAAAAA" size 12 xalign 0.5
                null height 6

                # -------------------------------------------------
                # CONCENTRAR / POTENCIAR (estado store)
                # -------------------------------------------------
                $ fcur = int(getattr(renpy.store, "focus_off_current_mult", 1) or 1)
                $ fst  = int(getattr(renpy.store, "focus_off_stored_mult", 1)  or 1)
                $ bcur = int(getattr(renpy.store, "boost_def_current_mult", 1) or 1)
                $ bst  = int(getattr(renpy.store, "boost_def_stored_mult", 1)  or 1)

                $ f_total = fcur * fst
                $ b_total = bcur * bst

                text "Concentrar (store): x{}".format(f_total) color "#C586C0" size 15 xalign 0.5
                text "Potenciar  (store): x{}".format(b_total) color "#55FFFF" size 15 xalign 0.5

                # -------------------------------------------------
                # Focus/Boost en COLA + objetivo afectado
                # -------------------------------------------------
                $ q = list(getattr(renpy.store, "player_action_queue", []))
                $ mode = getattr(renpy.store, "battle_mode", "offensive")

                $ has_focus = ("Concentrar x2" in q) or ("Concentrar" in q)
                $ has_boost = ("Potenciar" in q)

                $ target_name = None
                python:
                    try:
                        idx = selector_find_focus_target_index(q, mode)
                        if idx is not None and idx >= 0 and idx < len(q):
                            target_name = q[idx]
                    except:
                        target_name = None

                null height 6
                text "Modo selector: {}".format(mode) color "#DDDDDD" size 14 xalign 0.5
                text "Cola: {}".format(" | ".join(q) if q else "—") color "#AAAAAA" size 13 xalign 0.5

                if mode == "offensive":
                    text "Focus en cola: {}".format("Sí" if has_focus else "No") color "#C586C0" size 14 xalign 0.5
                else:
                    text "Boost en cola: {}".format("Sí" if has_boost else "No") color "#55FFFF" size 14 xalign 0.5

                text "🎯 Objetivo: {}".format(target_name or "—") color "#FFD35A" size 15 xalign 0.5

                $ f_cost = getattr(renpy.store, "focus_cost_active", False)
                text "FocusCostFlag: {}".format("ON" if f_cost else "OFF") color "#888888" size 13 xalign 0.5

                null height 8
                text "(Pulsa 'T' para ocultar/mostrar)" color "#888888" size 13 xalign 0.5


transform debug_fade:
    alpha 0.0
    linear 0.3 alpha 1.0
