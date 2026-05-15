# Bitacora - Pociones de combate

Fecha: 2026-05-14

## Objetivo

Completar el efecto runtime de las pociones generales del catalogo:

- HP
- EP
- EC
- Durabilidad

La regla de uso se mantiene estricta: el jugador debe comprar el item, prepararlo en el loadout de pre-combate y solo entonces puede usarlo durante el combate.

## Cobertura de catalogo

Pociones cubiertas:

- Pocion HP roja: +50% HP
- Pocion HP naranja: +35% HP
- Pocion HP amarilla: +25% HP
- Pocion EP roja: +50% EP
- Pocion EP naranja: +35% EP
- Pocion EP amarilla: +25% EP
- Pocion EC roja: +50% EC
- Pocion EC naranja: +35% EC
- Pocion EC amarilla: +25% EC
- Pocion de durabilidad roja: +50% durabilidad
- Pocion de durabilidad naranja: +35% durabilidad
- Pocion de durabilidad amarilla: +25% durabilidad

## Implementacion

Archivo:

- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`

Cambios:

- Se agrego `bs_battle_item_effect()` para resolver stat y porcentaje desde nombre/meta del item.
- HP sigue actualizando `player_hp`, facade de HP, barras y overlay de dano.
- EP actualiza `player_reiatsu`, `simulated_reiatsu` y recursos de unidad activa cuando existe battle_state.
- EC actualiza `player_energy`, `simulated_energy` y recursos de unidad activa cuando existe battle_state.
- Durabilidad restaura `coating_durability_current` hasta `coating_durability_max` en la unidad activa del jugador cuando el sistema esta disponible.
- El consumo de accion, inventario y usage runtime se centralizo en `bs_battle_commit_item_use()`.

## Verificacion estatica

- `git diff --check` sin errores.
- Se verifico que las 12 pociones generales del JSON del catalogo tienen stat y porcentaje reconocidos.

## Pendiente de prueba manual

Probar en Ren'Py:

1. Comprar una pocion de cada tipo.
2. Prepararla en el loadout.
3. Entrar a combate.
4. Gastar HP/EP/EC o durabilidad segun corresponda.
5. Usar la pocion.
6. Confirmar recuperacion, consumo de accion, descuento de inventario y log.

Sellos, amuletos y pociones de stats de Torre quedan fuera de esta pasada.
