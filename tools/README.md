# Tools — Economy Lab

## Archivo principal

- `tools/economy_lab.py`
- `tools/economy_toolkit.py` (entrypoint único recomendado)

Simulador CLI para EXP/Oro con:
- normal vs policy_boost,
- riesgo/desempeño/antiabuso,
- bandas por tier (`--tier-band`),
- batch con seed y randomización,
- export JSON/CSV,
- ejecución por escenarios QA.

Si preferís **un solo comando general**, usá `economy_toolkit.py`:

```bash
python tools/economy_toolkit.py --help
```

---

## Ejemplos rápidos

## 1) Corrida simple (duelo libre)

```bash
python tools/economy_lab.py \
  --mode duelo_libre \
  --account-tier B \
  --tier-band B \
  --base-exp 100 \
  --victory \
  --stars 15 \
  --runs 1
```

## 2) Batch con export

```bash
python tools/economy_lab.py \
  --mode torre \
  --account-tier S \
  --tier-band S \
  --base-exp 120 \
  --victory \
  --stars 20 \
  --runs 30 \
  --randomize \
  --seed 7 \
  --json-out /tmp/economy_lab.json \
  --csv-out /tmp/economy_lab.csv
```

## 3) Usar un escenario QA

```bash
python tools/economy_lab.py \
  --scenario normal \
  --json-out /tmp/economy_normal.json \
  --csv-out /tmp/economy_normal.csv
```

## 4) Ejecutar suite completa (casual/normal/hardcore)

```bash
python tools/economy_lab.py \
  --run-all-scenarios \
  --json-out /tmp/economy_suite.json
```

---

## Escenarios QA

- Archivo: `tools/scenarios/economy_lab_profiles.json`
- Perfiles incluidos:
  - `casual`
  - `normal`
  - `hardcore`

Podés editar/duplicar perfiles para crear suites de tuning por parche.

---

## Congelar baseline por versión

Runner recomendado:

```bash
python tools/run_economy_baseline.py \
  --version economy_v1_2026-04-12
```

Salida esperada en:

```
artifacts/economy_baseline/economy_v1_2026-04-12/
  suite.json
  casual.json
  casual.csv
  normal.json
  normal.csv
  hardcore.json
  hardcore.csv
  manifest.json
```

Con esto podés comparar versiones de balance entre parches sin perder trazabilidad.

---

## Ritual sugerido por ajuste (punto 1)

1. Congelar baseline nuevo:

```bash
python tools/run_economy_baseline.py \
  --version economy_vX_YYYY-MM-DD
```

2. Guardar/respaldar carpeta:
- `artifacts/economy_baseline/economy_vX_YYYY-MM-DD/`

3. Comparar contra versión previa (punto 2 + comparador v1):

```bash
python tools/compare_economy_baselines.py \
  --old-version economy_v1_2026-04-12 \
  --new-version economy_v2_2026-04-20 \
  --out-json /tmp/economy_diff_v1_v2.json \
  --out-md /tmp/economy_diff_v1_v2.md
```

Esto imprime una tabla con deltas de `gold_final_policy` y `exp_final_policy` (p50/p95) por escenario.

---

## Dashboard mínimo (Módulo B v0)

Generar HTML estático desde baseline + diff:

```bash
python tools/economy_dashboard.py \
  --suite-json artifacts/economy_baseline/economy_v2_2026-04-20/suite.json \
  --diff-json /tmp/economy_diff_v1_v2.json \
  --out-html /tmp/economy_dashboard_v2.html \
  --title "Economy Dashboard v2"
```

Luego abrir `/tmp/economy_dashboard_v2.html` en navegador.

---

## Automatización ligera (Makefile)

Desde raíz del repo:

```bash
make economy-smoke
make economy-freeze VERSION=economy_v2_2026-04-20
make economy-compare OLD=economy_v1_2026-04-12 NEW=economy_v2_2026-04-20
make economy-gate OLD=economy_v1_2026-04-12 NEW=economy_v2_2026-04-20
make economy-dashboard NEW=economy_v2_2026-04-20
```

También podés usar:

```bash
make economy-report VERSION=economy_v2_2026-04-20
```

para compilar + congelar baseline en un solo paso.

`economy-gate` falla (exit code != 0) si se superan umbrales de alerta.

---

## Integración CI

Se incluye workflow:

- `.github/workflows/economy-tools.yml`

Valida automáticamente:
1. compile smoke de scripts,
2. freeze baseline A/B,
3. gate baseline A vs B (con umbrales),
4. generación de dashboard HTML.

---

## Umbrales de alerta

- Archivo: `tools/scenarios/economy_alert_thresholds.json`
- Usado por:
  - `make economy-compare`
  - `make economy-gate`

---

## Toolkit unificado (sin Makefile)

### Freeze
```bash
python tools/economy_toolkit.py freeze --version economy_v2_2026-04-20
```

### Compare
```bash
python tools/economy_toolkit.py compare \
  --old-version economy_v1_2026-04-12 \
  --new-version economy_v2_2026-04-20 \
  --fail-on-alert
```

### Dashboard
```bash
python tools/economy_toolkit.py dashboard \
  --old-version economy_v1_2026-04-12 \
  --new-version economy_v2_2026-04-20 \
  --out-html /tmp/economy_dashboard_v2.html
```

### Ciclo completo (freeze + compare + dashboard)
```bash
python tools/economy_toolkit.py cycle \
  --version economy_v2_2026-04-20 \
  --previous-version economy_v1_2026-04-12 \
  --fail-on-alert
```
