# Acta de cierre — Fase 0 Lobby MVP v0.1

Fecha: 2026-04-14  
Estado: Cerrada
Alcance: cierre de P0-07 y P0-08 para habilitar entrada a P1.

---

## 1) Decisiones aprobadas

## D1 — Feature flag `experimental_canvas_ui` (P0-07)

Se define el comportamiento operativo del flag de UI experimental:

- Nombre canónico: `experimental_canvas_ui`.
- Tipo: boolean.
- Valor por defecto: `false`.
- Semántica:
  - `false` => UI `lobby_classic`.
  - `true` => UI `lobby_canvas_experimental`.
- Regla de seguridad: ante error en modo experimental, fallback inmediato a `lobby_classic`.

## D2 — Gate de salida formal de Fase 0 (P0-08)

Se aprueba el gate con 4 checks obligatorios:

1. Scope in/out sin ambigüedad.
2. Contratos de estado congelados.
3. Checklist no-regresión de combate disponible.
4. Tablero priorizado P0/P1/P2 publicado.

Resultado del gate: **PASS**.

---

## 2) Evidencia de cierre

- Scope/contratos/invariantes documentados en:
  - `docs/FASE0_ALINEACION_CONTRATOS_LOBBY_V0_1.md`
- Checklist no-regresión publicado en:
  - `docs/CHECKLIST_NO_REGRESION_COMBATE_LOBBY_V0_1.md`
- Tablero priorizado y actualizado en:
  - `docs/TABLERO_FASE0_LOBBY_P0_P1_P2.md`

---

## 3) Riesgos abiertos y mitigación inmediata

1. Riesgo: desvío de reglas de negocio entre classic/canvas.  
   Mitigación: casos de uso únicos en capa de negocio + checklist no-regresión por cada entrega P1.

2. Riesgo: ambigüedad al arrancar P1 en responsabilidades.  
   Mitigación: checklist de arranque P1 con entregables por tarea y criterio DoD.

---

## 4) Resolución

Con esta acta, **Fase 0 queda cerrada** y se autoriza inicio de ejecución de **P1-01 a P1-05**.

