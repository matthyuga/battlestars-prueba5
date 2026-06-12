from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_SIZE = (360, 300)
PORTRAIT_WINDOW = [(82, 81), (218, 81), (292, 137), (254, 220), (72, 220), (47, 137)]
PORTRAIT_V2_SIZE = (430, 330)
PORTRAIT_V2_WINDOW = [(74, 52), (260, 35), (325, 90), (286, 252), (95, 270), (34, 145)]
PORTRAIT_V3_SIZE = (430, 330)
PORTRAIT_V3_WINDOW = [(105, 46), (245, 46), (316, 104), (294, 248), (104, 269), (42, 154)]


@dataclass(frozen=True)
class HeroPortraitSpec:
    hero_id: str
    source: Path
    player_output: Path
    enemy_output: Path
    size: tuple[int, int]
    offset: tuple[int, int]
    brightness: float = 1.08
    contrast: float = 1.04


@dataclass(frozen=True)
class HeroPortraitV2Spec:
    hero_id: str
    source: Path
    player_output: Path
    enemy_output: Path
    size: tuple[int, int]
    offset: tuple[int, int]
    brightness: float = 1.08
    contrast: float = 1.06
    accent: tuple[int, int, int] = (165, 38, 255)


@dataclass(frozen=True)
class HeroPortraitV3Spec:
    hero_id: str
    source: Path
    player_output: Path
    enemy_output: Path
    size: tuple[int, int]
    offset: tuple[int, int]
    brightness: float = 1.10
    contrast: float = 1.08
    accent: tuple[int, int, int] = (66, 225, 255)


BORUTO = HeroPortraitSpec(
    hero_id="boruto",
    source=Path("game/images/character/hechos/boruto-portrait-style-01-cel.png"),
    player_output=Path("game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png"),
    enemy_output=Path("game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png"),
    size=(198, 233),
    offset=(82, 23),
)

DANNY_PHANTOM = HeroPortraitSpec(
    hero_id="danny_phantom",
    source=Path("game/images/character/hechos/tmp-imagegen/danny-phantom-portrait-style-01-cel-painted-transparent-clean.png"),
    player_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel.png"),
    enemy_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing.png"),
    size=(202, 238),
    offset=(78, 18),
    brightness=1.10,
    contrast=1.06,
)

HERO_SPECS = {
    BORUTO.hero_id: BORUTO,
    DANNY_PHANTOM.hero_id: DANNY_PHANTOM,
}

DANNY_PHANTOM_V2 = HeroPortraitV2Spec(
    hero_id="danny_phantom",
    source=Path("game/images/character/hechos/tmp-imagegen/danny-phantom-portrait-style-01-cel-painted-transparent-clean.png"),
    player_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v2.png"),
    enemy_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v2.png"),
    size=(286, 286),
    offset=(70, 4),
    brightness=1.10,
    contrast=1.08,
    accent=(122, 245, 210),
)

HERO_SPECS_V2 = {
    DANNY_PHANTOM_V2.hero_id: DANNY_PHANTOM_V2,
}

DANNY_PHANTOM_V3 = HeroPortraitV3Spec(
    hero_id="danny_phantom",
    source=Path("game/images/character/hechos/tmp-imagegen/danny-phantom-portrait-style-01-cel-painted-transparent-clean.png"),
    player_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v3.png"),
    enemy_output=Path("game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v3.png"),
    size=(264, 264),
    offset=(80, 16),
    accent=(72, 232, 255),
)

HERO_SPECS_V3 = {
    DANNY_PHANTOM_V3.hero_id: DANNY_PHANTOM_V3,
}


def repo_path(path: Path) -> Path:
    return REPO_ROOT / path


def load_rgba(path: Path) -> Image.Image:
    return Image.open(repo_path(path)).convert("RGBA")


