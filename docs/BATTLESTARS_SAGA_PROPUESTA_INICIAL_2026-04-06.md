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

### 4.1 Torneos (regla confirmada)

Regla confirmada para implementación:

- **Incrementos acumulativos por ronda ganada.**
- El **pool inicial** se asume invertido por el jugador al inicio (salvo puntos reservados).
- Si el jugador deja puntos sin usar, esos puntos **se conservan** para reasignación táctica en rondas posteriores.
- Cada victoria de ronda otorga nuevos puntos al pool para reforzar técnicas/stats de cara al siguiente combate.

Implicación de diseño:
- La economía de torneo debe mostrarse en UI como:
  - `pool_actual`,
  - `puntos_ganados_ronda`,
  - `puntos_sin_asignar`.

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
6. Torre del Cielo v1 (bloques C y B primero, sin tabla cerrada de drops).
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

- **(Resuelto)** Bonus de torneo: acumulativos por ronda ganada.
- **Pendiente fase posterior**: probabilidades exactas de drop por bloque en Torre.
  - Se implementará primero una **tabla de tipos de premio** (loot/drop, buff, personaje, ítem/poción consumible o permanente, tickets C/B/A).
  - El tuning de probabilidades se cierra cuando el modo ya esté jugable.
- **Pendiente diseño de progresión**: permanencia de personajes temporales en Torre.
  - Línea propuesta: personajes temporales pueden volverse permanentes al cumplir quests/desafíos opcionales de desempeño/protección de equipo.
- **Pendiente balance alto tier**: topes y/o soft caps de puntos por modo.
  - Decisión: priorizar calibración de tiers bajos (C/B/A) antes de cerrar límites de tiers altos.

---

## 9) Tabla inicial de balance (tiers bajos C/B/A)

> Objetivo: tener una primera versión operativa para QA interna.  
> Nota: valores sujetos a tuning tras primeras 20-30 corridas por modo.

### 9.1 Duelo libre (pool total por tier)

| Tier | Pool total sugerido | Comentario |
|---|---:|---|
| C | 1,000 | Entrada rápida para pruebas base. |
| B | 5,000 | Aumenta complejidad sin romper ritmo. |
| A | 10,000 | Punto de transición antes de escalas altas. |

### 9.2 Torneos (acumulativo por ronda ganada)

Regla común:
- Pool base inicial: 400 (200 técnicas + 100 atributo principal + 100 libre).
- Cada ronda ganada suma puntos al pool.
- Los puntos sin usar se conservan para la siguiente ronda.

#### Torneo Tier C (16 jugadores)

| Etapa | Premio de ronda | Pool acumulado de referencia* |
|---|---:|---:|
| Inicio | — | 400 |
| Gana R16 | +600 | 1,000 |
| Gana R8 | +800 | 1,800 |
| Gana R4 | +1,000 | 2,800 |
| Campeón (Final) | +1,500 | 4,300 |

#### Torneo Tier B (32 jugadores)

| Etapa | Premio de ronda | Pool acumulado de referencia* |
|---|---:|---:|
| Inicio | — | 2,000 (400 + 1,600 de entrada tier B) |
| Gana R32 | +1,000 | 3,000 |
| Gana R16 | +1,500 | 4,500 |
| Gana R8 | +2,000 | 6,500 |
| Gana R4 | +2,500 | 9,000 |
| Campeón (Final) | +3,000 | 12,000 |

#### Torneo Tier A (32 jugadores)

| Etapa | Premio de ronda | Pool acumulado de referencia* |
|---|---:|---:|
| Inicio | — | 5,000 (400 + 4,600 de entrada tier A) |
| Gana R32 | +1,500 | 6,500 |
| Gana R16 | +2,000 | 8,500 |
| Gana R8 | +2,500 | 11,000 |
| Gana R4 | +3,000 | 14,000 |
| Campeón (Final) | +3,500 | 17,500 |

\* El acumulado de referencia asume gasto 0 entre rondas (solo para lectura rápida).  
En runtime real puede variar según gasto en técnicas/stats.

### 9.3 Torre del Cielo (MVP C/B/A)

| Tier de piso | Ganancia por piso | Bloques MVP |
|---|---:|---|
| C | +50 | 2 bloques (1-20) |
| B | +150 | 3 bloques (21-50) |
| A | +250 | 4 bloques (51-90) |

Implementación MVP:
- Lanzar primero pisos 1-50 (C/B).
- Habilitar A (51-90) tras validar estabilidad y ritmo de progresión.

---

## 10) Conversión de estrellas por personajes (dos propuestas)

Se documentan ambas opciones para decidir en playtest interno.

### Propuesta 1 — Escalonada moderada (enfoque económico estable)

Conversión de duplicados a estrellas:
- Duplicado C: +10
- Duplicado B: +25
- Duplicado A: +60
- Duplicado S: +140
- Duplicado SS: +320
- Duplicado SSS: +700
- Duplicado IV: +1,500

Costo de compra en tienda:
- Personaje B: 120 estrellas
- Personaje A: 300 estrellas
- Personaje S: 800 estrellas
- Personaje SS: 1,800 estrellas
- Personaje SSS: 4,000 estrellas
- Personaje IV: 8,500 estrellas

Perfil:
- Menor inflación.
- Progreso más gradual.
- Menos riesgo de saltar tiers demasiado rápido.

### Propuesta 2 — Escalonada agresiva (enfoque progreso rápido)

Conversión de duplicados a estrellas:
- Duplicado C: +20
- Duplicado B: +50
- Duplicado A: +120
- Duplicado S: +260
- Duplicado SS: +550
- Duplicado SSS: +1,200
- Duplicado IV: +2,500

Costo de compra en tienda:
- Personaje B: 100 estrellas
- Personaje A: 240 estrellas
- Personaje S: 650 estrellas
- Personaje SS: 1,400 estrellas
- Personaje SSS: 3,000 estrellas
- Personaje IV: 6,500 estrellas

Perfil:
- Recompensa más alta por torneo/duplicado.
- Sensación de avance más rápida.
- Mayor riesgo de acortar demasiado el ciclo de desbloqueo.

### Recomendación operativa

- Empezar con **Propuesta 1** en producción interna.
- Correr 2-3 sesiones de QA con telemetría de:
  - estrellas/hora,
  - tiempo promedio para primer desbloqueo A/S,
  - tasa de frustración por duplicados.
- Si el avance se siente lento, mover parcialmente hacia Propuesta 2.
