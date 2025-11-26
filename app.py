import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL ESTABLE)
# ==========================================
MAIN_BG = "#D5D5D7"      # Gris Acero
SIDEBAR_BG = "#1E1E1E"   # Negro Carbón
CARD_BG = "#FFFFFF"      # Blanco Puro
TEXT_COLOR = "#000000"   # Negro
TEXT_SIDE = "#FFFFFF"    # Blanco
ACCENT = "#0d6efd"       # Azul Ingeniería

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    
    /* Textos del Sidebar */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {{
        color: {TEXT_SIDE} !important;
    }}
    
    /* Corrección para Inputs del Sidebar */
    div[data-baseweb="select"] > div {{ background-color: white; color: black; }}
    div[data-baseweb="select"] span {{ color: black !important; }}
    
    /* Tarjetas */
    .gdt-card {{
        background-color: {CARD_BG};
        border-left: 8px solid {ACCENT};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}
    
    .visual-card {{
        background-color: #f1f3f5; border: 1px solid #ccc;
        padding: 15px; border-radius: 8px; color: {TEXT_COLOR};
        font-size: 0.95em; margin-top: 10px;
    }}

    .interpretation-box {{
        background-color: #e8f4f8; border-left: 6px solid {ACCENT};
        padding: 20px; border-radius: 5px; margin-top: 10px;
        font-family: sans-serif; color: {TEXT_COLOR};
    }}
    
    .tech-text {{ font-family: 'Courier New', monospace; font-weight: bold; }}
    
    /* Forzar texto negro en área principal */
    .main h1, .main h2, .main h3, .main p, .main li, .main span {{
        color: {TEXT_COLOR} !important;
    }}
    
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS COMPLETA
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Controla la rectitud de una línea superficial o eje.',
        'desc': 'la rectitud de la línea superior', 'zone': 'dos líneas paralelas',
        'sim_3d_desc': '🔵 <b>Eje Real:</b> Línea curvada (Banana).<br>🟠 <b>Zona:</b> Cilindro de tolerancia.',
        'real_desc': 'Deslizamiento longitudinal con reloj.'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Controla la planitud de una superficie.',
        'desc': 'la planicidad de la superficie', 'zone': 'dos planos paralelos',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Mapa de error.<br>🔴 <b>Límites:</b> Planos superior e inferior.',
        'real_desc': 'Barrido completo de la superficie.'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Controla la circularidad (2D).',
        'desc': 'la circularidad', 'zone': 'dos círculos concéntricos',
        'sim_3d_desc': '🔵 <b>Perfil:</b> Aro deformado.<br>🔴 <b>Límites:</b> Círculos concéntricos.',
        'real_desc': 'Giro de pieza con palpador fijo.'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la forma cilíndrica (3D).',
        'desc': 'la cilindricidad', 'zone': 'dos cilindros coaxiales',
        'sim_3d_desc': '🌈 <b>Superficie 3D:</b> Deformada.<br>🔴 <b>Límites:</b> Mallas cilíndricas.',
        'real_desc': 'Escaneo espiral o múltiple.'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla ángulo respecto a Datum.',
        'desc': 'la angularidad', 'zone': 'dos planos inclinados',
        'sim_3d_desc': '🌈 <b>Plano:</b> Inclinado.<br>🟢 <b>Límites:</b> Planos verdes.',
        'real_desc': 'Uso de Mesa de Senos.'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Controla 90° respecto a Datum.',
        'desc': 'la perpendicularidad', 'zone': 'dos planos a 90°',
        'sim_3d_desc': '🌈 <b>Pared:</b> Vertical.<br>🔵 <b>Límites:</b> Planos azules.',
        'real_desc': 'Comparación contra Escuadra.'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Controla paralelismo a Datum.',
        'desc': 'el paralelismo', 'zone': 'dos planos paralelos al Datum',
        'sim_3d_desc': '🟣 <b>Límites:</b> Planos morados paralelos.',
        'real_desc': 'Deslizamiento sobre cara superior.'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B',
        'def': 'Controla ubicación exacta.',
        'desc': 'la posición del centro', 'zone': 'cilindro en posición teórica',
        'sim_3d_desc': '🔴 <b>Eje Rojo:</b> Real.<br>🟡 <b>Cilindro:</b> Tolerancia.',
        'real_desc': 'CMM o Gage funcional.'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla eje mediano.',
        'desc': 'la concentricidad', 'zone': 'cilindro coaxial',
        'sim_3d_desc': '🔴 <b>Puntos:</b> Centros medianos.<br>🟡 <b>Zona:</b> Tolerancia.',
        'real_desc': 'Medición diferencial.'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación circular al girar.',
        'desc': 'el alabeo circular', 'zone': 'distancia radial (sección)',
        'sim_3d_desc': '🟣 <b>Línea:</b> Trayectoria medida.',
        'real_desc': 'Giro en bloques V.'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación total al girar.',
        'desc': 'el alabeo total', 'zone': 'distancia radial (total)',
        'sim_3d_desc': '🔴 <b>Mallas:</b> Límites totales.',
        'real_desc': 'Barrido completo.'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Forma de línea 2D.',
        'desc': 'el perfil de línea', 'zone': 'banda uniforme',
        'sim_3d_desc': '🔵 <b>Curva:</b> Real.<br>🟢 <b>Banda:</b> Tolerancia.',
        'real_desc': 'Proyector de perfiles.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Forma de superficie 3D.',
        'desc': 'el perfil de superficie', 'zone': 'dos superficies envolventes',
        'sim_3d_desc': '🔵 <b>Capas:</b> Envolventes límite.',
        'real_desc': 'Escaneo CMM.'
    }
}

