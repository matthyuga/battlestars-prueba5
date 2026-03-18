# Sesión de diagnóstico — Pre-combate visible, cuelgue en fase ofensiva

Fecha: 2026-03-18  
Proyecto: Battlestars (Ren'Py 7.4.11, entorno reportado Win7 SP1 / 4 GB RAM)

## Contexto reportado
- Se observaban congelamientos al pasar por configuraciones de editor de puntos + pre-combate y luego entrar al combate.
- Se implementó un modo diagnóstico para el panel de pre-combate con:
  - métricas tipo FPS de UI (`FPS_UI~`),
  - contadores/costos promedio y máximos por función instrumentada,
  - controles ON/OFF/Reset/Overlay.

## Incidencias detectadas en esta sesión
1. **Crash inicial del overlay diagnóstico**
   - Error: `AttributeError: 'StoreModule' object has no attribute 'precombat_diag_report_text()'`.
   - Causa: intento de invocar función dentro de interpolación de texto Ren'Py (`"[store.precombat_diag_report_text()]"`).
   - Corrección aplicada: evaluar primero en variable local del screen y renderizarla como texto (`$ _diag_text = ...`, `text "[_diag_text]"`).

2. **Estado funcional tras fix**
   - El diagnóstico **se ve correctamente en el panel de pre-combate**.
   - Confirmación del usuario: el overlay aparece y muestra métricas.

3. **Problema actual pendiente (crítico)**
   - Al iniciar el duelo, el juego se vuelve lento y **en fase ofensiva deja de reaccionar**.
   - El diagnóstico actual no cubre runtime de combate, solo pre-combate.

## Conclusiones de sesión
- El problema de bloqueo **no quedó resuelto**; solo se estabilizó y habilitó observabilidad en pre-combate.
- El nuevo foco de investigación debe moverse al runtime de combate (especialmente transición e interacción en fase ofensiva).

## Hipótesis priorizadas para próxima sesión
1. Re-evaluación/cómputo excesivo dentro de screens del HUD ofensivo.
2. Funciones de resolución ofensiva con loops o reconstrucción de estructuras por interacción.
3. Congestión por redraw + logs + acciones de botón en cadena durante entrada a ofensiva.
4. Cuello de CPU/RAM amplificado por Win7 + 4 GB (swapping), revelando ineficiencias de runtime.

## Plan sugerido (próxima sesión)
1. Instrumentar también screens/runtime de combate (no solo pre-combate):
   - conteo de redraw en HUD de combate,
   - tiempos por bloque ofensivo/defensivo,
   - marcadores de entrada/salida de labels críticos.
2. Agregar “puntos de corte” de diagnóstico en:
   - inicio de combate,
   - inicio de turno ofensivo,
   - selección de técnica,
   - resolución de acción,
   - actualización del log/narrador.
3. Probar escenarios A/B:
   - directo a combate sin pre-combate,
   - con pre-combate mínimo,
   - con y sin navegador abierto en máquina objetivo.
4. Extraer un caso mínimo reproducible de cuelgue ofensivo para aislar regresión.

## Estado para handoff
- Se cierra sesión dejando diagnóstico pre-combate activo y usable.
- Se difiere la solución del freeze de fase ofensiva a una sesión dedicada de runtime combate.
