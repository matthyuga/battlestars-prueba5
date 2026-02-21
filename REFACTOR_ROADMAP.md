diff --git a/docs/REFACTOR_ROADMAP.md b/docs/REFACTOR_ROADMAP.md
new file mode 100644
index 0000000000000000000000000000000000000000..a4727f0c4fd80582f8a87cd5acdc7444e2232951
--- /dev/null
+++ b/docs/REFACTOR_ROADMAP.md
@@ -0,0 +1,323 @@
+# REFACTOR ROADMAP — Fase B1-A (Fachada mínima)
+
+## Contexto
+Este documento define una **fase preparatoria B1-A** para reestructuración con riesgo mínimo.
+
+- Base utilizada: `REPORT_ARCHITECTURE.md`.
+- Nota: `MODULE_CONTRACTS.md` no está presente en este repositorio al momento de redactar este roadmap.
+- Alcance B1-A: **solo especificación y plan de adopción** de una fachada `battle_state facade`.
+- Fuera de alcance B1-A: implementación en `.rpy` y cambios de lógica.
+
+---
+
+## 1) Objetivo B1-A
+
+Introducir una capa de acceso estable llamada **battle_state facade** (helpers/wrappers), para:
+
+1. Reducir lecturas/escrituras directas repetidas sobre variables globales (`player_hp`, `enemy_hp`, `battle_hp_*`, recursos, identidad, turno).
+2. Estandarizar puntos de acceso sin romper compatibilidad con código legacy.
+3. Preparar la transición a B1 real (adopción progresiva en labels) sin migrar lógica todavía.
+
+### Resultado esperado de B1-A
+- Contrato de helpers documentado.
+- Mapa de variables legacy impactadas por helper.
+- Orden de adopción por archivos/labels críticos.
+- Estrategia de reversión inmediata (rollback por commit único).
+
+---
+
+## 2) Especificación de helpers/wrappers (sin implementación)
+
+## 2.1 HP
+
+### `bs_get_hp(actor)`
+**Contrato propuesto**
+- Entrada: `actor in {"player", "enemy"}`.
+- Salida: HP actual entero (`player_hp` o `enemy_hp`).
+
+**Variables legacy (lee/escribe)**
+- Lee: `player_hp`, `enemy_hp`.
+- Escribe: ninguna.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/4/j/04C_OFFENSIVE_COREV3.rpy` (`label battle_offensive_turn`) para KO/checks y cálculos de daño al enemigo.
+- `game/4/j/04D_DEFENSIVE_OPERATION.rpy` (`label defensive_operation`) para `hp_before`.
+- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy` (`label defensive_resolve`) para decisiones KO jugador.
+- `game/04e_battle_end_result.rpy` (`label battle_end`) para resultado final.
+
+---
+
+### `bs_set_hp(actor, value)`
+**Contrato propuesto**
+- Entrada: `actor` + `value` entero (clamp en implementación futura).
+- Efecto: persistir HP lógico.
+
+**Variables legacy (lee/escribe)**
+- Lee: opcional `battle_hp_player_max`, `battle_hp_enemy_max` (si se aplica clamp).
+- Escribe: `player_hp` o `enemy_hp`.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/4/j/04C_OFFENSIVE_COREV3.rpy`: aplicación de daño a enemigo.
+- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`: aplicación de daño al jugador en rama `atk_from_def`.
+- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`: aplicación final de daño y KO.
+
+---
+
+### `bs_get_hp_max(actor)`
+**Contrato propuesto**
+- Entrada: `actor in {"player", "enemy"}`.
+- Salida: máximo HP en runtime.
+
+**Variables legacy (lee/escribe)**
+- Lee: `battle_hp_player_max`, `battle_hp_enemy_max`.
+- Escribe: ninguna.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/06A_BATTLE_HUD_SYSTEMV2.rpy`: cálculo de barra HP y porcentajes.
+- `game/09_BATTLE_DAMAGE_OVERLAY.rpy` y `game/08_BATTLE_ATMOSPHERE.rpy` cuando consultan estado por ratio HP.
+
+---
+
+### `bs_sync_hp_ui()`
+**Contrato propuesto**
+- Sin parámetros.
+- Deriva estado visual de HP desde estado lógico:
+  - `battle_hp_player <- player_hp`
+  - `battle_hp_enemy <- enemy_hp`
+- Mantiene llamada de actualización HUD centralizada (si aplica en B1 real).
+
+**Variables legacy (lee/escribe)**
+- Lee: `player_hp`, `enemy_hp`.
+- Escribe: `battle_hp_player`, `battle_hp_enemy`.
+- Opcional (no obligatorio): invocar `battle_update_hp_bars(player_hp, enemy_hp)`.
+
+**Primeros puntos de adopción (B1 real)**
+- Reemplazar secuencias repetidas `set hp + battle_update_hp_bars(...)` en:
+  - `game/4/j/04C_OFFENSIVE_COREV3.rpy`
+  - `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
+  - `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
+
+---
+
+## 2.2 Recursos
+
+### `bs_get_resources(actor)`
+**Contrato propuesto**
+- Entrada: `actor in {"player", "enemy"}`.
+- Salida: tupla/objeto `{reiatsu, energy}`.
+
+**Variables legacy (lee/escribe)**
+- Lee: `player_reiatsu`, `player_energy`, `enemy_reiatsu`, `enemy_energy`.
+- Escribe: ninguna.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/04F_SELECTOR_FUNCTIONSV2.rpy` (simulación base del selector).
+- `game/03_TECH_STATS_DATASETV2.rpy` (`can_afford`, validaciones).
+- `game/4/04D_AI_EXECUTIONV5.rpy` (`ai_can_pay`).
+
+---
+
+### `bs_set_resources(actor, reiatsu, energy)`
+**Contrato propuesto**
+- Entrada: actor + valores numéricos.
+- Efecto: persistencia central de recursos reales.
+
+**Variables legacy (lee/escribe)**
+- Lee: valores de entrada, opcional clamp >= 0.
+- Escribe: `player_reiatsu`, `player_energy` o `enemy_reiatsu`, `enemy_energy`.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/03_TECH_STATS_DATASETV2.rpy` (`pay_costs`).
+- `game/04X_REIATSU_ENERGY_SYSTEMV2.rpy` (`consume_resources`).
+- `game/4/04D_AI_EXECUTIONV5.rpy` (consumo IA indirecto vía helper común).
+
+---
+
+## 2.3 Identidad
+
+### `bs_get_identity(role)`
+**Contrato propuesto**
+- Entrada: `role in {"actor", "enemy"}`.
+- Salida: `current_actor_id` o `current_enemy_id`.
+
+**Variables legacy (lee/escribe)**
+- Lee: `current_actor_id`, `current_enemy_id`.
+- Escribe: ninguna.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/4/j/04C_OFFENSIVE_COREV3.rpy` (reflect target lookup).
+- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy` (fallback de target id).
+- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy` (source/target en reflect).
+
+---
+
+### `bs_set_identity(actor_id, enemy_id)`
+**Contrato propuesto**
+- Entrada: ids normalizados (o nombres resolubles en implementación B1 real).
+- Efecto: update consistente de identidad de combate activa.
+
+**Variables legacy (lee/escribe)**
+- Lee: opcional `BATTLE_IDENTITIES` (si recibe nombres y no IDs).
+- Escribe: `current_actor_id`, `current_enemy_id`.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/04b_battle_startV2.rpy` (`label battle_start`, momento de seteo inicial).
+- Puntos que hoy reasignan `current_enemy_id` durante turno IA.
+
+---
+
+## 2.4 Turn owner
+
+### `bs_get_turn_owner()`
+**Contrato propuesto**
+- Sin parámetros.
+- Salida: valor de owner actual.
+
+**Variables legacy (lee/escribe)**
+- Lee: `battle_turn_owner` (primario).
+- Opcional compat: lectura derivada de `battle_actor/battle_phase` solo para diagnóstico.
+- Escribe: ninguna.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/04b_battle_startV2.rpy` tras sorteo inicial.
+- `game/06F_BATTLE_TURN_CHANGE.RPY` como punto de consulta estandarizada.
+
+---
+
+### `bs_set_turn_owner(owner)`
+**Contrato propuesto**
+- Entrada: `owner in {"player", "enemy"}`.
+- Efecto: persistencia uniforme de dueño de turno.
+
+**Variables legacy (lee/escribe)**
+- Lee: validación de entrada.
+- Escribe: `battle_turn_owner`.
+- Opcional compat futura (no en B1-A): espejo hacia `battle_actor`.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/04b_battle_startV2.rpy` y `game/06F_BATTLE_TURN_CHANGE.RPY`.
+
+---
+
+## 2.5 Resets temporales
+
+### `bs_reset_turn_temp()`
+**Contrato propuesto**
+- Resetea variables efímeras de turno (no estado persistente de combate completo).
+
+**Variables legacy (lee/escribe)**
+- Escribe candidatos: `incoming_damage`, `incoming_direct_damage`, `turn_confirmed`, `maneuver_selected`, `summary_lines`, `player_action_queue`, flags temporales de reflect consumo (`_reflect_consumed_this_turn`, `_enemy_reflect_consumed_this_turn`).
+- No debe tocar HP máximos, identidades base ni datasets.
+
+**Primeros puntos de adopción (B1 real)**
+- Inicio de `battle_offensive_turn`, `battle_enemy_turn`, `battle_defensive_turn`.
+
+---
+
+### `bs_reset_battle_temp()`
+**Contrato propuesto**
+- Resetea estado temporal de inicio/fin de combate (sin destruir catálogos ni funciones registradas).
+
+**Variables legacy (lee/escribe)**
+- Escribe candidatos: logs temporales, operation buffer, secuencias de técnicas, flags de focus/boost no persistentes de turno, colas selector, overlays de resumen.
+- Incluye sync inicial de simulaciones de recursos con valores reales.
+
+**Primeros puntos de adopción (B1 real)**
+- `game/04b_battle_startV2.rpy` antes de inicialización completa del combate.
+- `game/99_autocleaner.rpy` para saneo pre-menú (si se decide).
+
+---
+
+## 3) Estrategia de adopción “zero-risk” (B1 real)
+
+1. **No cambiar labels ni flujo** en primera pasada.
+2. Introducir wrappers como capa fina sobre variables existentes.
+3. Reemplazar solo lecturas/escrituras repetidas de HP + sync HUD por wrappers (`bs_get_hp`, `bs_set_hp`, `bs_sync_hp_ui`).
+4. Mantener llamadas legacy en paralelo durante transición corta (si hace falta, modo dual).
+5. Migración por commits pequeños y reversibles.
+
+### Criterios de éxito de riesgo cero
+- Sin cambios de comportamiento observable de combate.
+- Sin cambios de nombres globales legacy.
+- Rollback trivial: revertir 1 commit devuelve estado previo.
+
+---
+
+## 4) “No hacer aún” en B1-A (prohibido)
+
+- No mover archivos ni reorganizar carpetas.
+- No renombrar variables globales legacy.
+- No eliminar `battle_hp_*`.
+- No unificar engines de turno (`battle_turn_owner` vs `battle_actor/battle_phase`) todavía.
+- No reescribir lógica de reflect.
+- No cambiar contratos de IA ni del selector.
+- No eliminar compat legacy de focus/boost/costos.
+- No introducir cambios funcionales en `.rpy` dentro de esta fase documental.
+
+---
+
+## 5) Plan sugerido de commits futuros (cuando inicie B1 real)
+
+## B1-A.1 — Scaffold de fachada HP
+**Objetivo**
+- Crear helpers `bs_get_hp`, `bs_set_hp`, `bs_get_hp_max`, `bs_sync_hp_ui`.
+
+**Archivos candidatos**
+- Nuevo módulo utilitario de estado (sin tocar lógica de labels).
+- Referencias iniciales en `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy` (adopción mínima y visible).
+
+---
+
+## B1-A.2 — Adopción HP en turnos críticos
+**Objetivo**
+- Reemplazar set/get repetidos de HP + sync HUD en ofensivo/defensivo.
+
+**Archivos candidatos**
+- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
+- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
+- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
+
+---
+
+## B1-A.3 — Recursos fachada mínima
+**Objetivo**
+- Introducir `bs_get_resources` / `bs_set_resources` y usar en puntos de consumo/lectura más repetidos.
+
+**Archivos candidatos**
+- `game/03_TECH_STATS_DATASETV2.rpy`
+- `game/04X_REIATSU_ENERGY_SYSTEMV2.rpy`
+- `game/4/04D_AI_EXECUTIONV5.rpy`
+
+---
+
+## B1-A.4 — Identidad y owner wrapper
+**Objetivo**
+- Introducir `bs_get_identity`/`bs_set_identity`, `bs_get_turn_owner`/`bs_set_turn_owner` con adopción limitada.
+
+**Archivos candidatos**
+- `game/04b_battle_startV2.rpy`
+- `game/06F_BATTLE_TURN_CHANGE.RPY`
+- `game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy`
+
+---
+
+## B1-A.5 — Resets encapsulados (sin cambio funcional)
+**Objetivo**
+- Encapsular secuencias repetidas de limpieza en `bs_reset_turn_temp` y `bs_reset_battle_temp`.
+
+**Archivos candidatos**
+- `game/04b_battle_startV2.rpy`
+- `game/4/j/04C_OFFENSIVE_COREV3.rpy`
+- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
+- `game/4/j/04D_DEFENSIVE_CORE.rpy`
+
+---
+
+## 6) Métricas de seguimiento sugeridas
+
+- Conteo de lecturas directas de `player_hp/enemy_hp` fuera de fachada.
+- Conteo de escrituras directas de `battle_hp_*` fuera de `bs_sync_hp_ui()`.
+- Conteo de fallbacks de identidad por archivo (reducir progresivamente).
+- Número de bloques duplicados de reset por turno.
+
+Estas métricas permiten medir avance de B1 sin necesidad de cambios arquitectónicos grandes.
