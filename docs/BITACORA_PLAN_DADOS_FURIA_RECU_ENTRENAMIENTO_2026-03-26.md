# BITÁCORA — Plan de continuidad: Dados (Recuperación/Furia), Sala de Entrenamiento y rutas de inicio

**Fecha:** 2026-03-26  
**Repositorio:** battlestars-prueba5  
**Objetivo de esta bitácora:** dejar registro claro de acuerdos, reglas funcionales, estado actual y plan de ejecución para la próxima sesión en otra rama.

---

## 1) Contexto resumido de lo conversado

Durante esta sesión se trabajó y discutió sobre:

1. **HUD de HP con barra fake gris por daño** (aparece al recibir daño y luego se desvanece).
2. **Reglas de pools específicos del panel de historia/piloto** (base + distribución para ataque/defensa).
3. **Nuevos assets** para:
   - dados de recuperación,
   - dados de furia (éxito/fracaso furia),
   - botones de panel para sala de entrenamiento.
4. **Diseño funcional de nuevas mecánicas**:
   - dado de recuperación (revivir por %),
   - dados de furia (5 tiradas, multiplicadores por éxitos).
5. **Necesidad de separar rutas de inicio (start labels/modes)** para evitar mezclar modos historia, entrenamiento y combate normal.

---

## 2) Estado observado en este workspace al cierre

- En este workspace no se encontraron todavía los nuevos PNG esperados para recuperación/furia/panel-buttons en rutas detectables de `game/`.
- Se acordó continuar en **nueva sesión / nueva rama** y retomar desde una base más limpia de ejecución.
- Se validó la conveniencia de **aislar modo entrenamiento** para que ajustes experimentales (HP, cubre, etc.) no contaminen flujo normal de combate.

---

## 3) Reglas funcionales acordadas — Dados de recuperación

### 3.1 Regla principal
- Se activan cuando una unidad cae derrotada por primera vez en la batalla.
- Aplican para **todos**: jugador, enemigo, aliado o neutro (según pertenencia a combate activo).
- **Uso único por batalla por unidad**.

### 3.2 Resultado del dado de recuperación
- Caras/resultado esperado: `0, 25, 50, 75, 100`.
- El valor representa **% de HP total** que se recupera tras caer.
- Si sale `0`, no revive y queda derrotado.
- Si sale `25/50/75/100`, revive con ese % de su HP máximo.

### 3.3 Persistencia
- El uso único se reinicia al iniciar un combate nuevo.

---

## 4) Reglas funcionales acordadas — Dados de furia

### 4.1 Disponibilidad
- Vía condición natural: unidad con **HP <= 10%**.
- Vía item habilitador (a futuro; item aún no implementado).

### 4.2 Costo de activación
- Requiere gastar:
  - **10% del Reiatsu total** (no actual), y
  - **10% de la Energía total** (no actual).

### 4.3 Resolución de tirada (5 unidades)
- Se lanzan 5 dados de furia.
- Dado calavera = `fracasofuria`.
- Dado colorido/Harribel = `exitofuria`.
- Multiplicador de daño según cantidad de éxitos:
  - 1–2 éxitos: `x1` (sin multiplicar)
  - 3–4 éxitos: `x2`
  - 5 éxitos: `x3`

### 4.4 Persistencia
- A diferencia de otros recursos “una vez por batalla”, furia puede usarse varias veces en un duelo **si cumple lineamientos/costos**.

---

## 5) Sala de Entrenamiento (fase inicial con placeholders)

### 5.1 Enfoque acordado
Iniciar por un **hub/pantalla de entrenamiento** (placeholder visual/funcional) con botones que lleven a módulos tutoriales.

### 5.2 Botones/módulos previstos
1. Salud y Cubre
2. Maniobras
3. Efectos especiales
4. Dados
5. Ítems consumibles (placeholder por ahora)

### 5.3 Flujo por módulo (primera versión)
- Click en botón -> label de explicación/fundamentos -> duelo de práctica con pautas condicionadas.
- Inicialmente puede quedar en modo placeholder (texto + navegación + retorno) y luego escalar a combate guiado.

---

## 6) Arquitectura de rutas de inicio — decisión de diseño

### Problema
Cambios tutoriales pueden afectar combates normales si comparten el mismo flujo de entrada/estado.

### Decisión
Separar rutas claramente por modo:
- `start` / flujo normal,
- `start historia` (piloto narrativo),
- `start entrenamiento` (nuevo hub),
- futuros modos de test/sandbox.

### Objetivo técnico
Evitar contaminación de estado entre modos (flags, overrides de HP/cubre, reglas especiales, etc.).

---

## 7) Plan de ejecución sugerido para próxima rama/sesión

### Fase A — Infraestructura de entrada (prioridad alta)
1. Agregar entrada visible “Start Entrenamiento” en menú.
2. Crear label y screen de `training_hub`.
3. Conectar botones placeholder a labels individuales.

### Fase B — Contratos mínimos de combate por modo
1. Namespacing de estado de entrenamiento (flags y overrides propios).
2. Guardas de limpieza/reset al salir del modo entrenamiento.

### Fase C — Dados de recuperación
1. Modelo de estado por unidad: `used_recovery_die_this_battle`.
2. Hook de derrota para tirada única y reaplicación de HP por porcentaje.
3. Soporte para actor jugador/enemigo/aliado/neutro.

### Fase D — Dados de furia
1. Validación de condición de uso (HP <= 10% o item habilitador).
2. Cobro de costo sobre totales (10% reiatsu + 10% energía).
3. Tirada de 5 dados y cálculo de multiplicador x1/x2/x3.
4. Integración visual (íconos éxito/fracaso furia).

### Fase E — Iteración de tutoriales
1. Salud y Cubre (fundamentos + combate guiado).
2. Maniobras.
3. Efectos especiales.
4. Dados.
5. Ítems consumibles (placeholder hasta sistema real).

---

## 8) Riesgos y notas operativas

- Verificar rutas finales de assets en la nueva rama antes de cablear UI.
- Evitar lógica hardcodeada de entrenamiento dentro del flujo estándar de duelo.
- Definir temprano puntos de extensión (hooks) para no romper 1v1/2v2 existentes.

---

## 9) Cierre

Se deja esta bitácora como documento puente para continuar en nueva rama/sesión con una implementación ordenada por fases, empezando por separación de starts y panel de entrenamiento placeholder, seguido de dados de recuperación y dados de furia.
