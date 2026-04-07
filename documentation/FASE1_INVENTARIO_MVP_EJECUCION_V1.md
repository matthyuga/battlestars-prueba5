# FASE1_INVENTARIO_MVP_EJECUCION_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (aprobado para iniciar)

## 1) Meta

Tener inventario funcional en lobby/perfil con equipamiento básico y carga de presets, sin entrar todavía a inventario en combate.

---

## 2) Alcance funcional (Fase 1)

### 2.1 Alta/baja de ítems

- Alta de ítems al inventario del perfil.
- Baja de ítems por consumo/eliminación manual permitida.
- Validación de cantidades (`qty >= 0`).
- Registro de cambios en log de inventario.

### 2.2 Equipamiento en slots MVP

Slots activos en esta fase:
- 2 anillos (`ring_left_1`, `ring_right_1`)
- 1 diadema (`head_circlet`)
- 1 collar (`necklace`)
- 2 brazaletes (`bracelet_left`, `bracelet_right`)
- 1 tatuaje (`tattoo_slot`)

Reglas:
- Un slot solo admite subtipos compatibles.
- Si no cumple tier/rareza requerida, bloquear equipamiento.
- Tatuaje: máximo 1 activo por personaje.

### 2.3 Presets por personaje

Soportar 3 presets fijos:
1. `balanceado`
2. `ofensivo`
3. `defensivo`

Operaciones obligatorias:
- Guardar preset.
- Cargar preset.
- Sobrescribir preset existente.
- Restablecer preset a vacío.

---

## 3) Modelo de datos mínimo (Fase 1)

### 3.1 `loadout_descriptor` requerido

Campos:
- `loadout_id`
- `owner_id`
- `preset_key` (`balanceado|ofensivo|defensivo`)
- `slots`
- `version`
- `created_at`
- `updated_at`

### 3.2 Ejemplo JSON

```json
{
  "loadout_id": "ld_hero_001_balanceado",
  "owner_id": "hero_001",
  "preset_key": "balanceado",
  "slots": {
    "ring_left_1": "itm_ring_c_01",
    "ring_right_1": "itm_ring_c_02",
    "head_circlet": "itm_circlet_b_01",
    "necklace": "itm_necklace_c_01",
    "bracelet_left": "itm_bracelet_c_03",
    "bracelet_right": "itm_bracelet_c_04",
    "tattoo_slot": "itm_tattoo_passive_01"
  },
  "version": 1,
  "created_at": "2026-04-06T00:00:00Z",
  "updated_at": "2026-04-06T00:00:00Z"
}
```

---

## 4) Flujo UI (lobby/perfil)

1. Abrir panel inventario.
2. Ver lista de ítems disponibles por categoría.
3. Seleccionar personaje.
4. Equipar/desequipar en slots MVP.
5. Guardar preset (`balanceado|ofensivo|defensivo`).
6. Cargar preset y verificar que equipa correctamente.

---

## 5) Criterios de salida Fase 1

1. Equipar/desequipar sin inconsistencias.
2. Guardar/cargar 3 presets estable.
3. Validación de tier/rareza funcionando.

Criterios QA adicionales:
- No se duplica item_instance al equipar en múltiples slots.
- Al remover un item equipado, vuelve a inventario disponible.
- Cargar preset inválido (ítem no disponible) muestra error controlado.

---

## 6) Checklist de implementación

- [ ] Screen de inventario lobby funcional.
- [ ] Adaptador de slots MVP implementado.
- [ ] Validadores tier/rareza activos.
- [ ] CRUD de presets (3 claves fijas).
- [ ] Mensajería de error de equipamiento inválido.
- [ ] Smoke test manual de equipar/desequipar/guardar/cargar.

---

## 7) Entregables de Fase 1

1. `documentation/FASE1_INVENTARIO_MVP_EJECUCION_V1.md` (este documento)
2. `documentation/CHECKLIST_QA_FASE1_INVENTARIO_MVP_V1.md` (pendiente)
3. `documentation/UI_FLOW_INVENTARIO_LOBBY_V1.md` (pendiente)
