import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (CORREGIDO PARA MENÚS VISIBLES)
# ==========================================
MAIN_BG = "#D5D5D7"      # Gris Acero (Fondo Principal)
SIDEBAR_BG = "#1E1E1E"   # Negro Carbón (Barra Lateral)
CARD_BG = "#FFFFFF"      # Blanco Puro
TEXT_COLOR = "#000000"   # Negro
ACCENT = "#0d6efd"       # Azul Ingeniería

st.markdown(f"""
<style>
    /* 1. FONDO PRINCIPAL */
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    
    /* 2. BARRA LATERAL */
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    
    /* Textos estáticos del Sidebar (Títulos y etiquetas) -> BLANCO */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stMarkdown p {{
        color: #FFFFFF !important;
    }}
    
    /* Corrección CRÍTICA para Menús Desplegables y Sliders: */
    /* Asegura que el texto dentro de los selectbox sea visible (no blanco sobre blanco) */
    div[data-baseweb="select"] span {{
        color: black !important; 
    }}
    
    /* 3. TARJETAS DE DEFINICIÓN */
    .gdt-card {{
        background-color: {CARD_BG};
        border-left: 8px solid {ACCENT};
        padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: {TEXT_COLOR}; margin-bottom: 20px;
    }}

    /* 4. TARJETAS DE EXPLICACIÓN VISUAL (Debajo del gráfico) */
    .visual-card {{
        background-color: #f1f3f5; border: 1px solid #ccc;
        padding: 15px; border-radius: 8px; color: {TEXT_COLOR};
        font-size: 0.95em; margin-top: 10px;
    }}
    
    /* Caja Azul de Interpretación de Plano */
    .interpretation-box {{
        background-color: #e8f4f8; border-left: 6px solid {ACCENT};
        padding: 20px; border-radius: 5px; margin-top: 10px;
        font-family: sans-serif; color: {TEXT_COLOR};
    }}
    
    /* 5. TEXTO NEGRO EN ÁREA PRINCIPAL */
    .main h1, .main h2, .main h3, .main p, .main li, .main span {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* 6. ICONOS */
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS COMPLETA
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤', 'type': 'surf', 'datum': False,
        'def': 'Controla qué tan recta es una línea específica (eje o superficie).',
        'compare': 'Es 2D. No confundir con Planicidad (3D).', 'app': 'Vástagos, rieles.', 'why': 'Evita fugas.',
        'desc': 'rectitud', 'zone': 'dos líneas paralelas',
        'sim_3d_desc': '🔵 <b>Eje Real:</b> Línea curvada azul.<br>🟠 <b>Zona Tolerancia:</b> Cilindro naranja semitransparente.',
        'real_desc': 'Se desplaza el reloj a lo largo de la pieza. La variación total de la aguja es el error.'
    },
    'Planicidad': {
        'symbol': '⏥', 'type': 'surf', 'datum': False,
        'def': 'Controla la planitud de una superficie.',
        'compare': 'No usa Datum. Intrínseca.', 'app': 'Culatas, mesas.', 'why': 'Sellado.',
        'desc': 'planicidad', 'zone': 'dos planos paralelos',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Mapa de colores del error.<br>🔴 <b>Planos Rojos:</b> Límites superior e inferior.',
        'real_desc': 'El reloj barre toda la superficie. La diferencia entre el punto más alto y más bajo es el error.'
    },
    'Redondez': {
        'symbol': '○', 'type': 'axis', 'datum': False,
        'def': 'Controla la circularidad de una sección (2D).',
        'compare': 'Sección por sección. No es 3D.', 'app': 'Rodamientos.', 'why': 'Vibración.',
        'desc': 'redondez', 'zone': 'dos círculos concéntricos',
        'sim_3d_desc': '🔵 <b>Perfil Azul:</b> Forma real del corte.<br>🔴 <b>Círculos Rojos:</b> Límites coaxiales.',
        'real_desc': 'La pieza gira, el reloj está fijo. Se mide la variación radial.'
    },
    'Cilindricidad': {
        'symbol': '⌭', 'type': 'axis', 'datum': False,
        'def': 'Controla la forma cilíndrica total (3D).',
        'compare': 'Incluye redondez, rectitud y conicidad.', 'app': 'Pistones.', 'why': 'Sellado dinámico.',
        'desc': 'cilindricidad', 'zone': 'dos cilindros coaxiales',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Forma real 3D.<br>🔴 <b>Mallas Rojas:</b> Cilindros límite.',
        'real_desc': 'Se escanea toda la superficie (espiral o múltiples cortes).'
    },
    'Angularidad': {
        'symbol': '∠', 'type': 'surf', 'datum': 'A',
        'def': 'Controla la inclinación respecto a un Datum.',
        'compare': 'Zona en mm, no grados.', 'app': 'Guías.', 'why': 'Contacto.',
        'desc': 'angularidad', 'zone': 'dos planos paralelos inclinados',
        'sim_3d_desc': '🌈 <b>Plano:</b> Superficie inclinada.<br>🟢 <b>Planos Verdes:</b> Límites de tolerancia.',
        'real_desc': 'Uso de Mesa de Senos para nivelar y medir variación.'
    },
    'Perpendicularidad': {
        'symbol': '⟂', 'type': 'surf', 'datum': 'A',
        'def': 'Controla los 90° respecto a un Datum.',
        'compare': 'Caso especial de Angularidad.', 'app': 'Escuadras.', 'why': 'Alineación.',
        'desc': 'perpendicularidad', 'zone': 'dos planos a 90°',
        'sim_3d_desc': '🌈 <b>Pared:</b> Superficie real.<br>🔵 <b>Planos Azules:</b> Zona de tolerancia a 90°.',
        'real_desc': 'Comparación contra una escuadra patrón de granito.'
    },
    'Paralelismo': {
        'symbol': '∥', 'type': 'surf', 'datum': 'A',
        'def': 'Controla el paralelismo respecto a un Datum.',
        'compare': 'Orientación y forma.', 'app': 'Rieles.', 'why': 'Atascamiento.',
        'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum',
        'sim_3d_desc': '🟣 <b>Planos Morados:</b> Límites paralelos al Datum inferior.',
        'real_desc': 'Deslizamiento del reloj sobre la cara superior.'
    },
    'Posición': {
        'symbol': '⌖', 'type': 'axis', 'datum': 'A B',
        'def': 'Controla la ubicación exacta del centro.',
        'compare': 'Garantiza ensamble.', 'app': 'Pernos.', 'why': 'Intercambiabilidad.',
        'desc': 'posición', 'zone': 'cilindro en posición teórica',
        'sim_3d_desc': '🔴 <b>Línea Roja:</b> Eje real del agujero.<br>🟡 <b>Cilindro Amarillo:</b> Zona de tolerancia.',
        'real_desc': 'Verificación con Máquina de Coordenadas (CMM) o Gage funcional.'
    },
    'Concentricidad': {
        'symbol': '◎', 'type': 'axis', 'datum': 'A',
        'def': 'Controla el eje mediano (balanceo).',
        'compare': 'Difícil de medir.', 'app': 'Rotores.', 'why': 'Balanceo.',
        'desc': 'concentricidad', 'zone': 'cilindro coaxial',
        'sim_3d_desc': '🔴 <b>Puntos Rojos:</b> Centros medianos derivados.<br>🟡 <b>Zona Amarilla:</b> Tolerancia.',
        'real_desc': 'Medición diferencial de puntos opuestos al girar.'
    },
    'Alabeo Circular': {
        'symbol': '↗', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación circular al girar (Runout).',
        'compare': 'Mide corte a corte.', 'app': 'Frenos.', 'why': 'Vibración.',
        'desc': 'alabeo circular', 'zone': 'distancia radial (sección)',
        'sim_3d_desc': '🟣 <b>Línea Morada:</b> Trayectoria medida.<br>🔴 <b>Líneas Punteadas:</b> Límites.',
        'real_desc': 'Giro de la pieza sobre bloques V con reloj fijo.'
    },
    'Alabeo Total': {
        'symbol': '⌰', 'type': 'axis', 'datum': 'A-B',
        'def': 'Variación total al girar.',
        'compare': 'Controla toda la pieza.', 'app': 'Ejes bomba.', 'why': 'Fugas.',
        'desc': 'alabeo total', 'zone': 'distancia radial (total)',
        'sim_3d_desc': '🔴 <b>Mallas Rojas:</b> Cilindros límite coaxiales.',
        'real_desc': 'Giro de la pieza mientras el reloj se desplaza longitudinalmente.'
    },
    'Perfil de una línea': {
        'symbol': '⌒', 'type': 'surf', 'datum': False,
        'def': 'Forma de línea 2D.',
        'compare': 'Solo el borde.', 'app': 'Alas.', 'why': 'Aerodinámica.',
        'desc': 'perfil de línea', 'zone': 'banda uniforme',
        'sim_3d_desc': '🔵 <b>Línea Azul:</b> Perfil real.<br>🟢 <b>Líneas Verdes:</b> Banda de tolerancia.',
        'real_desc': 'Proyector de perfiles con plantilla transparente.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓', 'type': 'surf', 'datum': False,
        'def': 'Forma de superficie 3D.',
        'compare': 'Piel tridimensional.', 'app': 'Carrocerías.', 'why': 'Estética.',
        'desc': 'perfil de superficie', 'zone': 'dos superficies envolventes',
        'sim_3d_desc': '🔵 <b>Capas Azules:</b> Límites envolventes superior e inferior.',
        'real_desc': 'Escaneo de puntos con CMM comparado contra CAD.'
    }
}

# ==========================================
# 2. FUNCIONES DE DIBUJO
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG, font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20), height=600
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc", showbackground=True)
        )
        # LEYENDA VISIBLE Y CLARA
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="#333", borderwidth=1, font=dict(color="black"), yanchor="top", y=0.95, xanchor="right", x=0.99)
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

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=False, hoverinfo='skip'))

def plot_control_frame(feature, tol_val):
    data = gdt_data.get(feature, {'symbol': '?', 'datum': False})
    has_datum = data['datum']
    fig = go.Figure()
    
    # DIBUJO DEL MARCO
    draw_rect_trace(fig, 0, 0, 1, 1, width=3)
    fig.add_annotation(x=0.5, y=0.5, text=f"<b>{data['symbol']}</b>", showarrow=False, font=dict(size=40, color="black"))
    draw_rect_trace(fig, 1, 0, 3, 1, width=3)
    fig.add_annotation(x=2, y=0.5, text=f"<b>{tol_val}</b>", showarrow=False, font=dict(size=35, color="black"))
    
    max_x = 3
    if has_datum:
        draw_rect_trace(fig, 3, 0, 4, 1, width=3)
        fig.add_annotation(x=3.5, y=0.5, text="<b>A</b>", showarrow=False, font=dict(size=35, color="black"))
        max_x = 4

    # Flechas explicativas
    fig.add_annotation(x=0.5, y=1.2, ax=0.5, ay=2, text="<b>Símbolo</b>", showarrow=True, arrowhead=2, arrowcolor="#d62728", font=dict(color="#d62728"))
    fig.add_annotation(x=2, y=1.2, ax=2, ay=2, text="<b>Tolerancia</b>", showarrow=True, arrowhead=2, arrowcolor="#0d6efd", font=dict(color="#0d6efd"))
    
    fig.update_layout(xaxis=dict(range=[-0.5, max_x+0.5], visible=False), yaxis=dict(range=[-0.5, 2.5], visible=False), height=180, margin=dict(t=10, b=10), paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG)
    return fig

# ==========================================
# VISTA 1: SIMULACIÓN 3D
# ==========================================
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False, name='Zona Tolerancia'))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Sup'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False, name='Inf'))
    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100); r = 5 + 0.2 * np.cos(3*th)
        fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=6), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(th), y=(5-tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Min'))
    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=6, dash='longdash'), name='Eje Común'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Límite'))
    elif feature == 'Angularidad':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20)); z_nom = x * np.tan(np.radians(45))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom + 0.1*np.sin(y), colorscale='Plasma', name='Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol/2, opacity=0.2, colorscale=[[0,'green'],[1,'green']], showscale=False, name='Lim Sup'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol/2, opacity=0.2, colorscale=[[0,'green'],[1,'green']], showscale=False, name='Lim Inf'))
    elif feature == 'Perpendicularidad':
        z_w = np.linspace(0,8,20); y_w = np.linspace(-3,3,20); Z, Y = np.meshgrid(z_w, y_w)
        fig.add_trace(go.Surface(x=np.linspace(-3,3,20), y=Y, z=np.zeros_like(Y), opacity=0.3, showscale=False, name='Datum'))
        fig.add_trace(go.Surface(x=0.2*(Z/8), y=Y, z=Z, colorscale='Jet', name='Real'))
        fig.add_trace(go.Surface(x=np.full_like(Z, tol/2), y=Y, z=Z, opacity=0.2, colorscale=[[0,'blue'],[1,'blue']], showscale=False, name='Zona'))
    elif feature == 'Paralelismo':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        fig.add_trace(go.Surface(x=x, y=y, z=5+0.05*x, colorscale='Magma', name='Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5+tol/2), opacity=0.2, colorscale=[[0,'purple'],[1,'purple']], showscale=False, name='Lim'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5-tol/2), opacity=0.2, colorscale=[[0,'purple'],[1,'purple']], showscale=False, name='Lim'))
    elif feature == 'Posición':
        fig.add_trace(go.Surface(x=0.5*np.cos(tg)+0.1, y=0.5*np.sin(tg)+0.1, z=zg, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,10], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], line=dict(color='black', dash='dash'), name='Teórico'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'yellow'],[1,'yellow']], showscale=False, name='Zona'))
    elif feature == 'Concentricidad':
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, colorscale=[[0,'gray'],[1,'gray']], showscale=False, name='Datum'))
        fig.add_trace(go.Surface(x=(4+0.05*np.sin(zg))*np.cos(tg), y=(4+0.05*np.sin(zg))*np.sin(tg), z=zg, colorscale='Cividis', name='Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.4, colorscale=[[0,'yellow'],[1,'yellow']], showscale=False, name='Zona'))
    elif feature == 'Alabeo Circular':
        fig.add_trace(go.Scatter3d(x=5.3*np.cos(theta)+0.2, y=5.3*np.sin(theta), z=np.zeros_like(theta), line=dict(color='purple', width=6), name='Medida'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot'), name='Límite'))
    elif feature == 'Perfil de una línea':
        x_v = np.linspace(0,10,50); z_n = 2*np.sin(x_v)
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+0.1*np.random.normal(0,1,x_v.shape), line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+tol/2, line=dict(color='green', width=5, dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n-tol/2, line=dict(color='green', width=5, dash='dash'), name='Min'))
    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3, 3, 30); y = np.linspace(-3, 3, 30); xg, yg = np.meshgrid(x, y); zg = 0.5 * (xg**2 + yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9, name='Nominal'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, colorscale=[[0,'blue'],[1,'blue']], showscale=False, name='Max'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, colorscale=[[0,'blue'],[1,'blue']], showscale=False, name='Min'))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMADO)
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ REPRODUCIR", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    draw_rect_trace(fig, -1, -1, 11, 0, color="black", fill="#ccc")
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
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
    
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    draw_line_trace(fig, 1, 4, 11, 4, width=1, dash='longdashdot')

    draw_line_trace(fig, 10, 6, 10.5, 6, width=1)
    draw_line_trace(fig, 10, 2, 10.5, 2, width=1)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5.5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    if ftype == 'surf': leader_x, leader_y = 6, 6; frame_x, frame_y = 6, 7.5 
    else: leader_x, leader_y = 10.25, 4.8; frame_x, frame_y = 10.25, 1.5 

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

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

menu = {
    '1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'],
    '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'],
    '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'],
    '4. Control': ['Alabeo Circular', 'Alabeo Total'],
    '5. Posición': ['Posición', 'Concentricidad']
}

cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
feat = st.sidebar.selectbox("Característica", menu[cat])
tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)

st.sidebar.markdown("### 👁️ Vista")
view_mode = st.sidebar.radio("Seleccione una vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Interpretación de Plano"], index=0)
st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- RENDERIZADO ---
info = gdt_data.get(feat, {'symbol': '?', 'def': '...'})

st.markdown(f"""
<div class="gdt-card">
    <div style="display: flex; align-items: center;">
        <div class="big-icon" style="flex: 1;">{info['symbol']}</div>
        <div style="flex: 4; padding-left: 20px;">
            <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
            <p><strong>Definición:</strong> {info['def']}</p>
            <p>🆚 <b>Comparación:</b> {info['compare']}</p>
            <p>🛠️ <b>Aplicación:</b> {info['app']} | {info['why']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# COTAS (Arriba)
st.plotly_chart(plot_control_frame(feat, tol), use_container_width=True)

if view_mode == "📐 Simulación 3D":
    st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🔍 Detalle Visual:</b><br>{info.get('sim_3d_desc', '...')}</div>""", unsafe_allow_html=True)

elif view_mode == "🏭 Montaje Real":
    st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🏭 Montaje:</b><br>{info.get('real_desc', '...')}</div>""", unsafe_allow_html=True)

elif view_mode == "📝 Interpretación de Plano":
    st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
    tol_str = f"Ø {tol} mm" if info.get('type', 'surf') == 'axis' else f"{tol} mm"
    st.markdown(f"""
    <div class="interpretation-box">
        <h4>🤓 Interpretación del Plano:</h4>
        <p style="font-size: 1.1em;">
            "Esta característica de <span class="tech-text" style="color: #d63384;">{feat.upper()}</span> 
            tiene una tolerancia de <b>{tol_str}</b>."
        </p>
        <ul>
            <li><b>Controla:</b> {info.get('desc', '').capitalize()}.</li>
            <li><b>Zona de Tolerancia:</b> {info.get('zone', '').capitalize()}.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
