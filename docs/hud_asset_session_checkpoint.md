# HUD Assets Session Checkpoint

Este commit deja un checkpoint **solo de documentación** para continuar en una nueva sesión sin perder el contexto.

## Decisiones confirmadas

- El cuadro mostrado por defecto en combate será **`stat`** (HP, Reiatsu y Energía).
- El cuadro **`option`** se mostrará al alternar con el botón de intercambio (swap).
- Cada estilo tendrá dos variantes: `stat` y `option`.

## Estilos confirmados

Los estilos definidos para el HUD son:

1. `carmesi`
2. `fantasy`
3. `grey`
4. `virtual`

## Convención de nombres propuesta para assets

Cuando se suban los PNG al repo, se recomienda esta estructura:

- `game/gui/battle/hud_ai/frames/`
  - `frame_carmesi_stat.png`
  - `frame_carmesi_option.png`
  - `frame_fantasy_stat.png`
  - `frame_fantasy_option.png`
  - `frame_grey_stat.png`
  - `frame_grey_option.png`
  - `frame_virtual_stat.png`
  - `frame_virtual_option.png`

- `game/gui/battle/hud_ai/icons/`
  - `icon_style_picker_arrow_gold.png`
  - `icon_panel_swap_blue.png`

- `game/gui/battle/hud_ai/thumbnails/`
  - `thumb_carmesi.png`
  - `thumb_fantasy.png`
  - `thumb_grey.png`
  - `thumb_virtual.png`

## Próximo paso en la nueva sesión

1. Subir assets a las rutas anteriores.
2. Generar thumbnails (si no vienen listos).
3. Conectar selector de estilo (flechita superior derecha) por unidad.
4. Conectar swap `stat`/`option` (botón azul inferior derecha) por unidad.
