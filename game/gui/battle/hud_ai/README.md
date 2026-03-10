# HUD AI assets

Estructura base creada para integrar assets visuales del HUD IA.

- `frames/` → marcos `frame_<style>_<mode>.png`
- `portraits/` → retratos `portrait_<char_id>_<head|full>.png`
- `icons/` → controles visuales (`icon_style_picker_arrow_gold.png`, `icon_panel_swap_blue.png`, `icon_panel_close_red.png`)
- `thumbnails/` → miniaturas por estilo

Posiciones UI acordadas para el panel expandido:
- `icon_style_picker_arrow_gold.png` → abajo izquierda
- `icon_panel_swap_blue.png` → abajo derecha
- `icon_panel_close_red.png` → arriba derecha


Panel secundario de opciones IA (opcional):
- `frames/frame_secondary_options.png` (genérico)
- `frames/frame_<style>_secondary_options.png` (por estilo, tiene prioridad sobre genérico)
