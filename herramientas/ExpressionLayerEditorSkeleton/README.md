# Expression Layer Editor - Skeleton v0.2 (Paso 1 limpio para escalar)

Este directorio contiene una base C# orientada a un plugin BepInEx/Koikatsu para edición de expresiones faciales con arquitectura preparada para escalar.

## Qué cambió en esta versión
- Se introdujo una separación más limpia entre:
  - **Runtime adapter** (`ICharacterRuntimeAdapter`) para conectar luego con KKAPI/Studio.
  - **Repositorio de presets** (`IPresetRepository`) en lugar de guardar/cargar por path suelto.
  - **Opciones de plugin** (`PluginOptions`) para configuración centralizada.
  - **Logger** (`ILogger`) para desacoplar salida (luego BepInEx logger).
- Se añadió `CompositionRoot` para bootstrap consistente.

## Estado actual (Paso 1)
- Ya existe un flujo MVP completo para:
  - personaje activo,
  - aplicar macro,
  - guardar/cargar preset,
  - snapshots A/B,
  - autokey opcional.
- Implementación por defecto con adapters en memoria y timeline nulo para prototipado.

## Estructura
- `src/Models.cs`: modelos + `PluginOptions`.
- `src/Interfaces.cs`: contratos escalables (runtime, preset repo, logger, etc.).
- `src/Services.cs`: servicios base y stubs (`JsonFilePresetRepository`, `InMemoryCharacterRuntimeAdapter`, etc.).
- `src/ExpressionLayerEditorOrchestrator.cs`: servicio de aplicación principal.
- `src/CompositionRoot.cs`: ensamblado de dependencias default.

## Siguiente implementación recomendada
1. Crear `BepInExCharacterRuntimeAdapter : ICharacterRuntimeAdapter`.
2. Crear `BepInExLogger : ILogger`.
3. Crear `TimelinePluginBridge : ITimelineBridge`.
4. Añadir panel IMGUI para operaciones principales (macro, preset, snapshot, autokey).
