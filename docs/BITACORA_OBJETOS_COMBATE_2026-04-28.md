# Bitacora - Objetos de combate y UX pre-duelo (2026-04-28)

## Contexto

Sesion enfocada en mejorar el flujo de duelo libre/pre-combate y abrir el primer corte del sistema de objetos de combate.

El proyecto estaba funcionando sin bugs visibles antes de esta iteracion. Se trabajo sobre UX de seleccion rapida de heroes y sobre la base tecnica para pasar de compra/inventario a uso dentro del combate.

## UX de pre-combate

Se ajusto la pantalla de pre-combate para evitar desplazamientos innecesarios y duplicacion de botones.

Cambios principales:

- Boton inferior fijo para iniciar duelo, visible sin bajar hasta el final del panel.
- Se elimino el boton duplicado de Preparacion que aparecia dentro del panel izquierdo.
- Se agrego una casilla rapida de heroe en Resumen de entrada.
- El marco/retrato de la casilla funciona como boton para agregar/cambiar heroe.
- En modo 2v2 aparece una segunda casilla para J2.
- El selector rapido de heroes tiene filtro `Solo disponibles`, activado por defecto.
- La `x` bajo la casilla solo aparece cuando hay heroe seleccionado:
  - J1 limpia seleccion principal.
  - J2 limpia el segundo slot.

Archivos principales:

- `game/ui_hub/ui_hub_screens_prep.rpy`
- `game/ui_hub/ui_hub_state.rpy`
- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`

## Sistema de objetos - Primer corte

Se implemento la base del loadout de objetos para combate.

Reglas actuales:

- Pociones: maximo 5 slots.
- Amuleto: maximo 1 slot.
- Sellos: maximo 3 slots.

El loadout se arma en pre-combate desde el inventario de cuenta. Al iniciar duelo se crea un snapshot runtime para que el combate use esa carga preparada.

## Uso en combate

Se agrego el boton `Usar objeto` en el selector de acciones del combate.

Disponible en:

- Turno ofensivo.
- Turno defensivo.

El boton abre una ventana modal con pestanas:

- Pociones.
- Amuleto.
- Sellos.

Estado funcional:

- Pociones HP: funcionales.
- Amuletos: visibles, efecto pendiente.
- Sellos: visibles, efecto pendiente.

## Pociones HP

La pocion HP puede usarse tanto en ataque como en defensa.

Comportamiento actual:

- Consume 1 accion del turno.
- Cura segun porcentaje definido en el catalogo (`+50% HP`, `+35% HP`, `+25% HP`).
- No supera el HP maximo.
- Descuenta 1 unidad del inventario de cuenta.
- Actualiza barras/overlay de HP cuando los helpers runtime estan disponibles.
- Registra mensaje en el log de combate.

Se agrego control para que el gasto de accion por objeto no sea ignorado si luego se reconstruye la simulacion del selector.

## Archivos tocados

- `game/ui_hub/ui_hub_state.rpy`
- `game/ui_hub/ui_hub_screens_prep.rpy`
- `game/12_BATTLESTARS_SAGA_UI_HUB_V1.rpy`
- `game/04F_SELECTOR_MENUV2.rpy`
- `game/04F_SELECTOR_FUNCTIONSV2.rpy`
- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`

## Verificacion realizada

- `git diff --check` paso sin errores.
- No se pudo correr lint de Ren'Py porque `renpy` no esta disponible en PATH.
- No se pudieron correr tests Python porque `pytest` no esta instalado en el entorno.

## Pendientes

- Probar en runtime dentro de Ren'Py:
  - Compra de pocion.
  - Preparar pocion en pre-combate.
  - Iniciar duelo.
  - Usar pocion HP en turno ofensivo.
  - Usar pocion HP en turno defensivo.
  - Validar descuento de inventario.
  - Validar consumo de accion.
- Definir efectos reales para:
  - Pociones EP.
  - Pociones EC.
  - Pociones de durabilidad.
  - Amuletos.
  - Sellos.
- Decidir si el descuento de inventario debe ser inmediato al usar o consolidado al final del combate.
- Mejorar la UI de loadout si el inventario crece mucho, posiblemente con modal dedicado y filtros por categoria.

## Estado de cierre

Primer corte implementado y listo para prueba manual en Ren'Py.

El sistema ya conecta inventario/pre-combate/combate para pociones HP. Amuletos y sellos quedaron preparados a nivel de UI y estructura, pero sin efectos activos hasta definir reglas de balance.
