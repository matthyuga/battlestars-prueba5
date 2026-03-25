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

    def story_reset_cfg():
        S.story_cfg = {
            "principal": None,
            "stats": {"fuerza": 0, "agilidad": 0, "resistencia": 0, "inteligencia": 0, "espiritu": 0},
            "pending_stat": 1,
            "distribution": {"ataque": 0, "defensa": 0, "hp": 0, "energia": 0, "reiatsu": 0},
            "pool_general_total": 200,
            "pool_general_off": 0,
            "pool_general_def": 0,
            "pool_principal_off": 0,
            "pool_principal_def": 0,
            "pool_principal_off_spent": 0,
            "pool_principal_def_spent": 0,
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

        cfg["pool_principal_off"] = int(cfg["distribution"].get("ataque", 0) or 0)
        cfg["pool_principal_def"] = int(cfg["distribution"].get("defensa", 0) or 0)

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

    frame:
        xfill True
        yfill True
        padding (28, 28)
        vbox:
            spacing 10
            text "Paso 4/4 — Técnicas, repertorio y confirmación" size 36

            text "Pool general: %s | Off: %s | Def: %s" % (
                cfg.get("pool_general_total", 200), cfg.get("pool_general_off", 0), cfg.get("pool_general_def", 0)
            ) size 22
            hbox:
                spacing 8
                textbutton "+Off 25" action Function(story_add_pool, "general_off", +25)
                textbutton "-Off 25" action Function(story_add_pool, "general_off", -25)
                textbutton "+Def 25" action Function(story_add_pool, "general_def", +25)
                textbutton "-Def 25" action Function(story_add_pool, "general_def", -25)

            text "Pool específico principal — Ataque: %s/%s | Defensa: %s/%s" % (
                cfg.get("pool_principal_off_spent", 0), cfg.get("pool_principal_off", 0),
                cfg.get("pool_principal_def_spent", 0), cfg.get("pool_principal_def", 0)
            ) size 22
            hbox:
                spacing 8
                textbutton "+Atk esp 25" action Function(story_add_pool, "principal_off", +25)
                textbutton "-Atk esp 25" action Function(story_add_pool, "principal_off", -25)
                textbutton "+Def esp 25" action Function(story_add_pool, "principal_def", +25)
                textbutton "-Def esp 25" action Function(story_add_pool, "principal_def", -25)

            text "Técnicas iniciales disponibles (sin concentrar por ahora):" size 22
            hbox:
                spacing 8
                textbutton "Ataque más fuerte" action Function(story_toggle_tech, "stronger_attack")
                textbutton "Ataque directo" action Function(story_toggle_tech, "direct_attack")
                textbutton "Defensa fuerte" action Function(story_toggle_tech, "defense_strong_block")
            text "Repertorio actual: %s" % (", ".join(rep) if rep else "(vacío)") size 20

            if errs:
                text "Requisitos pendientes:" size 22 color "#ffaaaa"
                for e in errs:
                    text "• [e]" color "#ffaaaa" size 18
            else:
                text "Configuración válida para duelo tutorial." size 22 color "#88ff88"

            hbox:
                spacing 10
                textbutton "Confirmar configuración" action Function(story_seal_configuration)
                textbutton "Iniciar duelo" action Return() sensitive bool(cfg.get("sealed", False))


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

    show expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png" at truecenter
    "Harribel" "Así que tú eres [S.story_player_name]. Camina conmigo."
    "Harribel" "Antes del duelo te enseñaré los fundamentos del sistema."

    menu:
        "Responder a Harribel"
        "Estoy listo para aprender.":
            "Harribel" "Bien. Vamos paso por paso."

    hide expression "gui/battle/hud_ai/portraits/portrait_harribel_full.png"
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

    $ story_apply_combat_overrides_from_cfg()

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
