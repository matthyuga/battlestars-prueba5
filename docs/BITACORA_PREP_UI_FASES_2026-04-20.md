# Bitácora de avance — Preparación/Roster (Fases 0→4)
Fecha: 2026-04-20

## Objetivo de esta bitácora
Dejar registro del estado actual para retomar en otra sesión sin perder contexto.

---

## ✅ Completado

### Fase 0 — Contrato de nomenclatura (UX)
- Se unificó el lenguaje de interfaz para evitar ambigüedad:
  - `Héroe activo` → `Jugador 1`
  - `Equipo`/`Equipo seleccionado` → `Alineación`/`Alineación del duelo`
  - Botones: `Elegir` → `Asignar J1`, etc.

### Fase 1 — Interacción por casillas (base)
- La selección en roster ahora comunica intención de slot:
  - Acción primaria `Asignar J1`.
  - En 2v2 aparece acción secundaria explícita para J2.
- Se añadieron lecturas visibles de slots (`J1/J2`) en pantallas de preparación y configuración.

### Fase 2 — Sincronización de estado (bug principal)
- Se corrigió la desincronización entre `Jugador 1` y `Alineación`:
  - `bs_saga_set_prep_hero(...)` ahora normaliza party y coloca al héroe elegido como slot J1.
  - En 1v1, la acción secundaria evita estados ambiguos delegando a asignación de J1.
  - En 2v2 se protege el flujo para no quitar J1 desde acciones de J2.

### Fase 3 — Controles de slots 2v2
- Se agregaron acciones directas:
  - `Promover J2 → J1`
  - `Quitar J2`
- Nuevos helpers:
  - `bs_saga_promote_prep_j2_to_j1()`
  - `bs_saga_clear_prep_j2_slot()`

### Fase 4 — Integración de flujo (prep → config → pre-combate)
- Se integró el estado de casillas en:
  - Sala de preparación
  - Configurar héroe
  - Pre-combate
- En pre-combate 2v2 se muestra estado de slots `completo/incompleto`.
- Ajuste semántico en validación: `Alineación completa` (antes “equipo completo”).

---

## 📌 Estado funcional actual
- El flujo principal de selección/alineación está operativo.
- El bug reportado de mismatch `Jugador 1` vs héroes del party quedó cubierto por la sincronización de Fase 2.
- La UX ya comunica mejor la intención de slots para 2v2.

---

## 🔧 Pendiente (pulido)
1. Pulir layout visual de botones de casillas (espaciado/jerarquía).
2. Revisar microcopys finales (consistencia entre “Alineación”, “Casillas”, “J1/J2”).
3. Revisar edge-cases UX:
   - cambios rápidos de modo 1v1 ↔ 2v2
   - promoción J2→J1 repetida
   - estado cuando J2 está vacío y se pulsa acciones de slot
4. Smoke QA manual final del flujo completo:
   - Lobby → Preparación → Configurar héroe → Pre-combate.

---

## ▶️ Recomendación para próxima sesión
Entrar directo a “fase de pulido”:
- Ajustes visuales finos.
- QA manual guiado por checklist.
- Cierre con correcciones menores de UX.

