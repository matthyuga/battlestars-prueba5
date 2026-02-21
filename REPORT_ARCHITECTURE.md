Auditoría de arquitectura — Proyecto Ren'Py (battlestars-prueba5)
Alcance: análisis estático del repositorio completo, sin cambios de lógica ni refactors.

1) Mapa de módulos/scripts (.rpy) y rol
Núcleo global / estado / utilidades
game/00_GLOBALS_SYSTEMV3.rpy: bootstrap global del combate; formateo, utilidades, identidades, defaults de runtime y compatibilidad legacy (incluye ReflectedDamage legacy).

game/00_GLOBALS_TURNSTATEV2.rpy: estado de turno/fase (battle_actor, battle_phase, battle_turn_no) con normalización y helpers para avanzar fase.

game/01_GLOBALS_COREV4.rpy: estado base de combate y sistema moderno de cargas para focus/boost ofensivo-defensivo.

game/00_GLOBALS_OPERATION_SYSTEMV2.rpy: bitácora de “operación defensiva” (buffer temporal de líneas + dump a battle log).

game/00_GLOBALS_OPERATION_COLORSV2.rpy: paleta de colores y sincronización de claves para formato de operación.

game/00_LOG_HELPERSV2.rpy: helpers compactos de logging (blog, blog_result, fmt) para unificar estilo de mensajes.

game/00_battle_styleV2.rpy: formato visual de logs/operaciones + wrappers seguros para compatibilidad (safe_battle_log_add, helpers de operación y focus).

game/04_UTIL_COSTSV2.rpy: helper utilitario de costo final (get_final_rei_cost) para evitar repetir cálculo manual.

Datos y modelos
game/00_definitions_charactersV2.rpy: dataset de personajes y getters (get_character, stats, HP, nombre, fondo).

game/02_TECHNIQUES_DATASETV2.rpy: catálogo de técnicas de combate y validación/reset de uso por tipo.

game/03_TECH_STATS_DATASETV2.rpy: costos/valor de técnicas, affordability y consumo de recursos en store.

game/01_ACTION_MODELV2.rpy: modelo de acción (clase/objeto) para encapsular cálculo de stats/multiplicadores.

Inicio de combate / ciclo general
game/04_battle_core_initV3.rpy: índice de integración de módulos de batalla (ensamble general del sistema).

game/04b_battle_startV2.rpy: punto de entrada del juego y setup completo del combate (enemigo, HP, recursos, IA, HUD, primer turno).

game/04e_battle_end_result.rpy: resolución de fin de combate (victoria/derrota/empate + mensaje final).

game/99_autocleaner.rpy: limpieza automática del entorno al entrar al menú principal.

game/99_DEBUG_BATTLE_IDENTITIESV4.rpy: panel/interruptor de depuración de identidades de combate.

Selector de técnicas (UI + simulación)
game/04F_SELECTOR_DATAV3.rpy: estado interno del selector y funciones de reset total/parcial.

game/04F_SELECTOR_FUNCTIONSV2.rpy: cálculo de costos simulados, validaciones de selección y reconstrucción de simulación.

game/04F_SELECTOR_MENUV2.rpy: lógica del menú de técnicas (preview, chequeos, agregado seguro a cola).

game/04F_SELECTOR_QUEUV2.rpy: cola de técnicas seleccionadas y toggles operativos del selector.

Sistema de costos Reiatsu/Energía
game/04X_REIATSU_ENERGY_SYSTEMV2.rpy: SSOT de costo dinámico (reiatsu_energy_dynamic_cost), valor base/final y consumo estandarizado.

game/02_FOCUS_BOOST_TURN_HOOKS.rpy: hooks de fin de turno para decaimiento/aplicación de cargas focus/boost y compat legacy.

Turno ofensivo/defensivo del jugador
game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy: fábrica/objeto de acciones ofensivas y texto/log asociado a daño/focus.

game/4/j/04C_OFFENSIVE_FORMULAV3.rpy: helpers de fórmula ofensiva y normalización numérica para resumen de daño.

game/4/j/04C_OFFENSIVE_COREV3.rpy: flujo principal del turno ofensivo de jugador (selector, ejecución, reflect, KO, salto de turno).

