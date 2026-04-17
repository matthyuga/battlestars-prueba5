# Plantilla de bitácora de sesión (v1)

> Objetivo: dejar trazabilidad clara para retomar trabajo en la próxima sesión sin perder contexto.

## Cómo usar esta plantilla
1. **Duplica este archivo** en `docs/` con nombre:
   - `bitacora_sesion_YYYY-MM-DD.md`
2. Completa cada sección al cierre de la sesión.
3. Usa fechas absolutas (ej. `2026-04-17`) para evitar ambigüedad.
4. Incluye cambios reales (archivos, módulos, labels, scripts) y evita texto genérico.
5. Cierra siempre con **“Próximo paso recomendado”** y **“Nota para retomar rápido”**.

---

# Bitácora de sesión — YYYY-MM-DD

## 1) Contexto de la sesión
- ¿Qué se buscó resolver hoy?
- ¿Qué problema(s) estaban abiertos al iniciar?
- ¿Qué restricciones/entorno aplicaron? (ej. Win7, Ren'Py 7.4.11)

## 2) Objetivo del día
- Objetivo principal:
- Objetivos secundarios:

## 3) Cambios aplicados (resumen ejecutivo)
1. Cambio A (qué se movió/corrigió y por qué).
2. Cambio B.
3. Cambio C.

## 4) Archivos tocados
- `ruta/archivo_1` → breve descripción.
- `ruta/archivo_2` → breve descripción.
- `ruta/archivo_3` → breve descripción.

## 5) Decisiones técnicas registradas
- Decisión 1 + motivo.
- Decisión 2 + tradeoff.
- Regla nueva (si aplica):
  - Ejemplo: “En `init python`, no usar `import renpy` directo; usar `renpy.store as S`”.

## 6) Bugs encontrados y estado
- Bug #1:
  - Síntoma:
  - Causa raíz (si se conoce):
  - Fix aplicado:
  - Estado: `resuelto` / `parcial` / `pendiente`.
- Bug #2 (opcional)...

## 7) Validaciones / testing
- Comandos ejecutados:
  - `comando_1` → PASS/FAIL + nota.
  - `comando_2` → PASS/FAIL + nota.
- Validación manual:
  - Flujo probado 1.
  - Flujo probado 2.

## 8) Riesgos y deuda técnica pendiente
- Riesgo 1.
- Riesgo 2.
- Deuda técnica 1.

## 9) Próximo paso recomendado (siguiente sesión)
1. Paso 1 (accionable, concreto).
2. Paso 2.
3. Paso 3.

## 10) Nota para retomar rápido
- “Si hay error en X, revisar primero Y/Z”.
- “Entrar por label/pantalla A para reproducir”.
- “Archivo de referencia principal: ...”.

## 11) Checklist de cierre de sesión
- [ ] Bitácora guardada en `docs/bitacora_sesion_YYYY-MM-DD.md`.
- [ ] Próximo paso definido.
- [ ] Riesgos/deuda anotados.
- [ ] Reproducción de bug crítico documentada (si aplicó).
