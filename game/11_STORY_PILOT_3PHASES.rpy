# ===========================================================
# 11_STORY_PILOT_3PHASES.rpy
# Piloto narrativo en 3 bloques:
# 1) Tutorial fundamentos
# 2) Configuración guiada (paneles secuenciales)
# 3) Duelo 1v1 + post-combate
# ===========================================================

init -100 python:
    import copy
    import renpy.store as S

    STORY_ATTRS = ("fuerza", "agilidad", "resistencia", "inteligencia", "espiritu")
    STORY_PARAMS = ("ataque", "defensa", "hp", "energia", "reiatsu")
    STORY_PRINCIPAL_OFF_BASE = 100
    STORY_PRINCIPAL_DEF_BASE = 100

    def story_reset_cfg():
        S.story_cfg = {
            "principal": None,
            "stats": {"fuerza": 0, "agilidad": 0, "resistencia": 0, "inteligencia": 0, "espiritu": 0},
            "pending_stat": 1,
            "distribution": {"ataque": 0, "defensa": 0, "hp": 0, "energia": 0, "reiatsu": 0},
            "pool_general_total": 200,
            "pool_general_off": 0,
            "pool_general_def": 0,
            # Regla: el pool ofensivo específico principal tiene base fija.
            "pool_principal_off": STORY_PRINCIPAL_OFF_BASE,
            "pool_principal_def": STORY_PRINCIPAL_DEF_BASE,
            "pool_principal_off_spent": 0,
            "pool_principal_def_spent": 0,
            "tech_points": {
                "stronger_attack": 0,
                "direct_attack": 0,
                "defense_strong_block": 0,
            },
            "repertoire": [],
            "sealed": False,
        }

    def story_cfg_get():
        cfg = getattr(S, "story_cfg", None)
        if not isinstance(cfg, dict):
            story_reset_cfg()
            cfg = S.story_cfg
        return cfg

    def story_set_principal(attr):
        cfg = story_cfg_get()
        if attr in STORY_ATTRS:
            cfg["principal"] = attr
            # Mantener el ataque específico principal con base fija.
            cfg["pool_principal_off"] = STORY_PRINCIPAL_OFF_BASE
            cfg["pool_principal_def"] = STORY_PRINCIPAL_DEF_BASE
            cfg["pool_principal_off_spent"] = min(
                int(cfg.get("pool_principal_off_spent", 0) or 0),
                int(cfg.get("pool_principal_off", STORY_PRINCIPAL_OFF_BASE) or STORY_PRINCIPAL_OFF_BASE),
            )
            cfg["pool_principal_def_spent"] = min(
                int(cfg.get("pool_principal_def_spent", 0) or 0),
                int(cfg.get("pool_principal_def", STORY_PRINCIPAL_DEF_BASE) or STORY_PRINCIPAL_DEF_BASE),
            )
            cfg["sealed"] = False

    def story_add_stat(attr, delta):
        cfg = story_cfg_get()
        principal = cfg.get("principal", None)
        if attr != principal:
            return
        dd = int(delta or 0)
        if dd > 0 and int(cfg.get("pending_stat", 0)) <= 0:
            return
        cur = int(cfg["stats"].get(attr, 0) or 0)
        nxt = max(0, cur + dd)
        used_delta = nxt - cur
        cfg["stats"][attr] = nxt
        cfg["pending_stat"] = max(0, int(cfg.get("pending_stat", 0)) - used_delta)
        cfg["sealed"] = False

    def story_set_distribution(param, value):
        cfg = story_cfg_get()
        if param not in STORY_PARAMS:
            return
        vv = int(value or 0)
        if vv not in (0, 25, 50, 75, 100):
            return
        cfg["distribution"][param] = vv

        # Ataque/Defensa específicos principales: base fija + distribución aplicada.
        cfg["pool_principal_off"] = STORY_PRINCIPAL_OFF_BASE + int(cfg["distribution"].get("ataque", 0) or 0)
        cfg["pool_principal_def"] = STORY_PRINCIPAL_DEF_BASE + int(cfg["distribution"].get("defensa", 0) or 0)

        cfg["pool_principal_off_spent"] = min(int(cfg.get("pool_principal_off_spent", 0) or 0), int(cfg["pool_principal_off"]))
        cfg["pool_principal_def_spent"] = min(int(cfg.get("pool_principal_def_spent", 0) or 0), int(cfg["pool_principal_def"]))
        cfg["sealed"] = False

    def story_distribution_total():
        cfg = story_cfg_get()
        return sum(int(cfg["distribution"].get(k, 0) or 0) for k in STORY_PARAMS)

    def story_distribution_active():
        cfg = story_cfg_get()
        return sum(1 for k in STORY_PARAMS if int(cfg["distribution"].get(k, 0) or 0) > 0)

    def story_add_pool(bucket, delta):
        cfg = story_cfg_get()
        dd = int(delta or 0)
        if bucket == "general_off":
            nxt = int(cfg.get("pool_general_off", 0) or 0) + dd
            nxt = max(0, nxt)
            gen_total = int(cfg.get("pool_general_total", 0) or 0)
            other = int(cfg.get("pool_general_def", 0) or 0)
            if nxt + other > gen_total:
                nxt = max(0, gen_total - other)
            cfg["pool_general_off"] = nxt
        elif bucket == "general_def":
            nxt = int(cfg.get("pool_general_def", 0) or 0) + dd
            nxt = max(0, nxt)
            gen_total = int(cfg.get("pool_general_total", 0) or 0)
            other = int(cfg.get("pool_general_off", 0) or 0)
            if nxt + other > gen_total:
                nxt = max(0, gen_total - other)
            cfg["pool_general_def"] = nxt
        elif bucket == "principal_off":
            nxt = int(cfg.get("pool_principal_off_spent", 0) or 0) + dd
            nxt = max(0, min(nxt, int(cfg.get("pool_principal_off", 0) or 0)))
            cfg["pool_principal_off_spent"] = nxt
        elif bucket == "principal_def":
            nxt = int(cfg.get("pool_principal_def_spent", 0) or 0) + dd
            nxt = max(0, min(nxt, int(cfg.get("pool_principal_def", 0) or 0)))
            cfg["pool_principal_def_spent"] = nxt
        cfg["sealed"] = False

    def story_toggle_tech(tech_key):
        cfg = story_cfg_get()
        rep = list(cfg.get("repertoire", []) or [])
        if tech_key in rep:
            rep.remove(tech_key)
        else:
            rep.append(tech_key)
        cfg["repertoire"] = rep
        cfg["sealed"] = False

    def story_off_budget():
        cfg = story_cfg_get()
        return int(cfg.get("pool_general_off", 0) or 0) + int(cfg.get("pool_principal_off_spent", 0) or 0)

    def story_def_budget():
        cfg = story_cfg_get()
        return int(cfg.get("pool_general_def", 0) or 0) + int(cfg.get("pool_principal_def_spent", 0) or 0)

    def story_off_spent():
        cfg = story_cfg_get()
        tp = cfg.get("tech_points", {}) if isinstance(cfg.get("tech_points", {}), dict) else {}
        return int(tp.get("stronger_attack", 0) or 0) + int(tp.get("direct_attack", 0) or 0)

    def story_def_spent():
        cfg = story_cfg_get()
        tp = cfg.get("tech_points", {}) if isinstance(cfg.get("tech_points", {}), dict) else {}
        return int(tp.get("defense_strong_block", 0) or 0)

    def story_add_tech_points(tech_key, delta):
        cfg = story_cfg_get()
        tp = cfg.get("tech_points", {}) if isinstance(cfg.get("tech_points", {}), dict) else {}
        if tech_key not in tp:
            return
        dd = int(delta or 0)
        cur = int(tp.get(tech_key, 0) or 0)
        nxt = max(0, cur + dd)

        if tech_key in ("stronger_attack", "direct_attack"):
            other = int(tp.get("direct_attack" if tech_key == "stronger_attack" else "stronger_attack", 0) or 0)
            cap = max(0, story_off_budget() - other)
            nxt = min(nxt, cap)
        elif tech_key == "defense_strong_block":
            cap = max(0, story_def_budget())
            nxt = min(nxt, cap)

        tp[tech_key] = nxt
        cfg["tech_points"] = tp
        cfg["sealed"] = False

    def story_preview_resources():
        st = story_build_preview_from_cfg()
        prev = st.get("preview", {}) if isinstance(st.get("preview", {}), dict) else {}
        return {
            "hp": int(prev.get("hp_after", 1000) or 1000),
            "reiatsu": int(prev.get("reiatsu_after", 1000) or 1000),
            "energia": int(prev.get("energia_after", 100) or 100),
        }

    def story_validate_cfg():
        cfg = story_cfg_get()
        errs = []

        principal = cfg.get("principal", None)
        if principal not in STORY_ATTRS:
            errs.append("Selecciona atributo principal.")

        if int(cfg.get("pending_stat", 0) or 0) != 0:
            errs.append("Debes gastar el punto de stat del tutorial.")

        total = story_distribution_total()
        active = story_distribution_active()
        if total != 100:
            errs.append("La distribución principal debe sumar 100.")
        if active > 4:
            errs.append("Máximo 4 parámetros activos en distribución principal.")

        spent_total = int(cfg.get("pool_general_off", 0) or 0) + int(cfg.get("pool_general_def", 0) or 0)
        if spent_total <= 0:
            errs.append("Asigna puntos del pool general a ataque o defensa.")

        rep = list(cfg.get("repertoire", []) or [])
        if len(rep) <= 0:
            errs.append("Añade al menos una técnica al repertorio.")
        if not any(k in rep for k in ("stronger_attack", "direct_attack")):
            errs.append("Debes incluir al menos una técnica ofensiva inicial.")
        if "defense_strong_block" not in rep:
            errs.append("Debes incluir Defensa fuerte en repertorio.")

        if story_off_spent() <= 0:
            errs.append("Asigna puntos de ataque a Ataque más fuerte o Ataque directo.")
        if story_def_spent() <= 0:
            errs.append("Asigna puntos defensivos a Defensa fuerte.")

        return errs

    def story_seal_configuration():
        cfg = story_cfg_get()
        errs = story_validate_cfg()
        if errs:
            cfg["sealed"] = False
            return False
        cfg["sealed"] = True
        return True

    def story_build_preview_from_cfg():
        cfg = story_cfg_get()

        st = rpgp_seed_new_player()
        principal = cfg.get("principal", None)
        st["principal"]["selected"] = principal
        st["principal"]["distribution"] = copy.deepcopy(cfg.get("distribution", {}))

        for k in STORY_ATTRS:
            st["stats"][k] = int(cfg.get("stats", {}).get(k, 0) or 0)
        st["pending"]["stat_points"] = int(cfg.get("pending_stat", 0) or 0)

        st["pool"]["offensive_spent"] = int(cfg.get("pool_general_off", 0) or 0)
        st["pool"]["defensive_spent"] = int(cfg.get("pool_general_def", 0) or 0)

        st = compute_preview(st)
        S.rpg_panel_state_v1 = st
        S.rpg_panel_baseline_v1 = copy.deepcopy(st)
        return st

    def story_apply_combat_overrides_from_cfg():
        cfg = story_cfg_get()
        st = story_build_preview_from_cfg()
        prev = st.get("preview", {}) if isinstance(st.get("preview", {}), dict) else {}
        tp = cfg.get("tech_points", {}) if isinstance(cfg.get("tech_points", {}), dict) else {}

        hp = int(prev.get("hp_after", 1000) or 1000)
        rei = int(prev.get("reiatsu_after", 1000) or 1000)
        ene = int(prev.get("energia_after", 100) or 100)

        e_hp = 900
        e_rei = 900
        e_ene = 90

        S.story_pilot_resource_override = {
            "player_hp": hp,
            "player_reiatsu": rei,
            "player_energy": ene,
            "enemy_hp": e_hp,
            "enemy_reiatsu": e_rei,
            "enemy_energy": e_ene,
        }

        rep = list(cfg.get("repertoire", []) or [])
        S.story_pilot_allowed_offensive = [k for k in rep if k in ("stronger_attack", "direct_attack")]
        S.story_pilot_allowed_defensive = [k for k in rep if k in ("defense_strong_block",)]

        # Sincronizar bonus de técnicas del tutorial con el motor real de combate.
        fn_set_bonus = getattr(S, "spa_set_bonus", None)
        if callable(fn_set_bonus):
            fn_set_bonus("player:0", "stronger_attack", int(tp.get("stronger_attack", 0) or 0), save=False)
            fn_set_bonus("player:0", "direct_attack", int(tp.get("direct_attack", 0) or 0), save=False)
            fn_set_bonus("player:0", "defense_strong_block", int(tp.get("defense_strong_block", 0) or 0), save=False)

            # Enemigo tutorial plano (100 base, sin bonus extra)
            fn_set_bonus("enemy:0", "stronger_attack", 0, save=False)
            fn_set_bonus("enemy:0", "direct_attack", 0, save=False)
            fn_set_bonus("enemy:0", "defense_strong_block", 0, save=False)


