from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_SIZE = (360, 300)
PORTRAIT_WINDOW = [(82, 81), (218, 81), (292, 137), (254, 220), (72, 220), (47, 137)]


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


BORUTO = HeroPortraitSpec(
    hero_id="boruto",
    source=Path("game/images/character/hechos/boruto-portrait-style-01-cel.png"),
    player_output=Path("game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png"),
    enemy_output=Path("game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png"),
    size=(198, 233),
    offset=(82, 23),
)


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


def main() -> None:
    save_pair(BORUTO)
    print("Generated HUD rebel portrait pair for Boruto.")


if __name__ == "__main__":
    main()
