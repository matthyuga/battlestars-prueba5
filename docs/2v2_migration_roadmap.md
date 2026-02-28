# Roadmap de migración (1v1 estable + 2v2 aislado)

## Objetivo
Separar el flujo de `2v2` del flujo legado `1v1` para eliminar desincronizaciones de turnos/defensor/HUD sin romper el modo clásico.

---

## Estrategia por commits

### C1 — Router por modo + congelar legado
**Estado:** definido.

- Introducir wrappers de entrada (`battle_offensive_turn`, `battle_enemy_turn`, `battle_defensive_turn`) que enrutan por `battle_team_mode`.
- Mover labels actuales a `*_legacy_entry` sin tocar su lógica.
- Crear stubs `*_2v2_entry` para preparar la migración incremental.
- No cambiar reglas de combate en este commit.

**Resultado esperado:** `1v1` sigue idéntico; `2v2` queda con punto de entrada aislable.

---

### C2 — Contexto único de daño entrante + popup 2v2 consistente (**en curso siguiente**)
**Estado:** plan detallado listo (este documento).

#### 1) Meta técnica C2
Unificar cómo se decide y se muestra el defensor en `2v2` antes del turno defensivo:
- siempre con `defender_key` válido,
- siempre con popup de daño entrante,
- siempre con nombre + slot visible (P1/P2 o E1/E2).

#### 2) Alcance C2 (sin romper 1v1)
- Solo rutas `2v2`.
- El `1v1` continúa con pantalla/flujo actual.
- No se cambia todavía la matemática completa de daño (eso queda para C3).

#### 3) Diseño de datos (SSOT de entrada defensiva)
Crear/normalizar un contexto de entrada defensiva en store:

- `incoming_ctx = {`
  - `defender_key`: clave de unidad que debe defender,
  - `defender_team`: `player|enemy`,
  - `defender_slot`: índice 0/1,
  - `defender_tag`: etiqueta visual (`P1`, `P2`, `E1`, `E2`),
  - `defender_name`: nombre de personaje,
  - `pending_damage`: daño acumulado para esa unidad,
  - `sources`: lista de fuentes que originaron ese daño,
  - `reason`: `direct|deferred|counter|...`
- `}`

Regla: en `2v2`, si no hay `defender_key` válido, **no** se entra a maniobra defensiva; se registra warning de debug y se aplica fallback controlado.

#### 4) Flujo funcional objetivo C2
1. Al detectar daño entrante en `2v2`, resolver `defender_key`.
2. Construir `incoming_ctx`.
3. Mostrar popup unificado: `Daño entrante — <tag> <nombre>`.
4. Entrar a turno defensivo con ese contexto ya fijado.
5. El encabezado del turno defensivo usa `incoming_ctx` (no inferencias tardías).

#### 5) Cambios por capas

##### A. Turn flow (2v2)
- Centralizar función helper de preparación de entrada defensiva 2v2.
- Quitar duplicaciones de cálculo de `tkey/_slot_idx/_pname` en ramas paralelas.
- Asegurar que ambos caminos (defensa normal / defensa por ataque) llamen al mismo helper.

##### B. Popup/UX
- Crear (o adaptar) popup específico de daño entrante para 2v2:
  - línea principal: daño entrante,
  - badge superior con `defender_tag + defender_name`.
- Mantener fallback a popup legacy si falla screen específico.

##### C. Observabilidad
Agregar logs de validación en C2:
- `INCOMING_DAMAGE defender_id defender_name pending_amount sources`
- `TURN_START actor_id actor_name team`
- `OFFENSE_CANCELLED actor_id reason` (si aplica)

#### 6) Criterios de aceptación C2
1. En `2v2`, **siempre** aparece popup de daño entrante antes del turno defensivo.
2. El popup muestra explícitamente el nombre y slot del defensor.
3. El encabezado del turno defensivo coincide con ese mismo defensor.
4. En `1v1`, no hay cambios de comportamiento.
5. Logs de debug muestran defensor consistente en entrada defensiva.

#### 7) Matriz mínima de prueba C2
- Caso A: enemigo ataca a P1 → popup muestra P1 + nombre correcto.
- Caso B: enemigo ataca a P2 → popup muestra P2 + nombre correcto.
- Caso C: daño diferido acumulado en P1 al inicio de turno de P1 → popup aparece antes de maniobra defensiva.
- Caso D: `1v1` smoke (turno ofensivo/defensivo normal) sin regresiones visuales.

#### 8) Riesgos y mitigación C2
- **Riesgo:** doble ruta de entrada defensiva sigue activa.
  - **Mitigación:** helper único obligatorio para construir `incoming_ctx`.
- **Riesgo:** fallback toma unidad equivocada.
  - **Mitigación:** validar team del `defender_key` antes de usarlo.
- **Riesgo:** screen conflict por popups legacy.
  - **Mitigación:** encapsular popup 2v2 y mantener fallback controlado.

#### 9) Rollback plan C2
- Si se detecta regresión, desactivar ruta 2v2 nueva detrás de flag (`use_incoming_ctx_2v2=False`) y volver temporalmente a rutas previas sin tocar `1v1`.

---

### C3 — Resolución de daño/HP por defender_key (consistencia HUD/log)
**Estado:** pendiente.

- Operación y resolve defensivo 2v2 leen/escriben HP usando `defender_key`.
- Eliminar dependencia de `player_hp` global para cálculos de unidad.
- Alinear operación, battle_log y HUD con la misma fuente.

**Resultado esperado:** no más desync `registro vs HUD`.

---

### C4 — Limpieza final + consolidación UI popups + hardening
**Estado:** pendiente.

- Consolidar popups para evitar solapamientos por múltiples definiciones.
- Limpiar rutas legacy de parches transitorios.
- Dejar guardas definitivas, logs y documentación final.

**Resultado esperado:** arquitectura mantenible con separación clara 1v1/2v2.

---

## Definición de "Done" global (C1..C4)
- `1v1` preservado sin regresiones funcionales.
- `2v2` sin desync actor/defensor.
- Popup de daño entrante visible y con nombre/slot correcto.
- HUD y log sincronizados con la misma unidad defendiendo.
- Flujo de commits incremental con rollback simple por fase.
