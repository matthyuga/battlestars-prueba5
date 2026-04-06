# FASE6_ROTACION_Y_EXPANSION_SLOTS_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (listo para implementar)

## 1) Meta

Activar contenido vivo mediante rotación semanal de personajes y ampliar gradualmente la complejidad de equipamiento con nuevos slots.

---

## 2) Alcance funcional (Fase 6)

### 2.1 Rotación semanal de personajes libres

Reglas base:
- Publicar rotación cada semana (`rotation_week_id`).
- Tamaño inicial recomendado: 10 personajes libres por semana.
- La rotación aplica por temporada y puede incluir mezcla de tiers.

Restricciones:
- Un personaje en rotación no implica desbloqueo permanente.
- Cambios de rotación no deben alterar inventario/equipamiento permanente.

### 2.2 Distinción entre libre temporal y desbloqueado permanente

Estados de acceso por personaje:
- `locked`
- `free_rotation` (temporal)
- `unlocked_permanent`

Reglas:
- `free_rotation` permite uso en modos permitidos sin posesión permanente.
- `unlocked_permanent` no depende de rotación.
- Si termina semana, `free_rotation` expira automáticamente.

### 2.3 Expansión progresiva de slots

Base ya establecida en fases previas:
- 2 anillos, 1 diadema, 1 collar, 2 brazaletes, 1 tatuaje.

Expansión Fase 6 (bajo feature flags):
1. `earring_left`, `earring_right`
2. `anklet_left`, `anklet_right`
3. `belt`
4. anillos extra (`ring_left_2`, `ring_right_2`)

Regla de rollout:
- Activar por etapas (1 grupo de slots por release).
- Monitorear impacto en balance antes de habilitar siguiente grupo.

---

## 3) Política operativa de rotación

Variables mínimas:
- `season_id`
- `rotation_week_id`
- `rotation_start_at`
- `rotation_end_at`
- `free_character_pool[]`

Validaciones:
- No repetir exactamente el mismo pool 2 semanas consecutivas (salvo excepción explícita).
- Garantizar diversidad mínima por tier/franquicia según objetivo de temporada.
- Registrar historial para auditoría y análisis de adopción.

---

## 4) Métricas clave (adopción y conversión)

### 4.1 Adopción
- `weekly_active_players`
- `free_rotation_pick_rate`
- `matches_played_with_free_rotation`

### 4.2 Conversión
- `free_to_permanent_conversion_rate`
- `time_to_first_unlock`
- `star_spend_on_unlocked_characters`

### 4.3 Balance de slots
- `equip_slot_usage_distribution`
- `avg_power_delta_after_slot_expansion`
- `winrate_variance_by_slot_count`

---

## 5) Criterios de salida Fase 6

1. Rotación estable por temporada.
2. Métricas de adopción y conversión de desbloqueos positivas.

Criterios QA adicionales:
- Cambio semanal aplica sin corrupción de estado.
- Personajes `free_rotation` expiran correctamente al cierre de semana.
- Activar nuevos slots no rompe presets existentes.

---

## 6) Riesgos y mitigación (fase)

1. Complejidad temprana alta
   - Mitigar con alcance MVP por fase y feature flags.
2. Power creep por ítems/buffs
   - Mitigar con caps, escalado de costo y telemetría temprana.
3. Conflictos de reglas en combate
   - Mitigar con contrato único + orden de resolución explícito.

---

## 7) Checklist de implementación

- [ ] Implementar servicio de rotación semanal (`rotation_week_id`).
- [ ] Implementar estados de acceso `locked/free_rotation/unlocked_permanent`.
- [ ] Integrar expiración automática de personajes temporales de rotación.
- [ ] Integrar expansión de slots por feature flags.
- [ ] Ejecutar validación de compatibilidad con presets viejos.
- [ ] Activar tablero de métricas de adopción/conversión.

---

## 8) Entregables de Fase 6

1. `documentation/FASE6_ROTACION_Y_EXPANSION_SLOTS_V1.md` (este documento)
2. `documentation/POLITICA_ROTACION_PERSONAJES_V1.md`
3. `documentation/CHECKLIST_QA_ROTACION_Y_SLOTS_V1.md` (pendiente)
