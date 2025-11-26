import streamlit as st
import plotly.graph_objects as go
import numpy as np
import uuid

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio GD&T - Ing. Jaime Silva")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL ALTO CONTRASTE)
# ==========================================
MAIN_BG = "#E0E0E0"      # Gris claro industrial
SIDEBAR_BG = "#121212"   # Negro profundo
TEXT_COLOR = "#000000"   # Negro absoluto
ACCENT = "#0055A4"       # Azul Ingeniería fuerte

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    
    /* BARRA LATERAL */
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] li {{
        color: #FFFFFF !important;
    }}
    /* Corrección para inputs en sidebar */
    div[data-baseweb="select"] > div {{ background-color: white !important; color: black !important; }}
    div[data-baseweb="select"] span {{ color: black !important; }}
    
    /* TARJETAS */
    .gdt-card {{
        background-color: #FFFFFF;
        border-left: 8px solid {ACCENT};
        padding: 20px;
        border-radius: 8px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}
    
    /* RECUADROS DE INTERPRETACIÓN */
    .info-box {{
        background-color: #D1E7DD;
        border-left: 6px solid #0f5132;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
        color: #000000;
    }}
    
    .big-icon {{
        font-size: 90px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center;
    }}
    
    h1, h2, h3 {{ color: {TEXT_COLOR} !important; }}
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (Basada en el PDF proporcionado)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta perfecta.',
        'app': 'Vástagos de cilindros, ejes largos.',
        'desc': 'la rectitud del elemento', 'zone': 'dos líneas paralelas separadas por la tolerancia',
        'geo': 'cylinder_axis' # Geometría específica para 3D
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'app': 'Culatas de motor, mesas de referencia.',
        'desc': 'la planicidad de la superficie', 'zone': 'dos planos paralelos separados por la tolerancia',
        'geo': 'cube_surf'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie circular (corte 2D) equidistan de un centro.',
        'app': 'Pistas de rodamientos, muñones.',
        'desc': 'la circularidad en cualquier sección', 'zone': 'dos círculos concéntricos',
        'geo': 'ring'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'app': 'Pistones hidráulicos, pernos maestros.',
        'desc': 'la forma cilíndrica total', 'zone': 'dos cilindros coaxiales',
        'geo': 'cylinder_full'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'app': 'Escuadras de fijación, bridas.',
        'desc': 'la perpendicularidad (90°)', 'zone': 'dos planos paralelos perpendiculares al Datum',
        'geo': 'L_bracket'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano Datum.',
        'app': 'Rieles, guías lineales.',
        'desc': 'el paralelismo', 'zone': 'dos planos paralelos al Datum',
        'geo': 'block_parallel'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla una superficie o eje a un ángulo específico (no 90°) respecto a un Datum.',
        'app': 'Guías de cola de milano, rampas.',
        'desc': 'la inclinación angular exacta', 'zone': 'dos planos paralelos inclinados al ángulo básico',
        'geo': 'wedge'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B C',
        'def': 'Controla la ubicación exacta del centro de una característica (agujero) respecto a Datums.',
        'app': 'Patrones de pernos, ensambles múltiples.',
        'desc': 'la posición verdadera del centro', 'zone': 'un cilindro centrado en la posición teórica',
        'geo': 'plate_hole'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla que los puntos medios de secciones opuestas caigan en una zona cilíndrica (Balanceo).',
        'app': 'Rotores de alta velocidad.',
        'desc': 'la coaxialidad de los puntos medios', 'zone': 'un cilindro coaxial al Datum',
        'geo': 'stepped_shaft'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación de la superficie en una sección circular al girar (Runout).',
        'app': 'Discos de freno, ejes de motor.',
        'desc': 'el alabeo en cada sección circular', 'zone': 'distancia radial entre círculos coaxiales',
        'geo': 'shaft_runout'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación de toda la superficie al girar y desplazarse.',
        'app': 'Ejes de bombas, rodillos.',
        'desc': 'el alabeo de toda la superficie', 'zone': 'distancia radial entre dos cilindros',
        'geo': 'shaft_runout'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una curva 2D en una sección transversal.',
        'app': 'Alas de avión, levas.',
        'desc': 'el perfil de la línea', 'zone': 'una banda uniforme siguiendo el perfil ideal',
        'geo': 'curved_surface'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una superficie 3D compleja.',
        'app': 'Carrocerías de autos, moldes.',
        'desc': 'el perfil de toda la superficie', 'zone': 'dos superficies envolventes',
        'geo': 'curved_surface'
    }
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO ROBUSTAS
# ==========================================
def get_clean_layout(title, is_3d=True):
    """Configuración gráfica para evitar fondos negros y letras invisibles"""
    bg_color = MAIN_BG if is_3d else "white"
    layout = dict(
        title=dict(text=title, font=dict(size=20, color='black')),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color='black'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=600,
        autosize=True
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            xaxis=dict(visible=False, backgroundcolor=bg_color),
            yaxis=dict(visible=False, backgroundcolor=bg_color),
            zaxis=dict(visible=True, backgroundcolor=bg_color, gridcolor="#ccc", title='')
        )
        # LEYENDA RESTAURADA
        layout['legend'] = dict(
            yanchor="top", y=0.99, xanchor="right", x=0.99,
            bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1
        )
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 15])
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 10])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))]
    return layout

