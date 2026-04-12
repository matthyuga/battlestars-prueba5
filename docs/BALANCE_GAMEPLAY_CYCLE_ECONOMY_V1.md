# Playbook — Ciclo de balance gameplay + Economy Lab (v1)

Fecha: 2026-04-12

## Objetivo

Conectar cambios de gameplay (duelo/torneo/torre) con un ciclo repetible de economía:
1. congelar baseline,
2. comparar contra versión previa,
3. revisar dashboard,
4. decidir ajuste/rollback.

---

## Flujo operativo por cambio

## Paso 0 — Preparar versión

Definir nombre:
- `economy_vX_YYYY-MM-DD`

Ejemplo:
- `economy_v3_2026-04-12`

## Paso 1 — Congelar baseline nuevo

```bash
make economy-freeze VERSION=economy_v3_2026-04-12
```

## Paso 2 — Comparar con versión anterior

```bash
make economy-compare OLD=economy_v2_2026-04-10 NEW=economy_v3_2026-04-12
```

Si querés modo gate duro (falla si supera umbrales):

```bash
make economy-gate OLD=economy_v2_2026-04-10 NEW=economy_v3_2026-04-12
```

## Paso 3 — Revisar dashboard

```bash
make economy-dashboard NEW=economy_v3_2026-04-12
```

Abrir HTML en `/tmp`.

## Paso 4 — Decisión

- Si no hay alertas críticas: continuar.
- Si hay alertas: ajustar fórmula/boosts y repetir desde paso 1.

---

## Umbrales de alerta v1

Archivo:
- `tools/scenarios/economy_alert_thresholds.json`

Métricas foco:
- `gold_final_policy.p50`
- `gold_final_policy.p95`
- `exp_final_policy.p50`
- `exp_final_policy.p95`

---

## Frecuencia recomendada

- Cada PR que toque:
  - boosts por tier,
  - bandas min/max de oro,
  - fórmula de desempeño/riesgo/antiabuso,
  - escenarios de balance.

---

## Entregables mínimos por iteración

1. Carpeta baseline nueva en `artifacts/economy_baseline/<version>/`
2. `diff` JSON/MD contra la versión previa
3. Dashboard HTML
4. Nota corta de decisión:
   - qué cambió,
   - qué métrica mejoró/empeoró,
   - si pasa/falla gate.
