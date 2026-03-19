# Bitácora integral — HP, HP falso, Estamina, Shadow y espacio libre

Fecha: 2026-03-19
Estado: Documento de continuidad para próxima sesión

---

## 0) Propósito
Esta bitácora resume el recorrido completo desde la idea inicial de **HP falso visual** hasta la formalización del modelo **HP + Estamina + Shadow**, incluyendo problemas detectados, ajustes de UX/rendimiento, decisiones funcionales y contrato técnico vigente.

Objetivo de continuidad: que una nueva sesión pueda retomar sin pérdida de contexto ni ambigüedades.

---

## 1) Evolución conceptual (timeline)

## 1.1 Inicio: HP falso visual (gris)
- Se parte de un requerimiento visual: dejar una “marca” gris cuando el HP baja.
- Primera implementación enfocada en HUD (sin recurso jugable real todavía).
- Estado inicial llamado internamente como `hp_fake_*`.

## 1.2 Ajustes visuales/compatibilidad
- Correcciones de sintaxis Ren'Py para `bar` y alpha vía transform.
- Resolución de visibilidad: la parte vacía opaca de la barra superior ocultaba la capa gris inferior.
- Se transparentó `right_bar` de la barra superior para que la capa gris pudiera verse.

## 1.3 Ajustes de timing
- Se probaron variantes:
  - persistente congelado,
  - desaparición instantánea tras delay,
  - fade final.
- Se estabilizó un comportamiento de “delay + tail fade” para naturalidad visual.

## 1.4 Problemas de trigger y rendimiento
- Problema detectado: updates de HP sin cambio podían resetear/cancelar el efecto.
- Solución: no reiniciar el efecto cuando `new_ratio == old_ratio`.
- Problema de micro-lag: tick muy frecuente.
- Solución: aumentar intervalo de tick para reducir carga de refresco UI.

## 1.5 Selector de técnicas (paralelo UX)
- Fase A: reducción de tamaño + scroll vertical.
- Fase B: pantalla/panel de técnicas con separación por tipo.
- Fase C: pulido visual.
- Ajuste final: mostrar **solo el panel correspondiente al turno** (ofensivo o defensivo).

## 1.6 Salto de “visual fake HP” a “recurso jugable”
- El gris pasa de efecto visual a candidato de recurso: **Estamina**.
- Se introduce concepto **Shadow** (negro) como bloqueo de espacio para generar estamina nueva.
- Se define “espacio vacío libre” como parámetro explícito.

---

## 2) Definiciones funcionales consolidadas

## 2.1 HP normal (celeste)
- Vida real de la unidad.
- Regla inviolable: si HP llega a 0 en la resolución del golpe => KO.

## 2.2 Estamina (gris)
- Recurso derivado del daño real a HP.
- Para generarse requiere:
  1. Daño real a HP.
  2. Espacio libre disponible.
- Estamina previa puede absorber daño posterior.
- Por norma general, estamina gastada no se recompone automáticamente.

## 2.3 Shadow / Sombra (negro)
- No daña por sí mismo: bloquea espacio para generación nueva de estamina.
- No anula estamina previa ya existente.
- Persistente por defecto (hasta desactivación/negación/expiración según diseño de perks/técnicas).
- Puede ser parcial (ocupación desde derecha hacia izquierda).

## 2.4 Espacio vacío libre (parámetro)
Propuesto como:

`free_space = max(0, hp_max - hp_current - stamina_current - shadow_current)`

Este parámetro gobierna cuánto puede entrar de estamina nueva.

---

## 3) Reglas de resolución acordadas (alto nivel)
Orden de hit propuesto:
1. Coating/cobertura/durabilidad.
2. Estamina absorbe daño (si existe).
3. Overflow a HP.
4. KO gate (si HP <= 0, termina).
5. Generación de estamina si sobrevive + hay espacio + perk habilita.

Notas clave:
- Si daño excede estamina + HP en el golpe actual => KO.
- Si sobrevive con HP > 0, puede generar estamina (si no está bloqueado por shadow y hay espacio libre).

---

## 4) Logging esperado (acordado)
Secuencia textual recomendada:
1. `Estamina: xxxx - daño = xxx`
2. `Estamina: xxxx - daño = -overflow` (si aplica)
3. `HP: xxxx - daño = xxx`
4. `HP genera xxx de estamina` (si aplica)
5. `Shadow bloquea xxx de espacio` (si aplica)

Objetivo: trazabilidad completa de cada resolución.

---

## 5) Estado técnico actual del repo (resumen)

## 5.1 HUD (HP falso)
- Existe capa gris funcional y configurable bajo barra de HP.
- Variables actuales en HUD con naming `hp_fake_*` (histórico visual).
- Falta migrar naming a entidad jugable oficial (`stamina_*`, `shadow_*`) en todo el flujo.

## 5.2 Combate/facade
- La función de daño por unidad ya devuelve estructura rica (`hp_before`, `hp_after`, coating, spill).
- Es el punto natural para integrar estamina/shadow como lógica real.

## 5.3 Selector
- Scroll vertical y tamaño reducido aplicados.
- Panel de técnicas limitado al tipo correspondiente al turno.

## 5.4 Documentación
- Existe contrato v1 formal (`CONTRATO_ESTAMINA_SHADOW_V1.md`).
- Esta bitácora lo complementa con narrativa de decisiones y contexto operativo.

---

## 6) Riesgos identificados
1. Solape semántico entre “hp_fake visual” y “estamina real” si no se migra naming.
2. Duplicidad de logs si se emiten en varias capas sin un helper canónico.
3. Inconsistencias de espacio si no se mantiene el invariante `stamina + shadow <= missing_hp`.
4. Degradación de UX si se vuelve a sobrecargar ticks de HUD.

---

## 7) Próximos pasos sugeridos (para nueva sesión)

## Paso 1 — Backend mínimo (estado real)
- Añadir campos reales de estamina/shadow por unidad en battle facade.
- Conservar compatibilidad con estado actual.

## Paso 2 — Resolución de daño
- Implementar orden completo (coating -> estamina -> HP -> KO -> generación).

## Paso 3 — Logging canónico
- Centralizar logs de estamina/HP/shadow con formato acordado.

## Paso 4 — Migración HUD
- Renombrar transición de `hp_fake_*` a `stamina_*`.
- Añadir barra negra real de shadow.

## Paso 5 — Integración perks/técnicas
- Activación/desactivación de estamina y shadow por perk/efecto.

## Paso 6 — QA
- Casos de overflow, KO, shadow parcial, supervivencia con 1 HP, etc.

---

## 8) Criterios de salida para considerar “v1 lista”
- Reglas de daño reproducibles y determinísticas.
- Logs completos por hit, sin duplicados.
- HUD alineado con estado real (no solo visual fake).
- KO consistente con regla de HP=0.
- Shadow parcial funcionando y limitando generación según espacio.

---

## 9) Nota final de traspaso
Esta bitácora está pensada para handoff directo a una nueva sesión. Si se retoma implementación, comenzar por **backend/facade** antes de ampliar UI, para evitar deuda técnica por desalineación entre lógica y visual.
