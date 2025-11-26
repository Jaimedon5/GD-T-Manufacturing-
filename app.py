import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio GD&T - Ing. Jaime Silva")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL DE ALTO CONTRASTE)
# ==========================================
MAIN_BG = "#E0E0E0"      # Gris claro industrial (descanso visual)
SIDEBAR_BG = "#121212"   # Negro profundo
TEXT_COLOR = "#000000"   # Negro absoluto para textos
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
        'geo': 'cylinder'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'app': 'Culatas de motor, mesas de referencia.',
        'desc': 'la planicidad de la superficie', 'zone': 'dos planos paralelos separados por la tolerancia',
        'geo': 'cube'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie circular (corte 2D) equidistan de un centro.',
        'app': 'Pistas de rodamientos, muñones.',
        'desc': 'la circularidad en cualquier sección', 'zone': 'dos círculos concéntricos',
        'geo': 'cylinder'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'app': 'Pistones hidráulicos, pernos maestros.',
        'desc': 'la forma cilíndrica total', 'zone': 'dos cilindros coaxiales',
        'geo': 'cylinder'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'app': 'Escuadras de fijación, bridas.',
        'desc': 'la perpendicularidad (90°)', 'zone': 'dos planos paralelos perpendiculares al Datum',
        'geo': 'L-bracket'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano Datum.',
        'app': 'Rieles, guías lineales.',
        'desc': 'el paralelismo', 'zone': 'dos planos paralelos al Datum',
        'geo': 'block'
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
        'geo': 'plate_holes'
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
        'geo': 'shaft'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación de toda la superficie al girar y desplazarse.',
        'app': 'Ejes de bombas, rodillos.',
        'desc': 'el alabeo de toda la superficie', 'zone': 'distancia radial entre dos cilindros',
        'geo': 'shaft'
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

    if geo_type == 'cylinder': # Rectitud, Redondez, Cilindricidad, Alabeos
        r = 5
        if feature == 'Rectitud':
            # Eje doblado
            fig.add_trace(go.Scatter3d(x=0.5*np.sin(z), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
            fig.add_trace(go.Surface(x=(tol)*np.cos(tg), y=(tol)*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Zona Tol'))
        elif feature == 'Redondez':
            # Un solo anillo
            th_ring = np.linspace(0, 2*np.pi, 100)
            r_error = 5 + 0.3*np.sin(5*th_ring)
            fig.add_trace(go.Scatter3d(x=r_error*np.cos(th_ring), y=r_error*np.sin(th_ring), z=np.zeros_like(th_ring), mode='lines', line=dict(color='blue', width=8), name='Perfil Real'))
            fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th_ring), y=(5+tol)*np.sin(th_ring), z=np.zeros_like(th_ring), line=dict(color='red', dash='dash'), name='Límite Sup'))
            fig.add_trace(go.Scatter3d(x=(5-tol)*np.cos(th_ring), y=(5-tol)*np.sin(th_ring), z=np.zeros_like(th_ring), line=dict(color='red', dash='dash'), name='Límite Inf'))
            fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2.5))) # Vista superior
        else:
            # Cilindro completo
            r_def = 5 + 0.2*np.sin(zg)
            fig.add_trace(go.Surface(x=r_def*np.cos(tg), y=r_def*np.sin(tg), z=zg, colorscale='Viridis', name='Superficie Real'))
            fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje Datum'))

    elif geo_type == 'plate_holes': # Posición
        # Placa con agujero
        x = np.linspace(-5, 5, res); y = np.linspace(-5, 5, res); xg, yg = np.meshgrid(x, y)
        fig.add_trace(go.Surface(z=np.zeros_like(xg), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Greys', name='Placa'))
        # Agujero
        hc_x, hc_y = 1, 1 # Centro desplazado
        fig.add_trace(go.Scatter3d(x=[hc_x, hc_x], y=[hc_y, hc_y], z=[-1, 5], line=dict(color='red', width=8), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-1, 5], line=dict(color='black', width=4, dash='dash'), name='Posición Verdadera'))
        # Cilindro tolerancia
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.4, colorscale='YlOrRd', showscale=False, name='Zona Tol'))

    elif geo_type == 'L-bracket': # Perpendicularidad
        # Pared vertical
        y_wall = np.linspace(0, 8, res); x_wall = np.linspace(-4, 4, res); Y, X = np.meshgrid(y_wall, x_wall)
        Z_wall = 0.3 * Y/8 # Inclinación
        fig.add_trace(go.Surface(x=X, y=Y, z=Z_wall, colorscale='Blues', name='Cara Real'))
        # Datum
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.5, colorscale='Greys', showscale=False, name='Datum A'))
        # Planos tol
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, tol), opacity=0.2, showscale=False, colorscale='Reds', name='Lim +'))
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, -tol), opacity=0.2, showscale=False, colorscale='Reds', name='Lim -'))

    else: # Planicidad, Paralelismo (Bloque)
        x = np.linspace(0, 10, res); y = np.linspace(0, 10, res); xg, yg = np.meshgrid(x, y)
        z_surf = 0.2 * np.sin(xg) * np.cos(yg)
        fig.add_trace(go.Surface(z=z_surf, x=xg, y=yg, colorscale='Plasma', name='Superficie'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Greens', name='Plano Sup'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Greens', name='Plano Inf'))

    fig.update_layout(**get_clean_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMACIÓN CORREGIDA)
