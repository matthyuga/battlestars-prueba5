# Phase 14 — Handoff técnico (panel IA por unidad + próximos pasos visuales)

## 1) Estado actual (resumen)

Se completaron las bases funcionales para trabajar IA por unidad enemiga (E1/E2) y mantener compatibilidad con los controles globales existentes.

### Entregado

- **Perfiles por unidad (`enemy:slot`)** con defaults, sanitización y persistencia opcional.
- **Targeting por unidad**: `auto` o `force_slot` (P1/P2 en la configuración actual).
- **Lectura efectiva en runtime** (fallback a global cuando el perfil no define override):
  - `allow_focus`
  - `offense_mode`
  - `defense_mode`
  - `defense_concat`
- **Panel HUD** con controles por unidad (E1/E2) para target/mode/focus/concat.
- **Compatibilidad** mantenida: si no hay perfil por unidad, el comportamiento sigue siendo el global previo.

---

## 2) Archivos clave y responsabilidad

### Núcleo de perfiles

- `game/4/04A_AI_DIFFICULTY_HUD_CORE_UNIT_PROFILEV1.rpy`
  - SSOT de perfiles: `ai_unit_profiles`
  - API principal:
    - `ai_unit_profile_get/set/reset`
    - `ai_unit_profile_sync_from_persistent_if_needed`
    - `ai_unit_profile_save_if_needed`
    - `ai_effective_*`
    - `ai_resolve_forced_target_key`
  - Helpers UI:
    - selector E1/E2
    - ciclos por unidad de target/modes/focus/concat

### Integración de HUD

- `game/4/04A_AI_DIFFICULTY_HUD_SCREENV2.rpy`
  - Sync de perfiles en `show/replace`
  - Botones por unidad (sección nueva “Perfil IA por unidad”).

- `game/4/04A_AI_DIFFICULTY_HUD_CORE_BASEV2.rpy`
  - `Guardar ON`: también persiste perfiles por unidad.

### Consumo en IA (fase C)

- `game/4/04D_AI_PLANS_COREV1.rpy`
  - `_ai_focus_allowed(unit_key=None)` con resolución efectiva por unidad.

- `game/4/04D_AI_PLANS_OFFENSEV1a.rpy`
  - resolución de `unit_key` enemigo actual
  - modo ofensivo efectivo por unidad
  - focus ofensivo respetando profile por unidad

- `game/4/04D_AI_PLANS_DEFENSEV1a.rpy`
  - modo defensivo efectivo por unidad
  - concat efectivo por unidad
  - focus defensivo por unidad

- `game/4/04D_AI_REACTIVE_DEFENSE_COREV1.rpy`
  - plan builder reactivo con mode/concat/focus efectivos por unidad.

- `game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy`
  - ejecución defensiva respeta `allow_focus` efectivo por unidad.

- `game/4/04D_AI_EXECUTIONV5.rpy`
  - ejecución ofensiva/defensiva IA respeta `allow_focus` efectivo por unidad.

### Target forzado (fase B)

- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
  - target primario ahora intenta `ai_resolve_forced_target_key(...)` antes de heurística.
  - si aplica forzado, policy queda en `single_target`.
  - log: `force_slot(Pn)`.

---

## 3) Contrato de perfil por unidad

Cada profile tiene forma:

```python
{
  "enabled": True,
  "target_mode": "auto" | "force_slot",
  "target_slot": 0,
  "offense_mode": "inherit" | "normal" | "stats" | "force_*",
  "defense_mode": "inherit" | "normal" | "stats" | "force_*",
  "defense_concat": "inherit" | True | False,
  "allow_focus": "inherit" | True | False,
}
```

### Regla de compat

- `inherit` => usa valor global actual.
- no profile para esa unidad => se comporta como global.

---

## 4) QA manual recomendado (próxima sesión)

1. **2v2 - target forzado**
   - E1: `force_slot P2`
   - E2: `auto`
   - validar que E1 persiste target en P2 mientras esté vivo.

2. **focus por unidad**
   - E1 `allow_focus=False`, E2 `inherit` con global ON.
   - validar logs: E1 bloquea focus, E2 sí puede.

3. **concat por unidad**
   - E1 concat ON, E2 concat OFF, ambos con defense mode normal.

4. **persistencia**
   - Guardar ON: salir/reiniciar y validar carga de perfiles.
   - Guardar OFF: cambios no deben persistir en `persistent`.

5. **modos mixtos por unidad**
   - E1 offense `force_direct`, E2 offense `stats`.
   - E1 defense `force_reflect`, E2 defense `normal`.

---

## 5) Hallazgos / posibles riesgos detectados

No se detectaron errores críticos de sintaxis en revisión estática, pero sí puntos a vigilar:

1. **Pesos stats siguen globales**
   - Aunque el modo puede ser por unidad, los weights de `stats` (ofensivo/defensivo) siguen siendo compartidos globalmente.
   - Si se quiere tuning fino por E1/E2, conviene migrar weights a perfil por unidad.

2. **UX del panel todavía “flat”**
   - Ya existen controles funcionales, pero visualmente todavía no hay agrupación/pestañas.
   - Próxima fase visual: seccionar panel en Global vs Unidad activa para reducir ruido.

3. **Logs de QA necesarios en 1v2/2v1**
   - El selector por unidad usa conteos dinámicos y fallback seguros; igual conviene validar casos de slots ausentes en HUD y targets forzados fuera de rango.

---

## 6) Siguiente paso sugerido (visual)

- Separar panel en bloques:
  - **Global (legacy)**
  - **Unidad seleccionada (E1/E2)**
- Añadir indicadores de herencia (`inherit`) con color neutro.
- Mostrar tooltip corto por opción (qué afecta exactamente).

