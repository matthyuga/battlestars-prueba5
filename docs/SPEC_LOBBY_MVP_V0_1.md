# SPEC v0.1 — Battlestars Saga Lobby (MVP Semifuncional)

Fecha: 2026-04-13  
Estado: Propuesto para implementación incremental

---

## 1) Objetivo

Construir un **lobby semifuncional** para Battlestars Saga que permita validar el metajuego sin depender del motor de combate.

Este MVP debe simular:

- cuenta (oro, exp, nivel, tier),
- compra de héroes e ítems,
- actualización de inventario,
- navegación entre secciones,
- auditoría simple de operaciones.

No reemplaza ni modifica el sistema de combate por turnos en esta fase.

---

## 2) Alcance

### 2.1 In-scope (entra al MVP)

1. Pantalla principal de lobby + navegación entre módulos.
2. Estado de cuenta simulado y visible en UI.
3. Módulo Héroes:
   - listar catálogo disponible,
   - comprar/desbloquear héroes,
   - ver roster adquirido.
4. Módulo Tienda:
   - listar ítems,
   - comprar ítems con validación de oro.
5. Módulo Inventario:
   - visualizar contenido de cuenta,
   - visualizar inventario por héroe (solo lectura en v0.1).
6. Auditoría de eventos de economía:
   - compra de héroe,
   - compra de ítem,
   - gasto/ingreso de oro.

### 2.2 Out-of-scope (fuera del MVP)

1. Integración completa con combate runtime.
2. Matchmaking, netcode o sincronización online.
3. Lógica avanzada de equipamiento (durabilidad, efectos por turno, etc.).
4. Persistencia final de producción cross-device.
5. Balance definitivo de precios/recompensas.

---

## 3) Arquitectura funcional (MVP)

### 3.1 Capas

1. **UI Lobby**
   - pantalla principal y subpantallas.
2. **State Store Saga**
   - estado de cuenta, catálogos, inventario y transacciones.
3. **Use Cases**
   - funciones puras de negocio (`buy_hero`, `buy_item`, `grant_exp`, etc.).
4. **Audit Log**
   - bitácora de eventos para debugging y validación.

### 3.2 Principio clave

El lobby opera como **meta-capa desacoplada del combate**.
Cualquier integración con combate se hará vía contratos explícitos en fases posteriores.

---

## 4) Modelo de datos (v0.1)

## 4.1 `account_state`

```json
{
  "account_id": "local_player",
  "display_name": "Mistico",
  "level": 1,
  "exp": 0,
  "exp_to_next": 100,
  "tier": "C",
  "gold": 5000,
  "gems": 0
}
```

## 4.2 `hero_catalog_entry`

```json
{
  "hero_id": "aqua",
  "name": "Aqua",
  "franchise": "KonoSuba",
  "tier": "C",
  "price_gold": 1200,
  "enabled_modes": ["duelo_libre", "torneo", "torre"]
}
```

## 4.3 `hero_owned_entry`

```json
{
  "hero_id": "aqua",
  "owned": true,
  "level": 1,
  "exp": 0,
  "is_rotation_free": false
}
```

## 4.4 `item_catalog_entry`

```json
{
  "item_id": "potion_hp_red",
  "name": "Poción HP roja",
  "item_type": "consumable",
  "rarity": "uncommon",
  "tier_requirement": "C",
  "price_gold": 300,
  "stackable": true,
  "max_stack": 20
}
```

## 4.5 `inventory_state`

```json
{
  "account_inventory": {
    "consumables": {"potion_hp_red": 3},
    "equipables": {},
    "materials": {}
  },
  "hero_inventories": {
    "aqua": {
      "consumables": {},
      "equipables": {}
    }
  }
}
```

## 4.6 `audit_event`

```json
{
  "ts": 1712966400,
  "event": "buy_hero",
  "payload": {
    "hero_id": "aqua",
    "price_gold": 1200,
    "gold_before": 5000,
    "gold_after": 3800
  }
}
```

---

## 5) Módulos de UI del MVP

## 5.1 Home Lobby

- Mostrar perfil básico, oro/exp/nivel/tier.
- Botones de navegación a módulos.
- No ejecuta combate en v0.1.

