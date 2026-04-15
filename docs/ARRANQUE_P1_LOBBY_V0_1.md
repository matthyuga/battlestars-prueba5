# Arranque P1 — Lobby MVP v0.1

Fecha: 2026-04-14  
Estado: Listo para ejecutar
Precondición: Fase 0 cerrada con acta.

---

## 1) Objetivo de P1

Construir el núcleo técnico del lobby para habilitar el primer vertical slice funcional:

1. store lobby unificado,
2. `buy_hero` con validaciones,
3. `buy_item` con validaciones,
4. auditoría económica,
5. conexión UI mínima a estado real.

---

## 2) Orden de ejecución recomendado

## Sprint P1-A (base de negocio)

- P1-01: implementar store lobby unificado.
- P1-02: implementar `buy_hero`.
- P1-03: implementar `buy_item`.
- P1-04: integrar `audit_event`.

## Sprint P1-B (vertical slice)

- P1-05: Home/Héroes/Tienda/Inventario conectados al store real.

---

## 3) Definition of Ready (DoR) por tarea

## P1-01 Store

- Contratos de estado congelados disponibles.
- Lista de módulos consumidores identificada (UI classic/canvas).

## P1-02 `buy_hero`

- Catálogo de héroes accesible en store.
- Validaciones definidas: existe, no duplicado, oro suficiente.

## P1-03 `buy_item`

- Catálogo de ítems accesible en store.
- Política de qty v0.1 confirmada (`qty=1`).

## P1-04 Auditoría

- Estructura `audit_event` congelada.
- Eventos mínimos confirmados: `buy_hero`, `buy_item`, `gold_delta`.

## P1-05 Vertical slice

- Navegación base habilitada.
- Mensajería de éxito/error definida.

---

## 4) Definition of Done (DoD) de P1

P1 se considera completo cuando:

1. Las operaciones `buy_hero` y `buy_item` pasan happy-path + error-path.
2. `gold` e inventario reflejan cambios consistentes tras cada operación.
3. Cada operación económica válida genera `audit_event`.
4. UI muestra datos del store real (sin mocks ocultos).
5. Checklist no-regresión de combate ejecutado sin bloqueantes.

---

## 5) Checklist operativo diario (P1)

- [ ] Levantar rama de trabajo de P1.
- [ ] Implementar 1 tarea P1 por ciclo.
- [ ] Ejecutar smoke no-regresión al cierre de cada tarea.
- [ ] Actualizar tablero (`todo/doing/blocked/done`).
- [ ] Registrar bloqueantes y decisión tomada.

---

## 6) Entregables esperados de entrada a P1

1. PR del store unificado + validaciones.
2. PR de auditoría conectada.
3. PR del vertical slice navegable.
4. Evidencia de ejecución del checklist no-regresión.

