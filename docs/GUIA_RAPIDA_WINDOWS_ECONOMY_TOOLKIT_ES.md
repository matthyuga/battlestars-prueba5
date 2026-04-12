# Guía rápida (Windows) — Economy Toolkit

Fecha: 2026-04-12

Esta guía está pensada para uso **no técnico** en Windows, en español, y responde a la duda principal:

- **¿Qué tengo que instalar?**
- **¿Tengo que instalar `make`?**

## 1) Qué necesitas instalar

Obligatorio:

1. **Python 3.10.x** (marcando "Add Python to PATH").
2. **pip** (viene con Python).

Opcional (solo si querés generar el `.exe`):

3. **PyInstaller**
   ```powershell
   python -m pip install --upgrade pyinstaller
   ```

No obligatorio:

- **`make` NO es obligatorio en Windows**.

---

## 2) Verificación rápida de instalación

En PowerShell, dentro del repo:

```powershell
python --version
python -m pip --version
```

Debe mostrar Python 3.10.x y pip instalado.

---

## 3) Uso recomendado sin `make` (directo)

### A) Ejecutar toolkit con Python

```powershell
python tools\economy_toolkit.py --help
python tools\economy_toolkit.py wizard
```

### B) Ejecutar ciclo por perfil (sin wizard)

```powershell
python tools\economy_toolkit.py run-profile --name balance_default --version economy_v1_2026-04-12 --previous-version economy_v0_2026-04-10
```

---

## 4) Si querés usar ejecutable `.exe`

1. Construir ejecutable:

```powershell
python tools\build_economy_toolkit_executable.py
```

2. Probar ejecutable:

```powershell
.\dist\economy-toolkit.exe --help
.\dist\economy-toolkit.exe wizard
```

---

## 5) Qué archivos se generan

Después de correr `wizard` o `run-profile`, revisá:

- `artifacts/economy_reports/<bundle>/diff.json`
- `artifacts/economy_reports/<bundle>/diff.md`
- `artifacts/economy_reports/<bundle>/dashboard.html`
- `artifacts/economy_reports/<bundle>/manifest.json`

Abrí `dashboard.html` con tu navegador para revisar resultados.

---

## 6) Errores comunes

1. **`No module named PyInstaller`**
   - Solución:
     ```powershell
     python -m pip install --upgrade pyinstaller
     ```

2. **`make` no se reconoce**
   - Solución: ignorar `make` y usar los comandos `python ...` de esta guía.

3. **`python` no se reconoce**
   - Reinstalar Python 3.10.x marcando "Add Python to PATH".

---

## 7) Resumen corto

- Sí: Python 3.10 + pip.
- Opcional: PyInstaller para crear `.exe`.
- No: `make` no hace falta en Windows.
- Recomendado: ejecutar `wizard` para flujo guiado.
