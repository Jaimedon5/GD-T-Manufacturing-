import streamlit as st
import plotly.graph_objects as go
import numpy as np
import uuid
import time

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab")

# ==========================================
# 0. ESTILOS CSS (BLINDADOS)
# ==========================================
st.markdown("""
<style>
    /* FONDO GENERAL */
    .stApp { background-color: #E0E0E0; color: black; }
    
    /* BARRA LATERAL */
    section[data-testid="stSidebar"] { background-color: #121212; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* MENÚS DESPLEGABLES (Texto visible) */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* TARJETAS DE INFORMACIÓN */
    .info-card {
        background-color: #ffffff;
        border-left: 8px solid #0055a4;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        color: #000000;
    }
    
    /* INTERPRETACIÓN DEL PLANO */
    .blueprint-box {
        background-color: #e3f2fd;
        border-left: 6px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        color: #000000;
        font-family: monospace;
        margin-top: 10px;
    }
    
    /* ICONO */
    .big-icon {
        font-size: 70px;
        font-weight: bold;
        text-align: center;
        color: #333;
        display: flex; align-items: center; justify-content: center;
    }
    
    h1, h2, h3, p { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS COMPLETA (TÉCNICA + PEDAGÓGICA)
# ==========================================
gdt_db = {
    'Rectitud': {
        'sym': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde un elemento lineal de una superficie o eje es una línea recta.',
        'desc': 'Rectitud', 'zone': 'Dos líneas paralelas', 'geo': 'shaft_banana',
        'app': 'Vástagos, rieles.', 'why': 'Evita fugas en sellos.',
        'sim_3d_desc': 'Eje real (azul) curvado dentro de un cilindro de tolerancia (naranja).',
        'real_desc': 'El reloj se desplaza longitudinalmente sobre la pieza.'
    },
    'Planicidad': {
        'sym': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie están en un solo plano.',
        'desc': 'Planicidad', 'zone': 'Dos planos paralelos', 'geo': 'plate_wavy',
        'app': 'Mesas de granito, culatas.', 'why': 'Asegura contacto total.',
        'sim_3d_desc': 'Superficie irregular contenida entre dos planos límite (rojos).',
        'real_desc': 'El palpador barre toda la superficie buscando picos y valles.'
    },
    'Redondez': {
        'sym': '○', 'type': 'surf', 'datum': False,
        'def': 'Condición donde los puntos de una sección circular (2D) equidistan del centro.',
        'desc': 'Circularidad', 'zone': 'Dos círculos concéntricos', 'geo': 'ring_lobed',
        'app': 'Rodamientos, ejes.', 'why': 'Evita vibraciones.',
        'sim_3d_desc': 'Perfil lobulado (azul) entre dos círculos perfectos (rojos).',
        'real_desc': 'La pieza gira 360° y el reloj mide la variación radial.'
    },
    'Cilindricidad': {
        'sym': '⌭', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma cilíndrica total (Redondez + Rectitud + Conicidad).',
        'desc': 'Cilindricidad', 'zone': 'Dos cilindros coaxiales', 'geo': 'cylinder_barrel',
        'app': 'Pistones, pernos.', 'why': 'Sellado dinámico.',
        'sim_3d_desc': 'Superficie completa 3D (barril) entre dos cilindros límite.',
        'real_desc': 'Escaneo en espiral de toda la superficie cilíndrica.'
    },
    'Perpendicularidad': {
        'sym': '⟂', 'type': 'orient', 'datum': 'A',
        'def': 'Condición donde una superficie o eje está a 90° de un Datum.',
        'desc': 'Perpendicularidad', 'zone': 'Dos planos a 90°', 'geo': 'L_bracket',
        'app': 'Escuadras, bridas.', 'why': 'Alineación de ensambles.',
        'sim_3d_desc': 'Pared inclinada respecto a la base (Datum A).',
        'real_desc': 'El reloj sube y baja comparando contra una escuadra patrón.'
    },
    'Angularidad': {
        'sym': '∠', 'type': 'orient', 'datum': 'A',
        'def': 'Condición a un ángulo específico (básico) respecto al Datum.',
        'desc': 'Angularidad', 'zone': 'Dos planos inclinados', 'geo': 'wedge',
        'app': 'Guías en V.', 'why': 'Contacto uniforme.',
        'sim_3d_desc': 'Plano inclinado real entre límites de tolerancia (verdes).',
        'real_desc': 'Uso de Mesa de Senos para anular el ángulo y medir plano.'
    },
    'Posición': {
        'sym': '⌖', 'type': 'loc', 'datum': 'A B C',
        'def': 'Controla la ubicación exacta del centro de una característica.',
        'desc': 'Posición', 'zone': 'Cilindro en posición teórica', 'geo': 'plate_hole',
        'app': 'Agujeros de pernos.', 'why': 'Garantiza ensamble.',
        'sim_3d_desc': 'Eje real (rojo) dentro de un cilindro de tolerancia (amarillo).',
        'real_desc': 'Verificación con Gage funcional de pernos fijos.'
    },
    'Paralelismo': {
        'sym': '∥', 'type': 'orient', 'datum': 'A',
        'def': 'Condición donde todos los puntos equidistan de un plano Datum.',
        'desc': 'Paralelismo', 'zone': 'Dos planos paralelos', 'geo': 'block_parallel',
        'app': 'Rieles, guías.', 'why': 'Movimiento suave.',
        'sim_3d_desc': 'Superficie superior inclinada respecto a la base.',
        'real_desc': 'Deslizamiento del reloj sobre la cara superior.'
    },
    'Alabeo Circular': {'sym': '↗', 'type': 'runout', 'datum': 'A-B', 'def': 'Variación en una sección al girar.', 'desc': 'Runout Circular', 'zone': 'Distancia radial', 'geo': 'shaft_runout', 'app':'Ejes.', 'why':'Vibración.', 'sim_3d_desc':'Línea de medición en una sección.', 'real_desc':'Giro de pieza en bloques V.'},
    'Alabeo Total': {'sym': '⌰', 'type': 'runout', 'datum': 'A-B', 'def': 'Variación de toda la superficie al girar.', 'desc': 'Runout Total', 'zone': 'Distancia radial total', 'geo': 'shaft_runout', 'app':'Rodillos.', 'why':'Balanceo.', 'sim_3d_desc':'Malla completa de la superficie.', 'real_desc':'Giro y desplazamiento longitudinal.'},
    'Perfil de una línea': {'sym': '⌒', 'type': 'profile', 'datum': False, 'def': 'Forma de una curva 2D.', 'desc': 'Perfil de línea', 'zone': 'Banda uniforme', 'geo': 'curved_surf', 'app':'Alas.', 'why':'Aerodinámica.', 'sim_3d_desc':'Curva 2D entre límites.', 'real_desc':'Proyector de perfiles.'},
    'Perfil de una superficie': {'sym': '⌓', 'type': 'profile', 'datum': False, 'def': 'Forma de superficie 3D.', 'desc': 'Perfil de superficie', 'zone': 'Banda 3D', 'geo': 'curved_surf', 'app':'Carrocería.', 'why':'Estética.', 'sim_3d_desc':'Superficie 3D entre límites.', 'real_desc':'Escaneo CMM.'},
    'Concentricidad': {'sym': '◎', 'type': 'loc', 'datum': 'A', 'def': 'Coaxialidad de puntos medios.', 'desc': 'Concentricidad', 'zone': 'Cilindro coaxial', 'geo': 'concentric', 'app':'Rotores.', 'why':'Balanceo.', 'sim_3d_desc':'Puntos medios alineados.', 'real_desc':'Medición diferencial.'}
}

# ==========================================
# 2. GENERADOR DE GRÁFICOS
# ==========================================
def get_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor='white', plot_bgcolor='white', font=dict(color='black'),
        margin=dict(l=10, r=10, t=40, b=10), height=550, autosize=True
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            xaxis=dict(visible=False, backgroundcolor='white'),
            yaxis=dict(visible=False, backgroundcolor='white'),
            zaxis=dict(visible=True, backgroundcolor='white', gridcolor="#ddd")
        )
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1, x=0.8, y=0.9)
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 12], scaleanchor='y')
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 8])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0.01, y0=0.01, x1=0.99, y1=0.99, line=dict(color='black', width=2))]
    return layout

# Funciones de dibujo vectorial
def draw_rect(fig, x0, y0, w, h, color="black", fill=None, width=2):
    x = [x0, x0+w, x0+w, x0, x0]; y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), hoverinfo='skip', showlegend=False))

def draw_line(fig, x0, y0, x1, y1, color="black", width=2, dash=None, name=None):
    show = True if name else False
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), name=name, showlegend=show, hoverinfo='skip'))

def draw_arrow(fig, x_tail, y_tail, x_head, y_head):
    fig.add_annotation(x=x_head, y=y_head, ax=x_tail, ay=y_tail, xref='x', yref='y', axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# ==========================================
# 3. SIMULACIONES 3D (CORREGIDAS)
# ==========================================
def plot_3d(feature, tol):
    fig = go.Figure()
    geo = gdt_db[feature]['geo']
    res = 40
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res); tg, zg = np.meshgrid(theta, z)

    if feature == 'Rectitud':
        x_real = 0.4 * np.sin(z * 0.5)
        fig.add_trace(go.Scatter3d(x=x_real, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=12), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Tol'))

    elif feature == 'Planicidad':
        x = np.linspace(-5, 5, res); y = np.linspace(-5, 5, res); xg, yg = np.meshgrid(x, y)
        z_real = 0.2 * np.sin(xg) * np.cos(yg)
        fig.add_trace(go.Surface(z=z_real, x=xg, y=yg, colorscale='Viridis', name='Sup. Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))

    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100)
        r_dev = 5 + 0.4*np.sin(4*th)
        fig.add_trace(go.Scatter3d(x=r_dev*np.cos(th), y=r_dev*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=10), name='Perfil'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th), y=(5+tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Límites'))
        fig.add_trace(go.Scatter3d(x=(5-tol)*np.cos(th), y=(5-tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), showlegend=False))
        fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2.5)))

    elif feature == 'Cilindricidad':
        r_dev = 5 + 0.3*np.sin(zg * 0.5)
        fig.add_trace(go.Surface(x=r_dev*np.cos(tg), y=r_dev*np.sin(tg), z=zg, colorscale='Spectral', name='Sup. Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Zona Tol'))

    elif feature == 'Angularidad':
        x = np.linspace(0, 10, 20); y = np.linspace(0, 10, 20); xg, yg = np.meshgrid(x, y)
        z_nom = xg * np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom, colorscale='Plasma', name='Plano 30°'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom+tol, opacity=0.2, colorscale='Greens', showscale=False))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom-tol, opacity=0.2, colorscale='Greens', showscale=False))

    elif feature == 'Posición':
        x = np.linspace(-5, 5, 20); y = np.linspace(-5, 5, 20); xg, yg = np.meshgrid(x, y)
        fig.add_trace(go.Surface(x=xg, y=yg, z=np.zeros_like(xg), opacity=0.2, colorscale='Greys', showscale=False, name='Placa'))
        fig.add_trace(go.Scatter3d(x=[1, 1], y=[1, 1], z=[-2, 5], line=dict(color='red', width=10), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-2, 5], line=dict(color='black', dash='dash', width=5), name='Centro Ideal'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.3, colorscale='YlOrRd', showscale=False, name='Zona Tol'))

    elif geo == 'L_bracket':
        y_w = np.linspace(0, 8, res); x_w = np.linspace(-4, 4, res); Y, X = np.meshgrid(y_w, x_w)
        Z_w = (tol*2) * (Y/8) 
        fig.add_trace(go.Surface(x=X, y=Y, z=Z_w, colorscale='Blues', name='Pared Real'))
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.5, colorscale='Greys', showscale=False, name='Datum A'))

    else: # Fallback
        r = 5
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Blues', opacity=0.8))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='longdash', width=5), name='Datum'))

    fig.update_layout(**get_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (FUNCIONAL)
# ==========================================
def plot_real_anim(feature):
    fig = go.Figure()
    layout = get_layout(f"Inspección Física: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)
    
    frames = []
    
    # CASO 1: ROTACIÓN
    if feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        draw_rect(fig, 0, 2, 1, 4, color="black", fill="#333") # Chuck
        draw_rect(fig, 1, 3, 8, 2, color="blue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40, color='white'))
        
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines', line=dict(color='gray', width=3), name='Soporte'))
        
        for i in range(50):
            dy = 0.3 * np.sin(i*0.5)
            frames.append(go.Frame(data=[go.Scatter(x=[5, 5], y=[6, 7.5+dy], mode='lines', line=dict(color='red', width=3))]))
        fig.add_trace(go.Scatter(x=[5, 5], y=[6, 7.5], mode='lines', line=dict(color='red', width=3), name='Aguja'))

    # CASO 2: ANGULARIDAD
    elif feature == 'Angularidad':
        draw_rect(fig, 0, 0, 10, 0.5, fill="#aaa") # Mesa
        fig.add_trace(go.Scatter(x=[2, 8], y=[1, 3], mode='markers', marker=dict(size=20, color='black'))) 
        draw_rect(fig, 7.5, 0.5, 1, 2.5, fill="blue") # Bloques
        fig.add_trace(go.Scatter(x=[2, 8], y=[1.5, 3.5], mode='lines', line=dict(color='black', width=5))) 
        draw_rect(fig, 2, 3.5, 6, 2, color="black") 
        
        for i in range(50):
            x = 2 + i/10
            frames.append(go.Frame(data=[go.Scatter(x=[x, x], y=[5.5, 7], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    # CASO 3: DESLIZAMIENTO
    else:
        draw_rect(fig, 0, 0, 10, 1, fill="#ccc") # Mesa
        x_s = np.linspace(1, 9, 100); y_s = 2 + 0.2*np.sin(x_s)
        fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='lines', line=dict(color='blue', width=4), name='Sup. Real'))
        
        for i in range(0, 100, 2):
            frames.append(go.Frame(data=[go.Scatter(x=[x_s[i], x_s[i]], y=[y_s[i], y_s[i]+2], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO TÉCNICO (DIBUJO CORRECTO)
# ==========================================
def draw_blueprint(feature, tol_val):
    info = gdt_db[feature]
    geo = info['geo']
    ftype = info['type']
    sym = info['symbol']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano de Ingeniería: {feature}", is_3d=False))
    
    # --- PIEZA ---
    if ftype == 'axis': # EJE
        draw_rect(fig, 2, 3, 8, 4, width=3)
        draw_line(fig, 1, 5, 11, 5, dash='longdashdot') # Centro
        draw_line(fig, 10, 3, 11, 3, width=1)
        draw_line(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", font=dict(size=14), showarrow=False)
        draw_arrow(fig, 10.5, 5.5, 10.5, 7); draw_arrow(fig, 10.5, 4.5, 10.5, 3)
        leader_target = (10.5, 4.5) # Apunta a cota
            
    else: # SUPERFICIE
        draw_rect(fig, 3, 2, 6, 3, width=3)
        leader_target = (6, 5) # Apunta superficie

    # --- MARCO ---
    frame_x, frame_y = 9, 8
    elbow_x = frame_x - 1
    
    # Línea líder
    fig.add_trace(go.Scatter(x=[leader_target[0], elbow_x, frame_x], y=[leader_target[1], frame_y+0.5, frame_y+0.5], mode='lines', line=dict(color='black', width=1.5), showlegend=False))
    draw_arrow(fig, elbow_x, frame_y+0.5, leader_target[0], leader_target[1])
    
    # Cajas
    w = 1.5
    draw_rect(fig, frame_x, frame_y, w, 1, width=2)
    fig.add_annotation(x=frame_x+w/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=24), showarrow=False)
    
    draw_rect(fig, frame_x+w, frame_y, w+0.5, 1, width=2)
    val = f"Ø {tol_val}" if ftype=='axis' else str(tol_val)
    fig.add_annotation(x=frame_x+w*1.2, y=frame_y+0.5, text=f"<b>{val}</b>", font=dict(size=18), showarrow=False)
    
    if datum:
        draw_rect(fig, frame_x+2*w+0.5, frame_y, w, 1, width=2)
        fig.add_annotation(x=frame_x+2*w+0.5+w/2, y=frame_y+0.5, text=f"<b>{datum[0]}</b>", font=dict(size=18), showarrow=False)

    return fig

# --- VISTA 4: CONSTRUCTOR ---
def draw_master(active_features):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro", is_3d=False))
    
    x=[1,11,11,9,9,4,4,1,1]; y=[1,1,3,3,5,5,8,8,1]
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black', width=3), showlegend=False))
    draw_line(fig, 0.5, 6.5, 11.5, 6.5, dash='longdashdot') # Eje
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20, ax=0)
    
    locs = {'Rectitud':(7,1,7,0), 'Posición':(3,6.5,3,9), 'Planicidad':(6,3,6,5), 'Perpendicularidad':(1,5,-1,5), 'Angularidad':(10,4,12,5)}
    
    for feat in active_features:
        if feat in locs:
            tx, ty, fx, fy = locs[feat]
            info = gdt_db[feat]
            draw_rect(fig, fx, fy, 4, 1, width=2)
            txt = f"{info['symbol']} 0.1 {info.get('datum','') if info.get('datum') else ''}"
            fig.add_annotation(x=fx+2, y=fy+0.5, text=f"<b>{txt}</b>", font=dict(size=16), showarrow=False)
            draw_arrow(fig, fx, fy+0.5, tx, ty)
    return fig

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Menú GD&T")
st.sidebar.markdown("---")

mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5)
    view = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    ukey = f"{feat}_{view}_{tol}_{time.time()}"
    info = gdt_db[feat]

    # TARJETA INFORMATIVA
    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #0055a4;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p><strong>Aplicación:</strong> {info.get('app', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if view == "📐 Simulación 3D":
        st.plotly_chart(plot_3d(feat, tol), use_container_width=True, key=ukey)
        st.info(f"Detalle: {gdt_db[feat].get('sim_3d_desc', '')}")
    elif view == "🏭 Montaje Real":
        st.plotly_chart(plot_real_anim(feat), use_container_width=True, key=ukey)
        st.info(f"Procedimiento: {gdt_db[feat].get('real_desc', '')}")
    elif view == "📝 Plano Técnico":
        st.plotly_chart(draw_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=ukey)
        st.markdown(f"""<div class='blueprint-box'><b>Interpretación:</b> La cota controla <b>{info['desc']}</b> dentro de una zona de <b>{info['zone']}</b> de valor {tol} mm.</div>""", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    sel = st.sidebar.multiselect("Agregar cotas:", list(gdt_db.keys()), default=['Rectitud', 'Posición'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
