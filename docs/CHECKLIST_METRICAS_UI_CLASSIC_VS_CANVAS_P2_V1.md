# P2-01 — Checklist de métricas UI: Classic vs Canvas (v1)

Fecha: 2026-04-14  
Estado: Aprobado (listo para ejecución por QA/UI)

---

## 1) Objetivo

Medir de forma comparable el costo/beneficio entre `lobby_classic` y `lobby_canvas_experimental` para decidir adopción parcial o descarte.

---

## 2) Escenarios mínimos de medición

Ejecutar en ambos modos (`classic` y `canvas`) los mismos flujos:

1. Home -> Héroes -> compra de héroe -> volver Home.
2. Home -> Tienda -> compra de ítem -> Inventario.
3. Home -> Catálogo técnicas -> volver Home.
4. Home -> Torre preview -> volver Home.

Cada flujo debe repetirse 5 veces y registrar promedio.

---

## 3) Métricas técnicas obligatorias

## 3.1 Rendimiento

- [ ] Tiempo de apertura inicial de lobby (ms).
- [ ] Tiempo de navegación entre pantallas clave (ms).
- [ ] FPS estable durante scroll/listados (promedio y p5).
- [ ] Caídas de frame >16ms por minuto.

## 3.2 Robustez

- [ ] Errores runtime por flujo (conteo).
- [ ] Reintentos manuales por acción (conteo).
- [ ] Fallos de interacción (botón no responde/estado desincronizado).

## 3.3 Mantenibilidad

- [ ] Complejidad percibida del cambio (baja/media/alta).
- [ ] Cantidad de puntos de acoplamiento UI<->negocio.
- [ ] Reutilización de casos de uso comunes (sí/no + evidencia).

## 3.4 UX funcional

- [ ] Feedback de compra visible y consistente.
- [ ] Oro/inventario actualizan sin refresh manual.
- [ ] Navegación no se rompe en back/forward.

---

## 4) Resultado de comparación

Registrar para cada métrica:
- `classic` valor,
- `canvas` valor,
- delta,
- interpretación.

Resultado final:
- [ ] GO Canvas parcial
- [ ] GO Classic-only (postergar Canvas)
- [ ] NO-GO Canvas

---

## 5) Criterios de aceptación P2-01

1. Todas las métricas completadas para ambos modos.
2. Hay conclusión trazable (GO/NO-GO).
3. Quedan riesgos y mitigaciones explícitos.