# ==========================================
# 2. HERRAMIENTAS GRÁFICAS
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        font=dict(color='black'), margin=dict(l=20, r=20, t=50, b=20), height=600, autosize=True
    )
    if is_3d:
        layout.update({
            'paper_bgcolor': MAIN_BG, 'plot_bgcolor': MAIN_BG,
            'scene': dict(
                aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
                xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
                yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
                zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc")
            ),
            'legend': dict(bgcolor="rgba(255,255,255,0.8)", font=dict(color="black"), yanchor="top", y=0.95, xanchor="right", x=0.99)
        })
    else:
        layout.update({'paper_bgcolor': 'white', 'plot_bgcolor': 'white', 'xaxis': dict(visible=False, showgrid=False, range=[-1, 14]), 'yaxis': dict(visible=False, showgrid=False, range=[-2, 9]), 'shapes': [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]})
    return layout

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=False, hoverinfo='skip'))

def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    fill_val = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=fill_val, fillcolor=fill, line=dict(color=color, width=width), mode='lines', showlegend=False, hoverinfo='skip'))

def draw_leader_arrow(fig, x_tail, y_tail, x_head, y_head):
    # Dibuja una línea sólida con punta de flecha manual para asegurar visibilidad
    fig.add_trace(go.Scatter(x=[x_tail, x_head], y=[y_tail, y_head], mode='lines+markers', 
                             marker=dict(symbol='arrow', size=10, angleref='previous'),
                             line=dict(color='black', width=2), showlegend=False, hoverinfo='skip'))

def plot_control_frame_manual(fig, x, y, sym, tol, datum):
    w, h = 1.5, 1.0
    # Caja 1
    draw_rect_trace(fig, x, y, x+w, y+h, width=2)
    fig.add_annotation(x=x+w/2, y=y+h/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=20, color="black"))
    # Caja 2
    draw_rect_trace(fig, x+w, y, x+w*2.5, y+h, width=2)
    fig.add_annotation(x=x+w*1.75, y=y+h/2, text=f"<b>{tol}</b>", showarrow=False, font=dict(size=16, color="black"))
    # Caja 3
    if datum:
        draw_rect_trace(fig, x+w*2.5, y, x+w*3.5, y+h, width=2)
        fig.add_annotation(x=x+w*3, y=y+h/2, text=f"<b>{datum}</b>", showarrow=False, font=dict(size=16, color="black"))
        return x+w*3.5
    return x+w*2.5