def portrait_window_mask() -> Image.Image:
    mask = Image.new("L", PORTRAIT_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(PORTRAIT_WINDOW, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(0.35))


def trim_transparent(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if not bbox:
        return image
    return image.crop(bbox)


def tune_source(image: Image.Image, brightness: float, contrast: float) -> Image.Image:
    r, g, b, a = image.split()
    rgb = Image.merge("RGB", (r, g, b))
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness)
    rgb = ImageEnhance.Contrast(rgb).enhance(contrast)
    return Image.merge("RGBA", (*rgb.split(), a))


def alpha_clip(image: Image.Image, mask: Image.Image) -> Image.Image:
    out = image.copy()
    clipped_alpha = ImageChops.multiply(out.getchannel("A"), mask)
    out.putalpha(clipped_alpha)
    return out


def draw_poly_glow(size: tuple[int, int], points: list[tuple[int, int]], color: tuple[int, int, int], width: int = 4) -> Image.Image:
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    for spread, alpha, line_w in ((12, 70, width + 10), (6, 100, width + 5), (2, 190, width + 1)):
        layer = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        draw.line(points + [points[0]], fill=color + (alpha,), width=line_w, joint="curve")
        if spread > 0:
            layer = layer.filter(ImageFilter.GaussianBlur(spread))
        glow.alpha_composite(layer)
    draw = ImageDraw.Draw(glow)
    draw.line(points + [points[0]], fill=color + (245,), width=width, joint="curve")
    return glow


def draw_slanted_panel(size: tuple[int, int], points: list[tuple[int, int]], fill: tuple[int, int, int], edge: tuple[int, int, int]) -> Image.Image:
    panel = Image.new("RGBA", size, (0, 0, 0, 0))
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.line(points + [points[0]], fill=edge + (180,), width=8, joint="curve")
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    panel.alpha_composite(glow)

    draw = ImageDraw.Draw(panel)
    shadow = [(x + 5, y + 6) for x, y in points]
    draw.polygon(shadow, fill=(0, 0, 0, 145))
    draw.polygon(points, fill=fill + (232,))
    draw.polygon([(points[0][0] + 8, points[0][1] + 5), (points[1][0] + 13, points[1][1] + 4), (points[2][0] - 18, points[2][1] + 5), (points[3][0] - 20, points[3][1] + 16), (points[4][0] - 12, points[4][1] + 17)], fill=(255, 255, 255, 34))
    draw.line(points + [points[0]], fill=(18, 18, 22, 255), width=4, joint="curve")
    draw.line([(points[1][0] + 12, points[1][1] + 3), (points[2][0] - 15, points[2][1] + 2), (points[3][0] - 18, points[3][1] + 10)], fill=edge + (245,), width=3)
    draw.line([(points[0][0] + 12, points[0][1] - 1), (points[4][0] - 14, points[4][1] - 1)], fill=(0, 0, 0, 120), width=2)
    draw.rectangle((15, 18, 28, 31), outline=(255, 255, 255, 150), width=3)
    draw.rectangle((282, 14, 298, 28), outline=(0, 0, 0, 115), width=3)
    return panel


def save_v3_ui_assets() -> dict[str, Path]:
    layer_dir = repo_path(Path("game/gui/battle/hud_rebel/portrait_layers_v3"))
    nameplate_dir = repo_path(Path("game/gui/battle/hud_rebel/nameplates"))
    layer_dir.mkdir(parents=True, exist_ok=True)
    nameplate_dir.mkdir(parents=True, exist_ok=True)

    w, h = PORTRAIT_V3_SIZE
    outer = [(86, 36), (261, 33), (348, 103), (312, 279), (88, 292), (15, 166)]
    inner = PORTRAIT_V3_WINDOW
    accent = (72, 232, 255)
    violet = (154, 43, 255)

    back = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(back)
    shadow = [(x + 8, y + 9) for x, y in outer]
    draw.polygon(shadow, fill=(0, 0, 0, 135))
    draw.polygon(outer, fill=(6, 7, 11, 230))
    draw.polygon([(104, 56), (245, 54), (318, 111), (286, 250), (104, 268), (40, 154)], fill=(16, 17, 22, 235))
    draw.polygon([(112, 62), (240, 61), (297, 108), (263, 226), (111, 241), (62, 153)], fill=(1, 3, 7, 228))
    draw.polygon([(88, 36), (261, 33), (330, 88), (308, 105), (250, 56), (106, 59)], fill=(255, 255, 255, 32))
    back.alpha_composite(draw_poly_glow(PORTRAIT_V3_SIZE, outer, violet, 3))
    back.save(layer_dir / "portrait_v3_layer_01_black_diamond.png")

    trim = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    trim.alpha_composite(draw_poly_glow(PORTRAIT_V3_SIZE, inner, accent, 3))
    draw = ImageDraw.Draw(trim)
    draw.line([(101, 269), (294, 248)], fill=(255, 255, 255, 185), width=2)
    draw.line([(42, 154), (105, 46), (245, 46)], fill=(255, 255, 255, 130), width=2)
    draw.line([(250, 274), (402, 253), (417, 285), (282, 300)], fill=violet + (205,), width=5)
    draw.line([(266, 268), (398, 250)], fill=accent + (185,), width=2)
    trim.save(layer_dir / "portrait_v3_layer_02_cyan_trim.png")

    mask = Image.new("L", PORTRAIT_V3_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(inner, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.45))
    mask.save(layer_dir / "portrait_v3_mask_window.png")

    player_plate = draw_slanted_panel((330, 54), [(2, 48), (18, 8), (292, 3), (326, 36), (314, 50)], (204, 91, 16), (75, 225, 255))
    enemy_plate = ImageOps.mirror(draw_slanted_panel((330, 54), [(2, 48), (18, 8), (292, 3), (326, 36), (314, 50)], (171, 48, 26), (255, 102, 86)))
    player_plate.save(nameplate_dir / "nameplate_player_modern.png")
    enemy_plate.save(nameplate_dir / "nameplate_enemy_modern.png")

    return {
        "back": Path("game/gui/battle/hud_rebel/portrait_layers_v3/portrait_v3_layer_01_black_diamond.png"),
        "trim": Path("game/gui/battle/hud_rebel/portrait_layers_v3/portrait_v3_layer_02_cyan_trim.png"),
        "mask": Path("game/gui/battle/hud_rebel/portrait_layers_v3/portrait_v3_mask_window.png"),
        "nameplate_player": Path("game/gui/battle/hud_rebel/nameplates/nameplate_player_modern.png"),
        "nameplate_enemy": Path("game/gui/battle/hud_rebel/nameplates/nameplate_enemy_modern.png"),
    }


def save_v2_layers() -> dict[str, Path]:
    layer_dir = repo_path(Path("game/gui/battle/hud_rebel/portrait_layers_v2"))
    layer_dir.mkdir(parents=True, exist_ok=True)

    w, h = PORTRAIT_V2_SIZE
    outer = [(45, 88), (113, 38), (264, 34), (355, 96), (318, 276), (89, 292), (20, 168)]
    inner = PORTRAIT_V2_WINDOW
    connector = [(238, 170), (420, 166), (398, 218), (258, 226)]
    accent = (174, 36, 255)
    cyan = (42, 222, 255)

    back = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(back)
    draw.polygon([(26, 96), (102, 46), (276, 40), (376, 103), (331, 292), (78, 306), (9, 170)], fill=(11, 6, 22, 210))
    draw.polygon(connector, fill=(10, 7, 18, 205))
    back.alpha_composite(draw_poly_glow(PORTRAIT_V2_SIZE, outer, accent, 4))
    back.save(layer_dir / "portrait_v2_layer_01_back_glow.png")

    glass = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glass)
    draw.polygon(outer, fill=(15, 10, 31, 185))
    draw.polygon(connector, fill=(12, 9, 25, 170))
    draw.polygon([(67, 88), (132, 55), (249, 53), (328, 101), (288, 257), (101, 269), (40, 153)], fill=(2, 11, 23, 125))
    draw.polygon([(45, 88), (113, 38), (264, 34), (281, 47), (117, 51), (55, 97)], fill=(255, 255, 255, 34))
    glass.save(layer_dir / "portrait_v2_layer_02_glass_plate.png")

    trim = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    trim.alpha_composite(draw_poly_glow(PORTRAIT_V2_SIZE, inner, cyan, 3))
    draw = ImageDraw.Draw(trim)
    draw.line([(258, 224), (398, 216)], fill=(133, 72, 255, 190), width=4)
    draw.line([(268, 220), (390, 214)], fill=(42, 222, 255, 140), width=2)
    trim.save(layer_dir / "portrait_v2_layer_03_front_trim.png")

    shard = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    shard_points = [(30, 133), (86, 72), (122, 97), (90, 254), (49, 267), (7, 177)]
    shard.alpha_composite(draw_poly_glow(PORTRAIT_V2_SIZE, shard_points, accent, 3))
    draw = ImageDraw.Draw(shard)
    draw.polygon(shard_points, fill=(91, 20, 168, 150))
    for xoff, a in ((0, 160), (18, 105), (34, 80)):
        draw.line([(34 + xoff, 177), (82 + xoff, 101)], fill=(231, 145, 255, a), width=3)
    shard.save(layer_dir / "portrait_v2_layer_04_side_shard.png")

    mask = Image.new("L", PORTRAIT_V2_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.polygon(inner, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.6))
    mask.save(layer_dir / "portrait_v2_mask_window.png")

    return {
        "back": Path("game/gui/battle/hud_rebel/portrait_layers_v2/portrait_v2_layer_01_back_glow.png"),
        "glass": Path("game/gui/battle/hud_rebel/portrait_layers_v2/portrait_v2_layer_02_glass_plate.png"),
        "trim": Path("game/gui/battle/hud_rebel/portrait_layers_v2/portrait_v2_layer_03_front_trim.png"),
        "shard": Path("game/gui/battle/hud_rebel/portrait_layers_v2/portrait_v2_layer_04_side_shard.png"),
        "mask": Path("game/gui/battle/hud_rebel/portrait_layers_v2/portrait_v2_mask_window.png"),
    }


