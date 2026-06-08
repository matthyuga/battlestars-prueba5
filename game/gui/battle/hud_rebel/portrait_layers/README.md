# HUD Rebel portrait layers

Capas fuente para generar retratos compuestos del HUD rebel.

No usar estas imagenes directamente en pantallas Ren'Py. El juego consume los PNG finales de `game/gui/battle/hud_rebel/portraits`.

Generador actual:

```powershell
python tools\build_hud_rebel_portraits.py
```

Piloto activo:

- Boruto se genera desde `game/images/character/hechos/boruto-portrait-style-01-cel.png`.
- Salidas:
  - `game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png`
  - `game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png`
