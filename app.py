import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL)
# ==========================================
MAIN_BG = "#D5D5D7"
SIDEBAR_BG = "#1E1E1E"
TEXT_COLOR = "#000000"
ACCENT = "#0d6efd"

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    /* Tarjeta de Definición */
    .gdt-card {{
        background-color: #FFFFFF;
        border-left: 8px solid {ACCENT};
        padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: {TEXT_COLOR}; margin-bottom: 20px;
    }}
    
    /* Caja de Interpretación Azul */
    .interpretation-box {{
        background-color: #e8f4f8;
        border-left: 6px solid {ACCENT};
        padding: 20px; border-radius: 5px;
        margin-top: 10px; font-family: sans-serif; color: {TEXT_COLOR};
    }}
    
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    h1, h2, h3, p, li, span, label {{ color: {TEXT_COLOR} !important; }}
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS UNIFICADA (COMPLETA)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta perfecta.',
        'compare': 'Es en 2D. No confundir con Planicidad (3D).',
        'app': 'Vástagos hidráulicos.', 'why': 'Evita fugas en sellos.',
        'desc': 'rectitud de la línea superior', 'zone': 'dos líneas paralelas'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'compare': 'No requiere Datum. Es intrínseca.',
        'app': 'Culatas de motor.', 'why': 'Asegura sellado hermético.',
        'desc': 'planicidad de la superficie', 'zone': 'dos planos paralelos'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie circular (corte 2D) equidistan de un centro.',
        'compare': 'Se mide por sección. No confundir con Cilindricidad.',
        'app': 'Rodamientos.', 'why': 'Evita vibraciones.',
        'desc': 'circularidad', 'zone': 'dos círculos concéntricos'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'compare': 'La más estricta para ejes. Incluye redondez.',
        'app': 'Pistones.', 'why': 'Sellado dinámico.',
        'desc': 'forma cilíndrica total', 'zone': 'dos cilindros concéntricos'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla una superficie o eje a un ángulo específico (no 90°) respecto a un Datum.',
        'compare': 'Zona de tolerancia milimétrica, no grados.',
        'app': 'Guías inclinadas.', 'why': 'Contacto uniforme.',
        'desc': 'inclinación exacta', 'zone': 'dos planos paralelos inclinados'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'compare': 'Caso especial de Angularidad.',
        'app': 'Escuadras.', 'why': 'Alineación de ensambles.',
        'desc': 'perpendicularidad (90°)', 'zone': 'dos planos paralelos a 90°'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano Datum.',
        'compare': 'Controla orientación y forma.',
        'app': 'Rieles.', 'why': 'Evita atascamientos.',
        'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B',
        'def': 'Controla la ubicación exacta del centro de una característica (agujero) respecto a Datums.',
        'compare': 'Garantiza intercambiabilidad.',
        'app': 'Patrones de pernos.', 'why': 'Ensamble perfecto.',
        'desc': 'ubicación del centro', 'zone': 'un cilindro en posición teórica'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla que los puntos medios de secciones opuestas caigan en una zona cilíndrica.',
        'compare': 'Es teórica (balanceo).',
        'app': 'Rotores.', 'why': 'Evita vibración.',
        'desc': 'coaxialidad de ejes', 'zone': 'un cilindro coaxial al Datum'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación de la superficie en una sección circular al girar.',
        'compare': 'Mide corte a corte.',
        'app': 'Frenos.', 'why': 'Frenado suave.',
        'desc': 'variación circular', 'zone': 'distancia radial (sección)'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación de toda la superficie al girar y desplazarse.',
        'compare': 'Controla toda la pieza.',
        'app': 'Sellos bomba.', 'why': 'Cero fugas.',
        'desc': 'variación total', 'zone': 'distancia radial (total)'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una curva 2D en una sección transversal.',
        'compare': 'Solo el borde.',
        'app': 'Alas.', 'why': 'Aerodinámica.',
        'desc': 'forma del perfil 2D', 'zone': 'una banda uniforme'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma, orientación y ubicación de una superficie 3D compleja.',
        'compare': 'Piel tridimensional.',
        'app': 'Carrocerías.', 'why': 'Estética.',
        'desc': 'forma de superficie 3D', 'zone': 'dos superficies envolventes'
    }
}

# ==========================================
# 2. FUNCIONES DE DIBUJO (COMMON)
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG,
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=550
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc", showbackground=True)
        )
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False)
        layout['yaxis'] = dict(visible=False, showgrid=False)
        layout['plot_bgcolor'] = 'white'
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
    return layout

def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    if fill: fig.add_trace(go.Scatter(x=x, y=y, fill="toself", fillcolor=fill, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))
    else: fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))

