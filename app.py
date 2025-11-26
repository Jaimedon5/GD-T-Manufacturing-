import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA "DARK ENGINEERING" FINAL)
# ==========================================
MAIN_BG = "#D5D5D7"      # Gris Acero (Fondo Principal)
SIDEBAR_BG = "#1E1E1E"   # Negro Carbón (Barra Lateral)
CARD_BG = "#FFFFFF"      # Blanco Puro (Tarjetas)
TEXT_COLOR = "#000000"   # Negro (Texto Principal)
TEXT_SIDE = "#FFFFFF"    # Blanco (Texto Lateral)
ACCENT = "#0d6efd"       # Azul Ingeniería

st.markdown(f"""
<style>
    /* FONDO PRINCIPAL */
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    
    /* BARRA LATERAL */
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    
    /* Textos del Sidebar (Blancos) */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{
        color: {TEXT_SIDE} !important;
    }}
    
    /* CORRECCIÓN CRÍTICA: Inputs del Sidebar (Fondo blanco, texto negro) */
    div[data-baseweb="select"] > div {{ background-color: white !important; color: black !important; }}
    div[data-baseweb="select"] span {{ color: black !important; }}
    
    /* TARJETAS DE DEFINICIÓN SUPERIOR */
    .gdt-card {{
        background-color: {CARD_BG};
        border-left: 8px solid {ACCENT};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}

    /* CAJA DE INTERPRETACIÓN DE PLANO (AZUL) */
    .interpretation-box {{
        background-color: #e8f4f8; 
        border-left: 6px solid {ACCENT};
        padding: 20px; 
        border-radius: 5px; 
        margin-top: 15px;
        font-family: sans-serif; 
        color: {TEXT_COLOR};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    /* CAJA DE EXPLICACIÓN VISUAL (GRIS) */
    .visual-card {{
        background-color: #f1f3f5;
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 8px;
        color: {TEXT_COLOR};
        font-size: 0.95em;
        margin-top: 10px;
    }}

    /* TEXTO NEGRO EN ÁREA PRINCIPAL */
    .main h1, .main h2, .main h3, .main p, .main li, .main span, .main label {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* ICONOS */
    .big-icon {{
        font-size: 80px;
        text-align: center;
        font-weight: bold;
        color: {TEXT_COLOR};
        display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    /* MÁRGENES */
    .block-container {{padding-top: 3rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS COMPLETA
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Controla qué tan recta es una línea específica (eje o superficie).',
        'compare': 'Es 2D. No confundir con Planicidad (3D).', 'app': 'Vástagos, rieles.', 'why': 'Evita fugas.',
        'desc': 'la rectitud de la línea superior', 'zone': 'dos líneas paralelas',
        'sim_3d_desc': '🔵 <b>Eje Real:</b> Línea curvada azul.<br>🟠 <b>Zona Tolerancia:</b> Cilindro naranja semitransparente.',
        'real_desc': 'Se desplaza el reloj a lo largo de la pieza. La variación total de la aguja es el error.'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Controla la planitud de una superficie.',
        'compare': 'No usa Datum. Intrínseca.', 'app': 'Culatas, mesas.', 'why': 'Sellado.',
        'desc': 'la planicidad de la superficie', 'zone': 'dos planos paralelos',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Mapa de error.<br>🔴 <b>Límites:</b> Planos superior e inferior.',
        'real_desc': 'El reloj barre toda la superficie. La diferencia entre el punto más alto y más bajo es el error.'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Controla la circularidad de una sección (2D).',
        'compare': 'Sección por sección. No es 3D.', 'app': 'Rodamientos.', 'why': 'Vibración.',
        'desc': 'la circularidad', 'zone': 'dos círculos concéntricos',
        'sim_3d_desc': '🔵 <b>Perfil Azul:</b> Forma real del corte.<br>🔴 <b>Círculos Rojos:</b> Límites coaxiales.',
        'real_desc': 'La pieza gira, el reloj está fijo. Se mide la variación radial.'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la forma cilíndrica total (3D).',
        'compare': 'Incluye redondez, rectitud y conicidad.', 'app': 'Pistones.', 'why': 'Sellado dinámico.',
        'desc': 'la cilindricidad', 'zone': 'dos cilindros coaxiales',
        'sim_3d_desc': '🌈 <b>Superficie 3D:</b> Deformada.<br>🔴 <b>Límites:</b> Mallas cilíndricas.',
        'real_desc': 'Se escanea toda la superficie (espiral o múltiples cortes).'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla la inclinación respecto a un Datum.',
        'compare': 'Zona en mm, no grados.', 'app': 'Guías.', 'why': 'Contacto.',
        'desc': 'la angularidad', 'zone': 'dos planos paralelos inclinados',
        'sim_3d_desc': '🌈 <b>Plano:</b> Superficie inclinada.<br>🟢 <b>Límites:</b> Planos verdes.',
        'real_desc': 'Uso de Mesa de Senos para nivelar y medir variación.'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Controla los 90° respecto a un Datum.',
        'compare': 'Caso especial de Angularidad.', 'app': 'Escuadras.', 'why': 'Alineación.',
        'desc': 'la perpendicularidad', 'zone': 'dos planos a 90°',
        'sim_3d_desc': '🌈 <b>Pared:</b> Superficie real.<br>🔵 <b>Límites:</b> Planos azules.',
        'real_desc': 'Comparación contra una escuadra patrón de granito.'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Controla el paralelismo respecto a un Datum.',
        'compare': 'Orientación y forma.', 'app': 'Rieles.', 'why': 'Atascamiento.',
        'desc': 'el paralelismo', 'zone': 'dos planos paralelos al Datum',
        'sim_3d_desc': '🟣 <b>Límites:</b> Planos morados paralelos.',
        'real_desc': 'Deslizamiento del reloj sobre la cara superior.'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B',
        'def': 'Controla la ubicación exacta del centro.',
        'compare': 'Garantiza ensamble.', 'app': 'Pernos.', 'why': 'Intercambiabilidad.',
        'desc': 'la posición del centro', 'zone': 'cilindro en posición teórica',
        'sim_3d_desc': '🔴 <b>Línea Roja:</b> Eje real del agujero.<br>🟡 <b>Cilindro Amarillo:</b> Zona de tolerancia.',
        'real_desc': 'Verificación con Máquina de Coordenadas (CMM) o Gage funcional.'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla el eje mediano (balanceo).',
        'compare': 'Difícil de medir.', 'app': 'Rotores.', 'why': 'Balanceo.',
        'desc': 'la concentricidad', 'zone': 'cilindro coaxial',
        'sim_3d_desc': '🔴 <b>Puntos Rojos:</b> Centros medianos derivados.<br>🟡 <b>Zona Amarilla:</b> Tolerancia.',
        'real_desc': 'Medición diferencial de puntos opuestos al girar.'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación circular al girar (Runout).',
        'compare': 'Mide corte a corte.', 'app': 'Frenos.', 'why': 'Vibración.',
        'desc': 'el alabeo circular', 'zone': 'distancia radial (sección)',
        'sim_3d_desc': '🟣 <b>Línea Morada:</b> Trayectoria medida.<br>🔴 <b>Líneas Punteadas:</b> Límites.',
        'real_desc': 'Giro de la pieza sobre bloques V con reloj fijo.'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación total al girar.',
        'compare': 'Controla toda la pieza.', 'app': 'Ejes bomba.', 'why': 'Fugas.',
        'desc': 'el alabeo total', 'zone': 'distancia radial (total)',
        'sim_3d_desc': '🔴 <b>Mallas Rojas:</b> Cilindros límite coaxiales.',
        'real_desc': 'Giro de la pieza mientras el reloj se desplaza longitudinalmente.'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Forma de línea 2D.',
        'compare': 'Solo el borde.', 'app': 'Alas.', 'why': 'Aerodinámica.',
        'desc': 'el perfil de línea', 'zone': 'banda uniforme',
        'sim_3d_desc': '🔵 <b>Línea Azul:</b> Perfil real.<br>🟢 <b>Líneas Verdes:</b> Banda de tolerancia.',
        'real_desc': 'Proyector de perfiles con plantilla transparente.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Forma de superficie 3D.',
        'compare': 'Piel tridimensional.', 'app': 'Carrocerías.', 'why': 'Estética.',
        'desc': 'el perfil de superficie', 'zone': 'dos superficies envolventes',
        'sim_3d_desc': '🔵 <b>Capas Azules:</b> Límites envolventes superior e inferior.',
        'real_desc': 'Escaneo de puntos con CMM comparado contra CAD.'
    }
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO (Trazo Seguro)
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG,
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600,
        autosize=True
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc")
        )
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.8)", font=dict(color="black"), yanchor="top", y=0.95, xanchor="right", x=0.99)
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 14])
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 9])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
    return layout

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=False, hoverinfo='skip'))

def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    fill_val = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=fill_val, fillcolor=fill, line=dict(color=color, width=width), mode='lines', showlegend=False, hoverinfo='skip'))

def plot_control_frame_manual(fig, x, y, sym, tol, datum):
    """Dibuja el marco de control usando trazos en lugar de shapes para garantizar visibilidad"""
    w, h = 1.5, 1.0
    # Caja 1
    draw_rect_trace(fig, x, y, x+w, y+h, width=2)
    fig.add_annotation(x=x+w/2, y=y+h/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=24, color="black"))
    # Caja 2
    draw_rect_trace(fig, x+w, y, x+w*2.5, y+h, width=2)
    fig.add_annotation(x=x+w*1.75, y=y+h/2, text=f"<b>{tol}</b>", showarrow=False, font=dict(size=20, color="black"))
    # Caja 3
    if datum:
        draw_rect_trace(fig, x+w*2.5, y, x+w*3.5, y+h, width=2)
        fig.add_annotation(x=x+w*3, y=y+h/2, text=f"<b>{datum}</b>", showarrow=False, font=dict(size=20, color="black"))
        return x+w*3.5
    return x+w*2.5

# ==========================================
# VISTA 1: SIMULACIÓN 3D (ESTABLE)
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
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Lim'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Lim'))
    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje'))
    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100); r = 5 + 0.2 * np.cos(3*th)
        fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(th), y=(5-tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Min'))
    elif feature == 'Posición':
        fig.add_trace(go.Surface(x=0.5*np.cos(tg)+0.1, y=0.5*np.sin(tg)+0.1, z=zg, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,10], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'yellow'],[1,'yellow']], showscale=False, name='Zona'))
    else:
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Eje'))
        fig.add_trace(go.Surface(x=2*np.cos(tg), y=2*np.sin(tg), z=zg, opacity=0.1, showscale=False))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMADO)
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ PLAY", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    draw_rect_trace(fig, -1, -1, 11, 0, color="black", fill="#ccc") # Mesa
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
    # Frames
    frames = []
    for i in range(0, 50, 2):
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

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA (ESTÁTICO CON COTA MANUAL)
# ==========================================
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data.get(feature, gdt_data['Rectitud'])
    ftype = info['type']; sym = info['symbol']; datum = info.get('datum', None)
    
    fig = go.Figure()
    # Fondo blanco para papel
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    # Dibujo de la Pieza
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    draw_line_trace(fig, 1, 4, 11, 4, width=1, dash='longdashdot')

    # Dibujo de Cotas de Tamaño
    draw_line_trace(fig, 10, 6, 10.5, 6, width=1)
    draw_line_trace(fig, 10, 2, 10.5, 2, width=1)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5.5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    # Datum (Si aplica)
    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # Marco de Control y Líder (Manual)
    if ftype == 'surf':
        leader_x, leader_y = 6, 6; frame_x, frame_y = 6, 7.5 
    else:
        leader_x, leader_y = 10.25, 4.8; frame_x, frame_y = 10.25, 1.5 

    w_box = 1.5; start_x = frame_x - w_box
    # Dibujar marco usando la función auxiliar
    plot_control_frame_manual(fig, start_x, frame_y, sym, f"Ø {tol_val}" if ftype=='axis' else str(tol_val), datum)
    
    # Línea líder manual (Trazo sólido)
    draw_line_trace(fig, leader_x, leader_y, frame_x, frame_y, width=2)
    # Flecha en la punta
    fig.add_annotation(x=leader_x, y=leader_y, ax=leader_x + (frame_x-leader_x)*0.1, ay=leader_y + (frame_y-leader_y)*0.1, arrowhead=2, arrowcolor="black")

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
    
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20, ax=0)
    
    locs = {
        'Rectitud': (7, 1.5, 7, 0.5, ''), 'Posición': (3, 7, 3, 8, 'A B'), 'Planicidad': (6, 3.5, 6, 5.5, ''), 
        'Perpendicularidad': (1.5, 5, 0.5, 5, 'A'), 'Angularidad': (10, 4, 11, 5, 'A')
    }

    for feat in active_features:
        if feat in locs:
            x_arr, y_arr, x_frm, y_frm, dat = locs[feat]
            sym = gdt_data[feat]['symbol']
            draw_line_trace(fig, x_arr, y_arr, x_frm, y_frm, width=1)
            fig.add_annotation(x=x_arr, y=y_arr, ax=x_arr + (x_frm-x_arr)*0.1, ay=y_arr+(y_frm-y_arr)*0.1, arrowhead=2, arrowcolor="black")
            plot_control_frame_manual(fig, x_frm, y_frm, sym, "0.1", dat)

    return fig

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

# SELECTOR DE MODO
mode_select = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano Maestro"])
st.sidebar.markdown("---")

if mode_select == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
    
    view_mode = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    st.sidebar.info("Profesor: Ing. Jaime Silva")
    
    info = gdt_data.get(feat, gdt_data['Rectitud'])
    
    # 1. DEFINICIÓN (SIEMPRE VISIBLE EN MODO ANÁLISIS)
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

    # CLAVE ÚNICA PARA ESTABILIDAD
    chart_key = f"{feat}_{view_mode}_{tol}"

    if view_mode == "📐 Simulación 3D":
        st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True, key=chart_key)
        st.markdown(f"""<div class='visual-card'><b>🔍 Detalle Visual:</b><br>{info.get('sim_3d_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "🏭 Montaje Real":
        st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True, key=chart_key)
        st.markdown(f"""<div class='visual-card'><b>🏭 Procedimiento:</b><br>{info.get('real_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "📝 Plano Técnico":
        st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=chart_key)
        tol_str = f"Ø {tol} mm" if info.get('type') == 'axis' else f"{tol} mm"
        st.markdown(f"""<div class='interpretation-box'><h4>🤓 Interpretación del Plano:</h4><p>Controla <b>{info.get('desc','')}</b> dentro de una zona de <b>{info.get('zone','')}</b> de tamaño <b>{tol_str}</b>.</p></div>""", unsafe_allow_html=True)

elif mode_select == "📝 Constructor de Plano Maestro":
    st.sidebar.info("Agregue múltiples cotas al plano:")
    feats_avail = ['Rectitud', 'Planicidad', 'Perpendicularidad', 'Posición', 'Angularidad']
    selected = st.sidebar.multiselect("Agregar:", feats_avail, default=['Rectitud', 'Posición'])
    st.markdown("## 📐 Plano de Ingeniería Maestro")
    st.plotly_chart(draw_interactive_blueprint(selected), use_container_width=True)
