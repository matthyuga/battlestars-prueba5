# ===========================================================
# 06B1_BATTLE_FX_CORE.RPY – Núcleo lógico de efectos visuales
# v1.02 NoRedFlash Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# Elimina el flash rojo de daño crítico, pero mantiene vibraciones
# y demás efectos activos.
# ===========================================================

init -969 python:
    import time
    import renpy.store as S

    battle_floating_texts = []
    battle_hit_feedback_events = []
    battle_hit_feedback_result_events = []

    if not hasattr(S, "bs_battle_hit_feedback_enabled"):
        S.bs_battle_hit_feedback_enabled = True
    if not hasattr(S, "bs_battle_legacy_damage_popups_enabled"):
        S.bs_battle_legacy_damage_popups_enabled = False
    if not hasattr(S, "bs_battle_fx_speed_mode"):
        S.bs_battle_fx_speed_mode = "normal"
    if not hasattr(S, "battle_hit_feedback_history"):
        S.battle_hit_feedback_history = []
    if not hasattr(S, "battle_hit_feedback_combo_segments"):
        S.battle_hit_feedback_combo_segments = []

    def bs_battle_hit_feedback_grade(hit_count=1):
        try:
            n = int(hit_count or 0)
        except:
            n = 0
        if n >= 6:
            return "SS"
        if n >= 4:
            return "S"
        if n >= 3:
            return "A"
        if n >= 2:
            return "B"
        return "C"

    def bs_battle_hit_feedback_archive_segment(target="", reason="reset"):
        try:
            count = int(getattr(S, "battle_hit_feedback_combo_count", 0) or 0)
        except:
            count = 0
        if count <= 0:
            return None

        target_s = str(target or getattr(S, "battle_hit_feedback_last_target", "") or "")
        entry = {
            "target": target_s,
            "hits": int(count),
            "grade": bs_battle_hit_feedback_grade(count),
            "reason": str(reason or "reset"),
            "ts": float(time.time()),
        }
        segments = list(getattr(S, "battle_hit_feedback_combo_segments", []) or [])
        segments.append(entry)
        S.battle_hit_feedback_combo_segments = segments[-80:]
        return entry

    def bs_battle_hit_feedback_reset_combo(target="", reason="reset"):
        try:
            bs_battle_hit_feedback_archive_segment(target, reason)
        except:
            pass
        S.battle_hit_feedback_combo_count = 0
        if target:
            S.battle_hit_feedback_last_target = str(target)
        return True

    def bs_battle_hit_feedback_prune(max_age=1.35):
        now = time.time()
        try:
            kept = []
            for ev in list(getattr(S, "battle_hit_feedback_events", []) or []):
                try:
                    if now - float(ev.get("ts", now)) <= float(max_age):
                        kept.append(ev)
                except:
                    pass
            S.battle_hit_feedback_events = kept[-8:]
            globals()["battle_hit_feedback_events"] = S.battle_hit_feedback_events
        except:
            S.battle_hit_feedback_events = []
            globals()["battle_hit_feedback_events"] = S.battle_hit_feedback_events
        try:
            kept_results = []
            for ev in list(getattr(S, "battle_hit_feedback_result_events", []) or []):
                try:
                    if now - float(ev.get("ts", now)) <= float(max_age):
                        kept_results.append(ev)
                except:
                    pass
            S.battle_hit_feedback_result_events = kept_results[-6:]
            globals()["battle_hit_feedback_result_events"] = S.battle_hit_feedback_result_events
        except:
            S.battle_hit_feedback_result_events = []
            globals()["battle_hit_feedback_result_events"] = S.battle_hit_feedback_result_events
        try:
            return True
        except:
            pass

    def bs_battle_hit_feedback_visible_events(hit_ttl=1.25, result_ttl=1.35):
        now = time.time()

        hits = []
        for ev in list(getattr(S, "battle_hit_feedback_events", []) or []):
            try:
                if now - float(ev.get("ts", now)) <= float(hit_ttl):
                    hits.append(ev)
            except:
                pass

        results = []
        for ev in list(getattr(S, "battle_hit_feedback_result_events", []) or []):
            try:
                if now - float(ev.get("ts", now)) <= float(result_ttl):
                    results.append(ev)
            except:
                pass

        S.battle_hit_feedback_events = hits[-8:]
        S.battle_hit_feedback_result_events = results[-6:]
        globals()["battle_hit_feedback_events"] = S.battle_hit_feedback_events
        globals()["battle_hit_feedback_result_events"] = S.battle_hit_feedback_result_events
        return {
            "hits": hits[-6:],
            "results": results[-4:],
        }

    def bs_battle_enqueue_hit_feedback(target="enemy", value=0, color="#FF6666", hit_kind="normal", count_hit=True):
        if not bool(getattr(S, "bs_battle_hit_feedback_enabled", True)):
            return None

        target_s = "player" if str(target or "").strip().lower() == "player" else "enemy"
        now = time.time()

        try:
            bs_battle_hit_feedback_prune()
        except:
            pass

        try:
            last_ts = float(getattr(S, "battle_hit_feedback_last_ts", 0.0) or 0.0)
        except:
            last_ts = 0.0
        try:
            last_target = str(getattr(S, "battle_hit_feedback_last_target", "") or "")
        except:
            last_target = ""

        count_hit_b = bool(count_hit)

        if count_hit_b and ((now - last_ts) > 1.25 or last_target != target_s):
            S.battle_hit_feedback_combo_count = 0

        if count_hit_b:
            try:
                hit_count = int(getattr(S, "battle_hit_feedback_combo_count", 0) or 0) + 1
            except:
                hit_count = 1
            S.battle_hit_feedback_combo_count = int(hit_count)
            S.battle_hit_feedback_last_ts = float(now)
            S.battle_hit_feedback_last_target = str(target_s)
        else:
            try:
                hit_count = max(1, int(getattr(S, "battle_hit_feedback_combo_count", 1) or 1))
            except:
                hit_count = 1

        kind_s = str(hit_kind or "normal")

        entry = {
            "target": target_s,
            "value": max(0, int(value or 0)),
            "color": str(color or ("#FF6666" if target_s == "enemy" else "#88CCFF")),
            "hit": int(hit_count),
            "grade": bs_battle_hit_feedback_grade(hit_count),
            "kind": kind_s,
            "count_hit": count_hit_b,
            "ts": float(now),
            "id": renpy.random.randint(100000, 999999),
        }

        if kind_s in ("final", "incoming"):
            events = list(getattr(S, "battle_hit_feedback_result_events", []) or [])
            events.append(entry)
            S.battle_hit_feedback_result_events = events[-6:]
            globals()["battle_hit_feedback_result_events"] = S.battle_hit_feedback_result_events
        else:
            events = list(getattr(S, "battle_hit_feedback_events", []) or [])
            events.append(entry)
            S.battle_hit_feedback_events = events[-8:]
            globals()["battle_hit_feedback_events"] = S.battle_hit_feedback_events
        history = list(getattr(S, "battle_hit_feedback_history", []) or [])
        history.append(entry)
        S.battle_hit_feedback_history = history[-240:]
        try:
            renpy.restart_interaction()
        except:
            pass
        return entry

    def bs_battle_enqueue_focus_break(target="enemy", label="CONCENTRAR"):
        target_s = "player" if str(target or "").strip().lower() == "player" else "enemy"
        try:
            bs_battle_hit_feedback_archive_segment(target_s, "focus")
        except:
            pass
        entry = bs_battle_enqueue_hit_feedback(target_s, 0, "#C586C0", "focus", count_hit=False)
        try:
            if isinstance(entry, dict):
                entry["label"] = str(label or "CONCENTRAR")
                events = list(getattr(S, "battle_hit_feedback_events", []) or [])
                if events:
                    events[-1] = entry
                    S.battle_hit_feedback_events = events[-8:]
                    globals()["battle_hit_feedback_events"] = S.battle_hit_feedback_events
                    history = list(getattr(S, "battle_hit_feedback_history", []) or [])
                    if history:
                        history[-1] = entry
                        S.battle_hit_feedback_history = history[-240:]
        except:
            pass
        S.battle_hit_feedback_combo_count = 0
        S.battle_hit_feedback_last_target = str(target_s)
        try:
            renpy.restart_interaction()
        except:
            pass
        return entry

    def bs_battle_visual_incoming(target="player", value=0, color="#FFAA44"):
        return bs_battle_enqueue_hit_feedback(target, int(value or 0), color, "incoming", count_hit=False)

    # -------------------------------------------------------
    # 🔹 Sacudida de cámara según tipo de golpe (SE MANTIENE)
    # -------------------------------------------------------
    def battle_shake_effect(fx_type="normal"):
        if fx_type == "critical":
            renpy.with_statement(vpunch)
            renpy.with_statement(hpunch)
        elif fx_type == "power":
            renpy.with_statement(vpunch)
        else:
            renpy.with_statement(hpunch)

    # -------------------------------------------------------
    # 🔹 Flash de impacto configurable
    # -------------------------------------------------------
    def fx_hit_red(damage=0, color="#FF6666", intensity=0.3, snake=True):
        try:
            if not snake:
                battle_light_glow(color, intensity)
                return
            fx_apply_combo(color, intensity, snake=True, final_value=None)
        except Exception as e:
            renpy.log("⚠️ fx_hit_red error: {}".format(e))

    # -------------------------------------------------------
    # 🔹 Daño flotante principal
    # -------------------------------------------------------
    def battle_visual_float(target="enemy", value=0, color=None, is_final=False):
        global battle_floating_texts
        if color is None:
            color = "#FF6666" if target == "enemy" else "#88CCFF"

        # Tipo de impacto
        fx_type = "normal"
        if is_final:
            if value >= 7000: fx_type = "critical"
            elif value >= 4000: fx_type = "power"

        if is_final:
            battle_shake_effect(fx_type)

        entry = {
            "target": target,
            "value": value,
            "color": color,
            "type": fx_type,
            "id": renpy.random.randint(1000, 9999),
        }
        battle_floating_texts.append(entry)

        try:
            if int(value or 0) > 0:
                if bool(is_final):
                    bs_battle_enqueue_hit_feedback(target, int(value or 0), color, "final", count_hit=False)
                else:
                    bs_battle_enqueue_hit_feedback(target, int(value or 0), color, fx_type, count_hit=True)
        except:
            pass

        renpy.restart_interaction()

    # -------------------------------------------------------
    # 🔹 FX de luz, críticos y cinematic (sin flash rojo)
    # -------------------------------------------------------
    def battle_light_glow(color="#FFFFFF", intensity=0.4, duration=0.4):
        renpy.show_screen("battle_light_glow",
                          glow_color=color,
                          glow_alpha=intensity,
                          glow_time=duration)

    def battle_visual_focus_effect():
        battle_light_glow("#00BFFF", 0.4)
        renpy.show_screen("focus_particles")
        renpy.pause(0.35)
        renpy.hide_screen("focus_particles")
        try:
            battle_atmo_flash("lab")
        except:
            pass

    # 🔕 Esta función ya no muestra flash rojo
    def battle_visual_critical_flash(target="enemy"):
        return  # desactivado

    # 🔕 Quita el flash rojo, pero mantiene vibración
    def battle_cinematic_impact(target="enemy", damage=0):
        if damage < 3000:
            return
        # No llama a battle_visual_critical_flash()
        renpy.with_statement(vpunch)
        renpy.pause(0.25)

    def battle_visual_on_attack(target="enemy", damage=0):
        if target == "enemy":
            hp_max = float(battle_hp_enemy_max) or 1.0
        else:
            hp_max = float(battle_hp_player_max) or 1.0
        rel = float(damage) / hp_max

        if damage <= 0:
            battle_visual_focus_effect(); return
        if damage < 1000 and rel < 0.10:
            battle_light_glow("#CCCCCC", 0.25); return
        if damage < 3000 and rel < 0.30:
            battle_light_glow("#FFFFFF", 0.3); renpy.with_statement(hpunch); return
        if damage < 5000 and rel < 0.40:
            # 🔕 sin flash rojo
            renpy.with_statement(vpunch); return
        battle_cinematic_impact(target, damage)

    # -------------------------------------------------------
    # 🔹 Onda expansiva cinematográfica del combo final
    # -------------------------------------------------------
    def battle_combo_shockwave(color="#FFFFFF", intensity=0.4, duration=0.6):
        try:
            renpy.show_screen("battle_combo_shockwave",
                              wave_color=color,
                              wave_alpha=intensity,
                              wave_time=duration)
        except Exception as e:
            renpy.log("⚠️ battle_combo_shockwave error: {}".format(e))

    # -------------------------------------------------------
    # 🔹 Glitch cromático (ataques/defensas)
    # -------------------------------------------------------
    def battle_glitch_effect(color="#FF0000", duration=0.25):
        try:
            renpy.show_screen("battle_glitch_overlay",
                              glitch_color=color,
                              glitch_time=duration)
        except Exception as e:
            renpy.log("⚠️ battle_glitch_effect error: {}".format(e))

    S.battle_visual_float = battle_visual_float
    S.battle_visual_on_attack = battle_visual_on_attack
    S.battle_light_glow = battle_light_glow
    S.battle_glitch_effect = battle_glitch_effect
    S.fx_hit_red = fx_hit_red
    S.battle_hit_feedback_events = battle_hit_feedback_events
    S.battle_hit_feedback_result_events = battle_hit_feedback_result_events
    S.bs_battle_hit_feedback_grade = bs_battle_hit_feedback_grade
    S.bs_battle_hit_feedback_prune = bs_battle_hit_feedback_prune
    S.bs_battle_hit_feedback_visible_events = bs_battle_hit_feedback_visible_events
    S.bs_battle_enqueue_hit_feedback = bs_battle_enqueue_hit_feedback
    S.bs_battle_hit_feedback_archive_segment = bs_battle_hit_feedback_archive_segment
    S.bs_battle_hit_feedback_reset_combo = bs_battle_hit_feedback_reset_combo
    S.bs_battle_enqueue_focus_break = bs_battle_enqueue_focus_break
    S.bs_battle_visual_incoming = bs_battle_visual_incoming
