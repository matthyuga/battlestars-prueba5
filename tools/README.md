# Tools — Economy Lab

## Archivo principal

- `tools/economy_lab.py`

Simulador CLI para EXP/Oro con:
- normal vs policy_boost,
- riesgo/desempeño/antiabuso,
- bandas por tier (`--tier-band`),
- batch con seed y randomización,
- export JSON/CSV,
- ejecución por escenarios QA.

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
