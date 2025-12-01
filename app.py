## (Línea eliminada: remanente de código viejo que causaba error de sintaxis)
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import streamlit.components.v1 as components
import numpy as np
import time

# ===================== CONFIGURACIÓN GENERAL =====================
st.set_page_config(layout="wide", page_title="GD&T Master Lab - Nueva Versión")

# ===================== ESTILOS Y LEYENDAS =====================
st.markdown("""<style>
.symbol-box{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:120px;width:120px;margin:0 auto;margin-top:18px;margin-bottom:18px;padding:8px;overflow:hidden;}
.symbol-box img,.symbol-box svg{max-width:100%;max-height:100%;height:auto;width:auto;display:block;}
.legend-stack{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}
.legend-box,.pedagogic-box{margin-bottom:0!important;}
.stApp{background-color:#e5e7eb!important;color:#222!important;}
[data-testid="stSidebar"]{background-color:#23272e!important;}
[data-testid="stSidebar"] *{color:#f3f4f6!important;}
.legend-box{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}
.info-card{background:#f3f4f6;border-left:8px solid #004B87;padding:16px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:200px;overflow:hidden;display:flex;gap:16px;}
.pedagogic-box{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:'Courier New',monospace;margin-top:15px;}
.category-label{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}
h1,h2,h3,h4,h5,h6{color:#23272e!important;}
</style>""", unsafe_allow_html=True)
ST_SYMBOL_SIZE = 200
st.markdown(f"""<style>.symbol-box{{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:{ST_SYMBOL_SIZE}px;width:{ST_SYMBOL_SIZE}px;margin:0 auto;margin-top:18px;margin-bottom:18px;}}.legend-stack{{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}}.legend-box,.pedagogic-box{{margin-bottom:0!important;}}.stApp{{background-color:#e5e7eb!important;color:#222!important;}}[data-testid=\"stSidebar\"]{{background-color:#23272e!important;}}[data-testid=\"stSidebar\"] *{{color:#f3f4f6!important;}}.legend-box{{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}}.info-card{{background:#f3f4f6;border-left:8px solid #004B87;padding:12px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:{ST_SYMBOL_SIZE}px;overflow:auto;display:flex;align-items:flex-start;}}.info-card table{{line-height:1.3;}}.pedagogic-box{{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:\'Courier New\',monospace;margin-top:15px;}}.category-label{{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}}h1,h2,h3,h4,h5,h6{{color:#23272e!important;}}</style>""", unsafe_allow_html=True)

# ===================== BASE DE DATOS DE CARACTERÍSTICAS =====================
# Incluye puntos clave y diferenciadores pedagógicos
def get_gd_data():
    return {
        'Rectitud': {
            'symbol': '⏤',
            'def': 'Condición donde un elemento lineal es una línea recta.',
            'zona_tol': 'Líneas paralelas, dónde debe estar el elemento de superficie.',
            'app': 'Vástagos, ejes largos, rieles.',
            'medicion': 'comparador o proyector de perfiles.',
            'key_points': [
                'Solo controla la línea central o generatriz, no la forma completa.',
                'No requiere datum.'
            ],
            'diff': 'No confundir con planicidad: la rectitud es 1D, la planicidad es 2D.',
            'pedagogic': 'Rectitud evalúa si un eje o borde es perfectamente recto, útil para piezas largas.',
            'legend': 'Línea azul: eje real. Cilindro naranja: zona de tolerancia.',
        },
        'Planicidad': {
            'symbol': '⏥',
            'def': 'Todos los puntos de una superficie están en un solo plano.',
            'app': 'Mesas de granito, culatas, sellos.',
            'key_points': [
                'Controla toda la superficie, no solo una línea.',
                'No requiere datum.',
                'Se mide con palpador o láser.'
            ],
            'diff': 'No confundir con rectitud: planicidad es para superficies, rectitud para líneas.',
            'pedagogic': 'Planicidad asegura que una superficie no tenga picos o valles fuera de tolerancia.',
            'legend': 'Superficie verde: real. Planos rojos: límites de tolerancia.'
        },
        # ...agrega el resto de características siguiendo el PDF...
    }

