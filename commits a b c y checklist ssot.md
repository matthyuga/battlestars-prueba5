Pack de scripts por commit
Commit A — Contrato único de daño directo (estado SSOT)
Scripts
game/01B_BATTLE_STATE_FACADE.rpy

Crea/normaliza battle_state["direct_pending"] con llaves player/enemy.

Agrega helpers SSOT: bs_get_direct_pending, bs_set_direct_pending, bs_add_direct_pending, bs_consume_direct_pending.

Exporta estos helpers al store (S.bs_*).

game/4/04D_AI_EXECUTIONV5.rpy

Productor IA (direct_attack) migra a bs_add_direct_pending("player", dmg) con fallback legacy.

game/4/j/04C_OFFENSIVE_RESOLVEV1.rpy

Productor jugador directo migra a bs_set_direct_pending("enemy", direct_damage) con fallback legacy (_last_player_direct_damage).

Commit B — Consumidores migrados al contrato facade
Scripts
game/4/j/04D_DEFENSIVE_OPERATION.rpy

Lee directo pendiente con bs_get_direct_pending("player") y fallback legacy; lo refleja en operación/HP total esperado.

game/4/j/04D_DEFENSIVE_RESOLVEV3.rpy

Consume directo pendiente con bs_consume_direct_pending("player") (o legacy si no existe helper).

game/4/04D_AI_REACTIVE_DEFENSE_ENGINEV2.rpy

Lectura de directo pendiente jugador→enemigo con facade/fallback para operación de HP total esperado.

Limpieza/consumo del pendiente vía bs_consume_direct_pending("enemy") (fallback legacy).

Commit C — Resumen ofensivo IA prioriza facade
Script
game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy

En el mensaje final, dmg_directo ahora prioriza bs_get_direct_pending("player"); si no existe helper, cae a incoming_direct_damage y luego enemy_direct_pending_damage.

Espeja a S.incoming_direct_damage para compatibilidad con piezas legacy de formateo/consumo visual/logs.

Checklist manual (6 puntos) — “split + logs 100% consistente”
Directo IA visible y consistente

Forzá direct_attack IA exitoso.

Verificá que aparezca “Daño total: X defendibles + Y directos = Z” en ofensiva IA y que Y coincida con lo pendiente en defensa.

Consumo único (sin doble aplicación)

Tras resolver defensa del jugador, el directo pendiente debe quedar en 0 y no reaplicarse en el siguiente turno.

Canal SSOT prioritario activo

En escenarios donde facade está cargada, el cálculo/log debe tomar bs_get_direct_pending (no depender de variable legacy).

Fallback legacy funcionando

Simulá ausencia de helper (build viejo o carga parcial): el flujo debe seguir por incoming_direct_damage -> enemy_direct_pending_damage sin romper logs.

Player directo consistente en motor reactivo IA

Ejecutá directo del jugador y confirmá que en defensa reactiva IA aparezca “Daño directo pendiente / HP total” y luego se consuma/limpie correctamente.

No regresión de turnos/reflect

Probá noatk_attack, reflect y maniobras para confirmar que no hay cambios de routing no deseados por la migración de canales directos.