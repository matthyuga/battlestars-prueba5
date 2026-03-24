# Ficha Técnica v1 — Escalado de Técnicas, Costos y Poder General (CP)

Fecha: 2026-03-24
Estado: Propuesta base lista para implementación/iteración.

## 1) Objetivo

Definir una arquitectura de escalado que:

- Mantenga el sistema **flat** como base de progreso (stats, principal, técnica).
- Permita crecimiento fuerte por tiers (D/C/B/A/S/SS/SSS) sin romper economía.
- Conecte daño, consumo de reiatsu, consumo de energía y CP general.
- Sea consistente para balance de mobs, élites, bosses y jefes de saga.

---

## 2) Reglas base del sistema de puntos

### 2.1 Pool técnico general

- Pool inicial técnico: **200** puntos.
- Ganancia por registro (cada 10 niveles): **+100** puntos.
- Registros máximos hasta nivel 500: **50**.
- Total técnico bruto al final (sin otros modificadores):
  - `200 + (50 * 100) = 5200`.

### 2.2 Aporte por stats (flat)

Por cada +1 punto en stat:

- Fuerza: `+100` ofensiva.
- Agilidad: `+100` defensiva.
- Resistencia: `+100` HP.
- Inteligencia: `+100` Energía.
- Espíritu: `+100` Reiatsu.
- Suerte / Carisma / Percepción: utilidad sistémica (sin aporte directo de puntos de combate).

### 2.3 Atributo principal (flat)

- El jugador elige 1 atributo principal.
- Ese atributo puede repartir **100 puntos** por punto invertido en dicho atributo, usando:
  - 25% / 50% / 75% / 100%
- Bonos posibles: Ataque, Defensa, HP, Reiatsu, Energía.
- Regla: se puede distribuir entre **hasta 4 opciones** de las 5.

---

## 3) Escalado de técnica ofensiva (modelo base)

### 3.1 Variables

- `D` = daño de la técnica.
- `R` = costo de reiatsu.
- `E` = costo de energía.

### 3.2 Fórmulas

1) **Consumo de reiatsu**

- `R = D`

2) **Consumo de energía por escalones de 1000 daño**

- `E = 10 + 10 * floor((D - 1) / 1000)`

Esto produce:

- 100–900 daño => 10 energía
- 1000–1900 daño => 20 energía
- 2000–2900 daño => 30 energía
- etc.

### 3.3 Ejemplos rápidos

- D=100 => R=100, E=10
- D=900 => R=900, E=10
- D=1000 => R=1000, E=20
- D=2000 => R=2000, E=30
- D=15000 => R=15000, E=160

---

## 4) Escalado de costos en defensa (v1)

Para técnicas defensivas se adopta misma lógica de costos para mantener simetría inicial:

- `R_def = V_def` (valor defensivo equivalente).
- `E_def = 10 + 10 * floor((V_def - 1) / 1000)`

> Nota: en v2 se puede separar costo defensivo con factor menor (ej. 0.85x) si los combates salen demasiado frágiles.

---

## 5) Tiers de poder y caps por técnica

## 5.1 Tiers por nivel

- D: 1–19
- C: 20–39
- B: 40–59
- A: 60–79
- S: 80–99
- SS: 100–299
- SSS: 300–499
- (L500: ápice SSS)

### 5.2 Cap recomendado por técnica ofensiva

- D: 900
- C: 2,000
- B: 5,000
- A: 12,000
- S: 25,000
- SS: 80,000
- SSS: 200,000

### 5.3 Cap recomendado por técnica defensiva

- D: 1,000
- C: 2,300
- B: 5,500
- A: 13,000
- S: 27,000
- SS: 90,000
- SSS: 240,000

> Defensa tiene cap ligeramente mayor por haber menos técnicas defensivas totales.

---

## 6) Eficiencia de energía por tier (sin romper economía)