## 5.2 Perfil

- Mostrar `account_state`.
- Mostrar progreso visual de EXP.

## 5.3 Héroes

- Lista de catálogo (tier, franquicia, precio).
- Acción: comprar héroe.
- Lista de héroes adquiridos.

## 5.4 Tienda

- Lista de ítems por categoría.
- Acción: comprar ítem (qty=1 en v0.1).

## 5.5 Inventario

- Vista de baúl de cuenta.
- Vista de inventario por héroe (solo lectura).

## 5.6 Catálogos (ítems/técnicas)

- Catálogos navegables para inspección de contenido.
- Sin edición avanzada en v0.1.

---

## 6) Casos de uso (Use Cases)

### 6.1 `buy_hero(account_id, hero_id)`

Validaciones:
1. héroe existe en catálogo,
2. no está ya adquirido,
3. oro suficiente,
4. héroe habilitado.

Efectos:
1. descuenta oro,
2. crea entrada en `hero_owned`,
3. registra `audit_event`.

### 6.2 `buy_item(account_id, item_id, qty=1)`

Validaciones:
1. ítem existe,
2. qty > 0,
3. oro suficiente,
4. respeta `max_stack`.

Efectos:
1. descuenta oro,
2. incrementa inventario,
3. registra `audit_event`.

### 6.3 `grant_account_exp(account_id, amount)`

Validaciones:
1. amount >= 0.

Efectos:
1. suma exp,
2. sube nivel si cruza umbral,
3. recalcula `exp_to_next`,
4. registra `audit_event`.

---

## 7) Reglas de negocio (v0.1)

1. **No oro negativo**.
2. **No qty negativa en inventario**.
3. **No compra duplicada de héroe** (en v0.1).
4. `hero_inventory` **no almacena oro**.
5. Todo cambio económico relevante genera audit log.

---

## 8) Integración con estado Saga existente

Se debe mapear el MVP sobre estado ya existente:

- `bs_account_inventory_v1`
- `bs_hero_inventories_v1`
- `bs_account_progress_v1`
- `bs_hero_progress_v1`
- `bs_economy_audit_log_v1`

Esto evita duplicar estado y facilita transición a fases siguientes.

---

## 9) No funcionales

1. Operación offline local (dev).
2. Latencia de acciones de UI < 100 ms local.
3. Respuesta consistente ante error (mensaje visible + no mutar estado inválido).
4. Logs mínimos de depuración en modo dev.

---

## 10) Criterios de aceptación (DoD)

1. Desde lobby se puede abrir Perfil, Héroes, Tienda, Inventario, Catálogos.
2. Comprar héroe descuenta oro y aparece en roster adquirido.
3. Comprar ítem descuenta oro y aparece en inventario de cuenta.
4. No se permite comprar sin oro suficiente.
5. Se registran eventos en auditoría por cada compra.
6. No se altera ni rompe flujo de combate existente.

---

## 11) Plan de implementación (iteraciones)

### Iteración 1 (núcleo de estado)

- Crear/normalizar store del lobby.
- Implementar use cases de compra.
- Implementar audit log.

### Iteración 2 (UI funcional)

- Construir navegación entre módulos.
- Conectar vistas a estado real.
- Exponer mensajes de éxito/error.

### Iteración 3 (validaciones + smoke)

- Tests manuales E2E del flujo compra héroe/ítem.
- Validación de invariantes (oro/qty).
- Checklist de no regresión del combate.

---

## 12) Riesgos y mitigaciones

1. **Riesgo**: catálogos hardcodeados en UI.
   - Mitigación: migrar progresivamente a catálogos data-driven.
2. **Riesgo**: divergencia entre estado del lobby y estado Saga base.
   - Mitigación: usar estado Saga existente como SSOT en MVP.
3. **Riesgo**: mezclar lógica de combate en el lobby.
   - Mitigación: mantener desacople estricto en v0.1.

---

## 13) Próximo documento (v0.2)

Proponer en v0.2:

1. contrato JSON canónico de catálogos (`heroes/items/techniques`),
2. adaptador toolkit -> script/estado de juego,
3. pruebas automáticas de reglas de compra y consistencia de inventario.
