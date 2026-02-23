# Roadmap de evolución combate (1v1 -> 2v2/5v5 y variantes NxM)

## Objetivo
Definir un mapa de implementación por pasos para evolucionar el sistema actual 1v1 hacia equipos/unidades (2v2, 5v5 y variantes como 3v5, 1v4), minimizando riesgo y manteniendo compatibilidad incremental.

---

## Principios de implementación

1. **Separar cálculo de daño de selección de objetivos**.
2. **Mantener facade como contrato único de estado** (`battle_state`).
3. **Compatibilidad 1v1 por defecto** durante toda la migración.
4. **Cambios por PR pequeños** (estructura -> integración -> UI).
5. **Evitar hardcode de nombres/lados**: operar por `team:slot`.

---

## Estado actual (baseline)

- Facade con soporte de `teams`, `active`, helpers de slot activo y contexto de turno.
- Turno con `owner_team`, `owner_slot`, `phase`, `round`.
- Selección de personaje jugador (Harribel/Grimmjow/Nel/Hollow).
- Compatibilidad 1v1 preservada.

---

## Fase A3b (siguiente paso recomendado): motor de targets + plan de daño

> Alcance: **infraestructura** (sin UI completa 2v2 todavía).

### A3b.1 - Clave canónica de unidad
- Introducir `unit_key = "<team>:<slot>"` (ej: `player:0`, `enemy:1`).
- Helpers de traducción:
  - `bs_unit_key(team, slot)`
  - `bs_parse_unit_key(key)`

### A3b.2 - Resolución de objetivos
- API para obtener objetivos válidos vivos por equipo.
- Soporte de modos:
  - `single_target`
  - `split_equal`
  - `split_manual`

### A3b.3 - DamagePlan (estructura intermedia)
- Definir una estructura única para aplicar daño:
  - `source_key`
  - lista de `entries[{target_key, amount, tags}]`
  - `meta` (`mode`, `skill_id`, etc.)
- La fórmula produce plan; un resolver central lo aplica.

### A3b.4 - Reflect por unidad
- Migrar reflect de enfoque por lado a enfoque por `target_key` + `source_key`.
- Definir política explícita de consumo/expiración por fase/turno.

### Criterio de cierre A3b
- Se puede calcular/aplicar daño dirigido a unidades específicas sin romper 1v1.
- Reflect mantiene trazabilidad por unidad.

---

## Fase A4: KO por unidad + auto-switch + fin de combate por equipo

### A4.1 - KO unitario
- KO deja fuera de combate solo a la unidad afectada.
- Marcar `alive=false` y bloquear selección como target.

### A4.2 - Auto-advance de activo
- Si unidad activa cae, seleccionar automáticamente siguiente unidad viva del mismo team.
- Si no hay unidades vivas, declarar derrota del team.

### A4.3 - Condición de victoria por equipo
- Fin de combate cuando `team_alive_count == 0` para un bando.
- Compat 1v1: equivale al comportamiento actual.

### Criterio de cierre A4
- Flujo de turnos estable con KO por unidad y transición automática de activo.

---

## Fase B (UI táctica): selección de targets y split manual

### B.1 - UI mínima de selección de objetivo
- En ofensiva, permitir elegir target cuando hay múltiples enemigos vivos.

### B.2 - UI de división de daño (manual)
- Permitir asignar paquetes/técnicas a objetivos distintos.
- Validación: suma asignada == daño total disponible (o regla definida).

### B.3 - Fallbacks automáticos
- Si no hay input manual, usar política por defecto (`single_target` o `split_equal`).

---

## Fase C (AI multi-unidad)

### C.1 - Priorización de targets
- Heurísticas iniciales:
  - focus target con menor HP
  - castigar unidad con mayor amenaza
  - proteger unidad propia crítica

### C.2 - Uso de reflect y defensa en contexto multi-target
- AI decide cuándo guardar/consumir reflect según riesgo por unidad.

### C.3 - Política de split de AI
- Decidir cuándo conviene burst (foco) vs presión distribuida.

---

## Fase D (stats/items pipeline sobre NxM)

1. Pipeline único: `base + crecimiento + equipo + buffs/debuffs = final`.
2. Buff/debuff por unidad y por team.
3. Ítems declarativos (no hardcode por técnica).
4. Recalcular en hooks controlados (inicio turno, equip/unequip, expiración).

---

## Smoke tests manuales por fase

### Smoke A3b
- 1v1 sigue funcionando igual.
- 2 objetivos vivos: resolver dirigido a uno.
- split_equal reparte daño en objetivos vivos.
- reflect registra `source_key/target_key` correctamente.

### Smoke A4
- KO de unidad no termina combate si quedan aliados vivos.
- Auto-switch al siguiente slot vivo.
- Victoria cuando un team queda sin unidades vivas.

### Smoke UI/AI
- Selección manual de target/split sin inconsistencias de suma.
- AI no elige targets KO.

---

## Orden de PR sugerido

1. **PR A3b.1**: unit_key + helpers base.
2. **PR A3b.2**: resolver de targets válidos + modos `single/split_equal`.
3. **PR A3b.3**: DamagePlan + apply centralizado.
4. **PR A3b.4**: reflect por unidad (`target_key/source_key`).
5. **PR A4**: KO unitario + auto-switch + victoria por equipo.
6. **PR UI-B**: selector objetivo + split manual.
7. **PR AI-C**: priorización y split AI.
8. **PR Stats/Items-D**: pipeline completo.

---

## Riesgos y mitigación

- **Riesgo**: romper 1v1 legacy.
  - **Mitigación**: fallback slot `0`, smoke 1v1 obligatorio por PR.
- **Riesgo**: duplicidad de fuentes de verdad.
  - **Mitigación**: facade SSOT + sync legacy encapsulado.
- **Riesgo**: complejidad de UI prematura.
  - **Mitigación**: motor primero, UI después.

---

## Definición de “listo para escalar a 5v5”

Se considera listo cuando:
1. El daño se expresa y aplica por `unit_key`.
2. Reflect opera por unidad y respeta fase/turno definidos.
3. KO y auto-switch funcionan por unidad.
4. El combate termina por estado de equipo (no solo por lado activo).
5. 1v1 sigue estable sin ramas especiales complejas.
