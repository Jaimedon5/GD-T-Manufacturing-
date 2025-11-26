import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab")

# ==========================================
# 0. ESTILOS CSS (BLINDADOS PARA VISIBILIDAD)
# ==========================================
# Usamos variables CSS para forzar alto contraste sin importar el tema del usuario
st.markdown("""
<style>
    /* FONDO GENERAL */
    .stApp {
        background-color: #e6e6ea; /* Gris ingeniería suave */
    }
    
    /* BARRA LATERAL */
    [data-testid="stSidebar"] {
        background-color: #111111; /* Negro industrial */
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important; /* Texto blanco forzado */
    }
    
    /* CORRECCIÓN DE INPUTS (Cajas de selección) */
    /* Esto arregla que no se vea el texto seleccionado */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* TARJETAS DE INFORMACIÓN (Estilo Ficha Técnica) */
    .info-card {
        background-color: #ffffff;
        border-left: 6px solid #0055a4; /* Azul fuerte */
        padding: 15px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 15px;
        color: #000000;
    }
    
    /* TÍTULOS PRINCIPALES */
    h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Arial', sans-serif;
    }
    
    /* TEXTO GENERAL */
    p, li, span {
        color: #000000 !important;
    }
    
    /* ÁREA DE GRÁFICOS */
    .plot-container {
        border: 1px solid #ccc;
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (CONTENIDO TÉCNICO PDF)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta.',
        'desc': 'Rectitud de superficie', 
        'zone': 'Dos líneas paralelas',
        'type': 'surf'
    },
    'Planicidad': {
        'symbol': '⏥', 
        'def': 'Condición donde todos los puntos de una superficie están en un solo plano.',
        'desc': 'Planicidad', 
        'zone': 'Dos planos paralelos',
        'type': 'surf'
    },
    'Redondez': {
        'symbol': '○', 
        'def': 'Condición donde todos los puntos de una superficie circular (corte) equidistan de un centro.',
        'desc': 'Circularidad (2D)', 
        'zone': 'Dos círculos concéntricos',
        'type': 'axis' # Aunque es superficie, se acota al diametro a veces, pero ASME prefiere superficie. Trataremos como surf para flecha directa
    },
    'Cilindricidad': {
        'symbol': '⌭', 
        'def': 'Condición de una superficie de revolución donde todos los puntos equidistan de un eje común.',
        'desc': 'Cilindricidad (3D)', 
        'zone': 'Dos cilindros coaxiales',
        'type': 'surf' # Toca la superficie
    },
    'Perpendicularidad': {
        'symbol': '⟂', 
        'def': 'Condición donde una superficie, eje o plano está a 90° de un Datum.',
        'desc': 'Perpendicularidad', 
        'zone': 'Dos planos paralelos a 90°',
        'datum': 'A',
        'type': 'surf'
    },
    'Angularidad': {
        'symbol': '∠', 
        'def': 'Condición donde una superficie o eje está a un ángulo específico (básico) del Datum.',
        'desc': 'Angularidad', 
        'zone': 'Dos planos paralelos inclinados',
        'datum': 'A',
        'type': 'surf'
    },
    'Paralelismo': {
        'symbol': '∥', 
        'def': 'Condición donde todos los puntos de una superficie son equidistantes de un plano Datum.',
        'desc': 'Paralelismo', 
        'zone': 'Dos planos paralelos',
        'datum': 'A',
        'type': 'surf'
    },
    'Posición': {
        'symbol': '⌖', 
        'def': 'Controla la ubicación exacta del centro de una característica de tamaño.',
        'desc': 'Posición', 
        'zone': 'Cilindro (si tiene Ø) centrado en la teórica',
        'datum': 'A B C',
        'type': 'axis' # Toca la cota
    },
    'Concentricidad': {
        'symbol': '◎', 
        'def': 'Controla que los puntos medios de secciones opuestas sean coaxiales al Datum.',
        'desc': 'Concentricidad', 
        'zone': 'Cilindro coaxial',
        'datum': 'A',
        'type': 'axis'
    },
    'Alabeo Circular': {
        'symbol': '↗', 
        'def': 'Controla la variación circular de una superficie al girar sobre un eje Datum.',
        'desc': 'Runout Circular', 
        'zone': 'Distancia radial en la sección',
        'datum': 'A-B',
        'type': 'surf' # Toca superficie
    },
    'Alabeo Total': {
        'symbol': '⌰', 
        'def': 'Controla la variación de toda la superficie al girar y desplazarse sobre un eje Datum.',
        'desc': 'Runout Total', 
        'zone': 'Distancia radial total',
        'datum': 'A-B',
        'type': 'surf'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 
        'def': 'Controla la forma de una línea curva en una sección transversal.',
        'desc': 'Perfil de línea', 
        'zone': 'Banda uniforme 2D',
        'type': 'surf'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 
        'def': 'Controla la forma de una superficie 3D.',
        'desc': 'Perfil de superficie', 
        'zone': 'Banda uniforme 3D',
        'type': 'surf'
    }
}

# ==========================================
# 2. FUNCIONES GRÁFICAS (HELPERS)
# ==========================================
def get_layout(title, is_3d=True):
    """Diseño limpio y forzado a blanco/negro para evitar errores de tema"""
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='black'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=550,
        autosize=True
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            xaxis=dict(visible=False, backgroundcolor='white'),
            yaxis=dict(visible=False, backgroundcolor='white'),
            zaxis=dict(visible=True, backgroundcolor='white', gridcolor="#ddd", title='')
        )
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="black", borderwidth=1, font=dict(color="black"))
    else:
        # Plano 2D
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 12], scaleanchor='y')
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 8])
        # Marco de la hoja
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0.01, y0=0.01, x1=0.99, y1=0.99, line=dict(color='black', width=2))]
    return layout

def draw_line(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), hoverinfo='skip', showlegend=False))

def draw_rect(fig, x0, y0, w, h, color="black", fill=None, width=2):
    x = [x0, x0+w, x0+w, x0, x0]
    y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), hoverinfo='skip', showlegend=False))

def draw_arrow(fig, x_tail, y_tail, x_head, y_head):
    fig.add_annotation(x=x_head, y=y_head, ax=x_tail, ay=y_tail, xref='x', yref='y', axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# ==========================================
# 3. SIMULACIONES 3D (GEOMETRÍAS REALES)
# ==========================================
def plot_3d(feature, tol):
    fig = go.Figure()
    
    # Mallas base
    res = 40
    z = np.linspace(0, 10, res)
    theta = np.linspace(0, 2*np.pi, res)
    tg, zg = np.meshgrid(theta, z)

    if feature == 'Rectitud':
        # Eje "Banana" (2D en espacio 3D)
        x_real = 0.4 * np.sin(z * 0.5)
        fig.add_trace(go.Scatter3d(x=x_real, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=12), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol)*np.cos(tg), y=(tol)*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Tolerancia'))

    elif feature == 'Planicidad':
        # Superficie ondulada
        x = np.linspace(-5, 5, res); y = np.linspace(-5, 5, res); xg, yg = np.meshgrid(x, y)
        z_real = 0.2 * np.sin(xg) * np.cos(yg)
        fig.add_trace(go.Surface(z=z_real, x=xg, y=yg, colorscale='Viridis', name='Sup. Real'))
        # Planos límite
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))

    elif feature == 'Redondez':
        # Anillo lobulado (2D)
        th = np.linspace(0, 2*np.pi, 100)
        r_dev = 5 + 0.4*np.sin(4*th)
        fig.add_trace(go.Scatter3d(x=r_dev*np.cos(th), y=r_dev*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=10), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th), y=(5+tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Límites'))
        fig.add_trace(go.Scatter3d(x=(5-tol)*np.cos(th), y=(5-tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), showlegend=False))
        fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2.5)))

    elif feature == 'Cilindricidad':
        # Cilindro deforme (Barril)
        r_dev = 5 + 0.3*np.sin(zg * 0.5)
        fig.add_trace(go.Surface(x=r_dev*np.cos(tg), y=r_dev*np.sin(tg), z=zg, colorscale='Spectral', name='Sup. Real'))
        # Cilindros límite
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Zona Tol'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.full_like(theta, 10), line=dict(color='red'), showlegend=False))

    elif feature == 'Angularidad':
        # Plano inclinado
        x = np.linspace(0, 10, 20); y = np.linspace(0, 10, 20); xg, yg = np.meshgrid(x, y)
        z_nom = xg * np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom, colorscale='Plasma', name='Plano 30°'))
        # Limites
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom+tol, opacity=0.2, colorscale='Greens', showscale=False))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom-tol, opacity=0.2, colorscale='Greens', showscale=False))

    elif feature == 'Posición':
        # Placa con agujero desplazado
        x = np.linspace(-5, 5, 20); y = np.linspace(-5, 5, 20); xg, yg = np.meshgrid(x, y)
        fig.add_trace(go.Surface(x=xg, y=yg, z=np.zeros_like(xg), opacity=0.2, colorscale='Greys', showscale=False))
        # Eje real (Desviado)
        fig.add_trace(go.Scatter3d(x=[1, 1], y=[1, 1], z=[-2, 5], line=dict(color='red', width=10), name='Eje Real'))
        # Eje nominal
        fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-2, 5], line=dict(color='black', dash='dash', width=5), name='Centro Ideal'))
        # Zona
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='YlOrRd', showscale=False, name='Zona Tol'))

    else:
        # Fallback (Cilindro genérico para Alabeos/Concentricidad)
        r = 5
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Blues', opacity=0.8))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='longdash', width=5), name='Datum Axis'))

    fig.update_layout(**get_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMACIONES CORRECTAS)
# ==========================================
def plot_real_anim(feature):
    fig = go.Figure()
    layout = get_layout(f"Montaje de Inspección: {feature}", is_3d=False)
    # Botón de Play
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)
    
    frames = []
    
    if feature == 'Angularidad':
        # MESA DE SENOS (SINE BAR)
        # Base
        draw_rect(fig, 0, 0, 10, 0.5, color="black", fill="#ddd") # Mesa granito
        # Rodillos de la mesa de senos
        draw_trace_circle(fig, 2, 1, 0.5) # Rodillo 1
        draw_trace_circle(fig, 8, 3, 0.5) # Rodillo 2 (Elevado)
        # Bloques patrón (Gage blocks) bajo rodillo 2
        draw_rect(fig, 7.5, 0.5, 1, 2, color="blue", fill="blue") 
        fig.add_annotation(x=8, y=1.5, text="Bloques", font=dict(color="white"))
        # Barra de senos (Inclinada)
        fig.add_trace(go.Scatter(x=[2, 8], y=[1.5, 3.5], mode='lines', line=dict(color='black', width=5)))
        # Pieza encima (Nivelada horizontalmente gracias a la mesa)
        draw_rect(fig, 2, 3.5, 6, 2, color="black") 
        # Reloj
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines', line=dict(color='red'), name='Reloj'))
        
        # Animación: Deslizamiento horizontal
        for i in range(60):
            x_pos = 2 + i/10
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[5.5, 7], mode='lines+markers', marker=dict(size=15), line=dict(color='red'))
            ]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines+markers', line=dict(color='red')))

    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total']:
        # ROTACIÓN (TORNO/CHUCK)
        draw_rect(fig, 0, 2, 1, 4, color="black", fill="#333") # Chuck
        draw_rect(fig, 1, 3, 8, 2, color="blue") # Pieza Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40))
        
        # Animación: Aguja oscilando
        for i in range(50):
            angle = i * 0.5
            dy = 0.2 * np.sin(angle)
            frames.append(go.Frame(data=[
                go.Scatter(x=[5, 5], y=[5, 6+dy], mode='lines', line=dict(color='red', width=3))
            ]))
        
        # Reloj inicial
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines+markers', marker=dict(size=15, symbol='circle-open'), line=dict(color='red'), name='Indicador'))

    else: 
        # DESLIZAMIENTO (RECTITUD/PLANICIDAD)
        draw_rect(fig, 0, 0, 10, 1, color="black", fill="#ccc") # Mármol
        # Pieza irregular
        x_surf = np.linspace(1, 9, 100)
        y_surf = 2 + 0.2*np.sin(x_surf)
        fig.add_trace(go.Scatter(x=x_surf, y=y_surf, mode='lines', line=dict(color='blue', width=4), name='Sup. Real'))
        
        # Animación
        for i in range(0, 100, 2):
            xi = x_surf[i]; yi = y_surf[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yi+2], mode='lines+markers', marker=dict(size=15), line=dict(color='red'))
            ]))
        
        fig.add_trace(go.Scatter(x=[1, 1], y=[2.2, 4.2], mode='lines+markers', line=dict(color='red'), name='Palpador'))

    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO TÉCNICO (CORRECTO 2D)
# ==========================================
def draw_blueprint(feature, tol_val):
    info = gdt_data[feature]
    ftype = info['type']
    sym = info['symbol']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano de Ingeniería: {feature}", is_3d=False))
    
    # DIBUJO DE LA PIEZA (Simple y Clara)
    if ftype == 'axis': # EJE
        draw_rect(fig, 2, 3, 6, 2, width=3) # Cuerpo eje
        draw_line(fig, 1, 4, 9, 4, width=1, dash='longdashdot') # Centro
        # Cota de tamaño
        draw_line(fig, 8, 3, 9, 3, width=1)
        draw_line(fig, 8, 5, 9, 5, width=1)
        fig.add_annotation(x=8.5, y=4, text="Ø 20 ±0.1", font=dict(size=14, color="black"), showarrow=False)
        draw_arrow(fig, 8.5, 4.2, 8.5, 5)
        draw_arrow(fig, 8.5, 3.8, 8.5, 3)
        
        # Flecha a la cota (Correcto para Posición/Cilindricidad)
        leader_target = (8.5, 3.8)
        
    else: # SUPERFICIE (Bloque)
        draw_rect(fig, 3, 2, 6, 3, width=3)
        leader_target = (6, 5) # Apunta a la superficie superior

    # MARCO DE CONTROL
    frame_x = 8; frame_y = 7
    
    # Líder quebrado (Codo)
    elbow_x = frame_x - 1
    fig.add_trace(go.Scatter(x=[leader_target[0], elbow_x, frame_x], y=[leader_target[1], frame_y+0.5, frame_y+0.5], mode='lines', line=dict(color='black', width=1.5), showlegend=False))
    draw_arrow(fig, elbow_x, frame_y+0.5, leader_target[0], leader_target[1])

    # Cajas
    w = 1.2
    draw_rect(fig, frame_x, frame_y, w, 1, width=2)
    fig.add_annotation(x=frame_x+w/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=22, color="black"), showarrow=False)
    
    draw_rect(fig, frame_x+w, frame_y, w+0.5, 1, width=2)
    t_val = f"Ø {tol_val}" if ftype == 'axis' else str(tol_val)
    fig.add_annotation(x=frame_x+w*1.2, y=frame_y+0.5, text=f"<b>{t_val}</b>", font=dict(size=18, color="black"), showarrow=False)
    
    if datum:
        draw_rect(fig, frame_x+2*w+0.5, frame_y, w, 1, width=2)
        fig.add_annotation(x=frame_x+2*w+0.5+w/2, y=frame_y+0.5, text=f"<b>{datum[0]}</b>", font=dict(size=18, color="black"), showarrow=False)

    return fig

# ==========================================
# VISTA 4: CONSTRUCTOR (CHECKLIST)
# ==========================================
def draw_master(selected_features):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro Interactivo", is_3d=False))
    
    # Pieza Maestra (Bloque con Agujero y Chaflán)
    x_p = [1, 9, 9, 7, 1, 1]
    y_p = [1, 1, 4, 6, 6, 1]
    fig.add_trace(go.Scatter(x=x_p, y=y_p, mode='lines', line=dict(color='black', width=3), showlegend=False))
    
    # Agujero
    draw_line(fig, 3, 3, 3, 5, dash='longdashdot') # Eje vertical
    
    # Ubicaciones (Hardcoded para que se vea bien)
    locs = {
        'Rectitud': {'x': 4, 'y': 6},      # Cara sup
        'Planicidad': {'x': 5, 'y': 1},    # Base
        'Posición': {'x': 3, 'y': 4},      # Agujero
        'Angularidad': {'x': 8, 'y': 5},   # Chaflán
        'Perpendicularidad': {'x': 9, 'y': 2} # Cara lateral
    }
    
    for i, feat in enumerate(selected_features):
        if feat in locs:
            pt = locs[feat]
            info = gdt_data[feat]
            # Marco flotante a la derecha
            fx = 11; fy = 8 - (i*1.5)
            
            # Líder
            fig.add_trace(go.Scatter(x=[pt['x'], fx], y=[pt['y'], fy+0.5], mode='lines', line=dict(color='black', width=1), showlegend=False))
            draw_arrow(fig, fx, fy+0.5, pt['x'], pt['y'])
            
            # Marco simplificado
            draw_rect(fig, fx, fy, 3, 1, width=2)
            lbl = f"{info['symbol']} 0.1 {info.get('datum','')}"
            fig.add_annotation(x=fx+1.5, y=fy+0.5, text=f"<b>{lbl}</b>", font=dict(size=14, color="black"), showarrow=False)

    return fig

# ==========================================
# INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("---")

mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5)
    
    view_mode = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    # CLAVE ÚNICA (TIMESTAMP) PARA EVITAR CACHÉ Y CONGELAMIENTOS
    ukey = f"{feat}_{view_mode}_{tol}_{time.time()}"
    
    info = gdt_data[feat]
    
    # TARJETA DE INFO (Siempre visible arriba)
    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #0055a4;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p>🛠️ <strong>Aplicación:</strong> {gdt_data[feat].get('app', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if view_mode == "📐 Simulación 3D":
        st.plotly_chart(plot_3d(feat, tol), use_container_width=True, key=ukey)
        st.info(f"💡 Detalle: {gdt_data[feat].get('sim_3d_desc','')}")
        
    elif view_mode == "🏭 Montaje Real":
        st.plotly_chart(plot_real_anim(feat), use_container_width=True, key=ukey)
        st.info(f"💡 Procedimiento: {gdt_data[feat].get('real_desc','')}")
        
    elif view_mode == "📝 Plano Técnico":
        st.plotly_chart(draw_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=ukey)
        st.markdown(f"""
        <div class="interpretation-box">
            <h4>🤓 Interpretación:</h4>
            <p>La cota controla <b>{info['desc']}</b>. El error no debe exceder <b>{tol} mm</b> dentro de una zona de <b>{info['zone']}</b>.</p>
        </div>
        """, unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    st.sidebar.success("Modo Constructor Activo")
    feats = ['Rectitud', 'Planicidad', 'Posición', 'Angularidad', 'Perpendicularidad']
    sel = st.sidebar.multiselect("Agregar al plano:", feats, default=['Rectitud'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
