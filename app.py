import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import uuid

# --- 1. CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab")

# --- 2. ESTILOS CSS (TEMA "ENGINEERING PRO") ---
st.markdown("""
<style>
    /* Fondo General */
    .stApp { background-color: #E8E8E8; color: black; }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #121212; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Corrección de Inputs (Fondo blanco, texto negro) */
    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
    }
    div[data-baseweb="select"] span { color: black !important; }
    div[data-baseweb="popover"] { background-color: white; color: black; }
    
    /* Tarjetas de Información */
    .info-card {
        background-color: white;
        border-left: 8px solid #004B87;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        margin-bottom: 20px;
        color: #333;
    }
    
    /* Caja de Interpretación de Plano */
    .blueprint-box {
        background-color: #E3F2FD;
        border: 1px solid #2196F3;
        border-left: 6px solid #2196F3;
        padding: 15px;
        border-radius: 4px;
        color: #0D47A1;
        font-family: 'Consolas', monospace;
        margin-top: 15px;
    }
    
    /* Títulos y Textos */
    h1, h2, h3, h4 { color: #000 !important; font-family: 'Segoe UI', sans-serif; }
    p, li { color: #333 !important; }
    
    /* Icono Grande */
    .big-icon {
        font-size: 70px;
        font-weight: bold;
        text-align: center;
        color: #333;
        display: flex; align-items: center; justify-content: center;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. BASE DE DATOS TÉCNICA (GD&T) ---
gdt_db = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde un elemento lineal de una superficie o eje es una línea recta.',
        'app': 'Vástagos de cilindros, ejes de transmisión, rieles.',
        'why': 'Evita desgaste irregular y fugas en sellos.',
        'geo': 'shaft_banana', # Geometría 3D específica
        'desc': 'rectitud', 'zone': 'Dos líneas paralelas'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie están en un solo plano.',
        'app': 'Caras de monoblocks, mesas de granito, bridas.',
        'why': 'Asegura sellado hermético en juntas.',
        'geo': 'plate_wavy',
        'desc': 'planicidad', 'zone': 'Dos planos paralelos'
    },
    'Redondez': {
        'symbol': '○', 'type': 'surf', 'datum': False,
        'def': 'Condición donde los puntos de una sección circular (2D) equidistan del centro.',
        'app': 'Pistas de rodamientos, muñones de cigüeñal.',
        'why': 'Evita vibraciones a altas revoluciones.',
        'geo': 'ring_lobed',
        'desc': 'circularidad', 'zone': 'Dos círculos concéntricos'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma cilíndrica total (Redondez + Rectitud + Conicidad).',
        'app': 'Pistones hidráulicos, pernos maestros.',
        'why': 'Crítica para sistemas de alta presión sin empaques.',
        'geo': 'cylinder_barrel',
        'desc': 'cilindricidad', 'zone': 'Dos cilindros coaxiales'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'orient', 'datum': 'A',
        'def': 'Condición donde una superficie, eje o plano está a 90° de un Datum.',
        'app': 'Escuadras, caras de apoyo.',
        'why': 'Evita desalineación en ensambles.',
        'geo': 'L_bracket',
        'desc': 'perpendicularidad', 'zone': 'Dos planos paralelos a 90°'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'orient', 'datum': 'A',
        'def': 'Condición a un ángulo específico (básico) respecto al Datum.',
        'app': 'Guías de cola de milano, rampas.',
        'why': 'Contacto uniforme en deslizamientos.',
        'geo': 'wedge',
        'desc': 'angularidad', 'zone': 'Dos planos paralelos inclinados'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'orient', 'datum': 'A',
        'def': 'Condición donde todos los puntos equidistan de un plano Datum.',
        'app': 'Rieles de máquinas, caras opuestas.',
        'why': 'Evita atascamientos en partes móviles.',
        'geo': 'block_parallel',
        'desc': 'paralelismo', 'zone': 'Dos planos paralelos'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'loc', 'datum': 'A B C',
        'def': 'Controla la ubicación exacta del centro de una característica de tamaño.',
        'app': 'Patrones de agujeros para pernos.',
        'why': 'Garantiza intercambiabilidad y ensamble.',
        'geo': 'plate_hole',
        'desc': 'posición', 'zone': 'Cilindro en posición teórica'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'loc', 'datum': 'A',
        'def': 'Controla que los puntos medios opuestos sean coaxiales al Datum.',
        'app': 'Rotores de alta velocidad.',
        'why': 'Balanceo dinámico.',
        'geo': 'concentric',
        'desc': 'concentricidad', 'zone': 'Cilindro coaxial'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'runout', 'datum': 'A-B', 
        'def': 'Variación en una sección circular al girar (Runout).',
        'app': 'Discos de freno.', 'why': 'Evita pulsaciones.',
        'geo': 'shaft_runout', 'desc': 'alabeo circular', 'zone': 'Distancia radial (2D)'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'runout', 'datum': 'A-B', 
        'def': 'Variación de toda la superficie al girar.',
        'app': 'Ejes de bombas.', 'why': 'Cero fugas.',
        'geo': 'shaft_runout', 'desc': 'alabeo total', 'zone': 'Distancia radial (Total)'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'profile', 'datum': False, 
        'def': 'Forma de una curva 2D en una sección.',
        'app': 'Alas, levas.', 'why': 'Aerodinámica.',
        'geo': 'curved_surf', 'desc': 'perfil de línea', 'zone': 'Banda uniforme 2D'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'profile', 'datum': False, 
        'def': 'Forma de una superficie 3D compleja.',
        'app': 'Moldes, carrocería.', 'why': 'Estética.',
        'geo': 'curved_surf', 'desc': 'perfil de superficie', 'zone': 'Banda uniforme 3D'
    }
}

# --- 4. FUNCIONES GRÁFICAS (HELPERS) ---
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
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.8)", font=dict(color="black"), x=0.8, y=0.9)
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 12], scaleanchor='y')
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 8])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0.01, y0=0.01, x1=0.99, y1=0.99, line=dict(color='black', width=3))]
    return layout

# Primitivas de dibujo seguro (Traces)
def draw_rect_trace(fig, x0, y0, w, h, color="black", fill=None, width=2):
    x = [x0, x0+w, x0+w, x0, x0]
    y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), hoverinfo='skip', showlegend=False))

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), hoverinfo='skip', showlegend=False))

def draw_arrow_trace(fig, x_tail, y_tail, x_head, y_head):
    fig.add_annotation(x=x_head, y=y_head, ax=x_tail, ay=y_tail, xref='x', yref='y', axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# --- 5. GRAFICADORES PRINCIPALES ---

# A) SIMULACIÓN 3D
def plot_3d(feature, tol):
    fig = go.Figure()
    geo = gdt_db[feature]['geo']
    
    # Mallas
    res = 30
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res); tg, zg = np.meshgrid(theta, z)

    if feature == 'Rectitud': # Eje curvo
        x_real = 0.4 * np.sin(z * 0.5)
        fig.add_trace(go.Scatter3d(x=x_real, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', showscale=False, name='Tol'))

    elif feature == 'Planicidad': # Placa ondulada
        x = np.linspace(-5, 5, res); y = np.linspace(-5, 5, res); xg, yg = np.meshgrid(x, y)
        z_real = 0.2 * np.sin(xg) * np.cos(yg)
        fig.add_trace(go.Surface(z=z_real, x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, colorscale='Reds', showscale=False))

    elif geo == 'L_bracket': # Perpendicularidad
        y_w = np.linspace(0,8,res); x_w=np.linspace(-4,4,res); Y,X = np.meshgrid(y_w,x_w)
        Z_w = (tol*2) * (Y/8) 
        fig.add_trace(go.Surface(x=X, y=Y, z=Z_w, colorscale='Blues', name='Pared'))
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.5, colorscale='Greys', showscale=False, name='Datum'))

    elif geo == 'wedge': # Angularidad
        x = np.linspace(0,10,res); y=np.linspace(0,10,res); xg,yg=np.meshgrid(x,y)
        z_nom = xg * np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom, colorscale='Plasma', name='Plano'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom+tol, opacity=0.2, colorscale='Greens', showscale=False))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom-tol, opacity=0.2, colorscale='Greens', showscale=False))

    elif feature == 'Posición': # Placa con agujero
        x = np.linspace(-5,5,20); y=np.linspace(-5,5,20); xg,yg=np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=np.zeros_like(xg), x=xg, y=yg, opacity=0.2, colorscale='Greys', showscale=False))
        fig.add_trace(go.Scatter3d(x=[1,1], y=[1,1], z=[-2,5], line=dict(color='red', width=8), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-2,5], line=dict(color='black', dash='dash', width=4), name='Teórico'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.3, colorscale='YlOrRd', showscale=False))

    elif feature == 'Redondez': # Aro
        th = np.linspace(0, 2*np.pi, 100)
        r_dev = 5 + 0.4*np.sin(4*th)
        fig.add_trace(go.Scatter3d(x=r_dev*np.cos(th), y=r_dev*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=8)))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(th), y=(5+tol)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash')))
        fig.update_layout(scene_camera=dict(eye=dict(x=0, y=0, z=2.5)))

    else: # Cilindro Default
        r = 5 + 0.2*np.sin(zg)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='dash', width=5), name='Datum'))

    fig.update_layout(**get_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# B) MONTAJE REAL
def plot_real(feature):
    fig = go.Figure()
    layout = get_layout(f"Inspección: {feature}", is_3d=False)
    # Botón Play funcional
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)
    
    frames = []
    
    if feature == 'Angularidad': # Mesa de Senos
        draw_rect_trace(fig, 0, 0, 10, 0.5, color="black", fill="#aaa") # Base
        # Rodillos
        fig.add_trace(go.Scatter(x=[2, 8], y=[1, 3], mode='markers', marker=dict(size=15, color='black'), showlegend=False))
        draw_rect_trace(fig, 7.5, 0.5, 1, 2.5, fill="blue") # Bloques
        fig.add_trace(go.Scatter(x=[2, 8], y=[1.5, 3.5], mode='lines', line=dict(color='black', width=4), showlegend=False)) # Barra
        draw_rect_trace(fig, 2, 3.5, 6, 2, fill="white") # Pieza
        
        # Reloj se desliza
        for i in range(50):
            x = 2 + i/10
            frames.append(go.Frame(data=[go.Scatter(x=[x, x], y=[5.5, 7], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5.5, 7], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total']:
        # Torno
        draw_rect_trace(fig, 0, 2, 1, 4, fill="#333") # Chuck
        draw_rect_trace(fig, 1, 3, 8, 2, fill="lightblue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40))
        
        # Reloj fijo, aguja se mueve
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines', line=dict(color='gray', width=3), name='Soporte'))
        for i in range(50):
            dy = 0.3 * np.sin(i*0.5)
            frames.append(go.Frame(data=[go.Scatter(x=[5, 5], y=[6, 7.5+dy], mode='lines', line=dict(color='red', width=3))]))
        fig.add_trace(go.Scatter(x=[5, 5], y=[6, 7.5], mode='lines', line=dict(color='red', width=3), name='Aguja'))

    else: # Deslizamiento (Mármol)
        draw_rect_trace(fig, 0, 0, 10, 1, fill="#ccc") 
        x_s = np.linspace(1, 9, 100); y_s = 2 + 0.2*np.sin(x_s)
        fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='lines', line=dict(color='blue'), name='Sup'))
        
        for i in range(0, 100, 2):
            frames.append(go.Frame(data=[go.Scatter(x=[x_s[i], x_s[i]], y=[y_s[i], y_s[i]+2], mode='lines+markers', line=dict(color='red'))]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    fig.frames = frames
    return fig

# C) PLANO TÉCNICO
def draw_blueprint(feature, tol):
    info = gdt_db[feature]
    ftype = info['type']
    sym = info['symbol']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano: {feature}", is_3d=False))

    if ftype == 'axis': # EJE
        draw_rect_trace(fig, 2, 3, 8, 4)
        draw_line_trace(fig, 1, 5, 11, 5, dash='longdashdot')
        draw_line_trace(fig, 10, 3, 11, 3, width=1); draw_line_trace(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", showarrow=False, font=dict(color='black', size=14))
        draw_arrow_trace(fig, 10.5, 5.5, 10.5, 7); draw_arrow_trace(fig, 10.5, 4.5, 10.5, 3)
        leader_target = (10.5, 4.5) # Apunta Cota
    else: # SUPERFICIE
        draw_rect_trace(fig, 3, 2, 6, 3)
        leader_target = (6, 5) # Apunta Superficie

    # Marco
    fx, fy = 9, 8
    draw_line_trace(fig, leader_target[0], leader_target[1], fx-1, fy+0.5, width=1.5) # Líder
    draw_line_trace(fig, fx-1, fy+0.5, fx, fy+0.5, width=1.5)
    draw_arrow_trace(fig, fx-1, fy+0.5, leader_target[0], leader_target[1])
    
    # Cajas
    draw_rect_trace(fig, fx, fy, 1.5, 1, fill='white')
    fig.add_annotation(x=fx+0.75, y=fy+0.5, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=22, color='black'))
    
    draw_rect_trace(fig, fx+1.5, fy, 2, 1, fill='white')
    tval = f"Ø {tol}" if ftype=='axis' else str(tol)
    fig.add_annotation(x=fx+2.5, y=fy+0.5, text=f"<b>{tval}</b>", showarrow=False, font=dict(size=16, color='black'))
    
    if datum:
        draw_rect_trace(fig, fx+3.5, fy, 1.5, 1, fill='white')
        fig.add_annotation(x=fx+4.25, y=fy+0.5, text=f"<b>{datum}</b>", showarrow=False, font=dict(size=16, color='black'))

    return fig

# D) CONSTRUCTOR PLANOS
def draw_master(active):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro", is_3d=False))
    
    # Pieza compleja
    draw_line_trace(fig, 1, 1, 11, 1, width=3)
    draw_line_trace(fig, 11, 1, 11, 3, width=3)
    draw_line_trace(fig, 11, 3, 9, 3, width=3)
    draw_line_trace(fig, 9, 3, 9, 5, width=3)
    draw_line_trace(fig, 9, 5, 4, 5, width=3)
    draw_line_trace(fig, 4, 5, 4, 8, width=3)
    draw_line_trace(fig, 4, 8, 1, 8, width=3)
    draw_line_trace(fig, 1, 8, 1, 1, width=3)
    
    draw_line_trace(fig, 0.5, 6.5, 11.5, 6.5, dash='longdashdot') # Eje
    
    locs = {'Rectitud':(7,1,7,0), 'Posición':(3,6.5,3,9), 'Planicidad':(6,3,6,5), 'Perpendicularidad':(1,5,-1,5), 'Angularidad':(10,3,12,4)}
    
    for f in active:
        if f in locs:
            tx, ty, fx, fy = locs[f]
            info = gdt_db[f]
            draw_rect_trace(fig, fx, fy, 3.5, 1, fill='white')
            txt = f"{info['symbol']} 0.1 {info['datum'] if info['datum'] else ''}"
            fig.add_annotation(x=fx+1.75, y=fy+0.5, text=f"<b>{txt}</b>", font=dict(color='black', size=14), showarrow=False)
            draw_line_trace(fig, tx, ty, fx, fy+0.5, width=1)
            draw_arrow_trace(fig, fx, fy+0.5, tx, ty)
    return fig

# --- 6. INTERFAZ PRINCIPAL ---
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
    info = gdt_db[feat]

    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #004B87;">{feat}</h3>
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
        st.markdown(f"<div class='blueprint-box'><b>Interpretación:</b> Controla {info['desc']} dentro de una zona de <b>{info['zone']}</b>.</div>", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    sel = st.sidebar.multiselect("Agregar:", list(gdt_db.keys()), default=['Rectitud'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