game/4/j/04D_DEFENSIVE_ACTIONS.rpy: ejecución de técnicas defensivas (bloqueo, reducción, reflect, potenciar, costos).

game/4/j/04D_DEFENSIVE_CORE.rpy: orquestación del turno defensivo (setup, UI, llamado a módulos acción/operación/resolve).

game/4/j/04D_DEFENSIVE_OPERATION.rpy: matemática defensiva + resumen de operación y cálculo de HP final esperado.

game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy: aplicación final de daño/reflect, limpieza de estado y enrutado al siguiente turno o fin.

IA y turnos enemigos
game/4/04D_AI_BASEV2.rpy: clases base de IA por enemigo y estructura de plan/turno.

game/4/04D_AI_PLANS_COREV1.rpy: helpers comunes para construir planes (peso, filtros, selección).

game/4/04D_AI_PLANS_OFFENSEV1a.rpy: generación del plan ofensivo IA (incluye modos de finisher).

game/4/04D_AI_PLANS_DEFENSEV1a.rpy: generación del plan defensivo/reactivo IA (incluye modos de defensa).

game/4/04D_AI_EXECUTIONV5.rpy: ejecución real de acciones IA (costos, focus, dados, daño directo/noatk, reflect).

game/4/04D_AI_REACTIVE_DEFENSE_COREV1.rpy: núcleo para armar plan reactivo de defensa IA.

game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy: motor para ejecutar plan reactivo defensivo IA.

game/4/04D_AI_REACTIVE_DEFENSEV2.rpy: orquestador/wrapper de defensa reactiva.

game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy: flujo de turno ofensivo enemigo completo (plan, ejecución, maniobra del jugador, transición).

game/4/04E_BATTLE_TURN_ENEMY_DEFENSIVV3.rpy: wrapper de compatibilidad para defensa enemiga legacy.

Reflect
game/4/04Z_REFLECT_MANAGERV3.rpy: ReflectManager centralizado por target_id con source_id (add/get/consume/clear).

game/4/04Z_REFLECT_HELPERS.rpy: fachada helper (reflect_queue, reflect_consume_for, etc.) sobre manager central.

HUD, overlays, FX, ambiente
game/03_VISUAL_SYSTEM_BASICV2.rpy: battle log principal, popup/log APIs y utilidades visuales básicas.

game/05_BATTLE_OVERLAY_SUMMARY.rpy: resumen de turno en overlay (save/clear de resumen).

game/06A_BATTLE_HUD_SYSTEMV2.rpy: HUD de HP/recursos, simulación visual y sincronización de barras.

game/06C_BATTLE_OVERLAY_MANAGER.rpy: registro/gestión de overlays activos de batalla.

game/06D_BATTLE_POPUP_TURN.RPY: popup de turno (API de mensaje contextual).

game/06F_BATTLE_TURN_CHANGE.RPY: helper de cambio de turno y mensajes asociados.

game/06G_BATTLE_MANEUVER_SCREENSV2.rpy: pantalla de maniobras defensivas/ofensivas y control de selección.

game/00B_BATTLE_TURN_SUMMARY_OVERLAY.rpy: capa placeholder para resumen visual de turno.

game/09_BATTLE_DAMAGE_OVERLAY.rpy: overlay de daño para enfatizar estado crítico de HP.

game/07_BATTLE_BACKGROUNDS.rpy: fondos de batalla y flashes de overlay de entorno.

game/08_BATTLE_ATMOSPHERE.rpy: atmósfera dinámica en función del estado de batalla/HP.

game/06A_FX_ACTIONS_ACTIVE.rpy: API de FX activables por acción (slash/pulse/focus/barrier/reflect).

game/06B1_BATTLE_FX_CORE.rpy: núcleo de efectos visuales (shake, glow, impact, etc.).

game/06B2_BATTLE_FX_SCREENS.rpy: screens Ren’Py para FX visuales.

game/06B3_BATTLE_FX_TRANSFORMS.rpy: transforms/ATL para animación de FX.

game/00_DICE_ICONS.rpy: assets y utilidades visuales mínimas de iconos de dados en log/UI.

game/04a_battle_fallbacks_fxV2.rpy: fallbacks no-op para FX/log/HUD si faltan funciones por orden de carga.

