# Auditoría de Registro de Combate (análisis + propuesta de orden)

## Objetivo

Analizar el estado actual del **registro de combate** (texto, formato, consistencia, colores, debug) para preparar una fase de depuración visual/UX, sin cambiar lógica de daño todavía.

---

## 1) Mapa actual: de dónde salen los textos del registro

### 1.1 Núcleo de render del log

- El log se guarda en `battle_log` y se imprime en `screen battle_log_screen`.
- Entrada principal: `battle_log_add(text, color=None, tech_key=None)`.
- Encabezados de fase: `battle_log_phase(title)`.

Archivo:
- `game/03_VISUAL_SYSTEM_BASICV2.rpy`

### 1.2 Formateadores y estilos “centrales”

- Paleta central base: `S.PALETTE` (`white`, `red`, `blue`, `purple`, `gold`, `orange`, `pink`, `effect`, `cyan`, etc.).
- Helpers `fmt_*`, `log_focus_unified`, `log_potenciar_unified`, `log_defense_*`, `log_operation`, `log_total`.

Archivo:
- `game/00_battle_styleV2.rpy`

### 1.3 Sistema de “operación” defensiva

- Acumula líneas vía `operation_add(...)` y vuelca con `operation_dump_to_battle_log()`.
- Hay dos implementaciones coexistiendo (una moderna y otra legacy), con firmas distintas.

Archivos:
- `game/00_GLOBALS_OPERATION_SYSTEMV2.rpy`
- `game/00_GLOBALS_SYSTEMV3.rpy`

### 1.4 Productores de texto en runtime (más ruido/inconsistencias)

- Ofensiva jugador: `04C_OFFENSIVE_ACTIONSV2.rpy`.
- Fórmula ofensiva final: `04C_OFFENSIVE_FORMULAV3.rpy`.
- Defensiva jugador: `04D_DEFENSIVE_ACTIONS.rpy` + `04D_DEFENSIVE_OPERATION.rpy`.
- Ofensiva IA/enemigo: `04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy` + `04D_AI_EXECUTIONV5.rpy`.
- Defensa reactiva IA: `04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy`.

---

## 2) Inconsistencias detectadas (las que reportaste + adicionales)

## 2.1 “Concentrar” en defensa muestra “Próximo ataque ×2”

### Hallazgo
`log_focus_unified` siempre devuelve texto orientado a ataque (“Próximo ataque ×2”), sin usar su parámetro `mode`.

- Definición actual: `game/00_battle_styleV2.rpy`.
- En defensa IA se llama `S.log_focus_unified("defense")`, pero texto sigue siendo de ataque:
  - `game/4/04D_AI_EXECUTIONV5.rpy`
  - `game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy`

### Impacto
No altera cálculo, pero comunica mal al jugador (semántica invertida en contexto defensivo).

---

## 2.2 “Defensa Extra” con formato duplicado tipo `500×(1.000)×2(1.000)`

### Hallazgo
En defensiva jugador se arma `blk_text(base, final)` como string intermedio (`"base×(final)"`), y luego se lo vuelve a pasar a `log_defense_extra(base, final)` que ya intenta reconstruir multiplicador si `base != final`.

Resultado: doble composición visual del multiplicador.

Archivo clave:
- `game/4/j/04D_DEFENSIVE_ACTIONS.rpy` (`blk_text` y uso en `log_defense_extra`/`log_defense_reducer`/`log_defense_reflect`).

### Impacto
Resultado numérico correcto, representación confusa/inconsistente.

---

## 2.3 Diferencia de estilo entre P (jugador) y E (enemigo/IA)

### Hallazgo
- Jugador usa más los helpers de `00_battle_styleV2`.
- Enemigo/IA mezcla helpers + strings hardcode + tags `{color=...}` directos.
- En ofensiva IA aparece `Daño total: ... defendibles` con estilo distinto al `log_total(...)` del jugador.