# ==========================================
def plot_real_anim(feature):
    fig = go.Figure()
    layout = get_clean_layout(f"Montaje de Inspección: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=30, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)

    # Escenario base según tipo
    geo_type = gdt_data[feature]['geo']
    
    frames = []
    
    if geo_type == 'L-bracket' or feature == 'Perpendicularidad':
        # Escuadra y pieza
        draw_trace_rect(fig, 0, 0, 4, 6, color="black", fill="#ccc") # Escuadra patrón
        draw_trace_line(fig, 4.2, 0, 4.2+2, 6, color="blue", width=4, name="Pieza") # Pieza inclinada
        
        # Animación vertical
        for i in range(0, 60, 2):
            y_pos = i/10
            x_contact = 4.2 + (y_pos * 0.05) # Sigue la inclinación
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_contact-1.5, x_contact], y=[y_pos, y_pos], mode='lines+markers', marker=dict(size=10), line=dict(color='red')), # Reloj
            ]))
        # Trace inicial
        fig.add_trace(go.Scatter(x=[2.7, 4.2], y=[0.5, 0.5], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    elif feature == 'Redondez' or feature == 'Cilindricidad' or 'Alabeo' in feature:
        # Chuck y Pieza giratoria
        draw_trace_rect(fig, 0, 2, 2, 6, color="black", fill="#555") # Chuck
        draw_trace_rect(fig, 2, 3, 8, 5, color="blue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40))
        
        # Animación (Aguja oscilando)
        for i in range(60):
            angle = i * 0.2
            needle_x = 5 + 0.5*np.cos(angle)
            frames.append(go.Frame(data=[
                go.Scatter(x=[5, 5], y=[5, 6.5], mode='lines', line=dict(color='gray')), # Vástago
                go.Scatter(x=[5, needle_x], y=[6.5, 7.5], mode='lines', line=dict(color='red', width=3)) # Aguja
            ]))
        
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6.5], mode='lines', line=dict(color='gray'), name='Soporte'))
        fig.add_trace(go.Scatter(x=[5, 5], y=[6.5, 7.5], mode='lines', line=dict(color='red'), name='Indicador'))

    else: # Rectitud, Planicidad (Deslizamiento horizontal)
        draw_trace_rect(fig, 0, 0, 12, 1, color="black", fill="#ccc") # Mesa
        y_surf = np.linspace(1, 1, 100) + 0.2*np.sin(np.linspace(0, 10, 100))
        fig.add_trace(go.Scatter(x=np.linspace(1,11,100), y=y_surf+1, mode='lines', line=dict(color='blue', width=4), name='Superficie'))
        
        for i in range(0, 100, 2):
            x_pos = 1 + i/10
            y_pos = 2 + 0.2*np.sin(i/10)
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[y_pos, y_pos+2], mode='lines+markers', marker=dict(symbol='circle', size=15), line=dict(color='red'))
            ]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Palpador'))

    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO TÉCNICO (COTAS CORREGIDAS)