screen story_panel_tutorial_basics():
    tag menu
    frame:
        xfill True
        yfill True
        padding (28, 28)
        vbox:
            spacing 12
            text "Fundamentos del sistema" size 42
            text "Atributos: fuerza, agilidad, resistencia, inteligencia, espiritu." size 24
            text "Parámetros: ataque, defensa, hp, energia, reiatsu." size 24
            text "Equivalencias (1 punto):" size 24
            text "• fuerza -> +100 ataque" size 22
            text "• agilidad -> +100 defensa" size 22
            text "• resistencia -> +100 hp" size 22
            text "• inteligencia -> +100 energia" size 22
            text "• espiritu -> +100 reiatsu" size 22
            text "Si un atributo es principal: distribuyes 100 en 4 de 5 parámetros (25/50/75/100)." size 22
            text "Pool técnico inicial: 200 (general)." size 22
            text "Técnicas iniciales: Ataque más fuerte, Ataque directo y Defensa fuerte." size 22
            null height 10
            textbutton "Continuar" action Return()


screen story_panel_choose_principal():
    tag menu
    $ cfg = story_cfg_get()
    frame:
        xfill True
        yfill True
        padding (28, 28)
        vbox:
            spacing 12
            text "Paso 1/4 — Elegir atributo principal" size 36
            text "Principal actual: %s" % (cfg.get("principal", "(ninguno)")) size 24
            hbox:
                spacing 10
                for k in STORY_ATTRS:
                    textbutton "[k]" action Function(story_set_principal, k)
            null height 8
            textbutton "Confirmar principal" action Return() sensitive (cfg.get("principal", None) in STORY_ATTRS)


