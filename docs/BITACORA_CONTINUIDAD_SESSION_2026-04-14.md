# Bitácora de continuidad — sesión 2026-04-14

## 1) Estado actual consolidado

### Lobby / cuenta / tiers
- Se implementó progresión de tier de cuenta por doble condición:
  - nivel mínimo por tier,
  - cantidad de héroes del mismo tier.
- Requisitos activos documentados en `CONTRATO_TIER_CUENTA_V1.md`.
- La cuenta empieza sin tier (`""` / "Sin tier") y se recalcula al comprar héroes y al entrar a lobby/perfil.

### DEV QA para pruebas rápidas
- Se agregó panel DEV en perfil para acelerar pruebas:
  - `+50k oro`
  - `Lv 99`
  - `EXP 0`
  - toggle `Infinite Gold`
  - toggle `Low-spec combate`
- Se agregaron helpers DEV de cuenta:
  - `bs_saga_dev_set_account_state(...)`
  - `bs_saga_dev_toggle_infinite_gold(...)`
  - `bs_saga_dev_apply_low_spec_mode(...)`

### Integración toolkit ↔ juego
- Se agregó bridge de catálogos para inyección controlada:
  - `bs_get_hero_catalog_v1`, `bs_get_item_catalog_v1`, `bs_set_catalog_bundle_v1`
- El Hub Saga intenta catálogos inyectados primero; fallback a esquema local si faltan.

### Combate / rendimiento
- Se agregó low-spec en HUD compat para saltar animaciones fake por timer.
- Se ajustó selector técnico en low-spec:
  - tamaño de botones reducido,
  - recorte de listas a 12 técnicas por columna en vista expandida,
  - aviso visual de modo recortado.
- Aun así, en Windows 7 persisten reportes de congelamiento en turno ofensivo (hover/click con latencia y freeze posterior) en partidas cargadas con muchas técnicas.

---

## 2) Hallazgos técnicos de performance (resumen)

- El costo no parece ser solo I/O de disco; hay presión de render/interacción en UI de combate:
  - evaluación por técnica de `tech_preview` y `tech_cost_check` en listas de botones,
  - tooltip dinámico con hover,
  - cálculos por fila en cola de técnicas,
  - timers periódicos de HUD (atenuados en low-spec).
- El cuello de botella se manifiesta más fuerte en hardware antiguo (Win7 oficina) y no en hardware alto (Win10/i9/32GB/RTX3060).

---

## 3) Preguntas abiertas que quedaron acordadas

1. ¿Conviene pantalla de carga/prewarm?
   - Sí, potencialmente útil para trasladar costo de primer render/cálculo al pre-combate.
2. ¿Qué precargar exactamente?
   - Datos de técnicas para UI (tooltip/costos), recursos visuales críticos (HUD/retratos/bg), estado inicial de selector.
3. ¿Es necesario cache temporal?
   - Sí, recomendable para evitar recálculo masivo por hover/interacción.

---

## 4) Decisión de trabajo para próxima sesión

- Ejecutar plan por fases (documentado en `PLAN_FASES_OPTIMIZACION_COMBATE_LOADER_V1.md`).
- Prioridad inmediata: Fase A + B (estabilidad + cache/invalidación).
- Luego: Fase C (loader pre-combate) y Fase D (telemetría).

---

## 5) Riesgos y criterios de éxito

### Riesgos
- Sobre-optimizar con hacks sin métrica.
- Introducir drift visual/funcional entre modo normal y low-spec.
- Cache sin invalidación correcta => datos stale.

### Criterios de éxito (QA)
- En Win7:
  - hover/click de técnicas responde en < 200ms percibido,
  - no freeze en 3 combates consecutivos ofensivos,
  - cierre normal del juego sin matar proceso desde administrador.
- En Win10:
  - no regresión visual/funcional en selector y HUD.

---

## 6) Checklist de arranque próxima sesión

- [ ] Verificar estado flags DEV (`Infinite Gold`, `Low-spec combate`).
- [ ] Reproducir caso de freeze en build de prueba (Win7) con save cargado.
- [ ] Aplicar Fase A (si queda pendiente).
- [ ] Implementar Fase B (cache + invalidación).
- [ ] Correr smoke QA comparativo Win7/Win10.
- [ ] Definir si se habilita Fase C (loader) bajo flag.
