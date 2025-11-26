import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(layout="wide", page_title="Laboratorio GD&T - Ing. Jaime Silva")

# ==========================================
# 0. ESTILOS VISUALES (TEMA INDUSTRIAL DE ALTO CONTRASTE)
# ==========================================
MAIN_BG = "#E6E6EA"      # Gris Industrial (No blanco brillante, no negro)
SIDEBAR_BG = "#111111"   # Negro Profundo
TEXT_COLOR = "#000000"   # Negro Absoluto
ACCENT = "#0044CC"       # Azul Ingeniería

st.markdown(f"""
<style>
    /* Fondo General */
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    
    /* Barra Lateral */
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    section[data-testid="stSidebar"] * {{ color: white !important; }}
    
    /* Corrección de Inputs en Sidebar (Fondo blanco para leer) */
    div[data-baseweb="select"] > div {{ background-color: white !important; color: black !important; }}
    div[data-baseweb="select"] span {{ color: black !important; }}
    
    /* Tarjetas de Información */
    .info-card {{
        background-color: white;
        border-left: 10px solid {ACCENT};
        padding: 20px;
        border-radius: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        color: black;
        margin-bottom: 15px;
    }}
    
    /* Interpretación del Plano (Estilo Nota Técnica) */
    .blueprint-note {{
        background-color: #FFF9C4; /* Amarillo pálido tipo nota */
        border: 1px solid #FBC02D;
        padding: 15px;
        border-radius: 3px;
        color: black;
        font-family: 'Courier New', monospace;
        font-weight: bold;
    }}

    /* Títulos y Textos */
    h1, h2, h3, p, li {{ color: black !important; }}
    
    /* Icono Gigante */
    .symbol-icon {{ font-size: 90px; font-weight: bold; color: {TEXT_COLOR}; text-align: center; }}

    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS PEDAGÓGICA (PDF "METROLOGÍA Y SUS APLICACIONES")
# ==========================================
# geo_type define qué lógica de dibujo usar: 'flat' (prismática), 'rot' (rotacional), 'hole' (agujeros)
gdt_db = {
    'Rectitud': {
        'sym': '⏤', 'geo_type': 'flat', 'datum': False,
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta perfecta.',
        'compare': 'Es una tolerancia 2D. No confundir con Planicidad (que es 3D).',
        'app': 'Vástagos de cilindros, rieles de guías lineales.',
        'interp': 'La línea superficial no debe desviarse más de la tolerancia (t) entre dos líneas paralelas.'
    },
    'Planicidad': {
        'sym': '⏥', 'geo_type': 'flat', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'compare': 'No requiere Datum. Es una cualidad intrínseca de la superficie.',
        'app': 'Culatas de motor, mesas de mármol, caras de sellado.',
        'interp': 'Toda la superficie debe estar contenida entre dos planos separados por la tolerancia (t).'
    },
    'Redondez': {
        'sym': '○', 'geo_type': 'rot', 'datum': False,
        'def': 'Condición donde todos los puntos de una superficie circular (en un corte transversal) equidistan de un centro.',
        'compare': 'Se mide corte por corte (2D). No es Cilindricidad.',
        'app': 'Pistas de rodamientos, muñones de cigüeñal.',
        'interp': 'En cualquier sección, el perfil debe estar entre dos círculos concéntricos separados por (t).'
    },
    'Cilindricidad': {
        'sym': '⌭', 'geo_type': 'rot', 'datum': False,
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'compare': 'Es la tolerancia de forma más estricta para ejes. Incluye a la redondez.',
        'app': 'Pistones hidráulicos, pernos de alta precisión.',
        'interp': 'Toda la superficie 3D debe estar entre dos cilindros coaxiales separados por (t).'
    },
    'Perpendicularidad': {
        'sym': '⟂', 'geo_type': 'L-shape', 'datum': 'A',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'compare': 'Es una tolerancia de orientación. Requiere Datum.',
        'app': 'Escuadras de fijación, caras de bridas.',
        'interp': 'La superficie debe estar entre dos planos paralelos separados por (t) y a 90° del Datum A.'
    },
    'Paralelismo': {
        'sym': '∥', 'geo_type': 'flat', 'datum': 'A',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano Datum.',
        'compare': 'Controla orientación (ángulo 0) y planicidad a la vez.',
        'app': 'Rieles de máquinas, caras opuestas de bloques.',
        'interp': 'La superficie tolerada debe estar entre dos planos paralelos al Datum A, separados por (t).'
    },
    'Angularidad': {
        'sym': '∠', 'geo_type': 'wedge', 'datum': 'A',
        'def': 'Controla una superficie o eje a un ángulo específico (no 90°) respecto a un Datum.',
        'compare': 'La tolerancia es una zona en mm, no en grados.',
        'app': 'Guías de cola de milano, rampas.',
        'interp': 'La superficie debe estar entre dos planos inclinados al ángulo básico, separados por (t).'
    },
    'Posición': {
        'sym': '⌖', 'geo_type': 'hole', 'datum': 'A B C',
        'def': 'Controla la ubicación exacta del centro de una característica (agujero) respecto a Datums.',
        'compare': 'Garantiza la intercambiabilidad de partes (ensamble).',
        'app': 'Patrones de pernos, bridas.',
        'interp': 'El eje del agujero debe estar dentro de un cilindro de diámetro (t) centrado en la posición teórica.'
    },
    'Concentricidad': {
        'sym': '◎', 'geo_type': 'rot', 'datum': 'A',
        'def': 'Controla que los puntos medios de secciones opuestas caigan en una zona cilíndrica.',
        'compare': 'Es teórica (balanceo). Difícil de medir, se prefiere usar Alabeo.',
        'app': 'Rotores de alta velocidad, turbinas.',
        'interp': 'Los puntos medios (medianos) deben estar dentro de un cilindro de diámetro (t) coaxial al Datum.'
    },
    'Alabeo Circular': {
        'sym': '↗', 'geo_type': 'rot', 'datum': 'A-B',
        'def': 'Variación de la superficie en una sección circular al girar sobre el Datum (Runout).',
        'compare': 'Controla redondez + concentricidad en esa sección.',
        'app': 'Discos de freno, ejes de transmisión.',
        'interp': 'Al girar la pieza, la aguja del indicador no debe moverse más de (t) en cada sección.'
    },
    'Alabeo Total': {
        'sym': '⌰', 'geo_type': 'rot', 'datum': 'A-B',
        'def': 'Variación de TODA la superficie al girar y desplazar el indicador.',
        'compare': 'Controla toda la pieza simultáneamente.',
        'app': 'Ejes de bombas, zonas de sellos.',
        'interp': 'Al girar y desplazar, la aguja no debe variar más de (t) en toda la superficie.'
    },
    'Perfil de una línea': {
        'sym': '⌒', 'geo_type': 'curve', 'datum': False,
        'def': 'Controla la forma de una curva 2D en una sección transversal.',
        'compare': 'Solo aplica al borde cortado.',
        'app': 'Alas de avión, levas.',
        'interp': 'El perfil real debe estar contenido en una banda de ancho (t) centrada en el perfil ideal.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'geo_type': 'curve', 'datum': False,
        'def': 'Controla la forma de una superficie 3D compleja.',
        'compare': 'Es una "piel" tridimensional.',
        'app': 'Carrocerías de autos, moldes.',
        'interp': 'Toda la superficie real debe estar entre dos límites envolventes separados por (t).'
    }
}

# ==========================================
# 2. MOTOR GRÁFICO "ANTIBALAS"
# ==========================================

def get_layout(title, is_3d=True):
    """Configuración gráfica estandarizada y limpia"""
    layout = dict(
        title=dict(text=title, font=dict(size=20, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG if is_3d else 'white',
        font=dict(color='black'),
        margin=dict(l=10, r=10, t=40, b=10),
        height=600, autosize=True
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='data',
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#bbb", title=''),
        )
        # Leyenda explícita
        layout['showlegend'] = True
        layout['legend'] = dict(x=0.9, y=0.9, bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1)
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[0, 12])
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[0, 8])
        # Marco de papel
        layout['shapes'] = [dict(type='rect', x0=0.2, y0=0.2, x1=11.8, y1=7.8, line=dict(color='black', width=3))]
    return layout

# ---------------------------------------------------------
# MÓDULO 1: SIMULACIÓN 3D (Geometrías Reales)
# ---------------------------------------------------------
def render_3d(feature, tol):
    fig = go.Figure()
    info = gdt_db.get(feature, gdt_db['Rectitud']) # Fallback
    gtype = info.get('geo_type', 'flat')
    
    # Mallas Universales
    z = np.linspace(0, 10, 40); th = np.linspace(0, 2*np.pi, 40); tg, zg = np.meshgrid(th, z)
    x_plane = np.linspace(-4, 4, 40); y_plane = np.linspace(-4, 4, 40); X, Y = np.meshgrid(x_plane, y_plane)

    # Lógica por Tipo de Geometría
    if gtype == 'rot': # Cilindros (Redondez, etc)
        r_nom = 4
        if feature == 'Redondez': # Solo un aro
            fig.add_trace(go.Scatter3d(x=(r_nom+0.2*np.sin(5*th))*np.cos(th), y=(r_nom+0.2*np.sin(5*th))*np.sin(th), z=np.zeros_like(th)+5, mode='lines', line=dict(color='blue', width=10), name='Perfil Real'))
            fig.add_trace(go.Scatter3d(x=(r_nom+tol)*np.cos(th), y=(r_nom+tol)*np.sin(th), z=np.zeros_like(th)+5, mode='lines', line=dict(color='red', dash='dash'), name='Límite Sup'))
            fig.add_trace(go.Scatter3d(x=(r_nom-tol)*np.cos(th), y=(r_nom-tol)*np.sin(th), z=np.zeros_like(th)+5, mode='lines', line=dict(color='red', dash='dash'), name='Límite Inf'))
        else: # Cilindro completo
            r_real = r_nom + 0.15 * np.sin(zg) * np.cos(tg*3)
            fig.add_trace(go.Surface(x=r_real*np.cos(tg), y=r_real*np.sin(tg), z=zg, colorscale='Spectral', opacity=0.9, name='Sup. Real'))
            fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='longdash'), name='Eje Datum'))
            # Mallas de tolerancia
            fig.add_trace(go.Scatter3d(x=(r_nom+tol)*np.cos(th), y=(r_nom+tol)*np.sin(th), z=np.full_like(th, 0), line=dict(color='red'), showlegend=False))
            fig.add_trace(go.Scatter3d(x=(r_nom+tol)*np.cos(th), y=(r_nom+tol)*np.sin(th), z=np.full_like(th, 10), line=dict(color='red'), name='Zona Tolerancia'))

    elif gtype == 'flat': # Bloques (Planicidad, Paralelismo)
        z_real = 0.2 * np.sin(X) * np.cos(Y)
        fig.add_trace(go.Surface(x=X, y=Y, z=z_real, colorscale='Viridis', name='Sup. Real'))
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(X, tol), opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Plano Sup'))
        fig.add_trace(go.Surface(x=X, y=Y, z=np.full_like(X, -tol), opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Plano Inf'))

    elif gtype == 'hole': # Posición
        # Bloque base
        fig.add_trace(go.Surface(x=X, y=Y, z=np.zeros_like(X)-2, opacity=0.1, colorscale='Greys', showscale=False))
        # Agujero Real vs Teórico
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[-2, 4], line=dict(color='black', dash='dash', width=3), name='Pos. Verdadera'))
        fig.add_trace(go.Scatter3d(x=[0.5, 0.5], y=[0.5, 0.5], z=[-2, 4], line=dict(color='red', width=8), name='Eje Real'))
        # Cilindro tolerancia
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg*0.4, opacity=0.3, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona Tol'))

    else: # Fallback (Rectitud, etc)
        # Eje Banana
        fig.add_trace(go.Scatter3d(x=np.sin(z)*0.5, y=np.zeros_like(z), z=z, line=dict(color='blue', width=12), name='Eje Real'))
        fig.add_trace(go.Surface(x=tol*np.cos(tg), y=tol*np.sin(tg), z=zg, opacity=0.2, colorscale=[[0,'orange'],[1,'orange']], name='Zona'))

    fig.update_layout(**get_layout(f"Simulación 3D: {feature}"))
    return fig

# ---------------------------------------------------------
# MÓDULO 2: MONTAJE REAL (ANIMACIONES LÓGICAS)
# ---------------------------------------------------------
def render_real_mount(feature):
    fig = go.Figure()
    layout = get_layout(f"Montaje de Inspección: {feature}", is_3d=False)
    
    # Botón de Play
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, buttons=[dict(label="▶️ REPRODUCIR ANIMACIÓN", method="animate", args=[None, dict(frame=dict(duration=50, redraw=True), fromcurrent=True)])])]
    fig.update_layout(**layout)

    info = gdt_db.get(feature, gdt_db['Rectitud'])
    gtype = info.get('geo_type', 'flat')

    frames = []
    
    # --- ESCENARIO 1: ROTACIÓN (Pieza en Chuck) ---
    if gtype == 'rot': 
        # Dibujo Estático
        fig.add_shape(type="rect", x0=0, y0=2, x1=2, y1=6, fillcolor="#333", line=dict(color="black")) # Chuck
        fig.add_shape(type="rect", x0=2, y0=3, x1=10, y1=5, line=dict(color="blue", width=2)) # Pieza
        fig.add_annotation(x=6, y=4, text="↻", font=dict(size=40))
        
        # Animación: La aguja del reloj sube y baja
        for i in range(40):
            # Simular error sinusoidal
            needle_h = 6.5 + 0.3 * np.sin(i * 0.5)
            frames.append(go.Frame(data=[
                go.Scatter(x=[6, 6], y=[5, 5.5], mode='lines', line=dict(color='gray', width=3)), # Punta
                go.Scatter(x=[6], y=[6], mode='markers', marker=dict(size=30, color='white', line=dict(color='black'))), # Reloj
                go.Scatter(x=[6, 6 + 0.4*np.cos(i)], y=[6, 6 + 0.4*np.sin(i)], mode='lines', line=dict(color='red', width=2)) # Aguja girando
            ]))
        # Inicial
        fig.add_trace(go.Scatter(x=[6, 6], y=[5, 5.5], line=dict(color='gray')))
        fig.add_trace(go.Scatter(x=[6], y=[6], mode='markers', marker=dict(size=30, color='white', line=dict(color='black'))))
        fig.add_trace(go.Scatter(x=[6, 6.4], y=[6, 6], line=dict(color='red')))

    # --- ESCENARIO 2: DESLIZAMIENTO (Pieza en Mesa) ---
    else: 
        # Mesa y Pieza
        fig.add_shape(type="rect", x0=0, y0=0, x1=12, y1=1, fillcolor="#ccc")
        # Pieza con error de forma
        x_p = np.linspace(1, 11, 50)
        y_p = 2 + 0.2 * np.sin(x_p)
        fig.add_trace(go.Scatter(x=x_p, y=y_p, mode='lines', line=dict(color='blue', width=4), name='Superficie'))
        
        # Animación: El reloj se mueve a la derecha
        for i in range(len(x_p)):
            xi = x_p[i]; yi = y_p[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=x_p, y=y_p, line=dict(color='blue')), # Mantener pieza
                go.Scatter(x=[xi, xi], y=[yi, yi+2], mode='lines+markers', marker=dict(symbol='circle-open', size=20), line=dict(color='black')), # Reloj
                go.Scatter(x=[xi], y=[yi], mode='markers', marker=dict(color='red', size=5)) # Punta
            ]))
        
        # Inicial
        fig.add_trace(go.Scatter(x=[1, 1], y=[2, 4], mode='lines+markers', line=dict(color='black')))
        fig.add_trace(go.Scatter(x=[1], y=[2], mode='markers', marker=dict(color='red')))

    fig.frames = frames
    return fig

# ---------------------------------------------------------
# MÓDULO 3: PLANO DE INGENIERÍA (VECTORES MANUALES)
# ---------------------------------------------------------
def draw_blueprint(feature, tol):
    fig = go.Figure()
    fig.update_layout(**get_layout(f"Plano Técnico: {feature}", is_3d=False))
    info = gdt_db.get(feature, gdt_db['Rectitud'])
    
    # --- DIBUJO DE LA PIEZA (EJE ESCALONADO) ---
    # Usamos Scatter lines para que NUNCA desaparezcan
    def line(x0, y0, x1, y1, w=2, d=None):
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color='black', width=w, dash=d), showlegend=False, hoverinfo='skip'))
    
    # Contorno
    line(1, 2, 3, 2); line(3, 2, 3, 1); line(3, 1, 9, 1) # Abajo
    line(9, 1, 9, 2); line(9, 2, 11, 2); line(11, 2, 11, 6) # Derecha
    line(11, 6, 9, 6); line(9, 6, 9, 7); line(9, 7, 3, 7) # Arriba
    line(3, 7, 3, 6); line(3, 6, 1, 6); line(1, 6, 1, 2) # Izquierda
    
    # Eje Central
    line(0, 4, 12, 4, 1, 'longdashdot')
    
    # --- COTA DE TAMAÑO ---
    line(11, 6, 11.5, 6, 1); line(11, 2, 11.5, 2, 1) # Ext
    fig.add_annotation(x=11.25, y=6, ax=11.25, ay=5, arrowhead=2, arrowcolor="black")
    fig.add_annotation(x=11.25, y=2, ax=11.25, ay=3, arrowhead=2, arrowcolor="black")
    fig.add_annotation(x=11.25, y=5, text="Ø 50 ±0.1", font=dict(size=14, color="black"), showarrow=False)

    # --- MARCO DE CONTROL ---
    # Coordenadas del marco
    fx, fy = 8, 8.5
    
    # Dibujar Marco (Rectángulos manuales)
    def rect(x, y, w, h):
        fig.add_trace(go.Scatter(x=[x, x+w, x+w, x, x], y=[y, y, y+h, y+h, y], fill='toself', fillcolor='white', line=dict(color='black'), showlegend=False))
    
    rect(fx, fy, 1.5, 1) # Símbolo
    fig.add_annotation(x=fx+0.75, y=fy+0.5, text=f"<b>{info.get('sym', '')}</b>", font=dict(size=24, color="black"), showarrow=False)
    
    rect(fx+1.5, fy, 2.5, 1) # Valor
    val_txt = f"Ø {tol}" if info['geo_type'] in ['rot', 'hole'] else str(tol)
    fig.add_annotation(x=fx+2.75, y=fy+0.5, text=f"<b>{val_txt}</b>", font=dict(size=20, color="black"), showarrow=False)
    
    if info['datum']:
        rect(fx+4, fy, 1.5, 1) # Datum
        fig.add_annotation(x=fx+4.75, y=fy+0.5, text=f"<b>{info['datum']}</b>", font=dict(size=20, color="black"), showarrow=False)

    # --- LÍDER (FLECHA CONECTORA) ---
    # Lógica: Si es superficie, apunta a la línea. Si es eje, apunta a la cota.
    if info['geo_type'] == 'flat' or info['geo_type'] == 'curve':
        # Apunta a la superficie superior
        line(6, 7, 6, 8.5) # Línea vertical
        fig.add_annotation(x=6, y=7, ax=6, ay=7.5, arrowhead=2, arrowcolor="black")
        line(6, 8.5, fx, 9) # Conexión al cuadro
    else:
        # Apunta a la cota de tamaño (Regla para Ejes)
        line(11.25, 5.2, 11.25, 8.5) # Línea vertical desde el texto
        line(11.25, 8.5, fx+5.5, 8.5) # Conexión horizontal al cuadro (por la derecha)

    return fig

# ---------------------------------------------------------
# MÓDULO 4: CONSTRUCTOR DE PLANO MAESTRO (CHECKLIST)
# ---------------------------------------------------------
def draw_master_blueprint(selected_features):
    fig = go.Figure()
    fig.update_layout(**get_layout("Plano Maestro Interactivo", is_3d=False))
    
    # Pieza Maestra (Bloque complejo)
    x_pts = [1, 11, 11, 8, 8, 4, 4, 1, 1]
    y_pts = [1, 1, 3, 3, 5, 5, 7, 7, 1]
    fig.add_trace(go.Scatter(x=x_pts, y=y_pts, fill="toself", fillcolor="#f0f0f0", line=dict(color="black", width=3), showlegend=False))
    
    # Eje Agujero
    fig.add_trace(go.Scatter(x=[2.5, 2.5], y=[2, 6], line=dict(color="black", dash="longdashdot"), showlegend=False))
    
    # Datum A (Base)
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20)

    # Mapa de Coordenadas para cada Cota
    loc_map = {
        'Rectitud': {'x': 9.5, 'y': 3, 'ax': 11, 'ay': 1.5},
        'Planicidad': {'x': 6, 'y': 5, 'ax': 6, 'ay': 6.5},
        'Perpendicularidad': {'x': 11, 'y': 2, 'ax': 13, 'ay': 2},
        'Posición': {'x': 2.5, 'y': 4, 'ax': 0.5, 'ay': 4},
        'Angularidad': {'x': 8, 'y': 4, 'ax': 9, 'ay': 5},
    }

    for feat in selected_features:
        if feat in loc_map:
            coords = loc_map[feat]
            sym = gdt_db[feat]['sym']
            # Marco
            fig.add_annotation(
                x=coords['x'], y=coords['y'],
                ax=coords['ax'], ay=coords['ay'],
                text=f"<b>{sym} 0.1 A</b>",
                font=dict(size=16, color="black"),
                bgcolor="white", bordercolor="black", borderwidth=2,
                arrowhead=2, arrowwidth=2, arrowcolor="black"
            )

    return fig

# ==========================================
# 5. INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])

if mode == "🔬 Análisis Individual":
    # Menú de Selección
    cats = {
        '1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'],
        '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'],
        '3. Localización': ['Posición', 'Concentricidad'],
        '4. Cabeceo': ['Alabeo Circular', 'Alabeo Total'],
        '5. Perfil': ['Perfil de una línea', 'Perfil de una superficie']
    }
    sel_cat = st.sidebar.selectbox("Categoría", list(cats.keys()))
    sel_feat = st.sidebar.selectbox("Característica", cats[sel_cat])
    tol_val = st.sidebar.slider("Tolerancia", 0.01, 1.0, 0.1)
    
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Plano Técnico"])
    
    # Generar Clave Única para forzar refresco
    plot_key = f"{sel_feat}_{view}_{tol_val}_{time.time()}"
    
    # 1. TARJETA DE INFORMACIÓN (Siempre Visible)
    info = gdt_db[sel_feat]
    st.markdown(f"""
    <div class="info-card">
        <div style="display:flex; align-items:center;">
            <div style="font-size:60px; margin-right:20px; color:#0044CC;">{info.get('sym', '?')}</div>
            <div>
                <h3 style="margin:0;">{sel_feat}</h3>
                <p><strong>Definición:</strong> {info['def']}</p>
                <p>⚠️ <strong>Importancia:</strong> {info.get('why', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. RENDERIZADO
    if view == "Simulación 3D":
        st.plotly_chart(render_3d(sel_feat, tol_val), use_container_width=True, key=plot_key)
        st.info(f"🔍 {info.get('interp', 'Visualización de la zona de tolerancia.')}")

    elif view == "Montaje Real":
        st.plotly_chart(render_real_mount(sel_feat), use_container_width=True, key=plot_key)
        st.info("🏭 Representación esquemática del proceso de inspección física.")

    elif view == "Plano Técnico":
        st.plotly_chart(draw_blueprint(sel_feat, tol_val), use_container_width=True, key=plot_key)
        # CAJA DE INTERPRETACIÓN (Solo en plano)
        st.markdown(f"""
        <div class="blueprint-note">
            📝 INTERPRETACIÓN DEL PLANO:<br>
            "La característica de {sel_feat.upper()} debe estar contenida dentro de una zona de 
            {info.get('zone', '')} de valor {tol_val} mm."
        </div>
        """, unsafe_allow_html=True)

elif mode == "📝 Constructor de Plano":
    st.sidebar.info("Seleccione las cotas a agregar:")
    options = ['Rectitud', 'Planicidad', 'Perpendicularidad', 'Posición', 'Angularidad']
    selection = st.sidebar.multiselect("Características:", options, default=['Rectitud'])
    
    st.plotly_chart(draw_master_blueprint(selection), use_container_width=True, key=f"master_{len(selection)}")
