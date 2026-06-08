# Bitacora - Visuales de personajes en combate

Fecha: 2026-05-26

## Objetivo

Integrar imagenes nuevas de personajes para empezar a probar una capa visual de combate:

- Retrato de HUD para Aqua, Darkness y Megumin.
- Pose de batalla para cuando el jugador confirma acciones ofensivas o defensivas.
- Animacion simple de entrada con fade y movimiento lineal de derecha a izquierda.

## Archivos y assets usados

Carpeta base: `game/images/character`

- Megumin HUD: `CharaStudio-2026-05-25-23-32-31-Render.png`
- Megumin pose: `CharaStudio-2026-05-25-23-53-13-Render.png`
- Aqua HUD: `CharaStudio-2026-05-25-23-33-06-Render.png`
- Aqua pose: `CharaStudio-2026-05-25-23-54-55-Render.png`
- Darkness HUD: `CharaStudio-2026-05-25-23-33-40-Render.png`
- Darkness pose: `CharaStudio-2026-05-25-23-50-17-Render.png`

## Implementacion

Se agrego `game/06B_BATTLE_CHARACTER_VISUALS.rpy` como capa separada de visuales de personajes.

Funciones principales:

- `bs_battle_head_portrait_displayable`: genera el retrato recortado para HUD compacto.
- `bs_battle_rebel_portrait_displayable`: genera el retrato para el HUD rebel.
- `bs_battle_pose_displayable`: prepara la pose de combate.
- `bs_battle_show_character_pose`: muestra la pose sobre la pantalla de combate.
- `battle_character_pose_fx`: screen visual con animacion temporal.

## Retratos armados del HUD rebel

Se generaron retratos compuestos en `game/gui/battle/hud_rebel/portraits`:

- `portrait_megumin_rebel.png`
- `portrait_megumin_rebel_facing.png`
- `portrait_aqua_rebel.png`
- `portrait_aqua_rebel_facing.png`
- `portrait_darkness_rebel.png`
- `portrait_darkness_rebel_facing.png`
- `portrait_kazuma_rebel.png`
- `portrait_kazuma_rebel_facing.png`
- `portrait_ino_rebel.png`
- `portrait_ino_rebel_facing.png`
- `portrait_sakura_rebel.png`
- `portrait_sakura_rebel_facing.png`
- `portrait_karin_rebel.png`
- `portrait_karin_rebel_facing.png`
- `portrait_boruto_rebel.png`
- `portrait_boruto_rebel_facing.png`

Cada retrato usa las capas experimentales del portarretrato rebel y deja el personaje recortado dentro del marco. El HUD usa estos PNG si el personaje actual tiene retrato armado; para otros personajes mantiene el fallback anterior.

Actualizacion 2026-05-26:

- Se sumaron Kazuma, Ino, Sakura, Karin y Boruto al mapa de retratos.
- `kazuma` tambien acepta el alias `kasuma`.
- Las rutas de Aqua, Darkness y Megumin se cambiaron a los nombres limpios de `game/images/character`.

Actualizacion de conexion:

- Se agrego `bs_battle_rebel_portrait_path` para devolver directamente el PNG armado del HUD rebel.
- `battle_hp_overlay` ahora dibuja esa ruta directa para jugador y enemigo.
- Si no hay retrato armado para el personaje, el HUD conserva `portrait_player_jugador_a_rebel.png` o `portrait_enemy_hollow_rebel_facing.png`.

Se conecto con:

- `game/06A_BATTLE_HUD_COMPAT_STUBS.rpy`: el HUD ahora consulta los retratos nuevos si existen; si no, cae al fallback anterior.
- `game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy`: al confirmar acciones ofensivas del jugador, dispara la pose si el personaje tiene asset mapeado.
- `game/4/j/04D_DEFENSIVE_ACTIONS.rpy`: al confirmar acciones defensivas relevantes, dispara la pose si el personaje tiene asset mapeado.

## Alcance actual

- Funciona para Aqua, Darkness y Megumin.
- El disparo visual esta conectado al jugador.
- En 2v2 intenta usar el actor actual si existe; si no, usa `battle_player_id`.
- Todavia no se conectaron poses de la IA/enemigo.
- Los crops de retrato son ajustes iniciales y pueden refinarse visualmente.

## Nota de continuidad 2026-06-07 - Pruebas de imagenes de heroes

La carpeta `game/images/character` esta siendo usada como zona activa de pruebas visuales para heroes.

Estado observado:

- En la raiz hay imagenes limpias o candidatas actuales como `aqua.png`, `darkness.png`, `megumin.png`, `kazuma.png`, `ino.png`, `karin.png`, `boruto.png` y `sakura.png`.
- Tambien hay variantes de estilo, por ejemplo `*-style-01-cel.png`, `*-style-02-keyart.png`, `*-style-03-chibi.png` y archivos `* spe.png`.
- `game/images/character/hechos` conserva retratos ya generados o seleccionados para varios heroes.
- `game/images/character/pendientes` conserva renders de CharaStudio todavia sin cerrar como asset final.

Regla para futuras sesiones:

