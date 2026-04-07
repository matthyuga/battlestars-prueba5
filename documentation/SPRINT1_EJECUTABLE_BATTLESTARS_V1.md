# SPRINT1_EJECUTABLE_BATTLESTARS_V1

Fecha: 2026-04-07  
Duración objetivo: 7 días (1 semana)  
Estado: Plan ejecutable

## 1) Objetivo del Sprint 1

Entregar un incremento funcional mínimo y testeable que cubra:
- Inventario MVP fuera de combate (Fase 1).
- Inventario en combate + consumibles base (Fase 2).
- Base de auditoría/logs para QA.

Resultado esperado: flujo completo **equipar en lobby → entrar combate → usar consumible con validaciones por turno → ver reporte/log**.

---

## 2) Alcance cerrado del sprint

### Incluye
1. Slots MVP: 2 anillos, 1 diadema, 1 collar, 2 brazaletes, 1 tatuaje.
2. Presets: balanceado/ofensivo/defensivo (guardar/cargar/sobrescribir).
3. Snapshot de combate al inicio.
4. Consumibles base: HP/EC/EP/Durabilidad (25/35/50 por color).
5. Reglas anti-spam por turno (1 por tipo/color + bloqueo duplicado).
6. Logs con `reason_code` y estado de tracker.

### No incluye (fuera de sprint)
- Amuletos raros (Fase 3).
- Fórmula económica avanzada y telemetría de inflación (Fase 4).
- Torre jugable completa (Fase 5).
- Rotación semanal de personajes (Fase 6).

---

## 3) Backlog ejecutable (tickets)

## Epic A — Inventario MVP Lobby (Fase 1)

### A1. Catálogo + inventario base
- Implementar lectura de `item_catalog` y `inventory_profile`.
- Validar `qty >= 0`.
- Soporte alta/baja básica de ítems.

### A2. Equipamiento por slots MVP
- Adaptador de compatibilidad slot/subtype.
- Validación tier/rareza.
- Tatuaje único por personaje.

### A3. Presets de loadout
- `balanceado`, `ofensivo`, `defensivo`.
- Guardar/cargar/sobrescribir/reset.
- Manejo de preset inválido (item ausente).

## Epic B — Inventario en Combate (Fase 2)

### B1. Builder de `combat_inventory_snapshot`
- Crear snapshot al iniciar batalla.
- Incluir `allowed_items`, `turn_usage_tracker`, `remaining_durability`.

### B2. Consumo base HP/EC/EP/Durabilidad
- Aplicación de efecto por % (25/35/50).
- Validar disponibilidad en snapshot.

### B3. Reglas anti-spam por turno
- Límite 1 por tipo/color por turno.
- Bloqueo duplicado exacto en turno.
- Reseteo en `on_turn_change`.

### B4. Logging QA
- Registrar `applied|rejected`, `reason_code`, before/after.
- Persistencia en log consultable para replay QA.

## Epic C — QA y cierre de sprint

### C1. Smoke QA funcional
- Equipar/desequipar.
- Guardar/cargar presets.
- Consumo válido e inválido en combate.

### C2. Casos borde obligatorios
- Doble uso mismo turno (falla).
- Sin stock (falla).
- Turno siguiente permite uso (si hay stock).

### C3. Cierre
- Checklist QA firmado.
- Demo interna del flujo E2E.

---

## 4) Plan por días (ejecutable)

### Día 1 — Setup técnico y contrato
- Congelar versión de contrato a usar (`inventory_contract_version=v1`).
- Montar estructuras base de inventario.
- Checklist técnico de dependencias.

### Día 2 — Lobby inventario (A1)
- Alta/baja ítems.
- Render de inventario por categoría.
- Validaciones de cantidad.

### Día 3 — Equipamiento y slots (A2)
- Equipar/desequipar slots MVP.
- Validación subtype/tier/rareza.
- Tatuaje único.

### Día 4 — Presets (A3)
- CRUD de presets (3 fijos).
- Carga y restauración de preset.
- Errores controlados de preset inválido.

### Día 5 — Snapshot + consumibles base (B1/B2)
- Generación de snapshot en inicio de combate.
- Uso de HP/EC/EP/Durabilidad 25/35/50.

### Día 6 — Anti-spam + logs (B3/B4)
- Validación por turno y bloqueo duplicado.
- Reseteo de tracker al cambio de turno.
- Registro de logs auditables.

### Día 7 — QA final + demo (C1/C2/C3)
- Ejecutar casos funcionales y borde.
- Corregir bugs críticos.
- Cierre con acta de validación Sprint 1.

---

## 5) Definition of Done (Sprint 1)

Se considera completado si:
1. Inventario lobby MVP usable (equipar + presets).
2. Combate consume HP/EC/EP/Durabilidad con reglas anti-spam correctas.
3. Logs permiten auditar por qué una acción fue aceptada/rechazada.
4. Smoke QA y casos borde pasan sin bloqueos críticos.

---

## 6) Riesgos del sprint y mitigación

1. **Scope creep**
   - Mitigar bloqueando features fuera de sprint.
2. **Inconsistencia entre lobby y combate**
   - Mitigar con snapshot canónico y contrato único.
3. **Bugs de turn tracker**
   - Mitigar con tests manuales de transición de turno + logs.

---

## 7) Métricas mínimas de seguimiento diario

- `% tickets completados`.
- `bugs críticos abiertos`.
- `fallos de validación por turno`.
- `tiempo medio para reproducir bug`.
- `estado semáforo`: verde / amarillo / rojo.

---

## 8) Entregables del Sprint 1

1. `documentation/SPRINT1_EJECUTABLE_BATTLESTARS_V1.md` (este documento)
2. `documentation/CHECKLIST_QA_INVENTARIO_Y_CONSUMO_V1.md` (a completar durante el sprint)
3. `documentation/ACTA_CIERRE_SPRINT1_V1.md` (al cierre)
