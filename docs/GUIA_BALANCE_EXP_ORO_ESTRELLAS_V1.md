# Guía de Balance: EXP, Oro, Diferencia de Registros y Estrellas de Desempeño (V1)

> Estado: Documento de diseño/validación para revisión de balance.
> Alcance: Duelo 1v1, combates múltiples (2v1, 1v2, 2v2) y medición por estrellas 0..30.

---

## 1) Objetivo

Definir una base clara y auditables para:

1. Recompensa de **EXP**.
2. Recompensa de **Oro**.
3. Escalado por **diferencia de registros (ΔR)**.
4. Impacto del **desempeño por estrellas (0..30)**.
5. Reglas simples para **combates múltiples** sin sobrecomplejidad.

---

## 2) Supuestos base del sistema

- Preset seleccionado: **Preset 2 (grindeo medio)**.
- Rango de estrellas de desempeño total: **0..30**.
- Diferencia de registros base: **ΔR en -5..+5** (tabla primaria).
- Para diferencias mayores a ±5, aplicar extensión por fórmula (sin tabla infinita).

### 2.1 Conversión nivel -> registro (referencia)

Regla de referencia utilizada en ejemplos:

- `registro = level // 10` (clamp entre 0 y 50).

Ejemplos:
- lvl 1 => reg 0
- lvl 10 => reg 1
- lvl 20 => reg 2
- lvl 30 => reg 3

---

## 3) Fórmula base por estrellas (Preset 2)

### 3.1 EXP base por desempeño

`EXP_base(stars) = 35 + 3.5 * stars`

- 0 estrellas => 35
- 15 estrellas => 88
- 30 estrellas => 140

### 3.2 Oro base por desempeño

`ORO_base(stars) = 15 + 2.0 * stars`

- 0 estrellas => 15
- 15 estrellas => 45
- 30 estrellas => 75

---

## 4) Tabla de riesgo por diferencia de registro (ΔR)

### 4.1 Multiplicadores de EXP por ΔR

| ΔR | Mult EXP |
|---:|---:|
| -5 | 0.15 |
| -4 | 0.25 |
| -3 | 0.40 |
| -2 | 0.60 |
| -1 | 0.82 |
|  0 | 1.00 |
| +1 | 1.25 |
| +2 | 1.55 |
| +3 | 1.90 |
| +4 | 2.30 |
| +5 | 2.80 |

### 4.2 Multiplicadores de Oro por ΔR

| ΔR | Mult Oro |
|---:|---:|
| -5 | 0.25 |
| -4 | 0.40 |
| -3 | 0.55 |
| -2 | 0.72 |
| -1 | 0.88 |
|  0 | 1.00 |
| +1 | 1.12 |
| +2 | 1.28 |
| +3 | 1.45 |
| +4 | 1.65 |
| +5 | 1.85 |

---

## 5) Grilla EXP 1v1 (Preset 2)

> Cálculo: `EXP_1v1 = EXP_base(stars) * mult_exp(ΔR)`

Tabla de referencia rápida (0⭐, 15⭐, 30⭐):

| ΔR | EXP @0⭐ | EXP @15⭐ | EXP @30⭐ |
|---:|---:|---:|---:|
| -5 | 5.25 | 13.20 | 21.00 |
| -4 | 8.75 | 22.00 | 35.00 |
| -3 | 14.00 | 35.20 | 56.00 |
| -2 | 21.00 | 52.80 | 84.00 |
| -1 | 28.70 | 72.16 | 114.80 |
|  0 | 35.00 | 88.00 | 140.00 |
| +1 | 43.75 | 110.00 | 175.00 |
| +2 | 54.25 | 136.40 | 217.00 |
| +3 | 66.50 | 167.20 | 266.00 |
| +4 | 80.50 | 202.40 | 322.00 |
| +5 | 98.00 | 246.40 | 392.00 |

---

## 6) Grilla Oro 1v1 (Preset 2)

> Cálculo: `ORO_1v1 = ORO_base(stars) * mult_oro(ΔR)`

Tabla de referencia rápida (0⭐, 15⭐, 30⭐):

| ΔR | Oro @0⭐ | Oro @15⭐ | Oro @30⭐ |
|---:|---:|---:|---:|
| -5 | 3.75 | 11.25 | 18.75 |
| -4 | 6.00 | 18.00 | 30.00 |
| -3 | 8.25 | 24.75 | 41.25 |
| -2 | 10.80 | 32.40 | 54.00 |
| -1 | 13.20 | 39.60 | 66.00 |
|  0 | 15.00 | 45.00 | 75.00 |
| +1 | 16.80 | 50.40 | 84.00 |
| +2 | 19.20 | 57.60 | 96.00 |
| +3 | 21.75 | 65.25 | 108.75 |
| +4 | 24.75 | 74.25 | 123.75 |
| +5 | 27.75 | 83.25 | 138.75 |

---

## 7) Extensión para ΔR fuera de rango (|ΔR| > 5)

Objetivo: evitar tablas infinitas y conservar progresión controlada.

### 7.1 EXP

- Si `ΔR > +5`:

`mult_exp = 2.80 * (1.20)^(ΔR - 5)`

- Si `ΔR < -5`:

`mult_exp = 0.15 * (0.80)^(-5 - ΔR)`

con piso recomendado: `mult_exp_min = 0.05`.

### 7.2 Oro

- Si `ΔR > +5`:

`mult_oro = 1.85 * (1.10)^(ΔR - 5)`

