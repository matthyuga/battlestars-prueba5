# REGLAS_CONSUMIBLES_Y_DURABILIDAD_V1

Fecha: 2026-04-06  
Estado: Draft SSOT (Fase 0)

## 1) Reglas de consumibles por turno

1. Máximo 1 uso por tipo/color por turno.
2. No se puede repetir la misma clase/color en el mismo turno.
3. Si un uso falla validación, no consume ítem.
4. La validación ocurre antes de aplicar efecto.

---

## 2) Clasificación base de consumibles

- Recurso instantáneo:
  - `hp_potion` (25/35/50%)
  - `ec_potion` (25/35/50%)
  - `ep_potion` (25/35/50%)
  - `durability_potion` (25/35/50%)
- Buff por técnica:
  - `atk_buff` (25/35/50%)
  - `def_buff` (25/35/50%)
- Buff de stats (principalmente Torre):
  - fuerza/agilidad/inteligencia/espíritu/resistencia (+1/+2/+3 según color)

---

## 3) Duración de efectos

- `instant`: aplica y termina.
- `turns`: dura N turnos.
- `battle`: dura hasta fin de combate.
- `run`: dura toda la run (Torre).
- `permanent`: persiste fuera del combate.

---

## 4) Durabilidad

### 4.1 Equipables
- Si `durability > 0`, provee efectos.
- Si `durability == 0`, permanece en inventario pero sin bonus.
- Restauración posible mediante `durability_potion` o reparación externa.

### 4.2 Amuletos
- Durabilidad inicial: 3 usos.
- Al llegar a 0, queda inactivo (según regla de diseño futura: recarga/crafting/consumo final).

---

## 5) Orden de resolución recomendado

1. Validación de límites por turno.
2. Verificación de stock/durabilidad.
3. Consumo (decremento de stack o durabilidad).
4. Aplicación de efecto primario.
5. Aplicación de efectos secundarios.
6. Registro en log de combate y tracker de turno.

---

## 6) Casos borde obligatorios (QA)

1. Intentar usar dos veces misma poción color en el mismo turno.
2. Usar consumible sin stock.
3. Usar equipable con durabilidad 0.
4. Restaurar durabilidad en ítem no compatible.
5. Cambio de turno resetea tracker correctamente.
6. Snapshot Torre no persiste buffs temporales fuera de la run.
