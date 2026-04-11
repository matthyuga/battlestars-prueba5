# Battlestars Saga — Documento de Reglas v1

## 1) Objetivo
Definir una base única y clara para progresión, economía, tipos de personaje e inventario en **Battlestars Saga**, priorizando:
- Duelo libre
- Torneos por tier (C/B/A)
- Torre del cielo

---

## 2) Tipos de personaje (canon Saga v1)
En Battlestars Saga se usarán estos tipos:
- **PLAYER**: cuenta/usuario principal (propietario del lobby, progreso de cuenta).
- **BETA**: NPC sin progresión persistente propia.
- **GAMMA**: invitado multiplayer (fase futura).

> Nota de transición: ALPHA/DELTA pueden existir en módulos legacy, pero **no forman parte del canon Saga v1**.

---

## 3) Progresión en 2 capas (separación obligatoria)

## A. Progresión de cuenta (Account)
- Nivel de cuenta
- EXP de cuenta
- Oro de cuenta
- Desbloqueos globales (modos, features, acceso)
- Inventario general tipo **baúl**

## B. Progresión de héroe (Hero)
- Identidad (id, nombre, clase/rol, tier)
- Técnicas desbloqueadas por tier
- Stats/build (solo en modos que lo permitan, especialmente Torre del cielo)
- Inventario del héroe: **equipables y consumibles asignados al héroe**

### Regla nueva (confirmada)
- **El inventario del héroe NO guarda oro.**
- **Todo el oro vive en la cuenta general** (baúl/economía global de usuario).

---

## 4) Inventario v1

## 4.1 Inventario de cuenta (baúl)
Contiene:
- Oro global
- Consumibles no asignados
- Equipables no asignados
- Materiales de canje / ascensión

Uso:
- Compra en tienda
- Transferencia hacia héroes
- Economía cross-modo (duelo, torneo, torre)

## 4.2 Inventario por héroe
Contiene:
- Equipables activos o en posesión del héroe
- Consumibles asignados al héroe

No contiene:
- Oro

---

## 5) Reglas por modo (v1)

| Modo | Recompensas de cuenta | Progreso de héroe | Comentarios |
|---|---|---|---|
| Duelo libre | Oro (+ opcional EXP cuenta) | No obligatorio | Modo rápido / práctica |
| Torneo C/B/A | Oro + EXP cuenta | Opcional por evento | Recompensas por ronda/fase |
| Torre del cielo | Oro + EXP cuenta + drops | Sí (nivel/stats/build) | Modo serio con dificultad |

---

## 6) Creador de personajes universal (v1)
Debe permitir:
- Crear/editar héroe con identidad y clase
- Definir tier (C/B/A/S u otro catálogo)
- Definir técnicas base por tier
- Definir si es:
  - NPC de Torre
  - Héroe jugable de rotación semanal/temporada
- Configurar pool/puntos iniciales según reglas del modo
- Simular vista previa del héroe en combate

Salida recomendada:
- Data-driven (json/dict/persistent) como fuente de verdad
- Export opcional a script oficial cuando se congele contenido

---

## 7) Puntos y stats (v1)
Separar origen de puntos:
1. Pool base por tier del héroe
2. Bonos por evento/ronda (torneos)
3. Bonos por stat principal/secundario (solo Torre, si aplica)
4. Bonos temporales por consumibles
5. Bonos por equipables

Requisito:
- Registrar trazabilidad del origen de cada punto para evitar desbalance oculto.

---

## 8) Economía y tienda
- Tienda normal con respawn de ítems
- Compra siempre con oro de cuenta
- Asignación posterior de equipables/consumibles a héroes

---

## 9) Escalabilidad futura (2v2 y más)
Este modelo soporta:
- Duelo 2v2
- Torneos 2v2
- Rotación de múltiples héroes por usuario (mínimo 5 en Torre)

Porque separa correctamente:
- Economía global de cuenta
- Estado táctico/progresión de cada héroe

---

## 10) Checklist de implementación v1
1. Congelar canon de tipos en Saga (PLAYER/BETA/GAMMA).
2. Implementar `account_inventory` con oro global.
3. Implementar `hero_inventory` sin oro.
4. Definir interfaz de transferencia baúl -> héroe.
5. Conectar reglas por modo a destinos de recompensa (cuenta/héroe).
6. Añadir auditoría simple de transferencias e ingresos de oro.

## Estado de avance
- ✅ Fase 1 iniciada en código con módulo base `12E_SAGA_FOUNDATIONS_V1.rpy`:
  - Canon Saga v1 expuesto como `BS_SAGA_CANON_ACTOR_TYPES_V1 = ("PLAYER", "BETA", "GAMMA")`.
  - Esquema mínimo de `bs_account_inventory_v1` (oro global + baúl).
  - Esquema mínimo de `bs_hero_inventories_v1` (sin oro por héroe).
- ✅ Fase 2 iniciada en código (economía e inventarios):
  - Helper `bs_account_add_item_v1(bucket, item_id, qty)` para altas en baúl de cuenta.
  - Helper `bs_transfer_chest_to_hero_v1(hero_id, bucket, item_id, qty)` para transferencias baúl -> héroe.
  - Transferencias limitadas a `consumables`/`equipables` (oro sigue fuera del inventario de héroe).
- ✅ Fase 3 iniciada en código (recompensas por modo):
  - Helper `bs_apply_mode_rewards_v1(mode, payload)` con enrutamiento para `duel_free`, `tournament` y `tower`.
  - Destino de recompensas conectado a cuenta (`oro/exp`) y, cuando aplique, progreso de héroe + drops.
- ✅ Fase 4 iniciada en código (trazabilidad y balance):
  - Log de auditoría `bs_economy_audit_log_v1` con eventos de ingresos, transferencias y consumos.
  - Helper de consumo `bs_consume_hero_item_v1(...)` + auditoría automática.
