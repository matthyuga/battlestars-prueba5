# Phase 1 Validation — Vertical Slice jugable estable

Fecha: 2026-04-04
Alcance validado: F1-T1, F1-T2, F1-T3, F1-T4, F1-T5

---

## F1-T1 — Verificar flujo actual

Objetivo:
`start -> tl_boot_start -> gate -> registro -> hub -> clases -> volver al hub`

Resultado (inspección de scripts): **PASS**

Evidencia:
- `start` redirige a `tl_boot_start`.
- `tl_boot_start` envía a `tl_sakura_gate` al confirmar Sakura.
- `tl_sakura_gate` permite ir a registro o volver.
- `tl_player_registration` continúa a hub o vuelve a gate.
- `tl_sakura_hub` entra a `go_lessons`, abre `tl_lessons_mock_screen` y retorna al hub.

---

## F1-T2 — Confirmar hotspots START/ENTER y navegación de retorno

Resultado (inspección de scripts): **PASS**

Evidencia:
- Hotspot START en menú principal (`Return("goto_sakura_gate")` cuando Sakura está seleccionada).
- Hotspot ENTER en puerta Sakura (`Return("register")`).
- Botones de retorno (`Volver`) en gate/registro y retorno general al hub desde lecciones.

---

## F1-T3 — Mantener blur + dark overlay en aula de lecciones

Resultado (inspección de scripts): **PASS**

Evidencia:
- Fondo de aula en lecciones usa `add bg at tl_soft_focus`.
- Overlay oscuro activo `add Solid("#00000088")` para legibilidad de UI.

---


## F1-T4 — Conectar botón “Probar Typing Lab” y retorno limpio al hub

Resultado (inspección de scripts): **PASS**

Evidencia:
- En lecciones, el botón ahora retorna `open_typing_lab` en lugar de hacer `Jump` directo.
- En `tl_sakura_hub`, al volver de `tl_lessons_mock_screen`, se detecta `open_typing_lab`, se hace `call typing_lab_start` y luego se regresa al hub.
- Este patrón evita salida abrupta del flujo y garantiza ida/vuelta limpia desde Clases.

---

## F1-T5 — Mensajes fallback claros cuando falta asset

Resultado (inspección de scripts): **PASS**

Evidencia:
- Se añadieron mensajes explícitos de fallback para fondos faltantes en:
  - menú principal,
  - puerta Sakura,
  - registro,
  - hub,
  - lecciones.
- Los mensajes informan ruta faltante y uso de fallback visual.

---
## Riesgo / limitación de entorno

No se pudo ejecutar validación runtime con Ren'Py en esta sesión de CLI porque el binario `renpy` no está disponible en PATH.

Recomendación de cierre de fase:
1. Ejecutar smoke test visual in-engine en entorno con Ren'Py.
2. Registrar captura/video corto del flujo completo (start -> clases -> volver hub).

---

## Estado de Fase 1 (actual)

- F1-T1: ✅ Cumplida por inspección de código.
- F1-T2: ✅ Cumplida por inspección de código.
- F1-T3: ✅ Cumplida por inspección de código.
- F1-T4: ✅ Cumplida por inspección de código.
- F1-T5: ✅ Cumplida por inspección de código.
- Runtime end-to-end en engine: ⚠️ Pendiente por dependencia de entorno.


## DoD Fase 1 (estado)

- Demo continua 3–5 min sin bloqueos: ⚠️ Pendiente de prueba in-engine (renpy no disponible en esta CLI).
- Navegación ida/vuelta 100% funcional: ✅ Verificada por inspección de flujo y retornos de labels/screens.