- Tratar esta carpeta como laboratorio visual, no como catalogo final cerrado.
- Antes de borrar o renombrar imagenes, revisar si estan mapeadas en `game/06B_BATTLE_CHARACTER_VISUALS.rpy`.
- Cuando un heroe quede aprobado, mover/normalizar su asset hacia un nombre estable y actualizar el mapa de retratos/poses.
- Mantener separados los retratos compuestos del HUD rebel en `game/gui/battle/hud_rebel/portraits`.
- La carpeta obsoleta `game/gui/battle/hud_ai` fue retirada; los fallbacks deben apuntar al HUD rebel o a assets actuales.

Piloto aplicado:

- Boruto se regenero desde `game/images/character/hechos/boruto-portrait-style-01-cel.png`.
- Salidas actualizadas:
  - `game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel.png`
  - `game/gui/battle/hud_rebel/portraits/portrait_boruto_rebel_facing.png`
- El armado se hizo por capas del marco rebel: base violeta, heroe recortado al pentagono, lineas cyan y shard lateral. La version enemy se genero espejando el resultado completo, igual que la logica actual.
- Se agrego el generador `tools/build_hud_rebel_portraits.py` para que el retrato final sea reproducible.
- Las capas runtime del marco quedaron en `game/gui/battle/hud_rebel/portrait_layers`.
- Se ajusto el overlay del HUD para escalar el retrato a `162x135`, acercarlo al frame HP y bajar la opacidad del fondo lateral.
- Se dejo una previsualizacion del piloto en `docs/materiales_experimentales/hud/hud_rebel_v2_boruto_preview.png`.

Decision tecnica:

- Mantener PNGs finales para Ren'Py.
- Mantener heroes, marcos y posiciones como fuentes modulares para regenerar resultados.
- No migrar el resto de Tier C hasta aprobar visualmente el piloto Boruto.

## Nota de continuidad 2026-06-07 - Barra HP up-flare experimental

Se implemento una nueva barra HP experimental basada en la variante agresiva elegida:

- inicio fino a la izquierda;
- curva ascendente hacia la derecha;
- final mas alto/ancho;
- base negra desplazada debajo;
- HP actual en verde;
- dano pendiente en rojo, usando la misma logica de `*_damage_fake`.

Archivos nuevos:

- `tools/build_hud_rebel_upflare_bars.py`
- `game/gui/battle/hud_rebel/upflare_bars/`

El HUD anterior no fue borrado. Quedo deshabilitado por variable:

- activo nuevo: `default bs_battle_hud_rebel_style = "upflare"`
- fallback viejo: `default bs_battle_hud_rebel_style = "legacy"`

La pantalla `battle_hp_overlay` conserva ambos caminos. La primera prueba uso `im.Crop` sobre PNGs curvos para mantener la logica de porcentaje sin estirar una barra rectangular.

## Fix 2026-06-07 - Rutas de retratos en seleccion

La pantalla de staging/preparacion podia fallar al seleccionar heroes cuyos `hud` apuntaban a imagenes raiz ya retiradas, por ejemplo `images/character/ino.png`.

Se actualizaron los `hud` de Megumin, Aqua, Darkness, Kazuma, Ino, Sakura, Karin y Boruto para usar `game/images/character/hechos`.

Tambien se reforzo `bs_character_visual_asset`: si una ruta declarada no es cargable por Ren'Py, devuelve vacio y deja que el flujo use fallback, evitando crasheos por assets faltantes.

## Fix 2026-06-07 - Empate y subsurface de barras up-flare

Al forzar un empate con la tool aparecio este error en Ren'Py 7.4.9:

- `subsurface size must be non-negative`
- el traceback caia durante `battle_end_result`, en el dialogo `"Ambos equipos han caido."`

Diagnostico:

- El texto de empate no era el origen real.
- El HUD de combate seguia renderizando durante el cambio de pantalla.
- Las barras `upflare` usaban `im.Crop` dinamico para mostrar porcentajes.
- En HP 0, empate o transiciones de fin de combate, Ren'Py 7.4.9 puede calcular una subsuperficie invalida.

Solucion aplicada:

- `tools/build_hud_rebel_upflare_bars.py` ahora genera pasos estaticos `000-100`.
- Se agregaron pasos para jugador/enemigo y para verde/rojo:
  - `game/gui/battle/hud_rebel/upflare_bars/steps/player`
  - `game/gui/battle/hud_rebel/upflare_bars/steps/enemy`
- `battle_hp_overlay` ya no usa `im.Crop` para las barras up-flare.
- El HUD calcula un porcentaje seguro `0-100` y carga el PNG correspondiente.
- Se documento el motivo en `game/gui/battle/hud_rebel/upflare_bars/README.md`.

Validacion:

- `renpy.exe lint` con SDK Ren'Py 7.4.9 paso sin errores.
- Se eliminaron los `.rpyc`; conteo final: `0`.

## Nota tecnica 2026-06-07 - Versiones de Ren'Py

Estado local observado:

- SDK actual usado para validar: `D:\aplocaciones\rempy\renpy-7.4.9-sdk`
- SDK moderno ya instalado: `D:\aplocaciones\rempy\renpy-8.4.1-sdk`

Decision sugerida:

- Mantener `7.4.9` para commits de esta tanda, porque el proyecto ya valida ahi.
- Probar migracion en rama aparte con `8.4.1` antes de saltar a una version mas nueva.
- El salto a Ren'Py 8 implica Python 3, por lo que conviene auditar helpers Python viejos antes de adoptarlo.

## Verificacion

- `git diff --check` sin errores en los archivos tocados.
- `renpy.exe lint` ejecutado sin errores.
