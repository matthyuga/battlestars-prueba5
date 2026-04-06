# Battlestars Saga — Propuesta inicial consolidada (v0)

Fecha: 2026-04-06  
Estado: Borrador de diseño

## 1) Visión

Aprovechar el sistema base existente (combate + técnicas/stats + puntos) para construir un juego con 3 modos:

1. **Duelo libre** (sandbox/pruebas/farmeo controlado).
2. **Torneos por tier** (progresión competitiva y desbloqueos).
3. **Torre del Cielo** (run de progresión larga con riesgo/recompensa).

---

## 2) Estructura de roster por tiers

- C: 30
- B: 40
- A: 57
- S: 42
- SS: 9
- SSS: 6
- IV: 4

Total actual: **188 personajes**.

---

## 3) Modos de juego

### 3.1 Duelo libre

- Formatos: 1v1 y 2v2.
- Objetivo: pruebas de builds/personajes sin presión de ranking.
- Recompensas: opcionales (oro/farm básico), sin desbloqueos grandes.

Pool por defecto sugerido por tier:
- C: 1,000
- B: 5,000
- A: 10,000
- S: 50,000
- SS: 100,000
- SSS: 500,000
- IV: 1,000,000

### 3.2 Torneos

Ruta de progresión propuesta:
- Torneo C (16): campeón recibe personaje tier B.
- Torneo B (32): campeón recibe personaje tier A.
- Torneo A (32): campeón recibe personaje tier S.

Sugerencia para duplicados:
- Convertir repetidos a **estrellas**.
- Tienda de estrellas para canjear personajes de tier superior.

### 3.3 Torre del Cielo

- Run con equipo de 5 personajes.
- Progresión por pisos y bloques de dificultad.
- Loot variable: oro, ítems, pociones, tickets torneo, personajes (permanentes o temporales por run).

Bloques por tier:
- C: 2 bloques
- B: 3 bloques
- A: 4 bloques
- S: 5 bloques
- SS: 6 bloques
- SSS: 7 bloques
- IV: 8 bloques

Capas altas: modo récord/infinito opcional tras completar IV.

---

## 4) Economía de puntos (base común)

Base de creación:
- Técnicas: 200
- Atributo principal: +100
- Distribución libre: +100
- **Total base inicial: 400**

### 4.1 Torneos (pendiente de normalización exacta)

Para implementación estable, definir explícitamente una de estas 2 reglas:

- **Regla A (incrementos acumulativos):** cada ronda superada suma puntos al pool.
- **Regla B (cap fijo por ronda):** cada ronda fija un pool máximo.

> Recomendación: usar Regla A para que la sensación de progreso sea más clara en UX.

### 4.2 Torre del Cielo (incremento por piso)

- Piso tier C: +50
- Piso tier B: +150
- Piso tier A: +250
- Piso tier S: +1,000
- Piso tier SS: +1,500
- Piso tier SSS: +5,000
- Piso tier IV: +10,000

---

## 5) Prioridad técnica recomendada

Dado el estado actual de la máquina de progresión EXP/Oro (en rediseño), se propone:

1. **Congelar temporalmente** el rediseño profundo de EXP/Oro.
2. Implementar un **MVP de Battlestars Saga** reutilizando combate + sistema de puntos.
3. Integrar recompensas por capas con feature flags:
   - v1: puntos + desbloqueo de personajes
   - v2: oro/ítems/tickets
   - v3: economía avanzada (estrellas/tienda)

---

## 6) Backlog MVP (ordenado)

1. Selector de modo (Duelo / Torneo / Torre).
2. Contrato de configuración por modo (JSON/persistencia).
3. Flujo de torneo C completo (16 participantes).
4. Conversión de duplicados a estrellas.
5. Tienda mínima de estrellas.
6. Torre del Cielo v1 (bloques C y B primero).
7. Telemetría simple (run, piso máximo, recompensas).

---

## 7) Riesgos y mitigaciones

- **Riesgo:** saltos de poder demasiado bruscos entre tiers altos.
  - Mitigación: soft caps y multiplicadores por modo.

- **Riesgo:** frustración por RNG de recompensas.
  - Mitigación: pity por bloques + conversión de duplicados.

- **Riesgo:** complejidad de balance temprano.
  - Mitigación: tablas de tuning por temporada y QA sandbox.

---

## 8) Definiciones pendientes

- ¿Los bonus de torneo son acumulativos o cap de ronda?
- ¿Probabilidades exactas de drop por bloque en Torre?
- ¿Regla de permanencia para personajes temporales en Torre?
- ¿Topes de puntos por modo para evitar desbordes en tiers altos?

