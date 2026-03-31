# Expression Layer Editor - Skeleton v0.5 (Commit 8)

Este módulo es una base C# para construir un editor de expresiones faciales de Koikatsu con separación limpia de capas:
- Dominio/orquestación
- Presentación/controlador
- Adapters de host (BepInEx/KKAPI/Timeline)

## Estado actual de implementación
### ✅ Listo
- Core de expresión: macros, presets, snapshots, blend y constraints.
- Operaciones por capa facial (consultar parámetros, aplicar valores, reset por capa/global).
- Repositorio de presets con operaciones CRUD básicas (`save/load/list/exists/delete/rename`).
- Controller UI-first (`ExpressionEditorController`) con handlers para flujo de edición.
- View host-agnostic (`ExpressionEditorWindow`) para adaptarse a IMGUI.
- CompositionRoot con factories para:
  - prototipo in-memory,
  - producción,
  - producción + UI.

### 🚧 Pendiente (para plugin real)
- Implementar adapters reales:
  - `BepInExCharacterRuntimeAdapter`
  - `TimelinePluginBridge`
  - `BepInExLogger`
- Sustituir el render textual de `ExpressionEditorWindow.Draw()` por IMGUI real en host.
- Añadir tests unitarios automáticos.


## Avance Fase 2 (inicio)
- `ExpressionEditorWindow` se amplió con flujo UI-first: selección/carga/guardado de presets, aplicación de macros, snapshots, edición por capas y modo básico/avanzado.
- Se añadieron hooks explícitos para mapear controles IMGUI del host a handlers del controller.

## Avance Fase 1 (inicio)
- `BepInExCharacterRuntimeAdapter` ahora tiene manejo defensivo de errores, fallback de personaje válido y cache de registry por personaje.
- `TimelinePluginBridge` ahora degrada de forma segura ante errores (sin romper flujo) y reporta warnings por logger.

## Avance Fase 0 (inicio)
- Los adapters de host ya pueden cablearse por delegados (`BepInExCharacterRuntimeAdapter`, `TimelinePluginBridge`, `BepInExLogger`) sin depender de tipos de Unity/BepInEx dentro de este proyecto.
- Se añadió `Phase0VerticalSliceBootstrap` para armar rápidamente el par `(orchestrator, controller)` con adapters reales del host.

## Flujo de uso recomendado (actual)
1. Inicializar controller/window:
   - `CreateProductionUi(...)` (host real) o
   - `CreateDefault(...)` + `CreateUiController(...)` (prototipo).
2. Llamar `OnInitialize()` desde UI.
3. Refrescar presets/macros/capas según interacción.
4. Aplicar macro/preset/snapshot blend desde handlers del controller.
5. Guardar preset y validar warnings de constraints.

## Checklist manual de QA (smoke)
Usar este checklist para validar comportamiento base después de cambios:

1. **Carga inicial**
   - [ ] `OnInitialize()` no arroja error.
   - [ ] Personaje activo visible en la vista.
2. **Presets**
   - [ ] Guardar preset nuevo funciona.
   - [ ] Cargar preset aplica cambios.
   - [ ] Duplicar preset funciona con/ sin overwrite.
   - [ ] Eliminar preset lo quita del listado.
3. **Expresión**
   - [ ] Aplicar macro modifica estado.
   - [ ] `OnApplyLayerValues` modifica solo la capa objetivo.
   - [ ] `OnResetVisibleLayer` resetea la capa.
   - [ ] `OnResetAllFace` resetea todo.
4. **Snapshots**
   - [ ] Capturar A/B funciona.
   - [ ] Slider de blend aplica transición sin error.
5. **UX/diagnóstico**
   - [ ] Busy state activa/desactiva en acciones.
   - [ ] Warnings y errores llegan a vista.

## Prioridad de roadmap
1. UI amigable + capa de expresiones (prioridad máxima).
2. Integración host real de runtime facial.
3. Integración timeline avanzada (después).
4. Pruebas automáticas.