# ==========================================
def draw_blueprint(feature, tol_val):
    info = gdt_data[feature]
    geo = info['geo']
    sym = info['symbol']
    datum = info['datum']
    
    fig = go.Figure()
    fig.update_layout(**get_clean_layout(f"Plano de Ingeniería: {feature}", is_3d=False))
    
    # --- 1. DIBUJO DE LA PIEZA SEGÚN GEOMETRÍA ---
    if geo == 'cylinder' or geo == 'shaft':
        # Eje
        draw_trace_rect(fig, 2, 3, 8, 4, width=3)
        draw_trace_line(fig, 1, 5, 10, 5, width=1, dash='longdashdot', name='Centro')
        # Cotas de tamaño
        draw_trace_line(fig, 10, 3, 11, 3, width=1)
        draw_trace_line(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", font=dict(size=14), showarrow=False)
        draw_arrow_manual(fig, 10.5, 5.5, 10.5, 7) # Flecha arriba
        draw_arrow_manual(fig, 10.5, 4.5, 10.5, 3) # Flecha abajo
        
        leader_target = (10.5, 4.5) # Apunta al texto de la cota (para ejes)
        if info['type'] == 'surf': leader_target = (6, 7) # Si es superficie (rectitud), apunta a la línea
            
    elif geo == 'plate_holes':
        # Placa vista superior
        draw_trace_rect(fig, 2, 1, 8, 6, width=3)
        # 4 Agujeros
        for px in [4, 6]:
            for py in [3, 5]:
                draw_trace_circle(fig, px, py, 0.5)
                draw_trace_line(fig, px-0.8, py, px+0.8, py, width=1, dash='dash') # Cruces
                draw_trace_line(fig, px, py-0.8, px, py+0.8, width=1, dash='dash')

        # Cota de tamaño (apunta a un agujero)
        fig.add_annotation(x=7.5, y=5.5, ax=6.5, ay=5.2, text="4X Ø 10 ±0.1", arrowhead=2, arrowcolor="black")
        leader_target = (7.5, 5.3) # Apunta al texto

    elif geo == 'L-bracket':
        # Escuadra
        x_pts = [2, 8, 8, 4, 4, 2, 2]
        y_pts = [1, 1, 3, 3, 7, 7, 1]
        fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode='lines', line=dict(color='black', width=3), showlegend=False))
        leader_target = (4, 5) # Apunta a la cara vertical

    else: # Bloque genérico
        draw_trace_rect(fig, 2, 2, 8, 4, width=3)
        leader_target = (6, 6)

    # --- 2. DATUM (SI APLICA) ---
    if datum:
        # Triángulo en la base
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[1, 1, 0.2, 1], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_trace_rect(fig, 3.1, -0.6, 0.8, 0.8, width=1)
        fig.add_annotation(x=3.5, y=-0.2, text="<b>A</b>", font=dict(size=14), showarrow=False)

    # --- 3. MARCO DE CONTROL Y LÍDER (QUEBRADO) ---
    # Posición del marco (Arriba derecha)
    frame_x, frame_y = 9, 8
    
    # Línea líder quebrada (Codo)
    # Desde el target hasta el lado del marco
    elbow_x = frame_x - 0.5
    fig.add_trace(go.Scatter(x=[leader_target[0], elbow_x, frame_x], y=[leader_target[1], frame_y+0.5, frame_y+0.5], mode='lines', line=dict(color='black', width=2), showlegend=False))
    # Punta de flecha en el target
    draw_arrow_manual(fig, elbow_x, frame_y+0.5, leader_target[0], leader_target[1])

    # Dibujar Marco
    w_sym, w_tol, w_dat = 1.2, 1.8, 1.2
    h = 1.0
    
    # Celda Símbolo
    draw_trace_rect(fig, frame_x, frame_y, w_sym, h, width=2)
    fig.add_annotation(x=frame_x+w_sym/2, y=frame_y+h/2, text=f"<b>{sym}</b>", font=dict(size=24), showarrow=False)
    
    # Celda Tolerancia
    draw_trace_rect(fig, frame_x+w_sym, frame_y, w_tol, h, width=2)
    t_txt = f"Ø {tol_val}" if info['type'] == 'axis' else str(tol_val)
    fig.add_annotation(x=frame_x+w_sym+w_tol/2, y=frame_y+h/2, text=f"<b>{t_txt}</b>", font=dict(size=18), showarrow=False)

    # Celda Datum
    if datum:
        draw_trace_rect(fig, frame_x+w_sym+w_tol, frame_y, w_dat, h, width=2)
        fig.add_annotation(x=frame_x+w_sym+w_tol+w_dat/2, y=frame_y+h/2, text=f"<b>{datum[0]}</b>", font=dict(size=18), showarrow=False)

    return fig

