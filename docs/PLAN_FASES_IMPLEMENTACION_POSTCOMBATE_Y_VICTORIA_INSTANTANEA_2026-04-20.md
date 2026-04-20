# Plan por fases — implementación post-combate (C4) + victoria instantánea (dev)

Fecha: 2026-04-20  
Estado: plan ejecutable para iniciar implementación

---

## Objetivo general
Implementar un rediseño incremental de la escena de recompensas post-combate (C4), priorizando claridad para el jugador (mostrar recompensa propia), explicabilidad de cálculo (parámetros/fórmulas), y habilitar una herramienta de depuración controlada para forzar victoria instantánea sin romper la ruta oficial de cierre.

---

## Alcance
- Incluye:
  - Refactor visual/UX de `sim_battle_end_reward_summary_v1`.
  - Exposición de parámetros de rendimiento ya disponibles en `SimulationResult`.
  - Integración dev-only de comando/botón de victoria instantánea.
  - Smoke QA funcional y checklist de release.
- Excluye:
  - Reescritura del contrato matemático del simulador.
  - Cambios de balance económico (base/step/tablas).

---

## Fase 0 — Preparación y baseline

### Objetivo
Dejar línea base reproducible para comparar antes/después.

### Tareas
1. Capturar evidencia actual de C4 en 3 escenarios: victoria, derrota, draw.
2. Registrar salida de `sim_result` y `apply_report` (campos clave).
3. Confirmar que el flujo actual muestra filas de enemigos no elegibles (+0/+0).

### Entregables
- Mini bitácora de baseline (capturas + notas).
- Lista de campos visibles actuales.

### Criterio de salida
- Baseline documentado y validado por equipo.

---

## Fase 1 — Diseño funcional C4 (sin cambiar lógica)

### Objetivo
Definir UX final del resumen post-combate antes de codificar.

### Tareas
1. Diseñar bloques de pantalla:
   - Bloque principal: **Recompensa obtenida** (jugador/equipo propio).
   - Bloque secundario: resumen de aplicación (`ok`, `count`, `EXP`, `Oro`).
   - Bloque técnico colapsable: warnings/errors y filas completas.
2. Definir regla visual para ocultar enemigos no relevantes:
   - default: ocultar `eligible=False` o `exp_gain=0 && oro_gain=0`.
   - toggle QA para mostrar todo.
3. Definir sección “Parámetros de rendimiento”:
   - base, multiplicadores, deltas, fórmula textual.

### Entregables
- Especificación UI C4 (wireframe textual + reglas de visibilidad).

### Criterio de salida
- Aprobación funcional de diseño por parte del equipo.

---

## Fase 2 — Implementación C4 v2

### Objetivo
Aplicar rediseño de C4 reutilizando datos existentes del resultado.

### Tareas
1. Refactor de `screen sim_battle_end_reward_summary_v1`:
   - separar “recompensa jugador” de “detalle técnico”.
   - añadir toggles de visibilidad.
2. Añadir panel “Parámetros de rendimiento” por actor recompensado.
3. Mantener intacta la ruta de negocio:
   - `battle_end` -> simulación -> persistencia -> apply -> resumen.

### Entregables
- C4 v2 funcional.
- Compatibilidad con casos sin filas o con errores de auditoría.

### Criterio de salida
- En victoria estándar, el primer bloque muestra solo recompensa propia.
- QA puede habilitar “ver todo” y revisar filas técnicas.

---

## Fase 3 — Consola dev / victoria instantánea (dev-only)

### Objetivo
Acelerar pruebas de cierre y recompensas sin alterar producción.

### Tareas
1. Definir API dev canónica (ejemplo):
   - `bs_dev_instant_victory()`
   - opcional: `bs_dev_exec_code(cmd)` con whitelist.
2. Implementar comando de victoria instantánea:
   - setear KO enemigo por ruta segura.
   - derivar a `jump battle_end` normal.
3. Agregar UI dev:
   - botón/hotkey en overlay debug, oculto fuera de dev.
4. Auditoría:
   - log de uso (`source=dev_instant_victory`, timestamp, actor).

### Guardrails obligatorios
- Solo habilitado con `config.developer` + flag dev.
- Desactivado en release.
- Sin bypass de simulador/aplicación.

### Entregables
- Herramienta dev de cierre instantáneo operativa y trazable.

### Criterio de salida
- Al usar victoria instantánea se llega a C4 y se aplica recompensa normal.
- No aparece la herramienta en build de release.

---

## Fase 4 — QA técnico/funcional

### Objetivo
Validar regresiones, consistencia visual y seguridad de la herramienta dev.

### Matriz mínima de pruebas
1. Victoria normal (1v1).
2. Derrota normal (1v1).
3. Draw.
4. Victoria instantánea dev.
5. Retry/duelos consecutivos (idempotencia estable).
6. Verificación de panel técnico (warnings/errors visibles).

### Entregables
- Checklist QA firmado.
- Bitácora de incidencias y fixes menores.

### Criterio de salida
- 0 bloqueantes en flujo crítico `battle_end`.

---

## Fase 5 — Cierre y handoff

### Objetivo
Dejar implementación lista para continuidad y mantenimiento.

### Tareas
1. Documentar decisiones finales (UI + dev tool + guardrails).
2. Agregar guía rápida para QA/manual testing.
3. Registrar backlog de mejoras futuras:
   - métricas visuales avanzadas,
   - comparativa por combate,
   - export de auditoría.

### Entregables
- Documento final de handoff.
- Changelog por fase.

### Criterio de salida
- Equipo puede continuar iteraciones sin depender de contexto oral.

---

## Orden recomendado de ejecución (sprint)
1. Fase 0 + Fase 1 (diseño y baseline).  
2. Fase 2 (C4 v2).  
3. Fase 3 (victoria instantánea dev-only).  
4. Fase 4 (QA).  
5. Fase 5 (handoff).

---

## Riesgos y mitigación resumidos
- **Riesgo:** romper cierre oficial de combate.  
  **Mitigación:** no bypass; siempre `battle_end` canónico.
- **Riesgo:** exponer comandos cheat en producción.  
  **Mitigación:** gating dev estricto + verificación release.
- **Riesgo:** UI sobrecargada en C4.  
  **Mitigación:** jerarquía visual + panel técnico colapsable.

---

## Definición de “listo” (DoD)
- C4 muestra recompensa propia de forma clara.
- Parámetros de rendimiento visibles y entendibles.
- Herramienta de victoria instantánea operativa solo en dev.
- QA smoke completo sin bloqueantes.
