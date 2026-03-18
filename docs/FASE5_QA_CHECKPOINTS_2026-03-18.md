# Fase 5 — QA incremental por checkpoints (2026-03-18)

## Estado
**Implementada (corte inicial de verificación)** con gate automático de contrato + matriz manual A/B/C/D.

---

## Objetivo de Fase 5
Validar avance sin mezclar todo de golpe, manteniendo control de regresiones en:
- UI pre-combate,
- reglas de slots,
- escalabilidad visual,
- comportamiento IA frente a bloqueos.

---

## Gate automático ejecutado

Script: `scripts/qa_fase5_precombat_gate.sh`

Cobertura del gate:
1. Presencia de artefactos clave (Fases 1/2/4).
2. Contratos mínimos pre-combate (validar/confirmar/persistir).
3. Contratos mínimos IA Fase 4 (bloqueo por `unit_key`, forzado vs normal, omisión en ejecución).
4. Coherencia documental del roadmap (Fase 5 QA incremental).

Resultado actual: **PASS**.

---

## Matriz QA por checkpoints

### QA-A (UI)
- Estado: **Parcialmente validado**
- Incluye:
  - pantalla pre-combate accesible,
  - modo libre / modo por slots,
  - paginación + iconos/fallback,
  - validación al confirmar loadout.

### QA-B (mecánicas especiales)
- Estado: **Pendiente parcial**
- Nota: depende del cierre completo de runtime de Fase 3 (Ladrón + Salvaguarda en resolución de combate).

### QA-C (modos 1v1/2v2)
- Estado: **Parcialmente validado**
- Capa IA por `unit_key` disponible; faltan pruebas integrales end-to-end de combate con especiales runtime.

### QA-D (IA forzado vs normal)
- Estado: **Validado en contrato de código**
- Regla implementada:
  - forzado bloqueado: no reemplaza,
  - normal/concat: omite bloqueada y sigue con válidas.

---

## ¿Qué falta para cerrar bloque completo?

- Para cerrar **todo el bloque funcional de especiales**, falta completar y cerrar la parte profunda de **Fase 3** (runtime de Ladrón/Salvaguarda en combate).
- Luego de eso, ejecutar una ronda final de QA-B + QA-C con casos integrales.