# --- VISTA 4: CONSTRUCTOR DE PLANOS ---
def draw_master_blueprint(active_features):
    fig = go.Figure()
    fig.update_layout(**get_clean_layout("Plano Maestro Interactivo", is_3d=False))
    
    # Pieza compleja (Base + Torre + Agujero + Chaflán)
    x_pts = [1, 11, 11, 9, 9, 4, 4, 1, 1]
    y_pts = [1, 1, 3, 3, 5, 5, 8, 8, 1]
    fig.add_trace(go.Scatter(x=x_pts, y=y_pts, mode='lines', line=dict(color='black', width=3), showlegend=False))
    
    # Eje
    draw_trace_line(fig, 0.5, 6.5, 11.5, 6.5, dash='longdashdot')
    
    # Iterar activas
    slot_y = 9
    for i, feat in enumerate(active_features):
        info = gdt_data[feat]
        # Dibujar marco en lista vertical a la derecha
        fx = 12; fy = slot_y - (i*1.5)
        draw_trace_rect(fig, fx, fy, 4, 1, width=2)
        txt = f"{info['symbol']} 0.1 {info['datum'] if info['datum'] else ''}"
        fig.add_annotation(x=fx+2, y=fy+0.5, text=f"<b>{txt}</b>", font=dict(size=16), showarrow=False)
        
        # Flecha apuntando a la pieza (genérica para el ejemplo)
        fig.add_annotation(x=6, y=5, ax=fx, ay=fy+0.5, arrowhead=2, arrowcolor="gray")

    return fig

# --- UTILIDADES DE DIBUJO ---
def draw_trace_line(fig, x0, y0, x1, y1, color="black", width=1, dash=None, name=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), name=name, showlegend=False))

def draw_trace_rect(fig, x0, y0, w, h, color="black", fill=None, width=2):
    x = [x0, x0+w, x0+w, x0, x0]; y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), showlegend=False))

def draw_trace_circle(fig, x, y, r):
    th = np.linspace(0, 2*np.pi, 30)
    fig.add_trace(go.Scatter(x=x+r*np.cos(th), y=y+r*np.sin(th), mode='lines', line=dict(color='black'), showlegend=False))

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
    
    # CLAVE ÚNICA PARA EVITAR CONGELAMIENTOS
    g_key = f"{feat}_{view}_{tol}_{time.time()}"
    
    info = gdt_data[feat]
    
    # TARJETA DE INFORMACIÓN SUPERIOR
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
        st.markdown(f"<div class='visual-card'><b>🔍 Detalle:</b> {info['sim_3d_desc']}</div>", unsafe_allow_html=True)
    elif view == "🏭 Montaje Real":
        st.plotly_chart(plot_real_anim(feat), use_container_width=True, key=g_key)
        st.markdown(f"<div class='visual-card'><b>🏭 Procedimiento:</b> {info['real_desc']}</div>", unsafe_allow_html=True)
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