La energía **sí escala**, pero no con multiplicación agresiva tipo CP.
Se usa reducción moderada de costo final:

- D/C/B: 0%
- A: 5%
- S: 10%
- SS: 18%
- SSS: 25%

Fórmula:

- `E_final = ceil(E_base * (1 - reduccion_tier))`

Esto evita “doble escalado roto” y mantiene relevancia del recurso.

---

## 7) Fórmula de Poder General (CP)

CP orienta balance global y comparación entre unidades.

Variables efectivas:

- `AtkEf`
- `DefEf`
- `HpEf`
- `ReiEf`
- `EnEf`

Fórmula base:

`CP_base = (AtkEf * 1.25) + (DefEf * 1.20) + (HpEf * 0.35) + (ReiEf * 0.30) + (EnEf * 0.45)`

Aplicación por tier:

`CP_final = CP_base * M_tier`

Multiplicadores recomendados:

- D: x1.00
- C: x1.30
- B: x1.75
- A: x2.35
- S: x3.20
- SS: x5.00 → x12.00 (rampa interna)
- SSS: x14.00 → x30.00 (rampa interna)

---

## 8) Curva de CP objetivo (hitos)

- L1: 1,000–1,400
- L10: 1,700–2,300
- L20: 2,800–3,800
- L30: 4,300–5,600
- L40: 6,300–8,200
- L50: 9,000–11,500
- L60: 12,500–16,000
- L80: 23,000–30,000
- L100: 45,000–65,000
- L150: 100,000–145,000
- L200: 160,000–240,000
- L299: 320,000–460,000
- L360: 620,000–900,000
- L400: 900,000–1,300,000
- L499/500: 1,900,000–2,800,000

---

## 9) Relación de CP para diseño de enemigos

Respecto al CP del jugador en su nivel/tramo:

- Mob normal: 0.70x–0.90x
- Elite: 1.00x–1.20x
- Mini-boss: 1.25x–1.45x
- Boss de zona: 1.50x–1.80x
- Boss de saga: 2.00x–2.60x
- Boss final: 2.80x–3.50x

---

## 10) Orden oficial de cálculo (antibugs)

Recalcular en este orden:

1. Base del personaje
2. Stats permanentes
3. Bono de atributo principal
4. Ítems permanentes
5. Buffs/nerfs temporales
6. Ajustes contextuales de combate
7. CP final

Eventos que fuerzan recálculo:

- Subida de registro
- Asignación/reasignación de stats
- Respec
- Equipar/quitar ítems
- Aplicar/caducar buffs/nerfs
- Inicio/fin de combate

---

## 11) Límites de stacking (seguridad de balance)

- Bono ofensivo temporal total: cap +35%
- Bono defensivo temporal total: cap +40%
- Reducción de daño acumulada: cap 75%
- Evasión acumulada: cap 60%

---

## 12) Criterios de ajuste (cuando testear)

Si en pruebas ocurre que:

1) Jugador queda sin energía demasiado rápido:
- bajar pendiente de E (ej. +8 por bloque de 1000 en lugar de +10), o
- aumentar eficiencia por inteligencia/espíritu.

2) Bosses mueren demasiado rápido en SS/SSS:
- subir caps por tier de enemigos,
- aumentar resistencia de reiatsu en bosses,
- revisar peso de AtkEf en CP.

3) Defensas se sienten irrelevantes:
- elevar peso DefEf (1.20 → 1.30),
- mejorar caps defensivos en S/SS/SSS,
- bajar penetración de ataques especiales.

---

## 13) Estado de implementación sugerido

Fase v1 (ya):

- Fórmulas base (D, R, E)
- Caps por tier
- CP base + multiplicador tier
- Orden de recálculo

Fase v1.1:

- Ajuste fino de eficiencia energética por inteligencia/espíritu
- Curvas separadas por tipo de técnica (burst, sustain, control)
- Balancing de bosses de saga por “ventanas de peligro”

