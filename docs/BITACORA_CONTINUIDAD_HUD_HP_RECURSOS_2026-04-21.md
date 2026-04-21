# Bitácora de continuidad — HUD HP/Recursos/Durabilidad (en suspenso)
Fecha: 2026-04-21
Estado: **en suspenso** (prioridad temporal a lógica/programación)

## Contexto de sesión
Se evaluó iniciar una mejora gráfica del HUD de combate para HP y recursos, tomando como referencia un estilo moderno con:
- barras inclinadas,
- máscara de recorte para visualizar solo el tramo válido,
- combinación de elementos estáticos (marcos PNG) y dinámicos (relleno por código + animaciones).

Durante la sesión se decidió **no implementar todavía** la mejora visual y mantener el HUD funcional actual para evitar desviar foco de objetivos de lógica.

## Lo que sí quedó definido (documentado)
1. **Dirección visual tentativa**
   - Barra inclinada con look moderno.
   - Uso de máscara para recorte de relleno.
   - Capas de recurso separadas (HP / Estamina / Shadow / espacio libre), alineadas al contrato funcional vigente.

2. **Criterio técnico recomendado (cuando se retome)**
   - Enfoque híbrido:
     - Arte estático (marcos/ornamentos en PNG).
     - Estado dinámico por código (valores/porcentajes/animación).
   - Mantener legibilidad priorizando números críticos sin inclinación excesiva.

3. **Alcance de Fase 0 (preparación) ya delimitado**
   - Definir assets mínimos (frame, mask, gloss).
   - Definir grado de inclinación y guideline tipográfica.
   - Confirmar reglas visuales para HP/Estamina/Shadow/Durabilidad.

## Estado actual del proyecto respecto al HUD
- Se conserva el HUD actual de combate (funcional) como baseline.
- No se realizaron cambios de código en esta sesión para el HUD.
- La mejora gráfica queda explícitamente en backlog, sin iniciar implementación.

## Decisión de priorización
A partir de la próxima sesión se priorizará:
1. lógica de combate,
2. programación de flujo/estado,
3. robustez funcional y QA de comportamiento,

antes de volver a tareas de polish visual del HUD.

## Pendientes para retomar la mejora gráfica más adelante
1. Reabrir Fase 0 de HUD (brief de arte + checklist técnico).
2. Prototipo visual no destructivo (feature flag) sin reemplazar baseline.
3. Integración progresiva (HP -> recursos -> durabilidad).
4. QA visual/funcional y validación de rendimiento.

## Nota de continuidad
La mejora gráfica de **HUD de HP + recursos + durabilidad** queda en estado **suspendido** hasta nueva instrucción de priorización.