screen story_panel_assign_stat():
    tag menu
    $ cfg = story_cfg_get()
    $ principal = cfg.get("principal", None)
    frame:
        xfill True
        yfill True
        padding (28, 28)
        vbox:
            spacing 12
            text "Paso 2/4 — Asignar 1 punto al atributo principal" size 36
            text "Principal: %s | Pendiente: %s" % (principal, cfg.get("pending_stat", 0)) size 24
            for k in STORY_ATTRS:
                hbox:
                    spacing 10
                    text "[k]" xsize 180
                    text "%s" % cfg.get("stats", {}).get(k, 0) xsize 40
                    if k == principal:
                        textbutton "+1" action Function(story_add_stat, k, +1) sensitive (int(cfg.get("pending_stat", 0) or 0) > 0)
                    else:
                        text "bloqueado" color "#999"
            null height 8
            textbutton "Confirmar punto de stat" action Return() sensitive (int(cfg.get("pending_stat", 0) or 0) == 0)


screen story_panel_distribution():
    tag menu
    $ cfg = story_cfg_get()
    frame:
        xfill True
        yfill True
        padding (28, 28)
        vbox:
            spacing 12
            text "Paso 3/4 — Distribución principal (100 en 4 de 5)" size 36
            text "Total: %s/100 | Activos: %s/4" % (story_distribution_total(), story_distribution_active()) size 24
            for p in STORY_PARAMS:
                hbox:
                    spacing 8
                    text "[p]" xsize 120
                    text "Actual: %s" % cfg.get("distribution", {}).get(p, 0) xsize 120
                    for v in (25, 50, 75, 100):
                        textbutton "[v]" action Function(story_set_distribution, p, v)
                    textbutton "0" action Function(story_set_distribution, p, 0)
            null height 8
            textbutton "Confirmar distribución" action Return() sensitive (story_distribution_total() == 100 and story_distribution_active() <= 4)