def draw_trace_line(fig, x, y, color="black", width=2, dash=None, name=None):
    show = True if name else False
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=width, dash=dash), showlegend=show, name=name, hoverinfo='skip'))

def draw_trace_rect(fig, x0, y0, w, h, color="black", fill=None):
    x = [x0, x0+w, x0+w, x0, x0]
    y = [y0, y0, y0+h, y0+h, y0]
    fill_val = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=fill_val, fillcolor=fill, mode='lines', line=dict(color=color, width=2), showlegend=False, hoverinfo='skip'))

def draw_trace_circle(fig, x_c, y_c, r, color="black"):
    theta = np.linspace(0, 2*np.pi, 50)
    x = x_c + r * np.cos(theta)
    y = y_c + r * np.sin(theta)
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=2), showlegend=False))

# ==========================================
# 3. VISTA 1: SIMULACIÓN 3D (GEOMETRÍAS ESPECÍFICAS)
# ==========================================
def plot_3d(feature, tol):
    fig = go.Figure()
    geo_type = gdt_data[feature]['geo']
    
    # Mallas base
    res = 40
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res)
    tg, zg = np.meshgrid(theta, z)

    # === LÓGICA DE GEOMETRÍA DISTINTA PARA CADA CASO ===
    
    if feature == 'Rectitud': # Eje
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real (Curvo)'))
        fig.add_trace(go.Surface(x=(tol)*np.cos(tg), y=(tol)*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Zona Tolerancia'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', dash='dash'), name='Eje Nominal'))

    elif feature == 'Redondez': # Aro 2D
        th = np.linspace(0, 2*np.pi, 100)
        r_err = 5 + 0.3*np.sin(5*th)
        fig.add_trace(go.Scatter3d(x=r_err*np.cos(th), y=r_err*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=8), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th), y=(5+tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Límite Sup'))
        fig.add_trace(go.Scatter3d(x=(5-tol)*np.cos(th), y=(5-tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Límite Inf'))

    elif geo_type == 'plate_hole' or feature == 'Posición':
        # Placa transparente
        x = np.linspace(-5, 5, 20); y = np.linspace(-5, 5, 20); xg, yg = np.meshgrid(x, y)
        fig.add_trace(go.Surface(z=np.zeros_like(xg), x=xg, y=yg, opacity=0.1, showscale=False, colorscale='Greys', name='Placa'))
        # Eje desviado
        fig.add_trace(go.Scatter3d(x=[1, 1], y=[1, 1], z=[-1, 5], line=dict(color='red', width=8), name='Eje Real del Agujero'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-1, 5], line=dict(color='black', width=4, dash='dash'), name='Posición Verdadera'))
        # Zona tol
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.4, colorscale='YlOrRd', showscale=False, name='Zona Cil. Tolerancia'))

    elif geo_type == 'L_bracket': # Perpendicularidad
        # Pared vertical
        y_w = np.linspace(0, 8, 20); x_w = np.linspace(-4, 4, 20); Y, X = np.meshgrid(y_w, x_w)
        Z_w = 0.5 * Y/8 # Inclinación
        fig.add_trace(go.Surface(x=X, y=Y, z=Z_w, colorscale='Blues', name='Cara Real (Inclinada)'))
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.3, showscale=False, name='Datum A (Base)'))
        # Planos límite
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, tol), opacity=0.2, showscale=False, colorscale='Reds', name='Lim +'))
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, -tol), opacity=0.2, showscale=False, colorscale='Reds', name='Lim -'))

    elif feature == 'Angularidad': # Cuña
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20)); z_nom = x * np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom, colorscale='Viridis', name='Plano Inclinado'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol, opacity=0.2, showscale=False, colorscale='Greens', name='Lim Sup'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol, opacity=0.2, showscale=False, colorscale='Greens', name='Lim Inf'))

    else: # Default (Cilindro o Plano)
        if geo_type == 'cylinder_full' or 'Alabeo' in feature:
            r = 5 + 0.2*np.sin(zg)
            fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Superficie Real'))
        else: # Planicidad
            x = np.linspace(0, 10, 20); y = np.linspace(0, 10, 20); xg, yg = np.meshgrid(x, y)
            z_surf = 0.2 * np.sin(xg) * np.cos(yg)
            fig.add_trace(go.Surface(z=z_surf, x=xg, y=yg, colorscale='Plasma', name='Sup. Real'))
            fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Reds', name='Lim Sup'))

    fig.update_layout(**get_clean_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMACIÓN CORREGIDA Y ROBUSTA)
