# FASE3_CONSUMIBLES_AVANZADOS_Y_AMULETOS_V1

Fecha: 2026-04-06  
Estado: Plan de ejecución (listo para implementar)

## 1) Meta

Añadir profundidad táctica con consumibles avanzados y amuletos raros sin romper el balance base de combate.

---

## 2) Alcance funcional (Fase 3)

### 2.1 Pociones de ataque/defensa por técnica

Tipos:
- `atk_buff_potion` (25% / 35% / 50%)
- `def_buff_potion` (25% / 35% / 50%)

Reglas:
- Se aplican sobre una técnica objetivo (`technique_id`).
- Duración base recomendada: 1 activación de técnica (consumo por uso).
- No reemplazan límites de Fase 2 (siguen valiendo reglas por turno).

### 2.2 Pociones de stats para Torre

Stats objetivo:
- fuerza
- agilidad
- inteligencia
- espíritu
- resistencia

Escala por color:
- amarilla: +1
- naranja: +2
- roja: +3

Duración configurable por regla:
- `battle` (todo el combate actual), o
- `run` (toda la run de Torre)

### 2.3 Amuletos raros (3 usos)

Todos los amuletos de esta fase tienen `durability_max = 3`.

Amuletos iniciales:
1. **espejo reflectante**
   - Efecto: refleja 30% del daño recibido (no anula el daño entrante).
2. **cilindro mágico**
   - Efecto: absorbe/reduce 30% del daño recibido.
3. **espada sagrada**
   - Efecto: aumenta 30% daño general (directo y defendible).
4. **daga maldita**
   - Efecto: convierte 30% del daño defendible en daño directo.
5. **daga envenenada**
   - Efecto: 30% del ataque general se aplica como daño directo a HP.

---

## 3) Orden de aplicación de efectos (estable)

Orden propuesto para resolver una acción ofensiva:

1. Buffs activos del atacante (incluye `atk_buff_potion`, espada sagrada).
2. Cálculo de daño base por técnica.
3. Conversión de tipo de daño (daga maldita / daga envenenada).
4. Mitigaciones/absorciones defensivas (cilindro mágico, defensa base, etc.).
5. Aplicación de daño final al objetivo.
6. Reflect post-daño (espejo reflectante).
7. Registro de evento detallado en log.
8. Decremento de durabilidad/consumo del ítem usado.

Notas:
- Reflect ocurre al final para evitar bucles infinitos de rebote.
- Toda conversión se calcula antes de mitigación final para mantener consistencia.

---

## 4) Tooltips y logs requeridos

### 4.1 Tooltips mínimos

Todo consumible avanzado/amulet debe mostrar:
- nombre
- tipo/subtipo
- % o valor de efecto
- duración (`instant | turns | battle | run`)
- usos/durabilidad restante
- restricciones de uso por turno/modo

### 4.2 Logs mínimos de runtime

Campos obligatorios:
- `battle_id`
- `turn_number`
- `actor_id`
- `item_id`
- `effect_step` (según orden de resolución)
- `value_before`
- `value_after`
- `duration_remaining`
- `durability_remaining`

---

## 5) Criterios de salida Fase 3

1. Orden de aplicación de efectos definido y estable.
2. Tooltips y logs muestran efecto aplicado y duración restante.

Criterios QA adicionales:
- Resultado consistente al repetir mismo escenario con misma semilla.
- No existen dobles consumos de amuleto en una única resolución.
- Durabilidad de amuleto nunca baja de 0.

---

## 6) Checklist de implementación

- [ ] Implementar `atk_buff_potion` y `def_buff_potion` por técnica.
- [ ] Implementar pociones de stats para Torre con duración `battle/run`.
- [ ] Implementar 5 amuletos raros con 3 usos.
- [ ] Integrar orden de resolución en pipeline de daño.
- [ ] Añadir tooltips completos en UI.
- [ ] Activar logging detallado por `effect_step`.
- [ ] Ejecutar smoke QA de escenarios espejo/cilindro/dagas/espada.

---

## 7) Entregables de Fase 3

1. `documentation/FASE3_CONSUMIBLES_AVANZADOS_Y_AMULETOS_V1.md` (este documento)
2. `documentation/MATRIZ_ORDEN_EFECTOS_COMBATE_V1.md` (pendiente)
3. `documentation/CHECKLIST_QA_FASE3_CONSUMIBLES_AVANZADOS_V1.md` (pendiente)