def build_portrait(spec: HeroPortraitSpec) -> Image.Image:
    base = load_rgba(Path("game/gui/battle/hud_rebel/portrait_layers/portrait_layer_01_base_violet.png"))
    inner = load_rgba(Path("game/gui/battle/hud_rebel/portrait_layers/portrait_layer_02_inner_cyan.png"))
    shard = load_rgba(Path("game/gui/battle/hud_rebel/portrait_layers/portrait_layer_03_side_violet_shard.png"))
    mask = portrait_window_mask()

    source = tune_source(trim_transparent(load_rgba(spec.source)), spec.brightness, spec.contrast)
    hero = source.resize(spec.size, Image.LANCZOS)

    hero_layer = Image.new("RGBA", PORTRAIT_SIZE, (0, 0, 0, 0))
    hero_layer.alpha_composite(hero, spec.offset)
    hero_layer = alpha_clip(hero_layer, mask)

    result = Image.new("RGBA", PORTRAIT_SIZE, (0, 0, 0, 0))
    result.alpha_composite(base)
    result.alpha_composite(hero_layer)
    result.alpha_composite(inner)
    result.alpha_composite(shard)
    return result


def save_pair(spec: HeroPortraitSpec) -> None:
    portrait = build_portrait(spec)
    player_output = repo_path(spec.player_output)
    enemy_output = repo_path(spec.enemy_output)
    player_output.parent.mkdir(parents=True, exist_ok=True)
    portrait.save(player_output)
    ImageOps.mirror(portrait).save(enemy_output)


