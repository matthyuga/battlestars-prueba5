# ECONOMÍA DE PROGRESIÓN — DROPS, TIENDA, TORNEOS Y ASCENSIÓN (V1)

Fecha: 2026-04-07  
Estado: Propuesta operativa lista para implementación incremental

---

## 1) Objetivo

Definir una economía clara y escalable para:

1. **Duelos y Torre del Cielo** (oro + materiales + chance de personaje).
2. **Tienda de materiales** (stock limitado y control anti-abuso).
3. **Torneos Tier C/B/A** (recompensas por posición).
4. **Ascensión de tier por alquimia** (cadena 5:1 por rareza).

La propuesta está diseñada para convivir con:
- personajes gratuitos/rotativos,
- personajes propios (progresión completa),
- compra de personajes altos mediante **estrellas**,
- y progresión por materiales + oro para ascensión.

---

## 2) Principios de diseño

1. **Progresión por contenido**: mayor dificultad => mejor botín.
2. **Ritmo controlado**: early game con comunes; mid/late con raros/especiales/épicos.
3. **Múltiples rutas**: drops, torneos y tienda (evitar bloqueo por RNG).
4. **Escasez saludable**: stock limitado para raros+.
5. **Legibilidad**: porcentajes y rangos simples de tunear.

---

## 3) Torre del Cielo — Tabla de drops por tier de piso

### 3.1 Supuestos base

- Cada victoria otorga:
  - **Oro base** (según tier de piso).
  - **1 tirada de loot principal**.
- Si el combate es de **jefe**, se añade:
  - **1 tirada extra de jefe**.

---

### 3.2 Pisos normales

| Tier piso | Oro por victoria | Material común | Material raro | Material especial | Material épico | Chance personaje | Pool de personaje sugerido |
|---|---:|---:|---:|---:|---:|---:|---|
| C | 120–220 | 65% | 20% | 4% | 0% | 0.5% (Tier C) | C / B (muy baja) |
| B | 240–420 | 35% | 35% | 12% | 2% | 1.0% (Tier C/B) | C / B |
| A | 450–750 | 15% | 30% | 22% | 6% | 1.8% (Tier B/A) | B / A |
| S | 800–1250 | 8% | 20% | 26% | 10% | 2.5% (Tier A/S) | A / S |
| SS | 1300–1900 | 4% | 15% | 24% | 14% | 3.2% (Tier S/SS) | S / SS |
| SSS | 2000–3000 | 2% | 10% | 20% | 18% | 4.0% (Tier SS/SSS) | SS / SSS |
| IV | 3200–5000 | 0% | 6% | 16% | 22% | 5.0% (Tier SSS/IV) | SSS / IV |

Notas:
- “Chance personaje” debe disparar un solo drop de personaje por tirada.
- Se recomienda tabla de exclusión para no repetir personaje ya obtenido en la misma run.

---

### 3.3 Tirada extra de jefe

| Tier jefe | Raro | Especial | Épico | Material de ascensión del tramo | Chance personaje |
|---|---:|---:|---:|---:|---:|
| C | 40% | 8% | 1% | 5% (C→B) | 1.0% (C) |
| B | 45% | 14% | 3% | 8% (B→A) | 1.5% (B) |
| A | 35% | 22% | 7% | 10% (A→S) | 2.0% (A) |
| S | 25% | 28% | 12% | 12% (S→SS) | 2.5% (S) |
| SS | 18% | 30% | 16% | 14% (SS→SSS) | 3.0% (SS) |
| SSS | 12% | 28% | 22% | 16% (SSS→IV) | 3.5% (SSS) |
| IV | 8% | 24% | 28% | 18% (núcleo IV) | 4.0% (IV) |

Notas:
- La tirada de jefe es independiente de la tirada normal del piso.
- Si se quiere mayor “epicidad”, se puede agregar una mini-probabilidad de “doble drop”.

---

## 4) Tienda de materiales (oro)

### 4.1 Stock y precios base

| Material | Precio unitario (oro) | Stock diario | Stock semanal |
|---|---:|---:|---:|
| Común | 250 | 30 | — |
| Raro | 1,200 | 10 | 40 |
| Especial | 4,500 | 5 | 20 |
| Épico | 14,000 | 2 | 8 |
| Legendario (futuro) | 40,000 | 0 | 3 |
| Mítico (futuro) | 95,000 | 0 | 1 |

### 4.2 Reglas recomendadas

1. **Reset diario**: común.
2. **Reset semanal**: raro+.
3. **Escasez por rareza**: a mayor rareza, menor stock.
4. **Control anti-abuso**: cada compra del mismo material en el mismo ciclo incrementa precio +8% (acumulativo suave).

