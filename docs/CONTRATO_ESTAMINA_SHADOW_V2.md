# Contrato técnico v2 — Estamina / Shadow modular (self/enemy)

Fecha: 2026-03-22  
Estado: Borrador de implementación (acordado para próxima iteración)

---

## 1) Objetivo

Evolucionar el sistema v1 para que **Estamina** y **Shadow** sean capas modulares de estado/efecto, desacopladas de técnicas concretas, con soporte para:

- activación por **perk** en pre-combate,
- activación por stats/ítems/pasivas/técnicas en runtime,
- aplicación sobre **self** o **enemy** según el efecto.

---

## 2) Principios de diseño

1. **Desacople de fuente**: ningún comportamiento base depende de una técnica específica.
2. **Target explícito**: todo efecto declara destino (`self`, `enemy`, `ally`, `team`).
3. **Pipeline determinístico**: orden de resolución estable por hit.
4. **Compatibilidad progresiva**: se mantiene compat con v1 durante migración.
5. **Auditabilidad**: cada efecto aplicado queda logueado de forma canónica.

---

## 3) Semántica funcional (v2)

### Estamina

- Capa de absorción prioritaria antes de HP.
- Puede existir en el usuario propio (**self_stamina**) o en objetivo rival (**enemy_stamina**) si un efecto lo define.
- Puede convertirse desde/hacia otros recursos por reglas explícitas (no implícitas).

### Shadow

- Estado de ocupación de espacio de generación de estamina.
- En v2 puede ser:
  - **shadow_local** (bloquea espacio del propio portador), o
  - **shadow_applied_to_enemy** (debuff que bloquea espacio del oponente).
- El modo se define por el efecto y su target; no por hardcode de técnica.

---

## 4) Modelo de datos (mínimo)

> Conserva campos v1 y agrega metadatos de targeting/origen.

### Campos por unidad

- `stamina_current` (int >= 0)
- `stamina_cap` (int >= 0)
- `stamina_enabled` (bool)
- `shadow_current` (int >= 0)
- `shadow_cap` (int >= 0)
- `shadow_active` (bool)

### Metadatos de estado (nuevos)

- `stamina_profile` (str): `"self" | "external" | "hybrid"`
- `shadow_profile` (str): `"local" | "applied" | "hybrid"`

### Metadatos de origen (nuevos)

- `stamina_sources` (lista): entries `{source_kind, source_id, magnitude, expires_on}`
- `shadow_sources` (lista): entries `{source_kind, source_id, magnitude, expires_on, target_mode}`

### Derivados

- `missing_hp = max(0, hp_max - hp_current)`
- `free_space = max(0, hp_max - hp_current - stamina_current - shadow_current)`
- invariante: `stamina_current + shadow_current <= missing_hp`

---

## 5) Contrato de efectos (nuevo)

Todo efecto debe declararse como:

```json
{
  "effect_kind": "stamina_enable|shadow_apply|stamina_convert|stamina_drain|stamina_to_hp|stamina_to_reiatsu|stamina_to_damage_bank",
  "source_kind": "perk|item|stat|passive|skill|aura",
  "source_id": "string",
  "target_scope": "self|enemy|ally|team",
  "timing": "precombat|on_hit|turn_start|turn_end|on_ko|manual",
  "magnitude": { "type": "flat|percent", "value": number },
  "duration": { "mode": "persistent|turns|instant", "value": number }
}
```

### Regla

- Si no hay `target_scope`, el efecto es inválido.
- Si no hay `timing`, fallback = `manual`.

---

## 6) Pre-combate (UI/UX obligatorio)

Se agrega bloque **Perks de Recursos** independiente de técnicas:

1. Toggle `Perk Estamina`.
2. Toggle `Perk Shadow`.
3. (Opcional) Selector de perfil: `local` / `applied_to_enemy`.

Persistencia mínima en `precombat_confirmed_loadout.resource_perks_v2`:

```json
{
  "stamina_perk_enabled": true,
  "shadow_perk_enabled": false,
  "shadow_target_mode": "applied_to_enemy",
  "shadow_seed_ratio": 0.15
}
```

### Restricción

- La activación por perks v2 **no** depende de specials del loadout.

---

## 7) Pipeline de resolución por hit (v2)

Orden:

1. Coating/cobertura.
2. Consumo de estamina disponible del objetivo.
3. Overflow a HP.
4. KO gate.
5. Generación de estamina (si reglas lo permiten).
6. Aplicación de efectos post-hit (ej. `shadow_apply` al enemigo).

### Nota importante

`shadow_applied_to_enemy` se evalúa sobre el `free_space` del objetivo enemigo al momento de su cálculo de generación.

---

## 8) Operaciones estratégicas habilitadas (v2+)

Se habilitan por contrato (sin implementación forzada en esta fase):

- `hp_to_stamina_target` (convertir HP del rival a estamina del rival).
- `hp_to_stamina_extra` (convertir porcentaje de HP no dañado a estamina).
- `stamina_drain_target` (consumir estamina rival).
- `stamina_target_to_hp_self` (robo/conversión estamina rival -> HP propio).
- `stamina_target_to_damage_bank` (acumular daño próximo turno).
- `stamina_target_to_reiatsu` (conversión a recurso mágico).

Cada una se implementa como `effect_kind` + reglas de límites.

---

## 9) Logging canónico (v2)

Por hit, en orden:

1. `Estamina: ...`
2. `HP: ...`
3. `HP genera ...` (si aplica)
4. `Shadow bloquea ...` (si aplica)
5. `Efecto aplicado: <effect_kind> source=<source_id> target=<scope>` (si hubo efecto extra)

---

## 10) Compatibilidad/migración

1. Mantener `resource_perks` v1 durante transición.
2. Introducir `resource_perks_v2` y priorizarlo si existe.
3. Si v2 no existe, fallback controlado a v1.
4. Remover inferencia por specials al cerrar migración.

---

## 11) Criterios de aceptación

- [ ] Pre-combate muestra toggles de perks independientes.
- [ ] `stamina_perk_enabled` activa generación sin requerir técnica especial.
- [ ] `shadow_target_mode=applied_to_enemy` bloquea espacio del rival (no local).
- [ ] Invariantes de espacio siempre válidos.
- [ ] Logs incluyen secuencia base + efectos aplicados.
- [ ] 1v1 y 2v2 operan con misma semántica de efectos.

---

## 12) Estado de implementación recomendado

- **Paso 0 (MVP)**: congelar alcance mínimo antes de seguir con integración:
  - perks independientes en pre-combate,
  - `shadow_target_mode` (`local` / `applied_to_enemy`),
  - pipeline base por hit + logging canónico,
  - compatibilidad v1→v2.
  - Referencia contractual: secciones 6, 7, 9 y 10.
- **Fase A**: UI pre-combate perks v2 + persistencia `resource_perks_v2`.
- **Fase B**: runtime apply v2 (self/enemy target mode).
- **Fase C**: desactivar inferencia por specials.
- **Fase D**: efectos avanzados de conversión/drenaje.

### Límites explícitos del MVP (Paso 0)

- No mezclar aún operaciones avanzadas de la sección 8.
- Mantener foco en estabilizar semántica base, logs y migración.
- Tratar la semántica de `shadow_local` / `shadow_applied_to_enemy` según sección 3.
