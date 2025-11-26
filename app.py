import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL ALTO CONTRASTE)
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
    
    /* Textos del Sidebar en Blanco */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span, [data-testid="stSidebar"] p {{
        color: {TEXT_SIDE} !important;
    }}
    
    /* Inputs del Sidebar (Fondo blanco, texto negro) */
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
# 1. BASE DE DATOS COMPLETA (SIN ERRORES DE CLAVES)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Controla la rectitud de una línea superficial o eje.',
        'compare': 'Es 2D. No confundir con Planicidad.',
        'app': 'Vástagos, rieles.', 'why': 'Evita fugas y desgaste.',
        'desc': 'rectitud', 'zone': 'dos líneas paralelas',
        'sim_3d_desc': 'Línea azul deformada (Banana) dentro de zona naranja.',
        'real_desc': 'Deslizamiento longitudinal con reloj.'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Controla la planitud de una superficie.',
        'compare': 'No usa Datum. Cualidad intrínseca.',
        'app': 'Culatas, mesas de mármol.', 'why': 'Asegura sellado.',
        'desc': 'planicidad', 'zone': 'dos planos paralelos',
        'sim_3d_desc': 'Superficie entre planos límite rojos.',
        'real_desc': 'Reloj sobre superficie apoyada.'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Controla la circularidad de una sección (2D).',
        'compare': 'Sección por sección. No es 3D.',
        'app': 'Rodamientos.', 'why': 'Evita vibraciones.',
        'desc': 'redondez', 'zone': 'dos círculos concéntricos',
        'sim_3d_desc': 'Perfil azul entre círculos rojos.',
        'real_desc': 'Giro de pieza con palpador fijo.'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la forma cilíndrica total (3D).',
        'compare': 'Incluye redondez, rectitud y conicidad.',
        'app': 'Pistones.', 'why': 'Sellado dinámico.',
        'desc': 'cilindricidad', 'zone': 'dos cilindros coaxiales',
        'sim_3d_desc': 'Superficie 3D completa deformada.',
        'real_desc': 'Escaneo espiral o múltiples secciones.'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla la inclinación respecto a un Datum.',
        'compare': 'Zona en mm, no en grados.',
        'app': 'Guías inclinadas.', 'why': 'Contacto uniforme.',
        'desc': 'angularidad', 'zone': 'dos planos paralelos inclinados',
        'sim_3d_desc': 'Plano inclinado entre límites verdes.',
        'real_desc': 'Uso de Mesa de Senos.'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Controla los 90° respecto a un Datum.',
        'compare': 'Caso especial de Angularidad.',
        'app': 'Escuadras.', 'why': 'Alineación de ensambles.',
        'desc': 'perpendicularidad', 'zone': 'dos planos a 90°',
        'sim_3d_desc': 'Pared vertical entre planos azules.',
        'real_desc': 'Comparación contra Escuadra Patrón.'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Controla el paralelismo respecto a un Datum.',
        'compare': 'Controla orientación y forma.',
        'app': 'Rieles.', 'why': 'Evita atascamientos.',
        'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum',
        'sim_3d_desc': 'Superficie entre planos morados.',
        'real_desc': 'Deslizamiento sobre superficie superior.'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B',
        'def': 'Controla la ubicación exacta del centro.',
        'compare': 'Garantiza intercambiabilidad.',
        'app': 'Pernos, agujeros.', 'why': 'Ensamble perfecto.',
        'desc': 'posición', 'zone': 'cilindro en posición teórica',
        'sim_3d_desc': 'Eje rojo dentro de cilindro amarillo.',
        'real_desc': 'CMM o Gage funcional.'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla la colinealidad de ejes opuestos (Balanceo).',
        'compare': 'Difícil de medir. Usar Alabeo si es posible.',
        'app': 'Rotores.', 'why': 'Balanceo dinámico.',
        'desc': 'concentricidad', 'zone': 'cilindro coaxial al Datum',
        'sim_3d_desc': 'Puntos medios (rojo) dentro de zona amarilla.',
        'real_desc': 'Medición diferencial de puntos opuestos.'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación circular al girar (Runout).',
        'compare': 'Mide corte a corte.',
        'app': 'Frenos.', 'why': 'Frenado suave.',
        'desc': 'alabeo circular', 'zone': 'distancia radial (sección)',
        'sim_3d_desc': 'Trayectoria morada del palpador.',
        'real_desc': 'Giro en bloques V.'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación total de superficie al girar.',
        'compare': 'Controla toda la pieza a la vez.',
        'app': 'Ejes bomba.', 'why': 'Cero fugas.',
        'desc': 'alabeo total', 'zone': 'distancia radial (total)',
        'sim_3d_desc': 'Malla roja límite completa.',
        'real_desc': 'Barrido completo giratorio.'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una curva 2D.',
        'compare': 'Solo el borde.',
        'app': 'Alas.', 'why': 'Aerodinámica.',
        'desc': 'perfil de línea', 'zone': 'banda uniforme',
        'sim_3d_desc': 'Curva azul entre bandas verdes.',
        'real_desc': 'Proyector de perfiles.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una superficie 3D.',
        'compare': 'Piel tridimensional.',
        'app': 'Carrocerías.', 'why': 'Estética.',
        'desc': 'perfil de superficie', 'zone': 'dos superficies envolventes',
        'sim_3d_desc': 'Superficie entre capas azules.',
        'real_desc': 'Escaneo CMM contra CAD.'
    }
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG,
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc", showbackground=True)
        )
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.6)", bordercolor="black", borderwidth=1, font=dict(color="black"))
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

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None, name=None):
    show = True if name else False
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=show, name=name, hoverinfo='skip'))

