# 🎓 GD&T Manufacturing Training Platform

> **Plataforma educativa interactiva para aprendizaje de Dimensionamiento y Tolerancias Geométricas (GD&T) según estándar ASME Y14.5-2018**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=matplotlib&logoColor=white)](https://matplotlib.org)

---

## 🌟 Características Principales

### ✅ **13 Características GD&T Completas**
Implementación total de las 5 categorías del estándar ASME Y14.5-2018:

| Categoría | Características | Estado |
|-----------|----------------|--------|
| **🔷 Forma** | Rectitud, Planicidad, Redondez, Cilindricidad | ✅ 100% |
| **🔶 Perfil** | Perfil de Línea, Perfil de Superficie | ✅ 100% |
| **🔸 Orientación** | Angularidad, Perpendicularidad, Paralelismo | ✅ 100% |
| **🔹 Ubicación** | Posición, Concentricidad | ✅ 100% |
| **🔺 Oscilación** | Oscilación Circular, Oscilación Total | ✅ 100% |

### 🎨 **4 Visualizaciones por Característica (52 Total)**

1. **📊 Simulación 3D Interactiva** - Geometría real vs zona de tolerancia con Plotly
2. **🔧 Montaje Real de Medición** - Sistema completo con comparador de diálogo
3. **📐 Zona de Tolerancia** - Vista 2D/3D de límites y área permitida
4. **📄 Plano Técnico Real** - Dibujo estándar con FCF, cotas y símbolos GD&T

### 🎓 **Sistema Pedagógico Completo**

- **52 textos "¿Qué ves?"** personalizados por vista
- **52 leyendas visuales** dinámicas
- **13 diferenciadores clave** para evitar confusiones
- **Tabla informativa** con definición, aplicación, medición y puntos clave
- **Slider interactivo** de tolerancia en tiempo real

---

## 🚀 Inicio Rápido

### **Opción 1: Streamlit Cloud (Recomendado)**
Accede directamente a la aplicación en línea (sin instalación):
```
https://share.streamlit.io/jaimedon5/gd-t-manufacturing-/main/app.py
```

### **Opción 2: Ejecución Local**

#### Requisitos
- Python 3.11+
- pip

#### Instalación
```powershell
# Clonar repositorio
git clone https://github.com/Jaimedon5/GD-T-Manufacturing-.git
cd GD-T-Manufacturing-

# Crear entorno virtual
python3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt

# Ejecutar aplicación
python -m streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

---

## 📚 Guía de Uso

### **1. Seleccionar Categoría**
En la barra lateral, elige una de las 5 categorías (Forma, Perfil, Orientación, Ubicación, Oscilación)

### **2. Elegir Característica**
Del menú desplegable, selecciona la característica específica (muestra símbolo GD&T + nombre)

### **3. Ajustar Tolerancia**
Usa el slider para modificar el valor de tolerancia (0.1 - 2.0 mm) y observa cómo cambian las visualizaciones en tiempo real

### **4. Explorar Visualizaciones**
Navega entre las 4 pestañas:
- **Simulación 3D**: Rota e interactúa con geometría 3D
- **Montaje Real**: Observa el setup de medición industrial
- **Zona de Tolerancia**: Comprende límites permitidos
- **Plano Técnico Real**: Aprende notación estándar

### **5. Leer Textos Pedagógicos**
- **Leyenda visual**: Explica elementos gráficos
- **¿Qué ves?**: Guía de interpretación
- **Diferenciador clave**: Evita confusiones

---

## 🎨 Paleta de Colores

```python
🖤 Negro (#000000)      → Geometría estática / contornos
🔴 Rojo (#D00000)       → Valores dinámicos / medidas
💗 Magenta (#e6007e)    → Zonas de tolerancia
💠 Cian (#009fe3)       → Textos explicativos
🔵 Azul (#1e40af)       → Referencias numeradas
🟠 Naranja (orange)     → Límites de tolerancia
```

---

## 📐 Símbolos GD&T Implementados

```
—   Rectitud              ⏥  Planicidad           ○  Redondez
⌭   Cilindricidad         ⌓  Perfil de Línea     ⌒  Perfil de Superficie
∠   Angularidad           ⊥  Perpendicularidad   ∥  Paralelismo
⊕   Posición              ◎  Concentricidad      ↗  Oscilación Circular
↗↗  Oscilación Total
```

---

## 🏗️ Arquitectura Técnica

### **Stack Tecnológico**
- **Frontend**: Streamlit (UI reactiva)
- **Visualización 3D**: Plotly (gráficos interactivos)
- **Planos Técnicos**: Matplotlib (dibujo vectorial)
- **Cálculos**: NumPy (arrays numéricos)

### **Estructura del Código**
```python
app.py (1600+ líneas)
├── get_gd_data()                    # Base de datos de 13 características
├── show_info_card()                 # Tabla informativa HTML
├── show_legend()                    # Leyendas dinámicas
│
├── Visualizaciones 3D (Plotly)
│   ├── plot_3d_rectitud()
│   ├── plot_3d_planicidad()
│   ├── plot_3d_redondez()
│   ├── plot_3d_cilindricidad()
│   ├── plot_3d_perfil()
│   ├── plot_3d_orientacion()
│   ├── plot_3d_ubicacion()
│   └── plot_3d_oscilacion()
│
├── Montajes Reales (Plotly)
│   ├── plot_real_rectitud()
│   └── plot_generic_montaje()
│
├── Zonas de Tolerancia (Plotly)
│   ├── plot_blueprint_rectitud()
│   └── plot_generic_zona()
│
└── Planos Técnicos (Matplotlib)
    ├── plot_technical_drawing_rectitud()
    └── plot_generic_plano_tecnico()
```

---

## 📊 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| **Características GD&T** | 13 |
| **Visualizaciones Totales** | 52 |
| **Textos Pedagógicos** | 52 |
| **Leyendas Visuales** | 52 |
| **Líneas de Código** | 1600+ |
| **Funciones de Visualización** | 16 |
| **Categorías ASME Y14.5-2018** | 5 |

---

## 🎯 Casos de Uso

### **Educación**
- Cursos universitarios de manufactura
- Capacitación técnica en metrología
- Entrenamiento en diseño mecánico

### **Industria**
- Onboarding de nuevos ingenieros
- Repaso rápido de estándares GD&T
- Referencia visual para inspectores

### **Certificación**
- Preparación para exámenes ASME
- Material de estudio GD&T
- Práctica con tolerancias variables

---

## 🔧 Personalización

### **Agregar Símbolos Personalizados**
Coloca imágenes en `Docs/` con formato:
```
Docs/simbolo_<característica>.svg
```

Ejemplo:
```
Docs/simbolo_rectitud.svg
Docs/simbolo_planicidad.png
```

Formatos soportados: `.png`, `.svg`, `.jpg`, `.jpeg`

### **Modificar Tolerancias por Defecto**
En `app.py`, línea ~1420:
```python
tol = st.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
```

---

## 📖 Documentación Adicional

- 📄 [**IMPLEMENTACION_COMPLETA.md**](./IMPLEMENTACION_COMPLETA.md) - Documentación técnica detallada
- 📘 [**ASME Y14.5-2018**](https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing) - Estándar oficial GD&T

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Para contribuir:

1. Fork el repositorio
2. Crea una rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👨‍💻 Autor

**Jaime Domínguez**
- GitHub: [@Jaimedon5](https://github.com/Jaimedon5)

---

## 🙏 Agradecimientos

- **ASME** - Por el estándar Y14.5-2018
- **Streamlit** - Por la plataforma de desarrollo web
- **Plotly** - Por visualizaciones 3D interactivas
- **Matplotlib** - Por dibujo técnico de precisión

---

## 📞 Soporte

Para reportar bugs o solicitar características:
- 🐛 [Abrir Issue](https://github.com/Jaimedon5/GD-T-Manufacturing-/issues)
- 💬 [Discusiones](https://github.com/Jaimedon5/GD-T-Manufacturing-/discussions)

---

## 🔮 Roadmap Futuro

- [ ] Animaciones 3D de procesos de medición
- [ ] Modo Quiz interactivo con evaluación
- [ ] Exportación de planos a PDF/DXF
- [ ] Casos de estudio industriales reales
- [ ] Multi-idioma (EN/ES)
- [ ] Comparación lado a lado de características
- [ ] Integración con modelos CAD (STEP/IGES)
- [ ] Generador automático de FCF

---

<div align="center">

**🎓 Aprende GD&T de manera visual e interactiva**

[🚀 Ver Demo](https://share.streamlit.io/jaimedon5/gd-t-manufacturing-/main/app.py) • [📖 Documentación](./IMPLEMENTACION_COMPLETA.md) • [🐛 Reportar Bug](https://github.com/Jaimedon5/GD-T-Manufacturing-/issues)

---

⭐ **Si este proyecto te ayudó, dale una estrella!** ⭐

</div>


