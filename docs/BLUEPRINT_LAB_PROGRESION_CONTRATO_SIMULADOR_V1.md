# Blueprint v1 + Contrato del Simulador de Progresión

> Documento de arquitectura funcional para el laboratorio de progresión (sin combate real).

---

## 1) Objetivo

Definir un laboratorio in-game para emular progresión/recompensas de forma controlada y reproducible:

- EXP y Oro por actor.
- Nivel, registro y build.
- Resultado de combate (victoria/derrota/empate).
- Desempeño por estrellas (0..30, 6 categorías de 0..5).
- Diferencia de registros (ΔR) en 1v1 y combates múltiples.

---

## 2) Taxonomía de actores (NPC/Jugador)

## 2.1 Tipos

1. **ALPHA**
   - Con progresión completa: nivel, EXP, oro, inventario, equipamiento, comportamiento bot avanzado.
   - Puede crecer, comprar/vender, desbloquear habilidades.

2. **BETA**
   - Actor de combate/encuentro/objetivo de misión.
   - No requiere progresión persistente completa.
   - Puede tener stats y atributos fijos o escalados por evento.

3. **GAMMA**
   - Actor social/ambiental (mercaderes, dadores de quest, peatones).
   - Sin loop de progresión de combate.

4. **DELTA**
   - Invitado (futuro multiplayer host/guest).
   - Tiene progresión propia (stats/EXP/oro/inventario), con límites de interacción de mundo anfitrión.

## 2.2 Matriz de capacidades (resumen)

| Capacidad | ALPHA | BETA | GAMMA | DELTA |
|---|---:|---:|---:|---:|
| Nivel/EXP | ✅ | ⚠️ opcional/no persistente | ❌ | ✅ |
| Oro | ✅ | ⚠️ opcional | ❌ | ✅ |
| Inventario | ✅ | ⚠️ limitado | ❌ | ✅ |
| Combate | ✅ | ✅ | ❌ (general) | ✅ |
| IA avanzada | ✅ | ⚠️ según rol | ❌ | ❌ (humano invitado) |
| Compra/venta | ✅ | ❌ | ✅ (como vendedor) | ⚠️ según reglas host |

---

## 3) Blueprint del laboratorio de progresión

## 3.1 Escena/Lugar de test

- Fondo de campo de juego (sin loop de combate).
- HUD de actor seleccionado:
  - imagen
  - stats
  - nivel/registro
  - barra EXP
  - oro
- Panel de laboratorio (overlay/panel lateral):
  - editar nivel/EXP/oro
  - editar build (principal, distribución, pool)
  - editor de estrellas por categoría
  - editor de enfrentamiento (equipos/resultados)
  - botón de simulación

## 3.2 Módulos funcionales

1. **Actor Registry Module**
   - Crea/carga actores de tipo ALPHA/BETA/GAMMA/DELTA.

2. **Progression Module**
   - Conversión EXP ⇄ nivel ⇄ registro.
   - Asignación de pool por registro/nivel.

3. **Rewards Engine Module**
   - Cálculo de EXP/Oro por resultado + estrellas + ΔR + factores extra.

4. **Match Emulation Module**
   - Construye equipos y determina ganador/perdedor/empate.
   - Soporta 1v1, 2v1, 1v2, 2v2 (extensible).

5. **Lab UI Module**
   - Controls + preview + historial de simulaciones.

6. **Audit/Log Module**
   - Snapshot de inputs/outputs por simulación para QA.

---

## 4) Contrato del simulador (API conceptual)

## 4.1 Input principal (`SimulationRequest`)

```json
{
  "simulation_id": "string",
  "mode": "1v1|2v1|1v2|2v2|custom",
  "source": "battle_end|mid_battle_event|lab_manual",
  "event_type": "victory|defeat|draw|conditional_gain",
  "actors": [
    {
      "actor_id": "string",
      "actor_type": "ALPHA|BETA|GAMMA|DELTA",
      "team": "A|B",
      "level": 1,
      "register": 0,
      "exp_current": 0,
      "exp_max": 100,
      "oro_current": 0,
      "build": {
        "principal": "fuerza|agilidad|resistencia|inteligencia|espiritu",
        "distribution": {"ataque": 0, "defensa": 0, "hp": 0, "reiatsu": 0, "energia": 0},
        "pool": {"total": 0, "offensive_spent": 0, "defensive_spent": 0}
      },
      "stars": {
        "ofensiva": 0,
        "defensiva": 0,
        "control": 0,
        "eficiencia": 0,
        "tecnica": 0,
        "impacto": 0
      },
      "flags": {
        "eligible_rewards": true,
        "allow_level_up": true,
        "allow_inventory_rewards": true
      }
    }
  ],
  "winner_team": "A|B|DRAW",
  "config": {
    "preset": "medium_v2",
    "allow_mid_battle_grants": true,
    "repetition_count": 1,
    "multi_factor_enabled": true
  }
}
```

