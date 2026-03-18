# Fase 0 — Decisiones funcionales cerradas (2026-03-18)

## Estado
**En curso (pre-aprobación):** decisiones núcleo consolidadas para arrancar implementación controlada.

---

## 1) Técnicas especiales iniciales (catálogo cerrado)

1. **Ladrón de ataque**
   - Elige una técnica ofensiva del rival.
   - El rival no podrá usarla en su siguiente turno.

2. **Ladrón de defensa**
   - Elige una técnica defensiva del rival.
   - El rival no podrá usarla en su siguiente turno.

3. **Ladrón de concentrar**
   - El rival no podrá usar `Concentrar` en su siguiente turno ofensivo.

4. **Salvaguarda principiante** (especial defensiva)
   - Reduce 50% del daño enemigo aplicable.
   - Regla de prioridad obligatoria:
     1) reducción de daño por técnica común,
     2) reducción de daño por técnica especial (Salvaguarda).
   - El porcentaje no se suma linealmente con reductora; se aplica por capas en secuencia.

---

## 2) Slots, modos y control de pruebas

### Regla oficial
- En juego oficial: 1 técnica especial por jugador.

### Parámetro de perk (mínimo)
- Se define un parámetro base (`extra_spc_slots`) para ampliar cupo especial.
- Comportamiento mínimo esperado:
  - valor base `0` => máximo especial `1`.
  - valor `1` => máximo especial `2`.

### Modos de configuración
- **Modo por slots**
  - aplica límites por `atk`, `def`, `spc`.
  - permite configurar cantidad de slots por categoría.
- **Modo libre**
  - orientado a pruebas rápidas (sin restricciones estrictas de slots).

---

## 3) Reglas de consumo de especiales

- Especial ofensiva consume `1 atk + 1 spc`.
- Especial defensiva consume `1 def + 1 spc`.
- `Concentrar` se trata como especial ofensiva.
- `Potenciar` se trata como especial defensiva.

---

## 4) Criterios de implementación para siguiente fase

- Mantener trazabilidad por `unit_key` / `team:slot` para bloqueo por objetivo.
- Separar flags de pipeline de daño:
  - efecto de técnica común,
  - efecto de técnica especial.
- Mantener logging de orden aplicado (común antes de especial).

---

## 5) Pendientes no bloqueantes

- Definir responsables finales de firma (funcional / implementación / QA) durante el avance.
- Completar checklist firmable de Fase 0 en sesión de validación conjunta.
