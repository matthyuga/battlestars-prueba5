# ===========================================================
# 06A_BATTLE_HUD_SYSTEM.RPY – Sistema de Barras de HP y HUD
# v3.5 FocusSync Edition (Ren'Py 7.4.9)
# -----------------------------------------------------------
# - Costos dinámicos EXACTOS (Reiatsu x2 solo en técnica afectada)
# - Energía no se duplica
# - El HUD muestra lo mismo que el selector
# - Cero costos fantasmas / reseteo limpio
# ===========================================================

init -970 python:

    # === Estado HUD ===
    battle_hp_player = 10000
    battle_hp_enemy = 10000
    battle_hp_player_max = 10000
    battle_hp_enemy_max = 10000

    hp_flash_timer = 0
    hp_flash_color = None
    hud_visible = False

    # === Nombres HUD (display) ===
    hud_player_name = "Jugador"
    hud_enemy_name  = "Enemigo"

    # === Estados de simulación de recursos (jugador) ===
    simulated_reiatsu = 0
    simulated_energy = 0

    enemy_simulated_reiatsu = 0
    enemy_simulated_energy = 0


    # ===========================================================
    # 🔸 MAPA GLOBAL (visual → TECH_ID)
    # ===========================================================
    TECH_MAP_GLOBAL = {
        "Ataque Extra":        "extra_attack",
        "Técnica Extra":       "extra_tech",
        "Ataque Reductor":     "attack_reducer",
        "Ataque Directo":      "direct_attack",
        "Ataque Negador":      "noatk_attack",
        "Ataque más fuerte":   "stronger_attack",

        "Defensa Extra":        "defense_extra",
        "Defensa Reductora":    "defense_reducer",
        "Defensa Reflectora":   "defense_reflect",
        "Defensa Fuerte":       "defense_strong_block",

        "Concentrar":          "focus",
        "Concentrar x2":       "focus",
        "Potenciar":           "defense_boost",
    }


    # ===========================================================
    # 🔍 DETECTAR QUÉ TÉCNICA SERÁ DUPLICADA POR FOCUS
    # ===========================================================
    def hud_find_focus_target_index(queue, mode):

        focus_seen = False
        boost_seen = False

        for i, name in enumerate(queue):

            # -------------------------
            # MODO OFENSIVO
            # -------------------------
            if mode == "offensive":
                if name in ("Concentrar", "Concentrar x2"):
                    focus_seen = True
                    continue

                if focus_seen:
                    tech_id = TECH_MAP_GLOBAL.get(name)
                    if tech_id in (
                        "extra_attack", "extra_tech", "attack_reducer",
                        "direct_attack", "noatk_attack",
                        "strong_attack", "stronger_attack"
                    ):
                        return i

            # -------------------------
            # MODO DEFENSIVO
            # -------------------------
            if mode == "defensive":
                if name == "Potenciar":
                    boost_seen = True
                    continue

                if boost_seen:
                    tech_id = TECH_MAP_GLOBAL.get(name)
                    if tech_id in (
                        "defense_extra", "defense_reducer",
                        "defense_reflect", "defense_strong_block"
                    ):
                        return i

        return None


    # ===========================================================
    # 🔹 FUNCIÓN: Actualizar costos dinámicos simulados (HUD)
    # ===========================================================
    def hud_update_simulation_costs(user, pending_tech_list):

        global simulated_reiatsu, simulated_energy

        import renpy.store as S

        # detectar técnica afectada por focus
        focus_target = hud_find_focus_target_index(pending_tech_list, S.battle_mode)

        total_rei = 0
        total_ene = 0

        for i, tech_name in enumerate(pending_tech_list):

            tech_id = TECH_MAP_GLOBAL.get(tech_name, None)
            if tech_id is None:
                continue

            cost = S.reiatsu_energy_dynamic_cost(tech_id, user)

            rei_cost = cost["reiatsu_cost"]
            ene_cost = cost["energy_cost"]

            # si esta técnica es la afectada → DUPLICAR SOLO REIATSU
            if i == focus_target:
                rei_cost *= 2

            total_rei += rei_cost
            total_ene += ene_cost

        simulated_reiatsu = S.player_reiatsu - total_rei
        simulated_energy  = S.player_energy  - total_ene


    # ===========================================================
    # 🔸 Actualiza barras de HP
    # ===========================================================
    def battle_update_hp_bars(player_hp, enemy_hp, flash_target=None, color=None):
        global battle_hp_player, battle_hp_enemy, hp_flash_timer, hp_flash_color

        battle_hp_player = int(player_hp)
        battle_hp_enemy = int(enemy_hp)

        if flash_target:
            hp_flash_timer = 10
            hp_flash_color = color

        if renpy.get_screen("battle_hp_overlay"):
            renpy.restart_interaction()

        try:
            battle_update_atmosphere_by_hp(player_hp, enemy_hp)
        except:
            pass


    # ===========================================================
    # 🔸 Mostrar HUD
    # ===========================================================
    def battle_show_hud(sync_fade=True):
        global hud_visible, simulated_reiatsu, simulated_energy
        global enemy_simulated_reiatsu, enemy_simulated_energy
        global hud_player_name, hud_enemy_name

        import renpy.store as S

        hud_visible = True

        # ✅ Nombres dinámicos (display) con fallback seguro
        try:
            hud_player_name = S.battle_player.get("name", "Jugador")
        except:
            hud_player_name = "Jugador"

        try:
            hud_enemy_name = S.battle_enemy.get("name", "Enemigo")
        except:
            hud_enemy_name = "Enemigo"

        simulated_reiatsu = S.player_reiatsu
        simulated_energy  = S.player_energy

        enemy_simulated_reiatsu = S.enemy_reiatsu
        enemy_simulated_energy  = S.enemy_energy

        if sync_fade:
            renpy.with_statement(Dissolve(0.35))

        renpy.show_screen("battle_hp_overlay")
        renpy.show_screen("battle_damage_popups")
        renpy.show_screen("battle_turn_summary_overlay")

        renpy.restart_interaction()


    # ===========================================================
    # 🔸 Ocultar HUD
    # ===========================================================
    def battle_hide_hud():
        global hud_visible
        hud_visible = False

        renpy.with_statement(Dissolve(0.25))

        renpy.hide_screen("battle_hp_overlay")
        renpy.hide_screen("battle_damage_popups")
        renpy.hide_screen("battle_turn_summary_overlay")

        renpy.restart_interaction()