Interfaz general Ren’Py
game/screens.rpy: screens base del proyecto (UI general + componentes reutilizados).

game/gui.rpy: configuración de estilos GUI globales de Ren’Py.

game/options.rpy: opciones/config global de proyecto Ren’Py.

game/04A_BATTLE_CHARACTER_SELECTV3.rpy: selección de oponente y entrada al loop de batalla, con HUD de dificultad IA.

game/4/04A_AI_DIFFICULTY_HUD_CORE_BASEV2.rpy: configuración persistente/base del HUD de dificultad IA.

game/4/04A_AI_DIFFICULTY_HUD_CORE_DEFENSEV2.rpy: configuración persistente del modo defensivo IA.

game/4/04A_AI_DIFFICULTY_HUD_SCREENV2.rpy: screen del HUD para editar dificultad IA en runtime.

2) Diagrama textual del flujo de combate
start
  -> battle_select_opponent (elige enemy_id)
  -> battle_start
      -> reset estado temporal/log/operation/focus/reflect
      -> carga character sheets (player/enemy) + HP + recursos
      -> set identities (current_actor_id/current_enemy_id)
      -> init enemy_ai
      -> decide battle_turn_owner aleatorio

Si inicia player:
  battle_offensive_turn
    -> preparar snapshot recursos turno + limpiar colas
    -> mostrar selector y confirmar cola de acciones
    -> offensive_process_actions(selected)
         -> consume_resources
         -> calcula daño por acción
         -> aplica focus ofensivo cuando corresponde
         -> puede setear enemy_skip_attack (Ataque Negador)
    -> resolver reflect pendiente contra enemy target (consume)
    -> aplicar daño a enemy_hp
    -> sync HUD/log/FX
    -> si enemy_hp <= 0 -> battle_end
    -> else -> jump battle_enemy_turn

Si inicia enemy (o después del turno player):
  battle_enemy_turn
    -> ai_plan_offensive(enemy_ai)
    -> while plan: ai_execute_offensive_action(enemy_ai)
         -> consume_resources(enemy)
         -> daño defendible a incoming_damage
         -> daño directo pendiente (direct_attack)
         -> skip del jugador (noatk_attack)
         -> puede encolar reflect según técnica
    -> consume reflect pendiente contra player target (si aplica)
    -> incoming_damage final
    -> jugador elige maniobra (atk_from_def / def_from_atk / normal)

Ramas desde maniobra:
  atk_from_def:
    -> jugador recibe daño directo
    -> gana acción ofensiva extra
    -> jump battle_offensive_turn

  def_from_atk:
    -> activa defense_for_attack_active
    -> jump battle_defensive_turn

  normal:
    -> call battle_defensive_turn

battle_defensive_turn
  -> setup estado defensivo + selector
  -> defensive_process_actions(selected, base_damage)
       -> calcula bloques/reducción/reflect y consume recursos
  -> defensive_operation(...)
       -> calcula received_damage + hp_after + logs operación
  -> defensive_resolve(received_damage, hp_after, reflected)
       -> aplica daño real a player_hp
       -> aplica reflect (queue al target enemigo)
       -> limpia estados temporales y debuffs
       -> decide siguiente turno (enemy/player)
       -> KO player? -> battle_end

battle_end
  -> resultado final + popup/log
  -> retorno a flujo post-combate
3) Fuentes de verdad actuales (SSOT real vs SSOT aspirado)
3.1 HP
Variables activas en runtime: player_hp, enemy_hp (store + script vars), y espejo HUD battle_hp_player, battle_hp_enemy, con máximos battle_hp_player_max, battle_hp_enemy_max.

Escritura principal:

Inicialización en battle_start desde dataset de personajes.

Daño jugador en battle_enemy_turn y defensive_resolve.

Daño enemigo en battle_offensive_turn.

Lectura principal: KO checks (battle_offensive_turn, battle_end), HUD (battle_update_hp_bars, screen HUD), overlay de daño/atmósfera.

Observación: hay duplicación explícita entre HP “lógico” (player_hp/enemy_hp) y HP “visual” (battle_hp_*).

