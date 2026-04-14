# Plan de trabajo — Lobby MVP v0.1 (Battlestars Saga)

Fecha: 2026-04-13  
Base: `docs/SPEC_LOBBY_MVP_V0_1.md`  
Estado: Listo para ejecución

---

## 1) Objetivo operativo

Implementar un lobby semifuncional por fases, sin tocar el combate, para validar metajuego de cuenta/héroes/tienda/inventario con trazabilidad.

---

## 2) Enfoque por fases

## Fase 0 — Preparación y alineación (0.5–1 día)

### Meta
Dejar definidos alcance, reglas y criterios de salida antes de programar.

### Pasos
1. Confirmar scope in/out del MVP con el equipo.
2. Congelar contratos mínimos de estado (`account`, `heroes`, `inventory`, `audit`).
3. Definir checklist de no-regresión de combate.
4. Crear tablero de tareas (P0/P1/P2).

### Entregables
- Scope cerrado y firmado.
- Backlog inicial priorizado.
- Checklist de validación inicial.

### DoD
- No hay ambigüedad en “qué entra” y “qué no entra”.

---

## Fase 1 — Núcleo de estado y reglas (2–3 días)

### Meta
Tener el corazón funcional del lobby sin UI completa.

### Pasos
1. Normalizar store del lobby sobre Saga foundations.
2. Implementar use cases:
   - `buy_hero`
   - `buy_item`
   - `grant_account_exp`
3. Implementar validaciones de negocio:
   - oro no negativo,
   - no compra duplicada de héroe,
   - qty válida y límites básicos.
4. Registrar auditoría de eventos económicos.

### Entregables
- Módulo de estado estable.
- Casos de uso funcionales.
- Log de auditoría operativo.

### DoD
- Casos de uso pasan pruebas manuales de happy-path + error-path.

---

## Fase 2 — Vertical slice funcional (2 días)

### Meta
Entregar primer flujo end-to-end visible.

### Flujo objetivo
`Lobby -> Tienda -> Comprar héroe -> Descontar oro -> Reflejar roster/inventario -> Audit log`

### Pasos
1. Construir navegación mínima entre Home/Héroes/Tienda/Inventario.
2. Conectar UI a estado real (sin mocks ocultos).
3. Mostrar feedback de acción (éxito/error).

### Entregables
- Demo interna navegable.
- Flujo de compra héroe e ítem verificable.

### DoD
- Flujo vertical funciona sin scripts manuales.

---

## Fase 3 — Cobertura de módulos MVP (2–3 días)

### Meta
Completar módulos previstos para v0.1.

### Pasos
1. Perfil: visualización de progreso de cuenta.
2. Héroes: catálogo + roster adquirido.
3. Tienda: listado por categoría + compra.
4. Inventario: cuenta + héroe (lectura v0.1).
5. Catálogos: ítems/técnicas navegables.

### Entregables
- Módulos MVP completos en navegación.

### DoD
- Todas las pantallas del spec v0.1 son accesibles y consistentes.

---

## Fase 4 — Hardening funcional y QA (1–2 días)

### Meta
Cerrar calidad del MVP y preparar siguiente iteración.

### Pasos
1. Ejecutar smoke tests manuales E2E.
2. Validar invariantes de negocio (oro/qty/auditoría).
3. Revisar no-regresión del combate.
4. Corregir bugs críticos/altos detectados.

### Entregables
- Checklist QA firmado.
- Lista de issues residuales (si aplica).

### DoD
- Sin bloqueantes críticos para demo MVP.

---

## Fase 5 — Cierre v0.1 y preparación v0.2 (1 día)

### Meta
Dejar v0.1 utilizable y el camino claro a data-driven.

### Pasos
1. Documentar límites conocidos del MVP.
2. Crear plan de migración de catálogos hardcodeados a JSON canónico.
3. Definir contrato toolkit -> lobby (import/export simple).

### Entregables
- Informe de cierre v0.1.
- Plan v0.2 aprobado.

### DoD
- Hoja de ruta siguiente con tareas concretas.

---

## 3) Priorización de ejecución

## P0 (bloqueante)
- Estado unificado del lobby.
- `buy_hero` / `buy_item` / validaciones / auditoría.
- Vertical slice end-to-end.

## P1 (importante)
- Catálogo técnicas e ítems navegable.
- Perfil con progreso y métricas básicas.

## P2 (mejora)
- Mayor pulido visual.
- Telemetría adicional.
- Pre-adaptadores para toolkit avanzado.

---

## 4) Riesgos y mitigaciones

1. **Riesgo**: crecimiento de hardcode en UI.
   - Mitigación: congelar interfaces de datos desde Fase 1.
2. **Riesgo**: desalineación con sistema Saga base.
   - Mitigación: mapear contra store existente y evitar estados duplicados.
3. **Riesgo**: contaminación del combate por cambios de lobby.
   - Mitigación: desacople estricto + checklist de no-regresión.

---

## 5) Checklist de arranque (día 1)

1. Crear branch de implementación del lobby MVP.
2. Confirmar estructura de archivos objetivo.
3. Implementar `account_state` + `audit_event` base.
4. Implementar `buy_hero` con validaciones.
5. Probar manualmente compra y rollback por error de oro.

---

## 6) Métricas de avance semanales

- `% módulos MVP funcionales`.
- `# flujos E2E pasando`.
- `# bugs críticos/altos abiertos`.
- `tiempo medio de resolución de bug crítico`.

---

## 7) Definición de éxito de v0.1

Se considera completado cuando:

1. Lobby permite navegar todas las secciones del MVP.
2. Compra de héroes e ítems funciona con reglas de negocio.
3. Inventario y oro se actualizan consistentemente.
4. Auditoría registra operaciones clave.
5. El combate no se ve afectado.