def build_portrait_v2(spec: HeroPortraitV2Spec) -> Image.Image:
    layers = save_v2_layers()
    back = load_rgba(layers["back"])
    glass = load_rgba(layers["glass"])
    trim = load_rgba(layers["trim"])
    shard = load_rgba(layers["shard"])
    mask = Image.open(repo_path(layers["mask"])).convert("L")

    source = tune_source(trim_transparent(load_rgba(spec.source)), spec.brightness, spec.contrast)
    hero = source.resize(spec.size, Image.LANCZOS)
    hero_shadow = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    hero_shadow.alpha_composite(hero, (spec.offset[0] + 5, spec.offset[1] + 8))
    shadow_alpha = hero_shadow.getchannel("A").filter(ImageFilter.GaussianBlur(6))
    hero_shadow = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    hero_shadow.putalpha(shadow_alpha.point(lambda p: int(p * 0.50)))

    hero_layer = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    hero_layer.alpha_composite(hero, spec.offset)
    clipped = alpha_clip(hero_layer, mask)
    # Let hair and shoulders breathe above the frame while keeping the lower body tidy.
    breakout_mask = Image.new("L", PORTRAIT_V2_SIZE, 0)
    draw = ImageDraw.Draw(breakout_mask)
    draw.rectangle((56, 0, 308, 126), fill=255)
    draw.rectangle((66, 126, 294, 258), fill=140)
    breakout_alpha = ImageChops.lighter(clipped.getchannel("A"), ImageChops.multiply(hero_layer.getchannel("A"), breakout_mask))
    hero_layer.putalpha(breakout_alpha)

    result = Image.new("RGBA", PORTRAIT_V2_SIZE, (0, 0, 0, 0))
    result.alpha_composite(back)
    result.alpha_composite(glass)
    result.alpha_composite(hero_shadow)
    result.alpha_composite(hero_layer)
    result.alpha_composite(trim)
    result.alpha_composite(shard)
    return result