screen story_panel_tech_and_confirm():
    tag menu
    $ cfg = story_cfg_get()
    $ errs = story_validate_cfg()
    $ rep = list(cfg.get("repertoire", []) or [])
    $ tp = cfg.get("tech_points", {}) if isinstance(cfg.get("tech_points", {}), dict) else {}
    $ hudp = story_preview_resources()

    frame:
        xfill True
        yfill True
        padding (21, 21)
        vbox:
            spacing 8
            viewport:
                id "story_step4_vp"
                xfill True
                yfill True
                draggable True
                mousewheel True
                scrollbars "horizontal"
                hbox:
                    spacing 16

                    vbox:
                        xsize 885
                        spacing 8
                        text "Paso 4/4 — Técnicas, repertorio y confirmación" size 27

                        text "Pool general: %s | Off: %s | Def: %s" % (
                            cfg.get("pool_general_total", 200), cfg.get("pool_general_off", 0), cfg.get("pool_general_def", 0)
                        ) size 17
                        hbox:
                            spacing 6
                            textbutton "+Off 25" action Function(story_add_pool, "general_off", +25)
                            textbutton "-Off 25" action Function(story_add_pool, "general_off", -25)
                            textbutton "+Def 25" action Function(story_add_pool, "general_def", +25)
                            textbutton "-Def 25" action Function(story_add_pool, "general_def", -25)

                        text "Pool específico principal — Ataque: %s/%s | Defensa: %s/%s" % (
                            cfg.get("pool_principal_off_spent", 0), cfg.get("pool_principal_off", 0),
                            cfg.get("pool_principal_def_spent", 0), cfg.get("pool_principal_def", 0)
                        ) size 17
                        hbox:
                            spacing 6
                            textbutton "+Atk esp 25" action Function(story_add_pool, "principal_off", +25)
                            textbutton "-Atk esp 25" action Function(story_add_pool, "principal_off", -25)
                            textbutton "+Def esp 25" action Function(story_add_pool, "principal_def", +25)
                            textbutton "-Def esp 25" action Function(story_add_pool, "principal_def", -25)

                        text "Asignación vertical de técnicas (base 100 por defecto):" size 17
                        hbox:
                            spacing 14

                            frame:
                                padding (8, 8)
                                vbox:
                                    spacing 4
                                    text "Ataque más fuerte" size 15
                                    text "Base: 100 | Bonus: %s | Total: %s" % (tp.get("stronger_attack", 0), 100 + int(tp.get("stronger_attack", 0) or 0)) size 14
                                    hbox:
                                        spacing 4
                                        textbutton "+25" action Function(story_add_tech_points, "stronger_attack", +25)
                                        textbutton "-25" action Function(story_add_tech_points, "stronger_attack", -25)
                                    textbutton ("Quitar" if "stronger_attack" in rep else "Añadir al repertorio") action Function(story_toggle_tech, "stronger_attack")

                            frame:
                                padding (8, 8)
                                vbox:
                                    spacing 4
                                    text "Ataque directo" size 15
                                    text "Base: 100 | Bonus: %s | Total: %s" % (tp.get("direct_attack", 0), 100 + int(tp.get("direct_attack", 0) or 0)) size 14
                                    hbox:
                                        spacing 4
                                        textbutton "+25" action Function(story_add_tech_points, "direct_attack", +25)
                                        textbutton "-25" action Function(story_add_tech_points, "direct_attack", -25)
                                    textbutton ("Quitar" if "direct_attack" in rep else "Añadir al repertorio") action Function(story_toggle_tech, "direct_attack")

                            frame:
                                padding (8, 8)
                                vbox:
                                    spacing 4
                                    text "Defensa fuerte" size 15
                                    text "Base: 100 | Bonus: %s | Total: %s" % (tp.get("defense_strong_block", 0), 100 + int(tp.get("defense_strong_block", 0) or 0)) size 14
                                    hbox:
                                        spacing 4
                                        textbutton "+25" action Function(story_add_tech_points, "defense_strong_block", +25)
                                        textbutton "-25" action Function(story_add_tech_points, "defense_strong_block", -25)
                                    textbutton ("Quitar" if "defense_strong_block" in rep else "Añadir al repertorio") action Function(story_toggle_tech, "defense_strong_block")

                        text "Off disponible/spent: %s / %s | Def disponible/spent: %s / %s" % (
                            story_off_budget(), story_off_spent(), story_def_budget(), story_def_spent()
                        ) size 15
                        text "Repertorio actual: %s" % (", ".join(rep) if rep else "(vacío)") size 15

                        if errs:
                            text "Requisitos pendientes:" size 17 color "#ffaaaa"
                            for e in errs:
                                text "• [e]" color "#ffaaaa" size 14
                        else:
                            text "Configuración válida para duelo tutorial." size 17 color "#88ff88"

                        hbox:
                            spacing 6
                            textbutton "Confirmar configuración" action Function(story_seal_configuration)
                            textbutton "Iniciar duelo" action Return() sensitive bool(cfg.get("sealed", False))

                    frame:
                        xsize 270
                        yfill True
                        padding (9, 9)
                        vbox:
                            spacing 8
                            text "HUD previo del personaje" size 18
                            text "HP: %s" % hudp.get("hp", 1000) size 17
                            text "Reiatsu: %s" % hudp.get("reiatsu", 1000) size 17
                            text "Energía: %s" % hudp.get("energia", 100) size 17

            bar value XScrollValue("story_step4_vp") xfill True


