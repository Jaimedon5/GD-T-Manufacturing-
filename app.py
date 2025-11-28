## (Línea eliminada: remanente de código viejo que causaba error de sintaxis)
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# ===================== CONFIGURACIÓN GENERAL =====================
st.set_page_config(layout="wide", page_title="GD&T Master Lab - Nueva Versión")

# ===================== ESTILOS Y LEYENDAS =====================
st.markdown("""
<style>
    /* Fondo general gris neutro y textos oscuros */
    .stApp {
        background-color: #e5e7eb !important;
        color: #222 !important;
    }
    /* Sidebar fondo gris más oscuro */
    [data-testid="stSidebar"] {
        background-color: #23272e !important;
    }
    [data-testid="stSidebar"] * {
        color: #f3f4f6 !important;
    }
    /* Recuadro de leyenda */
    .legend-box {
        background: #f3f4f6;
        border-left: 6px solid #1976d2;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 18px;
        font-size: 1.05em;
        color: #23272e;
    }
    /* Recuadro de información */
    .info-card {
        background: #f3f4f6;
        border-left: 8px solid #004B87;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        color: #23272e;
    }
    /* Recuadro pedagógico */
    .pedagogic-box {
        background: #e0e7ef;
        border: 1px solid #2196f3;
        border-left: 6px solid #2196f3;
        padding: 15px;
        border-radius: 4px;
        color: #0d47a1;
        font-family: 'Courier New', monospace;
        margin-top: 15px;
    }
    .category-label {
        font-weight: bold;
        color: #004B87;
        background: #e0e7ef;
        border-radius: 6px;
        padding: 2px 8px;
        margin-right: 8px;
    }
    /* Mejorar contraste de títulos */
    h1, h2, h3, h4, h5, h6 {
        color: #23272e !important;
    }
    /* Mejorar contraste de inputs y sliders */
    .stSlider > div[data-baseweb="slider"] {
        background: #d1d5db !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================== BASE DE DATOS DE CARACTERÍSTICAS =====================
# Incluye puntos clave y diferenciadores pedagógicos
def get_gd_data():
    return {
        'Rectitud': {
            'symbol': '⏤',
            'def': 'Condición donde un elemento lineal es una línea recta.',
            'app': 'Vástagos, ejes largos, rieles.',
            'key_points': [
                'Solo controla la línea central o generatriz, no la forma completa.',
                'No requiere datum.',
                'Se mide con comparador o proyector de perfiles.'
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

def show_info_card(feature):
    info = GD_DATA[feature]
    st.markdown(f"""
    <div class="info-card">
        <h3 style="margin:0; color: #004B87;">{feature} {info['symbol']}</h3>
        <p><b>Definición:</b> {info['def']}</p>
        <p><b>Aplicación:</b> {info['app']}</p>
        <ul>
            <b>Puntos clave para identificar:</b>
            {''.join([f'<li>{pt}</li>' for pt in info['key_points']])}
        </ul>
        <p style="color:#1976d2;"><b>¿Cómo NO confundirlo?</b> {info['diff']}</p>
    </div>
    """, unsafe_allow_html=True)

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
st.sidebar.title("Menú GD&T Pedagógico")
main_mode = st.sidebar.radio("Modo:", ["Análisis Individual", "Constructor de Plano"])

if main_mode == "Análisis Individual":
    menu = list(GD_DATA.keys())
    cat = st.sidebar.selectbox("Característica", menu)
    st.markdown("<div style='color:#f3f4f6; font-size:13px; margin-bottom:0px;'>Tolerancia (mm)</div>", unsafe_allow_html=True)
    tol = st.sidebar.slider("", 0.1, 2.0, 0.5, key="slider_tol")
    st.markdown(f"<div style='color:#f3f4f6; background:transparent; display:inline-block; padding:2px 10px; margin-top:4px; margin-bottom:10px; font-size:15px; font-weight:bold;'>Valor: {tol:.2f} mm</div>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Mejora el color del texto del slider de tolerancia */
    .stSlider .css-1gv0vcd, .stSlider .css-1gv0vcd span, .stSlider .css-1gv0vcd label {
        color: #f3f4f6 !important;
        font-weight: bold;
    }
    .stSlider .css-14xtw13 {
        color: #f3f4f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Zona de Tolerancia", "Plano Técnico Real"])

    # Leyenda y guía visual SIEMPRE visible
    show_legend(cat)

    # Tarjeta de información enriquecida
    show_info_card(cat)

    # Simulación y explicación pedagógica
    if view == "Simulación 3D":
        if cat == 'Rectitud':
            st.plotly_chart(plot_3d_rectitud(tol), use_container_width=True)
            st.markdown(f"<div class='pedagogic-box'><b>¿Qué ves?</b> El eje azul representa el elemento real, el cilindro naranja la zona de tolerancia. Si el eje azul permanece dentro del cilindro, la pieza cumple rectitud.</div>", unsafe_allow_html=True)
        # ...agrega el resto de características aquí...
    elif view == "Montaje Real":
        if cat == 'Rectitud':
            st.plotly_chart(plot_real_rectitud(), use_container_width=True)
            st.markdown(f"<div class='pedagogic-box'><b>¿Qué ves?</b> El palpador rojo recorre el eje real, mientras la escala a la derecha muestra la lectura del comparador dial. Así se observa la variación de rectitud en la práctica, igual que en un laboratorio real.</div>", unsafe_allow_html=True)
        # ...agrega el resto de características aquí...
    elif view == "Zona de Tolerancia":
        if cat == 'Rectitud':
            st.plotly_chart(plot_blueprint_rectitud(tol), use_container_width=True)
            st.markdown(f"<div class='pedagogic-box'><b>Interpretación:</b> La rectitud se controla dentro de una zona delimitada por dos líneas paralelas separadas {tol} mm. El eje real debe permanecer entre ellas.</div>", unsafe_allow_html=True)
        # ...agrega el resto de características aquí...
    elif view == "Plano Técnico Real":
        st.markdown("### Plano Técnico Real")
        st.info("Esta función mostrará un plano técnico realista con cotas, líneas de referencia y anotaciones, como en los ejemplos del PDF. (En desarrollo)")
        # Ejemplo base: plano técnico simple
        fig = go.Figure()
        # Cuerpo principal
        fig.add_shape(type='rect', x0=1, x1=9, y0=1, y1=3, line=dict(color='#222', width=2))
        # Línea de cota
        fig.add_shape(type='line', x0=1, x1=9, y0=0.7, y1=0.7, line=dict(color='#1976d2', width=2, dash='dot'))
        # Flechas
        fig.add_annotation(x=1, y=0.7, ax=1.5, ay=0.7, showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2)
        fig.add_annotation(x=9, y=0.7, ax=8.5, ay=0.7, showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2)
        # Texto de cota
        fig.add_annotation(x=5, y=0.5, text="8.00", showarrow=False, font=dict(size=16, color='#1976d2'))
        # Etiqueta
        fig.add_annotation(x=5, y=3.2, text="Rectitud", showarrow=False, font=dict(size=16, color='#222'))
        fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0), height=350,
            paper_bgcolor='#e5e7eb', plot_bgcolor='#e5e7eb',
            xaxis=dict(visible=False, range=[0,10]),
            yaxis=dict(visible=False, range=[0,4])
        )
        st.plotly_chart(fig, use_container_width=True)

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
            st.markdown(f"<div class='pedagogic-box'>Cota {idx+1}: Zona de tolerancia de rectitud de {tol} mm</div>", unsafe_allow_html=True)
    else:
        st.warning("Agrega al menos una cota para ver el plano.")
## Así cada simulación será independiente, robusta y pedagógica.
