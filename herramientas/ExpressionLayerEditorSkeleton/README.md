# Expression Layer Editor - Skeleton v0.4 (Paso 3)

Este directorio contiene una base C# orientada a un plugin BepInEx/Koikatsu para edición de expresiones faciales con arquitectura preparada para escalar.

## Qué incluye Paso 3
- Mantiene todo el Paso 2 (macros, presets, snapshots, timeline por rango).
- Añade capa de **presentación/controlador** para desacoplar UI del dominio:
  - `ExpressionEditorController` para callbacks de botones/acciones IMGUI.
  - `IExpressionEditorView` para mostrar info, warnings, errores y refrescar presets.
- Añade stubs de integración productiva para host/plugin real:
  - `BepInExLogger`
  - `BepInExCharacterRuntimeAdapter`
  - `TimelinePluginBridge`
- Añade `CompositionRoot.CreateProduction(...)` para inyectar adapters reales desde el plugin host.

## Estado actual
- El core ya soporta:
  - edición por macro,
  - guardado/carga de presets,
  - snapshots A/B y blend,
  - autokey,
  - operaciones de rango temporal.
- Paso 3 deja preparada la entrada a plugin real sin acoplar la lógica a IMGUI/BepInEx directamente.

## Estructura
- `src/Models.cs`: modelos + `TimelineRange`.
- `src/Interfaces.cs`: contratos de dominio e interfaz de vista.
- `src/Services.cs`: servicios y adapters in-memory.
- `src/ExpressionLayerEditorOrchestrator.cs`: lógica principal.
- `src/Presentation/ExpressionEditorController.cs`: controlador de UI.
- `src/Adapters/BepInExAdapterStubs.cs`: stubs de integración real.
- `src/CompositionRoot.cs`: bootstrap para prototipado y producción.

## Próximo paso sugerido
1. Crear plugin BepInEx real que llame `CreateProduction(...)`.
2. Implementar `IExpressionEditorView` con IMGUI.
3. Reemplazar stubs de `Adapters/` con llamadas reales a KKAPI/Timeline.
4. Agregar tests unitarios del controlador y orquestador.
