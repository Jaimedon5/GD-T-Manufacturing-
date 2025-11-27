import streamlit as st
import plotly.graph_objects as go
import numpy as np
import uuid
import time

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab")

# --- 2. ESTILOS CSS (CORREGIDOS Y BLINDADOS) ---
st.markdown("""
<style>
    /* Fondo y Texto Base */
    .stApp { background-color: #E0E0E0; color: #000000; }
    
    /* Barra Lateral Negra */
    [data-testid="stSidebar"] { background-color: #121212; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Corrección de Menús Desplegables (Texto Negro en Fondo Blanco) */
    .stSelectbox div[data-baseweb="select"] > div, 
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    div[data-baseweb="select"] span { color: #000000 !important; }
    div[data-baseweb="popover"] { background-color: #FFFFFF; color: #000000; }
    
    /* Tarjetas de Información */
    .info-card {
        background-color: #FFFFFF;
        border-left: 8px solid #004B87;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        color: #000000;
    }
    
    /* Caja de Interpretación de Plano */
    .blueprint-box {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        border-left: 6px solid #2196F3;
        padding: 15px;
        border-radius: 4px;
        color: #0D47A1;
        font-family: 'Courier New', monospace;
        margin-top: 15px;
    }
    
    /* Títulos y Textos */
    h1, h2, h3 { color: #000000 !important; }
    p, li { color: #333333 !important; }
    
    /* Icono Grande */
    .big-icon {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        color: #333;
        display: flex; align-items: center; justify-content: center;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS MAESTRA (GD_DATA) ---
# Claves estandarizadas: symbol, def, app, geo, type, datum, desc, zone
GD_DATA = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': None,
        'def': 'Condición donde un elemento lineal es una línea recta.',
        'app': 'Vástagos, ejes largos, rieles.', 'geo': 'shaft_banana',
        'desc': 'rectitud', 'zone': 'Cilíndrica (eje) o dos líneas paralelas (superficie)'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': None,
        'def': 'Todos los puntos de una superficie están en un solo plano.',
        'app': 'Mesas de granito, culatas, sellos.', 'geo': 'plate_wavy',
        'desc': 'planicidad', 'zone': 'Dos planos paralelos'
    },
    'Redondez': {
        'symbol': '○', 'type': 'surf', 'datum': None,
        'def': 'Puntos de una sección circular equidistantes del centro.',
        'app': 'Rodamientos, muñones.', 'geo': 'ring_lobed',
        'desc': 'circularidad', 'zone': 'Dos círculos concéntricos'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'surf', 'datum': None,
        'def': 'Controla redondez, rectitud y conicidad (3D).',
        'app': 'Pistones, cilindros hidráulicos.', 'geo': 'cylinder_barrel',
        'desc': 'cilindricidad', 'zone': 'Dos cilindros coaxiales'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'orient', 'datum': 'A',
        'def': 'Superficie o eje a 90° de un Datum.',
        'app': 'Escuadras, bridas.', 'geo': 'L_bracket',
        'desc': 'perpendicularidad', 'zone': 'Dos planos o cilindro a 90°'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'orient', 'datum': 'A',
        'def': 'Superficie o eje a un ángulo básico del Datum.',
        'app': 'Guías en V, rampas.', 'geo': 'wedge',
        'desc': 'inclinación angular', 'zone': 'Dos planos paralelos inclinados'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'orient', 'datum': 'A',
        'def': 'Puntos equidistantes de un plano Datum.',
        'app': 'Rieles, ranuras.', 'geo': 'block_parallel',
        'desc': 'paralelismo', 'zone': 'Dos planos paralelos al Datum'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'loc', 'datum': 'A B C',
        'def': 'Ubicación exacta del centro de una característica.',
        'app': 'Agujeros de pernos.', 'geo': 'plate_hole',
        'desc': 'posición del centro', 'zone': 'Cilindro centrado en la teórica'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'loc', 'datum': 'A',
        'def': 'Coaxialidad de puntos medios (Balanceo).',
        'app': 'Rotores de alta velocidad.', 'geo': 'concentric',
        'desc': 'concentricidad', 'zone': 'Cilindro coaxial'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'runout', 'datum': 'A-B',
        'def': 'Variación en una sección al girar.',
        'app': 'Discos de freno.', 'geo': 'shaft_runout',
        'desc': 'alabeo circular', 'zone': 'Distancia radial (2D)'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'runout', 'datum': 'A-B',
        'def': 'Variación total de superficie al girar.',
        'app': 'Ejes de bombas.', 'geo': 'shaft_runout',
        'desc': 'alabeo total', 'zone': 'Distancia radial (3D)'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'profile', 'datum': None,
        'def': 'Forma de una curva 2D.',
        'app': 'Alas de avión.', 'geo': 'curved_surf',
        'desc': 'perfil de línea', 'zone': 'Banda uniforme 2D'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'profile', 'datum': None,
        'def': 'Forma de superficie 3D.',
        'app': 'Moldes, carrocerías.', 'geo': 'curved_surf',
        'desc': 'perfil de superficie', 'zone': 'Banda uniforme 3D'
    }
}

# --- 4. FUNCIONES GRÁFICAS ---

def create_canvas(title, is_3d=True):
    """Crea el lienzo base limpio"""
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor='white', plot_bgcolor='white',
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=550,
        autosize=True
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
        layout['xaxis'] = dict(visible=False, range=[-1, 12], showgrid=False)
        layout['yaxis'] = dict(visible=False, range=[-2, 8], showgrid=False, scaleanchor='x')
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0.01, y0=0.01, x1=0.99, y1=0.99, line=dict(color='black', width=2))]
    return layout

# --- Primitivas de Dibujo (Trace-based para que no desaparezcan) ---
def add_rect(fig, x, y, w, h, color='black', fill=None, width=2):
    x_pts = [x, x+w, x+w, x, x]
    y_pts = [y, y, y+h, y+h, y]
    f = 'toself' if fill else 'none'
    fig.add_trace(go.Scatter(x=x_pts, y=y_pts, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), hoverinfo='skip', showlegend=False))

def add_line(fig, x0, y0, x1, y1, color='black', width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), hoverinfo='skip', showlegend=False))

def add_leader(fig, x_target, y_target, x_box, y_box):
    # Dibuja una flecha líder sólida
    fig.add_annotation(
        x=x_target, y=y_target, ax=x_box, ay=y_box,
        xref='x', yref='y', axref='x', ayref='y',
        arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor='black'
    )

def add_gdt_frame(fig, x, y, sym, tol, datum):
    w_s, w_t, w_d = 1.2, 1.8, 1.2
    h = 1.0
    # Símbolo
    add_rect(fig, x, y, w_s, h, width=2)
    fig.add_annotation(x=x+w_s/2, y=y+h/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=22, color='black'))
    # Tolerancia
    add_rect(fig, x+w_s, y, w_t, h, width=2)
    fig.add_annotation(x=x+w_s+w_t/2, y=y+h/2, text=f"<b>{tol}</b>", showarrow=False, font=dict(size=18, color='black'))
    # Datum
    if datum:
        add_rect(fig, x+w_s+w_t, y, w_d, h, width=2)
        fig.add_annotation(x=x+w_s+w_t+w_d/2, y=y+h/2, text=f"<b>{datum[0]}</b>", showarrow=False, font=dict(size=18, color='black'))
        return x + w_s + w_t + w_d
    return x + w_s + w_t

# --- GRAFICADOR 3D ---
def plot_3d(feature, tol):
    fig = go.Figure()
    geo = GD_DATA[feature]['geo']
    
    res = 35
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res); tg, zg = np.meshgrid(theta, z)

    if feature == 'Rectitud': # Eje banana
        x_r = 0.4 * np.sin(z*0.5)
        fig.add_trace(go.Scatter3d(x=x_r, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', name='Tol'))
        
    elif feature == 'Planicidad': # Superficie ondulada
        x = np.linspace(-5,5,res); y=np.linspace(-5,5,res); xg,yg=np.meshgrid(x,y)
        z_r = 0.2*np.sin(xg)*np.cos(yg)
        fig.add_trace(go.Surface(z=z_r, x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))

    elif geo == 'ring_lobed': # Redondez
        th = np.linspace(0, 2*np.pi, 100)
        r = 5 + 0.3*np.sin(5*th)
        fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=8), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th), y=(5+tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Lim'))
        fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2.5)))
        
    elif geo == 'L_bracket': # Perpendicularidad
        y_w=np.linspace(0,8,res); x_w=np.linspace(-4,4,res); Y,X=np.meshgrid(y_w,x_w)
        fig.add_trace(go.Surface(x=X, y=Y, z=0.5*Y/8, colorscale='Blues', name='Pared'))
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.4, colorscale='Greys', name='Datum'))
        
    elif geo == 'wedge': # Angularidad
        x=np.linspace(0,10,res); y=np.linspace(0,10,res); xg,yg=np.meshgrid(x,y)
        z_nom = xg*np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom, colorscale='Plasma', name='Real'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom+tol, opacity=0.2, colorscale='Greens', showscale=False))
        
    else: # Default Cilindro
        r = 5
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', opacity=0.8))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', width=5, dash='dash'), name='Datum'))

    fig.update_layout(**create_canvas(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# --- GRAFICADOR REAL (ANIMADO) ---
def plot_real(feature):
    fig = go.Figure()
    layout = create_canvas(f"Inspección: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.1, y=0, buttons=[dict(label="▶️ Play", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)
    
    frames = []
    geo = GD_DATA[feature]['geo']
    
    if feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        # Rotación
        add_rect(fig, 0, 2, 1, 4, color="black", fill="#444") # Chuck
        add_rect(fig, 1, 3, 8, 2, color="blue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40, color='white'))
        # Reloj
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines', line=dict(color='gray', width=3)))
        # Animacion aguja
        for i in range(50):
            dy = 0.3*np.sin(i*0.5)
            frames.append(go.Frame(data=[go.Scatter(x=[5, 5], y=[6, 7.5+dy], mode='lines', line=dict(color='red', width=3))]))
        fig.add_trace(go.Scatter(x=[5, 5], y=[6, 7.5], mode='lines', line=dict(color='red', width=3)))
        
    elif feature == 'Angularidad':
        # Mesa senos
        add_rect(fig, 0, 0, 10, 0.5, fill="#ccc") 
        fig.add_trace(go.Scatter(x=[2, 8], y=[1, 3], mode='markers', marker=dict(size=20, color='black')))
        add_line(fig, 2, 1.5, 8, 3.5, width=5)
        add_rect(fig, 2, 3.5, 6, 2, color="black") # Pieza
        # Animacion deslizamiento
        for i in range(50):
            x = 2 + i/10
            frames.append(go.Frame(data=[go.Scatter(x=[x, x], y=[5.5, 7], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines+markers', line=dict(color='red')))
        
    else: # Deslizamiento
        add_rect(fig, 0, 0, 10, 1, fill="#ccc")
        x_s = np.linspace(1, 9, 100); y_s = 2 + 0.2*np.sin(x_s)
        fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='lines', line=dict(color='blue'), name='Sup'))
        for i in range(0, 100, 2):
            frames.append(go.Frame(data=[go.Scatter(x=[x_s[i], x_s[i]], y=[y_s[i], y_s[i]+2], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red')))

    fig.frames = frames
    return fig

# --- PLANO TÉCNICO ---
def draw_blueprint(feature, tol):
    info = GD_DATA[feature]
    ftype = info['type']
    sym = info['symbol']
    datum = info['datum']
    
    fig = go.Figure()
    fig.update_layout(**create_canvas(f"Plano: {feature}", is_3d=False))
    
    # Pieza
    if ftype == 'axis': # Eje
        add_rect(fig, 2, 3, 8, 4)
        add_line(fig, 1, 5, 11, 5, dash='longdashdot')
        add_line(fig, 10, 3, 11, 3, width=1); add_line(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", showarrow=False, font=dict(color='black'))
        add_leader(fig, 10.5, 5.5, 10.5, 7); add_leader(fig, 10.5, 4.5, 10.5, 3)
        target = (10.5, 4.5) # Apunta a cota
    else: # Superficie
        add_rect(fig, 3, 2, 6, 3)
        target = (6, 5) # Apunta superficie
        
    # Marco
    fx, fy = 9, 8
    # Línea codo sólida
    fig.add_trace(go.Scatter(x=[target[0], fx-1, fx], y=[target[1], fy+0.5, fy+0.5], mode='lines', line=dict(color='black', width=1.5), showlegend=False))
    add_leader(fig, target[0], target[1], fx-1, fy+0.5)
    
    val = f"Ø {tol}" if ftype=='axis' else str(tol)
    add_gdt_frame(fig, fx, fy, info['symbol'], val, info['datum'])
    
    return fig

# --- CONSTRUCTOR ---
def draw_master(active):
    fig = go.Figure()
    fig.update_layout(**create_canvas("Plano Maestro", is_3d=False))
    
    # Pieza compleja
    pts_x = [1, 11, 11, 9, 9, 4, 4, 1, 1]; pts_y = [1, 1, 3, 3, 5, 5, 8, 8, 1]
    fig.add_trace(go.Scatter(x=pts_x, y=pts_y, mode='lines', line=dict(color='black', width=3), showlegend=False))
    add_line(fig, 0.5, 6.5, 11.5, 6.5, dash='longdashdot') # Eje central
    
    # Datum A
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20)
    
    locs = {'Rectitud':(7,1,7,0), 'Posición':(3,6.5,3,9), 'Planicidad':(6,3,6,5), 'Perpendicularidad':(1,5,-1,5), 'Angularidad':(10,4,12,5)}
    
    for f in active:
        if f in locs:
            tx, ty, fx, fy = locs[f]
            info = GD_DATA[f]
            # Marco
            val = "0.1"
            dat = info['datum'] if info['datum'] else ""
            add_gdt_frame(fig, fx, fy, info['symbol'], val, dat)
            # Líder
            fig.add_trace(go.Scatter(x=[tx, fx], y=[ty, fy+0.5], mode='lines', line=dict(color='black', width=1), showlegend=False))
            add_leader(fig, tx, ty, fx, fy+0.5)
            
    return fig

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Menú GD&T")
mode = st.sidebar.radio("Modo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5)
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Plano Técnico"])
    
    ukey = f"{feat}_{view}_{tol}_{time.time()}"
    info = GD_DATA[feat]

    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #004B87;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p><strong>Aplicación:</strong> {info.get('app', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if view == "Simulación 3D":
        st.plotly_chart(plot_3d(feat, tol), use_container_width=True, key=ukey)
    elif view == "Montaje Real":
        st.plotly_chart(plot_real(feat), use_container_width=True, key=ukey)
    elif view == "Plano Técnico":
        st.plotly_chart(draw_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=ukey)
        st.markdown(f"<div class='blueprint-box'><b>Interpretación:</b> {info['desc']} dentro de una zona de <b>{info['zone']}</b>.</div>", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    sel = st.sidebar.multiselect("Agregar cotas:", list(GD_DATA.keys()), default=['Rectitud'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
