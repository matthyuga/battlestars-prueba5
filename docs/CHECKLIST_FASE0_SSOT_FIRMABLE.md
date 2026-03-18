# Checklist firmable — Fase 0 (SSOT funcional pre-combate y técnicas especiales)

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
- [ ] Regla oficial vigente: 1 técnica especial por jugador (salvo perks futuros).

### 4.2 Doble consumo para especiales

- [ ] Especial ofensiva consume `1 atk + 1 spc`.
- [ ] Especial defensiva consume `1 def + 1 spc`.
- [ ] `Concentrar` tratado como especial ofensiva.
- [ ] `Potenciar` tratado como especial defensiva.

### 4.3 Casos borde acordados

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

- [ ] Reduce 50% de daño defendible.
- [ ] No reduce daño directo en versión principiante.
- [ ] Prioridad confirmada: reducción común → reducción especial.
- [ ] Fórmula de referencia aprobada para documentación.
- [ ] Evolución futura “Salvaguarda intermedio” documentada (incluye directo).

Casos de validación funcional:

- [ ] Caso solo defendible.
- [ ] Caso mixto (defendible + directo).
- [ ] Caso solo directo.

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

- [ ] 100% de ítems obligatorios en estado `✅ Aprobado`.
- [ ] 0 contradicciones abiertas en reglas núcleo.
- [ ] 0 términos ambiguos en diccionario.
- [ ] 0 decisiones pendientes que bloqueen Fase 1.
- [ ] Aprobación explícita de responsables funcionales y técnicos.

---

## 9) Firmas de aprobación

- **Responsable diseño funcional:** ____________________  **Fecha:** __________
- **Responsable implementación:** ______________________  **Fecha:** __________
- **Responsable QA:** _________________________________  **Fecha:** __________
- **Aprobación final (GO Fase 1):** ___________________  **Fecha:** __________

---

## 10) Registro de dudas abiertas (si aplica)

1. ________________________________________________________________
2. ________________________________________________________________
3. ________________________________________________________________

> Si esta sección tiene dudas bloqueantes, el estado de Fase 0 queda en `⚠️ Pendiente`.
