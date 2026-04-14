# Checklist no-regresión combate por cambios de Lobby (v0.1)

Fecha: 2026-04-14  
Estado: Activo

Objetivo: garantizar que avances de lobby (classic/canvas) no impacten runtime de combate.

---

## A) Precondiciones

- [ ] Build ejecutable inicia y entra a combate sin errores.
- [ ] Feature flag `experimental_canvas_ui` configurable en runtime.
- [ ] Modo baseline (`lobby_classic`) disponible para comparación.
- [ ] Logging de errores activo.

---

## B) Smoke de arranque y navegación

- [ ] Abrir Home lobby sin excepciones.
- [ ] Navegar Home -> Héroes -> Tienda -> Inventario -> Home.
- [ ] Cambiar `classic`/`canvas` (si canvas habilitado) sin crash.
- [ ] Volver a Home mantiene estado de cuenta consistente.

---

## C) Flujo economía mínimo (lobby)

- [ ] Comprar héroe descuenta oro y registra auditoría.
- [ ] Comprar ítem descuenta oro y actualiza inventario.
- [ ] Error por oro insuficiente no muta estado.
- [ ] No se permite compra duplicada de héroe.

---

## D) Pasaje a combate (no-regresión)

- [ ] Desde flujo de juego estándar se puede iniciar combate.
- [ ] HUD/entrada a turno cargan sin errores.
- [ ] No hay referencias rotas a estado de lobby en runtime de combate.
- [ ] Finalizar combate no corrompe estado de lobby al volver.

---

## E) Consumo básico en combate (si fase habilitada)

- [ ] Uso válido de consumible descuenta stock.
- [ ] Reglas anti-spam por turno funcionan.
- [ ] Tracker de turno resetea en cambio de turno.
- [ ] Eventos de combate quedan logueados con `reason_code` correcto cuando hay rechazo.

---

## F) Integridad de datos

- [ ] `gold >= 0` siempre.
- [ ] `qty >= 0` siempre.
- [ ] `audit_event` se registra en operaciones económicas válidas.
- [ ] Sin divergencias entre UI mostrada y estado persistido en memoria.

---

## G) Resultado

- [ ] PASS (sin bloqueantes)
- [ ] FAIL (con bloqueantes)

Bloqueantes detectados:
- ...

Acciones correctivas:
- ...

