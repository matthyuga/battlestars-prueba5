# Phase 6 Plan — QA, balance y expansión

Fecha: 2026-04-04
Objetivo: pulir la experiencia antes de escalar contenido.
Estado: En ejecución (ongoing).

---

## F6-T1 — QA funcional (rutas, retorno, save/load, edge cases)

## Checklist de rutas críticas
- [ ] Menú -> Sakura -> Registro -> Hub -> Clases -> Hub.
- [ ] Clases -> Typing Lab -> retorno limpio al Hub.
- [ ] Hub -> Práctica (letters/words/phrases) -> retorno.
- [ ] Hub -> Exámenes -> evaluación score -> retorno.
- [ ] Hub -> Actividades (quest) -> check + afinidad.
- [ ] Hub -> Diario tabs (académico/social) -> retorno.
- [ ] Hub -> Biblioteca tabs (cursos/personajes) -> retorno.

## Checklist de persistencia
- [ ] Guardar/cargar con checks académicos previos.
- [ ] Guardar/cargar con afinidad modificada.
- [ ] Guardar/cargar con romance modificado (modo 3 + elegibilidad).
- [ ] Carga de save viejo sin romper estructura (`_*_ensure_store`).

## Edge cases mínimos
- [ ] Player `gender=none`: romance bloqueado con mensaje correcto.
- [ ] `mode!=3`: romance bloqueado con mensaje "Disponible solo en modo 3".
- [ ] Afinidad no supera 10 ni baja de 0.
- [ ] Romance no supera 24 ni baja de 0.

---

## F6-T2 — Balance de puntos

## Afinidad
Regla actual: +1 por interacción/misión exitosa.

### Criterios de balance
- [ ] Alcanzar 10 puntos no debe ocurrir en menos de 8–10 interacciones.
- [ ] Progressión debe sentirse consistente entre personajes.
- [ ] Ajustar eventos repetibles para evitar farmeo trivial.

## Romance
Regla actual: crecimiento por eventos de romance (modo 3 + elegibilidad).

### Criterios de balance
- [ ] Evitar desbloqueo romance por accidente en primeras sesiones.
- [ ] Mantener ritmo más lento que afinidad social.
- [ ] Revisar mapeo visual 0..24 -> p0..p25 para sensación de progreso.

---

## F6-T3 — QA visual (barras, corazón, fallback assets)

## Checklist visual
- [ ] Barras de afinidad renderizan c0..c10 correctamente por personaje.
- [ ] Corazón renderiza p0..p25 sin glitches en modo 3 elegible.
- [ ] Mensajes de bloqueo romance aparecen en casos no elegibles.
- [ ] Mensajes fallback de assets faltantes son legibles y no tapan acciones clave.
- [ ] Diario social y ficha social mantienen consistencia visual de estados.

---

## F6-T4 — Preparar expansión

## Backlog de expansión inmediata
- [ ] Activar uso completo de `p25` como hito final de romance (cuando diseño lo confirme).
- [ ] Rutas por personaje (mínimo 1 evento exclusivo por personaje principal).
- [ ] Más quests sociales (mínimo 3 adicionales con distinta recompensa).
- [ ] Lecciones nuevas (Lección 2+) con checks y desbloqueo progresivo.

---

## DoD de Fase 6

- [ ] Build estable para pruebas externas.
- [ ] Sin bloqueos críticos en flujo principal.
- [ ] Save/load consistente para académico/social/romance.

---

## Tablero sugerido (actualizado)

- **Now (inmediato):** F6-T1 (QA funcional) + F6-T3 (QA visual)
- **Next:** F6-T2 (balance fino)
- **Then:** F6-T4 (expansión controlada)
- **Ongoing:** F6 (ciclo QA -> ajuste -> revalidación)

---

## Mini plantilla por tarea (copiar/pegar)

- **ID:** F3-T2
- **Resumen:** Crear `add_affinity(character_id, amount=1)`
- **Entrada:** interacción/misión exitosa
- **Salida:** puntos 0..10 + refresh UI
- **Criterio aceptación:** no pasa de 10 ni baja de 0; persistencia OK
- **Dependencias:** F0-T2, F3-T1
- **Estimación:** 2–3h
