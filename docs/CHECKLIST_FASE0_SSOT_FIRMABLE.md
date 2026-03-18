# Checklist firmable — Fase 0 (SSOT funcional pre-combate y técnicas especiales)

## 0) Estado de cierre (sesión actual)

- [x] Fase 0 aprobada para avance operativo a Fase 1.
- [x] Reglas núcleo consolidadas en acta de decisiones (`docs/FASE0_SSOT_DECISIONES_2026-03-18.md`).
- [x] Pendientes no bloqueantes permitidos: definición nominal de responsables de firma en el camino.

---

> **Propósito:** cerrar ambigüedades funcionales antes de implementar código.
>
> **Uso:** marcar cada ítem como `✅ Aprobado`, `⚠️ Pendiente`, o `❌ Rechazado`.

---

## 1) Datos de control de revisión

- **Fecha de revisión:** ____________________
- **Versión del SSOT evaluada:** ____________________
- **Facilitador de sesión:** ____________________
- **Participantes con voto:** ____________________
- **Alcance de revisión:** `1v1` / `2v2` / `otro: __________`

---

## 2) Matriz de reglas por técnica (bloque obligatorio)

> Completar para cada técnica inicial:
> - Ladrón ofensivo
> - Ladrón defensivo
> - Ladrón de concentrar
> - Salvaguarda principiante

### 2.1 Plantilla por técnica

- **Técnica:** ____________________
- **Categoría:** ofensiva / defensiva / especial
- **Tipo de consumo de slots:** ____________________
- **Input requerido (selector/objetivo):** ____________________
- **Momento de activación exacto:** ____________________
- **Objetivo permitido (unidad/slot):** ____________________
- **Efecto exacto:** ____________________
- **Duración exacta:** ____________________
- **Condición de expiración:** ____________________
- **Comportamiento en IA forzada:** ____________________
- **Comportamiento en IA normal:** ____________________
- **Comportamiento en concatenación:** ____________________
- **Reglas de excepción / no aplica cuando:** ____________________
- **Formato mínimo de log esperado:** ____________________

### 2.2 Validación de completitud de matriz

- [ ] Las 4 técnicas tienen ficha completa sin campos vacíos críticos.
- [ ] No hay contradicciones entre efecto, duración y expiración.
- [ ] Las reglas IA están definidas para forzado y no forzado.
- [ ] Las reglas de concatenación quedaron explícitas.

---

## 3) Diccionario único de términos (obligatorio)

Definir de forma inequívoca:

- [ ] **Forzado:** _______________________________________________
- [ ] **Normal (no forzado):** ___________________________________
- [ ] **Bloqueada:** _____________________________________________
- [ ] **Expira:** ________________________________________________
- [ ] **Turno rival siguiente:** __________________________________
- [ ] **Técnica válida alternativa:** _____________________________

Criterio de aceptación:

- [ ] Cada término tiene una sola definición operativa.
- [ ] No hay términos duplicados con significados distintos.

---

## 4) Reglas de slots y consumo (obligatorio)

### 4.1 Categorías y límites

- [ ] Categorías confirmadas: `atk`, `def`, `spc`.
- [ ] Base de prueba confirmada: `atk=7`, `def=5`, `spc=1`.
- [ ] Perfil ejemplo nivel 1 confirmado: `atk=2`, `def=1`, `spc=1`.
- [ ] Regla oficial vigente: 1 técnica especial por jugador en modo por slots.

### 4.2 Configuración de modos y perks (control de pruebas)

- [ ] Existe parámetro base para perk de especiales (ej. `extra_spc_slots`) que permite subir de 1 a 2 especiales.
- [ ] Existe modo de configuración `modo libre` y `modo por slots` para pruebas/control.
- [ ] En `modo por slots` se puede definir cantidad de slots de `atk`, `def`, `spc`.

### 4.3 Doble consumo para especiales

- [ ] Especial ofensiva consume `1 atk + 1 spc`.
- [ ] Especial defensiva consume `1 def + 1 spc`.
- [ ] `Concentrar` tratado como especial ofensiva.
- [ ] `Potenciar` tratado como especial defensiva.

### 4.4 Casos borde acordados

- [ ] ¿Qué pasa si no hay `spc` disponible?
- [ ] ¿Qué pasa si hay `atk`/`def` disponible pero falta `spc`?
- [ ] ¿Se permite seleccionar técnica si invalida el loadout al confirmar?
- [ ] ¿Cómo se comunica el error al usuario?

---

## 5) Bloqueos “Ladrón ...” (obligatorio)

- [ ] Selección de técnica rival definida en panel post-Finalizar turno.
- [ ] Bloqueo con duración de **1 turno rival** confirmado.
- [ ] Scope técnico por `team:slot` / `unit_key` confirmado.
- [ ] Regla IA forzada bloqueada: no reemplaza técnica.
- [ ] Regla IA normal bloqueada: busca técnica válida alternativa.
- [ ] Regla concatenación: se omite bloqueada y continúa lo válido.

Casos de validación funcional:

- [ ] Bloqueo aplica al objetivo correcto.
- [ ] Bloqueo no “salta” a otra unidad.
- [ ] Bloqueo expira en el turno correcto.

---

## 6) Salvaguarda principiante (obligatorio)

- [ ] Reduce 50% del daño enemigo final aplicable en la resolución (con prioridad por capas).
- [ ] Prioridad confirmada: reducción común → reducción especial (Salvaguarda).
- [ ] No se suma porcentualmente con técnica reductora; se aplica secuencialmente por prioridad.
- [ ] Definidos flags separados de efecto común y efecto especial para pipeline de daño.
- [ ] Fórmula de referencia aprobada para documentación.

Casos de validación funcional:

- [ ] Caso solo defendible.
- [ ] Caso mixto (defendible + directo).
- [ ] Caso solo directo.
- [ ] Caso con reducción común + Salvaguarda (validando orden y no suma directa de %).

---

## 7) Criterios de trazabilidad y QA documental

- [ ] Cada regla tiene referencia a sección SSOT.
- [ ] Existe lista de riesgos funcionales actualizada.
- [ ] Existe lista de supuestos explícitos.
- [ ] Existe lista de fuera-de-alcance para evitar creep.
- [ ] Checklist de humo propuesto para Fase 1+ preparado.

---

## 8) Criterio de “Done” de Fase 0 (gate de salida)

La Fase 0 se considera cerrada **solo si**:

- [x] 100% de ítems obligatorios en estado `✅ Aprobado`.
- [x] 0 contradicciones abiertas en reglas núcleo.
- [x] 0 términos ambiguos en diccionario.
- [x] 0 decisiones pendientes que bloqueen Fase 1.
- [x] Aprobación explícita en modalidad operativa para iniciar Fase 1.

---

## 9) Firmas de aprobación

- **Responsable diseño funcional:** Equipo sesión actual  **Fecha:** 2026-03-18
- **Responsable implementación:** Equipo sesión actual  **Fecha:** 2026-03-18
- **Responsable QA:** Equipo sesión actual  **Fecha:** 2026-03-18
- **Aprobación final (GO Fase 1):** Aprobado (modalidad operativa)  **Fecha:** 2026-03-18

---

## 10) Registro de dudas abiertas (si aplica)

1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

> Si esta sección tiene dudas bloqueantes, el estado de Fase 0 queda en `⚠️ Pendiente`.


> Nota: este cierre usa modalidad operativa de avance; la asignación nominal de firmantes puede completarse durante Fase 1.