Archivos con mezcla:
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
- `game/4/04D_AI_EXECUTIONV5.rpy`

### Impacto
Mismo fenómeno de juego se ve distinto según actor/flujo (P vs E).

---

## 2.4 Debug visible dentro del log principal (ruido)

### Hallazgo
Se inyectan muchas líneas `[DEBUG] ...` directamente en `battle_log_add` durante turnos, transiciones y daño en cola.

Ejemplos:
- `TURN_ADVANCE`, `TURN_START`, `POPUP_TRANSITION`, `OFFENSE_CANCELLED`, `DEFENSE_RESOLVE`, etc.
- Además, “Daño entrante en cola 2v2 → ...” entra siempre al mismo log visual.

Archivos:
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
- `game/06F_BATTLE_TURN_CHANGE.RPY`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`
- `game/4/04D_AI_EXECUTIONV5.rpy`

### Impacto
El log de jugador mezcla “narrativa de combate” con “telemetría de ingeniería”.

---

## 2.5 Coexistencia de dos sistemas de operación

### Hallazgo
- `00_GLOBALS_OPERATION_SYSTEMV2.rpy`: `operation_add(text, border=None)` y estructura dict.
- `00_GLOBALS_SYSTEMV3.rpy`: `operation_add(text, color=None)` y tupla `(text, color)`.

Aunque puede funcionar por orden de init/override, arquitectónicamente es frágil y propenso a inconsistencias.

### Impacto
Riesgo de formatos distintos o pérdida de metadatos (border/color) según quién haya quedado activo.

---

## 3) Fuentes de color actuales (y por qué se ven “desordenadas”)

## 3.1 Fuente A: paleta semántica central (recomendada)

- `S.PALETTE` en `00_battle_styleV2.rpy`.
- Tokens semánticos: `red`, `blue`, `gold`, `purple`, etc.

## 3.2 Fuente B: sync de operación (`OP_COLOR_*`)

- `op_colors_sync()` en `00_GLOBALS_OPERATION_COLORSV2.rpy`.
- Intenta mapear colores de operación a `S.PALETTE`.

## 3.3 Fuente C: defaults/fallback en Visual System

- `battle_log_add` auto-colorea por tipo técnica si no se pasa color.
- `battle_log_phase` define colores de header por texto (`OFENSIVO`, `DEFENSIVO`, nombre actor, etc.).

## 3.4 Fuente D: hardcode por módulo

Muchos módulos aún inyectan hex directos (`#80DEEA`, `#B39DDB`, `#FF66CC`, etc.).

Muestra rápida de densidad (hardcoded):
- `00_battle_styleV2`: 15 apariciones.
- `03_VISUAL_SYSTEM_BASICV2`: 24.
- `04C_OFFENSIVE_ACTIONSV2`: 25.
- `04D_BATTLE_TURN_ENEMY_OFENSIVEV5`: 24.
- `04D_AI_EXECUTIONV5`: 16.
- `04D_AI_REACTIVE_DEFENSE_ENGINEV2`: 9.

**Conclusión:** hay tokenización parcial; la práctica real sigue siendo híbrida (token + hex directo).

---

## 4) Inventario de datos visibles hoy en registro

## 4.1 Fase/actor
- Inicio de combate.
- Turno ofensivo/defensivo con nombre y (en 2v2) tag de slot.

## 4.2 Líneas de técnica
- Ofensivas: daño por técnica, costos `(Reiatsu / Ene)`, efectos especiales (extra acción, no-atk, reducer).
- Defensivas: bloqueos, reducción %, reflect %, potenciar/concentrar.

## 4.3 Operación ofensiva
- Suma de partes (`a + b + c...`).
- Total de daño.
- A veces texto de “defendibles/directos” en flujo enemigo.

