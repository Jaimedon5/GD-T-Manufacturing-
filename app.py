import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(layout="wide", page_title="GD&T Master Lab - Ing. Jaime Silva")

# ==========================================
# 0. ESTILOS CSS (BLINDADOS)
# ==========================================
st.markdown("""
<style>
    /* FONDO GENERAL */
    .stApp { background-color: #e6e6ea; }
    
    /* BARRA LATERAL */
    section[data-testid="stSidebar"] { background-color: #111111; }
    
    /* TEXTOS DEL SIDEBAR (BLANCOS) */
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stMarkdown {
        color: #ffffff !important;
    }
    
    /* INPUTS DEL SIDEBAR (FONDO BLANCO, TEXTO NEGRO) - CORRECCIÓN CRÍTICA */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    div[data-testid="stSlider"] label { color: #ffffff !important; }
    
    /* TARJETAS DE INFORMACIÓN (ENCABEZADO) */
    .info-card {
        background-color: #ffffff;
        border-left: 8px solid #0055a4;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* TEXTOS GENERALES (NEGROS) */
    h1, h2, h3, p, li, span { color: #000000; }
    
    /* ICONO GRANDE */
    .big-icon {
        font-size: 80px;
        font-weight: bold;
        text-align: center;
        color: #000000;
    }
    
    /* CONTENEDOR GRÁFICO */
    .plot-container { border: 1px solid #ccc; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (PDF REFERENCE)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Condición donde cada elemento lineal debe estar dentro de una línea recta.',
        'compare': 'Es 2D (Línea). No confundir con Planicidad (3D).',
        'app': 'Vástagos cilíndricos, rieles, ejes largos.',
        'why': 'Evita desgaste irregular y fugas en sellos.',
        'geo': 'shaft_banana'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie están en un solo plano.',
        'compare': 'No usa Datum. Es una cualidad de la superficie misma.',
        'app': 'Caras de monoblocks, mesas de granito, juntas de estanqueidad.',
        'why': 'Asegura contacto total y sellado hermético.',
        'geo': 'plate_wavy'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Condición donde todos los puntos de una sección circular (2D) equidistan del centro.',
        'compare': 'Se mide corte por corte. No es Cilindricidad.',
        'app': 'Muñones de cigüeñal, pistas de rodamientos.',
        'why': 'Evita vibraciones y ruido a altas revoluciones.',
        'geo': 'ring_lobed'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la forma cilíndrica total (Redondez + Rectitud + Conicidad).',
        'compare': 'Es 3D. La más estricta para ejes.',
        'app': 'Pistones de inyección, pernos hidráulicos.',
        'why': 'Crítica para sistemas de alta presión sin empaques.',
        'geo': 'cylinder_barrel'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Condición donde una superficie o eje está a 90° de un Datum.',
        'compare': 'Es una Angularidad fija a 90°.',
        'app': 'Escuadras, bridas de sujeción.',
        'why': 'Evita que los tornillos se doblen al apretar.',
        'geo': 'L_bracket'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Condición a un ángulo específico (básico) respecto al Datum.',
        'compare': 'La zona es milimétrica (planos paralelos), no en grados.',
        'app': 'Guías de cola de milano, rampas de levas.',
        'why': 'Asegura contacto uniforme en deslizamientos.',
        'geo': 'wedge'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Todos los puntos equidistan de un plano Datum.',
        'compare': 'Controla orientación (0°) y planicidad.',
        'app': 'Rieles de máquinas, caras de bloques patrón.',
        'why': 'Evita atascamientos en partes móviles.',
        'geo': 'block_parallel'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B C',
        'def': 'Controla la ubicación exacta del centro (eje) de una característica.',
        'compare': 'Permite Bonus Tolerance (MMC). Garantiza ensamble.',
        'app': 'Patrones de agujeros para pernos.',
        'why': 'Asegura que las piezas coincidan al atornillar.',
        'geo': 'plate_hole'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla que los puntos medios opuestos sean coaxiales al Datum.',
        'compare': 'Es teórica (balanceo). Usar Alabeo si es posible.',
        'app': 'Rotores de alta velocidad.',
        'why': 'Balanceo dinámico para evitar vibración.',
        'geo': 'shaft_concentric'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'surf', 'datum': 'A-B',
        'def': 'Variación en una sección circular al girar (Runout).',
        'compare': 'Mide corte a corte. Suma redondez + excentricidad.',
        'app': 'Discos de freno, ejes de motores.',
        'why': 'Evita pulsaciones en el frenado.',
        'geo': 'shaft_runout'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'surf', 'datum': 'A-B',
        'def': 'Variación de TODA la superficie al girar y desplazarse.',
        'compare': 'Controla toda la pieza simultáneamente.',
        'app': 'Rodillos de impresión, ejes de bombas.',
        'why': 'Cero fugas en sellos mecánicos.',
        'geo': 'shaft_runout'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una curva 2D en una sección.',
        'compare': 'Solo aplica al borde cortado.',
        'app': 'Álabes de turbina, levas.',
        'why': 'Rendimiento aerodinámico.',
        'geo': 'curved_surface_2d'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Controla la forma de una superficie 3D compleja.',
        'compare': 'Piel tridimensional (Envelope).',
        'app': 'Cofre de auto, moldes de inyección.',
        'why': 'Estética y ajuste de formas orgánicas.',
        'geo': 'curved_surface_3d'
    }
}

# ==========================================
# 2. FUNCIONES GRÁFICAS (HELPERS)
# ==========================================
def get_layout(title, is_3d=True):
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
        # Leyenda siempre visible
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1, x=0.9, y=0.9)
    else:
        # Plano 2D
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 12], scaleanchor='y')
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 8])
        # Marco de hoja
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0.01, y0=0.01, x1=0.99, y1=0.99, line=dict(color='black', width=3))]
    return layout

# Funciones de dibujo 2D seguras
def draw_rect(fig, x0, y0, w, h, color="black", fill=None, width=2):
    x = [x0, x0+w, x0+w, x0, x0]
    y = [y0, y0, y0+h, y0+h, y0]
    f = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=f, fillcolor=fill, mode='lines', line=dict(color=color, width=width), hoverinfo='skip', showlegend=False))

def draw_line(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), hoverinfo='skip', showlegend=False))

def draw_arrow(fig, x_start, y_start, x_end, y_end):
    fig.add_annotation(x=x_end, y=y_end, ax=x_start, ay=y_start, xref='x', yref='y', axref='x', ayref='y', arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")

# ==========================================
# VISTA 1: SIMULACIONES 3D (REALES Y VARIADAS)
# ==========================================
def plot_3d_sim(feature, tol):
    fig = go.Figure()
    geo = gdt_data[feature]['geo']
    
    # Mallas
    res = 40
    z = np.linspace(0, 10, res); theta = np.linspace(0, 2*np.pi, res)
    tg, zg = np.meshgrid(theta, z)

    if feature == 'Rectitud': # Eje Banana
        x_real = 0.5 * np.sin(z * 0.5)
        fig.add_trace(go.Scatter3d(x=x_real, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.2, colorscale='Oranges', showscale=False, name='Tol'))

    elif feature == 'Planicidad': # Superficie
        x = np.linspace(-5,5,res); y = np.linspace(-5,5,res); xg,yg = np.meshgrid(x,y)
        z_real = 0.2 * np.sin(xg/2) * np.cos(yg/2)
        fig.add_trace(go.Surface(z=z_real, x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Reds', name='Max'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol), x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Reds', name='Min'))

    elif geo == 'L_bracket': # Perpendicularidad
        # Pared vertical
        y_w = np.linspace(0, 8, res); x_w = np.linspace(-4, 4, res); Y, X = np.meshgrid(y_w, x_w)
        Z_w = (tol*2) * (Y/8) # Inclinación exagerada
        fig.add_trace(go.Surface(x=X, y=Y, z=Z_w, colorscale='Blues', name='Pared Real'))
        # Datum Base
        fig.add_trace(go.Surface(x=X, y=np.zeros_like(Y), z=Y, opacity=0.5, colorscale='Greys', showscale=False, name='Datum A'))
        # Planos limite
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, tol), opacity=0.2, showscale=False, colorscale='Reds', name='Tol +'))
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(Y, -tol), opacity=0.2, showscale=False, colorscale='Reds', name='Tol -'))

    elif geo == 'wedge': # Angularidad
        x = np.linspace(0,10,res); y = np.linspace(0,10,res); xg,yg = np.meshgrid(x,y)
        z_nom = xg * np.tan(np.radians(30))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom, colorscale='Plasma', name='Plano Real'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom+tol, opacity=0.2, showscale=False, colorscale='Greens'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=z_nom-tol, opacity=0.2, showscale=False, colorscale='Greens'))

    elif feature == 'Posición': # Placa con agujero
        x = np.linspace(-5,5,20); y=np.linspace(-5,5,20); xg,yg=np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=np.zeros_like(xg), x=xg, y=yg, opacity=0.1, showscale=False, colorscale='Greys', name='Placa'))
        # Agujero desviado
        fig.add_trace(go.Scatter3d(x=[1,1], y=[1,1], z=[-2,5], line=dict(color='red', width=8), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-2,5], line=dict(color='black', dash='dash', width=4), name='Teórico'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.5, opacity=0.3, showscale=False, colorscale='YlOrRd', name='Zona'))

    elif 'Perfil' in feature: # Superficie compleja
        x = np.linspace(-3,3,30); y=np.linspace(-3,3,30); xg,yg=np.meshgrid(x,y)
        z_base = 0.5*(xg**2 + yg**2)
        fig.add_trace(go.Surface(z=z_base, x=xg, y=yg, opacity=0.9, colorscale='Jet', name='Nominal'))
        fig.add_trace(go.Surface(z=z_base+tol, x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Blues', name='Env +'))
        fig.add_trace(go.Surface(z=z_base-tol, x=xg, y=yg, opacity=0.2, showscale=False, colorscale='Blues', name='Env -'))

    else: # Cilindro por defecto (Cilindricidad, Alabeo)
        r = 5 + 0.2*np.sin(zg) # Deforme
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='dash', width=5), name='Datum'))

    fig.update_layout(**get_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMACIONES FUNCIONALES)
# ==========================================
def plot_real_anim(feature):
    fig = go.Figure()
    layout = get_layout(f"Inspección Física: {feature}", is_3d=False)
    # Botón Play
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ INICIAR", method="animate", args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)
    
    geo = gdt_data[feature]['geo']
    frames = []

    if feature == 'Angularidad': # Mesa de Senos
        # Mesa
        draw_rect(fig, 0, 0, 10, 0.5, color="black", fill="#aaa") 
        # Rodillos
        fig.add_trace(go.Scatter(x=[2, 8], y=[1, 3], mode='markers', marker=dict(size=20, color='black')))
        # Bloques
        draw_rect(fig, 7.5, 0.5, 1, 2.5, color="blue", fill="blue")
        # Barra senos
        fig.add_trace(go.Scatter(x=[2, 8], y=[1, 3], mode='lines', line=dict(color='black', width=5)))
        # Pieza
        draw_rect(fig, 2, 3, 6, 2, color="black") # Recta gracias a la inclinacion
        
        # Animación deslizamiento
        for i in range(50):
            x = 2 + i/10
            frames.append(go.Frame(data=[
                go.Scatter(x=[x, x], y=[5, 7], mode='lines+markers', line=dict(color='red'), marker=dict(size=10))
            ]))
        fig.add_trace(go.Scatter(x=[2, 2], y=[5, 7], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        # Torno/Chuck
        draw_rect(fig, 0, 2, 1, 4, color="black", fill="#333")
        draw_rect(fig, 1, 3, 8, 2, color="blue") # Eje
        fig.add_annotation(x=5, y=4, text="↻", font=dict(size=40, color='white'))
        
        # Animación aguja
        for i in range(50):
            dy = 0.3 * np.sin(i*0.5)
            frames.append(go.Frame(data=[
                go.Scatter(x=[5, 5], y=[5, 6+dy], mode='lines', line=dict(color='red', width=3))
            ]))
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines', line=dict(color='gray'), name='Soporte')) # Base fija
        fig.add_trace(go.Scatter(x=[5, 5], y=[5, 6], mode='lines', line=dict(color='red', width=3), name='Aguja')) # Móvil

    elif feature == 'Perpendicularidad': # Escuadra
        draw_rect(fig, 0, 0, 4, 6, fill="#ccc") # Escuadra patrón
        fig.add_trace(go.Scatter(x=[4.2, 4.5], y=[0, 6], mode='lines', line=dict(color='blue', width=4), name='Pieza'))
        
        for i in range(50):
            y = i/8
            x = 4.2 + (y*0.05) # Inclinacion
            frames.append(go.Frame(data=[
                go.Scatter(x=[x-1, x], y=[y, y], mode='lines+markers', line=dict(color='red'))
            ]))
        fig.add_trace(go.Scatter(x=[3.2, 4.2], y=[0.5, 0.5], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    else: # Planicidad/Rectitud
        draw_rect(fig, 0, 0, 10, 1, fill="#ccc") # Mármol
        x_s = np.linspace(1, 9, 100); y_s = 2 + 0.2*np.sin(x_s)
        fig.add_trace(go.Scatter(x=x_s, y=y_s, mode='lines', line=dict(color='blue'), name='Sup. Real'))
        
        for i in range(0, 100, 2):
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_s[i], x_s[i]], y=[y_s[i], y_s[i]+2], mode='lines+markers', line=dict(color='red'))
            ]))
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='red'), name='Reloj'))

    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA (NORMA ASME)
# ==========================================
def draw_blueprint(feature, tol_val):
    info = gdt_data[feature]
    geo = info['geo']
    ftype = info['type']
    sym = info['symbol']
    datum = info['datum']
    
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano: {feature}", is_3d=False))
    
    # --- DIBUJAR PIEZA ---
    leader_target = (0,0)
    
    if 'cylinder' in geo or 'shaft' in geo:
        # Eje
        draw_rect(fig, 2, 3, 8, 4, width=3)
        draw_line(fig, 1, 5, 11, 5, dash='longdashdot')
        # Cota tamaño
        draw_line(fig, 10, 3, 11, 3, width=1)
        draw_line(fig, 10, 7, 11, 7, width=1)
        fig.add_annotation(x=10.5, y=5, text="Ø 40 ±0.1", font=dict(size=14), showarrow=False)
        draw_arrow(fig, 10.5, 5.5, 10.5, 7)
        draw_arrow(fig, 10.5, 4.5, 10.5, 3)
        
        if ftype == 'axis': leader_target = (10.5, 4.5) # Apunta a Cota
        else: leader_target = (6, 7) # Apunta Superficie
            
    elif 'plate' in geo:
        draw_rect(fig, 2, 2, 8, 6, width=3)
        # Agujero
        th=np.linspace(0,2*np.pi,50); fig.add_trace(go.Scatter(x=6+1*np.cos(th), y=5+1*np.sin(th), mode='lines', line=dict(color='black')))
        # Cota agujero
        fig.add_annotation(x=8, y=7, ax=6.5, ay=6, text="Ø 20", arrowhead=2, arrowcolor="black")
        leader_target = (8, 6.8)

    elif 'L_bracket' in geo:
        x=[2, 8, 8, 4, 4, 2, 2]; y=[2, 2, 4, 4, 8, 8, 2]
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black', width=3), showlegend=False))
        leader_target = (4, 6) # Cara vertical

    else: # Bloque
        draw_rect(fig, 2, 3, 8, 4, width=3)
        leader_target = (6, 7)

    # --- DATUM ---
    if datum:
        fig.add_trace(go.Scatter(x=[3,4,3.5,3], y=[3,3,2.2,3], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect(fig, 3.1, 1.4, 0.8, 0.8, width=1)
        fig.add_annotation(x=3.5, y=1.8, text=f"<b>{datum[0]}</b>", showarrow=False)

    # --- MARCO DE CONTROL ---
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
        fig.add_annotation(x=frame_x+2*w+0.5+w/2, y=frame_y+0.5, text=f"<b>{datum}</b>", font=dict(size=18), showarrow=False)

    return fig

# --- VISTA 4: CONSTRUCTOR DE PLANOS ---
def draw_master(active_features):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro", is_3d=False))
    
    # Pieza Maestra
    x=[1,11,11,9,9,4,4,1,1]; y=[1,1,3,3,5,5,8,8,1]
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='black', width=3), showlegend=False))
    draw_line(fig, 0.5, 6.5, 11.5, 6.5, dash='longdashdot') # Eje
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20, ax=0) # Datum
    
    locs = {'Rectitud':(7,1,7,0), 'Posición':(3,6.5,3,9), 'Planicidad':(6,3,6,5), 'Perpendicularidad':(1,5,-1,5), 'Angularidad':(10,4,12,5)}
    
    for feat in active_features:
        if feat in locs:
            tx, ty, fx, fy = locs[feat]
            info = gdt_data[feat]
            draw_rect(fig, fx, fy, 4, 1, width=2)
            fig.add_annotation(x=fx+2, y=fy+0.5, text=f"<b>{info['symbol']} 0.1 {info['datum'] if info['datum'] else ''}</b>", font=dict(size=16), showarrow=False)
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
    
    info = gdt_data[feat]
    key = f"{feat}_{view}_{tol}_{time.time()}" # LLAVE ANTI-CONGELAMIENTO

    # TARJETA INFORMATIVA (SIEMPRE VISIBLE)
    st.markdown(f"""
    <div class="info-card">
        <div style="display: flex; align-items: center;">
            <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
            <div style="flex: 4; padding-left: 20px;">
                <h3 style="margin:0; color: #0055a4;">{feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p><strong>Comparación:</strong> {info['compare']}</p>
                <p><strong>Aplicación:</strong> {info['app']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if view == "📐 Simulación 3D":
        st.plotly_chart(plot_3d(feat, tol), use_container_width=True, key=key)
        st.info(f"Detalle Visual: {gdt_data[feat]['sim_3d_desc']}")
    elif view == "🏭 Montaje Real":
        st.plotly_chart(plot_real_anim(feat), use_container_width=True, key=key)
        st.info(f"Procedimiento: {gdt_data[feat]['real_desc']}")
    elif view == "📝 Plano Técnico":
        st.plotly_chart(draw_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=key)
        st.markdown(f"<div class='info-box'><b>Interpretación:</b> Controla <b>{info['desc']}</b> dentro de una zona de <b>{info['zone']}</b>.</div>", unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    sel = st.sidebar.multiselect("Agregar cotas:", list(gdt_data.keys()), default=['Rectitud', 'Posición'])
    st.plotly_chart(draw_master(sel), use_container_width=True, key=f"master_{time.time()}")
