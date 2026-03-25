# ===========================================================
# 11_STORY_PILOT_3PHASES.rpy
# Piloto narrativo en 3 fases:
# A) Intro historia
# B) Asignación RPG guiada
# C) Combate 1v1 + post-combate
# ===========================================================

init -100 python:
    import renpy.store as S

    def story_pilot_prepare_level1_panel():
        # Seed nivel 1 + 1 punto de stat para tutorial.
        st = rpgp_open_panel("new_player")
        st.setdefault("pending", {})["stat_points"] = 1
        S.rpg_panel_state_v1 = compute_preview(st)
        S.rpg_panel_baseline_v1 = S.rpg_panel_state_v1
        return S.rpg_panel_state_v1

    def story_pilot_is_panel_ready(st):
        if not isinstance(st, dict):
            return False
        principal = st.get("principal", {}) if isinstance(st.get("principal", {}), dict) else {}
        selected = principal.get("selected", None)
        if selected not in RPGP_MAIN_STATS:
            return False

        if int(principal.get("distribution_total", 0) or 0) != 100:
            return False

        if int(principal.get("active_slots", 0) or 0) > 4:
            return False

        pending = st.get("pending", {}) if isinstance(st.get("pending", {}), dict) else {}
        if int(pending.get("stat_points", 0) or 0) != 0:
            return False

        stats = st.get("stats", {}) if isinstance(st.get("stats", {}), dict) else {}
        main_spent = 0
        for k in RPGP_MAIN_STATS:
            main_spent += int(stats.get(k, 0) or 0)
        if main_spent < 1:
            return False

        pool = st.get("pool", {}) if isinstance(st.get("pool", {}), dict) else {}
        spent_pool = int(pool.get("offensive_spent", 0) or 0) + int(pool.get("defensive_spent", 0) or 0)
        if spent_pool <= 0:
            return False

        val = st.get("validation", {}) if isinstance(st.get("validation", {}), dict) else {}
        return bool(val.get("is_valid", False))


label story_phaseA_intro:
    $ import renpy.store as S
    $ S.story_mode_active = True
    $ S.story_pilot_last_result = "unknown"

    scene fondo3 with fade
    "Un eco extraño cruza el aire..."
    "Sientes que este mundo no te reconoce todavía."

    $ _name = renpy.input("¿Cómo te llamas?", length=24)
    if _name is None or _name.strip() == "":
        $ _name = "forastero"
    $ S.story_player_name = _name.strip()

    "[S.story_player_name], una presencia enmascarada te observa a la distancia."
    "Creador" "Bienvenido. Aquí no sobrevives por fuerza bruta, sobrevives aprendiendo."
    "Creador" "Sigue mis indicaciones y busca a Harribel en el desierto."

    scene black with dissolve
    "Una luz te envuelve y el suelo desaparece bajo tus pies..."
    scene fondo3 with fade

    show expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png" at truecenter
    "Harribel" "Así que tú eres [S.story_player_name]. Camina conmigo."
    "Harribel" "Si quieres vivir en Hueco Mundo, debes aprender a combatir con cabeza."

    menu:
        "Responder a Harribel"
        "Estoy listo para aprender.":
            "Harribel" "Bien. Un Hollow viene hacia nosotros. Lo usarás para entrenar."

    hide expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png"
    jump story_phaseB_training_panel


label story_phaseB_training_panel:
    $ import renpy.store as S
    "Harribel" "Fase B: define tu base de combate."
    "Harribel" "1) Elige atributo principal y distribúyelo."
    "Harribel" "2) Asigna 1 punto de stat."
    "Harribel" "3) Reparte el pool técnico general de 200 entre ofensivo y defensivo."

    $ story_pilot_prepare_level1_panel()

    label story_phaseB_training_panel_loop:
        call screen rpg_panel_v1
        $ _st = rpg_panel_state_v1 if isinstance(rpg_panel_state_v1, dict) else {}
        if not story_pilot_is_panel_ready(_st):
            "Harribel" "Aún no. Debes cumplir todo:"
            "Harribel" "• Principal elegido."
            "Harribel" "• Distribución 100 por ciento en hasta 4 parámetros."
            "Harribel" "• Gastar tu 1 punto de stat."
            "Harribel" "• Asignar puntos al pool técnico."
            jump story_phaseB_training_panel_loop

    "Harribel" "Perfecto. Ya tienes una configuración inicial válida."
    jump story_phaseC_battle_bridge


label story_phaseC_battle_bridge:
    $ import renpy.store as S
    "Harribel" "Ahora enfréntate al Hollow."
    "Harribel" "Concéntrate: observa tus recursos y no desperdicies energía."

    $ S.battle_team_mode = "1v1"
    $ S.battle_player_id = "Harribel"
    $ S.battle_enemy_id = "Hollow"
    $ S.story_pilot_allowed_offensive = ["stronger_attack", "direct_attack", "focus_attack"]
    $ S.story_pilot_allowed_defensive = ["defense_strong_block"]
    $ S.story_pilot_resource_override = {
        "player_reiatsu": 1200,
        "player_energy": 120,
        "enemy_reiatsu": 950,
        "enemy_energy": 90,
    }

    jump battle_start


label story_phaseC_postbattle:
    $ import renpy.store as S

    scene fondo3 with fade
    show expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png" at truecenter

    if S.story_pilot_last_result == "victory":
        "Harribel" "Buen trabajo, [S.story_player_name]. Ganaste tu primera lección."
        "Harribel" "No fue suerte. Fue control."
    elif S.story_pilot_last_result == "defeat":
        "Harribel" "Perdiste... y Hueco Mundo no perdona la debilidad."
        "Harribel" "Levántate sola o quédate atrás."
    else:
        "Harribel" "No hay victoria clara, pero aprendiste a sobrevivir un poco más."

    "Harribel" "Fin de la prueba piloto. La próxima vez, no te sostendré la mano."

    hide expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png"
    $ S.story_mode_active = False
    $ S.story_pilot_allowed_offensive = []
    $ S.story_pilot_allowed_defensive = []
    $ S.story_pilot_resource_override = {}
    $ renpy.full_restart()
    return