## 4.4 Operación defensiva
- Daño enemigo efectivo tras reductores.
- Defensas sumadas y debuff de defensa aplicado.
- Daño neto recibido.
- HP antes/después.
- (si aplica) daño directo pendiente y reflect.

## 4.5 Estado diferido 2v2
- Daño en cola por unidad objetivo (`Daño entrante en cola 2v2`).

## 4.6 Debug técnico
- Eventos de transición y routing.
- Contexto de actor/target/sources.
- Mensajes de hardening/errores no fatales.

---

## 5) Propuesta de reorganización (sin romper lógica)

## Fase A — Homogeneidad textual (rápida y de bajo riesgo)

1. Definir **plantillas canónicas** por tipo de evento:
   - `phase_header`
   - `tech_offensive`
   - `tech_defensive`
   - `operation_offensive`
   - `operation_defensive`
   - `total_damage`
2. Corregir semántica de focus en defensa (texto “Próxima defensa ×2”).
3. Corregir `blk_text`/`log_defense_*` para evitar doble multiplicador.
4. Estandarizar separadores (`→`, `·`, paréntesis, espacios, `x2/×2`).

## Fase B — Colores semánticos únicos

1. Crear mapa de color semántico de log (ejemplo):
   - `log.phase.offense`, `log.phase.defense`
   - `log.tech.offense`, `log.tech.defense`, `log.tech.special`
   - `log.operation.title`, `log.operation.value`, `log.operation.total`
   - `log.meta.queue`, `log.meta.warning`, `log.meta.debug`
2. Prohibir nuevos hex directos en módulos de gameplay (solo tokens).
3. Mantener hardcodes solo en capa de tema/skin.

## Fase C — Separación “combate” vs “debug”

1. Agregar flag store `ui_show_battle_debug_log = False`.
2. `battle_log_add_debug(...)` separado de `battle_log_add(...)`.
3. Render condicional de filas debug en `battle_log_screen`.

---

## 6) Propuesta específica para lo que pediste (botones)

## 6.1 Panel debug (Focus/Reflect)

Estado actual:
- Ya es ocultable con tecla `T`, pero `battle_start` lo muestra siempre (`show screen debug_battle_identity`).

Propuesta:
- No auto-mostrar en start.
- Añadir botón pequeño en HUD/log (ej. `🛠 Debug`) que togglee `debug_identity_panel`.
- Mantener atajo `T` como alternativo.

## 6.2 “Daño entrante en cola”

Propuesta:
- Guardar snapshot en variable (ej. `ui_incoming_queue_summary`).
- Mostrar un renglón compacto colapsado por defecto: `Daño en cola (2v2): [n objetivos]`.
- Botón `▸/▾` para expandir detalle (`player2:+3200 | player1:+2200`).
- Opcional: que viva en panel HUD/overlay y no en log narrativo principal.

---

## 7) Paleta recomendada (base UX)

Sugerencia pragmática para legibilidad sobre fondo oscuro:

- Ofensivo (acciones/daño): `#FF6B6B`
- Defensivo (bloqueos): `#4FC3F7`
- Especial (focus/boost): `#C586C0`
- Operación matemática: `#E0E0E0`
- Total final: `#FFD700`
- Warning: `#FFA726`
- Error/fallo pago: `#EF5350`
- Debug: `#80DEEA` (pero oculto por defecto)
- Cola diferida 2v2/meta: `#B39DDB`

Nota: no es necesario cambiar todo de golpe; conviene mapear primero tokens semánticos y luego recolorear.

---

## 8) Resumen ejecutivo

- El sistema ya está funcional, pero el registro tiene **deuda de presentación** por crecimiento por capas.
- Las dos inconsistencias que marcaste son reales y localizables (focus defensivo textual + duplicado en Defensa Extra).
- El principal salto de prolijidad vendrá de:
  1) unificar plantillas de texto,
  2) centralizar color por tokens,
  3) separar debug/meta del log narrativo (oculto por defecto con toggle).

