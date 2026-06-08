from __future__ import annotations

from pathlib import Path
import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "game/gui/battle/hud_rebel/upflare_bars"

BAR_SIZE = (420, 96)
STEP_DIR = OUT_DIR / "steps"


def q(points: list[tuple[float, float]]) -> list[tuple[int, int]]:
    return [(int(round(x)), int(round(y))) for x, y in points]


def upflare_points(
    x: float,
    y: float,
    w: float,
    h0: float,
    h1: float,
    rise: float,
    samples: int = 44,
    nose: float = 22.0,
) -> list[tuple[float, float]]:
    top: list[tuple[float, float]] = []
    bottom: list[tuple[float, float]] = []
    for i in range(samples + 1):
        t = i / float(samples)
        px = x + w * t
        curve = rise * (t ** 1.75)
        thick = h0 + (h1 - h0) * (t ** 1.35)
        crown = math.sin(t * math.pi) * 3.5
        top.append((px, y - curve - crown - thick * 0.50))
        bottom.append((px - nose * t, y - curve + thick * 0.50))
    bottom.reverse()
    return top + bottom


def empty_layer() -> Image.Image:
    return Image.new("RGBA", BAR_SIZE, (0, 0, 0, 0))


def gradient(size: tuple[int, int], left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> Image.Image:
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    px = out.load()
    w, h = size
    for x in range(w):
        t = x / float(max(1, w - 1))
        col = tuple(int(left[i] * (1.0 - t) + right[i] * t) for i in range(4))
        for y in range(h):
            px[x, y] = col
    return out


def polygon_mask(points: list[tuple[float, float]], blur: float = 0.55) -> Image.Image:
    mask = Image.new("L", BAR_SIZE, 0)
    ImageDraw.Draw(mask).polygon(q(points), fill=255)
    if blur:
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return mask


def apply_mask(image: Image.Image, mask: Image.Image) -> Image.Image:
    out = image.copy()
    out.putalpha(ImageChops.multiply(out.getchannel("A"), mask))
    return out


def glow_from_mask(mask: Image.Image, color: tuple[int, int, int, int], blur: float = 7.0) -> Image.Image:
    glow = Image.new("RGBA", BAR_SIZE, color)
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(blur)))
    return glow


def draw_poly(
    image: Image.Image,
    points: list[tuple[float, float]],
    fill: tuple[int, int, int, int] | None = None,
    outline: tuple[int, int, int, int] | None = None,
    width: int = 2,
    glow: tuple[int, int, int, int] | None = None,
) -> None:
    layer = empty_layer()
    draw = ImageDraw.Draw(layer)
    pts = q(points)
    if fill:
        draw.polygon(pts, fill=fill)
    if outline:
        draw.line(pts + [pts[0]], fill=outline, width=width, joint="curve")
    if glow:
        image.alpha_composite(glow_from_mask(layer.getchannel("A"), glow, 5.0))
    image.alpha_composite(layer)


def build_frame() -> Image.Image:
    image = empty_layer()
    x, y, w = 22, 78, 374
    h0, h1, rise = 11, 42, 30

    base = [(px + 18, py + 20) for px, py in upflare_points(x + 6, y + 2, w * 0.94, h0 * 0.78, h1 * 0.54, rise * 0.52, nose=16)]
    draw_poly(image, base, fill=(9, 10, 11, 226), outline=(36, 36, 38, 180), width=1)

    shell = upflare_points(x, y, w, h0 + 8, h1 + 14, rise, nose=22)
    draw_poly(image, shell, fill=(33, 16, 44, 195), outline=(228, 226, 250, 230), width=2, glow=(145, 42, 255, 62))
    return image


def build_fill(left: tuple[int, int, int, int], right: tuple[int, int, int, int], glow: tuple[int, int, int, int]) -> Image.Image:
    image = empty_layer()
    x, y, w = 22, 78, 374
    h0, h1, rise = 11, 42, 30
    fill_pts = upflare_points(x, y, w, h0, h1, rise, nose=20)
    mask = polygon_mask(fill_pts)
    image.alpha_composite(glow_from_mask(mask, glow, 6.0))
    image.alpha_composite(apply_mask(gradient(BAR_SIZE, left, right), mask))
    return image


def save_pair(name: str, image: Image.Image) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUT_DIR / f"{name}_player.png")
    ImageOps.mirror(image).save(OUT_DIR / f"{name}_enemy.png")


def save_steps(name: str, image: Image.Image) -> None:
    w, h = image.size
    player_dir = STEP_DIR / "player"
    enemy_dir = STEP_DIR / "enemy"
    player_dir.mkdir(parents=True, exist_ok=True)
    enemy_dir.mkdir(parents=True, exist_ok=True)

    enemy_image = ImageOps.mirror(image)
    for pct in range(101):
        visible_w = int(round(w * pct / 100.0))

        player_step = Image.new("RGBA", image.size, (0, 0, 0, 0))
        if visible_w > 0:
            player_step.alpha_composite(image.crop((0, 0, visible_w, h)), (0, 0))
        player_step.save(player_dir / f"{name}_{pct:03d}.png")

        enemy_step = Image.new("RGBA", image.size, (0, 0, 0, 0))
        if visible_w > 0:
            left = w - visible_w
            enemy_step.alpha_composite(enemy_image.crop((left, 0, w, h)), (left, 0))
        enemy_step.save(enemy_dir / f"{name}_{pct:03d}.png")


def main() -> None:
    frame = build_frame()
    green_fill = build_fill((0, 166, 12, 255), (40, 255, 58, 255), (0, 255, 52, 82))
    red_fill = build_fill((150, 12, 16, 245), (255, 46, 48, 255), (255, 24, 32, 76))

    save_pair("hp_frame_upflare", frame)
    save_pair("hp_fill_green_upflare", green_fill)
    save_pair("hp_fill_damage_red_upflare", red_fill)
    save_steps("hp_fill_green_upflare", green_fill)
    save_steps("hp_fill_damage_red_upflare", red_fill)
    print("Generated aggressive up-flare HUD rebel HP bars and safe percent steps.")


if __name__ == "__main__":
    main()
