# Fase 0 — Diagnóstico Ejecutivo del Registro de Combate

## Alcance

Este diagnóstico consolida:

1. Hallazgos previos de `COMBAT_LOG_AUDIT_V1`.
2. Feedback UX detallado del usuario (capturas + reglas de formato deseadas).
3. Contraste técnico por lectura de código en los módulos que generan log de player/enemy.

> Objetivo: preparar implementación por fases sin tocar la lógica de daño, priorizando homogeneidad visual y semántica.

---

## Hallazgo crítico reportado: “forza defensa fuerte” sin línea de defensa visible

### Síntoma observado
- El panel HUD de IA muestra modo de defensa forzada ("force strong"),
- pero en el registro puede aparecer solo `Concentrar Activado` y no la línea esperada de técnica defensiva específica.

### Causa técnica probable (confirmada por código)
1. El plan defensivo puede seleccionar `"defense_strong_block"` cuando el modo está en `force_strong`. (`_def_pick_one`).
2. En el ejecutor defensivo, esa key no tiene rama de log dedicada (solo existen ramas explícitas para `def_extra`, `def_reduct`, `def_reflect`).
3. Resultado: se aplica bloqueo (entra en operación defensiva), pero no siempre aparece una línea “bonita/canónica” de técnica en el bloque de resumen.

### Evidencia de código
- Selección de `force_strong -> defense_strong_block` en planner: `game/4/04D_AI_PLANS_DEFENSEV1a.rpy`.
- Logs defensivos con ramas explícitas limitadas (`def_extra`, `def_reduct`, `def_reflect`): `game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy`.

### Acción recomendada (Fase A)
- Añadir plantilla canónica para `defense_strong_block` (ej. `log_defense_strong(...)`) y/o mapearla a `log_defense_extra(...)` si semánticamente corresponde.
- Garantizar que toda técnica defensiva ejecutada emita una línea visible de técnica antes de la operación.

---

## Diagnóstico de homogeneidad (player vs enemy)

## 1) Costos de técnica (Reiatsu / Energía)

### Estado actual
- Player y enemy no usan exactamente el mismo estilo ni nomenclatura (en algunos casos aparece `Ene`/`E`).

### Decisión UX recomendada
- Estandarizar etiqueta a `Energía` en ambos flujos.
- Mantener costo en gris (como meta-info secundaria), conservando legibilidad.

---

## 2) Ofensiva: plantilla canónica deseada

### Formato objetivo
- `Nombre técnica` en rojo.
- `→ Inflige` en blanco.
- Valor de daño en rojo.
- Cierre textual: `de daño.`
- Segunda línea: `(Reiatsu X / Energía Y)` en gris.

### Ajuste de Focus/Concentrar
- Mantener color especial violeta para estado boost.
- En técnica impactada por focus, explicitar `×2` en la fórmula y mantener valor final potenciado en rojo.

---

## 3) Operación ofensiva y metadatos (target / cola)

### Problema
- Saturación visual por bloques matemáticos + targeting + cola 2v2 en el mismo nivel de prioridad.

### Propuesta
- UI colapsable (spoiler/toggle) para:
  - `Operación ofensiva` (expandir suma detallada).
  - `Target asignado`.
  - `Daño en cola 2v2`.
- Mantener visible por defecto solo resumen de alto valor (`Daño total` con desglose `defendibles/directos` cuando aplique).

---

## 4) Direct attack (ataque indefendible)

### Ajustes recomendados
- Reutilizar verbo `Inflige` para consistencia con ofensivas estándar.
- Corregir expresión de daño: incluir `×2` cuando aplique y finalizar como `de daño.`
- Texto de condición:
  - `Si saca 2/3 dados de éxito, este ataque es indefendible.`
- Agrupar `Tirada` + `Resultado` en bloque visual separado del resto del log (separador/sangría).

---

## 5) Defensiva: consistencia de color y semántica

### Objetivo de color
- Técnicas y valores defensivos en celeste (consistente entre nombre y número).
- Boost `Potenciar/Concentrar` en violeta.
- Paréntesis y `×2` neutros (blanco).

### Operación defensiva
- Título `Operación Defensiva` en blanco (no celeste), para jerarquía neutra de sección.
- `Daño enemigo:` en rojo.
- Reducción porcentual en azul con signo negativo explícito (`-10%`) y valor asociado en paréntesis (`(320)`).
- `Daño neto:` con dos puntos y valores finales en rojo.
- `HP` en blanco + valor en verde (rojo solo si llega a 0 / KO).

---

## 6) Debug en log principal

### Estado y decisión
- El log narrativo no debe mezclar telemetría de ingeniería.
- Mantener debug en panel dedicado (atajo `T`) y oculto por defecto en log principal.

### Acción
- Separar `battle_log_add_debug(...)` de `battle_log_add(...)` y controlar visibilidad con flag.

---

## Backlog implementable (orden sugerido)

1. **Canon de plantillas A1**: ofensiva/defensiva + costos + focus + direct attack.
2. **Fix A2 crítico**: soporte visible para `defense_strong_block` en log defensivo IA.
3. **Canon de resumen A3**: `Daño total` con desglose defendible/directo consistente.
4. **Tokens B1**: unificación de color semántico (sin nuevos hex en gameplay).
5. **Debug C1**: separación debug/narrativo con toggle.
6. **UX C2**: toggles tipo spoiler para operación/target/cola 2v2.

---

## Criterios de aceptación (QA rápido)

- Toda técnica ejecutada (player/enemy) imprime una línea canónica de técnica.
- `force_strong` muestra línea defensiva explícita, no solo operación resultante.
- No aparece `Ene` ni `E`; solo `Energía`.
- `Daño total` siempre explicita tipo de daño cuando exista mezcla (directo + defendible).
- Debug técnico no aparece en log narrativo por defecto.
- Operación/target/cola pueden ocultarse y expandirse bajo demanda.

