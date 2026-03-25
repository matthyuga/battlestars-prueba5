# Análisis forense: regresión entre commit 9 (`72c100d`) y commit 10 (`324d556`)

## Contexto validado
- `72c100d` deja el flujo defensivo estable (sin crash), pero sin aviso de **"Daño entrante"**.
- `324d556` intenta resolver visibilidad del aviso y override de target defensivo en 2v2.
- A partir de `324d556`, aparecen síntomas reportados:
  - 1v1: aparece aviso, al elegir defensa se produce crash.
  - 2v2: no siempre aparece aviso de daño entrante y salta directo a turno defensivo.

## Qué cambió exactamente en commit 10
Según `git diff 72c100d..324d556` en los dos archivos tocados:

### 1) `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`
Se insertaron **dos bloques nuevos** de aviso de daño entrante usando llamadas directas a Ren'Py:
- `renpy.show_screen("battle_popup_turn", ...)`
- `renpy.pause(...)`
- `renpy.hide_screen(...)`

Uno en la ruta `def_from_atk` y otro en defensa normal, antes de entrar al turno defensivo. El flujo ya existente de `battle_popup_turn("Turno defensivo ...")` se mantuvo, por lo que ahora hay doble capa de anuncio previa al defensivo. Esto se observa hoy en el archivo en los bloques de líneas de aviso entrante y transición a defensivo.【F:game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy†L849-L863】【F:game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy†L924-L945】

### 2) `game/4/j/04D_DEFENSIVE_CORE.rpy`
Se ajustó la priorización del target de defensa para 2v2:
- si viene `forced_in` (target explícito de incoming), no sobrescribir con `owner_slot` de turno.

Este cambio está encapsulado en la rama 2v2 y no impacta directo el flujo 1v1. Actualmente puede verse en la condición `if not forced_in:` dentro del bloque de `mode == "2v2"`.【F:game/4/j/04D_DEFENSIVE_CORE.rpy†L136-L147】

## Hallazgos técnicos

### A. Probable origen del crash 1v1: introducción de UI calls directas en commit 10
En el archivo ofensivo, el bloque insertado en `324d556` usa API directa de Ren'Py antes del salto/call defensivo. Es consistente con la cadena de commits posteriores enfocada en "harden"/guards de APIs UI (`pause`, `show_screen`, `get_screen`, `with_statement`) para evitar crashes runtime, lo cual sugiere que esta zona efectivamente quedó frágil desde ese punto.

Además, en una de las rutas se mezcló después un helper seguro con `renpy.pause` sin import garantizado, protegido por `try/except`; eso no siempre crashea duro, pero sí facilita comportamientos silenciosos (se pierde aviso por fallback).【F:game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy†L924-L943】

### B. Por qué en 2v2 puede no aparecer "Daño entrante" y saltar directo
El patrón actual del aviso entrante está envuelto en `try/except` amplio y, ante fallo de UI, cae a fallback o incluso `pass`; luego siempre se ejecuta el popup de "Turno defensivo" y se entra al label defensivo. Esto explica exactamente el síntoma "a veces no aparece aviso entrante pero sí avanza el turno".

### C. El cambio en `04D_DEFENSIVE_CORE.rpy` no parece ser el detonador del crash 1v1
El ajuste de `forced_in` opera dentro de `mode == "2v2"`; en 1v1 no debería alterar la resolución principal de target defensivo. El crash 1v1 apunta más a la capa de UI/transition en ofensiva que al cálculo de target defensivo.

## Línea temporal resumida (post commit 10)
Después de `324d556` hay una larga secuencia de hardening/rollback/guards y fixes de compatibilidad runtime, lo cual refuerza el diagnóstico de regresión introducida en la capa de transición UI del enemigo→defensivo y no en un único bug aislado posterior. En otras palabras:
- **Sí hay un quiebre relevante en commit 10** (sobre todo en `04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy`).
- Los commits siguientes parecen mayormente mitigaciones y retrabajo alrededor de ese quiebre.

## Conclusión operativa
1. Tu hipótesis es consistente: hubo confusión entre "popup" genérico y "ventana de daño entrante" (contexto de maniobras), y eso contaminó la transición.
2. El commit 10 no sólo añade visibilidad; también mete una capa de UI directa que vuelve más frágil la transición en 1v1 y puede ocultar aviso en 2v2 por fallbacks silenciosos.
3. El script con más probabilidad de haber dañado la estructura de flujo es efectivamente `game/4/04D_BATTLE_TURN_ENEMY_OFENSIVEV5.rpy` (no tanto `04D_DEFENSIVE_CORE.rpy`).

## Recomendación de corrección (siguiente paso)
- Rehacer la entrada de "Daño entrante" con **un único helper seguro** (store-safe), sin `show_screen/hide_screen/pause` directos en esta transición.
- Mantener un solo canal de anuncio entrante + anuncio de turno defensivo (sin duplicación de rutas ambiguas).
- Preservar la lógica `forced_in` de 2v2 (es útil para target correcto), pero desacoplada de la presentación UI.
