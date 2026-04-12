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

## Dashboard (Módulo B v1.1)

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

### Simulate (wrapper de economy_lab)
```bash
python tools/economy_toolkit.py simulate -- --scenario normal --json-out /tmp/economy_normal.json
```


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


## Ejecutable (sin Python CLI ni Makefile)

Si preferís usarlo como programa ejecutable:

1) Instalar empaquetador (solo una vez):
```bash
python -m pip install pyinstaller
```

2) Construir binario:
```bash
make economy-exe
```

3) Resultado esperado:
- Linux/macOS: `dist/economy-toolkit`
- Windows: `dist/economy-toolkit.exe`

Luego podés ejecutar el binario con los mismos subcomandos (`freeze`, `compare`, `dashboard`, `cycle`, `simulate`).


## Release packaging (multi-OS)

Para generar paquete release local (ZIP + SHA256):

```bash
make economy-release-package
```

Salida esperada:
- `dist/release/economy-toolkit-<platform>-py310.zip`
- `dist/release/economy-toolkit-<platform>-py310.zip.sha256`

CI de release:
- `.github/workflows/economy-release.yml`
- Trigger por tag: `economy-toolkit-v*`
- Build en `ubuntu-latest`, `windows-latest`, `macos-latest`

Roadmap completo:
- `docs/ROADMAP_ECONOMY_TOOLKIT_COMPLETION_V1.md`


## Hardening de distribución (Fase D)

### Convención de tags semánticos
Usar tags con formato estricto:

- `economy-toolkit-vMAJOR.MINOR.PATCH`
- ejemplo: `economy-toolkit-v1.2.0`

El workflow de release valida este patrón y falla si no se cumple.

### Changelog automático
El workflow `.github/workflows/economy-release.yml` genera changelog automáticamente al publicar release en tags semánticos.

### Firma/attestation
- Se genera `SHA256` por paquete (`.sha256`).
- El workflow produce **build provenance attestation** para artifacts de release.
- Firma GPG opcional local de checksum con `ECONOMY_GPG_KEY_ID`.

### Verificación de checksum (consumo interno)

```bash
python tools/verify_release_checksum.py \
  --package dist/release/<archivo>.zip \
  --checksum-file dist/release/<archivo>.zip.sha256
```

Atajo Make:

```bash
make economy-verify-checksum PACKAGE=dist/release/<archivo>.zip CHECKSUM=dist/release/<archivo>.zip.sha256
```


Referencia de consumo interno:
- `docs/RELEASE_CONSUMPTION_VERIFICATION_V1.md`


## UX ejecutable (Fase E)

### Wizard interactivo (no técnico)

```bash
python tools/economy_toolkit.py wizard
```

Menú guiado para ejecutar `cycle + bundle` con preguntas paso a paso.

### Profiles cargables por nombre

Listar profiles disponibles:

```bash
python tools/economy_toolkit.py profile-list
```

Ejecutar profile:

```bash
python tools/economy_toolkit.py run-profile \
  --name balance_default \
  --version economy_v2_2026-04-12 \
  --previous-version economy_v1_2026-04-10
```

Profiles incluidos:
- `tools/profiles/balance_default.json`
- `tools/profiles/release_candidate.json`

### Report bundle (diff + dashboard + manifest)

Modo directo:

```bash
python tools/economy_toolkit.py bundle \
  --old-version economy_v1 \
  --new-version economy_v2 \
  --diff-json /tmp/economy_diff.json \
  --diff-md /tmp/economy_diff.md \
  --dashboard-html /tmp/economy_dashboard.html \
  --bundle-dir artifacts/economy_reports
```

O automático dentro de `cycle` / `run-profile` / `wizard`.

Salida bundle:
- `diff.json`
- `diff.md`
- `dashboard.html`
- `manifest.json`


## Calidad y soporte (Fase F)

### Ejecutar tests unitarios + golden

```bash
python -m pytest -q
```

Cobertura base:
- fórmulas clave (`economy_lab.py`),
- comparador (`compare_economy_baselines.py`),
- golden files de regresión (`tests/golden/`).

### Manual no técnico
- `docs/MANUAL_OPERACION_ECONOMY_TOOLKIT_V1.md`

### Criterio práctico de toolkit completo
- release multi-OS automático,
- tests + gate antes de release,
- ejecución principal no técnica mediante ejecutable + wizard.


## Preflight recomendado antes de usar

```bash
make economy-preflight
```

Incluye:
- compile smoke,
- tests unitarios + golden,
- `doctor` de archivos/perfiles mínimos.

Chequeo manual rápido:

```bash
python tools/economy_toolkit.py doctor
```

Readiness assessment:
- `docs/READINESS_ASSESSMENT_ECONOMY_TOOLKIT_V1.md`
