# Bitacora continuidad - HUD rebelde, catalogo y fixes de combate

Fecha: 2026-04-27  
Rama local: `codex/review-recent-changes-to-item-catalog-n5vphi`

## Resumen

Sesion enfocada en tres frentes:

- Ajuste visual del catalogo de items para separarlo mejor del header.
- Exploracion y prototipo de HUD rebelde para combate, con assets experimentales y primera integracion jugable.
- Fixes de bugs detectados durante pruebas: overlay rojo persistente al volver al lobby y acumulacion incorrecta de dano directo enemigo.

## Cambios de UI catalogo

- Archivo: `game/ui_hub/ui_hub_screens_lobby.rpy`
- Pantalla: `bs_saga_catalog_screen`
- Cambio: se bajo el panel principal del catalogo usando un `yalign` calculado para ganar aire respecto al header superior.
- Objetivo visual: que el bloque de "Catalogo de items" no quede tan pegado al panel de Battlestars Saga.

## Assets experimentales HUD rebelde

Carpeta principal:

- `docs/materiales_experimentales/hud/`

Se crearon assets conceptuales y piezas separadas:

- `hud_hp_rebelde_concept_v1.png`
- `rebel_v1/`
- `rebel_v1_no_numbers/`
- `rebel_v1_no_numbers/portrait_layers/`
- `rebel_v1_no_numbers/portrait_tests/`
- `stickers/sticker_perrito_sin_texto_transparente_v1.png`

Notas:

- El portarretrato fue separado en 3 capas: base violeta, inner cyan y shard violeta lateral.
- Se probaron retratos contenidos para `Jugador_a` y `Hollow` usando imagenes temporales del proyecto Bleach.
- Se generaron piezas sin numeros para poder componer el HUD desde Ren'Py.

## Assets runtime HUD rebelde

Carpeta integrada al juego:

- `game/gui/battle/hud_rebel/`

Incluye:

- `portraits/portrait_player_jugador_a_rebel.png`
- `portraits/portrait_enemy_hollow_rebel.png`
- `portraits/portrait_enemy_hollow_rebel_facing.png`
- `frames/hp_frame_empty_no_numbers.png`
- `frames/hp_frame_empty_no_numbers_enemy.png`
- `frames/durability_frame_empty_no_numbers.png`
- `bars/hp_fill_green_player.png`
- `bars/hp_fill_green_enemy.png`
- `bars/hp_fill_damage_red_player.png`
- `bars/hp_fill_damage_red_enemy.png`

## Integracion jugable HUD rebelde

- Archivo: `game/06A_BATTLE_HUD_COMPAT_STUBS.rpy`
- Pantalla modificada: `battle_hp_overlay`

Estado actual:

- Se agrego un HUD experimental encima del HUD legacy.
- Jugador a la izquierda, enemigo a la derecha.
- Enemigo usa frame y retrato espejados para que ambos HUDs se enfrenten.
- HP activo en verde para ambos lados.
- EP y EC quedaron solo como numeros, sin barra.
- Durabilidad se dejo fuera del flujo por ahora, porque el proyecto aun no la maneja como sistema central.

Pendiente:

- Resolver relleno inclinado de HP de manera mas prolija, idealmente con mascara/poligono o assets segmentados.
- Agregar efecto de dano con cola roja que baja despues del HP actual.
- Quitar o reubicar definitivamente el HUD legacy cuando el nuevo HUD este listo.

## Fix: halo rojo persistente al volver al lobby

Problema:

- Al caer derrotado y usar dados de recuperacion, el overlay rojo de dano podia quedar pegado despues de terminar la partida y volver al lobby.

Archivos:

- `game/09_BATTLE_DAMAGE_OVERLAY.rpy`
- `game/04e_battle_end_result.rpy`
- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`

Solucion:

- Se agrego `battle_clear_damage_overlay()`, que oculta `battle_damage_overlay` y resetea `_overlay_current`.
- `battle_end` ahora limpia el overlay antes de saltar a postbattle/lobby.
- `bs_saga_lobby` tambien limpia el overlay como red de seguridad si alguna ruta salta directo al lobby.

Prueba recomendada:

1. Entrar a combate.
2. Caer derrotado.
3. Usar dados de recuperacion si aparecen.
4. Terminar la partida y volver al lobby.
5. Confirmar que el halo rojo ya no queda visible.

## Fix: dano directo enemigo acumulado

Problema:

- En un turno enemigo se observo un total tipo `200 defendibles + 400 directos`, cuando por reglas debia ser:
  - `Ataque negador`: dano defendible y efecto de no poder atacar si acierta dados.
  - `Ataque directo`: dano directo solo si acierta dados.
- El dano directo parecia arrastrarse de turnos anteriores y duplicarse.

Archivo:

- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`

Solucion:

- Al inicio del turno ofensivo enemigo ahora se limpian:
  - `incoming_direct_damage`
  - `enemy_direct_pending_damage`
  - `enemy_direct_base_damage`
  - `pending_direct_damage_for_defense`
  - `defense_received_includes_direct`
  - `bs_set_direct_pending("player", 0)`

Prueba recomendada:

1. Forzar o esperar turno enemigo con `Concentrar`.
2. Que use `Ataque negador` y `Ataque directo`.
3. Revisar que el total no arrastre directos viejos.
4. Confirmar que `Ataque negador` no se contabiliza como directo.

## Limpieza de repo

Se agregaron al `.gitignore` artefactos generados que no conviene commitear:

- `artifacts/`
- `build/`
- `dist/`
- `tools/__pycache__/`
- `economy-toolkit.spec`

## Verificacion realizada

Comandos usados:

- `git diff --check`
- `git diff --stat`

Resultado:

- Sin errores de diff.
- Solo warnings normales de CRLF en Windows.

## Proximos pasos sugeridos

- Probar el fix del halo rojo en una partida real.
- Probar secuencia de `Concentrar` + `Ataque negador` + `Ataque directo`.
- Continuar con el HUD rebelde:
  - resolver relleno inclinado del HP,
  - implementar cola roja de dano,
  - definir layout final en esquinas,
  - decidir si el retrato sera contenido o si sobresaldra del marco.
