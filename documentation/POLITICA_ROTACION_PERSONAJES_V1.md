# POLITICA_ROTACION_PERSONAJES_V1

Fecha: 2026-04-06  
Estado: Política operativa inicial

## 1) Objetivo

Regular cómo se seleccionan y publican personajes de rotación libre semanal sin afectar la progresión permanente del jugador.

---

## 2) Reglas base

1. Cada rotación dura 7 días exactos.
2. Pool objetivo: 10 personajes libres por semana.
3. Estado temporal de acceso: `free_rotation`.
4. Al finalizar semana, el acceso temporal expira automáticamente.
5. Un personaje desbloqueado permanente ignora rotación.

---

## 3) Criterios de selección de pool

- Diversidad mínima por tier (evitar mono-tier continuo).
- Diversidad de franquicia/arquetipo.
- Evitar repetir >60% del pool de la semana previa.
- Permitir excepciones en eventos de temporada.

---

## 4) Publicación y versionado

- Identificador: `rotation_week_id`.
- Campos requeridos:
  - `season_id`
  - `rotation_start_at`
  - `rotation_end_at`
  - `character_ids[]`
- Mantener historial de al menos 12 semanas para análisis.

---

## 5) Telemetría mínima

- `pick_rate_by_character`
- `winrate_by_character`
- `free_to_permanent_conversion_rate`
- `star_spend_after_rotation_exposure`

---

## 6) Reglas de seguridad

- Cambio de rotación no debe borrar presets existentes.
- Cambio de rotación no debe alterar inventario permanente.
- Si falla publicación, fallback a rotación previa y generar alerta.
