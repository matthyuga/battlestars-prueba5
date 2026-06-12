# ============================================================
# 06B_BATTLE_CHARACTER_VISUALS.rpy
# Character HUD portraits and battle pose presentation layer.
# ============================================================

init -940 python:
    import renpy.store as S

    BS_CHARACTER_PROFILE_ROOT = "images/character/hechos/tmp-imagegen"

    def bs_visual_char_norm(value):
        return str(value or "").strip().lower().replace("_", " ").replace("-", " ")

    BS_CHARACTER_VISUAL_ASSETS = {
        "megumin": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/megumin-portrait-style-01-cel.png",
            "hud": "images/character/hechos/megumin-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_megumin_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_megumin_rebel_facing.png",
            "pose": "images/character/megumin-style-01-cel.png",
            "pose_color": "#FF554A",
            "pose_zoom": 0.52,
            "hud_crop": (300, 45, 650, 720),
        },
        "aqua": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/aqua-portrait-style-01-cel.png",
            "hud": "images/character/hechos/aqua-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_aqua_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_aqua_rebel_facing.png",
            "pose": "images/character/aqua-style-01-cel.png",
            "pose_color": "#72D9FF",
            "pose_zoom": 0.52,
            "hud_crop": (300, 45, 650, 720),
        },
        "darkness": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/darkness-portrait-style-01-cel.png",
            "hud": "images/character/hechos/darkness-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_darkness_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_darkness_rebel_facing.png",
            "pose": "images/character/darkness-style-01-cel.png",
            "pose_color": "#FFD166",
            "pose_zoom": 0.50,
            "hud_crop": (300, 45, 650, 720),
        },
        "kazuma": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/kazuma-portrait-style-01-cel.png",
            "hud": "images/character/hechos/kazuma-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_kazuma_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_kazuma_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "ino": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/ino-portrait-style-01-cel.png",
            "hud": "images/character/hechos/ino-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_ino_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_ino_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "sakura": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/sakura-portrait-style-01-cel-v2.png",
            "hud": "images/character/hechos/sakura-portrait-style-01-cel-v2.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_sakura_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_sakura_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "karin": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/karin-portrait-style-01-cel.png",
            "hud": "images/character/hechos/karin-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_karin_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_karin_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "boruto": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/boruto-portrait-style-01-cel.png",
            "hud": "images/character/hechos/boruto-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png",
            "hud_crop": (335, 75, 585, 650),
        },
        "amber": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/amber-portrait-style-01-cel.png",
        },
        "bloom": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/bloom-portrait-style-01-cel.png",
        },
        "bertrand": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/blonde-battle-outfit-portrait-v2.png",
        },
        "choji": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/choji-portrait-style-01-cel.png",
        },
        "danny_phantom": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/danny-phantom-portrait-style-01-cel-painted-transparent-clean.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing.png",
            "hud_rebel_v2": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v2.png",
            "hud_rebel_enemy_v2": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v2.png",
            "hud_rebel_v3": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v3.png",
            "hud_rebel_enemy_v3": "gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v3.png",
        },
        "elizabeth": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/elizabeth-portrait-style-01-cel.png",
        },
        "hanabi": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/hanabi-closeup-portrait-transparent-clean.png",
        },
        "kiba": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/kiba-portrait-style-01-cel.png",
        },
        "laezel": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/laezel-portrait-style-01-cel.png",
        },
        "maki_zenin": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/maki-zenin-portrait-style-01-cel.png",
        },
        "nobara": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/nobara-portrait-style-01-cel.png",
        },
        "revy": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/revy-closeup-camera-v2.png",
        },
        "ryuko": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/ryuko-portrait-style-01-cel.png",
        },
        "shadowheart": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/shadowheart-portrait-style-01-cel-v2.png",
        },
        "shikamaru": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/shikamaru-portrait-style-01-cel.png",
        },
        "shino": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/shino-portrait-style-01-cel.png",
        },
        "shrinking_rae": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/shrinking-rae-portrait-style-01-cel.png",
        },
        "the_twins": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/the-twin-portrait-style-01-cel.png",
        },
        "yanfei": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/yanfei-portrait-style-01-cel.png",
        },
        "yor_forger": {
            "profile": BS_CHARACTER_PROFILE_ROOT + "/yor-forger-portrait-style-01-cel.png",
        },
    }

    BS_CHARACTER_VISUAL_ALIASES = {
        "megumin": "megumin",
        "aqua": "aqua",
        "darkness": "darkness",
        "kazuma": "kazuma",
        "kasuma": "kazuma",
        "ino": "ino",
        "sakura": "sakura",
        "karin": "karin",
        "boruto": "boruto",
        "amber": "amber",
        "bloom": "bloom",
        "bertrand": "bertrand",
        "choji": "choji",
        "chouji": "choji",
        "danny phantom": "danny_phantom",
        "elizabeth": "elizabeth",
        "hanabi": "hanabi",
        "kiba": "kiba",
        "laezel": "laezel",
        "lae zel": "laezel",
        "lae'zel": "laezel",
        "maki": "maki_zenin",
        "maki atadura celestial": "maki_zenin",
        "maki zenin": "maki_zenin",
        "nobara": "nobara",
        "revy": "revy",
        "ryuko": "ryuko",
        "shadowheart": "shadowheart",
        "shikamaru": "shikamaru",
        "shino": "shino",
        "shrinking rae": "shrinking_rae",
        "the twin": "the_twins",
        "the twins": "the_twins",
        "twins": "the_twins",
        "yanfei": "yanfei",
        "yor": "yor_forger",
        "yor forger": "yor_forger",
    }

    def bs_visual_candidate_names(char_id=""):
        out = []
        raw = str(char_id or "").strip()
        if raw:
            out.append(raw)
        try:
            row_fn = getattr(S, "bs_saga_hero_row", None)
            row = row_fn(raw) if callable(row_fn) else None
            if isinstance(row, dict):
                for key in ("name", "hero_id", "id"):
                    val = str(row.get(key, "") or "").strip()
                    if val:
                        out.append(val)
        except:
            pass
        try:
            ch_fn = getattr(S, "get_character", None)
            ch = ch_fn(raw) if callable(ch_fn) else None
            if isinstance(ch, dict):
                for key in ("name", "id"):
                    val = str(ch.get(key, "") or "").strip()
                    if val:
                        out.append(val)
        except:
            pass
        clean = []
        seen = {}
        for item in out:
            key = bs_visual_char_norm(item)
            if key and not seen.get(key):
                seen[key] = True
                clean.append(item)
        return clean

    def bs_character_visual_key(char_id=""):
        for value in bs_visual_candidate_names(char_id):
            n = bs_visual_char_norm(value)
            if n in BS_CHARACTER_VISUAL_ALIASES:
                return BS_CHARACTER_VISUAL_ALIASES[n]
        return ""

    def bs_character_visual_asset(char_id="", kind="hud"):
        key = bs_character_visual_key(char_id)
        if not key:
            return ""
        data = BS_CHARACTER_VISUAL_ASSETS.get(key, {}) or {}
        path = str(data.get(kind, "") or "")
        if not path:
            return ""
        try:
            if renpy.loadable(path):
                return path
        except:
            pass
        return ""

    def bs_character_visual_hud_crop(char_id=""):
        key = bs_character_visual_key(char_id)
        if not key:
            return None
        data = BS_CHARACTER_VISUAL_ASSETS.get(key, {}) or {}
        crop = data.get("hud_crop", None)
        if isinstance(crop, tuple) and len(crop) == 4:
            return crop
        return None

    def bs_battle_current_visual_char_id(side="player"):
        side_s = "enemy" if str(side or "").strip().lower() == "enemy" else "player"

        key = ""
        try:
            if side_s == "player":
                key = str(getattr(S, "defense_target_key", "") or getattr(S, "current_actor_unit_key", "") or "")
            else:
                key = str(getattr(S, "current_enemy_unit_key", "") or "")
        except:
            key = ""

        if key:
            try:
                fn_get = getattr(S, "bs_get_unit_by_key", None)
                unit = fn_get(key) if callable(fn_get) else None
                if isinstance(unit, dict):
                    cid = str(unit.get("char_id", "") or unit.get("id", "") or "").strip()
                    if cid:
                        return cid
            except:
                pass

        if side_s == "enemy":
            return str(getattr(S, "battle_enemy_id", "") or "")
        return str(getattr(S, "battle_player_id", "") or "")

    def bs_battle_head_portrait(char_id="", side="player"):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        path = bs_character_visual_asset(cid, "hud")
        if not path:
            path = bs_character_visual_asset(cid, "profile")
        if path:
            return path
        if str(side or "").strip().lower() == "enemy":
            return "gui/battle/hud_rebel/portraits/portrait_enemy_hollow_rebel_facing.png"
        return "gui/battle/hud_rebel/portraits/portrait_player_jugador_a_rebel.png"

    def bs_battle_head_portrait_displayable(char_id="", side="player", width=64, height=64):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        path = bs_character_visual_asset(cid, "hud")
        crop = bs_character_visual_hud_crop(cid)
        if path and crop:
            return im.Scale(im.Crop(path, crop), int(width), int(height))
        return im.Scale(bs_battle_head_portrait(cid, side), int(width), int(height))

    def bs_character_profile_portrait(char_id="", fallback_side="player"):
        cid = str(char_id or "").strip()
        path = bs_character_visual_asset(cid, "profile")
        if path:
            return path
        return bs_battle_head_portrait(cid, fallback_side)

    def bs_character_profile_portrait_displayable(char_id="", width=220, height=260):
        return im.Scale(bs_character_profile_portrait(char_id, "player"), int(width), int(height))

    def bs_battle_rebel_portrait_displayable(char_id="", side="player", width=136, height=113):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        side_s = "enemy" if str(side or "").strip().lower() == "enemy" else "player"
        rebel_path = bs_battle_rebel_portrait_path(cid, side_s)
        if rebel_path:
            return im.Scale(rebel_path, int(width), int(height))
        path = bs_character_visual_asset(cid, "hud")
        crop = bs_character_visual_hud_crop(cid)
        if path and crop:
            return im.Scale(im.Crop(path, crop), int(width), int(height))
        return im.Scale(bs_battle_head_portrait(cid, side), int(width), int(height))

    def bs_battle_rebel_portrait_path(char_id="", side="player"):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        side_s = "enemy" if str(side or "").strip().lower() == "enemy" else "player"
        rebel_kind = "hud_rebel_enemy" if side_s == "enemy" else "hud_rebel"
        v3_kind = rebel_kind + "_v3"
        path = bs_character_visual_asset(cid, v3_kind)
        if path:
            return path

        fallback = bs_character_visual_asset("danny phantom", v3_kind)
        if fallback:
            return fallback

        v2_kind = rebel_kind + "_v2"
        path = bs_character_visual_asset(cid, v2_kind)
        if path:
            return path

        fallback = bs_character_visual_asset("danny phantom", v2_kind)
        if fallback:
            return fallback

        path = bs_character_visual_asset(cid, rebel_kind)
        if path:
            return path
        return bs_character_visual_asset("danny phantom", rebel_kind)

    def bs_battle_pose_displayable(char_id="", side="player"):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        path = bs_character_visual_asset(cid, "pose")
        if not path:
            return None
        return path

    def bs_battle_pose_style(char_id="", side="player"):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        key = bs_character_visual_key(cid)
        data = BS_CHARACTER_VISUAL_ASSETS.get(key, {}) or {}
        return {
            "color": str(data.get("pose_color", "#FFD700") or "#FFD700"),
            "zoom": float(data.get("pose_zoom", 0.52) or 0.52),
            "key": str(key or ""),
        }

    def bs_battle_show_character_pose(side="player", char_id="", trigger=""):
        side_s = "enemy" if str(side or "").strip().lower() == "enemy" else "player"
        cid = str(char_id or bs_battle_current_visual_char_id(side_s) or "")
        if not bs_battle_pose_displayable(cid, side_s):
            return False
        try:
            renpy.show_screen("battle_character_pose_fx", char_id=cid, side=side_s, trigger=str(trigger or ""))
            renpy.restart_interaction()
            return True
        except:
            return False

    S.BS_CHARACTER_VISUAL_ASSETS = BS_CHARACTER_VISUAL_ASSETS
    S.bs_character_visual_asset = bs_character_visual_asset
    S.bs_character_profile_portrait = bs_character_profile_portrait
    S.bs_character_profile_portrait_displayable = bs_character_profile_portrait_displayable
    S.bs_battle_current_visual_char_id = bs_battle_current_visual_char_id
    S.bs_battle_head_portrait = bs_battle_head_portrait
    S.bs_battle_head_portrait_displayable = bs_battle_head_portrait_displayable
    S.bs_battle_rebel_portrait_path = bs_battle_rebel_portrait_path
    S.bs_battle_rebel_portrait_displayable = bs_battle_rebel_portrait_displayable
    S.bs_battle_pose_displayable = bs_battle_pose_displayable
    S.bs_battle_pose_style = bs_battle_pose_style
    S.bs_battle_show_character_pose = bs_battle_show_character_pose


