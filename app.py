import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import uuid

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab")

# ==========================================
# 0. ESTILOS CSS (BLINDADOS)
# ==========================================
st.markdown("""
<style>
    /* FONDO Y TEXTO BASE */
    .stApp { background-color: #E0E0E0; color: black; }
    
    /* SIDEBAR NEGRO, TEXTO BLANCO */
    [data-testid="stSidebar"] { background-color: #121212; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* CORRECCIÓN DE INPUTS (Fondo Blanco, Texto Negro) */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    div[data-baseweb="popover"] { background-color: white; color: black; }
    div[data-baseweb="select"] span { color: black !important; }
    
    /* TARJETAS */
    .info-card {
        background-color: white;
        border-left: 8px solid #0055A4;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: black;
    }
    
    .blueprint-box {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        color: #0D47A1;
        margin-top: 10px;
    }
    
    /* TEXTOS GENERALES */
    h1, h2, h3, p, li { color: black !important; }
    
    .big-icon {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (CLAVES UNIFICADAS 'symbol')
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde un elemento lineal es una línea recta.',
        'app': 'Vástagos, rieles.', 'geo': 'shaft_banana',
        'desc': 'la rectitud del eje/superficie', 'zone': 'Cilindro (si es eje) o dos líneas paralelas'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Todos los puntos de una superficie en un solo plano.',
        'app': 'Mesas, culatas.', 'geo': 'plate_wavy',
        'desc': 'la planicidad', 'zone': 'Dos planos paralelos'
    },
    'Redondez': {
        'symbol': '○', 'type': 'surf', 'datum': False,
        'def': 'Puntos de una sección circular equidistantes del centro.',
        'app': 'Rodamientos.', 'geo': 'ring_lobed',
        'desc': 'la circularidad (2D)', 'zone': 'Dos círculos concéntricos'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'surf', 'datum': False,
        'def': 'Controla redondez, rectitud y conicidad (3D).',
        'app': 'Pistones.', 'geo': 'cylinder_barrel',
        'desc': 'la cilindricidad total', 'zone': 'Dos cilindros coaxiales'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'orient', 'datum': 'A',
        'def': 'Superficie o eje a 90° de un Datum.',
        'app': 'Escuadras.', 'geo': 'L_bracket',
        'desc': 'la perpendicularidad', 'zone': 'Dos planos/cilindro a 90°'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'orient', 'datum': 'A',
        'def': 'Superficie o eje a un ángulo básico del Datum.',
        'app': 'Guías en V.', 'geo': 'wedge',
        'desc': 'la inclinación angular', 'zone': 'Dos planos paralelos inclinados'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'orient', 'datum': 'A',
        'def': 'Puntos equidistantes de un plano Datum.',
        'app': 'Rieles.', 'geo': 'block_parallel',
        'desc': 'el paralelismo', 'zone': 'Dos planos paralelos al Datum'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'loc', 'datum': 'A B C',
        'def': 'Ubicación exacta del centro de una característica.',
        'app': 'Agujeros de pernos.', 'geo': 'plate_hole',
        'desc': 'la posición del centro', 'zone': 'Cilindro centrado en la teórica'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'loc', 'datum': 'A',
        'def': 'Coaxialidad de puntos medios (Balanceo).',
        'app': 'Rotores.', 'geo': 'concentric',
        'desc': 'la concentricidad', 'zone': 'Cilindro coaxial'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'runout', 'datum': 'A-B',
        'def': 'Variación en una sección al girar.',
        'app': 'Frenos.', 'geo': 'shaft_runout',
        'desc': 'el alabeo circular', 'zone': 'Distancia radial (2D)'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'runout', 'datum': 'A-B',
        'def': 'Variación total de superficie al girar.',
        'app': 'Ejes bomba.', 'geo': 'shaft_runout',
        'desc': 'el alabeo total', 'zone': 'Distancia radial (3D)'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'profile', 'datum': False,
        'def': 'Forma de una curva 2D.',
        'app': 'Alas.', 'geo': 'curved_surf',
        'desc': 'el perfil de línea', 'zone': 'Banda uniforme 2D'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'profile', 'datum': False,
        'def': 'Forma de superficie 3D.',
        'app': 'Moldes.', 'geo': 'curved_surf',
        'desc': 'el perfil de superficie', 'zone': 'Banda uniforme 3D'
    }
}

# ==========================================
# 2. GRAFICADORES
# ==========================================
def get_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor='white', plot_bgcolor='white', font=dict(color='black'),
        margin=dict(l=10, r=10, t=40, b=10), height=550, autosize=True
    )
    if is_3d:
        layout['scene'] = dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6), xaxis=dict(visible=False, backgroundcolor='white'), yaxis=dict(visible=False, backgroundcolor='white'), zaxis=dict(visible=True, backgroundcolor='white', gridcolor="#ccc"))
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 13], scaleanchor='y')
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 8])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))]
    return layout

# --- PRIMITIVAS DE DIBUJO (SCATTERS) ---
def draw_lines(fig, x, y, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color=color, width=width, dash=dash), hoverinfo='skip', showlegend=False))

def draw_rect_shape(fig, x0, y0, w, h, color="black", fill=None):
    x = [x0, x0+w, x0+w, x0, x0]
    y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=2), hoverinfo='skip', showlegend=False))

def draw_arrow_manual(fig, x1, y1, x2, y2):
    fig.add_annotation(x=x2, y=y2, ax=x1, ay=y1, xref='x', yref='y', axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# --- SIMULACIÓN 3D ---
def plot_3d(feature, tol):
    fig = go.Figure()
    geo = gdt_data[feature]['geo']
    res = 30
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res); tg, zg = np.meshgrid(theta, z)
    
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.4*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Tol'))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,res); y=np.linspace(-5,5,res); xg,yg=np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.2*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
    elif geo == 'L_bracket': # Perpendicularidad
        y_w = np.linspace(0,8,res); x_w=np.linspace(-4,4,res); Y,X = np.meshgrid(y_w,x_w)
        fig.add_trace(go.Surface(x=X, y=Y, z=0.5*Y/8, colorscale='Blues', name='Real'))
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.3, showscale=False, name='Datum'))
    elif feature == 'Posición': # Placa
        x = np.linspace(-5,5,20); y=np.linspace(-5,5,20); xg,yg=np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=np.zeros_like(xg), x=xg, y=yg, opacity=0.1, colorscale='Greys', showscale=False))
        fig.add_trace(go.Scatter3d(x=[1,1], y=[1,1], z=[-2,5], line=dict(color='red', width=8), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.3, colorscale='YlOrRd', showscale=False))
    else: # Default Cylinder
        r = 5 + 0.2*np.sin(zg)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        
    fig.update_layout(**get_layout(f"3D: {feature}", is_3d=True))
    return fig

# --- MONTAJE REAL ---
def plot_real(feature):
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Inspección: {feature}", is_3d=False))
    layout = get_layout(f"Inspección: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=40), fromcurrent=True)])])]
    fig.update_layout(**layout)

    frames = []
    
    if feature == 'Angularidad': # Mesa de senos
        draw_rect_shape(fig, 0, 0, 10, 0.5, fill="#aaa") # Base
        draw_lines(fig, [2, 8], [1.5, 3.5], width=5) # Barra
        draw_rect_shape(fig, 7.5, 0.5, 1, 2.5, fill="blue") # Bloque
        draw_rect_shape(fig, 2, 3.5, 6, 2, fill="white") # Pieza
        
        for i in range(50):
            x = 2 + i/10
            frames.append(go.Frame(data=[go.Scatter(x=[x, x], y=[5.5, 7], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total']:
        draw_rect_shape(fig, 0, 2, 1, 4, fill="#333") # Chuck
        draw_rect_shape(fig, 1, 3, 8, 2, fill="lightblue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40))
        
        for i in range(50):
            dy = 0.3 * np.sin(i*0.5)
            frames.append(go.Frame(data=[go.Scatter(x=[5, 5], y=[6, 7.5+dy], mode='lines', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[5, 5], y=[6, 7.5], mode='lines', line=dict(color='red'), name='Aguja'))
        
    else: # Deslizamiento
        draw_rect_shape(fig, 0, 0, 10, 1, fill="#ccc")
        xs = np.linspace(1, 9, 100); ys = 2 + 0.2*np.sin(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='blue'), name='Sup'))
        for i in range(0, 100, 2):
            frames.append(go.Frame(data=[go.Scatter(x=[xs[i], xs[i]], y=[ys[i], ys[i]+2], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    fig.frames = frames
    return fig

def draw_rect_shape(fig, x, y, w, h, color="black", fill=None):
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=[x, x+w, x+w, x, x], y=[y, y, y+h, y+h, y], fill=f, fillcolor=fill, line=dict(color=color), showlegend=False))

# --- PLANO TÉCNICO ---
def draw_blueprint(feature, tol):
    info = gdt_data[feature]
    ftype = info['type']
    sym = info['symbol']
    
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano: {feature}", is_3d=False))

    if ftype == 'axis': # Eje
        draw_rect_shape(fig, 2, 3, 8, 4)
        draw_lines(fig, [1, 11], [5, 5], dash='longdashdot')
        draw_lines(fig, [10, 11], [3, 3], width=1)
        draw_lines(fig, [10, 11], [7, 7], width=1)
        draw_arrow_manual(fig, 10.5, 5.5, 10.5, 7)
        draw_arrow_manual(fig, 10.5, 4.5, 10.5, 3)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", showarrow=False, font=dict(color='black'))
        leader_target = (10.5, 4.5)
    else: # Superficie
        draw_rect_shape(fig, 3, 2, 6, 3)
        leader_target = (6, 5)

    # Marco Control
    fx, fy = 9, 8
    draw_lines(fig, [leader_target[0], fx-1, fx], [leader_target[1], fy+0.5, fy+0.5], width=1.5)
    draw_arrow_manual(fig, fx-1, fy+0.5, leader_target[0], leader_target[1])
    
    # Cajas
    draw_rect_shape(fig, fx, fy, 1.2, 1, fill='white')
    fig.add_annotation(x=fx+0.6, y=fy+0.5, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=20, color='black'))
    draw_rect_shape(fig, fx+1.2, fy, 1.8, 1, fill='white')
    tval = f"Ø {tol}" if ftype=='axis' else str(tol)
    fig.add_annotation(x=fx+2.1, y=fy+0.5, text=f"<b>{tval}</b>", showarrow=False, font=dict(size=16, color='black'))
    
    if info['datum']:
        draw_rect_shape(fig, fx+3, fy, 1.2, 1, fill='white')
        fig.add_annotation(x=fx+3.6, y=fy+0.5, text=f"<b>{info['datum'][0]}</b>", showarrow=False, font=dict(size=16, color='black'))

    return fig

# --- CONSTRUCTOR ---
def draw_master(active):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro", is_3d=False))
    # Pieza
    draw_lines(fig, [1, 11, 11, 9, 9, 4, 4, 1, 1], [1, 1, 3, 3, 5, 5, 8, 8, 1], width=3)
    draw_lines(fig, [0.5, 11.5], [6.5, 6.5], dash='longdashdot')
    
    locs = {'Rectitud':(7,1,7,0), 'Posición':(3,6.5,3,9), 'Planicidad':(6,3,6,5), 'Perpendicularidad':(1,5,-1,5), 'Angularidad':(10,4,12,5)}
    
    for f in active:
        if f in locs:
            tx, ty, fx, fy = locs[f]
            info = gdt_data[f]
            draw_rect_shape(fig, fx, fy, 3.5, 1, fill='white')
            txt = f"{info['symbol']} 0.1 {info['datum'] if info['datum'] else ''}"
            fig.add_annotation(x=fx+1.75, y=fy+0.5, text=f"<b>{txt}</b>", font=dict(color='black'), showarrow=False)
            draw_lines(fig, [tx, fx], [ty, fy+0.5], width=1)
            draw_arrow_manual(fig, fx, fy+0.5, tx, ty)
    return fig

# ==========================================
# INTERFAZ
# ==========================================
st.sidebar.title("🎛️ Menú GD&T")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Modo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia", 0.1, 2.0, 0.5)
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Plano Técnico"])
    
    info = gdt_data[feat]
    ukey = f"{feat}_{view}_{tol}_{time.time()}" # Anti-congelamiento

    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #0055a4;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p><strong>Aplicación:</strong> {info['app']}</p>
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
    sel = st.sidebar.multiselect("Agregar:", list(gdt_data.keys()), default=['Rectitud'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
