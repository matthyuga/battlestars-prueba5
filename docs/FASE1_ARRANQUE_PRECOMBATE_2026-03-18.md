# Fase 1 — Arranque operativo (Pre-combate UI + validación de slots)

## Estado
**Iniciada** (habilitada por cierre de Fase 0).

---

## Objetivo de Fase 1
Implementar la sala de pre-combate para configurar loadout por categorías (`atk`, `def`, `spc`) con soporte de `modo libre` y `modo por slots`, sin entrar aún a resolución runtime profunda.

---

## Alcance acordado para primer corte

1. UI de pre-combate accesible desde flujo de navegación actual.
2. Selector por categorías con contadores de usados/restantes.
3. Toggle de modo:
   - `modo por slots`: valida límites activos.
   - `modo libre`: permite pruebas rápidas.
4. Regla de consumo:
   - especial ofensiva: `1 atk + 1 spc`,
   - especial defensiva: `1 def + 1 spc`.
5. Soporte mínimo de perk base:
   - `extra_spc_slots=0` => máx `spc=1`,
   - `extra_spc_slots=1` => máx `spc=2`.

---

## Criterios de aceptación de Fase 1 (primer hito)

- Se puede abrir pantalla de pre-combate sin romper flujo existente.
- No se puede confirmar loadout inválido en `modo por slots`.
- Sí se puede confirmar loadout en `modo libre` para pruebas.
- La selección persiste en sesión/perfil para entrar a combate.

---

## Checklist de implementación inmediata

- [ ] Definir estructura de estado de pre-combate (`mode`, slots, loadout seleccionado).
- [ ] Implementar validador central de slots (incluye doble consumo).
- [ ] Conectar UI base con datasets de técnicas.
- [ ] Agregar feedback de error de validación en confirmación.
- [ ] Guardar/restaurar selección para inicio de combate.

---

## Riesgos activos y mitigación

1. **Desalineación entre modo libre y modo por slots**
   - Mitigación: validador único con bandera de modo.
2. **Confusión en especiales por doble consumo**
   - Mitigación: mostrar consumo explícito en UI.
3. **Regresiones de navegación**
   - Mitigación: smoke test de ruta pre-combate -> volver -> iniciar combate.
