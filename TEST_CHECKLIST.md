diff --git a/docs/TEST_CHECKLIST.md b/docs/TEST_CHECKLIST.md
new file mode 100644
index 0000000000000000000000000000000000000000..16daeef20bfbc08c9e9338c93b2b752b580893e5
--- /dev/null
+++ b/docs/TEST_CHECKLIST.md
@@ -0,0 +1,129 @@
+# TEST CHECKLIST — Validación manual para cambios B1-A (futuros)
+
+> Objetivo: asegurar que cualquier adopción futura de wrappers/fachada (B1 real) no rompa comportamiento de combate.
+
+---
+
+## 1) Inicio de turnos
+
+### 1.1 Player starts
+- [ ] Iniciar combate varias veces hasta que el primer turno sea del jugador.
+- [ ] Verificar popup/turno correcto y selector funcional.
+- [ ] Confirmar que HP y recursos iniciales se muestran correctamente.
+
+### 1.2 Enemy starts
+- [ ] Iniciar combate varias veces hasta que el primer turno sea del enemigo.
+- [ ] Verificar plan ofensivo IA + transición correcta a maniobra/defensa.
+- [ ] Confirmar que no hay saltos de turno inconsistentes.
+
+---
+
+## 2) Condiciones de fin de combate
+
+### 2.1 KO enemy
+- [ ] Ejecutar secuencia que reduzca `enemy_hp` a 0.
+- [ ] Confirmar victoria, log final y salida por `battle_end`.
+- [ ] Verificar que HUD no queda desincronizado en el último golpe.
+
+### 2.2 KO player
+- [ ] Forzar daño suficiente para `player_hp <= 0`.
+- [ ] Confirmar derrota, mensaje final y limpieza de estado esperada.
+- [ ] Verificar que no queden flags de turno bloqueando reinicio.
+
+---
+
+## 3) Reflect (ambos sentidos)
+
+### 3.1 Reflect jugador -> enemigo
+- [ ] Activar defensa reflectora del jugador.
+- [ ] Confirmar que el reflect se encola al target correcto.
+- [ ] Confirmar consumo correcto al siguiente ataque enemigo/jugador según flujo.
+
+### 3.2 Reflect enemigo -> jugador
+- [ ] Hacer que IA ejecute técnica con reflect.
+- [ ] Confirmar aplicación/consumo en target correcto.
+- [ ] Validar logs de reflect y fuente (`source_id`) cuando esté disponible.
+
+### 3.3 Desvanecimiento/consumo
+- [ ] Validar caso donde el ataque no ocurre y reflect se desvanece.
+- [ ] Confirmar que reflect no se aplica dos veces.
+
+---
+
+## 4) Maniobras
+
+### 4.1 `atk_from_def`
+- [ ] Seleccionar maniobra `atk_from_def`.
+- [ ] Confirmar daño aplicado al jugador + acción ofensiva extra.
+- [ ] Verificar transición al turno ofensivo jugador.
+
+### 4.2 `def_from_atk`
+- [ ] Seleccionar maniobra `def_from_atk`.
+- [ ] Confirmar activación de `defense_for_attack_active`.
+- [ ] Verificar transición a turno defensivo correcto.
+
+### 4.3 `normal`
+- [ ] Seleccionar maniobra normal.
+- [ ] Confirmar flujo completo de `battle_defensive_turn`.
+
+---
+
+## 5) Sincronización HUD
+
+### 5.1 HP
+- [ ] Tras cada daño/curación relevante, verificar coherencia entre HP lógico y barras.
+- [ ] Validar que no haya “saltos” visuales al cambiar turno.
+
+### 5.2 Recursos
+- [ ] Confirmar que consumo de Reiatsu/Energía en acciones coincide con HUD.
+- [ ] Confirmar que simulación del selector coincide con recursos reales al confirmar turno.
+
+---
+
+## 6) IA ofensiva + defensa reactiva
+
+### 6.1 Offense IA
+- [ ] Verificar ejecución de plan ofensivo completo (`current_plan` agotado).
+- [ ] Confirmar manejo de acciones `focus`, `direct_attack`, `noatk_attack`.
+
+### 6.2 Reactive defense IA
+- [ ] Ejecutar escenarios que disparen defensa reactiva.
+- [ ] Confirmar que plan/reactive engine no rompe el orden de turnos.
+
+---
+
+## 7) Casos borde
+
+### 7.1 Recursos en 0
+- [ ] Player con recursos insuficientes: selector bloquea/avisa sin romper turno.
+- [ ] Enemy con recursos insuficientes: IA cae en acciones válidas (`none`/fallback) sin crash.
+
+### 7.2 Focus/Boost activos
+- [ ] Activar focus ofensivo y comprobar consumo/aplicación esperada.
+- [ ] Activar boost defensivo y verificar multiplicador/consumo one-shot.
+- [ ] Confirmar que no hay dobles aplicaciones por turnos consecutivos.
+
+### 7.3 Ataque negador
+- [ ] Caso éxito de `Ataque Negador` (jugador y/o IA según corresponda).
+- [ ] Confirmar skip del turno objetivo exactamente una vez.
+- [ ] Validar interacción con reflect pendiente (consumo o desvanecimiento correcto).
+
+---
+
+## 8) Smoke matrix mínima sugerida por build B1
+
+- [ ] Build B1 + Enemy starts + Maniobra normal + Sin reflect.
+- [ ] Build B1 + Player starts + KO enemy.
+- [ ] Build B1 + Enemy starts + KO player.
+- [ ] Build B1 + Reflect ambos sentidos + noatk.
+- [ ] Build B1 + Recursos límite (0/justo costo exacto).
+
+---
+
+## 9) Criterios de aceptación B1 (futuros)
+
+- [ ] Sin cambios de comportamiento observable vs baseline.
+- [ ] Sin errores de script/traceback en flujos principales.
+- [ ] HUD sincronizado en todos los escenarios listados.
+- [ ] Reflect/turn routing consistente en casos borde.
+- [ ] Reversión fácil: rollback de último commit devuelve comportamiento previo.