3.2 Recursos (Reiatsu / Energía)
Variables activas: player_reiatsu, player_energy, enemy_reiatsu, enemy_energy.

SSOT funcional de costo: reiatsu_energy_dynamic_cost() + final_value_factory() en 04X_REIATSU_ENERGY_SYSTEMV2.rpy.

Escritura de consumo: consume_resources (y caminos que terminan en ese helper); IA también consume por helper común.

Lectura: selector (simulación de costo), ejecución de acciones (player/IA), HUD y validaciones can_afford.

Observación: coexistencia de simulaciones (simulated_reiatsu/energy, enemy_simulated_*) fuera del SSOT de recursos reales.

3.3 Identidad actor/enemy
Variables activas: current_actor_id, current_enemy_id, tabla BATTLE_IDENTITIES.

Setter central: set_battle_identity(actor, enemy).

Lectura principal: reflect (target/source), debug panel de identidades y flujos de turno.

Observación: también aparecen rutas alternativas de identidad (player_id, current_player_id, BATTLE_PLAYER_ID) en turnos enemigos, señal de compat legacy.

3.4 battle_state / turn state
Sistema A (turnstate): battle_actor, battle_phase, battle_turn_no + battle_next_phase.

Sistema B (owner): battle_turn_owner + helper battle_turn_change("player|enemy").

Sistema C (flags runtime): defense_for_attack_active, extra_offensive_actions, extra_defensive_actions, turn_confirmed, etc.

Observación: hay múltiples “máquinas de estado” parciales en paralelo; no existe un único objeto de estado transaccional.

3.5 Logs y operación
Log principal: battle_log_add, battle_log_clear, battle_log_phase (visual/basic + wrappers de estilo).

Operation log secundario: buffer operation_add/operation_clear/operation_dump_to_battle_log.

Resumen de turno: summary_lines, battle_save_turn_summary.

Observación: conviven tres canales de logging (battle log, operation log, summary overlay), con acoplamientos cruzados.

4) Dependencias clave entre scripts
4.1 Dependencias estructurales (alto nivel)
04b_battle_startV2.rpy depende de:

dataset personaje (00_definitions_charactersV2.rpy),

HUD/atmósfera/fondo (06A_BATTLE_HUD_SYSTEMV2.rpy, 08_BATTLE_ATMOSPHERE.rpy, 07_BATTLE_BACKGROUNDS.rpy),

identidades/globales (00_GLOBALS_SYSTEMV3.rpy),

IA base (4/04D_AI_BASEV2.rpy),

log visual (03_VISUAL_SYSTEM_BASICV2.rpy).

4/j/04C_OFFENSIVE_COREV3.rpy depende de:

selector (04F_SELECTOR_*),

costos/consumo (04X_REIATSU_ENERGY_SYSTEMV2.rpy, 03_TECH_STATS_DATASETV2.rpy),

reflect (4/04Z_REFLECT_*),

turn routing (06F_BATTLE_TURN_CHANGE.RPY),

HUD/log/FX (06A_*, 03_VISUAL_*, 06B*).

4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy depende de:

IA plan + ejecución (4/04D_AI_PLANS_*, 4/04D_AI_EXECUTIONV5.rpy),

reflect helpers/manager,

pantalla de maniobra (06G_*),

defensivo de jugador (4/j/04D_*).

4/j/04D_DEFENSIVE_CORE.rpy depende de:

acciones (04D_DEFENSIVE_ACTIONS.rpy),

operación (04D_DEFENSIVE_OPERATION.rpy),

resolución (04D_DEFENSIVE_RESOLVEV3.rpy),

costos/focus hooks/log/HUD.

4.2 Dependencias por llamada crítica
battle_start -> jump battle_offensive_turn | battle_enemy_turn.

battle_enemy_turn -> call battle_defensive_turn (o salto directo ofensivo según maniobra).

battle_defensive_turn -> call defensive_process_actions -> call defensive_operation -> call defensive_resolve.

ai_execute_offensive_action y offensive_process_actions convergen en consumo de recursos + escritura de daño entrante/saliente.

defensive_resolve y ai_execute_* convergen en reflect queue/consume.

5) Riesgos actuales detectados
5.1 Duplicación y dispersión de estado
Doble representación de HP (player_hp/enemy_hp vs battle_hp_player/battle_hp_enemy) con sincronización manual frecuente.