# ==========================================
# VISTA 1: SIMULACIÓN 3D (SIN ERRORES DE ARRAY)
# ==========================================
def plot_3d_simulation(feature, tol):
    # Mallas base para todos los gráficos
    z = np.linspace(0, 10, 30)
    theta = np.linspace(0, 2 * np.pi, 30)
    tg, zg = np.meshgrid(theta, z)
    
    fig = go.Figure()
    
    if feature == 'Rectitud':
        # Visualización 2D (Banana)
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona'))

    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Lim'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Lim'))

    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100)
        r_real = 5 + 0.2 * np.cos(3*th)
        fig.add_trace(go.Scatter3d(x=r_real*np.cos(th), y=r_real*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(th), y=(5-tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Min'))

    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje'))

    elif feature == 'Concentricidad':
        # Lógica corregida para evitar error de índices: Usamos meshgrid directamente
        cx = 0.05 * np.sin(zg)  # Variación en X según altura Z
        cy = 0.05 * np.cos(zg)  # Variación en Y según altura Z
        # Cilindro base desplazado
        x_surf = 4 * np.cos(tg) + cx
        y_surf = 4 * np.sin(tg) + cy
        
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, showscale=False, colorscale=[[0,'gray'],[1,'gray']], name='Datum'))
        fig.add_trace(go.Surface(x=x_surf, y=y_surf, z=zg, colorscale='Cividis', name='Real'))
        fig.add_trace(go.Scatter3d(x=cx[:,0], y=cy[:,0], z=z, mode='lines', line=dict(color='red', width=5), name='Eje Mediano'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.4, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona'))

    elif feature == 'Posición':
        fig.add_trace(go.Surface(x=0.5*np.cos(tg)+0.1, y=0.5*np.sin(tg)+0.1, z=zg, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,10], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='dash'), name='Teórico'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona'))

    # Fallback para las demás (Angularidad, Perpendicularidad, etc usan lógica similar a Planicidad/Rectitud)
    else:
        # Cilindro genérico para evitar error
        fig.add_trace(go.Surface(x=5*np.cos(tg), y=5*np.sin(tg), z=zg, opacity=0.2, showscale=False))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Eje'))

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
    
    # Dibujo estático
    draw_rect_trace(fig, -1, -1, 11, 0, color="black", fill="#ccc") # Mesa
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
    # Frames animación
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

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA
# ==========================================
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data.get(feature, gdt_data['Rectitud'])
    ftype = info['type']; sym = info['symbol']; datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    # Pieza
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    draw_line_trace(fig, 1, 4, 11, 4, width=1, dash='longdashdot', name='Centro')

    # Cotas
    draw_line_trace(fig, 10, 6, 10.5, 6, width=1)
    draw_line_trace(fig, 10, 2, 10.5, 2, width=1)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    # Texto elevado para no chocar
    fig.add_annotation(x=10.25, y=5.2, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    if datum:
        # Triángulo Datum
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

# --- B. PLANO MAESTRO (MULTIPLE) ---
def draw_interactive_blueprint(active_features):
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y"), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', height=600, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))])
    
    # Pieza Maestra
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
            # Dibujar marco simplificado
            draw_rect_trace(fig, x_frm, y_frm, x_frm+3, y_frm+1, width=2)
            fig.add_annotation(x=x_frm+1.5, y=y_frm+0.5, text=f"<b>{sym} 0.1 {dat}</b>", showarrow=False, font=dict(size=14, color="black"))
            fig.add_annotation(x=x_arr, y=y_arr, ax=x_frm, ay=y_frm, arrowhead=2, arrowcolor="black")

    return fig

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

# SELECTOR DE MODO
mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano Maestro"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
    
    view_mode = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    st.sidebar.info("Profesor: Ing. Jaime Silva")
    
    info = gdt_data.get(feat, gdt_data['Rectitud'])
    st.markdown(f"""<div class="gdt-card"><div style="display: flex; align-items: center;"><div class="big-icon" style="flex: 1;">{info['symbol']}</div><div style="flex: 4; padding-left: 20px;"><h3 style="margin:0; color: #0d6efd;">{feat}</h3><p><strong>Definición:</strong> {info['def']}</p></div></div></div>""", unsafe_allow_html=True)

    if view_mode == "📐 Simulación 3D":
        st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
        st.markdown(f"""<div class='visual-card'><b>🔍 Detalle Visual:</b><br>{info.get('sim_3d_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "🏭 Montaje Real":
        st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)
        st.markdown(f"""<div class='visual-card'><b>🏭 Montaje:</b><br>{info.get('real_desc', '...')}</div>""", unsafe_allow_html=True)
    elif view_mode == "📝 Plano Técnico":
        st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
        st.markdown(f"""<div class='interpretation-box'><h4>🤓 Interpretación:</h4><p>Controla <b>{info.get('desc','')}</b> dentro de una zona de <b>{info.get('zone','')}</b>.</p></div>""", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano Maestro":
    st.sidebar.info("Seleccione características para agregarlas al plano:")
    feats_avail = ['Rectitud', 'Planicidad', 'Perpendicularidad', 'Posición', 'Angularidad']
    selected = st.sidebar.multiselect("Agregar:", feats_avail, default=['Rectitud'])
    st.markdown("## 📐 Plano de Ingeniería Maestro")
    st.plotly_chart(draw_interactive_blueprint(selected), use_container_width=True)