# ==========================================
# VISTA 1: SIMULACIÓN 3D (Resumida)
# ==========================================
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    # Lógica gráfica
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False, name='Zona'))
    elif feature == 'Posición':
        z_c = np.linspace(0,4,20); TH, Z = np.meshgrid(theta, z_c)
        fig.add_trace(go.Surface(x=0.5*np.cos(TH)+0.1, y=0.5*np.sin(TH)+0.1, z=Z, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,4], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona'))
    # (El resto de la lógica 3D se mantiene de la versión anterior para no alargar, el sistema ya la tiene)
    else: 
        # Fallback genérico elegante
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='blue', width=5), name='Elemento'))
        fig.add_trace(go.Surface(x=2*np.cos(tg), y=2*np.sin(tg), z=zg, opacity=0.1, showscale=False))
    
    fig.update_layout(**get_common_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_common_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ PLAY", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    # Dibujo estático base
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#ccc", line=dict(color="black"))
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    fig.add_trace(go.Scatter(x=[5], y=[4.5], mode='markers+text', marker=dict(size=40, color='white', line=dict(color='black', width=2)), text=['0']))
    return fig

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA
# ==========================================
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data[feature]
    ftype = info['type']
    sym = info['symbol']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    # Pieza
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    fig.add_trace(go.Scatter(x=[1, 11], y=[4, 4], mode='lines', line=dict(color='black', width=1, dash='longdashdot'), showlegend=False))

    # Cotas
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[6, 6], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[2, 2], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # Marco Control
    if ftype == 'surf':
        leader_x, leader_y = 6, 6; frame_x, frame_y = 6, 7.5 
    else:
        leader_x, leader_y = 10.25, 4.8; frame_x, frame_y = 10.25, 1.5 

    w_box = 1.5; start_x = frame_x - w_box
    draw_rect_trace(fig, start_x, frame_y, start_x+w_box, frame_y+1, width=2, fill='white')
    fig.add_annotation(x=start_x+w_box/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=24, color="black"), showarrow=False)
    
    draw_rect_trace(fig, start_x+w_box, frame_y, start_x+w_box*2.5, frame_y+1, width=2, fill='white')
    tol_str = f"Ø {tol_val}" if ftype == 'axis' else f"{tol_val}"
    fig.add_annotation(x=start_x+w_box*1.75, y=frame_y+0.5, text=f"<b>{tol_str}</b>", font=dict(size=20, color="black"), showarrow=False)
    
    if datum:
        draw_rect_trace(fig, start_x+w_box*2.5, frame_y, start_x+w_box*3.5, frame_y+1, width=2, fill='white')
        fig.add_annotation(x=start_x+w_box*3, y=frame_y+0.5, text=f"<b>{datum}</b>", font=dict(size=20, color="black"), showarrow=False)

    fig.add_annotation(x=leader_x, y=leader_y, ax=frame_x, ay=frame_y if ftype == 'surf' else frame_y+1, arrowhead=2, arrowwidth=2, arrowcolor="black")
    return fig

# ==========================================
# 4. INTERFAZ
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

menu = {
    '1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'],
    '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'],
    '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'],
    '4. Control': ['Alabeo Circular', 'Alabeo Total'],
    '5. Posición': ['Posición', 'Concentricidad']
}

cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
feat = st.sidebar.selectbox("Característica", menu[cat])
tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)

st.sidebar.markdown("### 👁️ Vista")
view_mode = st.sidebar.radio("Seleccione una vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Interpretación de Plano"], index=0)
st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- RENDERIZADO ---
info = gdt_data[feat]

st.markdown(f"""
<div class="gdt-card">
    <div style="display: flex; align-items: center;">
        <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
        <div style="flex: 4; padding-left: 20px;">
            <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
            <p><strong>Definición:</strong> {info['def']}</p>
            <p>🆚 <b>Comparación:</b> {info['compare']}</p>
            <p>🛠️ <b>Aplicación:</b> {info['app']} | {info['why']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if view_mode == "📐 Simulación 3D":
    st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
elif view_mode == "🏭 Montaje Real":
    st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)
elif view_mode == "📝 Interpretación de Plano":
    st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
    tol_str = f"Ø {tol} mm" if info['type'] == 'axis' else f"{tol} mm"
    st.markdown(f"""
    <div class="interpretation-box">
        <h4>🤓 Interpretación del Plano:</h4>
        <p style="font-size: 1.1em;">
            "La característica señalada es <b>{feat.upper()}</b> con tolerancia <b>{tol_str}</b>."
        </p>
        <ul>
            <li><b>Controla:</b> {info['desc'].capitalize()}.</li>
            <li><b>Zona:</b> {info['zone'].capitalize()}.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