# ==========================================
def plot_real_anim(feature):
    fig = go.Figure()
    layout = get_clean_layout(f"Montaje de Inspección: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=30, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)

    # Identificar tipo de movimiento
    geo_type = gdt_data[feature]['geo']
    is_rotational = feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']
    
    frames = []
    
    if is_rotational:
        # Configuración Torno/Chuck
        draw_trace_rect(fig, 0, 2, 2, 6, color="black", fill="#555") # Chuck
        draw_trace_rect(fig, 2, 3, 8, 5, color="blue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40, color='white'))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', opacity=0, name='Start')) # Dummy trace 0

        # Animación: Aguja oscilando
        for i in range(60):
            angle = i * 0.3
            needle_x = 5 + 0.5*np.cos(angle)
            frames.append(go.Frame(data=[
                go.Scatter(x=[5, 5], y=[5, 6.5], mode='lines', line=dict(color='gray')), # Vástago fijo
                go.Scatter(x=[5, needle_x], y=[6.5, 7.5], mode='lines', line=dict(color='red', width=3)) # Aguja móvil
            ], traces=[1, 2]))
        
        # Traces iniciales (Indices 1 y 2)
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6.5], mode='lines', line=dict(color='gray'), name='Soporte'))
        fig.add_trace(go.Scatter(x=[5, 5.5], y=[6.5, 7.5], mode='lines', line=dict(color='red'), name='Indicador'))

    elif geo_type == 'L_bracket': # Perpendicularidad
        draw_trace_rect(fig, 0, 0, 4, 6, color="black", fill="#ccc") # Escuadra
        draw_trace_line(fig, 4.2, 0, 4.2+1, 6, color="blue", width=4, name="Pieza") # Pieza inclinada
        
        for i in range(0, 60, 2):
            y_pos = i/10
            x_contact = 4.2 + (y_pos * 0.16) 
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_contact-1.5, x_contact], y=[y_pos, y_pos], mode='lines+markers', marker=dict(size=10), line=dict(color='red')),
            ], traces=[1]))
        fig.add_trace(go.Scatter(x=[2.7, 4.2], y=[0, 0], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    else: # Deslizamiento (Rectitud, Planicidad, Paralelismo)
        draw_trace_rect(fig, 0, 0, 12, 1, color="black", fill="#ccc") # Mesa
        # Pieza ondulada
        x_surf = np.linspace(1, 11, 100)
        y_surf = 2 + 0.3*np.sin(x_surf)
        fig.add_trace(go.Scatter(x=x_surf, y=y_surf, mode='lines', line=dict(color='blue', width=4), name='Superficie'))
        
        for i in range(0, 100, 2):
            xi = x_surf[i]; yi = y_surf[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yi+2], mode='lines+markers', marker=dict(symbol='circle', size=15), line=dict(color='red'))
            ], traces=[1]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Palpador'))

    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO TÉCNICO (ESTÁTICO, CORRECTO)
