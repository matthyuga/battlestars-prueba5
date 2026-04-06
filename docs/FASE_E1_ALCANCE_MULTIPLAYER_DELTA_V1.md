# FASE E1 — Alcance y plan de ejecución (DELTA multiplayer)

Fecha: 2026-03-31  
Estado: Aprobado para iniciar implementación

---

## 1) Objetivo de E1

Definir un alcance **cerrado y verificable** para Fase E, orientada a preparar el simulador de progresión para escenarios DELTA multiplayer sin romper los flujos actuales de single-player/pilot.

E1 no introduce cambios de balance; establece contrato operativo, riesgos y criterio de done para E2..E5.

---

## 2) Alcance incluido en Fase E

1. **Permisos host/invitado (DELTA)**
   - Reglas explícitas de qué eventos pueden otorgar rewards cuando el actor no es host.
   - Política de ownership por `match_id` + `actor_id` para evitar escrituras cruzadas.

2. **Aislamiento de estado**
   - Separación de ledger/idempotencia por sesión multiplayer.
   - Prevención de contaminación entre partidas consecutivas o entre host/invitado.

3. **Trazabilidad multiplayer**
   - Audit mínimo extendido con metadata de sesión (`session_id`, `host_actor_id`, `guest_actor_id` cuando aplique).
   - Evidencia legible para QA de por qué un grant fue aplicado o ignorado.

4. **Ruta de acceso QA al Lab**
   - Punto de entrada explícito para inspección manual (dev-only recomendado).
   - No requiere exponerlo al jugador final en producción.

5. **Checklist de cierre E**
   - Definir los escenarios canónicos a ejecutar manualmente en runtime antes de declarar Fase E cerrada.

---

## 3) Fuera de alcance en Fase E

- Rebalanceo numérico de EXP/Oro/estrellas.
- Matchmaking real online o netcode.
- UI final de producto para jugadores (se mantiene foco QA/dev).
- Refactor general de pantallas no relacionadas al simulador.

---

## 4) Riesgos y mitigaciones

1. **Duplicación de recompensas por reconexión/retry**
   - Mitigación: reforzar idempotencia por actor con claves de sesión.

2. **Persistencia incompatible entre versiones Ren'Py**
   - Mitigación: mantener guardado persistente con compatibilidad 7.x/8.x.

3. **Difícil reproducibilidad QA**
   - Mitigación: fixtures y checklist con resultados esperados por escenario.

---

## 5) Criterios de aceptación de Fase E (alto nivel)

- [ ] Un tester puede abrir el Lab desde una ruta definida sin usar consola.
- [ ] En escenarios DELTA, los grants respetan permisos host/invitado.
- [ ] No hay doble pago entre mid-battle y battle_end en retry/reconexión.
- [ ] El audit permite explicar cada decisión de pago/bloqueo.
- [ ] Checklist manual E ejecutado completo sin crash bloqueante.

---

## 6) Plan secuencial E2..E5

### E2 — Entrada QA + hardening UX mínimo
- Exponer acceso a Sim Lab en modo dev.
- Mensajes de estado para funciones no disponibles.

### E3 — Reglas host/invitado en pipeline
- Extender runtime context con metadata multiplayer.
- Aplicar reglas de autorización en grants mid-battle y cierre.

### E4 — Auditoría y fixtures multiplayer
- Agregar fixtures canónicos host/guest.
- Exportes QA con campos de sesión.

### E5 — Cierre operacional
- Ejecutar checklist manual de punta a punta.
- Registrar evidencia de resultados y issues remanentes.

---

## 7) Definición de Done de E1

E1 queda cerrado cuando:
- Existe este documento aprobado por diseño/QA.
- Está acordada la prioridad de E2 como próximo ítem inmediato.
- Se confirma que los bugs bloqueantes conocidos se corrigen antes de declarar cierre E.

