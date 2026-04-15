# Plan por fases — Optimización de combate y loader pre-combate (v1)

## Objetivo
Reducir congelamientos/latencia en turno ofensivo (especialmente en hardware antiguo) sin romper la UX normal del combate.

---

## Fase A — Hardening rápido (bajo riesgo)

### Alcance
- Mantener low-spec como ruta estable.
- Reducir trabajo visual por frame/interacción en selector y HUD.
- Evitar operaciones pesadas en hover cuando low-spec está activo.

### Entregables
- Ajustes de UI low-spec (botones/listas/tooltips).
- Guardas para timers/animaciones no críticas.

### Validación
- Smoke test de selector ofensivo en combate corto y largo.

---

## Fase B — Cache de selector (alto impacto)

### Alcance
- Cachear resultados de:
  - `tech_preview(tech_key, mode)`
  - `tech_cost_check(tech_key)`
- Agregar estrategia de invalidación por firma de estado:
  - recursos (reiatsu/energy),
  - modo de batalla,
  - cola actual,
  - toggles relevantes (focus/fury/split).

### Entregables
- Módulo/helper de cache temporal por combate.
- Métricas simples (hits/misses) para auditoría técnica.

### Validación
- Comparativa tiempo de respuesta hover/click antes/después.

---

## Fase C — Loader pre-combate (UX + prewarm)

### Alcance
- Pantalla de carga corta antes de entrar al núcleo de combate.
- Prewarm de:
  - catálogos/estructuras de técnicas para selector,
  - recursos visuales base (retratos/bg/HUD),
  - estado inicial de paneles críticos.

### Entregables
- Screen/label de loader bajo feature flag.
- Pipeline de preparación con timeout seguro.

### Validación
- Menor pico de latencia al primer turno ofensivo.

---

## Fase D — Telemetría y decisión de rollout

### Alcance
- Instrumentación mínima por sesión:
  - tiempo de apertura de selector,
  - tiempo de hover/click promedio,
  - conteo de freeze/reportes.

### Entregables
- Bitácora QA comparativa Win7 vs Win10.
- Recomendación Go/No-Go por fase.

### Validación
- Criterios cuantitativos de estabilidad.

---

## Feature flags sugeridos
- `bs_battle_low_spec_mode` (ya existente).
- `bs_battle_selector_cache_enabled`.
- `bs_battle_preload_loader_enabled`.

---

## Orden recomendado de ejecución
1. Fase A
2. Fase B
3. Fase D (medición intermedia)
4. Fase C
5. Fase D (medición final + decisión de rollout)
