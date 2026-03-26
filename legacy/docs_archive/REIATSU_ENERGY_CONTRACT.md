# Contrato funcional: Consumo de Reiatsu y Energía

## 1) Objetivo
Definir una **fuente única de verdad** para el consumo de recursos en combate, de forma consistente entre:
- preview del selector,
- validación de recursos,
- ejecución real de acciones,
- IA.

Este contrato documenta la base estructural acordada: **Reiatsu 1:1 con valor de técnica** y **Energía por escalado de casillas**.

---

## 2) Alcance
Aplica a técnicas ofensivas y defensivas modernas del sistema de batalla.

Incluye:
- cálculo de costo base,
- cálculo de costo final (con multiplicadores permitidos),
- reglas de consumo,
- reglas de validación.

No incluye balance numérico fino (eso se considera configuración de datos).

---

## 3) Definiciones
- **Valor de técnica (`value`)**: magnitud base de daño o bloqueo de la técnica.
- **Escala (`scale`)**: cantidad de casillas (de 100 puntos) necesarias para que suba el costo de energía.
- **Casilla**: tramo de 100 puntos de valor.
  - 100 → casilla 1
  - 200 → casilla 2
  - 300 → casilla 3
  - etc.
- **Bloque de energía (`block`)**: grupos de casillas determinados por `scale`.

---

## 4) Regla de costo de Reiatsu

### 4.1 Regla base
`reiatsu_cost_base = value`

### 4.2 Regla final
`reiatsu_cost_final = reiatsu_cost_base * mult_reiatsu`

Donde:
- `mult_reiatsu = 1` por defecto,
- puede subir a `x2` o `x4` únicamente por mecánicas explícitas (ej. focus/potenciar),
- debe estar acotado a un rango seguro (mínimo 1).

### 4.3 Consecuencia de diseño
Si una técnica tiene valor final 500, su costo de reiatsu base es 500.

---

## 5) Regla de costo de Energía (escalado por casillas)

### 5.1 Normalización mínima
Si `value < 100`, se normaliza a `100` para cálculo de energía.

### 5.2 Fórmula
1. `cell = value // 100`
2. `block = (cell - 1) // scale`
3. `energy_cost = 10 + block * 10`

### 5.3 Intuición
- El costo parte en 10.
- Sube +10 cada vez que se completa un bloque de `scale` casillas.
- Técnicas con menor `scale` suben energía más rápido.

---

## 6) Escalas de referencia por técnica

### 6.1 Ofensivas
- `extra_attack`: 9
- `extra_tech`: 7
- `attack_reducer`: 5
- `direct_attack`: 6
- `noatk_attack`: 6
- `stronger_attack`: 9

### 6.2 Defensivas
- `defense_extra`: 9
- `defense_reducer`: 5
- `defense_reflect`: 4
- `defense_strong_block`: 9

> Nota: estas escalas son datos de configuración y se pueden ajustar en balance, sin romper la estructura del contrato.

---

## 7) Técnicas especiales
- Técnicas especiales sin entrada de valor (ej. `focus`, `defense_boost`) tienen costo base `0` de reiatsu y energía.
- Si una mecánica especial aplica multiplicador, debe hacerlo por una ruta explícita y auditada del costo final.

---

## 8) Invariantes obligatorios
1. **Consistencia UI/ejecución**: el costo mostrado al jugador debe ser igual al costo consumido.
2. **No negativos**: ningún costo final puede ser negativo.
3. **Clamp de recursos**: el consumo no puede dejar recursos por debajo de 0.
4. **Fuente única**: selector, IA y ejecución deben usar la misma función de costo final.
5. **Determinismo**: mismo estado de entrada ⇒ mismo costo resultante.

---

## 9) Criterios de aceptación (QA funcional)

### 9.1 Reiatsu 1:1
- Dado `value=500` y sin multiplicador,
- entonces `reiatsu_cost_final=500`.

### 9.2 Energía con escala 9
- `value=100` ⇒ energía 10
- `value=900` ⇒ energía 10
- `value=1000` ⇒ energía 20
- `value=2000` ⇒ energía 30

### 9.3 Energía con escala 5
- `value=100` ⇒ energía 10
- `value=600` ⇒ energía 20
- `value=1100` ⇒ energía 30
- `value=1600` ⇒ energía 40

### 9.4 Multiplicador de reiatsu
- Dado `value=700` y `mult_reiatsu=2`,
- entonces `reiatsu_cost_final=1400`.
- Energía se mantiene por su regla de escala base, salvo regla explícita en contrario.

### 9.5 Técnicas especiales
- Dado `focus` o `defense_boost` como acción especial base,
- entonces costo base reiatsu=0 y energía=0.

---

## 10) Política de cambios
Cualquier cambio futuro en costos debe:
1. actualizar este contrato,
2. mantener o actualizar los criterios de aceptación,
3. indicar si el cambio es:
   - **estructural** (rompe reglas base), o
   - **de balance** (ajusta escalas/valores sin romper estructura).

---

## 11) Resumen ejecutivo
- **Reiatsu**: proporcional directo al valor de la técnica (1:1), con multiplicadores controlados.
- **Energía**: escalado por casillas según `scale` de la técnica.
- Esta dualidad define la economía central de recursos del combate.


## 12) Próximo paso recomendado
Para implementación por fases del sistema de puntos por slot (P1/P2/E1/E2 y extensible), ver:
- `docs/TECHNICAL_DESIGN_SLOT_POINTS_V1.md`
