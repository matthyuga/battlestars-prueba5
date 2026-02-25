# QA checklist regresión 1v1 / 2v2 (M8)

## Preparación
- Iniciar juego desde limpio (sin estado viejo cargado).
- Verificar modo seleccionado en `battle_select_player`.
- Abrir log de batalla para observar owner/slot y daños.

---

## 1v1 intacto

### 1) Inicio de combate
- [ ] Entrar en modo `1v1`.
- [ ] Seleccionar 1 jugador y 1 enemigo.
- [ ] Confirmar popup de turno inicial sin slot (`[Sx]` no obligatorio en 1v1).

### 2) Daño básico + reflect
- [ ] Ejecutar ataque ofensivo normal del jugador y verificar daño en HP enemigo.
- [ ] Ejecutar defensa reflectora y verificar que reflect se aplique sin crash.
- [ ] Confirmar que barra HP/HUD sigue sincronizada.

### 3) Fin de combate
- [ ] Reducir HP enemigo a 0 y validar victoria.
- [ ] Reducir HP jugador a 0 y validar derrota.

---

## 2v2

### 1) Inicialización 2+2
- [ ] Entrar en modo `2v2`.
- [ ] Seleccionar `player_slot_0` y `player_slot_1` (sin duplicados).
- [ ] Confirmar draft de `enemy_slot_0` y `enemy_slot_1`.
- [ ] Verificar HUD 2v2: dos slots por team, HP/KO visibles.

### 2) Turnos por slot
- [ ] Validar round-robin visible en popup/HUD (`owner_team` + `S1/S2`).
- [ ] Confirmar que acciones/costos/log se atribuyen al slot activo del turno.

### 3) KO slot activo + auto-switch
- [ ] Forzar KO del slot activo.
- [ ] Verificar auto-switch al siguiente slot vivo del mismo team.
- [ ] Confirmar continuidad de turnos sin congelar combate.

### 4) KO de ambos aliados => derrota
- [ ] KO de `player:S1` y `player:S2`.
- [ ] Confirmar derrota del equipo jugador.

### 5) Split manual jugador
- [ ] Con ambos objetivos enemigos vivos, usar split manual.
- [ ] Confirmar distribución por entradas y daño por target.

### 6) Split/Burst IA + defensa
- [ ] Observar casos de IA `single_target` (burst) y `split_equal`.
- [ ] En defensa 2v2, validar regla MVP:
  - [ ] Se defiende target principal del turno.
  - [ ] Entradas split restantes se aplican por target (passthrough) sin cover avanzado.

---

## Criterios de salida
- [ ] No crashes al abrir menú/save/load en combate.
- [ ] No desync grave entre HP lógico y HUD.
- [ ] 1v1 sigue jugable de punta a punta.
- [ ] 2v2 cubre ciclo completo (inicio, turnos por slot, KO/victoria/derrota).
