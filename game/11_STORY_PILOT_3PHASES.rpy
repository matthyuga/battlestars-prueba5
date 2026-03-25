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
    call screen rpg_panel_v1

    "Harribel" "Perfecto. Ya tienes una configuración inicial."
    jump story_phaseC_battle_bridge


label story_phaseC_battle_bridge:
    $ import renpy.store as S
    "Harribel" "Ahora enfréntate al Hollow."
    "Harribel" "Concéntrate: observa tus recursos y no desperdicies energía."

    $ S.battle_team_mode = "1v1"
    $ S.battle_player_id = "Harribel"
    $ S.battle_enemy_id = "Hollow"

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
    $ renpy.full_restart()
    return
