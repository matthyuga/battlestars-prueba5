# Manual definitivo (Windows) — Economy Toolkit

Fecha: 2026-04-13

Este documento centraliza todo el flujo operativo que venimos usando:

- qué hace cada herramienta,
- cómo abrir PowerShell y en qué ruta trabajar,
- qué comandos ejecutar (sin `make`),
- qué esperar como resultado,
- qué errores son normales y cómo resolverlos.

---

## 1) Objetivo del toolkit (en una frase)

El Economy Toolkit sirve para **simular, congelar y comparar** economía (oro/EXP) entre versiones y generar evidencia (`diff`, `dashboard`, `bundle`) para decidir si aprobar o ajustar un parche de balance.

---

## 2) Requisitos mínimos

Obligatorio:

1. Python 3.10.x
2. pip

Opcional:

3. PyInstaller (solo para compilar `.exe`)

```powershell
python -m pip install --upgrade pyinstaller
```

Importante:

- En Windows **no necesitas `make`**.

---

## 3) Abrir PowerShell y entrar al repo (paso 0 siempre)

Podés usar el mismo PowerShell durante toda la sesión; **no hace falta cerrar y abrir** entre comandos.

Solo asegurate de estar en la ruta del repo:

```powershell
cd C:\Users\KEVIN\Desktop\battlestars-prueba5
pwd
```

Si `pwd` no muestra esa carpeta, corrígelo antes de ejecutar comandos del toolkit.

---

## 4) Mapa rápido de herramientas

- `tools/economy_toolkit.py`: CLI unificado (recomendado).
- `tools/economy_lab.py`: simulación pura de economía.
- `tools/run_economy_baseline.py`: congelar baseline versionado.
- `tools/compare_economy_baselines.py`: comparar old vs new y alertas.
- `tools/economy_dashboard.py`: generar HTML dashboard.
- `tools/build_economy_toolkit_executable.py`: construir `dist/economy-toolkit.exe`.
- `tools/package_economy_toolkit_release.py`: empaquetado de release.
- `tools/verify_release_checksum.py`: verificación de checksum.
- `tools/generate_economy_ci_metrics.py`: métricas para CI.

---

## 5) Flujo recomendado (no técnico, con executable)

### 5.1 Construir el ejecutable (una vez por actualización de código)

```powershell
python tools\build_economy_toolkit_executable.py
```

Verificación rápida:

```powershell
.\dist\economy-toolkit.exe profile-list
```

Debe listar:

- `balance_default`
- `release_candidate`

### 5.2 Ejecutar wizard

```powershell
.\dist\economy-toolkit.exe wizard
```

Flujo recomendado:

1. `Elegí opción [1]`: `1` (Ejecutar profile)
2. `Número de profile [1]`: `1` (`balance_default`)
3. `Nueva versión`: ejemplo `economy_v1_2026-04-12`
4. `Versión previa`: ejemplo `economy_v0_2026-04-10`
5. `Nombre bundle`: ejemplo `primer_bundle`

### 5.3 Resultado esperado

Si sale bien, verás mensajes `[ok]` de:

- baseline congelado,
- compare sin error,
- dashboard generado,
- report bundle generado.

Y tendrás:

`artifacts/economy_reports/primer_bundle/`

con archivos:

- `diff.json`
- `diff.md`
- `dashboard.html`
- `manifest.json`

Abrí `dashboard.html` en navegador.

---

## 6) Flujo alternativo (sin wizard, comando directo)

```powershell
python tools\economy_toolkit.py run-profile --name balance_default --version economy_v1_2026-04-12 --previous-version economy_v0_2026-04-10
```

O equivalente con executable:

```powershell
.\dist\economy-toolkit.exe run-profile --name balance_default --version economy_v1_2026-04-12 --previous-version economy_v0_2026-04-10
```

---

## 7) Cuándo debes crear baseline previa

Si te aparece error de tipo:

`no existe old suite: artifacts/economy_baseline/<version>/suite.json`

entonces falta congelar la versión anterior. Solución:

```powershell
python tools\run_economy_baseline.py --version economy_v0_2026-04-10 --out-dir artifacts/economy_baseline
```

Luego vuelves a correr wizard/run-profile con esa `previous_version`.

---

## 8) Errores comunes y solución corta

1. `No such file or directory` al ejecutar `python tools\...`
   - Estás fuera del repo (`C:\Users\KEVIN>` en vez de `...\battlestars-prueba5`).
   - Solución: `cd` a la carpeta del proyecto.

2. `no hay profiles en tools/profiles` usando `.exe`
   - Ejecutable viejo o compilado antes del fix.
   - Solución: actualizar repo y recompilar `.exe`.

3. traceback al guardar en `/tmp` en Windows
   - Ejecutable viejo.
   - Solución: actualizar repo + recompilar (el toolkit actual ya usa temp dir del sistema).

4. `cmd requerido` al ejecutar `.exe`
   - Faltó subcomando o typo en bandera.
   - Ejemplo correcto: `.\dist\economy-toolkit.exe wizard`

---

## 9) Sesión PowerShell: ¿cerrar o seguir en la misma?

Podés seguir en la **misma sesión** sin problema.

Solo cerrá/abrí de nuevo si:

- cambiaste instalación de Python/PATH y no se refresca,
- querés “limpiar estado mental” de comandos.

En general no es obligatorio cerrar.

---

## 10) Checklist operativo rápido (copiar y pegar)

```powershell
cd C:\Users\KEVIN\Desktop\battlestars-prueba5
python --version
python -m pip --version
python tools\build_economy_toolkit_executable.py
.\dist\economy-toolkit.exe profile-list
.\dist\economy-toolkit.exe wizard
```

Después, abrir:

`artifacts\economy_reports\<bundle>\dashboard.html`

---

## 11) Referencias internas

- `tools/README.md`
- `docs/GUIA_RAPIDA_WINDOWS_ECONOMY_TOOLKIT_ES.md`
- `docs/MANUAL_OPERACION_ECONOMY_TOOLKIT_V1.md`

