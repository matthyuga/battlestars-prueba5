# Bitacora - Hit feedback visual

Fecha: 2026-06-07

## Objetivo

Crear una primera capa visual para impactos comunes y combos, separada de los `special_cutin`.

La idea es que cada tecnica que realmente golpea pueda generar un evento visual:

- contador de HIT;
- numero de dano;
- rango simple `C/B/A/S`;
- entrada rapida con deformacion tipo choque.

## Regla inicial

- Un ataque que hace dano parcial registra 1 hit.
- `Concentrar` no registra hit por si mismo, porque solo potencia el siguiente ataque.
- El resultado final del turno no registra hit extra para evitar duplicados; se muestra como `TOTAL`.
- Si varios impactos ocurren cerca en el tiempo, el contador sube y cambia el rango.

## Implementacion

Archivos tocados:

- `game/06B1_BATTLE_FX_CORE.rpy`
  - Agrega la cola `battle_hit_feedback_events`.
  - Agrega `bs_battle_enqueue_hit_feedback`.
  - Agrega `bs_battle_hit_feedback_grade`.
  - Agrega `bs_battle_hit_feedback_prune`.
  - Conecta `battle_visual_float(..., is_final=False)` con el nuevo sistema como hit.
  - Conecta `battle_visual_float(..., is_final=True)` como evento `TOTAL`, sin sumar combo.
  - Agrega `bs_battle_enqueue_focus_break` para mostrar `CONCENTRAR` como corte visual.
  - Agrega historial `battle_hit_feedback_history` y segmentos `battle_hit_feedback_combo_segments` para futuras mecanicas que lean cadenas de hits.
  - Agrega banderas:
    - `bs_battle_hit_feedback_enabled`
    - `bs_battle_legacy_damage_popups_enabled`
    - `bs_battle_fx_speed_mode`

- `game/06B2_BATTLE_FX_SCREENS.rpy`
  - Agrega `screen battle_hit_feedback_layer`.
  - Muestra HIT, dano y rango.
  - Apaga por defecto los numeros flotantes antiguos mediante `bs_battle_legacy_damage_popups_enabled = False`.
  - Separa etiquetas visuales:
    - `HIT`: golpe individual con rango.
    - `ENTRANTE`: dano antes de maniobras/defensa.
    - `FINAL`: dano final aplicado al enemigo.
    - `RECIBIDO`: dano final aplicado al HP del jugador.

- `game/06B3_BATTLE_FX_TRANSFORMS.rpy`
  - Agrega transforms de entrada para enemigo y jugador.
  - Simula numero viajando rapido, deformandose y chocando.
  - Agrega transforms `battle_result_feedback_enemy/player` para dano final/recibido con estilo de impacto mas pesado.

- `game/06C_BATTLE_OVERLAY_MANAGER.rpy`
  - Registra `battle_hit_feedback_layer` como overlay.

- `game/4/04D_AI_EXECUTIONV5.rpy`
  - Al usar Concentrar, la IA dispara un corte visual y reinicia el contador del combo contra el jugador.
  - El Ataque Directo exitoso de la IA tambien dispara HIT aunque vuelva antes del flujo defendible normal.
  - Ajuste posterior: la IA emite el `HIT` desde un punto comun inmediatamente despues de calcular/pagar el dano de la tecnica ofensiva. Esto evita que ramas como directo, negador o reductor salten el feedback parcial.

- `game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy`
  - Al usar Concentrar, el jugador dispara un corte visual y reinicia el contador del combo contra el enemigo.

- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
  - El dano previo a maniobras se muestra como `ENTRANTE`.
  - La maniobra `Ataque por defensa` muestra el dano real al HP como `TOTAL`.

- `game/4/j/04C_OFFENSIVE_RESOLVEV1.rpy`
  - El dano final del jugador contra el enemigo se calcula por delta real de HP y se muestra como `TOTAL`.

- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
  - El dano final recibido por el jugador se calcula por delta real de HP y se muestra como `TOTAL`.

## Ajuste 2026-06-07

Se retiro el `timer` repetitivo del overlay de hits. Al ser un overlay global, ese timer podia refrescar pantallas fuera de combate y provocar problemas con viewports/scrollbars, por ejemplo listas de heroes o pantallas de preparacion que vuelven hacia arriba al desplazarse.

## Ajuste final 2026-06-07

Se reviso el flujo tras probar combos del jugador y de la IA:

- Si la IA atacaba sin `Concentrar`, el combo llegaba correctamente a `HIT A`.
- Si la IA usaba `Concentrar`, el golpe posterior podia quedar visualmente pisado por `ENTRANTE` o por el refresco del resultado.
- Al finalizar defensa, a veces aparecian hits viejos mezclados con `RECIBIDO`.
- Los hits del jugador salian demasiado juntos porque el procesamiento ofensivo del jugador ejecutaba toda la cola sin pausas entre tecnicas.

Cambios aplicados:

- `game/06B1_BATTLE_FX_CORE.rpy`
  - Se separa la cola de hits (`battle_hit_feedback_events`) de la cola de resultados (`battle_hit_feedback_result_events`).
  - `incoming` y `final` ya no cuentan como hits ni compiten por los mismos slots visuales.
  - Se agrega `bs_battle_hit_feedback_visible_events`, con TTL separado para hits y resultados.
  - Se ajusta el tiempo visible de hits para acompanar animaciones mas lentas.

- `game/06B2_BATTLE_FX_SCREENS.rpy`
  - `battle_hit_feedback_layer` ahora renderiza en dos pasadas:
    - hits/combo (`HIT`, `CONCENTRAR`);
    - resultados (`ENTRANTE`, `FINAL`, `RECIBIDO`).
  - Esto evita que el dano final tape el hit posterior a `Concentrar`.

- `game/06B3_BATTLE_FX_TRANSFORMS.rpy`
  - Se ralentiza la animacion de hits aproximadamente un 25%.

- `game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy`
  - Se agrega `_offensive_fx_hit_pause`.
  - El jugador ahora hace una pausa corta despues de cada hit ofensivo, igualando mejor el ritmo del turno enemigo.
  - `Concentrar` tambien deja una pequena pausa visual antes de continuar.

Validacion:

- `renpy.exe D:\2026\battlestars-prueba5 lint` ejecutado sin errores nuevos.
- El unico aviso persistente es el asset faltante antiguo `images/character/Harribel_a.png`, no relacionado con este sistema.

## Estado actual

Primera version funcional:

- Aprovecha los lugares donde el combate ya llama a `battle_visual_float`.
- Se dispara como hit cuando `is_final=False`.
- Se dispara como `TOTAL` cuando `is_final=True`.
- El objetivo puede ser `enemy` o `player`.
- El grado es automatico por cantidad de hits cercanos:
  - `C`: 1 hit
  - `B`: 2 hits
  - `A`: 3 hits
  - `S`: 4-5 hits
  - `SS`: 6+ hits

## Modelo visual actual

- Golpes parciales: `HIT` con rango `C/B/A/S/SS`.
- Concentrar: muestra `CONCENTRAR`, archiva la cadena anterior y reinicia el contador.
- Dano antes de maniobras: `ENTRANTE`.
- Dano efectivo al enemigo tras resolucion: `FINAL`.
- Dano efectivo al jugador tras defensa/maniobra/resolucion: `RECIBIDO`.

## Pendientes

- Ajustar posicion/tamano despues de verlo en pantalla.
- Decidir si el rango debe depender solo de cantidad de hits o tambien de dano/precision.
- Crear una variante para especiales multi-hit con ticks programados.
- Agregar sonidos y particulas.
- Evitar saturacion si una tecnica futura genera demasiados impactos.
