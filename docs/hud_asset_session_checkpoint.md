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
  - `icon_panel_close_red.png`

- `game/gui/battle/hud_ai/thumbnails/`
  - `thumb_carmesi.png`
  - `thumb_fantasy.png`
  - `thumb_grey.png`
  - `thumb_virtual.png`

## Próximo paso en la nueva sesión

1. Subir assets a las rutas anteriores.
2. Generar thumbnails (si no vienen listos).
3. Conectar selector de estilo (flechita **inferior izquierda**) por unidad.
4. Conectar swap `stat`/`option` (botón azul **inferior derecha**) por unidad.
5. Conectar cierre de panel (cruz roja **superior derecha**) para volver a vista de fichas.


## Assets recibidos (preview) y mapeo confirmado

Con base en los cuadros compartidos en esta sesión, el mapeo visual por estilo queda:

- `carmesi`
  - `stat`: variante de panel inferior liso/gradiente.
  - `option`: variante de panel inferior con filas/botones.
- `fantasy`
  - `stat`: variante de panel inferior liso/ambiental.
  - `option`: variante de panel inferior con filas/botones.
- `grey`
  - `stat`: variante de panel inferior liso/neblina.
  - `option`: variante de panel inferior con filas/botones.
- `virtual`
  - `stat`: variante de panel inferior liso con grilla sutil.
  - `option`: variante de panel inferior con filas/botones.

### Convención final sugerida de archivos (lista operativa)

- `game/gui/battle/hud_ai/frames/frame_carmesi_stat.png`
- `game/gui/battle/hud_ai/frames/frame_carmesi_option.png`
- `game/gui/battle/hud_ai/frames/frame_fantasy_stat.png`
- `game/gui/battle/hud_ai/frames/frame_fantasy_option.png`
- `game/gui/battle/hud_ai/frames/frame_grey_stat.png`
- `game/gui/battle/hud_ai/frames/frame_grey_option.png`
- `game/gui/battle/hud_ai/frames/frame_virtual_stat.png`
- `game/gui/battle/hud_ai/frames/frame_virtual_option.png`

> Nota: este checkpoint documenta el mapeo visual acordado; la integración en `screen` (selector por unidad + swap stat/option + iconos) se conecta en el siguiente paso de implementación.


## Assets recibidos (personajes + controles) y nombres recomendados

Se recibieron retratos **head** y **full-body** para personajes del HUD IA, más los dos iconos de control de panel.

### Portraits por personaje (operativo)

- Grimmjow
  - `game/gui/battle/hud_ai/portraits/portrait_grimmjow_head.png`
  - `game/gui/battle/hud_ai/portraits/portrait_grimmjow_full.png`
- Harribel
  - `game/gui/battle/hud_ai/portraits/portrait_harribel_head.png`
  - `game/gui/battle/hud_ai/portraits/portrait_harribel_full.png`
- Hollow
  - `game/gui/battle/hud_ai/portraits/portrait_hollow_head.png`
  - `game/gui/battle/hud_ai/portraits/portrait_hollow_full.png`
- Nel
  - `game/gui/battle/hud_ai/portraits/portrait_nel_head.png`
  - `game/gui/battle/hud_ai/portraits/portrait_nel_full.png`

### Iconos de navegación del HUD

- Flecha para cambio de estilo de cuadro:
  - `game/gui/battle/hud_ai/icons/icon_style_picker_arrow_gold.png`
- Botón azul para swap `stat`/`option`:
  - `game/gui/battle/hud_ai/icons/icon_panel_swap_blue.png`
- Botón rojo para cerrar cuadro expandido:
  - `game/gui/battle/hud_ai/icons/icon_panel_close_red.png`

### Regla de uso en integración

- `icon_style_picker_arrow_gold.png` se usa para ciclar estilo visual por unidad IA.
- `icon_panel_swap_blue.png` se usa para alternar panel por unidad entre `stat` y `option`.
- `icon_panel_close_red.png` se usa para cerrar panel expandido y dejar solo fichas.
- Retratos `*_head` priorizados para cuadro superior; `*_full` para variantes/expansión de cuadro de estado.

### Posicionamiento validado en preview

- `icon_style_picker_arrow_gold.png` -> esquina **abajo izquierda** del panel.
- `icon_panel_swap_blue.png` -> esquina **abajo derecha** del panel.
- `icon_panel_close_red.png` -> esquina **arriba derecha** del panel.