# ==========================================
# VISTA 1: SIMULACIÓN 3D
# ==========================================
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False, name='Zona'))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Sup'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Inf'))
    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100); r = 5 + 0.2 * np.cos(3*th)
        fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(th), y=(5-tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Min'))
    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje'))
    elif feature == 'Concentricidad':
        cx = 0.05 * np.sin(z); cy = 0.05 * np.cos(z)
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, colorscale=[[0,'gray'],[1,'gray']], showscale=False, name='Datum'))
        fig.add_trace(go.Surface(x=(4+0.05*np.sin(zg))*np.cos(tg), y=(4+0.05*np.sin(zg))*np.sin(tg), z=zg, colorscale='Cividis', name='Real'))
        fig.add_trace(go.Scatter3d(x=cx, y=cy, z=z, mode='lines', line=dict(color='red', width=5), name='Eje Mediano')) # CORREGIDO 1D
    elif feature == 'Posición':
        fig.add_trace(go.Surface(x=0.5*np.cos(tg)+0.1, y=0.5*np.sin(tg)+0.1, z=zg, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,10], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='dash'), name='Teórico'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'yellow'],[1,'yellow']], showscale=False, name='Zona'))
    else:
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Eje'))
        fig.add_trace(go.Surface(x=2*np.cos(tg), y=2*np.sin(tg), z=zg, opacity=0.1, showscale=False))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ PLAY", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    draw_rect_trace(fig, -1, -1, 11, 0, color="black", fill="#ccc") # Mesa
    
    # Base de animación
    frames = []
    for i in range(50):
        x = i/5; y = 1.5+0.2*np.sin(x)
        frames.append(go.Frame(data=[
            go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50))),
            go.Scatter(x=[x, x], y=[y, y+3], mode="lines", line=dict(color="#444", width=4)),
            go.Scatter(x=[x], y=[y+3], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2))),
            go.Scatter(x=[x, x+0.5*np.cos(i)], y=[y+3, y+3+0.5*np.sin(i)], mode="lines", line=dict(color="red", width=2))
        ]))
    
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    fig.add_trace(go.Scatter(x=[0,0], y=[1.5, 4.5], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
    fig.add_trace(go.Scatter(x=[0], y=[4.5], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
    fig.add_trace(go.Scatter(x=[0,0.5], y=[4.5, 4.5], mode="lines", line=dict(color="red", width=2), name="Aguja"))
    
    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA (INDIVIDUAL)
# ==========================================
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data.get(feature, gdt_data['Rectitud'])
    ftype = info['type']; sym = info['symbol']; datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    # Pieza
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    draw_line_trace(fig, 1, 4, 11, 4, width=1, dash='longdashdot')

    # Cotas
    draw_line_trace(fig, 10, 6, 10.5, 6, width=1)
    draw_line_trace(fig, 10, 2, 10.5, 2, width=1)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5.5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # Marco Control y Líder Manual
    if ftype == 'surf':
        frame_x, frame_y = 6, 7.5 
        # Línea líder manual: Desde la superficie (6, 6) hasta la caja (6, 7.5)
        draw_line_trace(fig, 6, 6, 6, 7.5, width=1)
        # Flecha manual en la punta
        fig.add_annotation(x=6, y=6, ax=6, ay=6.5, arrowhead=2, arrowcolor="black")
    else:
        frame_x, frame_y = 10.25, 1.5 
        draw_line_trace(fig, 10.25, 4.5, 10.25, 2, width=1) # Línea conectora

    w_box = 1.5; start_x = frame_x - w_box
    plot_control_frame_manual(fig, start_x, frame_y, sym, f"Ø {tol_val}" if ftype == 'axis' else str(tol_val), datum)
    
    return fig

# ==========================================
# VISTA 4: CONSTRUCTOR DE PLANO MAESTRO
# ==========================================
def draw_interactive_blueprint(active_features):
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y"), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', height=600, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))])
    
    draw_rect_trace(fig, 1, 1, 11, 3, width=3) # Base
    draw_rect_trace(fig, 2, 3, 4, 7, width=3) # Torreta
    draw_line_trace(fig, 3, 4, 3, 6, width=1, dash='longdashdot', name='Eje')
    
    # Datums
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20, ax=0)
    
    locs = {
        'Rectitud': (7, 1.5, 7, 0.5, ''), 'Posición': (3, 7, 3, 8, 'A B'), 'Planicidad': (6, 3.5, 6, 5.5, ''), 
        'Perpendicularidad': (1.5, 5, 0.5, 5, 'A'), 'Angularidad': (10, 4, 11, 5, 'A')
    }

    for feat in active_features:
        if feat in locs:
            x_arr, y_arr, x_frm, y_frm, dat = locs[feat]
            sym = gdt_data[feat]['symbol']
            
            # Líder manual
            draw_line_trace(fig, x_arr, y_arr, x_frm, y_frm, width=1)
            fig.add_annotation(x=x_arr, y=y_arr, ax=x_arr + (x_frm-x_arr)*0.1, ay=y_arr+(y_frm-y_arr)*0.1, arrowhead=2, arrowcolor="black")
            
            plot_control_frame_manual(fig, x_frm, y_frm, sym, "0.1", dat)

    return fig

# ==========================================
# 5. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano Maestro"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
    
    view_mode = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Interpretación de Plano"])
    st.sidebar.info("Profesor: Ing. Jaime Silva")
    
    info = gdt_data.get(feat, gdt_data['Rectitud'])
    chart_key = f"{feat}_{view_mode}_{tol}"

    # En 3D y Real NO mostramos la tarjeta de definición grande para no estorbar
    if view_mode == "📝 Interpretación de Plano":
         st.markdown(f"""<div class="gdt-card"><div style="display: flex; align-items: center;"><div class="big-icon" style="flex: 1;">{info['symbol']}</div><div style="flex: 4; padding-left: 20px;"><h3 style="margin:0; color: #0d6efd;">{feat}</h3><p><b>Definición:</b> {info['def']}</p></div></div></div>""", unsafe_allow_html=True)

    if view_mode == "📐 Simulación 3D":
        st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True, key=chart_key)
        st.markdown(f"""<div class='visual-card'><b>🔍 Detalle Visual:</b><br>{info.get('sim_3d_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "🏭 Montaje Real":
        st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True, key=chart_key)
        st.markdown(f"""<div class='visual-card'><b>🏭 Montaje:</b><br>{info.get('real_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "📝 Interpretación de Plano":
        st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=chart_key)
        st.markdown(f"""<div class='interpretation-box'><h4>🤓 Interpretación:</h4><p>Controla <b>{info.get('desc','')}</b> dentro de una zona de <b>{info.get('zone','')}</b>.</p></div>""", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano Maestro":
    st.sidebar.info("Seleccione características para agregarlas al plano:")
    feats_avail = ['Rectitud', 'Planicidad', 'Perpendicularidad', 'Posición', 'Angularidad']
    selected = st.sidebar.multiselect("Agregar:", feats_avail, default=['Rectitud'])
    st.markdown("## 📐 Plano de Ingeniería Maestro")
    st.plotly_chart(draw_interactive_blueprint(selected), use_container_width=True)
