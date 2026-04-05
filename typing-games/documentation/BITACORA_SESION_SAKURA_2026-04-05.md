# Bitácora de sesión — Sakura Sunshine Academy

**Fecha:** 2026-04-05  
**Proyecto:** Typing Legends / Sakura Sunshine Academy  
**Objetivo de la sesión:** estabilizar flujo MVP (Fase 0–5) y cerrar ruta principal de Clases (modo aprendizaje).

---

## 1) Resumen ejecutivo

En esta sesión se avanzó sobre el flujo completo de acceso y núcleo académico:

- Se estabilizó el arranque hasta Hub (Gate → Registro → Bienvenida → Pasillo).
- Se convirtió el Hub en mapa de navegación con módulos y lugares placeholder.
- Se implementó flujo por capas para Clases (categoría → docente → intro curso → panel de sublecciones).
- Se cerró Modo 1 (aprendizaje puro) reduciendo ruido social/romance.
- Se agregó soporte de QA técnico/UX dentro del juego (checklist, save/load desde panel de lecciones, feedback de botones sensibles).
- Se corrigió un crash real en selección de docente por sustitución de texto incompatible con Ren'Py 7.4.

---

## 2) Cambios funcionales realizados

## Fase 0 — Hotfix de estabilidad

- Se eliminaron sustituciones frágiles con acceso directo a dict dentro de textos de pantalla.
- Se introdujo helper seguro para `done/total` de progreso académico.
- Resultado: menor riesgo de `KeyError`/errores de sustitución en Hub/Diario/Biblioteca.

## Fase 1 — Flujo visual de acceso Sakura

- Gate ajustado para `sakura_intro`.
- Registro con fondo de entrada y validación de nombre por `trim`.
- Slide de bienvenida agregado con botón único de avance al Hub.
- Flujo consolidado: Inicio → Gate → Registro → Bienvenida → Hub.

## Fase 2 — Hub Pasillo como mapa

- Hub con fondo de pasillo y panel central de navegación.
- Módulos visibles: Clases, Repaso/Práctica, Exámenes, Juegos/Actividades, Biblioteca (+ Diario existente).
- Lugares placeholder: Entrada y Patio con retorno limpio.

## Fase 3 — Módulo Clases (núcleo)

- Selección académica: Básica habilitada, Intermedia/Avanzada en “próximamente”.
- Selección docente: Haru/Misaki con feedback visual de selección.
- Presentación de curso y panel de lección 1 (submódulos 1.1–1.7).
- Inicio de sublección con mapeo de modo Typing Lab y marcado de check al volver.
- Persistencia de checks reflejada visualmente en panel.

## Fase 4 — Modo 1 sin ruido narrativo/social

- Modo 1 prioriza mecanografía y oculta componentes de romance en vistas sociales.
- Se redujo narrativa a mensajes cortos de foco académico.

## Fase 5 — QA técnico y UX

- Se añadió pantalla in-game de QA técnico con checklist rápido.
- Se añadió acceso a Guardar/Cargar en panel de sublecciones (validación de save/load en mitad de flujo).
- Botones sensibles muestran feedback textual cuando están bloqueados.

---

## 3) Corrección crítica aplicada (error reportado por runtime)

### Error observado

- `NameError` en `tl_classes_teacher_screen` por sustitución inline en texto:
  - `"Docente elegida/o: [tl_selected_teacher if tl_selected_teacher else '—']"`

### Causa

- En Ren'Py 7.4, ciertas expresiones inline complejas en `[]` pueden fallar en sustitución.

### Solución implementada

- Precalcular variables (`_teacher_label`, `_teacher_name`, `_selected_label`) y luego interpolar nombres simples.
- Reubicar presentación docente al paso previo a selección de lecciones.
- Resultado: pantalla de docente deja de crashear y flujo queda más claro.

---

## 4) Estado actual del flujo de Clases

Flujo actual:

1. Selección de categoría (Básica)
2. Selección de docente (Haru/Misaki)
3. Presentación breve docente + listado de lecciones disponibles
4. Botón “Ver lecciones”
5. Panel Lección 1 (1.1–1.7)
6. Selección de sublección
7. Lanzamiento Typing Lab
8. Retorno con check actualizado

---

## 5) Archivos más impactados en la sesión

- `typing-games/game/10_SAKURA_BOOTSTRAP_V1.rpy` (principal, flujo/UI/QA/fixes)
- `typing-games/documentation/BITACORA_SESION_SAKURA_2026-04-05.md` (esta bitácora)

Nota: los backends de checks/afinidad/romance se mantuvieron como base operativa para esta etapa.

---

## 6) Pendientes para la próxima sesión

- Ajustes finos de UX visual (espaciados, tamaños, copy final).
- Ampliar contenido docente (más líneas por sublección si se desea).
- Validación runtime real con binario Ren'Py (smoke E2E + save/load + navegación completa).
- Revisión final de assets/sprites definitivos de Haru/Misaki.

---

## 7) Nota operativa

Esta bitácora se deja como punto de continuidad para retomar en la siguiente sesión sin perder contexto de decisiones, flujo y estado técnico.
