# Backlog exacto por fases (Expression Layer Editor)

> Objetivo: llevar el skeleton actual a plugin usable en CharaStudio con riesgo controlado.

## Supuestos
- Prioridad principal: edición de expresiones faciales amigable.
- Timeline se integra después de tener runtime + UI estable.
- Se trabaja en vertical slices para validar cableado real cuanto antes.

---

## Fase 0 — Vertical Slice mínimo (bloqueante técnico)
**Meta:** probar conexión real plugin ↔ CharaStudio con mínimo alcance.

### Tareas
1. Crear plugin host mínimo BepInEx (entrypoint + Awake/OnGUI).
2. Implementar `BepInExLogger` funcional.
3. Implementar `BepInExCharacterRuntimeAdapter` con soporte inicial de 3-5 blendshapes.
4. Implementar vista IMGUI mínima:
   - 1 slider
   - 1 botón "Apply"
   - 1 botón "Save preset"
5. Enlazar con `CompositionRoot.CreateProductionUi(...)`.

### Criterios de salida
- El plugin carga en Studio sin errores.
- El slider cambia blendshape en personaje activo en tiempo real.
- Se puede guardar y cargar al menos un preset.

### Estimación
- 1 a 2 días.

---

## Fase 1 — Runtime estable (núcleo de integración)
**Meta:** hacer robusto el acceso a personaje/estado facial.

### Tareas
1. Completar `BepInExCharacterRuntimeAdapter`:
   - resolver personaje activo,
   - leer registry de parámetros faciales,
   - leer estado actual,
   - aplicar estado completo.
2. Manejar casos borde:
   - no hay personaje seleccionado,
   - personaje destruido/cambiado,
   - escena vacía.
3. Añadir logging contextual en errores críticos.
4. Validar rendimiento básico (no spikes al mover sliders).

### Criterios de salida
- Lectura/escritura facial estable durante sesión larga.
- Sin excepciones no controladas al cambiar personaje/escena.

### Estimación
- 2 a 3 días.

---

## Fase 2 — UX real (editor usable)
**Meta:** convertir la vista en herramienta diaria de trabajo.

### Tareas
1. Portar `ExpressionEditorWindow` a IMGUI real (paneles):
   - Header/contexto,
   - Macros,
   - Presets,
   - Snapshots,
   - Layer panel,
   - Warnings/errors.
2. Conectar todos los handlers de `ExpressionEditorController`:
   - initialize/refresh,
   - save/load/delete/duplicate preset,
   - apply/reset por capa,
   - reset global,
   - blend A/B.
3. Añadir modo básico/avanzado visible.
4. Añadir busy state y feedback en UI.

### Criterios de salida
- Flujo completo sin salir del panel.
- Usuario puede construir una expresión en < 30 segundos.

### Estimación
- 3 a 4 días.

---

## Fase 3 — Timeline básico (post-prioridad)
**Meta:** integración mínima con timeline, sin complejidad avanzada.

### Tareas
1. Implementar `TimelinePluginBridge` básico:
   - detectar disponibilidad,
   - leer frame actual,
   - set key para parámetro.
2. Activar `OnAutoKeyModified` en UI.
3. Activar `ApplySnapshotBlendToRange` y `ApplyPresetAcrossRange` en UI (modo simple).
4. Manejar degradación si timeline no está instalado.

### Criterios de salida
- Keyframes básicos funcionando en rango corto.
- UI no rompe si Timeline plugin no existe.

### Estimación
- 2 días.

---

## Fase 4 — Calidad y hardening
**Meta:** confiabilidad para uso real.

### Tareas
1. Tests unitarios:
   - `ExpressionLayerEditorOrchestrator`,
   - `ExpressionEditorController`,
   - `JsonFilePresetRepository`.
2. Ejecutar checklist smoke del README en sesión real.
3. Corregir regresiones y edge cases detectados.
4. Documentar troubleshooting común.

### Criterios de salida
- Suite de tests pasando.
- Smoke checklist completado sin fallos críticos.

### Estimación
- 2 a 3 días.

---

## Orden recomendado de ejecución
1. Fase 0
2. Fase 1
3. Fase 2
4. Fase 3
5. Fase 4

---

## Definición de “MVP listo para usar”
Se considera MVP cuando:
- El plugin carga y funciona en CharaStudio.
- Permite editar expresiones por capa en tiempo real.
- Permite guardar/cargar presets.
- Permite snapshots A/B y blend.
- No crashea en cambios de personaje/escena.

Timeline avanzado queda fuera del MVP inicial.
