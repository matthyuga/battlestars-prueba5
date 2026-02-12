# ===========================================================
# 06B1_BATTLE_FX_CORE.RPY – Núcleo lógico de efectos visuales
# v1.02 NoRedFlash Edition (Ren’Py 7.4.9)
# -----------------------------------------------------------
# Elimina el flash rojo de daño crítico, pero mantiene vibraciones
# y demás efectos activos.
# ===========================================================

init -969 python:
    battle_floating_texts = []

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
