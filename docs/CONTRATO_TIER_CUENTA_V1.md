# Contrato Tier de Cuenta v1 (Saga)

Define cómo se calcula el tier de la cuenta de usuario para lobby/perfil.

## Regla base

El tier se desbloquea cuando se cumplen **ambas condiciones**:

1. Nivel de cuenta mínimo para ese tier.
2. Cantidad mínima de héroes **del mismo tier** comprados/poseídos.

Si no se cumple ningún tier, el estado es **"Sin tier"**.

## Requisitos activos (v1)

| Tier | Nivel mínimo | Héroes del tier requeridos |
|---|---:|---:|
| C | 1 | 20 |
| B | 5 | 15 |
| A | 10 | 10 |
| S | 15 | 5 |
| SS | 20 | 4 |
| SSS | 25 | 3 |
| IV | 30 | 1 |

## Fuente de verdad runtime

En `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`:

- `bs_saga_tier_hero_requirements`
- `bs_saga_tier_level_requirements`
- `bs_saga_eval_account_tier()`
- `bs_saga_refresh_account_tier()`

## Orden de evaluación

Se evalúa de mayor a menor prioridad: `IV -> SSS -> SS -> S -> A -> B -> C`.

## Notas

- Los requisitos son **data-driven** (diccionarios), ajustables sin reescribir toda la lógica.
- Las compras de héroes recalculan tier en tiempo real.