### Reglas mínimas de validación

- `actors` no vacío.
- `team` obligatorio por actor.
- Si `winner_team != DRAW`, debe existir al menos un actor en ese equipo.
- `stars` por categoría clamp 0..5.
- `stars_total` clamp 0..30.
- `register` clamp 0..50.
- Actores `GAMMA` no deben recibir EXP/Oro de combate por defecto.

---

## 4.2 Output principal (`SimulationResult`)

```json
{
  "simulation_id": "string",
  "mode": "1v1",
  "winner_team": "A",
  "results": [
    {
      "actor_id": "string",
      "eligible": true,
      "stars_total": 22,
      "delta_register": 2,
      "multipliers": {
        "risk_exp": 1.55,
        "risk_oro": 1.28,
        "result_exp": 1.0,
        "result_oro": 1.0,
        "performance_exp": 1.14,
        "performance_oro": 1.02,
        "antiabuso": 1.0,
        "multi_factor": 1.0
      },
      "base": {
        "exp": 112,
        "oro": 59
      },
      "final": {
        "exp_gain": 198,
        "oro_gain": 97,
        "exp_after": 540,
        "oro_after": 1240,
        "level_after": 13,
        "register_after": 1
      },
      "notes": ["level_up:+1", "register_up:+1"]
    }
  ],
  "audit": {
    "warnings": [],
    "errors": [],
    "timestamp": "iso8601"
  }
}
```

---

## 5) Reglas de cálculo (v1)

## 5.1 Estrellas y desempeño

- `stars_total = sum(6 categorias)`.
- clamp `0..30`.
- multipliers de desempeño según configuración activa (preset medio base).

## 5.2 ΔR

Por actor:

- `reg_opp_avg = promedio registros equipo rival`
- `ΔR = reg_opp_avg - reg_actor`

## 5.3 Factor multi (opcional)

`m_multi = clamp((enemigos/aliados)^0.5, 0.85, 1.35)`

## 5.4 Elegibilidad por tipo de actor

- ALPHA, DELTA: elegibles por defecto.
- BETA: configurable (normalmente no persistente).
- GAMMA: no elegible por defecto.

## 5.5 Ganancias mid-battle

Para eventos condicionados (pasivas/técnicas/items):

- `source = mid_battle_event`
- aplica contrato parcial de recompensa
- registra evento en bitácora
- evita duplicar pago en cierre con `reward_event_id` único.

---

## 6) Escenarios que debe cubrir el laboratorio

## 6.1 Duelos individuales

- 1v1 con ganador A/B y empate.
- Ajuste manual de nivel/registro.
- Ajuste de estrellas por categoría.

## 6.2 Duelos múltiples

- 2v1 y 1v2.
- 2v2.
- Variantes con mezcla de tipos ALPHA/BETA/DELTA.

## 6.3 Sin combate real (sandbox)

- Probar únicamente la matemática de progresión/recompensa.
- Mostrar resultado esperado por actor con desglose de multiplicadores.

---

## 7) Auditoría y trazabilidad

Cada simulación debe dejar snapshot:

- Input recibido completo.
- Multiplicadores aplicados.
- Resultado final por actor.
- Razones de exclusión (si algún actor no recibió recompensa).
- Versión de configuración (`reward_config_version`).

---

## 8) Estrategia de implementación por fases

1. **Fase A (Contrato + motor puro)**
   - Implementar funciones sin UI.
   - Tests unitarios de cálculo.

2. **Fase B (Laboratorio UI mínimo)**
   - 1v1 y 2v2 con editor manual.
   - Panel de estrellas + ΔR.

3. **Fase C (Integración con cierre de combate)**
   - Integrar resultado del motor a flow de fin de combate.

4. **Fase D (Eventos mid-battle)**
   - Activar recompensas parciales condicionales.

5. **Fase E (Preparación DELTA multiplayer)**
   - Añadir reglas de permisos y aislamiento host/invitado.

---

## 9) Criterios de aceptación (QA)

- [ ] Simulación 1v1 produce mismo resultado con misma semilla/input.
- [ ] Simulación 2v1/2v2 aplica `ΔR` por actor correctamente.
- [ ] `stars_total` no supera 30 ni baja de 0.
- [ ] Actor `GAMMA` no recibe recompensa de combate por defecto.
- [ ] No hay duplicación de recompensa entre `mid_battle_event` y `battle_end`.
- [ ] Log/auditoría guarda trazabilidad completa por simulación.

---

## 10) Decisiones abiertas para refinar luego

1. Persistencia de recompensas para BETA.
2. Escalado de `m_multi` en modos >2v2.
3. Política de empate (reward parcial o neutro).
4. Cap global diario/semanal anti-farm.
5. Reglas de interacción DELTA con quests/diálogos del host.

