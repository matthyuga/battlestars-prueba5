# Plan de análisis: refactor visual HUD IA (sin tocar lógica)

## Objetivo de esta fase
Diseñar un refactor **solo visual** del HUD de IA para:
- separar claramente panel táctico por unidad y panel de estado/soporte,
- definir estructura de carpetas para assets,
- preparar un layout modular con offsets por componente,
- mantener intacta la lógica de funciones ya existentes.

> Esta fase no implementa comportamiento nuevo; define arquitectura visual y plan de ejecución.

---

## 1) Estado actual (mapa funcional)

### Capa visual principal
- `game/4/04A_AI_DIFFICULTY_HUD_SCREENV2.rpy`
  - hoy concentra casi toda la composición visual del panel.

### Núcleo lógico (mantener estable)
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_BASEV2.rpy`
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_DEFENSEV2.rpy`
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_UNIT_PROFILEV1.rpy`

Conclusión: el mejor camino es **modularizar screen/layout + assets**, sin invadir core.

---

## 2) Modelo visual propuesto (dos cuadros + nameplate)

## Cuadro 1 (control táctico por unidad)
Debe contener exactamente 6 controles:
1. Forzar ofensiva (unidad)
2. Concat ofensiva (unidad)
3. Forzar defensiva (unidad)
4. Concat defensiva (unidad)
5. Focus (unidad)
6. Target (unidad)

Y al pie: **nombre del personaje** (nameplate).

## Cuadro 2 (estado de unidad)
Debe contener:
- retrato full-body (o busto según variante),
- HP,
- Reiatsu,
- Energía,
- (futuro) estados y stats extra: fuerza/agilidad/envenenado/anulado/etc.

---

## 3) Estructura de carpetas recomendada

Ruta base recomendada:

`game/gui/battle/hud_ai/`

Subcarpetas:

- `frames/`
  - marcos de panel táctico, panel estado y nameplate.
- `portraits/`
  - retratos UI-ready por personaje (headshot/fullbody).
- `icons/`
  - iconos de categorías (target/focus/ofensiva/defensiva/concat/estados).
- `styles/` *(opcional)*
  - overlays, placas de texto, fondos de fila.

### Nomenclatura sugerida (funcional, no estética)

#### Frames
- `ai_hud_panel_tactical_nature.png`
- `ai_hud_panel_stats_nature.png`
- `ai_hud_nameplate_nature.png`

#### Portraits (pares por personaje)
- `portrait_grimmjow_head.png`
- `portrait_grimmjow_full.png`
- `portrait_harribel_head.png`
- `portrait_harribel_full.png`
- `portrait_nel_head.png`
- `portrait_nel_full.png`
- `portrait_hollow_head.png`
- `portrait_hollow_full.png`

#### Icons
- `icon_target.png`
- `icon_focus.png`
- `icon_offense_force.png`
- `icon_offense_concat.png`
- `icon_defense_force.png`
- `icon_defense_concat.png`

---

## 4) Separación de scripts recomendada

Crear:

1. `game/4/04A_AI_DIFFICULTY_HUD_LAYOUT.rpy`
   - rutas de assets,
   - posiciones globales,
   - rectángulos internos por panel,
   - tipografías/tamaños/spacing,
   - offsets finos.

2. `game/4/04A_AI_DIFFICULTY_HUD_COMPONENTS.rpy`
   - `screen ai_hud_unit_tactical_panel(...)`
   - `screen ai_hud_unit_stats_panel(...)`
   - `screen ai_hud_nameplate(...)`
   - `screen ai_hud_option_row(...)`

3. Mantener `game/4/04A_AI_DIFFICULTY_HUD_SCREENV2.rpy`
   - como ensamblador (llama `use ...`),
   - sin hardcode masivo de layout.

---

## 5) Contrato de no-regresión funcional

Durante el refactor visual, estas funciones deben seguir funcionando igual:
- `ai_cycle_level`
- `ai_toggle_save`
- `ai_ui_cycle_target_rule`
- `ai_ui_cycle_offense_mode`
- `ai_ui_cycle_offense_concat_rule`
- `ai_ui_cycle_defense_mode`
- `ai_ui_cycle_concat_rule`
- `ai_ui_cycle_focus_rule`

Regla: cambiar `style/screen/posiciones/assets`, no semántica de acciones.

---

## 6) Orden de implementación sugerido (fases)

## Fase A — Preparación de assets
- Crear carpetas nuevas en `game/gui/battle/hud_ai/`.
- Mover/renombrar PNG con nomenclatura funcional.

## Fase B — Layout central
- Crear `04A_AI_DIFFICULTY_HUD_LAYOUT.rpy` con constantes y rects.

## Fase C — Componentes
- Crear `04A_AI_DIFFICULTY_HUD_COMPONENTS.rpy` y encapsular bloques reutilizables.

## Fase D — Ensamblado final
- Reducir `04A_AI_DIFFICULTY_HUD_SCREENV2.rpy` a composición con `use`.

## Fase E — Pulido
- Ajustes finos de pixeles (padding/yoffset/line gap) por panel,
- pruebas visuales en 1v1 y 2v2.

---

## 7) Riesgos y mitigaciones

- **Riesgo:** romper bindings de acciones al mover botones.
  - **Mitigación:** conservar `action Function(...)` original en cada fila.

- **Riesgo:** desalineación entre retratos de distinto aspecto.
  - **Mitigación:** usar rect de retrato fijo + escala por personaje en layout.

- **Riesgo:** screen monolítico difícil de mantener.
  - **Mitigación:** components + archivo layout central.

---

## 8) Checklist de validación visual (cuando se implemente)

- Cuadro 1 muestra 6 controles tácticos correctos por unidad.
- Cuadro 2 muestra retrato + HP/Reiatsu/Energía sin clipping.
- Nameplate inferior mantiene legibilidad en todos los personajes.
- 1v1 y 2v2 no superponen paneles.
- Botones responden y actualizan textos de estado sin cambio de lógica.

---

## 9) Siguiente paso recomendado

Antes de codificar el refactor:
1. confirmar nombres finales de PNG,
2. confirmar tamaño objetivo de cada frame (ancho/alto),
3. confirmar si panel táctico y panel de estado van lado a lado o apilados,
4. recién después implementar Fase A→E.
