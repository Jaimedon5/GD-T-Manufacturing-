import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (CORREGIDOS PARA MENÚS)
# ==========================================
MAIN_BG = "#F0F2F6"
SIDEBAR_BG = "#1E1E1E"
TEXT_COLOR = "#000000"
ACCENT_COLOR = "#0d6efd"

st.markdown(f"""
<style>
    /* Fondo Principal */
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    
    /* BARRA LATERAL OSCURA */
    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}
    
    /* TEXTOS DE BARRA LATERAL (Títulos y Etiquetas) -> BLANCO */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown {{
        color: #FFFFFF !important;
    }}
    
    /* CAJAS DE SELECCIÓN (INPUTS) -> TEXTO NEGRO PARA QUE SE VEA */
    div[data-baseweb="select"] > div {{
        background-color: white;
        color: black;
    }}
    div[data-baseweb="select"] span {{
        color: black !important;
    }}
    
    /* Tarjeta de Definición */
    .gdt-card {{
        background-color: #FFFFFF;
        border-left: 8px solid {ACCENT_COLOR};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}
    
    /* Caja de Interpretación Azul */
    .interpretation-box {{
        background-color: #e8f4f8;
        border-left: 6px solid #0d6efd;
        padding: 20px;
        border-radius: 5px;
        margin-top: 10px;
        font-family: sans-serif;
        color: #000000;
    }}
    
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    /* Forzar texto negro en área principal */
    .main h1, .main h2, .main h3, .main p, .main li, .main span {{ color: {TEXT_COLOR} !important; }}
    
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS
# ==========================================
gdt_data = {
    'Rectitud': {'symbol': '⏤', 'type': 'surf', 'datum': False, 'def': 'Controla la rectitud de una línea.', 'sim_3d_desc': 'Línea azul deformada (2D) dentro de cilindro de tolerancia.', 'real_desc': 'Deslizamiento longitudinal con reloj.', 'zone': 'dos líneas paralelas'},
    'Planicidad': {'symbol': '⏥', 'type': 'surf', 'datum': False, 'def': 'Controla la planitud de una superficie.', 'sim_3d_desc': 'Superficie entre dos planos paralelos.', 'real_desc': 'Reloj sobre superficie apoyada.', 'zone': 'dos planos paralelos'},
    'Redondez': {'symbol': '○', 'type': 'axis', 'datum': False, 'def': 'Controla la circularidad en una sección transversal (2D).', 'sim_3d_desc': 'Un solo anillo deformado entre dos círculos concéntricos.', 'real_desc': 'Giro de pieza con palpador fijo.', 'zone': 'dos círculos concéntricos'},
    'Cilindricidad': {'symbol': '⌭', 'type': 'axis', 'datum': False, 'def': 'Controla la forma cilíndrica completa (3D).', 'sim_3d_desc': 'Superficie completa 3D deformada.', 'real_desc': 'Escaneo espiral.', 'zone': 'dos cilindros concéntricos'},
    'Angularidad': {'symbol': '∠', 'type': 'surf', 'datum': 'A', 'def': 'Controla ángulo respecto a Datum.', 'sim_3d_desc': 'Plano inclinado entre límites verdes.', 'real_desc': 'Uso de Mesa de Senos.', 'zone': 'dos planos paralelos inclinados'},
    'Perpendicularidad': {'symbol': '⟂', 'type': 'surf', 'datum': 'A', 'def': 'Controla 90° respecto a Datum.', 'sim_3d_desc': 'Pared vertical entre planos azules.', 'real_desc': 'Comparación contra Escuadra Patrón.', 'zone': 'dos planos paralelos a 90°'},
    'Paralelismo': {'symbol': '∥', 'type': 'surf', 'datum': 'A', 'def': 'Controla paralelismo a Datum.', 'sim_3d_desc': 'Superficie entre planos morados.', 'real_desc': 'Deslizamiento sobre superficie superior.', 'zone': 'dos planos paralelos al Datum'},
    'Posición': {'symbol': '⌖', 'type': 'axis', 'datum': 'A B', 'def': 'Controla ubicación exacta.', 'sim_3d_desc': 'Eje rojo dentro de cilindro amarillo.', 'real_desc': 'CMM o Gage funcional.', 'zone': 'un cilindro en posición teórica'},
    'Concentricidad': {'symbol': '◎', 'type': 'axis', 'datum': 'A', 'def': 'Controla eje mediano.', 'sim_3d_desc': 'Puntos medios dentro de zona cilíndrica.', 'real_desc': 'Medición diferencial compleja.', 'zone': 'un cilindro coaxial al Datum'},
    'Alabeo Circular': {'symbol': '↗', 'type': 'axis', 'datum': 'A-B', 'def': 'Variación circular al girar.', 'sim_3d_desc': 'Trayectoria morada del palpador.', 'real_desc': 'Giro en bloques V.', 'zone': 'distancia radial (sección)'},
    'Alabeo Total': {'symbol': '⌰', 'type': 'axis', 'datum': 'A-B', 'def': 'Variación total al girar.', 'sim_3d_desc': 'Malla roja límite.', 'real_desc': 'Barrido completo giratorio.', 'zone': 'distancia radial (total)'},
    'Perfil de una línea': {'symbol': '⌒', 'type': 'surf', 'datum': False, 'def': 'Forma de línea 2D.', 'sim_3d_desc': 'Curva azul entre bandas verdes.', 'real_desc': 'Proyector de perfiles.', 'zone': 'una banda uniforme'},
    'Perfil de una superficie': {'symbol': '⌓', 'type': 'surf', 'datum': False, 'def': 'Forma de superficie 3D.', 'sim_3d_desc': 'Superficie entre capas azules.', 'real_desc': 'Escaneo CMM contra CAD.', 'zone': 'dos superficies envolventes'}
}

# ==========================================
# 2. FUNCIONES GRÁFICAS
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(title=dict(text=title, font=dict(size=18, color='black')), paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG, font=dict(color='black'), margin=dict(l=20, r=20, t=50, b=20), height=600)
    if is_3d:
        layout['scene'] = dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6), camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)), xaxis=dict(visible=False, backgroundcolor=MAIN_BG), yaxis=dict(visible=False, backgroundcolor=MAIN_BG), zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc", showbackground=True))
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.5)", font=dict(color="black"))
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False); layout['yaxis'] = dict(visible=False, showgrid=False)
        layout['plot_bgcolor'] = 'white'
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
    return layout

def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    if fill: fig.add_trace(go.Scatter(x=x, y=y, fill="toself", fillcolor=fill, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))
    else: fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))

# --- VISTA 1: SIMULACIÓN 3D ---
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    if feature == 'Rectitud':
        # Banana Shape (Línea curva simple)
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False, name='Zona'))

    elif feature == 'Redondez':
        # CORRECCIÓN: UN SOLO ARO 2D, NO SUPERFICIE
        th = np.linspace(0, 2*np.pi, 100)
        r_real = 5 + 0.2 * np.cos(3*th)
        # Anillo real
        fig.add_trace(go.Scatter3d(x=r_real*np.cos(th), y=r_real*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=8), name='Perfil Real'))
        # Limites
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(th), y=(5-tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Min'))
        # Ajustar vista para ver desde arriba
        fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2)))

    elif feature == 'Cilindricidad':
        # CORRECCIÓN: SUPERFICIE COMPLETA 3D
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Sup. Real'))
        # Limites (Mallas)
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Límites', showlegend=True))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.full_like(theta, 10), line=dict(color='red'), showlegend=False))
        
    # ... (Resto de geometrías usando la lógica corregida de V13) ...
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False))
    elif feature == 'Posición':
        z_c = np.linspace(0,4,20); TH, Z = np.meshgrid(theta, z_c)
        fig.add_trace(go.Surface(x=0.5*np.cos(TH)+0.1, y=0.5*np.sin(TH)+0.1, z=Z, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,4], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona'))
    else:
        # Fallback para las demás
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Ejemplo Genérico'))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# --- VISTA 2: MONTAJE REAL ---
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ REPRODUCIR", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#ccc", line=dict(color="black"))
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
    frames = []
    for i in range(50):
        x = i/5; y = 1.5+0.2*np.sin(x)
        frames.append(go.Frame(data=[
            go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50))), 
            go.Scatter(x=[x, x], y=[y, y+3], mode="lines", line=dict(color="#444", width=4)), 
            go.Scatter(x=[x], y=[y+3], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2))), 
            go.Scatter(x=[x, x+0.5*np.cos(i)], y=[y+3, y+3+0.5*np.sin(i)], mode="lines", line=dict(color="red", width=2))
        ]))
    
    fig.add_trace(go.Scatter(x=[0,0], y=[1.5, 4.5], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
    fig.add_trace(go.Scatter(x=[0], y=[4.5], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
    fig.add_trace(go.Scatter(x=[0,0.5], y=[4.5, 4.5], mode="lines", line=dict(color="red", width=2), name="Aguja"))
    fig.frames = frames
    return fig

# --- VISTA 3: PLANO DE INGENIERÍA ---
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data.get(feature, gdt_data['Rectitud'])
    ftype = info['type']; sym = info['symbol']; datum = info.get('datum', None)
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    fig.add_trace(go.Scatter(x=[1, 11], y=[4, 4], mode='lines', line=dict(color='black', width=1, dash='longdashdot'), showlegend=False))
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[6, 6], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[2, 2], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5.5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    if ftype == 'surf': leader_x, leader_y = 6, 6; frame_x, frame_y = 6, 7.5 
    else: leader_x, leader_y = 10.25, 4.8; frame_x, frame_y = 10.25, 1.5 

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
# 4. INTERFAZ DE USUARIO
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

info = gdt_data.get(feat, {'symbol': '?', 'def': '...'})

st.markdown(f"""
<div class="gdt-card">
    <div style="display: flex; align-items: center;">
        <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
        <div style="flex: 4; padding-left: 20px;">
            <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
            <p><strong>Definición:</strong> {info['def']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if view_mode == "📐 Simulación 3D":
    st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🔍 Detalle Visual:</b><br>{info.get('sim_3d_desc', '...')}</div>""", unsafe_allow_html=True)
elif view_mode == "🏭 Montaje Real":
    st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🏭 Montaje:</b><br>{info.get('real_desc', '...')}</div>""", unsafe_allow_html=True)
elif view_mode == "📝 Interpretación de Plano":
    st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
    tol_str = f"Ø {tol} mm" if info.get('type', 'surf') == 'axis' else f"{tol} mm"
    st.markdown(f"""<div class='interpretation-box'><h4>🤓 Interpretación del Plano:</h4><p>Controla <b>{info.get('desc','')}</b> con tolerancia <b>{tol_str}</b>.</p></div>""", unsafe_allow_html=True)