---

## 5) Torneos — Recompensas Tier C, B, A

> Recompensa por posición: Campeón, Subcampeón, Semifinal.

### 5.1 Torneo Tier C

- **Campeón**:
  - Oro: 2,000
  - Materiales: 10 comunes + 3 raros
  - Personaje: 12% chance Tier B
- **Subcampeón**:
  - Oro: 1,200
  - Materiales: 6 comunes + 2 raros
  - Personaje: 4% chance Tier B
- **Semifinal**:
  - Oro: 700
  - Materiales: 4 comunes + 1 raro

### 5.2 Torneo Tier B

- **Campeón**:
  - Oro: 4,500
  - Materiales: 6 raros + 2 especiales
  - Personaje: 10% chance Tier A + 20% chance Tier B
- **Subcampeón**:
  - Oro: 2,800
  - Materiales: 4 raros + 1 especial
  - Personaje: 6% chance Tier A
- **Semifinal**:
  - Oro: 1,500
  - Materiales: 3 raros + 1 especial

### 5.3 Torneo Tier A

- **Campeón**:
  - Oro: 9,000
  - Materiales: 4 especiales + 1 épico
  - Personaje: 8% chance Tier S + 15% chance Tier A
- **Subcampeón**:
  - Oro: 5,500
  - Materiales: 3 especiales + 25% chance 1 épico
  - Personaje: 5% chance Tier S
- **Semifinal**:
  - Oro: 3,000
  - Materiales: 2 especiales + 15% chance 1 épico

---

## 6) Ascensión alquímica por materiales (5:1)

### 6.1 Cadena principal

- 5 comunes = 1 raro (**C→B**)
- 5 raros = 1 especial (**B→A**)
- 5 especiales = 1 épico (**A→S**)
- 5 épicos = 1 legendario (**S→SS**)
- 5 legendarios = 1 mítico (**SS→SSS**)
- 5 míticos = 1 infernal (**SSS→IV**)

### 6.2 Coherencia numérica acumulada

- 1 raro = 5 comunes
- 1 especial = 25 comunes
- 1 épico = 125 comunes
- 1 legendario = 625 comunes
- 1 mítico = 3,125 comunes
- 1 infernal = 15,625 comunes

Esto mantiene la fantasía de escasez en tiers altos y premia el contenido difícil.

---

## 7) Costos de forja sugeridos por tramo

| Ascenso | Material objetivo | Oro de forja |
|---|---|---:|
| C→B | Raro | 2,000 |
| B→A | Especial | 5,000 |
| A→S | Épico | 12,000 |
| S→SS | Legendario | 28,000 |
| SS→SSS | Mítico | 60,000 |
| SSS→IV | Infernal | 120,000 |

Opcionales para tuning:
- costo variable por número de ascensos ya realizados del personaje,
- costo reducido si se usa material de evento especial,
- “pity de forja” (descuento progresivo tras varios intentos).

---

## 8) Integración con estrellas y duplicados

Este modelo convive con el sistema de estrellas:

1. Duplicados -> conversión a estrellas.
2. Estrellas -> compra de personajes Tier B+.
3. Materiales + oro -> ascensión de personaje propio.

Resultado: dos rutas paralelas de progresión:
- **Adquisición** (estrellas/personajes).
- **Fortalecimiento** (forja/ascensión/pool).

---

## 9) Riesgos y mitigaciones

### Riesgo A: inflación de oro en late game
Mitigación:
- precios dinámicos en tienda,
- sinks de oro (forja, expansión de pool, mantenimiento).

### Riesgo B: bloqueo por RNG de material específico
Mitigación:
- tienda con stock limitado,
- drop de jefe con probabilidad acumulativa suave (pity).

### Riesgo C: power creep acelerado por torneos
Mitigación:
- caps por temporada,
- tickets de entrada,
- control de frecuencia por jugador.

---

## 10) Checklist mínimo para implementación

1. Definir tablas de drop en dataset (JSON/py dict).
2. Integrar tirada normal + tirada de jefe.
3. Implementar stock diario/semanal de tienda.
4. Implementar fórmula de precio dinámico (+8% por compra en ciclo).
5. Implementar forja 5:1 en UI de pentagrama.
6. Registrar auditoría de economía (oro/materiales/personajes).

---

## 11) Siguiente paso recomendado

Cerrar tres presets de balance para playtest:

- **Casual**: más oro, más drops, tienda más generosa.
- **Normal**: valores de esta propuesta.
- **Hardcore**: menos oro, más escasez, costos de forja más altos.

Con esto se puede ajustar rápido sin reescribir reglas.
