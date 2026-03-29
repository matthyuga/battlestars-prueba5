# Resumen de ajustes recientes — IA Concat + Forzar (Ofensiva/Defensiva)

Este documento deja trazabilidad de los últimos cambios funcionales antes de iniciar el rediseño visual del panel/HUD.

## 1) Objetivo de los ajustes

Unificar reglas de **compatibilidad entre `Concat` y modos `Forzar`** para evitar combinaciones inválidas en runtime y en UI.

- Si una técnica ya está incluida como técnica inicial por `Concat`, no debe poder forzarse como técnica especial en ese mismo estado.
- Mantener coherencia entre:
  - modo global,
  - override por unidad,
  - resolución efectiva,
  - y construcción final del plan IA.

---

## 2) Ofensiva — reglas finales

### 2.1 Modos de concat ofensivo
- `off`
- `level1_attack`
- `level1_tech`
- `level2_full`

### 2.2 Modos forzados ofensivos disponibles
- `force_reducer`
- `force_stronger`
- `force_direct`
- `force_noatk`
- `force_extra_attack`
- `force_extra_tech`

### 2.3 Regla de bloqueo clave
- `force_extra_attack` y `force_extra_tech` **solo aplican cuando concat ofensivo efectivo es `off`**.
- Si concat está activo (`level1_*` o `level2_full`), esos modos se degradan a `normal` o se filtran del ciclo UI.

### 2.4 Efecto en el plan ofensivo
- Concat `off`: el finisher puede incluir `extra_attack`/`extra_tech` como especiales adicionales.
- Concat activo: el plan usa la estructura de concat seleccionada y no permite forzar esas técnicas iniciales como especiales.

---

## 3) Defensiva — reglas finales

### 3.1 Concat defensivo
- Booleano efectivo (`ON/OFF`, con posibilidad de heredar por unidad).
- Cuando concat está `ON`, el plan defensivo ya incluye `def_extra` como técnica inicial.

### 3.2 Modos forzados defensivos disponibles
- `force_extra`
- `force_reduct`
- `force_reflect`
- `force_strong` (agregado en los últimos ajustes)

### 3.3 Regla de bloqueo clave
- `force_extra` **solo aplica cuando concat defensivo efectivo está `OFF`**.
- Si concat está `ON` (o `Heredar` que resuelve a ON), `force_extra` se bloquea/normaliza para evitar redundancia.

### 3.4 Defensa fuerte en forzar
- Se agregó soporte para `force_strong`.
- Resolver `force_strong` produce `defense_strong_block` en planificación defensiva.

---

## 4) Capas donde se aplicó la lógica

Para ambas ramas (ofensiva/defensiva), la validación se aplicó en estas capas:

1. **Core HUD global**
   - validación en get/set/cycle de modos forzados.
2. **Perfil por unidad**
   - resolución efectiva (`inherit` + fallback global).
   - bloqueo/normalización de estados incompatibles.
3. **UI por unidad**
   - filtrado de opciones inválidas en el ciclo de botones.
4. **AI planner / core reactivo**
   - guardas defensivas adicionales para evitar ejecutar combinaciones inválidas aunque llegue estado viejo.

---

## 5) Estado funcional listo para próxima sesión visual

Con esto queda estable la base lógica para avanzar a la parte visual:

- Los modos y reglas de compatibilidad ya están definidos y aplicados.
- El siguiente paso es rediseñar HUD/controles para hacer más clara la lectura de:
  - `Concat` global vs por unidad,
  - modos `Forzar` habilitados/bloqueados,
  - y estados efectivos (incluyendo `Heredar`).

