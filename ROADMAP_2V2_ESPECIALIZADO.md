# Roadmap especializado 2vs2 (sin stats ni ítems)

## Objetivo
Entregar un **modo 2vs2 jugable de punta a punta** con estabilidad (store-safe), manteniendo compatibilidad con 1v1 durante la migración.

---

## Estado actual (hasta Fase C)

### ✅ Base de datos de combate por unidades/equipos
- Ya existe soporte de `teams`, `active`, `unit_key`, parseo de keys y helpers de alive/KO por unidad.
- Ya existe daño por `target_key` y `DamagePlan` multi-target.
- Ya existe condición de derrota por equipo (`team_alive_count == 0`).

### ✅ Fase A4 (KO/auto-switch/victoria por equipo)
- KO unitario funcional.
- Auto-advance de activo funcional al caer la unidad activa.
- Victoria por equipo funcional (cuando no quedan unidades vivas).

### ✅ Fase B (UI táctica jugador)
- B.1 selección de target mínima.
- B.2 split manual por paquetes.
- B.3 fallbacks (`single_target` / `split_equal`).

### ✅ Fase C (IA multi-unidad)
- C.1 priorización de targets (HP + amenaza).
- C.2 uso de contexto reflect en decisión táctica.
- C.3 política burst vs split de IA.

---

## Scripts ya involucrados (núcleo actual)

### Facade / estado de combate
- `game/01B_BATTLE_STATE_FACADE.rpy`
  - Modelo `teams/active/turn`.
  - `bs_unit_key`, `bs_parse_unit_key`, `bs_get_unit_by_key`.
  - `bs_get_valid_target_keys`, `bs_resolve_target_keys`.
  - `bs_make_damage_plan`, `bs_apply_damage_plan`, `bs_apply_damage_to_unit_key`.
  - KO/avance activo y helpers de victoria por equipo.

### Inicio de batalla
- `game/04b_battle_startV2.rpy`
  - Actualmente inicializa equipos en modo single-team compat (`bs_init_single_teams`).
  - Configura actor inicial/turn owner.

### Selección de personajes
- `game/04A_BATTLE_CHARACTER_SELECTV3.rpy`
  - Actualmente selecciona 1 personaje jugador y 1 enemigo (flujo 1v1).

### Turno ofensivo del jugador
- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
  - UI de target/split para jugador, construcción de `offensive_damage_plan`.

### Resolución ofensiva del jugador
- `game/4/j/04C_OFFENSIVE_RESOLVEV1.rpy`
  - Aplica plan/target por fallback chain.

### Turno ofensivo IA
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
  - Heurísticas C.1/C.2/C.3.
  - Construye y aplica `enemy_damage_plan` con fallback.

### Flujo defensivo
- `game/4/j/04D_DEFENSIVE_CORE.rpy`
- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
  - Aún muy orientado a flujo simple (1 unidad activa por lado por turno).

### Fin de combate
- `game/04e_battle_end_result.rpy`
  - Evalúa derrota/victoria usando `bs_is_team_defeated(...)`.

---

## Lo que falta para 2vs2 jugable real

## M1 — Inicialización 2vs2 real
**Falta:** crear init de equipos dobles (2 slots por lado) y usarlo en `battle_start`.

### Entregables
- Nuevo helper en facade (ejemplo):
  - `bs_init_teams(player_units=[...], enemy_units=[...])`
- `battle_start` usando ese helper cuando modo = `2v2`.

## M2 — Selección/draft 2+2
**Falta:** selección de 2 personajes jugador + 2 IA.

### Entregables
- Flujo de selección por slots:
  - `player_slot_0`, `player_slot_1`
  - `enemy_slot_0`, `enemy_slot_1` (fijo o elegido por IA/pool)
- Validación básica (sin duplicados si así se define).

## M3 — Orden de turnos por unidad
**Falta:** scheduler de turnos 2vs2 explícito (no solo alternancia player/enemy).

### Entregables
- Política de turnos MVP (ejemplo round-robin por slot):
  - `player:0 -> enemy:0 -> player:1 -> enemy:1`
- Salto automático de slots KO.
- Integración con `bs_get_turn_ctx / bs_set_turn_ctx`.

## M4 — Actor activo real en UI del jugador
**Falta:** que ofensiva/defensiva use claramente la unidad activa del turno.

### Entregables
- Mostrar nombre/slot activo en popup/hud.
- Asegurar que costos, cooldowns, logs y acciones se atribuyan al `owner_slot`.

## M5 — HUD mínimo 2vs2
**Falta:** panel de 2 unidades por equipo visible en combate.

### Entregables
- HP/KO por slot.
- Resaltado de unidad activa.
- Marcador de turn owner/slot.

## M6 — Defensa en contexto multi-unidad
**Falta:** definir regla defensiva de 2vs2.

### Entregables (MVP sugerido)
- Defiende la unidad objetivo principal.
- Si hay split, cada entrada del plan se resuelve por target (sin cover avanzado aún).

## M7 — IA por slot/unidad
**Falta:** decidir arquitectura de IA 2vs2.

### Opción recomendada MVP
- Mantener una IA de equipo, pero ejecutar decisiones por `owner_slot`.
- A futuro: IA por unidad si se necesita especialización.

## M8 — QA de regresión 1v1/2v2
**Falta:** checklist sistemático de pruebas funcionales.

### Casos mínimos
- 1v1 intacto (inicio, daño, reflect, fin).
- 2v2:
  - KO slot activo + auto-switch.
  - KO de ambos aliados => derrota.
  - split manual jugador (2 targets vivos).
  - split/burst IA sin romper defensa ni turnos.

---

## Plan sugerido por tandas (PRs chicos)

### PR-2v2-01
- Facade: `bs_init_teams(...)` + wiring modo 2v2 en `battle_start`.

### PR-2v2-02
- Selección de personajes 2+2 (UI simple de slots).

### PR-2v2-03
- Scheduler de turnos por unidad (`owner_slot` real).

### PR-2v2-04
- HUD mínimo 2vs2 + actor activo visible.

### PR-2v2-05
- Ajuste de defensa multi-target MVP.

### PR-2v2-06
- QA hardening + fixes de regresión.

---

## Definición de “2vs2 MVP listo para jugar”
Se considera listo cuando:
1. Se seleccionan 2 personajes del jugador y 2 de IA.
2. El combate inicia con 4 unidades vivas en equipos correctos.
3. Turnos rotan por unidad con salto de KO.
4. Jugador puede atacar con target/split funcional.
5. IA decide foco/split sin romper flujo.
6. Fin de combate ocurre al caer ambos miembros de un team.
7. El modo 1v1 sigue funcionando sin cambios de UX críticos.

---

## Nota operativa (GitHub/sincronización)
- Este roadmap se deja en repo para que puedas sincronizar directo.
- Si tu remote está configurado, con:
  - `git push origin <tu-rama>`
- Si no está configurado:
  - `git remote add origin <url-del-repo>`
  - `git push -u origin <tu-rama>`