Variables de identidad con varias rutas de fallback (current_*_id, player_id, BATTLE_PLAYER_ID) en lugar de una interfaz única.

Simulación de recursos en variables separadas y con nombres inconsistentes (simulated_enemy_* vs enemy_simulated_*).

5.2 Orden de init y compat legacy
Existen múltiples init con prioridades negativas y funciones repetidas en distintos módulos globales (ej. helpers de operation_*, battle_fmt_num).

Se observan wrappers/fallbacks para cubrir orden de carga, señal de dependencia implícita fuerte entre scripts.

5.3 Acoplamiento alto UI ↔ lógica de dominio
Lógica de negocio (consumo, reflect, KO, cambios de turno) se ejecuta mezclada con show/hide screen, pause, FX y logs.

Esto dificulta testeo aislado y rastreo de regresiones lógicas.

5.4 Side effects y flujo no transaccional
Varias funciones escriben directamente en renpy.store en múltiples puntos del mismo turno.

Cambios de turno y resets ocurren por jump/call + flags mutables distribuidas, sin “commit” de estado por fase.

5.5 Manejo de errores silencioso
Uso extendido de try/except: pass (en turnos, logs, reflect, FX), lo que puede ocultar errores reales y dejar estado parcial.

6) Señales de deuda técnica
Repetición de bloques similares de reflect consume/desvanecimiento tanto en turno jugador como IA.

Repetición de lógica de logging seguro con getattr/globals en varios archivos.

Responsabilidades mezcladas en archivos “core” de turno (orquestación + cálculo + UX + logging + routing).

Coexistencia de sistemas nuevo/legacy de focus/boost/costos (cargas modernas + banderas legacy como focus_cost_active, reset_concentrar).

Dependencias cruzadas por nombre global en lugar de API de dominio explícita.

7) Candidatos de reestructuración (sin tocar código todavía)
7.1 Responsabilidades a separar
State module: consolidar estado de combate, turno y flags en un único namespace/objeto (battle_state).

Calculations module: mover cálculo puro de daño, bloqueos, reflect y costos a helpers side-effect-free.

Turn engine module: mantener únicamente orquestación de fases (start_turn, resolve_actions, end_turn).

UI adapter module: encapsular show/hide screen, popups, FX y sincronización HUD fuera del dominio.

Logging module: unificar battle_log, operation_log, summary bajo una interfaz coherente (eventos + render).

7.2 Variables a consolidar (SSOT)
HP: dejar player_hp/enemy_hp como únicos valores lógicos; battle_hp_* solo derivados visuales read-only.

Turn state: unificar battle_turn_owner, battle_actor/battle_phase y flags de transición en una sola estructura.

Identity: consolidar todas las lecturas en get_battle_identity("actor|enemy") y eliminar aliases legacy gradualmente.

Resources: mantener solo player_*/enemy_* reales + un subestado de simulación con naming uniforme.

Reflect: forzar paso por helpers de ReflectManager, evitar buffers legacy paralelos salvo compat encapsulada.

7.3 Helpers comunes candidatos
sync_hp_ui_from_state() y sync_resource_ui_from_state().

consume_reflect_or_drop(target_id, reason) para unificar ramas duplicadas.

safe_log(level, msg, channel="battle") para reducir wrappers repetidos.

apply_turn_transition(next_actor, next_phase, reason) para centralizar cambios de turno.

compute_offense_result(actions, actor_ctx) y compute_defense_result(actions, incoming, actor_ctx) como funciones puras.

8) Rutas de reestructuración propuestas
Opción A — Mínima (reordenar/renombrar + compat)
Objetivo: mejorar legibilidad y trazabilidad sin cambiar diseño base.

Pasos sugeridos

Documentar contrato de cada script (inputs/outputs/store vars).

Normalizar nombres de variables de simulación y aliases en comentarios/API wrappers.

Centralizar acceso a logs y reflect vía helpers ya existentes (sin eliminar legacy).

Ordenar secuencia de init y registrar explícitamente precedencias.

