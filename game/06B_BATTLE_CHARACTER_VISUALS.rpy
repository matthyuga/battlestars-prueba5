# ============================================================
# 06B_BATTLE_CHARACTER_VISUALS.rpy
# Character HUD portraits and battle pose presentation layer.
# ============================================================

init -940 python:
    import renpy.store as S

    def bs_visual_char_norm(value):
        return str(value or "").strip().lower().replace("_", " ").replace("-", " ")

    BS_CHARACTER_VISUAL_ASSETS = {
        "megumin": {
            "hud": "images/character/hechos/megumin-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_megumin_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_megumin_rebel_facing.png",
            "pose": "images/character/megumin spe.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "aqua": {
            "hud": "images/character/hechos/aqua-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_aqua_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_aqua_rebel_facing.png",
            "pose": "images/character/aqua spe.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "darkness": {
            "hud": "images/character/hechos/darkness-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_darkness_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_darkness_rebel_facing.png",
            "pose": "images/character/darkness spe.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "kazuma": {
            "hud": "images/character/hechos/kazuma-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_kazuma_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_kazuma_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "ino": {
            "hud": "images/character/hechos/ino-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_ino_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_ino_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "sakura": {
            "hud": "images/character/hechos/sakura-portrait-style-01-cel-v2.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_sakura_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_sakura_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "karin": {
            "hud": "images/character/hechos/karin-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_karin_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_karin_rebel_facing.png",
            "hud_crop": (300, 45, 650, 720),
        },
        "boruto": {
            "hud": "images/character/hechos/boruto-portrait-style-01-cel.png",
            "hud_rebel": "gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png",
            "hud_rebel_enemy": "gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png",
            "hud_crop": (335, 75, 585, 650),
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
    }

    def bs_character_visual_key(char_id=""):
        n = bs_visual_char_norm(char_id)
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
        return bs_character_visual_asset(cid, rebel_kind)

    def bs_battle_pose_displayable(char_id="", side="player"):
        cid = str(char_id or bs_battle_current_visual_char_id(side) or "")
        path = bs_character_visual_asset(cid, "pose")
        if not path:
            return None
        return path

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
    S.bs_battle_current_visual_char_id = bs_battle_current_visual_char_id
    S.bs_battle_head_portrait = bs_battle_head_portrait
    S.bs_battle_head_portrait_displayable = bs_battle_head_portrait_displayable
    S.bs_battle_rebel_portrait_path = bs_battle_rebel_portrait_path
    S.bs_battle_rebel_portrait_displayable = bs_battle_rebel_portrait_displayable
    S.bs_battle_pose_displayable = bs_battle_pose_displayable
    S.bs_battle_show_character_pose = bs_battle_show_character_pose


transform bs_battle_pose_slide:
    alpha 0.0
    xanchor 1.0
    yanchor 1.0
    xpos 1.10
    ypos 1.03
    zoom 0.74
    linear 0.22 alpha 1.0 xpos 0.92
    pause 0.88
    linear 0.26 alpha 0.0 xpos 0.76


screen battle_character_pose_fx(char_id="", side="player", trigger=""):
    zorder 87
    $ _pose_fn = getattr(store, "bs_battle_pose_displayable", None)
    $ _pose_disp = _pose_fn(char_id, side) if callable(_pose_fn) else None

    if _pose_disp:
        add _pose_disp at bs_battle_pose_slide

    timer 1.42 action Hide("battle_character_pose_fx")
