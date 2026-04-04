# Bitácora de sesión — Sakura Sunshine Academy (bootstrap)

Fecha de cierre: 2026-04-04

## Contexto trabajado
Se avanzó sobre una base MVP de navegación para **Typing Legends** enfocada en **Sakura Sunshine Academy**, con idea de separar:
- `typing-games/documentation` (lore, planes, vínculos)
- `typing-games/typing-master` (fuente de lecciones y estructura TM)
- `typing-games/game` (proyecto Ren'Py jugable)

## Lo que se implementó en código durante esta sesión
1. **Entrada del juego redirigida al bootstrap Sakura**
   - `start` ahora salta a `tl_boot_start`.

2. **Flujo base Sakura (MVP)**
   - Menú principal Typing Legends.
   - Puerta/entrada Sakura.
   - Registro de jugador (nombre, sexo, modo de experiencia).
   - Hub de academia con módulos:
     - Clases
     - Práctica
     - Exámenes
     - Actividades
     - Diario
     - Biblioteca

3. **Regla de diseño aplicada en registro**
   - Si `sexo = none`, el modo se fuerza a `modo 1`.

4. **Vista de lecciones mock**
   - Lección 1 (subclases 1.1–1.7) como layout de prueba.
   - Puente temporal a `typing_lab_start`.

5. **Mejoras de UX aplicadas luego del feedback**
   - Selección por puerta + START como acción final.
   - Hotspot sobre ENTER en puerta Sakura.
   - Estado visible de selección en registro (`✓` en sexo/modo).
   - Corrección de crash de interpolación Ren'Py en hub (se reemplazó expresión inline por bloque `if/else`).

## Problemas detectados
1. **Desfase de ramas/entorno local**
   - En el entorno local de trabajo, `typing-games/game` aparecía incompleto (solo algunos `.rpy`).
   - En la rama remota indicada por el usuario sí estaban `gui/`, `images/`, `screens.rpy`, etc.
   - Esto explicó por qué en local se usaban fallbacks visuales en lugar de arte real.

2. **No se ejecutaron pruebas runtime con Ren'Py en este entorno**
   - El binario `renpy` no estaba disponible en esta sesión de CLI para correr validación final in situ.

## Estado al cerrar
- Existe una base funcional para arrancar Sakura-first.
- Queda pendiente en siguiente sesión:
  1. Sincronizar entorno local con rama remota completa.
  2. Reapuntar rutas de assets reales en `typing-games/game/images` y `typing-games/game/gui`.
  3. Ajustar hotspots pixel-perfect con los fondos finales.
  4. Revalidar visualmente con ejecución Ren'Py.

## Archivos clave tocados/relacionados
- `typing-games/game/script.rpy`
- `typing-games/game/10_SAKURA_BOOTSTRAP_V1.rpy`
- `game/12_TYPING_LEGENDS_LESSON1_BLUEPRINT.rpy`

