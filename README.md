# GD-T-Manufacturing-
GD&amp;T

## Ejecutar la app localmente

Recomendado: usar un entorno virtual con Python 3.11.

Pasos rápidos (PowerShell):

```powershell
cd 'D:\Laboratorio\GD-T-Manufacturing-'
# (recrear el venv si es necesario)
python3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

Si `streamlit` no se encuentra en el PATH, ejecutar `python -m streamlit run app.py`.

## Añadir símbolos para características

Coloca imágenes en la carpeta `Docs/` con nombre `simbolo_<caracteristica>.<ext>` donde `<caracteristica>` es el nombre de la característica en minúsculas y espacios reemplazados por guiones bajos. Ejemplos que ya existen en el repositorio:

- `Docs/simbolo_rectitud.svg`
- `Docs/simbolo_planicidad.svg`

Se soportan extensiones: `.png`, `.svg`, `.jpg`, `.jpeg`.

Si no se encuentra una imagen, la app mostrará un SVG de fallback con el nombre de la característica.

## Notas

- Si la instalación falla por compilación de paquetes nativos (ej. `pyarrow`), preferible usar Python 3.11 o instalar CMake y Visual Studio Build Tools en Windows.

