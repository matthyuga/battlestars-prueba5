# Contrato de coherencia — Daño, HP y Pool por Tier (v1)

Fecha: 2026-04-15  
Estado: Base operativa para duelos libres/rápidos (iterable).

---

## 1) Principio de diseño

- **Pool** = capacidad táctica disponible (distribución de técnicas/parámetros).
- **HP** = castigo que un héroe puede absorber antes de caer.
- No deben ser iguales: el HP escala con un factor por tier para controlar la duración de combates.

---

## 2) Objetivo de ritmo de combate

En espejo de tier (mismo tier vs mismo tier):

- Turno normal: **8%–12%** de HP rival.
- Turno fuerte (combo/sinergia): **18%–25%** de HP rival.

Regla de tuning inicial:

- C/B: combates ágiles pero no explosivos.
- A/S+: más margen táctico y menos burst instantáneo.

---

## 3) Pool de técnicas por tier (base)

| Tier | Pool técnicas |
|---|---:|
| C | 1,000 |
| B | 5,000 |
| A | 10,000 |
| S | 50,000 |
| SS | 100,000 |
| SSS | 500,000 |
| IV | 1,000,000 |

---

## 4) HP recomendado (coherencia HP/Pool)

| Tier | Factor HP/Pool | HP recomendado |
|---|---:|---:|
| C | x5 | 5,000 |
| B | x5 | 25,000 |
| A | x6 | 60,000 |
| S | x7 | 350,000 |

Para SS/SSS/IV se mantiene x7 como base inicial hasta cierre de tuning alto tier.

---

## 5) Recursos por tier (v1)

### Regla especial
- **Durabilidad y cubre** se habilitan desde **Tier A**.
- En **D/C/B** ambos se fuerzan a 0.

### Tabla operativa

| Tier | HP | EP | EC | Durabilidad | Cubre |
|---|---:|---:|---:|---:|---:|
| C | 5,000 | 15,000 | 1,000 | 0 | 0 |
| B | 25,000 | 75,000 | 5,000 | 0 | 0 |
| A | 60,000 | 180,000 | 10,000 | 5,000 | 5,000 |
| S | 350,000 | 1,000,000 | 50,000 | 30,000 | 30,000 |

---

## 6) Descansar (táctico, no curación fuerte)

Base recomendada:

- HP: **3%** (o 0% en variantes más duras).
- EP: **20%**.
- EC: **20% + 2 escalas**.

Regla prudente:

- si el héroe está en `<=25% HP`, no aumentar recuperación de HP (solo EP/EC).

Nota: descanso prioriza EP/EC para mantener tensión y evitar duelos infinitos.

---

## 7) Técnicas por héroe

Cada héroe mantiene su perfil técnico por `config` + `build`:

- `mode`: `virgen | preconfig`
- `pool_total`
- `pool_spent_off`
- `pool_spent_def`
- `tech_points` (por técnica)

Resolución de combate:
- `virgen`: arranca sin preasignación técnica.
- `preconfig`: puede cargar preset externo por héroe/tier (`bs_get_hero_tech_preset_v1`) o usar configuración guardada.

---

## 8) Criterios de validación mínima

1. C espejo: KO esperado en 7–10 turnos promedio.
2. B espejo: KO esperado en 8–10 turnos promedio.
3. A espejo: KO esperado en 9–12 turnos promedio.
4. S espejo: KO esperado en 10–13 turnos promedio.
5. En C/B no debe aparecer daño por cubre/durabilidad (siempre 0).
6. Daño normal no debe superar 12% de HP salvo excepciones explícitas.
7. Combo no debe superar 25% salvo eventos especiales claramente marcados.

---

## 9) Estado de implementación

Aplicado en runtime de preparación/duelo:

- pools por tier,
- stats por tier,
- reglas de daño objetivo (guardadas como payload de combate),
- perfiles técnicos por héroe con modo virgen/preconfig.

Pendiente siguiente iteración:

- cerrar tabla de daño objetivo por técnica,
- calibrar IA para respetar banda normal/combo por tier,
- smoke comparativo Win7/Win10 con 10+ duelos por tier C/B.
