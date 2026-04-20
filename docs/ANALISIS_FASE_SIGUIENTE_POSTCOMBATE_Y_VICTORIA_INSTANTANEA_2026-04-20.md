# Análisis y documentación — siguiente fase (post-combate + victoria instantánea)

Fecha: 2026-04-20
Estado: análisis técnico + plan de refactor (sin implementar cambios funcionales)

---

## 1) Estado actual: escena de post-combate / recompensas (C4)

### 1.1 Punto de entrada y pipeline
- El cierre ocurre en `label battle_end` y ahí se construye el `runtime` para simulación.
- Se ejecuta `sim_run_battle_end_simulation(runtime=runtime)`.
- Luego se persiste (`sim_persist_simulation_artifacts`) y se aplica (`sim_apply_simulation_rewards_to_runtime`).
- Finalmente se muestra la pantalla `sim_battle_end_reward_summary_v1`.

Referencia de flujo: `game/04e_battle_end_result.rpy`.

### 1.2 Qué muestra hoy la pantalla C4
- Encabezado con: `sim_id`, `mode`, `winner`.
- Bloque agregado de aplicación: `ok`, `count`, `EXP`, `Oro`.
- Auditoría: `warnings/errors`.
- Lista de `results[]`, actor por actor (incluye también rivales no elegibles), con `outcome`, `eligible`, `EXP`, `Oro`.

Esto explica por qué visualmente aparece el enemigo con `EXP +0 | Oro +0`: es una fila de resultado del contrato, no un premio real aplicado.

### 1.3 Datos disponibles para explicar rendimiento
El resultado por actor ya trae suficiente telemetría para mostrar “por qué gané X recompensa”:
- `base` (exp/oro base)
- `multipliers` (risk, result, performance, antiabuso, multi_factor, hp_reward_multiplier, reward_condition_* )
- `delta_register`, `stars_total`, `outcome`
- `final` (exp_gain, oro_gain, exp_after, oro_after)

Fuente: `compute_actor_reward` en `game/10C_PROGRESSION_SIM_CONTRACT_V1.rpy`.

---

## 2) Hallazgos para rediseño de C4 (enfoque UX/producto)

### 2.1 Problema de UX reportado
- El usuario final quiere ver “mi recompensa” de forma directa.
- Ver al enemigo con `+0` agrega ruido y no aporta decisión.

### 2.2 Propuesta de rediseño incremental (sin romper contrato)

#### Nivel A (mínimo)
1. Mantener el pipeline actual.
2. En C4, separar visualmente:
   - **Recompensa aplicada al jugador/equipo propio** (bloque principal grande)
   - **Detalle técnico** (colapsable)
3. Ocultar por defecto filas de enemigos no elegibles (`eligible=False` o ganancia 0).

#### Nivel B (explicabilidad)
1. Añadir sección **“Parámetros de rendimiento”**:
   - Base EXP/Oro
   - Multiplicadores (riesgo, resultado, HP, condiciones)
   - Fórmula textual simple:
     - `exp_gain = base_exp * risk_exp * result_exp * performance_exp * antiabuso * multi_factor * hp_reward_multiplier * reward_condition_exp_mult`
     - `oro_gain = base_oro * risk_oro * result_oro * performance_oro * antiabuso * multi_factor * hp_reward_multiplier * reward_condition_oro_mult`
2. Mostrar redondeo final y deltas.

#### Nivel C (QA/Dev)
1. Toggle “ver detalle técnico completo” para QA.
2. Mantener warnings/errors visibles siempre.

---

## 3) Estructura técnica actual para “victoria instantánea”

### 3.1 Dónde termina el duelo hoy
- Cuando se detecta equipo enemigo derrotado se hace `jump battle_end`.
- Esto existe tanto en resolución ofensiva como en turno enemigo.

Ejemplos:
- `game/4/j/04C_OFFENSIVE_RESOLVEV1.rpy`
- `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`

### 3.2 ¿Se puede agregar consola de códigos?
Sí, es posible en 2 variantes:

#### Variante 1 — Console de dev nativa Ren’Py
- Útil para desarrollo interno.
- Riesgo: exposición accidental si queda habilitada en build release.
- Recomendación: usarla solo en `config.developer`.

#### Variante 2 — Consola/overlay propia del juego (recomendada)
- Screen modal simple con input de texto + parser de comandos.
- Permite whitelist de comandos seguros (ej. `victory_now`, `set_enemy_hp 0`).
- Activación por hotkey dev y/o flag `bs_saga_dev_admin_enabled`.

### 3.3 ¿Se puede agregar “botón victoria instantánea”?
Sí. Técnica segura:
1. Comando/botón setea HP enemigo a 0 (o marca derrota por helper canónico si existe).
2. Reusa la ruta normal (`jump battle_end`) para no saltarse simulación, idempotencia, persistencia ni aplicación.
3. Registrar auditoría de debug (ej. `source=dev_instant_victory`) para trazabilidad.

---

## 4) Riesgos y guardrails

### 4.1 Riesgos
- Saltar directo a `battle_end` sin coherencia de estado podría dejar datos parciales de turno.
- Si el comando debug se filtra a producción, puede romper economía/progresión.

### 4.2 Guardrails recomendados
- Gating estricto por entorno dev (`config.developer` + flag local).
- Comandos no disponibles en release.
- Audit log explícito cuando se use instant victory.
- Mantener la ruta oficial de cierre (no bypass de simulador/aplicación).

---

## 5) Plan de refactor propuesto (próximas fases)

### Fase R1 — Diseño funcional C4
- Mock del nuevo layout (bloque recompensa principal + panel parámetros + panel técnico).
- Definir qué campos quedan visibles por defecto y cuáles van en expandible.

### Fase R2 — Implementación UI C4
- Ajustar `screen sim_battle_end_reward_summary_v1` sin tocar el contrato del simulador.
- Filtro visual de filas no relevantes (enemigo sin payout).

### Fase R3 — Consola/botón victoria instantánea (dev)
- Crear API dev (`bs_dev_instant_victory()` o equivalente).
- Integrar botón/hotkey en overlay debug.
- Registrar trazas/auditoría.

### Fase R4 — QA y validación
- Smoke: batalla normal, victoria instantánea, derrota, draw.
- Verificar que C4 y aplicación de recompensas siguen correctas.
- Verificar que en release el comando no aparece.

---

## 6) Respuesta a la duda del equipo

**Pregunta:** “¿Se puede agregar una consola para escribir códigos (ej. derrotar enemigo y cerrar duelo)?”

**Respuesta técnica:** Sí, totalmente viable. La forma más robusta es una consola/botón de debug que fuerce KO enemigo y derive al cierre normal `battle_end`, manteniendo intacta la cadena de recompensas.

---

## 7) Alcance de este documento
- Este entregable es **solo documentación/análisis**.
- No define aún el diseño visual final ni implementa comandos dev.
