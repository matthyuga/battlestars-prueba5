# Contrato técnico v1 — HP / Estamina / Shadow

Fecha: 2026-03-19
Estado: Borrador operativo para implementación incremental

## 1) Objetivo
Definir reglas **determinísticas** para resolver daño con tres capas:
1. HP normal (celeste).
2. Estamina (gris).
3. Shadow/Sombra (negro, bloquea espacio para generación nueva de estamina).

> Regla inviolable: si HP llega a 0 en la resolución del golpe, hay KO.

---

## 2) Campos de estado propuestos (por unidad)

### Núcleo vida
- `hp_max` (int >= 1)
- `hp_current` (int >= 0, <= hp_max)

### Estamina
- `stamina_current` (int >= 0)
- `stamina_cap` (int >= 0, por defecto `hp_max`)
- `stamina_enabled` (bool; por perk/efecto)

### Shadow
- `shadow_current` (int >= 0)
- `shadow_cap` (int >= 0, por defecto `hp_max`)
- `shadow_active` (bool)

### Derivados de espacio
- `missing_hp = max(0, hp_max - hp_current)`
- `free_space = max(0, hp_max - hp_current - stamina_current - shadow_current)`

Invariante espacial:
- `stamina_current + shadow_current <= missing_hp`

---

## 3) Orden de resolución de daño (por hit)

## Paso A — Capas previas existentes
1. Resolver cobertura/durabilidad (sistema coating actual).
2. Obtener daño que realmente llega a vida/recursos internos (`incoming_after_coating`).

## Paso B — Consumo de estamina (si existe)
1. `st_before = stamina_current`
2. `stamina_absorb = min(st_before, incoming_after_coating)`
3. `stamina_current = st_before - stamina_absorb`
4. `overflow_to_hp = incoming_after_coating - stamina_absorb`

## Paso C — Daño a HP
1. `hp_before = hp_current`
2. `hp_current = max(0, hp_before - overflow_to_hp)`
3. `hp_damage_real = hp_before - hp_current`

## Paso D — KO inmediato
- Si `hp_current <= 0` => KO y **no** se genera estamina por este golpe.

## Paso E — Generación de estamina por daño a HP
Solo si se cumple todo:
1. `hp_damage_real > 0`
2. `stamina_enabled == True`
3. `hp_current > 0` (sobrevivió)
4. `free_space > 0` (espacio libre no ocupado por shadow)

Cálculo:
- `stamina_gain_raw = hp_damage_real`
- `stamina_gain = min(stamina_gain_raw, free_space, stamina_cap - stamina_current)`
- `stamina_current += stamina_gain`

---

## 4) Reglas de Shadow

## Función principal
- Shadow **bloquea espacio** para generar estamina nueva.
- Shadow no impide gastar estamina existente.
- Shadow no impide convertir estamina previa a HP (si esa mecánica existe luego).

## Persistencia
- Por defecto, shadow persiste mientras esté activo.
- Puede apagarse por:
  - expiración temporal,
  - cancelación del usuario,
  - técnica/efecto negador.

## Shadow parcial (derecha -> izquierda)
- Permitido: `shadow_current` puede crecer parcialmente.
- Ejemplo: daño pequeño puede bloquear solo parte del espacio faltante.

---

## 5) Logging canónico (formato base)

Para cada resolución relevante, loggear en este orden:

1. Resultado de estamina (si hubo consumo):
   - `Estamina: {st_before} - {incoming_after_coating} = {st_after}`
   - Si overflow: `Estamina: {st_before} - {incoming_after_coating} = -{overflow_to_hp}`

2. Resultado de HP:
   - `HP: {hp_before} - {overflow_to_hp} = {hp_after}`

3. Generación de estamina (si aplica):
   - `HP genera {stamina_gain} de estamina`

4. Bloqueo por shadow (si limitó ganancia):
   - `Shadow bloquea {blocked_amount} de espacio para estamina`

---

## 6) Casos de referencia

## Caso A: genera estamina normal
- `hp 10000, st 0, shadow 0, daño_hp_real 5000`
- `free_space = 5000`
- `stamina_gain = 5000`
- Resultado: `hp 5000, st 5000`

## Caso B: shadow bloquea generación nueva
- Estado previo: `hp 5000, st 5000`
- Llega daño 6000 -> `st 5000 -> 0`, overflow `1000` a HP
- `hp 5000 -> 4000`
- Si shadow bloquea el espacio nuevo, `stamina_gain = 0`
- Resultado: `hp 4000, st 0`

## Caso C: KO por exceso
- `hp 3000, st 2000` (suma efectiva 5000)
- daño 6000 => overflow final KO
- Resultado: KO, sin generación de estamina

## Caso D: sobrevive por 1 HP y sí genera
- `hp 4001, st 2000`, daño 6000
- estamina absorbe 2000 -> overflow 4000
- HP: 4001 -> 1
- sobrevive y puede generar según `free_space`

---

## 7) Criterios de implementación segura
- No usar `hp_fake_*` como fuente de verdad jugable.
- Introducir estado de estamina/shadow en facade de batalla (unidad activa y lista de equipos).
- Mantener invariantes de espacio tras cada operación.
- Aislar logging en helper dedicado para evitar duplicados.

---

## 8) Criterios de aceptación (QA)
- [ ] KO al llegar HP a 0 siempre.
- [ ] Sin KO, HP dañado genera estamina solo con espacio libre.
- [ ] Shadow bloquea generación nueva, no consume estamina existente.
- [ ] Logs muestran secuencia y números correctos.
- [ ] `stamina_current + shadow_current <= missing_hp` siempre.
