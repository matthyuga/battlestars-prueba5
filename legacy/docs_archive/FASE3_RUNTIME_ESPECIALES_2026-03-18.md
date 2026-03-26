# Fase 3 — Runtime de técnicas especiales (2026-03-18)

## Estado
**Implementada (corte funcional)** para Ladrón y Salvaguarda en runtime base.

---

## Cambios aplicados

1. **Dataset y validación fuerte**
   - Se añadieron técnicas:
     - `ladron_ofensivo`
     - `ladron_defensivo`
     - `ladron_concentrar`
     - `salvaguarda_principiante`
   - Se amplió validación de `special` para nuevos tipos de especial.

2. **Integración de selector**
   - Nuevas técnicas visibles/mapeadas en selector moderno (funciones, cola y menú).
   - Íconos y labels conectados para uso en combate.

3. **Runtime ofensivo “Ladrón ...”**
   - En ejecución ofensiva del jugador:
     - detecta técnica ladrón,
     - resuelve objetivo enemigo por `unit_key`,
     - aplica bloqueo por 1 turno con `ai_block_tech_for_unit(...)`,
     - registra log operativo.

4. **Runtime defensivo “Salvaguarda principiante”**
   - Se incorporó en acciones defensivas.
   - Marca reducción especial (`special_defense_reduction_pct = 0.50`).
   - En operación defensiva se aplica tras reducción común y antes del total con directo.

---

## Archivos

- `game/02_TECHNIQUES_DATASETV2.rpy`
- `game/04F_SELECTOR_FUNCTIONSV2.rpy`
- `game/04F_SELECTOR_QUEUV2.rpy`
- `game/04F_SELECTOR_MENUV2.rpy`
- `game/4/j/04C_OFFENSIVE_ACTIONSV2.rpy`
- `game/4/j/04D_DEFENSIVE_ACTIONS.rpy`
- `game/4/j/04D_DEFENSIVE_OPERATION.rpy`

---

## Nota de alcance

- Este cierre cubre runtime funcional base para especiales en el flujo actual.
- La selección modal avanzada de técnica objetivo por UI dedicada puede iterarse en una mejora posterior sin bloquear el flujo central.