# ===========================================================
# 🔹 SCREEN HUD (HP, Reiatsu, Energía con dif dinámico)
# ===========================================================
screen battle_hp_overlay():
    zorder 80
    modal False

    if not hud_visible:
        null
    else:

        if hp_flash_timer > 0:
            $ hp_flash_timer -= 1

        # ======================================================
        # ⚔️ HUD DEL JUGADOR
        # ======================================================
        frame at hud_fade_in:
            background "#0008"
            xalign 0.0 yalign 0.0
            xpadding 12 ypadding 8

            vbox at hp_pulse_player:
                spacing 2

                # ✅ Nombre dinámico
                text hud_player_name color "#88CCFF" size 22 bold True

                bar:
                    value (float(battle_hp_player) / battle_hp_player_max)
                    range 1.0 xmaximum 280 ymaximum 16
                    left_bar "#00BFFF" right_bar "#222222"

                text "{} / {}".format(
                    battle_fmt_num(battle_hp_player),
                    battle_fmt_num(battle_hp_player_max)
                ) color "#FFFFFF" size 16

                # -----------------------------
                # REIATSU (con resta dinámica)
                # -----------------------------
                hbox:
                    spacing 6
                    text "Reiatsu: {}".format(battle_fmt_num(player_reiatsu)) size 15 color "#55FFFF"

                    $ rei_diff = 0
                    if hasattr(store, "pending_tech_list") and store.pending_tech_list:
                        $ rei_diff = simulated_reiatsu - player_reiatsu

                    if rei_diff != 0:
                        text "-{}".format(battle_fmt_num(abs(rei_diff))) size 15 color "#66CCFFAA"

                # -----------------------------
                # ENERGÍA (con resta dinámica)
                # -----------------------------
                hbox:
                    spacing 6
                    text "Energía: {}".format(battle_fmt_num(player_energy)) size 15 color "#FFA500"

                    $ ene_diff = 0
                    if hasattr(store, "pending_tech_list") and store.pending_tech_list:
                        $ ene_diff = simulated_energy - player_energy

                    if ene_diff != 0:
                        text "-{}".format(battle_fmt_num(abs(ene_diff))) size 15 color "#FFBB66AA"



        # ======================================================
        # 👹 HUD DEL ENEMIGO
        # ======================================================
        frame at hud_fade_in:
            background "#0008"
            xalign 1.0 yalign 0.0
            xpadding 12 ypadding 8

            vbox at hp_pulse_enemy:
                spacing 2

                # ✅ Nombre dinámico
                text hud_enemy_name color "#FF7777" size 22 bold True

                bar:
                    value (float(battle_hp_enemy) / battle_hp_enemy_max)
                    range 1.0 xmaximum 280 ymaximum 16
                    left_bar "#FF3333" right_bar "#222222"

                text "{} / {}".format(
                    battle_fmt_num(battle_hp_enemy),
                    battle_fmt_num(battle_hp_enemy_max)
                ) color "#FFFFFF" size 16

                hbox:
                    spacing 6
                    text "Reiatsu: {}".format(battle_fmt_num(enemy_reiatsu)) size 15 color "#55FFFF"

                hbox:
                    spacing 6
                    text "Energía: {}".format(battle_fmt_num(enemy_energy)) size 15 color "#FFA500"



# ===========================================================
# 🔹 TRANSFORMS
# ===========================================================
transform hud_fade_in:
    alpha 0.0
    linear 0.35 alpha 1.0

transform hp_pulse_player:
    on show:
        linear 0.15 zoom 1.03
        linear 0.15 zoom 1.00

transform hp_pulse_enemy:
    on show:
        linear 0.15 zoom 1.03
        linear 0.15 zoom 1.00
