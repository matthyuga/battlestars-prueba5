# Typing Legends — Rediseño Arquitectura (Fase 0)

Fecha: 2026-04-06  
Estado: ✅ Completado (baseline congelado + contrato mínimo + zonas de extracción)

## 1) Baseline congelado

- Archivo baseline temporal: `typing-games/game/10_SAKURA_BOOTSTRAP_V1.rpy`.
- Regla de trabajo: no agregar features nuevas aquí; solo fixes críticos mientras se migra.

## 2) Contrato mínimo de integración (engine)

Contrato propuesto para el router de sublecciones:

- **Entrada:** `sublesson_id: str`
- **Salida:** `result: str` con uno de:
  - `complete`
  - `back_class`
  - `error`

Notas:
- `complete` habilita registrar check académico.
- `back_class` regresa al panel de submódulos sin registrar check.
- `error` permite fallback seguro a placeholder y logging técnico.

## 3) Zonas actuales a extraer de bootstrap

- [x] Panel de submódulos (`tl_classes_lesson_panel_screen`).
- [x] Intro 1.1 (`tl_sublesson_intro_screen`).
- [x] Router de sublecciones (`tl_classes_lesson_panel_flow` con `if/elif`).
- [x] Selección docente + retratos/fallback.

## 4) Mapa de extracción (origen -> destino)

- `10_SAKURA_BOOTSTRAP_V1.rpy` (UI submódulos/intro/router)
  - ➜ `20_CHARACTERS_DB_V1.rpy` (data personajes)
  - ➜ `21_LESSONS_DB_V1.rpy` (data lecciones)
  - ➜ fases siguientes: `30_*` engine, `40_*` screens

## 5) Criterio para iniciar Fase 1

Fase 1 inicia cuando:
1. Exista DB de personajes (docentes/compañeros + sexo + hooks).
2. Exista DB de lecciones (1.1 real + 1.2..1.7 placeholder).
3. No haya UI/flujo embebido dentro de archivos de DB.

