# Ficha Técnica v1 — Escalado de Técnicas, Costos y Poder General (CP)

Fecha: 2026-03-24  
Estado: Propuesta base lista para implementación/iteración.

## 1) Objetivo

Definir una arquitectura de escalado que:

- Mantenga el sistema **flat** como base de progreso (stats, principal, técnica).
- Permita crecimiento fuerte por tiers (D/C/B/A/S/SS/SSS) sin romper economía.
- Conecte daño, consumo de reiatsu, consumo de energía y CP general.
- Use **escalado por técnica individual** (cada técnica tiene su propia curva/costos).

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

## 3) Sistema de escalado por técnica (regla oficial)

**Regla central:** cada técnica ofensiva/defensiva tiene su propia tabla de escalado.

- La arquitectura general se mantiene (pool, stats, principal, tiers).
- El costo y progresión final de cada técnica se define por su tabla individual.
- Si se crea una técnica nueva, se agrega al repo con su propia tabla y se registra en esta ficha.

### 3.1 Convención de tabla por técnica

Cada tabla define:

1. `ValorTécnica` (100, 200, 300...)
2. `CostoReiatsu` (normalmente ligado al valor)
3. `CostoEnergía` por hitos específicos
4. `Escala` de referencia (4, 5, 6, 7, 9, etc.)

---

## 4) Catálogo base de técnicas y su escalado

## 4.1 Ofensivas

### A) Ataque Extra (`escala 9`)

- Hitos de energía:
  - Valor 100 => Energía 10
  - Valor 1000 => Energía 20
  - Valor 2000 => Energía 30
- Reiatsu: `R = ValorTécnica`.

### B) Técnica Extra (`escala 7`)

- Hitos de energía:
  - 100 => 20
  - 800 => 30
  - 1400 => 40
  - 2100 => 50
- Reiatsu: `R = ValorTécnica`.

### C) Ataque Reductor (`escala 5`)

- Hitos de energía:
  - 100 => 40
  - 600 => 50
  - 1100 => 60
  - 1600 => 70
  - 2100 => 80
- Reiatsu: `R = ValorTécnica`.

### D) Ataque Directo (`escala 6`)

- Hitos de energía:
  - 100 => 30
  - 700 => 40
  - 1300 => 50
  - 1900 => 60
- Reiatsu: `R = ValorTécnica`.

### E) Ataque Negador (`escala 6`)

- Hitos de energía:
  - 100 => 30
  - 700 => 40
  - 1300 => 50
  - 1900 => 60
- Reiatsu: `R = ValorTécnica`.

### F) Ataque Más Fuerte (`escala 9`)

- Hitos de energía:
  - 100 => 10
  - 1000 => 20
  - 2000 => 30
- Reiatsu: `R = ValorTécnica`.

### G) Efecto Especial ofensivo (`escala 5`)

- Hitos de energía (curva especial):
  - 100 => 500
  - 600 => 510
  - 1100 => 520
  - 1600 => 530
  - 2100 => 540
- Reiatsu: definido por diseño de la técnica/efecto; por defecto usar `R = ValorTécnica` salvo excepción documentada.

## 4.2 Defensivas

### A) Defensa Extra (`escala 9`)

- Hitos de energía:
  - 100 => 10
  - 1000 => 20
  - 2000 => 30
- Reiatsu: `R = ValorTécnica`.

### B) Defensa Más Fuerte (`escala 9`)

- Hitos de energía:
  - 100 => 10
  - 1000 => 20
  - 2000 => 30
- Reiatsu: `R = ValorTécnica`.

### C) Defensa Reductora (`escala 5`)

- Hitos de energía:
  - 100 => 40
  - 600 => 50
  - 1100 => 60
  - 1600 => 70
  - 2100 => 80
- Reiatsu: `R = ValorTécnica`.

### D) Defensa Reflectora (`escala 4`)

- Hitos de energía:
  - 100 => 50
  - 500 => 60
  - 900 => 70
  - 1300 => 80
  - 1700 => 90
  - 2100 => 100
- Reiatsu: `R = ValorTécnica`.

### E) Efecto Especial defensivo (`escala 5`)