# ==========================================
def draw_blueprint(feature, tol_val):
    info = gdt_data[feature]
    geo = info['geo']
    sym = info['symbol']
    datum = info['datum']
    ftype = info['type']
    
    fig = go.Figure()
    fig.update_layout(**get_clean_layout(f"Plano de Ingeniería: {feature}", is_3d=False))
    
    # --- 1. DIBUJO DE PIEZA ---
    leader_target = (0,0)
    
    if geo in ['cylinder', 'shaft', 'stepped_shaft', 'cylinder_axis', 'cylinder_full', 'shaft_runout']:
        # Eje
        draw_trace_rect(fig, 2, 3, 8, 4, width=3)
        draw_trace_line(fig, 1, 5, 10, 5, width=1, dash='longdashdot', name='Centro')
        # Cota tamaño
        draw_trace_line(fig, 10, 3, 11, 3, width=1)
        draw_trace_line(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", font=dict(size=14), showarrow=False)
        draw_arrow_manual(fig, 10.5, 5.5, 10.5, 7)
        draw_arrow_manual(fig, 10.5, 4.5, 10.5, 3)
        
        if ftype == 'axis':
            leader_target = (10.5, 4.5) # Apunta a cota
        else:
            leader_target = (6, 7) # Apunta superficie
            
    elif geo == 'plate_hole':
        # Placa superior
        draw_trace_rect(fig, 2, 1, 8, 6, width=3)
        draw_trace_circle(fig, 6, 4, 1) # Agujero
        draw_trace_line(fig, 6, 2, 6, 6, dash='dash')
        draw_trace_line(fig, 4, 4, 8, 4, dash='dash')
        # Cota agujero
        fig.add_annotation(x=7.5, y=5.5, ax=6.5, ay=4.8, text="Ø 20 ±0.1", arrowhead=2, arrowcolor="black")
        leader_target = (7.5, 5.3)

    elif geo == 'L_bracket':
        x_pts = [2, 8, 8, 4, 4, 2, 2]; y_pts = [1, 1, 3, 3, 7, 7, 1]
        fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode='lines', line=dict(color='black', width=3), showlegend=False))
        leader_target = (4, 5)

    else: # Bloque
        draw_trace_rect(fig, 2, 2, 8, 4, width=3)
        leader_target = (6, 6)

    # --- 2. DATUM ---
    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[1, 1, 0.2, 1], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_trace_rect(fig, 3.1, -0.6, 0.8, 0.8, width=1)
        fig.add_annotation(x=3.5, y=-0.2, text=f"<b>{datum[0]}</b>", font=dict(size=14), showarrow=False)

    # --- 3. MARCO DE CONTROL ---
    frame_x, frame_y = 9, 8
    elbow_x = frame_x - 0.5
    
    # Líder quebrado
    fig.add_trace(go.Scatter(x=[leader_target[0], elbow_x, frame_x], y=[leader_target[1], frame_y+0.5, frame_y+0.5], mode='lines', line=dict(color='black', width=2), showlegend=False))
    draw_arrow_manual(fig, elbow_x, frame_y+0.5, leader_target[0], leader_target[1])

    # Celdas
    w_sym, w_tol, w_dat = 1.2, 2.0, 1.2
    
    draw_trace_rect(fig, frame_x, frame_y, w_sym, 1, width=2)
    fig.add_annotation(x=frame_x+w_sym/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=24), showarrow=False)
    
    draw_trace_rect(fig, frame_x+w_sym, frame_y, w_tol, 1, width=2)
    t_txt = f"Ø {tol_val}" if ftype == 'axis' else str(tol_val)
    fig.add_annotation(x=frame_x+w_sym+w_tol/2, y=frame_y+0.5, text=f"<b>{t_txt}</b>", font=dict(size=18), showarrow=False)
    
    if datum:
        draw_trace_rect(fig, frame_x+w_sym+w_tol, frame_y, w_dat, 1, width=2)
        fig.add_annotation(x=frame_x+w_sym+w_tol+w_dat/2, y=frame_y+0.5, text=f"<b>{datum}</b>", font=dict(size=18), showarrow=False)

    return fig

