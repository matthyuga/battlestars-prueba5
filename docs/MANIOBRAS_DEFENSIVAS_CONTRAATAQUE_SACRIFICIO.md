# Maniobras defensivas — Contraataque y Sacrificio

Fecha: 2026-03-15  
Proyecto: `battlestars-prueba5`

## Objetivo
Documentar el estado actual de las dos maniobras defensivas nuevas:
- **Contraataque**
- **Solicitar maniobra de sacrificio**

Este documento sirve como base de continuidad para la próxima sesión.

---

## 1) Contraataque

### Resumen funcional
- Es una maniobra defensiva seleccionable en popup de daño entrante.
- Requiere tirada de **4 dados**.
- Solo se considera éxito con **4/4** dados exitosos.

### Reglas vigentes
1. **Uso único por batalla** (flag global `counterattack_used_in_battle`).
2. **Prohibición por riesgo de KO**:
   - Si `HP actual <= daño entrante`, **no se puede usar**.
3. **Umbral mínimo de recursos actuales**:
   - Debe tener al menos 50% del **valor base** de Reiatsu y Energía para poder ejecutarla.
4. **Diferencia base vs actual**:
   - La regla usa 50% de base (no 50% de actual).

### Resolución
- **Si acierta (4/4):**
  - no recibe daño por ese impacto,
  - gana +1 acción ofensiva,
  - no paga penalización de la maniobra.
- **Si falla:**
  - pierde 50% de Reiatsu base y 50% de Energía base,
  - recibe daño completo del impacto,
  - continúa flujo normal del turno.

### Integración UI
- Disponible en `battle_maneuver_choice`.
- Muestra razones de indisponibilidad:
  - ya usada,
  - moriría con ese daño,
  - recursos actuales insuficientes frente a base,
  - unidad derrotada.

---

## 2) Solicitar maniobra de sacrificio

### Resumen funcional
- La unidad objetivo del daño entrante puede solicitar que un aliado se interponga.
- El daño se **redirige al aliado seleccionado** (daño completo).
- El orden de turnos **no cambia**.

### Reglas vigentes
1. **Uso único por batalla para todo el equipo** (flag `sacrifice_used_in_battle`).
2. Solo aparece disponible si hay **aliado vivo** elegible.
3. Si el aliado receptor tiene `HP <= daño entrante`:
   - **no se bloquea** la maniobra,
   - solo se muestra **advertencia de posible KO**.

### Selección de receptor
- En 2v2 se elige entre aliados vivos (distintos del defensor actual).
- La selección se guarda temporalmente en `sacrifice_receiver_key` para resolver daño.
- El diseño es escalable a equipos de 3+ (iteración por candidatos disponibles).

### Resolución
- Si se ejecuta correctamente:
  - marca uso de sacrificio de batalla,
  - aplica daño al receptor elegido con razón `sacrifice`.
- Si no es ejecutable:
  - no redirige,
  - se mantiene la ruta defensiva normal.

---

## 3) Estado técnico (alto nivel)

### Núcleo (helpers / flags)
- Contraataque:
  - `roll_4d`
  - `bs_counterattack_can_use`
  - `bs_counterattack_execute`
- Sacrificio:
  - `bs_sacrifice_candidates`
  - `bs_sacrifice_can_use`
  - `bs_sacrifice_execute`
- Flags:
  - `counterattack_used_in_battle`
  - `sacrifice_used_in_battle`
  - `sacrifice_receiver_key`

### UI y flujo
- Popup de maniobras con opciones y mensajes para ambas maniobras.
- Resolución integrada en:
  - flujo principal de daño entrante del enemigo,
  - flujo diferido de incoming en ofensiva.

### HUD
- Recursos mostrados como **actual/base** para dar visibilidad directa al umbral del 50% base.

---

## 4) Pendientes sugeridos para próxima sesión

1. **QA funcional por matriz de escenarios**:
   - 1v1 y 2v2,
   - contraataque éxito/fallo,
   - bloqueo por HP <= daño,
   - bloqueo por recursos < 50% base,
   - sacrificio con aliado que sobrevive,
   - sacrificio con aliado que puede morir (warning visible).
2. **Microcopy final**:
   - unificar textos (tono, acentos, consistencia de mensajes).
3. **Futuro buff de sacrificio**:
   - soporte para permitir más de un sacrificio por batalla según estado/buff por unidad.
4. **Generalización 3v3**:
   - validar selector de receptor en más de 2 aliados y orden visual del selector.

---

## 5) Checklist de continuidad rápida
- [ ] Confirmar que contraataque se bloquea siempre cuando `HP <= daño entrante`.
- [ ] Confirmar que el costo por fallo de contraataque usa 50% de base (no actual).
- [ ] Confirmar que sacrificio solo consume 1 uso por batalla para el equipo.
- [ ] Confirmar warning de KO potencial en sacrificio sin bloquear selección.
- [ ] Validar que el orden de turnos no cambia al usar sacrificio.
