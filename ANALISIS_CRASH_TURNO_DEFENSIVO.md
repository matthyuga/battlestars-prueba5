# Análisis: crash al entrar en turno defensivo

## Contexto
Se revisó la rama local `work` para identificar cambios relacionados al crash al entrar en turno defensivo (especialmente al elegir *Defender normalmente* o *Defensa por ataque*).

## Hallazgo principal
El commit **`2d4bd76`** contiene un fix directamente alineado con este síntoma:

- **`game/04F_SELECTOR_QUEUV2.rpy`**
  - Evita interpolaciones complejas inline en textos del selector.
  - Separa el botón de finalizar turno para ofensivo/defensivo.
- **`game/4/j/04D_DEFENSIVE_CORE.rpy`**
  - En 2v2 evita abrir defensa en un slot de jugador no objetivo.
  - Si el slot no fue target, mantiene `defend_amount=0` para que el turno defensivo se salte correctamente.

## Diff recomendado (si tu rama con crash no tiene ese fix)
Aplicar/cherry-pick de `2d4bd76` o replicar este cambio mínimo:

```diff
--- a/game/04F_SELECTOR_QUEUV2.rpy
+++ b/game/04F_SELECTOR_QUEUV2.rpy
@@
- text "Objetivo: [(_sel if _sel else 'AUTO')]"
- text "Daño: [('Dividir x2' if _policy == 'split_equal' else 'Foco único')]"
+ $ _sel_txt = _sel if _sel else "AUTO"
+ $ _dmg_mode_txt = "Dividir x2" if _policy == "split_equal" else "Foco único"
+ text "Objetivo: [_sel_txt]"
+ text "Daño: [_dmg_mode_txt]"
@@
- textbutton "✅ Finalizar turno (objetivo listo)":
-     action Function(confirm_turn_actions)
+ if battle_mode == "offensive":
+     textbutton "✅ Finalizar turno (objetivo listo)":
+         action Function(confirm_turn_actions)
+ else:
+     textbutton "✅ Finalizar turno":
+         action Function(confirm_turn_actions)

--- a/game/4/j/04D_DEFENSIVE_CORE.rpy
+++ b/game/4/j/04D_DEFENSIVE_CORE.rpy
@@
- if defend_amount <= 0 and first_key:
-     # fallback para defender principal
-     ...
+ # Si este slot no fue objetivo, no debe abrir defensa de otra unidad.
+ # Mantener defend_amount=0 fuerza skip defensivo por no daño real.
```

## Comando sugerido
```bash
git cherry-pick 2d4bd76
```

Si hay conflictos, resolver primero en:
- `game/04F_SELECTOR_QUEUV2.rpy`
- `game/4/j/04D_DEFENSIVE_CORE.rpy`
