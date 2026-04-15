# Itinerario de continuidad Lobby/Combate

Fecha de arranque: 2026-04-15  
Estado general: En curso

---

## 1) Objetivo del itinerario

Mantener un registro único de pendientes, ejecución y evidencia para continuar el trabajo de **lobby/perfil/preparación/combate** con foco inmediato en estabilidad y rendimiento (especialmente Win7).

---

## 2) Estado base confirmado (checkpoint)

### Ya implementado
- Progresión de tier de cuenta por nivel mínimo + cantidad de héroes por tier.
- Panel DEV en perfil para QA rápido (`+50k oro`, `Lv 99`, `EXP 0`, `Infinite Gold`, `Low-spec combate`).
- Bridge de catálogos toolkit ↔ juego con fallback local.
- Pantalla Perfil (resumen cuenta + top héroes).
- Pantalla de preparación pre-combate (roster/rotación/config rápida/verificación previa).
- Smoke QA funcional (PASS provisional en alcance actual).

### Riesgo activo
- Freeze/latencia en turno ofensivo en Win7 con cargas de técnicas altas.

---

## 3) Backlog maestro (pendientes)

### A. Estabilidad y performance (prioridad alta)
- [ ] A1. Reproducir freeze Win7 con caso controlado (save representativo).
- [ ] A2. Fase A: estabilización mínima de interacción en selector técnico.
- [ ] A3. Fase B: cache temporal + estrategia de invalidación segura.
- [ ] A4. Smoke comparativo Win7/Win10 luego de A2-A3.
- [ ] A5. Definir umbral objetivo de respuesta en hover/click (<200ms percibido).

### B. UX de perfil/preparación (prioridad media)
- [ ] B1. Historial de combates detallado en Perfil.
- [ ] B2. Chequeo completo de técnicas/pool por tier en preparación.
- [ ] B3. Sustitución total del selector legacy por selector data-driven desde roster lobby.

### C. Robustez operativa (prioridad media)
- [ ] C1. Mantener smoke corto en cada cambio de selector/runtime.
- [ ] C2. Abrir fase de hardening visual/datos con criterios de no-regresión.
- [ ] C3. Evaluar activación de Fase C (loader pre-combate) bajo flag.
- [ ] C4. Planear Fase D (telemetría mínima para diagnóstico).

---

## 4) Itinerario sugerido por sesiones

## Sesión 1 — Repro + línea base de rendimiento
**Meta:** obtener reproducción confiable y baseline comparable.

- [ ] Preparar entorno Win7 con save de estrés.
- [ ] Confirmar flags DEV (`Infinite Gold`, `Low-spec combate`).
- [ ] Ejecutar 3 combates ofensivos seguidos y registrar:
  - [ ] tiempo percibido de hover/click,
  - [ ] presencia/ausencia de freeze,
  - [ ] cierre limpio del proceso.
- [ ] Repetir smoke equivalente en Win10 (control).
- [ ] Registrar conclusión y decisión de ajuste inmediato.

**Salida esperada:** evidencia mínima reproducible + baseline Win7/Win10.

---

## Sesión 2 — Fase A (estabilidad)
**Meta:** reducir bloqueos en interacción sin drift funcional.

- [ ] Aplicar optimizaciones de interacción prioritarias en selector.
- [ ] Verificar que no hay regresión visual en HUD/selector.
- [ ] Correr smoke rápido A..G en alcance actual.
- [ ] Registrar resultado y riesgos remanentes.

**Salida esperada:** mejora perceptible de fluidez y 0 bloqueos críticos nuevos.

---

## Sesión 3 — Fase B (cache + invalidación)
**Meta:** bajar recálculo por hover/click con consistencia de datos.

- [ ] Implementar cache temporal de datos de técnicas para UI.
- [ ] Definir y probar invalidación (cambio de estado/equipo/modo).
- [ ] Ejecutar smoke comparativo Win7/Win10.
- [ ] Validar criterio de éxito (<200ms percibido, sin freeze en 3 combates).

**Salida esperada:** estabilidad sostenida y mejora de rendimiento en hardware limitado.

---

## Sesión 4 — Decisión Fase C + preparación Fase D
**Meta:** decidir loader pre-combate y diseño mínimo de telemetría.

- [ ] Revisar necesidad real de loader/prewarm con base en resultados de A+B.
- [ ] Si aplica, activar experimento de loader bajo flag.
- [ ] Definir eventos mínimos de telemetría (sin sobrecarga).
- [ ] Documentar decisión Go/No-Go de Fase C.

**Salida esperada:** roadmap técnico validado para cierre de ciclo.

---

## 5) Registro de seguimiento (actualizar en cada sesión)

| Fecha | Sesión | Responsable | Foco | Resultado | Estado |
|---|---|---|---|---|---|
| 2026-04-15 | Preparación | Equipo | Crear itinerario y consolidar pendientes | Itinerario inicial publicado | ✅ Hecho |
| 2026-04-15 | Revisión HC | Equipo | Auditoría de hardcodes lobby/combate | Documento de hotspots y priorización P0/P1/P2 publicado | ✅ Hecho |
| YYYY-MM-DD | S1 |  | Baseline Win7/Win10 |  | ⏳ Pendiente |
| YYYY-MM-DD | S2 |  | Fase A |  | ⏳ Pendiente |
| YYYY-MM-DD | S3 |  | Fase B |  | ⏳ Pendiente |
| YYYY-MM-DD | S4 |  | Fase C/D decisión |  | ⏳ Pendiente |

---

## 6) Criterios de éxito del ciclo actual

### Win7
- [ ] Hover/click de técnicas < 200ms percibido.
- [ ] 0 freeze en 3 combates ofensivos consecutivos.
- [ ] Cierre normal del juego sin finalizar proceso manualmente.

### Win10
- [ ] Sin regresión visual/funcional en selector y HUD.

---

## 7) Plantilla de bitácora por sesión (copiar/pegar)

```md
# Bitácora de sesión — YYYY-MM-DD

## Objetivo
-

## Cambios aplicados
-

## Pruebas ejecutadas
-

## Resultado
- Estado: PASS / PASS parcial / FAIL
- Riesgos:

## Pendientes actualizados
-

## Próximo paso recomendado
-
```

---

## 8) Reglas de mantenimiento del registro

- Este archivo es la fuente rápida para continuidad operativa.
- Toda sesión debe cerrar con actualización de la tabla de seguimiento.
- Si cambia prioridad, actualizar primero Backlog maestro y luego Itinerario por sesiones.
- Vincular cada bitácora diaria a este itinerario para trazabilidad.
