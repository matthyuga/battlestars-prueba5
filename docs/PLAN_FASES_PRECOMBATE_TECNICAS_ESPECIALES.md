# Plan por fases — Pre-combate, slots y técnicas especiales

## Objetivo
Implementar de forma incremental el sistema de **pre-combate** con selección de técnicas por slots, integrar nuevas técnicas especiales, mantener compatibilidad con `1v1`/`2v2`, y reducir riesgo de regresiones visuales/lógicas.

---

## Estado de ejecución actual
- **Fase 0:** cerrada en modalidad operativa (documentación consolidada).
- **Fase 1:** implementada (UI pre-combate + validación + persistencia).
- **Fase 2:** implementada (compactación, paginación horizontal, vista íconos/fallback simple).

---

## Resumen de reglas funcionales acordadas

### 1) Categorías de slots
- `atk` = slots para técnicas ofensivas.
- `def` = slots para técnicas defensivas.
- `spc` = slots para técnicas especiales.

### 2) Configuración base de prueba (editable)
- `atk`: 7
- `def`: 5
- `spc`: 1

### 3) Configuración ejemplo de nivel bajo (editable)
- Nivel 1 (ejemplo):
  - `atk`: 2
  - `def`: 1
  - `spc`: 1

### 4) Regla oficial del juego para especiales
- Oficialmente se admite **1 técnica especial** por jugador en modo por slots.
- Se incorpora parámetro base de perk (`extra_spc_slots`) para habilitar 2 especiales cuando aplique.
- En etapa de pruebas se habilita `modo libre` para validar comportamiento sin límites estrictos.

### 5) Doble consumo para técnicas especiales
- Especial ofensiva consume: `1 atk + 1 spc`.
- Especial defensiva consume: `1 def + 1 spc`.

### 6) Concentrar y Potenciar como especiales
- `Concentrar` (en ataque) se considera técnica `spc` ofensiva:
  - consume `1 atk + 1 spc`.
- `Potenciar` (en defensa) se considera técnica `spc` defensiva:
  - consume `1 def + 1 spc`.

### 7) Técnicas especiales de esta iteración
- `Ladrón ofensivo`
- `Ladrón defensivo`
- `Ladrón de concentrar`
- `Salvaguarda principiante`

---

## Fase 0 — Contrato funcional (sin cambios profundos)

### Objetivo
Congelar reglas para evitar retrabajo.

### Entregables
- Documento SSOT de reglas de slots y especiales.
- Definición clara de comportamiento para bloqueo por “Ladrón...”.
- Definición de prioridad para “Salvaguarda principiante”.

### Criterio de salida
- Reglas aprobadas antes de implementar UI/engine.

---

## Fase 1 — Sala de pre-combate (UI + estado)

### Objetivo
Crear un panel de pre-combate, similar al editor de puntos, para seleccionar técnicas a usar en combate.

### Alcance
- Nueva pantalla de pre-combate accesible por botón/ruta.
- Selección de técnicas por categorías (`atk`, `def`, `spc`).
- Contadores visibles de slots usados/restantes.
- Selector de modo: `modo libre` / `modo por slots`.
- Validación de límites por slot cuando esté activo modo por slots.
- Integración de reglas de doble consumo para especiales.
- Inclusión explícita de `Concentrar` y `Potenciar` como `spc` según tipo.

### Criterio de salida
- No se puede confirmar loadout inválido.
- Se puede guardar/recuperar selección para iniciar batalla.

---

## Fase 2 — Integración visual de técnicas y escalabilidad UI

### Objetivo
Asegurar que el selector soporte crecimiento de técnicas sin saturarse.

### Alcance
- Integrar íconos nuevos en `tech_buttons`.
- Reducir tamaño de botones (~20%).
- Añadir desplazamiento lateral o paginación en selector de técnicas.
- Mantener modo de panel simple/sin PNG para compat y QA.

### Criterio de salida
- UI usable con lista larga de técnicas en resoluciones objetivo.
- Sin solapes críticos ni recortes de botones.

---

## Fase 3 — Mecánicas de bloqueo “Ladrón ...”

### Objetivo
Implementar efectos especiales de anulación temporal de técnica rival.

### Alcance
- Al finalizar turno, si aplica técnica ladrón:
  - overlay oscuro + panel central de selección.
  - selección de objetivo por slot rival (ej. `E1`, `E2`, con nombre).
  - selección de técnica del rival a bloquear.
- Bloqueo de técnica dura solo el siguiente turno del rival objetivo.
- Preparar estructura escalable por `team:slot` (futuro `2v2v2`).

### Regla IA acordada
- Si IA está en modo forzado y la técnica forzada está bloqueada: no reemplaza.
- Si IA no está forzada: puede escoger variante válida no bloqueada.
- En concatenación: bloquear una técnica no cancela automáticamente todo el plan, solo esa técnica.

### Criterio de salida
- Bloqueos se aplican y expiran correctamente por unidad/turno.

---

## Fase 4 — Mecánica defensiva especial “Salvaguarda”

### Objetivo
Aplicar reducción especial con prioridad correcta en pipeline de daño.

### Alcance
- `Salvaguarda principiante`:
  - reduce 50% del daño enemigo aplicable en resolución,
  - no se suma linealmente al porcentaje de técnica común; se aplica por capas.
- Prioridad obligatoria:
  1. reducción de técnica común (p. ej. defensa reductora),
  2. reducción de técnica especial (`Salvaguarda`).
- Requisito técnico:
  - separar flags de efecto común y efecto especial para el pipeline.

### Fórmula base (principiante)
- `D1 = D_in * (1 - r_comun)`
- `D2 = D1 * 0.50`
- `D_total = D2`

### Criterio de salida
- Logs y operación muestran prioridad aplicada sin ambigüedad.

---

## Fase 5 — Integración con inicio de combate (1v1 primero)

### Objetivo
Conectar pre-combate con flujo de inicio de batalla.

### Alcance
- Botón “Iniciar batalla” desde pre-combate.
- Flujo inicial: priorizar `1v1`.
- Mantener opción de HUD simple/sin PNG.
- Cargar loadout seleccionado antes de entrar al selector de turno.

### Criterio de salida
- Camino completo pre-combate → inicio batalla → selector funcional.

---

## Fase 6 — Compatibilidad 2v2 y modos múltiples

### Objetivo
Escalar sistema por unidad/slot y equipos múltiples.

### Alcance
- Selección de objetivo por slot (`P1/P2/E1/E2`) en efectos especiales.
- Persistencia por `unit_key` y resolución por actor activo.
- Diseño preparado para extender a `2v2v2`.

### Criterio de salida
- Mismas reglas funcionando por actor en 2v2.

---

## Fase 7 — QA incremental por hitos

### Objetivo
Reducir regresiones y validar comportamiento real de combate.

### Hitos sugeridos
1. **QA-UI:** slots, validación, scroll, escalado de botones.
2. **QA-SPECIAL:** ladrón + salvaguarda (incluye expiración 1 turno).
3. **QA-IA:** forzado/no forzado + concatenaciones con bloqueos.
4. **QA-MODOS:** smoke 1v1 y 2v2 por slot.

### Criterio de salida
- Checklist de humo completo en build limpia para hitos activos.

---

## Orden recomendado de ejecución
1. Fase 0
2. Fase 1
3. Fase 2
4. Fase 3
5. Fase 4
6. Fase 5
7. Fase 6
8. Fase 7

Este orden prioriza primero reglas y UX base, luego mecánicas profundas, y finalmente escalado por modos/equipos.
