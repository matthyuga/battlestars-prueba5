# HUD Rebel up-flare HP bars

Assets del modo experimental `upflare` para la barra HP.

El HUD anterior no fue borrado. Sigue en:

- `game/gui/battle/hud_rebel/bars`
- `game/gui/battle/hud_rebel/frames`

Selector de estilo:

```renpy
default bs_battle_hud_rebel_style = "upflare"
```

Para volver temporalmente al HUD anterior, cambiar el valor a:

```renpy
default bs_battle_hud_rebel_style = "legacy"
```

Generador:

```powershell
python tools\build_hud_rebel_upflare_bars.py
```

Logica visual:

- `hp_frame_upflare_*`: marco/sombra/resto vacio.
- `hp_fill_green_upflare_*`: HP actual.
- `hp_fill_damage_red_upflare_*`: dano pendiente/fake damage.
- `*_enemy.png`: version espejada para enemigo.
- `steps/player` y `steps/enemy`: pasos 000-100 ya recortados en PNG.
  El HUD usa estos pasos para evitar `im.Crop` dinamico en Ren'Py 7.4.9,
  que puede romper con `subsurface size must be non-negative` durante empates,
  HP en cero o cambios de pantalla.