def save_pair_v2(spec: HeroPortraitV2Spec) -> None:
    portrait = build_portrait_v2(spec)
    player_output = repo_path(spec.player_output)
    enemy_output = repo_path(spec.enemy_output)
    player_output.parent.mkdir(parents=True, exist_ok=True)
    portrait.save(player_output)
    ImageOps.mirror(portrait).save(enemy_output)


def build_portrait_v3(spec: HeroPortraitV3Spec) -> Image.Image:
    layers = save_v3_ui_assets()
    back = load_rgba(layers["back"])
    trim = load_rgba(layers["trim"])
    mask = Image.open(repo_path(layers["mask"])).convert("L")

    source = tune_source(trim_transparent(load_rgba(spec.source)), spec.brightness, spec.contrast)
    hero = source.resize(spec.size, Image.LANCZOS)

    hero_shadow = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    hero_shadow.alpha_composite(hero, (spec.offset[0] + 5, spec.offset[1] + 8))
    shadow_alpha = hero_shadow.getchannel("A").filter(ImageFilter.GaussianBlur(7))
    hero_shadow = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    hero_shadow.putalpha(shadow_alpha.point(lambda p: int(p * 0.52)))

    hero_layer = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    hero_layer.alpha_composite(hero, spec.offset)
    clipped = alpha_clip(hero_layer, mask)

    breakout_mask = Image.new("L", PORTRAIT_V3_SIZE, 0)
    draw = ImageDraw.Draw(breakout_mask)
    draw.rectangle((72, 0, 310, 128), fill=255)
    draw.rectangle((78, 128, 297, 238), fill=96)
    breakout_alpha = ImageChops.lighter(clipped.getchannel("A"), ImageChops.multiply(hero_layer.getchannel("A"), breakout_mask))
    hero_layer.putalpha(breakout_alpha)

    result = Image.new("RGBA", PORTRAIT_V3_SIZE, (0, 0, 0, 0))
    result.alpha_composite(back)
    result.alpha_composite(hero_shadow)
    result.alpha_composite(hero_layer)
    result.alpha_composite(trim)
    return result


def save_pair_v3(spec: HeroPortraitV3Spec) -> None:
    portrait = build_portrait_v3(spec)
    player_output = repo_path(spec.player_output)
    enemy_output = repo_path(spec.enemy_output)
    player_output.parent.mkdir(parents=True, exist_ok=True)
    portrait.save(player_output)
    ImageOps.mirror(portrait).save(enemy_output)


