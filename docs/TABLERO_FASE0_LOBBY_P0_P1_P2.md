# Tablero Fase 0 — Lobby MVP (P0/P1/P2)

Fecha: 2026-04-14  
Estado: Fase 0 cerrada · P1 implementada (QA final pendiente)

Uso:
- Actualizar `Estado` en cada sesión: `todo | doing | blocked | done`.
- Si una tarea queda en `blocked`, documentar causa y siguiente acción.

Referencia de ejecución P1: `docs/ARRANQUE_P1_LOBBY_V0_1.md`.

---

## P0 (bloqueante de arranque)

| ID | Tarea | Entregable | Estado | Responsable |
|---|---|---|---|---|
| P0-01 | Confirmar in-scope / out-of-scope v0.1 | Scope firmado | done | Equipo core |
| P0-02 | Congelar contrato `account_state` | Contrato v0.1 | done | Gameplay/State |
| P0-03 | Congelar contrato `hero_*` (catalog/owned) | Contrato v0.1 | done | Gameplay/State |
| P0-04 | Congelar contrato `inventory_state` | Contrato v0.1 | done | Gameplay/State |
| P0-05 | Congelar contrato `audit_event` + eventos mínimos | Contrato v0.1 | done | Gameplay/State |
| P0-06 | Publicar checklist no-regresión combate | Checklist v0.1 activo | done | QA |
| P0-07 | Definir feature flag `experimental_canvas_ui` | Config de entorno | done | UI |
| P0-08 | Definir gate de salida Fase 0 | Acta de cierre F0 | done | PM/Tech lead |

---

## P1 (importante, siguiente paso)

| ID | Tarea | Entregable | Estado | Responsable |
|---|---|---|---|---|
| P1-01 | Implementar store lobby unificado | Módulo state base | done | Gameplay/State |
| P1-02 | Implementar `buy_hero` + validaciones | Use case operativo | done | Gameplay |
| P1-03 | Implementar `buy_item` + validaciones | Use case operativo | done | Gameplay |
| P1-04 | Conectar auditoría económica | Log funcional | done | Gameplay/QA |
| P1-05 | Vertical slice Home/Héroes/Tienda/Inventario | Demo E2E interna | done | UI |

---

## P2 (mejora / hardening)

| ID | Tarea | Entregable | Estado | Responsable |
|---|---|---|---|---|
| P2-01 | Definir métricas técnicas de UI (classic vs canvas) | Checklist evaluación | todo | UI/Tech lead |
| P2-02 | Documentar contrato toolkit -> lobby (import/export simple) | Borrador v0.1 | todo | Data/Tools |
| P2-03 | Diseñar template de reporte Go/No-Go del spike canvas | Plantilla decisión | todo | PM |
| P2-04 | Pre-adaptadores para catálogos JSON canónicos | Plan v0.2 | todo | Data/Gameplay |

---

## Gate de cierre Fase 0 (check rápido)

- [x] Alcance sin ambigüedad.
- [x] Contratos de estado congelados.
- [x] Checklist no-regresión combate listo.
- [x] Acta de cierre Fase 0 firmada.