GD_DATA = get_gd_data()

# ===================== FUNCIONES DE LEYENDA Y EXPLICACIÓN PEDAGÓGICA =====================
def show_legend(feature):
    info = GD_DATA[feature]
    st.markdown(f"""
    <div class="legend-box">
        <b>Leyenda visual:</b> {info['legend']}<br>
        <b>Diferenciador clave:</b> {info['diff']}
    </div>
    """, unsafe_allow_html=True)
    # Asegura que la info-card tenga altura fija y el .sim-box la misma apariencia
    try:
        current_box = ST_SYMBOL_SIZE
    except NameError:
        current_box = 200
    st.markdown(f"""<style>
    .symbol-box{{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:{current_box}px;width:{current_box}px;margin:0 auto;margin-top:18px;margin-bottom:18px;padding:12px;overflow:hidden;}}
    .symbol-box img,.symbol-box svg{{max-width:100%;max-height:100%;height:auto;width:auto;display:block;}}
    .legend-stack{{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}}
    .legend-box,.pedagogic-box{{margin-bottom:0!important;}}
    .stApp{{background-color:#e5e7eb!important;color:#222!important;}}
    [data-testid="stSidebar"]{{background-color:#23272e!important;}}
    [data-testid="stSidebar"] *{{color:#f3f4f6!important;}}
    .legend-box{{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}}
    .info-card{{background:#f3f4f6;border-left:8px solid #004B87;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:200px;overflow:auto;}}
    .pedagogic-box{{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:'Courier New',monospace;margin-top:15px;}}
    .category-label{{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}}
    h1,h2,h3,h4,h5,h6{{color:#23272e!important;}}
    .sim-box{{border:2.5px solid #23272e;border-radius:8px;padding:10px;background:#fff;margin:0;}}
    </style>""", unsafe_allow_html=True)
