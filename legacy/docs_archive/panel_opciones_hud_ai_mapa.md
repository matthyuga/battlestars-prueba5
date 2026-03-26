# Mapa de scripts del panel de opciones IA

Este mapa identifica en qué archivos está cada opción del panel mostrado en HUD.

## 1) Estructura visual del panel (botones/layout)
- `game/4/04A_AI_DIFFICULTY_HUD_SCREENV2.rpy`
  - Screen principal: `screen ai_difficulty_hud()`.
  - Aquí están los `textbutton` del panel y el orden visual (Básico, Guardar, Perfil IA, Target, Ofensiva/Defensa por unidad, Concat, Focus, resets, etc.).

## 2) Texto/estado de opciones base
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_BASEV2.rpy`
  - `ai_level_text()` / `_label_for_level()` → `🧠 Básico / Intermedio / Avanzado`.
  - `ai_save_text()` → `💾 Guardar: ON/OFF`.
  - `ai_finisher_mode_text()` / `_label_for_test_mode()` → `🎯 Forzar: Stronger` y otros modos ofensivos.
  - `ai_focus_text()` → `🧿 Focus IA: ON/OFF`.

## 3) Perfil por unidad (target y toggles por unidad)
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_UNIT_PROFILEV1.rpy`
  - `ai_ui_enemy_slot_text()` → `👥 Perfil IA: ...`.
  - `ai_ui_target_rule_text()` → `🎯 Target: Forzar P1/P2` o `Auto`.
  - `ai_ui_offense_mode_text()` → `⚔️ Ofensiva (unidad): ...`.
  - `ai_ui_defense_mode_text()` → `🛡️ Defensa (unidad): ...`.
  - `ai_ui_concat_rule_text()` → `🔗 Concat (unidad): ON/OFF/Heredar`.
  - `ai_ui_focus_rule_text()` → `🧿 Focus (unidad): ON/OFF/Heredar`.

## 4) Defensa global (modo/concat/reset)
- `game/4/04A_AI_DIFFICULTY_HUD_CORE_DEFENSEV2.rpy`
  - `ai_defense_mode_text()` → `🛡️ Defensa: Normal/Stats` y `🛡️ Forzar: Extra/Reduct/Reflect`.
  - `ai_defense_concat_text()` → `🔗 Concat: ON/OFF`.
  - `ai_reset_defense_stats()` → lógica de reset stats defensivos.

## Nota rápida
Si quieres rediseñar el panel "a algo más visual", empieza por `04A_AI_DIFFICULTY_HUD_SCREENV2.rpy` (layout/estilos) y ajusta los textos/estados en los `CORE_*` según sea necesario.