def build_danny_v2_preview() -> Path:
    portrait_path = DANNY_PHANTOM_V2.player_output
    if not repo_path(portrait_path).exists():
        save_pair_v2(DANNY_PHANTOM_V2)

    out = repo_path(Path("artifacts/hud_portrait_v2_danny_preview.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (760, 250), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 760, 250), fill=(8, 4, 18, 245))

    portrait = load_rgba(portrait_path).resize((258, 198), Image.LANCZOS)
    canvas.alpha_composite(portrait, (0, 18))

    frame = load_rgba(Path("game/gui/battle/hud_rebel/upflare_bars/hp_frame_upflare_player.png"))
    hp = load_rgba(Path("game/gui/battle/hud_rebel/upflare_bars/hp_fill_green_upflare_player.png"))
    bar_scale = (470, 108)
    frame = frame.resize(bar_scale, Image.LANCZOS)
    hp = hp.resize(bar_scale, Image.LANCZOS)
    bar_x, bar_y = 174, 70
    canvas.alpha_composite(frame, (bar_x, bar_y))
    canvas.alpha_composite(hp, (bar_x, bar_y))

    try:
        font_big = None
        font_small = None
    except:
        font_big = None
        font_small = None
    draw.text((220, 28), "Jugador (danny_phantom)", fill=(53, 216, 255, 255), font=font_small)
    draw.text((366, 84), "1000 / 1000", fill=(248, 248, 255, 255), anchor="mm", font=font_big, stroke_width=2, stroke_fill=(36, 16, 51, 255))
    draw.text((213, 178), "EP 15000 / 15000", fill=(87, 207, 255, 255), font=font_small)
    draw.text((438, 178), "EC 1000 / 1000", fill=(255, 194, 74, 255), font=font_small)
    canvas.save(out)
    return out


def build_danny_v3_preview() -> Path:
    portrait_path = DANNY_PHANTOM_V3.player_output
    if not repo_path(portrait_path).exists():
        save_pair_v3(DANNY_PHANTOM_V3)

    save_v3_ui_assets()
    out = repo_path(Path("artifacts/hud_portrait_v3_danny_preview.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (820, 230), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, 820, 230), fill=(74, 16, 68, 255))
    draw.rectangle((410, 0, 820, 230), fill=(83, 25, 20, 245))

    portrait = load_rgba(portrait_path).resize((190, 146), Image.LANCZOS)
    canvas.alpha_composite(portrait, (-7, 5))

    frame = load_rgba(Path("game/gui/battle/hud_rebel/upflare_bars/hp_frame_upflare_player.png")).resize((420, 96), Image.LANCZOS)
    hp = load_rgba(Path("game/gui/battle/hud_rebel/upflare_bars/hp_fill_green_upflare_player.png")).resize((420, 96), Image.LANCZOS)
    canvas.alpha_composite(frame, (86, 45))
    canvas.alpha_composite(hp, (86, 45))

    plate = load_rgba(Path("game/gui/battle/hud_rebel/nameplates/nameplate_player_modern.png")).resize((252, 40), Image.LANCZOS)
    canvas.alpha_composite(plate, (132, 5))

    draw.text((165, 14), "Jugador (danny_phantom)", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(24, 12, 8, 255))
    draw.text((296, 61), "1000 / 1000", fill=(248, 248, 255, 255), anchor="mm", stroke_width=2, stroke_fill=(36, 16, 51, 255))
    draw.text((152, 151), "EP 15000 / 15000", fill=(87, 207, 255, 255))
    draw.text((324, 151), "EC 1000 / 1000", fill=(255, 194, 74, 255))
    canvas.save(out)
    return out


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].strip().lower() == "--v3":
        requested = [arg.strip().lower() for arg in sys.argv[2:] if arg.strip()]
        if not requested:
            requested = sorted(HERO_SPECS_V3.keys())
        unknown = [hero_id for hero_id in requested if hero_id not in HERO_SPECS_V3 and hero_id != "preview"]
        if unknown:
            valid = ", ".join(sorted(HERO_SPECS_V3.keys()) + ["preview"])
            raise SystemExit("Unknown v3 hero ids: {}. Valid ids: {}".format(", ".join(unknown), valid))
        save_v3_ui_assets()
        for hero_id in requested:
            if hero_id == "preview":
                path = build_danny_v3_preview()
                print("Generated HUD rebel v3 preview at {}.".format(path.relative_to(REPO_ROOT)))
            else:
                save_pair_v3(HERO_SPECS_V3[hero_id])
                print("Generated HUD rebel v3 portrait pair for {}.".format(hero_id))
        return

    if len(sys.argv) > 1 and sys.argv[1].strip().lower() == "--v2":
        requested = [arg.strip().lower() for arg in sys.argv[2:] if arg.strip()]
        if not requested:
            requested = sorted(HERO_SPECS_V2.keys())
        unknown = [hero_id for hero_id in requested if hero_id not in HERO_SPECS_V2 and hero_id != "preview"]
        if unknown:
            valid = ", ".join(sorted(HERO_SPECS_V2.keys()) + ["preview"])
            raise SystemExit("Unknown v2 hero ids: {}. Valid ids: {}".format(", ".join(unknown), valid))
        for hero_id in requested:
            if hero_id == "preview":
                path = build_danny_v2_preview()
                print("Generated HUD rebel v2 preview at {}.".format(path.relative_to(REPO_ROOT)))
            else:
                save_pair_v2(HERO_SPECS_V2[hero_id])
                print("Generated HUD rebel v2 portrait pair for {}.".format(hero_id))
        return

    requested = [arg.strip().lower() for arg in sys.argv[1:] if arg.strip()]
    if not requested:
        requested = sorted(HERO_SPECS.keys())

    unknown = [hero_id for hero_id in requested if hero_id not in HERO_SPECS]
    if unknown:
        valid = ", ".join(sorted(HERO_SPECS.keys()))
        raise SystemExit("Unknown hero ids: {}. Valid ids: {}".format(", ".join(unknown), valid))

    for hero_id in requested:
        save_pair(HERO_SPECS[hero_id])
        print("Generated HUD rebel portrait pair for {}.".format(hero_id))


if __name__ == "__main__":
    main()
