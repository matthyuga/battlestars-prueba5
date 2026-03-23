# Bitácora de implementación — Estamina/Shadow v2

Fecha: 2026-03-23  
Estado: Continuidad para próxima sesión

---

## 1) Qué quedó implementado

- Contrato técnico v2 documentado (modelo, pipeline, logs, migración).
- Facade con campos y APIs de capas:
  - `bs_get_unit_stamina_shadow`
  - `bs_set_unit_stamina_shadow`
  - `bs_apply_advanced_resource_effect`
- Pipeline por hit activo:
  - coating -> estamina -> HP -> KO gate -> generación
  - bloqueo por shadow local y `applied_to_enemy`
  - logs canónicos + `Efecto aplicado`
- Pre-combate:
  - perks v2 independientes (`stamina`, `shadow`, `shadow_target_mode`)
  - persistencia en `precombat_confirmed_loadout.resource_perks_v2`
  - fallback legacy controlado para snapshots viejos
- HUD:
  - vista de estamina/shadow en overlays/paneles existentes
- Ayuda F1:
  - pestaña **Design Perks** con referencia de efectos
- QA:
  - gate F6 y validador runtime con casos 1v1/2v2 e invariantes

---

## 2) Efectos avanzados disponibles hoy (runtime)

- `stamina_drain_target`
- `stamina_target_to_hp_self`
- `hp_to_stamina_target`

Todos se aplican vía:

```python
S.bs_apply_advanced_resource_effect(effect_kind, source_key, target_key, magnitude, ratio)
```

---

## 3) Qué NO está todavía

- UI/botones para “ensamblar” perks/efectos avanzados dentro de técnicas específicas.
- Editor visual de reglas por técnica (`effect_kind`, timing, magnitud, duración, costo).
- Efectos pendientes del backlog:
  - `hp_to_stamina_extra`
  - `stamina_target_to_damage_bank`
  - `stamina_target_to_reiatsu`

---

## 4) Respuesta rápida para siguiente sesión

Si la próxima sesión retoma continuidad:

1. Definir formato de “effect package” por técnica (JSON/struct por skill).
2. Crear UI mínima para asignar 1 efecto avanzado por técnica.
3. Conectar ejecución de técnica -> llamada a `bs_apply_advanced_resource_effect`.
4. Extender QA con casos de integración técnica+efecto.

---

## 5) Checklist operativo (go/no-go)

- [x] Perks v2 pre-combate independientes
- [x] `shadow_target_mode` local/enemy en runtime
- [x] Logging canónico con “Efecto aplicado”
- [x] Compat v1->v2 con fallback seguro
- [x] QA runtime + gate en PASS
- [ ] UI de ensamblaje de efectos en técnicas
- [ ] Efectos avanzados restantes del backlog