def show_info_card(feature):
    info = GD_DATA[feature]
    # Construir puntos clave como texto simple
    puntos_html = '<br>'.join([f'• {pt}' for pt in info['key_points']])
    # HTML en formato tabla: fila 1 título, fila 2 encabezados, fila 3 datos
    html = f"""
    <div class="info-card">
        <table style="width:100%;border-collapse:collapse;font-size:0.85em;">
            <tr>
                <th colspan="6" style="text-align:left;padding:8px;font-size:1.1em;color:#004B87;border-bottom:2px solid #004B87;">{feature}</th>
            </tr>
            <tr style="background:#e0e7ef;">
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Definición</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Zona de tolerancia</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Aplicación</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Medición</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Puntos clave para identificar</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;">¿Cómo NO confundirlo?</th>
            </tr>
            <tr>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info['def']}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info.get('zona_tol', 'N/A')}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info['app']}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info.get('medicion', 'N/A')}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{puntos_html}</td>
                <td style="padding:8px;vertical-align:top;color:#1976d2;">{info['diff']}</td>
            </tr>
        </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def get_symbol_image_path(feature):
    """Devuelve la ruta relativa a la imagen del símbolo para la característica.
    Busca archivos en `Docs/simbolo_<slug>.png`. Si no existe, devuelve None.
    """
    slug = feature.replace(' ', '_').lower()
    import os
    # Buscar en varios formatos: png, svg, jpg, jpeg
    for ext in ('png', 'svg', 'jpg', 'jpeg'):
        candidate = os.path.join('Docs', f'simbolo_{slug}.{ext}')
        if os.path.exists(candidate):
            return candidate.replace('\\', '/')
    return None

# ===================== SIMULACIONES =====================
def plot_3d_rectitud(tol):
    z = np.linspace(0, 10, 35)
    x_r = 0.4 * np.sin(z*0.5)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=x_r, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje real'))
    # Zona de tolerancia
    theta = np.linspace(0, 2*np.pi, 35)
    tg, zg = np.meshgrid(theta, z)
    fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', name='Zona de tolerancia'))
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0), height=500,
        scene=dict(
            xaxis=dict(visible=False, backgroundcolor='#e5e7eb'),
            yaxis=dict(visible=False, backgroundcolor='#e5e7eb'),
            zaxis=dict(visible=True, backgroundcolor='#e5e7eb'),
            bgcolor='#e5e7eb'
        ),
        paper_bgcolor='#e5e7eb', plot_bgcolor='#e5e7eb'
    )
    return fig

def plot_real_rectitud():
    # Simulación pedagógica: comparador dial recorriendo el eje
    x = np.linspace(0, 10, 100)
    y = 0.4 * np.sin(x*0.5)
    fig = go.Figure()
    # Eje real
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='blue', width=4), name='Eje real'))
    # Base de soporte
    fig.add_shape(type='rect', x0=0, x1=10, y0=-1, y1=-0.7, fillcolor='#888', line_color='#444', layer='below')
    # Comparador dial (palpador)
    dial_x = [x[0]]
    dial_y = [y[0]]
    fig.add_trace(go.Scatter(x=dial_x, y=dial_y, mode='markers', marker=dict(size=22, color='red', symbol='circle'), name='Palpador'))
    # Escala de medición
    fig.add_shape(type='line', x0=10.5, x1=10.5, y0=-0.5, y1=0.5, line=dict(color='#222', width=3))
    for tick in np.linspace(-0.5, 0.5, 11):
        fig.add_shape(type='line', x0=10.5, x1=10.7, y0=tick, y1=tick, line=dict(color='#222', width=2))
    # Lectura animada
    frames = []
    for i in range(0, 100, 2):
        frames.append(go.Frame(data=[
            go.Scatter(x=[x[i]], y=[y[i]], mode='markers', marker=dict(size=22, color='red', symbol='circle')),
            go.Scatter(x=[10.5], y=[y[i]], mode='markers', marker=dict(size=16, color='green', symbol='line-ns-open'))
        ]))
    # Marcador de lectura inicial
    fig.add_trace(go.Scatter(x=[10.5], y=[y[0]], mode='markers', marker=dict(size=16, color='green', symbol='line-ns-open'), name='Lectura'))
    fig.frames = frames
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0), height=400,
        xaxis=dict(range=[-0.5, 11.5], visible=False),
        yaxis=dict(range=[-1.2, 1.2], visible=False),
        updatemenus=[dict(type="buttons", showactive=False, x=0.1, y=0, buttons=[dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])])]
    )
    return fig

def plot_blueprint_rectitud(tol):
    fig = go.Figure()
    # Dibuja área de tolerancia como un rectángulo gris claro
    x = np.linspace(0, 10, 2)
    y1 = tol/2 * np.ones_like(x)
    y2 = -tol/2 * np.ones_like(x)
    fig.add_shape(type='rect', x0=0, x1=10, y0=-tol/2, y1=tol/2, fillcolor='#d1d5db', line=dict(color='#bdbdbd', width=0), layer='below')
    # Líneas de límite de tolerancia
    fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', line=dict(color='#ff9800', width=5), name='Límite sup.'))
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', line=dict(color='#ff9800', width=5), name='Límite inf.'))
    # Eje real
    fig.add_trace(go.Scatter(x=x, y=np.zeros_like(x), mode='lines', line=dict(color='#1976d2', width=4), name='Eje real'))
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0), height=350,
        paper_bgcolor='#e5e7eb', plot_bgcolor='#e5e7eb',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig



# ===================== INTERFAZ PRINCIPAL =====================
st.sidebar.title("Menú GD&T")
main_mode = st.sidebar.radio("Modo:", ["Análisis Individual", "Constructor de Plano"])

if main_mode == "Análisis Individual":
    menu = list(GD_DATA.keys())
    cat = st.sidebar.selectbox("Característica", menu)
    # Símbolo con tamaño fijo (200x200)
    st.sidebar.markdown("<div style='color:#f3f4f6; font-size:13px; margin-bottom:0px;'>Tolerancia (mm)</div>", unsafe_allow_html=True)
    tol = st.sidebar.slider("", 0.1, 2.0, 0.5, key="slider_tol")
    st.sidebar.markdown(f"<div style='color:#fff; background:transparent; display:inline-block; padding:2px 10px; margin-top:4px; margin-bottom:10px; font-size:15px; font-weight:bold;'>Valor: {tol:.2f} mm</div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <style>
    /* Oculta los valores del slider (min, max, actual) */
    .stSlider .css-1aumxhk,
    .stSlider .css-1r6slb0,
    .stSlider .css-14xtw13,
    .stSlider .css-1gv0vcd,
    .stSlider .st-c2,
    .stSlider label[data-testid=\"stWidgetLabel\"] + div > div > div > span {
        display: none !important;
    }
    /* SOLO en el sidebar: fondo oscuro para el slider y contorno oscuro */
    [data-testid=\"stSidebar\"] .stSlider > div[data-baseweb=\"slider\"] {
        background: #23272e !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        border: 1.5px solid #181a1b !important;
    }
    [data-testid=\"stSidebar\"] .stSlider .css-13cymwt, [data-testid=\"stSidebar\"] .stSlider .st-c1, [data-testid=\"stSidebar\"] .stSlider [role=\"slider\"] ~ div > div {
        background: #444 !important;
    }
    [data-testid=\"stSidebar\"] .stSlider label, [data-testid=\"stSidebar\"] .stSlider div, [data-testid=\"stSidebar\"] .stSlider span {
        color: #fff !important;
    }
    [data-testid=\"stSidebar\"] .stSlider .css-1gv0vcd, [data-testid=\"stSidebar\"] .stSlider .css-14xtw13, [data-testid=\"stSidebar\"] .stSlider .css-1r6slb0 {
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Zona de Tolerancia", "Plano Técnico Real"])

    # --- LAYOUT CORREGIDO: SÍMBOLO COMO IMAGEN EN RECUADRO BLANCO CON BORDE NEGRO ---
    # Arriba: símbolo a la izquierda (solo imagen), info-card a la derecha
    # CSS adicional para alinear verticalmente arriba y ajustar spacing
    st.markdown("""<style>
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
    }
    .symbol-box {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    .info-card {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    </style>""", unsafe_allow_html=True)
    top1, top2 = st.columns([1, 5], gap="small")
    with top1:
        # Mostrar la imagen del símbolo según la característica seleccionada.
        img_path = get_symbol_image_path(cat)
        box_px = ST_SYMBOL_SIZE
        if img_path:
            # si es SVG, incrustar el contenido para asegurar renderizado correcto
            if img_path.lower().endswith('.svg'):
                try:
                    with open(img_path, 'r', encoding='utf-8') as f:
                        svg_text = f.read()
                    st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>{svg_text}</div>", unsafe_allow_html=True)
                except Exception:
                    st.image(img_path, width=box_px-20)
            else:
                st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>", unsafe_allow_html=True)
                st.image(img_path, width=box_px-20)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback SVG simple y en negro (sin fondo). Línea centrada para mantener estilo.
            stub_svg = f"<svg viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'>" \
                       f"<line x1='12' y1='60' x2='108' y2='60' stroke='#000' stroke-width='8' stroke-linecap='round'/>" \
                       f"</svg>"
            st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>{stub_svg}</div>", unsafe_allow_html=True)
    with top2:
        show_info_card(cat)

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # Abajo: simulación a la izquierda, leyenda y ¿Qué ves? apilados a la derecha
    bot1, bot2 = st.columns([2.5, 1.5], gap="medium")
    with bot1:
        if view == "Simulación 3D":
            fig = plot_3d_rectitud(tol)
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            sim_html = f"<div class='sim-box'>{html_plot}</div>"
            components.html(sim_html, height=540, scrolling=False)
        elif view == "Montaje Real":
            fig = plot_real_rectitud()
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            sim_html = f"<div class='sim-box'>{html_plot}</div>"
            components.html(sim_html, height=460, scrolling=False)
        elif view == "Zona de Tolerancia":
            fig = plot_blueprint_rectitud(tol)
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            sim_html = f"<div class='sim-box'>{html_plot}</div>"
            components.html(sim_html, height=400, scrolling=False)
        elif view == "Plano Técnico Real":
            st.markdown("### Plano Técnico Real")
            st.info("Esta función mostrará un plano técnico realista con cotas, líneas de referencia y anotaciones, como en los ejemplos del PDF. (En desarrollo)")
            fig = go.Figure()
            fig.add_shape(type='rect', x0=1, x1=9, y0=1, y1=3, line=dict(color='#222', width=2))
            fig.add_shape(type='line', x0=1, x1=9, y0=0.7, y1=0.7, line=dict(color='#1976d2', width=2, dash='dot'))
            fig.add_annotation(x=1, y=0.7, ax=1.5, ay=0.7, showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2)
            fig.add_annotation(x=9, y=0.7, ax=8.5, ay=0.7, showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2)
            fig.add_annotation(x=5, y=0.5, text="8.00", showarrow=False, font=dict(size=16, color='#1976d2'))
            fig.add_annotation(x=5, y=3.2, text="Rectitud", showarrow=False, font=dict(size=16, color='#222'))
            fig.update_layout(
                margin=dict(l=0, r=0, t=40, b=0), height=350,
                paper_bgcolor='#e5e7eb', plot_bgcolor='#e5e7eb',
                xaxis=dict(visible=False, range=[0,10]),
                yaxis=dict(visible=False, range=[0,4])
            )
            html = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            st.markdown("<div class='sim-box'>", unsafe_allow_html=True)
            components.html(html, height=360, scrolling=False)
            st.markdown("</div>", unsafe_allow_html=True)
    with bot2:
        st.markdown("<div class='legend-stack'>", unsafe_allow_html=True)
        show_legend(cat)
        if view == "Simulación 3D":
            st.markdown(f"<div class='pedagogic-box'><b>¿Qué ves?</b> El eje azul representa el elemento real, el cilindro naranja la zona de tolerancia. Si el eje azul permanece dentro del cilindro, la pieza cumple rectitud.</div>", unsafe_allow_html=True)
        elif view == "Montaje Real":
            st.markdown(f"<div class='pedagogic-box'><b>¿Qué ves?</b> El palpador rojo recorre el eje real, mientras la escala a la derecha muestra la lectura del comparador dial. Así se observa la variación de rectitud en la práctica, igual que en un laboratorio real.</div>", unsafe_allow_html=True)
        elif view == "Zona de Tolerancia":
            st.markdown(f"<div class='pedagogic-box'><b>Interpretación:</b> La rectitud se controla dentro de una zona delimitada por dos líneas paralelas separadas {tol} mm. El eje real debe permanecer entre ellas.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif main_mode == "Constructor de Plano":
    st.markdown("## Constructor de Plano Técnico")
    st.info("Agrega cotas y tolerancias para construir un plano técnico completo. Por ahora solo disponible para 'Rectitud'.")
    # Estado de plano (solo para 'Rectitud' por ahora)
    if 'plano_rectitud' not in st.session_state:
        st.session_state['plano_rectitud'] = []
    nueva_tol = st.slider("Tolerancia de rectitud a agregar (mm)", 0.1, 2.0, 0.5)
    if st.button("Agregar cota de rectitud"):
        st.session_state['plano_rectitud'].append(nueva_tol)
    st.markdown("### Vista del plano construido")
    # Mostrar todas las cotas agregadas
    if st.session_state['plano_rectitud']:
        for idx, tol in enumerate(st.session_state['plano_rectitud']):
            st.plotly_chart(plot_blueprint_rectitud(tol), use_container_width=True)
            st.markdown(f"<div class='pedagogic-box'>Cota {idx+1}: Zona de tolerancia de rectitud de {tol:.2f} mm</div>", unsafe_allow_html=True)
    else:
        st.warning("Agrega al menos una cota para ver el plano.")
## Así cada simulación será independiente, robusta y pedagógica.