transform bs_battle_pose_slide_player(z=0.52):
    alpha 0.0
    xanchor 0.5
    yanchor 1.0
    xpos -0.25
    ypos 1.07
    zoom (z * 0.92)
    xzoom 1.14
    yzoom 0.92
    easeout 0.22 alpha 1.0 xpos 0.46 zoom (z * 1.04) xzoom 0.96 yzoom 1.05
    easeout 0.10 xpos 0.51 zoom z xzoom 1.00 yzoom 1.00
    pause 0.98
    linear 0.24 alpha 0.0 xpos 0.58

transform bs_battle_pose_slide_enemy(z=0.52):
    alpha 0.0
    xanchor 0.5
    yanchor 1.0
    xpos 1.25
    ypos 1.07
    zoom (z * 0.92)
    xzoom 1.14
    yzoom 0.92
    easeout 0.22 alpha 1.0 xpos 0.54 zoom (z * 1.04) xzoom 0.96 yzoom 1.05
    easeout 0.10 xpos 0.49 zoom z xzoom 1.00 yzoom 1.00
    pause 0.98
    linear 0.24 alpha 0.0 xpos 0.42

transform bs_battle_pose_aura_player:
    alpha 0.0
    xalign 0.0
    yalign 0.5
    xzoom 0.0
    yzoom 1.0
    easeout 0.18 alpha 0.55 xzoom 1.0
    pause 0.68
    linear 0.34 alpha 0.0 xzoom 1.12

