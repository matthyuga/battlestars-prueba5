# Plan de implementación visual HUD IA (arranque)

Este documento transforma el checkpoint de assets en un **plan ejecutable** para iniciar la implementación visual del HUD IA.

## 0) Estado actual y criterio de inicio

Con lo ya acordado se puede comenzar la implementación.
No hace falta re-negociar estilos ni naming base.

Ya definido:
- 4 estilos (`carmesi`, `fantasy`, `grey`, `virtual`).
- 2 variantes por estilo (`stat`, `option`).
- portraits por personaje (`*_head`, `*_full`).
- iconos de control y posición por panel:
  - flechita de estilo (`icon_style_picker_arrow_gold.png`) **abajo izquierda**.
  - swap `stat/option` (`icon_panel_swap_blue.png`) **abajo derecha**.
  - cerrar panel (`icon_panel_close_red.png`) **arriba derecha**.

## 1) Pre-flight de assets (bloqueante corto)

Antes de tocar screens, validar:

1. Todos los PNG presentes en rutas finales:
   - `game/gui/battle/hud_ai/frames/`
   - `game/gui/battle/hud_ai/portraits/`
   - `game/gui/battle/hud_ai/icons/`
2. Resolución/ratio consistente por familia:
   - frames (`*_stat` y `*_option`) con mismo canvas por estilo.
   - portraits `head` y `full` por personaje.
3. Transparencias correctas (alpha limpio, sin fondos sólidos).

Si algo falta, la integración igual puede arrancar con fallback textual, pero lo ideal es cerrar este punto primero.

## 2) Fase 1 — Wiring mínimo en layout (sin romper lógica)

Objetivo: conectar imágenes al HUD sin tocar reglas IA.

1. Crear tabla de rutas de assets (diccionarios) en un módulo de layout visual.
2. Definir estado visual por unidad IA:
   - `hud_style_by_unit[unit_key]` (carmesi/fantasy/grey/virtual).
   - `hud_panel_mode_by_unit[unit_key]` (stat/option).
3. Resolver frame activo por unidad:
   - `frame_path = frame_{style}_{mode}.png`.
4. Render base:
   - cuadro superior: portrait `*_head`.
   - cuadro inferior:
     - `stat`: HP/Reiatsu/Energía.
     - `option`: 6 controles tácticos ya existentes.

## 3) Fase 2 — Controles visuales (flechita, swap y cerrar)

1. Botón flecha (`icon_style_picker_arrow_gold.png`) en esquina **abajo izquierda**:
   - ciclo por estilos (orden fijo sugerido: carmesi → fantasy → grey → virtual).
2. Botón swap azul (`icon_panel_swap_blue.png`) en esquina **abajo derecha**:
   - alterna `stat` ↔ `option` por unidad.
3. Botón cerrar (`icon_panel_close_red.png`) en esquina **arriba derecha**:
   - colapsa el cuadro y deja solo fichas compactas.
4. Persistencia opcional:
   - guardar elección visual por unidad en `persistent`.

## 4) Fase 3 — Portrait routing por personaje

1. Definir map de personaje a archivos:
   - `portrait_<char>_head.png`
   - `portrait_<char>_full.png`
   - `portrait_<char>_token.png` (ficha compacta, opcional)
2. Fallback cuando falte portrait:
   - `token -> head -> full -> placeholder` en colapsado.
   - `head -> full -> token -> placeholder` en expandido.
3. Regla recomendada:
   - `token` en ficha compacta.
   - `head` en ventana superior.
   - `full` reservado para expansiones/variantes del panel de estado.

## 5) Fase 4 — Ajuste fino visual

1. Anchors/offsets por estilo (porque los marcos no suelen tener idénticos márgenes internos).
2. Tipografía y contraste por estilo (legibilidad).
3. Escalado adaptativo para 1v1, 2v2 y composiciones manuales asimétricas (2v1/1v2) sobre runtime de unidades.
4. Perfil de layout por modo/cantidad de unidades visibles (panel/token/espaciado/tamaño de texto).
5. Validación de overlap con overlays ya existentes.

## Cobertura transversal de modos (aplica a todas las fases)

- La implementación de HUD por unidades no debe quedar amarrada al string de modo (`1v1`/`2v2`), sino al runtime de unidades disponible.
- Criterio de compatibilidad mínimo por fase: `1v1`, `2v2` y composiciones manuales asimétricas (`2v1`, `1v2`) usando la misma capa de unidades.
- Las reglas de controles visuales (`style`, `swap`, `close`) deben operar por `unit_key` para no contaminar otras unidades ni otros lados.

## 6) QA mínimo por checklist

1. Swap funciona por unidad y no cambia otras unidades.
2. Cambio de estilo funciona por unidad y conserva modo (`stat`/`option`).
3. Cierre (`X`) colapsa solo el panel seleccionado y no rompe focus.
4. `stat` muestra datos correctos del actor activo.
5. `option` dispara acciones existentes sin romper lógica IA.
6. Sin artefactos visuales al cambiar turno, KO, o replace de screen.

## 7) Orden recomendado de implementación (rápido)

1. Wiring de frame dinámico.
2. Swap `stat/option`.
3. Style picker.
4. Portrait routing.
5. Offsets y polish.
6. Persistencia (si aplica).

## 8) ¿Falta algo para arrancar?

No es bloqueante, pero ayuda mucho tener definido:

- Tamaño objetivo de render (ancho/alto final en pantalla) para cada panel.
- Margen interno útil de cada frame (zona segura para texto/portrait).
- Convención definitiva de `char_id` ↔ nombre de archivo para portraits.
- Decisión de persistencia: sesión actual vs `persistent`.

Con eso, ya se puede entrar directamente a implementación.


### Nota de compatibilidad de nombres (Fase 3)

- Soportar aliases de `char_id` para portraits (ej: `neliel -> nel`, `tier_harribel -> harribel`) evita roturas entre datasets y assets.


## 9) Estado de cierre actual

- Fase 1: completa (wiring base por unidad).
- Fase 2: completa (controles style/swap/close por `unit_key`).
- Fase 3: completa (portrait routing con aliases y fallback por estado).
- Fase 4: completa (layout adaptativo por modo/cantidad de unidades).
- Fase 5: completa a nivel técnico de UI/runtime.

Pendiente para cierre absoluto de producción:
- smoke manual en combate real por modo (`1v1`, `2v2`, `2v1`, `1v2`) con assets finales.
- ajustes finos de offsets por estilo tras validar arte final en juego.
