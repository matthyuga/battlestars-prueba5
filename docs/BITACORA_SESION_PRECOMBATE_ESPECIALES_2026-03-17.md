# Bitácora de sesión — Pre-combate y técnicas especiales (2026-03-17)

## Objetivo de esta bitácora
Consolidar en un solo documento todo el contexto funcional acordado en la sesión para retomar trabajo sin perder definiciones ni prioridades.

---

## Estado general de la sesión
- Se trabajó a nivel de **análisis y planificación**, sin implementar mecánicas nuevas de runtime.
- Se confirmó creación de plan por fases en:
  - `docs/PLAN_FASES_PRECOMBATE_TECNICAS_ESPECIALES.md`
- Se validó disponibilidad de nuevos assets en `game/gui/tech_buttons` para especiales.

---

## Decisiones funcionales cerradas

### 1) Nuevas técnicas especiales (concepto y alcance)
- `Ladrón ofensivo`
- `Ladrón defensivo`
- `Ladrón de concentrar`
- `Salvaguarda principiante`

Estas técnicas pertenecen al bloque de **Efecto Especial** y usan botones visuales dedicados.

### 2) Regla de bloqueo para técnicas “Ladrón ...”
- La técnica objetivo se elige desde una lista emergente (panel modal) al resolver efectos tras finalizar turno.
- El bloqueo aplica **solo por 1 turno** del rival objetivo.
- Debe funcionar por slot/unidad (`team:slot`) para escalar a 2v2 y futuros modos multi-equipo.

### 3) Interacción con IA (acordada)
- Si IA está en modo **forzado** a una técnica bloqueada: no reemplaza esa técnica.
- Si IA está en modo normal (no forzado): puede elegir otra técnica válida.
- En concatenación, bloquear una técnica no cancela todo el plan automáticamente; se omite la bloqueada y continúa con el resto válido.

### 4) Regla de “Salvaguarda principiante”
- Es una especial defensiva.
- Reduce 50% del daño **defendible**.
- No afecta daño directo en su versión principiante.
- Prioridad de cálculo acordada:
  1. reducción de técnica común (ej. defensa reductora),
  2. reducción de técnica especial (salvaguarda).

### 5) Evolución futura de salvaguarda
- `Salvaguarda intermedio` podrá reducir también 50% del daño directo.

---

## Escalado de costo/efecto especial discutido
Se definió como escalado por tramos (stepwise), no lineal continuo:
- 100 → 500
- 600 → 510
- 1100 → 520
- 1600 → 530
- 2100 → 540

Interpretación: cada +500 en valor base incrementa +10 en costo asociado.

---

## Reglas de slots pre-combate (acordadas)

### Categorías
- `atk` (ataque)
- `def` (defensa)
- `spc` (especial)

### Configuración base de prueba
- `atk = 7`
- `def = 5`
- `spc = 1`

### Regla oficial
- En juego oficial, por defecto: **1 técnica especial** por jugador.
- A futuro puede ampliarse con perks.
- Para pruebas, se puede habilitar más de una especial si hace falta.

### Perfil ejemplo nivel 1
- `atk = 2`
- `def = 1`
- `spc = 1`

### Doble consumo para especiales
- Especial ofensiva: consume `1 atk + 1 spc`.
- Especial defensiva: consume `1 def + 1 spc`.

### Concentrar/Potenciar dentro de slots especiales
- `Concentrar` se trata como especial ofensiva (`1 atk + 1 spc`).
- `Potenciar` se trata como especial defensiva (`1 def + 1 spc`).

---

## Decisiones de UX/UI para escalabilidad
- Existe riesgo de saturación visual al aumentar técnicas.
- Se acordó evaluar:
  - reducción de tamaño de botones (~20%),
  - desplazamiento lateral/paginación en selector,
  - mantener opción de panel simple/sin PNG para fallback.

---

## Assets verificados en sesión
Se confirmó presencia local de estos archivos en `game/gui/tech_buttons`:
- `ladron_concentrar.png`
- `ladron_defensivo.png`
- `ladron_ofensivo.png`
- `salvaguarda_principiante.png`

---

## Riesgos identificados
1. UI saturada sin scroll/paginación.
2. Complejidad de resolución por orden (común vs especial) si no se centraliza pipeline.
3. IA forzada vs no forzada requiere reglas explícitas para no generar comportamientos ambiguos.
4. Escalado a 2v2/multi-team exige diseñar todo por `unit_key` desde el inicio.

---

## Próximos pasos sugeridos (sesión siguiente)
1. Arrancar por Fase 0/1 del plan (contrato + pre-combate UI mínimo).
2. Implementar validador de slots con doble consumo.
3. Integrar selector de loadout previo a `battle_start` (1v1 primero).
4. Recién luego entrar en mecánicas runtime de “Ladrón ...” y “Salvaguarda”.

---

## Referencias de continuidad
- Plan maestro por fases:
  - `docs/PLAN_FASES_PRECOMBATE_TECNICAS_ESPECIALES.md`
- Esta bitácora está pensada como checkpoint narrativo para retomar rápido contexto funcional.

---

## Addendum de continuidad (2026-03-18)
- Se mantiene Fase 0 como cierre funcional documental previo a implementación.
- Se acuerda incorporar para configuración de pruebas:
  - `modo libre`,
  - `modo por slots` con cantidades configurables de `atk`, `def`, `spc`.
- Se acuerda un parámetro base de perk para especiales (`extra_spc_slots`) para habilitar de 1 a 2 técnicas especiales cuando aplique.
- Se consolida regla operativa de `Salvaguarda principiante` en capas:
  1. reducción común,
  2. reducción especial (50%),
  sin suma lineal de porcentajes.


---

## Addendum de avance (2026-03-18, cierre Fase 0 -> inicio Fase 1)
- Se confirma cierre operativo de Fase 0 para habilitar implementación incremental.
- Se inicia Fase 1 con foco en UI de pre-combate, validador central de slots y persistencia de loadout.
- Se mantiene estrategia: resolver runtime de especiales en fases posteriores para evitar retrabajo temprano.