- Si `ΔR < -5`:

`mult_oro = 0.25 * (0.90)^(-5 - ΔR)`

con piso recomendado: `mult_oro_min = 0.10`.

---

## 8) Medición de estrellas por desempeño (0..30)

### 8.1 Estructura

Se recomiendan **6 categorías**, cada una en escala **0..5**.

`stars_total = sum(categoria_1..categoria_6)`

1. Ofensiva
2. Defensiva
3. Control
4. Eficiencia
5. Técnica
6. Impacto decisivo

### 8.2 Rúbrica global por categoría

- 0 = nulo
- 1 = bajo
- 2 = aceptable
- 3 = bueno
- 4 = alto
- 5 = sobresaliente

### 8.3 Indicadores sugeridos

#### Ofensiva
- % HP rival removido
- % durabilidad removida
- mayor golpe (HP/durabilidad)
- aciertos de técnicas ofensivas

#### Defensiva
- % HP preservado
- % durabilidad preservada
- mitigación efectiva (bloqueo/reducción/reflect)
- contraataque efectivo

#### Control
- negaciones/anulaciones exitosas
- uso efectivo de técnicas de control
- ítems que cancelan técnicas (si aplica)

#### Eficiencia
- gasto de energía/reiatsu relativo al resultado
- dependencia de descansar/pociones/recuperación
- premio a independencia y timing eficiente

#### Técnica
- uso correcto de especiales (focus/boost/furia)
- concatenación efectiva de técnicas
- sincronización de jugadas (timing)

#### Impacto decisivo
- jugadas que cambian el rumbo del combate
- cierres críticos
- eventos de alto impacto estratégicamente justificables

---

## 9) Reglas para combates múltiples (simple y escalable)

Para cada jugador `i`:

1. Calcular `reg_opp_prom_i` = promedio de registros del equipo rival.
2. Definir `ΔR_i = reg_opp_prom_i - reg_i`.
3. Calcular recompensa base con estrellas + ΔR como en 1v1.
4. Aplicar factor por tamaño relativo de equipos:

`m_multi = clamp((enemigos / aliados)^0.5, 0.85, 1.35)`

5. Resultado final por jugador:

`reward_i = base_por_stars * mult_ΔR_i * m_multi * (otros_factores)`

Donde `otros_factores` puede incluir resultado (victoria/derrota) y antiabuso por repetición.

### 9.1 Interpretación rápida

- 2v2 => neutro (~1.00)
- 2v1 => dúo penalizado (~0.85), solo bonificado (~1.35)
- 1v2 => simétrico al caso anterior

---

## 10) Ejemplos de combates múltiples

### Ejemplo A (2v2)

`lvl1(reg0) + lvl30(reg3) vs lvl30(reg3) + lvl10(reg1)`

- Para reg0: rival promedio = (3+1)/2 = 2 => ΔR = +2
- Para reg3 (equipo izquierdo): rival promedio = 2 => ΔR = -1
- Para reg3 (equipo derecho): rival promedio = (0+3)/2 = 1.5 => ΔR ≈ -1
- Para reg1: rival promedio = 1.5 => ΔR ≈ +1

Factor numérico: 2v2 => ~1.00.

### Ejemplo B (2v1 potencialmente abusivo)

`lvl20(reg2) + lvl30(reg3) vs lvl10(reg1)`

- Dúo (reg2/reg3) contra promedio rival 1 => ΔR negativo o neutro bajo.
- Solo reg1 contra promedio rival 2.5 => ΔR positivo.
- Factor numérico: dúo ~0.85, solo ~1.35.

Resultado esperado:
- Si gana el dúo, recompensas contenidas.
- Si gana el solo, recompensa alta proporcional al mérito.

---

## 11) Pipeline recomendado de recompensa

1. Calcular `stars_total` (0..30).
2. Obtener base por estrellas (EXP_base / ORO_base).
3. Calcular `ΔR` y multiplicador de riesgo.
4. Aplicar `m_multi` en combates múltiples.
5. Aplicar factor de resultado (victoria/derrota).
6. Aplicar antiabuso por repetición.
7. Redondear y clamplear mínimos/máximos globales de economía.

---

## 12) Checklist de QA para validar balance

- [ ] 1v1: validar tabla completa ΔR -5..+5 para 0⭐, 15⭐, 30⭐.
- [ ] |ΔR|>5: validar extensión por fórmula y pisos.
- [ ] 2v1 / 1v2: confirmar penalización/bonificación por `m_multi`.
- [ ] 2v2: confirmar neutralidad de `m_multi`.
- [ ] Revisar que no exista ruta de farmeo abusiva de Oro/EXP.
- [ ] Verificar que derrota con buen desempeño siga otorgando progreso razonable.

---

## 13) Notas de implementación práctica

- Evitar lógica duplicada: centralizar cálculo en una sola función por recurso.
- Versionar parámetros en una estructura única (`reward_config_v1`).
- Exponer valores en F1 para revisión de diseño/QA.
- Al añadir nuevas mecánicas (ítems/efectos), sumar métricas sin romper la escala 0..30.

---

## 14) Resumen ejecutivo

- Se adopta **Preset 2** como base de progresión media.
- Se documentan y separan **EXP**, **Oro**, **ΔR**, y **estrellas** con tablas auditables.
- Se propone un modelo simple de combates múltiples con `ΔR` individual + `m_multi`.
- El sistema es escalable y evita complejidad innecesaria manteniendo justicia de recompensa.

