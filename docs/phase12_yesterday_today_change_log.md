# Phase 12 — Bitácora de cambios (ayer y hoy)

> Objetivo: dejar una referencia única y corta de todos los ajustes recientes para retomar en nueva sesión sin perder contexto.

## 1) Resumen ejecutivo

En estas últimas iteraciones se consolidaron cinco frentes:

1. **Flujo 2v2/turnos**: correcciones de avance de turno y consumo de flags por unidad.
2. **Negador (NO ATK) por unidad**: se evitó semántica global en 2v2.
3. **Focus/Concentrar por equipo**: se aisló ownership para evitar “robo” o acumulación cruzada.
4. **Dados/UI**: tiradas etiquetadas, tiradas independientes por técnica y layout múltiple.
5. **Selector multijugador manual**: nuevo modo para elegir tamaño de equipos `P`/`E` (1..2) y HUD adaptado a 1v2/2v1.

---

## 2) Línea de commits recientes (ordenados de más nuevo a más antiguo)

- `6083f2d` — hide absent slots in HUD for 1v2 and 2v1.
- `3c487b9` — fix KeyError de sustitución Ren'Py en resumen multijugador.
- `eac5c53` — modo multijugador manual con selector de cantidad P/E.
- `2142345` — dos paneles de dados lado a lado (Directo+Negador) + etiqueta en IA.
- `a83e76e` — tiradas separadas por técnica (Directo y Negador).
- `0760032` — split 2v2 sin efectos especiales ofensivos.
- `d1803e4` — base de NO ATK por unidad + Focus team-aware (iteración previa de fixes 2v2).

---

## 3) Cambios funcionales por bloque

### A. NO ATK / turnos 2v2

- Se migró el comportamiento de `NO ATK` a semántica por unidad en 2v2 para que afecte al objetivo real, no al “próximo actor global”.
- Se corrigieron casos de avance incorrecto de turno (repetición de actor) cuando había skip/negador activo.

### B. Focus / Concentrar

- Se agregó ownership por equipo para `Focus` ofensivo.
- Se evitó que cargas de un equipo se apliquen o acumulen sobre el otro.
- Se corrigieron escenarios donde la IA terminaba beneficiándose de `Concentrar` del jugador (y viceversa).

### C. Dados (jugador + IA)

- Directo y Negador ya no comparten una sola tirada cuando se usan juntos.
- Cada técnica tiene su tirada independiente y su etiqueta visual.
- Si hay 2 técnicas con dados en el mismo turno, se renderizan **dos tarjetas lado a lado**.
- IA también muestra etiqueta de técnica al tirar dados.

### D. Split damage 2v2

- Cuando se usa daño dividido (`split_equal` / `split_manual`) en 2v2, el daño se procesa “limpio”:
  - sin dados,
  - sin efecto de negador,
  - sin directo indefendible,
  - sin reducción de defensa.

### E. Selector multijugador manual y UX

- Se agregó nuevo modo: **Multijugador (manual P/E)**.
- Permite elegir cantidad de integrantes por equipo (`P=1/2`, `E=1/2`) manteniendo los modos clásicos 1v1 y 2v2.
- Se ajustó la finalización de equipos para permitir configuraciones 1v2/2v1.
- Se corrigió crash por sustitución inválida en diálogo (`[len(...)]`).
- HUD/resumen 2v2 ahora ocultan slots inexistentes en 1v2/2v1.

---

## 4) Estado actual para próxima sesión

### Estable

- Modo multijugador manual disponible en selector.
- Flujo base de turnos funcional con skips por unidad.
- Dados etiquetados y layout múltiple funcionando.
- HUD sin “fantasmas” de slots inexistentes en 1v2/2v1.

### A vigilar (QA manual recomendado)

1. Ciclos largos de turnos con combinaciones: `Negador + Directo + split`.
2. Casos borde de 2v1 con KO temprano del único integrante del bando corto.
3. Persistencia/rollback de flags keyed:
   - `player_skip_attack_by_key`
   - `enemy_skip_attack_by_key`
4. Coherencia entre “orden mostrado” y actor real en popups de transición.

---

## 5) Checklist corto para retomar trabajo

Antes de nuevos cambios:

1. Ejecutar limpieza de build: `bash scripts/qa_clean_build.sh`.
2. Probar smoke manual mínimo:
   - 1v1,
   - 2v2,
   - 1v2,
   - 2v1.
3. Validar en cada modo:
   - skip por unidad correcto,
   - Focus no cruza equipo,
   - dados por técnica (single/multi),
   - HUD sin slots inexistentes.

