# Bitacora HUD rebel y perfiles de heroes

Fecha: 2026-06-12

## Contexto

Se trabajo sobre el HUD de combate modular para reemplazar el portarretrato viejo por una version nueva tipo rebel/upflare, usando primero a `danny_phantom` como caso de prueba y fallback visual.

## Cambios realizados

- Se conectaron los perfiles de heroes desde `game/images/character/hechos/tmp-imagegen`.
- Se agrego fallback de retrato HUD rebel hacia Danny Phantom cuando un heroe aun no tiene imagen propia.
- Se deshabilito visualmente el HUD compacto viejo que quedaba por detras del HUD nuevo.
- Se quitaron los paneles negros semitransparentes del HUD nuevo.
- Se genero una version v3 del portarretrato de Danny Phantom:
  - base oscura tipo rombo/hexagono;
  - borde cyan y brillo violeta moderado;
  - retrato mas limpio y menos invasivo sobre la barra de HP.
- Se agregaron placas modernas para el nombre de jugador y enemigo.
- Se dejo el generador `tools/build_hud_rebel_portraits.py` preparado para regenerar la version v3.

## Archivos principales

- `game/06A_BATTLE_HUD_COMPAT_STUBS.rpy`
- `game/06B_BATTLE_CHARACTER_VISUALS.rpy`
- `tools/build_hud_rebel_portraits.py`
- `game/gui/battle/hud_rebel/nameplates/`
- `game/gui/battle/hud_rebel/portrait_layers_v3/`
- `game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_v3.png`
- `game/gui/battle/hud_rebel/portraits/portrait_danny_phantom_rebel_facing_v3.png`
- `game/images/character/hechos/tmp-imagegen/`

## Validacion

Se ejecuto lint con Ren'Py 8.5.3:

```powershell
& 'D:\aplocaciones\rempy\8.5.3\renpy-8.5.3-sdk\renpy.exe' 'D:\2026\battlestars-prueba5' lint
```

Resultado: sin errores nuevos. Se mantienen avisos previos del proyecto sobre prioridad de init, `Harribel_a.png` y `im.Scale`.

## Pendiente

- Probar visualmente Danny vs Danny dentro del combate.
- Si el estilo v3 queda aprobado, generar el mismo portarretrato por tandas para los demas heroes.
- Revisar si conviene mover definitivamente los calculos de nombres fuera del HUD viejo invisible para retirar ese bloque completo en una limpieza posterior.