- Hitos de energía (curva especial):
  - 100 => 500
  - 600 => 510
  - 1100 => 520
  - 1600 => 530
  - 2100 => 540
- Reiatsu: definido por diseño de la técnica/efecto; por defecto usar `R = ValorTécnica` salvo excepción documentada.

---

## 5) Fórmula de costos y fallback (solo para técnicas nuevas)

Para técnicas nuevas sin tabla aprobada todavía, usar temporalmente:

- `R = ValorTécnica`
- `E_base = 10 + 10 * floor((ValorTécnica - 1) / 1000)`

Esto es **solo fallback** hasta que la técnica tenga su tabla propia en repo.

---

## 6) Tiers de poder y caps por técnica

### 6.1 Tiers por nivel

- D: 1–19
- C: 20–39
- B: 40–59
- A: 60–79
- S: 80–99
- SS: 100–299
- SSS: 300–499
- (L500: ápice SSS)

### 6.2 Cap recomendado por técnica ofensiva

- D: 900
- C: 2,000
- B: 5,000
- A: 12,000
- S: 25,000
- SS: 80,000
- SSS: 200,000

### 6.3 Cap recomendado por técnica defensiva

- D: 1,000
- C: 2,300
- B: 5,500
- A: 13,000
- S: 27,000
- SS: 90,000
- SSS: 240,000

### 6.4 Aplicación PvP/PvE con misma base

- La **base** de cap por registro es única.
- El valor final por modo se muestra como `(PvP/PvE)`.
- Detalle completo por registros en: `docs/PLANILLA_CAPS_TECNICAS_REGISTROS_V1.md`.

---

## 7) Eficiencia de energía por tier

La energía escala por eficiencia moderada (sin multiplicación agresiva tipo CP):

- D/C/B: 0%
- A: 5%
- S: 10%
- SS: 18%
- SSS: 25%

Fórmula:

- `E_final = ceil(E_base * (1 - reduccion_tier))`

> `E_base` sale de la tabla de cada técnica (no de una fórmula global, salvo fallback).

---

## 8) Fórmula de Poder General (CP)

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

## 9) Curva de CP objetivo (hitos)

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

## 10) Relación de CP para diseño de enemigos

Respecto al CP del jugador en su nivel/tramo:

- Mob normal: 0.70x–0.90x
- Elite: 1.00x–1.20x
- Mini-boss: 1.25x–1.45x
- Boss de zona: 1.50x–1.80x
- Boss de saga: 2.00x–2.60x
- Boss final: 2.80x–3.50x

---

## 11) Orden oficial de cálculo

Recalcular en este orden:

1. Base del personaje
2. Stats permanentes
3. Bono de atributo principal
4. Ítems permanentes
5. Buffs/nerfs temporales
6. Ajustes contextuales de combate
7. Costos finales de técnica
8. CP final

Eventos que fuerzan recálculo:

- Subida de registro
- Asignación/reasignación de stats
- Respec
- Equipar/quitar ítems
- Aplicar/caducar buffs/nerfs
- Inicio/fin de combate

---

## 12) Límites de stacking

- Bono ofensivo temporal total: cap +35%
- Bono defensivo temporal total: cap +40%
- Reducción de daño acumulada: cap 75%
- Evasión acumulada: cap 60%

---

## 13) Gobernanza de nuevas técnicas

Proceso mínimo obligatorio para cada nueva técnica:

1. Subir imagen/tabla de escalado al repo.
2. Registrar la técnica en esta ficha:
   - tipo (ofensiva/defensiva)
   - escala
   - hitos de energía
   - regla de reiatsu
3. Definir cap por tier si difiere de estándar.
4. Validar en test de economía (energía/reiatsu) y DPS/mitigación.

---

## 14) Estado de implementación sugerido

Fase v1 (ya):

- tablas de técnicas base (ofensivas + defensivas)
- costos finales por técnica + eficiencia tier
- CP base + multiplicador tier
- orden de recálculo

Fase v1.1:

- ajustes finos por tipo de técnica (burst/sustain/control)
- curva de bosses de saga por ventanas de peligro
- telemetría de consumo medio por combate
