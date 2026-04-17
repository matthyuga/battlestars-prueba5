# Contrato de escalas y gasto de técnicas (v1)

Fecha: 2026-04-16  
Estado: Activo (fuente de verdad para costo por puntos/escala)

---

## 1) Objetivo

Definir una regla **determinista y auditable** para convertir:

- `puntos` (progreso en bloques de 100),
- `escala` (contador cíclico 1..10),
- `ec_costo` (gasto de energía EC por técnica),

de acuerdo con el gráfico/planilla acordado.

Este contrato es el estándar para balance, QA y futuras migraciones runtime.

---

## 2) Fuente de referencia

La referencia operativa del contrato vive en:

- `docs/planilla_costos_tecnicas_ep_ec_v1.csv` (vista horizontal extendida a 20000)
- `docs/patron_escala_1_a_10_ec_v1.csv` (patrón 1..10 por técnica)
- `docs/regla_escalado_tecnicas_v1.md` (fórmula resumida)

---

## 3) Definiciones

- **puntos**: entero positivo en múltiplos de 100 para la planilla base.
- **escala**: valor cíclico de 1 a 10:
  - 100 -> 1
  - 200 -> 2
  - ...
  - 1000 -> 10
  - 1100 -> 1 (reinicio de ciclo)
- **escala_base**: umbral por técnica que dispara salto de costo.
- **ec_base**: costo EC inicial de la técnica.
- **ec_step**: incremento fijo de EC por cada umbral superado (v1: `10`).

---

## 4) Regla canónica de cálculo

Para técnicas que usan EC:

`ec_costo = ec_base + ec_step * floor((puntos - 1) / (escala_base * 100))`

Condición de salto:

- el costo sube **al superar** el umbral (`+1` punto también cuenta),
- ejemplo: `escala_base=9`:
  - hasta 900 => tramo anterior,
  - 901 en adelante => siguiente tramo.

Para técnicas que **no usan EC**:

- `ec_costo = vacío/null` (no imputable).

---

## 5) Parámetros por técnica (v1)

| tecnica | escala_base | ec_base | ec_step | usa_ec |
|---|---:|---:|---:|---|
| ataque_extra | 9 | 10 | 10 | si |
| tecnica_extra | 7 | 20 | 10 | si |
| ataque_reductor | 5 | 40 | 10 | si |
| ataque_directo | 6 | 30 | 10 | si |
| ataque_negador | 6 | 30 | 10 | si |
| efecto_especial | 5 | 500 | 10 | si |
| ataque_basico | - | - | - | no |
| defensa_extra | 9 | 10 | 10 | si |
| defensa_reductora | 5 | 40 | 10 | si |
| defensa_basica | - | - | - | no |
| defensa_reflectora | 4 | 50 | 10 | si |

---

## 6) Invariantes obligatorios

1. `escala` siempre en `[1..10]` para filas de planilla.
2. Para técnicas con EC, `ec_costo` es monótono no-decreciente al aumentar `puntos`.
3. Para técnicas sin EC, `ec_costo` permanece vacío.
4. Los cambios de tramo se rigen por `escala_base` y por la condición “supera umbral”.
5. Cualquier ajuste de balance debe versionarse (v2, v3...) y no sobrescribir este contrato.

---

## 7) Casos de verificación mínima (QA)

- `ataque_extra` (`escala_base=9`):
  - 900 => 10
  - 901/1000 => 20
  - 1900 => 30
- `tecnica_extra` (`escala_base=7`):
  - 700 => 20
  - 800 => 30
- `defensa_reflectora` (`escala_base=4`):
  - 400 => 50
  - 500 => 60
  - 900 => 70

---

## 8) Uso en sesiones futuras

Este contrato se utiliza para:

1. evaluar cambios de balance por técnica,
2. validar planillas CSV de costos,
3. alinear integración runtime (`can_afford`, `pay_costs`, selector),
4. comparar comportamiento Win7/Win10 sin ambigüedad de reglas.