# --- VISTA 4: CONSTRUCTOR ---
def draw_master_blueprint(active_features):
    fig = go.Figure()
    fig.update_layout(**get_clean_layout("Plano Maestro Interactivo", is_3d=False))
    
    # Pieza maestra
    x_pts = [1, 11, 11, 9, 9, 4, 4, 1, 1]
    y_pts = [1, 1, 3, 3, 5, 5, 8, 8, 1]
    fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode='lines', line=dict(color='black', width=3), showlegend=False))
    
    slot_y = 9
    for i, feat in enumerate(active_features):
        info = gdt_data[feat]
        fx = 12; fy = slot_y - (i*1.5)
        draw_trace_rect(fig, fx, fy, 4, 1, width=2)
        txt = f"{info['symbol']} 0.1 {info['datum'] if info['datum'] else ''}"
        fig.add_annotation(x=fx+2, y=fy+0.5, text=f"<b>{txt}</b>", font=dict(size=16), showarrow=False)
        # Flecha simple indicativa
        fig.add_annotation(x=6, y=5, ax=fx, ay=fy+0.5, arrowhead=2, arrowcolor="gray")

    return fig

# --- HELPERS ---
def draw_arrow_manual(fig, x0, y0, x1, y1):
    fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# ==========================================
# 4. LÓGICA PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5)
    view = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    # Clave única para romper caché
    g_key = f"{feat}_{view}_{tol}_{uuid.uuid4()}"
    info = gdt_data[feat]
    
    # Tarjeta Superior
    st.markdown(f"""
    <div class="gdt-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p>⚙️ <strong>Aplicación:</strong> {info['app']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if view == "📐 Simulación 3D":
        st.plotly_chart(plot_3d(feat, tol), use_container_width=True, key=g_key)
        st.markdown(f"<div class='info-box'><b>🔍 Detalle:</b> {info['sim_3d_desc']}</div>", unsafe_allow_html=True)
    elif view == "🏭 Montaje Real":
        st.plotly_chart(plot_real_anim(feat), use_container_width=True, key=g_key)
        st.markdown(f"<div class='info-box'><b>🏭 Procedimiento:</b> {info['real_desc']}</div>", unsafe_allow_html=True)
    elif view == "📝 Plano Técnico":
        st.plotly_chart(draw_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=g_key)
        st.markdown(f"""
        <div class="interpretation-box">
            <h4>🤓 Interpretación:</h4>
            <p>Controla <b>{info['desc']}</b> dentro de una zona de <b>{info['zone']}</b> de valor <b>{tol}</b>.</p>
        </div>
        """, unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    st.sidebar.info("Agregue características al plano:")
    sel = st.sidebar.multiselect("Agregar:", list(gdt_data.keys()), default=['Rectitud', 'Posición'])
    st.plotly_chart(draw_master_blueprint(sel), use_container_width=True, key=f"master_{len(sel)}")