Pros: bajo riesgo, rápida adopción, casi cero impacto en saves.
Contras: no elimina deuda estructural de fondo.
Riesgos: seguir acumulando acoplamiento si se agregan features nuevas.
Esfuerzo: bajo.

Opción B — Media (consolidar state + helpers)
Objetivo: reducir duplicación de estado y side effects dispersos.

Pasos sugeridos

Introducir battle_state como fachada de acceso (sin romper variables actuales, con espejo temporal).

Extraer helpers comunes de reflect/log/turn transition/costos a módulos únicos.

Migrar turnos player/IA para usar helpers comunes (manteniendo labels y archivos).

Marcar variables legacy como deprecated con capa de compatibilidad.

Pros: mejora mantenibilidad y testabilidad sin reescritura total.
Contras: transición gradual requiere disciplina en nuevas features.
Riesgos: desync temporal entre facade state y globals legacy durante migración.
Esfuerzo: medio.

Opción C — Grande (arquitectura por dominios)
Objetivo: rediseñar por capas de dominio con separación fuerte lógica/UI.

Pasos sugeridos

Definir dominios: state, engine, combat_rules, ai, ui_adapter, logging.

Convertir lógica de daño/defensa/reflect/costos en funciones puras testables.

Reescribir labels de turno como orquestadores del engine (event-driven).

Dejar UI como consumidor de eventos de estado (sin mutar dominio directo).

Plan de migración de saves/compat para variables legacy.

Pros: arquitectura limpia, escalable, menor fragilidad a futuro.
Contras: inversión alta y necesidad de estrategia de migración robusta.
Riesgos: regresiones amplias si no se hace por fases con test harness.
Esfuerzo: alto.

9) Problemas críticos observados (sin corregir)
Múltiples sistemas de estado de turno activos en paralelo (battle_turn_owner vs battle_actor/battle_phase + flags de maniobra), con riesgo de inconsistencias de routing.

Ejemplo: battle_start decide por battle_turn_owner, mientras otras transiciones usan battle_turn_change("player|enemy") y también existe battle_next_phase() como camino alterno.

Doble/triple canal de estado y logging (battle log / operation log / summary) sin orquestación única de eventos.

Ejemplo: defensive_operation() escribe con operation_add(...) y luego se vuelca a battle_log_add(...), mientras summary_lines se guarda aparte para overlays.

Persistencia de compat legacy mezclada con sistema nuevo (focus/boost/costos), elevando complejidad cognitiva y probabilidad de side effects.

Ejemplo: coexisten focus_off_charges/boost_def_charges (nuevo) con focus_cost_active y reset_concentrar(...) (legacy compat).

Dependencia fuerte en try/except: pass en nodos críticos de turno, que puede ocultar errores lógicos y dejar combate en estado parcial.

Ejemplo: bloques de consumo/aplicación de reflect y logging seguro en turnos ofensivos de jugador/IA silencian errores sin fallback estructurado.

Ejemplos concretos (archivo + función/variable)
game/04b_battle_startV2.rpy (label battle_start): inicializa y sincroniza player_hp/enemy_hp y en paralelo battle_hp_player/battle_hp_enemy, lo que exige sync manual continuo.

game/4/j/04C_OFFENSIVE_COREV3.rpy (label battle_offensive_turn): mezcla routing de turno, resolución de reflect, consumo de recursos, UI (show_screen) y KO checks en el mismo bloque.

game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy (label battle_enemy_turn): usa múltiples fallbacks de identidad (current_player_id, player_id, BATTLE_PLAYER_ID, BATTLE_IDENTITIES).

game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy (label defensive_resolve): aplica daño real, encola reflect y además ejecuta limpieza global de estado y decisión de routing del próximo turno.

game/04X_REIATSU_ENERGY_SYSTEMV2.rpy (reiatsu_energy_dynamic_cost): SSOT de costos, pero con compat legacy (focus_cost_active) que puede interferir con lectura de foco actual.

10) Conclusión
El proyecto ya tiene piezas valiosas (datasets, manager de reflect, helpers de costo dinámico, módulos separados por intención), pero hoy la arquitectura opera como malla de globals + compat layers más que como un engine con límites de dominio claros. El siguiente paso recomendado es una ruta B (media) por fases, para obtener SSOT real y helpers comunes antes de una re-arquitectura total.