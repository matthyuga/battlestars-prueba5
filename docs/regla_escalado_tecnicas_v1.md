# Regla de escalado de técnicas (v1)

## Definición
- `puntos`: tramo en bloques de 100.
- `escala`: contador cíclico 1..10 por cada bloque de 100 puntos.
- `escala_base`: umbral de salto de costo EC por técnica.

Regla de costo para técnicas que usan EC:

`ec_costo = ec_base + ec_step * floor((puntos - 1) / (escala_base * 100))`

Donde `ec_step=10` en esta versión.

## Escala base por técnica
- ataque extra: 9
- tecnica extra: 7
- ataque reductor: 5
- ataque directo: 6
- ataque negador: 6
- efecto especial: 5
- ataque basico: no usa EC
- defensa extra: 9
- defensa reductora: 5
- defensa basica: no usa EC
- defensa reflectora: 4
