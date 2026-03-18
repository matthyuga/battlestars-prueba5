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

- [x] Definir estructura de estado de pre-combate (`mode`, slots, loadout seleccionado).
- [x] Implementar validador central de slots (incluye doble consumo vía especiales derivadas).
- [x] Conectar UI base con catálogo técnico inicial (incluye especiales previstas de Fase 3 para equipamiento).
- [x] Agregar feedback de error de validación en confirmación.
- [x] Guardar/restaurar selección de pre-combate por perfil persistente.

---

## Riesgos activos y mitigación

1. **Desalineación entre modo libre y modo por slots**
   - Mitigación: validador único con bandera de modo.
2. **Confusión en especiales por doble consumo**
   - Mitigación: mostrar consumo explícito en UI.
3. **Regresiones de navegación**
   - Mitigación: smoke test de ruta pre-combate -> volver -> iniciar combate.


---

## Implementación aplicada (corte actual)

- Archivo UI/estado: `game/04I_PRECOMBAT_LOADOUT_SCREENV1.rpy`.
- Entrada desde menú principal: botón `Pre-combate (Fase 1)` en `game/screens.rpy`.
- Resultado de corte: sala funcional de configuración + validación + confirmación de loadout.


---

## Evolución a Fase 2

- Sobre este corte de Fase 1 se aplicó escalabilidad visual (compactación, paginación, íconos/fallback).
- Ver detalle en `docs/FASE2_UI_ESCALABILIDAD_2026-03-18.md`.
