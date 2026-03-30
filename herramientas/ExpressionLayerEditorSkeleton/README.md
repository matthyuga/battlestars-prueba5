# Expression Layer Editor - Skeleton v0.1

Este directorio contiene un esqueleto de código C# orientado a un plugin BepInEx/Koikatsu para edición de expresiones faciales por capas.

## Objetivo
- Servir como base para implementar el plugin **Expression Layer Editor (ELE)**.
- Separar responsabilidades (contexto de personaje, composición, constraints, presets, snapshots, timeline bridge y UI).

## Estado actual
- Esqueleto (interfaces + clases base + modelos de datos).
- Sin dependencias externas (BepInEx/KKAPI/Timeline) para mantenerlo portable.
- Métodos clave marcados con `throw new NotImplementedException()` o implementación mínima.

## Estructura
- `src/Models.cs`: modelos de datos y enums.
- `src/Interfaces.cs`: contratos de servicios.
- `src/Services.cs`: implementaciones stub de servicios.
- `src/ExpressionLayerEditorOrchestrator.cs`: coordinador de flujo principal.

## Próximo paso sugerido
1. Reemplazar `Console.WriteLine` por logger BepInEx.
2. Conectar `CharacterContextService` a objeto de personaje activo en Studio.
3. Implementar `TimelineBridge` contra plugin Timeline real.
4. Añadir UI IMGUI/Unity UI.
