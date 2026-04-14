# Plan Spike — HTML-in-Canvas para Lobby Battlestars Saga (v0.1)

Fecha: 2026-04-14  
Estado: Aprobado para ejecutar (spike exploratorio)

---

## 1) Objetivo

Evaluar si `HTML-in-Canvas` aporta valor real al lobby semifuncional sin comprometer estabilidad, mantenibilidad ni compatibilidad.

---

## 2) Hipótesis de trabajo

1. HTML-in-Canvas puede mejorar calidad visual y composición UI del lobby.
2. Para MVP, su uso debe ser opcional y bajo feature flag.
3. No debe bloquear el flujo principal del juego ni del toolkit.

---

## 3) Alcance del spike

## 3.1 In-scope

- Probar un módulo de lobby visual (Home + 1 submódulo) con HTML-in-Canvas.
- Medir:
  - rendimiento percibido,
  - complejidad de implementación,
  - estabilidad de interacción.
- Documentar riesgos técnicos.

## 3.2 Out-of-scope

- Migración total del lobby.
- Integración con combate.
- Dependencia obligatoria en producción.

---

## 4) Criterios Go / No-Go

## Go (continuar)

- El prototipo mantiene UX fluida y navegación estable.
- El costo de mantenimiento es razonable.
- No rompe el flujo base de lobby clásico.

## No-Go (detener)

- Fragilidad alta de implementación.
- Demasiada dependencia de flags/entornos no estables.
- Sobrecosto de mantenimiento frente a valor visual.

---

## 5) Estrategia técnica

1. Mantener **arquitectura dual**:
   - `lobby_classic` (base estable)
   - `lobby_canvas_experimental` (flag)
2. No tocar lógica de negocio:
   - compras,
   - inventario,
   - auditoría.
3. Reusar contratos del MVP v0.1 para estado y eventos.

---

## 6) Plan por pasos

## Paso 1 — Preparar entorno (0.5 día)

- Integrar carpeta `html-canvas` al contexto de trabajo local.
- Definir bandera `experimental_canvas_ui`.
- Crear pantalla demo aislada.

## Paso 2 — Prototipo visual mínimo (1 día)

- Construir Home Lobby experimental con:
  - barra de recursos,
  - navegación principal,
  - botón de acceso a Tienda.

## Paso 3 — Integración funcional mínima (1 día)

- Conectar un caso real: `buy_item` con estado compartido.
- Verificar actualización de oro e inventario en UI experimental.

## Paso 4 — Evaluación objetiva (0.5 día)

- Comparar clásico vs canvas en:
  - esfuerzo de implementación,
  - legibilidad del código,
  - robustez de interacción,
  - costo de mantenimiento.

## Paso 5 — Decisión técnica (0.5 día)

- Emitir informe final con decisión Go/No-Go.
- Si Go: definir fase de adopción parcial.
- Si No-Go: mantener clásico y archivar learnings.

---

## 7) Entregables del spike

1. Demo funcional experimental (acotada).
2. Checklist de resultados técnicos.
3. Informe de decisión Go/No-Go.
4. Plan de siguiente fase (si aplica).

---

## 8) Riesgos y mitigación

1. **Riesgo:** dependencia de funcionalidades experimentales.
   - Mitigación: feature flag + fallback clásico.
2. **Riesgo:** sobrecosto de mantenimiento UI.
   - Mitigación: usarlo sólo en módulos con alto retorno visual.
3. **Riesgo:** desalineación con roadmap MVP.
   - Mitigación: limitar spike a una vertical pequeña.

---

## 9) Definición de éxito del spike

El spike es exitoso si permite tomar una decisión técnica informada en < 4 días hábiles, sin bloquear implementación del Lobby MVP clásico.