image story_harribel_pilot = im.Scale("images/characters/Harribel_a.png", 900, 675)


label story_phaseA_intro:
    $ import renpy.store as S
    $ S.story_mode_active = True
    $ S.story_pilot_last_result = "unknown"
    $ story_reset_cfg()

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

    show story_harribel_pilot at truecenter
    "Harribel" "Así que tú eres [S.story_player_name]. Camina conmigo."
    "Harribel" "Antes del duelo te enseñaré los fundamentos del sistema."

    menu:
        "Responder a Harribel"
        "Estoy listo para aprender.":
            "Harribel" "Bien. Vamos paso por paso."

    hide story_harribel_pilot
    jump story_phaseB_training_panel


label story_phaseB_training_panel:
    call screen story_panel_tutorial_basics
    call screen story_panel_choose_principal
    call screen story_panel_assign_stat
    call screen story_panel_distribution
    call screen story_panel_tech_and_confirm

    "Harribel" "Configuración sellada. Ahora empieza el duelo."
    jump story_phaseC_battle_bridge


label story_phaseC_battle_bridge:
    $ import renpy.store as S
    $ S.battle_team_mode = "1v1"
    $ S.battle_player_id = "Harribel"
    $ S.battle_enemy_id = "Hollow"
    $ S.ai_offense_concat_mode = "off"
    $ S.ai_allow_focus = False
    $ S.ai_finisher_test_mode = "force_stronger"
    $ S.ai_defense_test_mode = "force_strong"
    $ S.ai_defense_concat = False
    $ S.story_tutorial_enemy_force_strong_100 = True
    $ S.story_tutorial_enemy_force_def_strong_50 = True

    $ story_apply_combat_overrides_from_cfg()

    jump battle_start


label story_phaseC_postbattle:
    $ import renpy.store as S

    scene fondo3 with fade
    show story_harribel_pilot at truecenter

    if S.story_pilot_last_result == "victory":
        "Harribel" "Buen trabajo, [S.story_player_name]. Ganaste tu primera lección."
        "Harribel" "No fue suerte. Fue control."
    elif S.story_pilot_last_result == "defeat":
        "Harribel" "Perdiste... y Hueco Mundo no perdona la debilidad."
        "Harribel" "Levántate sola o quédate atrás."
    else:
        "Harribel" "No hay victoria clara, pero aprendiste a sobrevivir un poco más."

    "Harribel" "Fin de la prueba piloto. La próxima vez, no te sostendré la mano."

    hide story_harribel_pilot
    $ S.story_mode_active = False
    $ S.story_pilot_allowed_offensive = []
    $ S.story_pilot_allowed_defensive = []
    $ S.story_pilot_resource_override = {}
    $ S.story_tutorial_enemy_force_strong_100 = False
    $ S.story_tutorial_enemy_force_def_strong_50 = False
    $ renpy.full_restart()
    return