transform bs_battle_pose_aura_enemy:
    alpha 0.0
    xalign 1.0
    yalign 0.5
    xzoom 0.0
    yzoom 1.0
    easeout 0.18 alpha 0.55 xzoom 1.0
    pause 0.68
    linear 0.34 alpha 0.0 xzoom 1.12

transform bs_battle_pose_flash:
    alpha 0.0
    zoom 0.94
    easeout 0.12 alpha 0.28 zoom 1.0
    linear 0.34 alpha 0.0 zoom 1.04

transform bs_battle_pose_nameplate:
    alpha 0.0
    yoffset 18
    easeout 0.18 alpha 1.0 yoffset 0
    pause 0.80
    linear 0.22 alpha 0.0 yoffset -8


screen battle_character_pose_fx(char_id="", side="player", trigger=""):
    zorder 238
    modal False
    $ _pose_fn = getattr(store, "bs_battle_pose_displayable", None)
    $ _pose_disp = _pose_fn(char_id, side) if callable(_pose_fn) else None
    $ _style_fn = getattr(store, "bs_battle_pose_style", None)
    $ _pose_style = _style_fn(char_id, side) if callable(_style_fn) else {"color": "#FFD700", "zoom": 0.52, "key": ""}
    $ _pose_color = str(_pose_style.get("color", "#FFD700") or "#FFD700")
    $ _pose_zoom = float(_pose_style.get("zoom", 0.52) or 0.52)
    $ _side_s = "enemy" if str(side or "").strip().lower() == "enemy" else "player"
    $ _name_s = str(char_id or "").strip().upper()

    if _pose_disp:
        if _side_s == "enemy":
            add Solid(_pose_color + "30") at bs_battle_pose_aura_enemy
            add Solid("#FFFFFF") at bs_battle_pose_flash
            add _pose_disp at bs_battle_pose_slide_enemy(_pose_zoom)
            frame at bs_battle_pose_nameplate:
                xpos 700
                ypos 608
                xsize 390
                ysize 42
                background Solid("#05070CDD")
                padding (14, 6)
                text _name_s size 24 color _pose_color bold True outlines [(2, "#000000", 0, 0)]
        else:
            add Solid(_pose_color + "30") at bs_battle_pose_aura_player
            add Solid("#FFFFFF") at bs_battle_pose_flash
            add _pose_disp at bs_battle_pose_slide_player(_pose_zoom)
            frame at bs_battle_pose_nameplate:
                xpos 190
                ypos 608
                xsize 390
                ysize 42
                background Solid("#05070CDD")
                padding (14, 6)
                text _name_s size 24 color _pose_color bold True outlines [(2, "#000000", 0, 0)]

    timer 1.58 action Hide("battle_character_pose_fx")
