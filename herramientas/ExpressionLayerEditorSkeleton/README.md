# Expression Layer Editor - Skeleton v0.3 (Paso 2)

Este directorio contiene una base C# orientada a un plugin BepInEx/Koikatsu para edición de expresiones faciales con arquitectura preparada para escalar.

## Qué incluye Paso 2
- Continúa la arquitectura limpia del Paso 1 (runtime adapter, preset repository, logger, composition root).
- Añade capacidades de timeline para flujo de animación:
  - `SetTimelineFrame(int frame)`
  - `AutoKeyModified(...)`
  - `ApplySnapshotBlendToRange(TimelineRange, smoothStep)`
  - `ApplyPresetAcrossRange(preset, TimelineRange, intensity)`
- Incorpora `InMemoryTimelineBridge` para prototipar keyframes por frame y rangos con interpolación lineal.

## Estado actual
- MVP cubre:
  - personaje activo,
  - macros,
  - presets,
  - snapshots A/B,
  - autokey y operaciones por rango temporal.

## Estructura
- `src/Models.cs`: modelos + `PluginOptions` + `TimelineRange`.
- `src/Interfaces.cs`: contratos escalables.
- `src/Services.cs`: servicios base y stubs (`JsonFilePresetRepository`, `InMemoryCharacterRuntimeAdapter`, `InMemoryTimelineBridge`, etc.).
- `src/ExpressionLayerEditorOrchestrator.cs`: lógica principal de aplicación.
- `src/CompositionRoot.cs`: bootstrap por defecto.

## Próximo paso recomendado (Paso 3)
1. Implementar adapters reales:
   - `BepInExCharacterRuntimeAdapter`
   - `TimelinePluginBridge`
   - `BepInExLogger`
2. Agregar UI IMGUI para:
   - selector de presets,
   - snapshot A/B + slider t,
   - acciones de rango temporal.
3. Añadir pruebas unitarias para `SnapshotService`, `InMemoryTimelineBridge` y `ExpressionLayerEditorOrchestrator`.
