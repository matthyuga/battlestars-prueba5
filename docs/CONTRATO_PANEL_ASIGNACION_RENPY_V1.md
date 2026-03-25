# Contrato v1 — Panel de Asignación (Ren'Py)

Fecha: 2026-03-25  
Scope: runtime UI en Ren'Py (sin web).

## 1) Objetivo

Definir el contrato único de datos/eventos para implementar el panel de asignación de forma determinista en Ren'Py, alineado con:

- `docs/FICHA_TECNICA_ESCALADO_TECNICAS_V1.md`
- `docs/PLANILLA_CAPS_TECNICAS_REGISTROS_V1.md`
- `docs/PLANILLA_CONSUMO_TECNICAS_REGISTROS_V1.md`
- `docs/PLANILLA_EXP_ORO_DESEMPENO_V1.md`

---

## 2) Estructura de pantalla (v1)

Se implementan **2 paneles + 1 modal**:

1. Panel A: Identidad y Stats
2. Panel B: Principal + Pool técnico
3. Modal: Confirmación final (resumen + validaciones)

---

## 3) Estado de UI (`panel_state`)

```python
panel_state = {
  "player": {
    "level": 1,
    "max_level": 500,
    "register": 0,
    "max_register": 50,
    "exp_current": 0,
    "exp_max": 100
  },
  "pending": {
    "stat_points": 0,
    "tech_pool_points": 200
  },
  "stats": {
    "fuerza": 0,
    "agilidad": 0,
    "resistencia": 0,
    "inteligencia": 0,
    "espiritu": 0,
    "suerte": 0,
    "carisma": 0,
    "percepcion": 0
  },
  "limits": {
    "stat_soft_cap": 20,
    "stat_hard_cap": 25
  },
  "principal": {
    "selected": null,
    "distribution": {
      "ataque": 0,
      "defensa": 0,
      "hp": 0,
      "reiatsu": 0,
      "energia": 0
    },
    "distribution_total": 0,
    "active_slots": 0,
    "max_slots": 4
  },
  "pool": {
    "base_initial": 200,
    "per_register_gain": 100,
    "total": 200,
    "offensive_spent": 0,
    "defensive_spent": 0,
    "available": 200
  },
  "mode": {
    "view": "pve"  # pvp|pve
  },
  "preview": {
    "hp_before": 1000,
    "hp_after": 1000,
    "energia_before": 100,
    "energia_after": 100,
    "reiatsu_before": 1000,
    "reiatsu_after": 1000,
    "atk_before": 0,
    "atk_after": 0,
    "def_before": 0,
    "def_after": 0
  },
  "validation": {
    "is_valid": False,
    "errors": [],
    "warnings": []
  }
}
```

---

## 4) Reglas de negocio obligatorias

1. **Registro**: `register = floor(level/10)` con caso inicial nivel 1 => registro 0.
2. **Pool técnico total**: `200 + (register * 100)`.
3. **Aporte por +1 stat**:
   - fuerza +100 ofensiva
   - agilidad +100 defensiva
   - resistencia +100 HP
   - inteligencia +100 energía
   - espiritu +100 reiatsu
4. **Atributo principal**:
   - 1 seleccionado
   - distribución suma exacta 100
   - tramos válidos: 25, 50, 75, 100
   - máximo 4 categorías activas (de 5)
5. **Caps por tier**: usar planilla de caps por registro (`Reg 0–50`).
6. **Vista PvP/PvE**: mostrar misma base con variante por modo.

---

## 5) API interna de cálculo (funciones puras)

```python
def compute_register(level): ...
def compute_pool_total(register): ...
def compute_stat_effects(stats): ...
def compute_principal_bonus(principal_selected, distribution): ...
def compute_caps_for_register(register, mode): ...
def compute_consumption_at_cap(register, mode): ...
def compute_exp_oro_reward(base_exp, base_oro, player_register, rival_register, is_victory, stars, repetition_count=1): ...
def compute_preview(panel_state): ...
def validate_panel_state(panel_state): ...
```

### Contrato de `validate_panel_state`

Devuelve:

```python
{
  "is_valid": bool,
  "errors": ["..."],
  "warnings": ["..."]
}
```

Errores bloqueantes mínimos:
- principal no seleccionado
- distribución != 100
- más de 4 categorías activas
- intento de gasto > disponible
- excede cap por tier

---

## 6) Eventos UI (Ren'Py)

- `on_select_principal(attr)`
- `on_change_distribution(bucket, delta)`
- `on_add_stat(attr)`
- `on_remove_stat(attr)`
- `on_add_pool(type, amount)`  # offense/defense
- `on_remove_pool(type, amount)`
- `on_toggle_mode("pvp"|"pve")`
- `on_reset_changes()`
- `on_confirm_open_modal()`
- `on_confirm_apply()`

Todos los eventos ejecutan:
1) mutación controlada,
2) `compute_preview`,
3) `validate_panel_state`.

---

## 7) Estados semilla de QA (obligatorios)

1. `seed_new_player`: nivel 1, reg 0, principal vacío.
2. `seed_reg10_balanced`: nivel 100, reg 10, build equilibrada.
3. `seed_reg35_specialized`: nivel 350, reg 35, build especializada.

---

## 8) Persistencia (mínima v1)

Al confirmar:

- guardar stats finales,
- guardar principal + distribución,
- guardar gasto de pool,
- registrar snapshot en log de auditoría:
  - level/register
  - pending consumidos
  - before/after
  - timestamp

---

## 9) Integración futura (no bloqueante v1)

- Cálculo de recompensa EXP/Oro post-combate (doc específico).
- Pantalla de desempeño 30 estrellas.
- Reglas de respec con costos/economía.
