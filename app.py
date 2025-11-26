import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA "HIGH CONTRAST ENGINEERING" - RESTAURADO)
# ==========================================
# Paleta de Colores V5.1 (La que funcionaba bien)
MAIN_BG = "#D5D5D7"      # Gris Acero (Fondo Principal)
SIDEBAR_BG = "#1E1E1E"   # Negro Carbón (Barra Lateral)
CARD_BG = "#FFFFFF"      # Blanco Puro (Tarjetas)
TEXT_MAIN = "#000000"    # Negro (Texto Principal)
TEXT_SIDE = "#FFFFFF"    # Blanco (Texto Barra Lateral)
ACCENT = "#0d6efd"       # Azul Ingeniería

st.markdown(f"""
<style>
    /* 1. FONDO PRINCIPAL */
    .stApp {{
        background-color: {MAIN_BG};
        color: {TEXT_MAIN};
    }}
    
    /* 2. BARRA LATERAL (OSCURA) */
    [data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG};
    }}
    /* Forzar texto blanco en la barra lateral */
    [data-testid="stSidebar"] * {{
        color: {TEXT_SIDE} !important;
    }}
    /* Arreglar inputs en sidebar para que sean legibles */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] select, [data-testid="stSidebar"] div[role="radiogroup"] {{
        color: {TEXT_MAIN} !important;
    }}
    
    /* 3. TARJETAS DE DEFINICIÓN */
    .gdt-card {{
        background-color: {CARD_BG};
        border-left: 8px solid {ACCENT};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        color: {TEXT_MAIN};
        margin-bottom: 20px;
    }}

    /* 4. TARJETAS DE EXPLICACIÓN VISUAL */
    .visual-card {{
        background-color: #f0f2f6;
        border: 1px solid #ccc;
        padding: 15px;
        border-radius: 8px;
        color: {TEXT_MAIN};
        font-size: 0.95em;
        margin-top: 10px;
    }}
    
    /* 5. FUENTES GLOBALES (Forzar Negro en área principal) */
    .main h1, .main h2, .main h3, .main h4, .main p, .main li, .main span, .main label {{
        color: {TEXT_MAIN} !important;
    }}
    
    /* 6. ICONOS GIGANTES */
    .big-icon {{
        font-size: 100px;
        text-align: center;
        font-weight: bold;
        color: {TEXT_MAIN};
        display: flex; align-items: center; justify-content: center; height: 100%;
    }}

    /* Ajustes generales */
    .block-container {{padding-top: 2rem; padding-bottom: 2rem; padding-left: 2rem; padding-right: 2rem;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS PEDAGÓGICA (COMPLETA)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤',
        'def': 'Controla qué tan recta es una línea específica (como el eje central o una línea en la superficie).',
        'compare': '🆚 <b>Diferencia:</b> Se evalúa en 2D. No confundir con <b>Planicidad</b> (superficies) ni <b>Cilindricidad</b> (3D).',
        'app': '🔩 <b>Aplicación Real:</b> Vástagos de cilindros hidráulicos, rieles de guías lineales.',
        'why': '⚠️ <b>Importancia:</b> Un vástago doblado dañará los sellos prematuramente, causando fugas.',
        'sim_3d_desc': '🔵 <b>Línea Azul:</b> Eje real de la pieza (exageradamente doblado).<br>🟠 <b>Cilindro Naranja:</b> Zona de tolerancia. El eje debe estar contenido dentro.',
        'real_desc': '🏭 <b>Montaje:</b> Pieza sobre bloques V. Reloj comparador sobre la generatriz superior.<br>👁️ <b>Acción:</b> Desplazar reloj longitudinalmente.'
    },
    'Planicidad': {
        'symbol': '⏥',
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'compare': '🆚 <b>Diferencia:</b> No requiere Datum. Es una cualidad intrínseca de la superficie.',
        'app': '🚗 <b>Aplicación Real:</b> Culatas de motor (cabezas) y mesas de mármol.',
        'why': '⚠️ <b>Importancia:</b> Una culata deformada no sellará con el empaque, mezclando fluidos.',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Pieza real con valles y crestas.<br>🔴 <b>Planos Rojos:</b> Límites superior e inferior (Sándwich).',
        'real_desc': '🏭 <b>Montaje:</b> Reloj comparador en soporte deslizante sobre la superficie (o la pieza se mueve sobre un mármol con palpador inferior).'
    },
    'Redondez': {
        'symbol': '○',
        'def': 'Condición donde todos los puntos de una superficie circular (corte 2D) equidistan de un centro.',
        'compare': '🆚 <b>Diferencia:</b> Se mide por sección. No confundir con <b>Cilindricidad</b> (3D).',
        'app': '⚙️ <b>Aplicación Real:</b> Pistas de rodamientos, muñones de cigüeñal.',
        'why': '⚠️ <b>Importancia:</b> La falta de redondez causa vibración y ruido.',
        'sim_3d_desc': '🔵 <b>Línea Azul:</b> Perfil real medido (ovalado/lobulado).<br>🔴 <b>Círculos Rojos:</b> Límites concéntricos de tolerancia.',
        'real_desc': '🏭 <b>Montaje:</b> Pieza en plato giratorio de precisión. Palpador fijo toca la superficie mientras gira.'
    },
    'Cilindricidad': {
        'symbol': '⌭',
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'compare': '🆚 <b>Diferencia:</b> La más estricta para ejes. Incluye redondez y rectitud.',
        'app': '💉 <b>Aplicación Real:</b> Pistones de inyección diésel.',
        'why': '⚠️ <b>Importancia:</b> Crítica para sellos metal-metal.',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Pieza real deformada.<br>🔴 <b>Mallas Rojas:</b> Dos cilindros coaxiales perfectos (frontera).',
        'real_desc': '🏭 <b>Montaje:</b> Máquina de medición de redondez que escanea en espiral (o CMM).'
    },
    'Angularidad': {
        'symbol': '∠',
        'def': 'Controla una superficie o eje a un ángulo específico (no 90°) respecto a un Datum.',
        'compare': '🆚 <b>Diferencia:</b> Define una zona de tolerancia milimétrica entre dos planos (no es ±grados).',
        'app': '📐 <b>Aplicación Real:</b> Guías de cola de milano.',
        'why': '⚠️ <b>Importancia:</b> Asegura contacto uniforme en superficies inclinadas.',
        'sim_3d_desc': '🌈 <b>Plano Inclinado:</b> Superficie real.<br>🟢 <b>Planos Verdes:</b> Límites paralelos inclinados al ángulo exacto.',
        'real_desc': '🏭 <b>Montaje:</b> Uso de <b>Mesa de Senos</b> para nivelar la superficie y medir con reloj horizontal.'
    },
    'Perpendicularidad': {
        'symbol': '⟂',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'compare': '🆚 <b>Diferencia:</b> Caso especial de Angularidad a 90°.',
        'app': '🏗️ <b>Aplicación Real:</b> Escuadras de fijación.',
        'why': '⚠️ <b>Importancia:</b> Si no es perpendicular, el ensamble quedará torcido.',
        'sim_3d_desc': '🌈 <b>Pared:</b> Superficie real inclinada.<br>🔵 <b>Planos Azules:</b> Zona de tolerancia perpendicular al Datum.',
        'real_desc': '🏭 <b>Montaje:</b> Comparación contra una <b>Escuadra Patrón</b> de granito usando reloj.'
    },
    'Paralelismo': {
        'symbol': '∥',
        'def': 'Todos los puntos de la superficie deben estar a la misma distancia del Datum.',
        'compare': '🆚 <b>Diferencia:</b> Controla orientación (0°) y planicidad.',
        'app': '🛤️ <b>Aplicación Real:</b> Rieles de máquinas herramienta.',
        'why': '⚠️ <b>Importancia:</b> Evita atascamientos en partes móviles.',
        'sim_3d_desc': '🌈 <b>Superficie Sup:</b> Pieza real.<br>🟣 <b>Planos Morados:</b> Zona de tolerancia paralela al Datum inferior.',
        'real_desc': '🏭 <b>Montaje:</b> Deslizar reloj comparador sobre la cara superior (pieza apoyada en mármol).'
    },
    'Concentricidad': {
        'symbol': '◎',
        'def': 'Controla que los puntos medios (medianos) de secciones opuestas caigan en una zona cilíndrica.',
        'compare': '🆚 <b>Diferencia:</b> Es teórica (balanceo). Difícil de medir (usar Alabeo si es posible).',
        'app': '⚖️ <b>Aplicación Real:</b> Rotores de turbinas.',
        'why': '⚠️ <b>Importancia:</b> Minimiza vibración rotacional.',
        'sim_3d_desc': '🔴 <b>Línea Roja:</b> Lugar geométrico de los puntos medios.<br>🟡 <b>Cilindro:</b> Zona de tolerancia.',
        'real_desc': '🏭 <b>Montaje:</b> Complejo. Girar pieza y medir puntos opuestos simultáneamente para calcular centros.'
    },
    'Posición': {
        'symbol': '⌖',
        'def': 'Controla la ubicación exacta del centro de una característica (agujero) respecto a Datums.',
        'compare': '🆚 <b>Diferencia:</b> Garantiza intercambiabilidad en ensambles.',
        'app': '🔩 <b>Aplicación Real:</b> Patrones de pernos en rines.',
        'why': '⚠️ <b>Importancia:</b> Asegura que los tornillos entren en los agujeros correspondientes.',
        'sim_3d_desc': '🔴 <b>Eje Rojo:</b> Eje del agujero real.<br>🟡 <b>Cilindro Amarillo:</b> Zona de tolerancia en posición teórica.',
        'real_desc': '🏭 <b>Montaje:</b> CMM (Máquina de Coordenadas) o Gage funcional de pernos fijos.'
    },
    'Alabeo Circular': {
        'symbol': '↗',
        'def': '(Runout). Variación de la superficie en una sección circular al girar 360°.',
        'compare': '🆚 <b>Diferencia:</b> Suma redondez + concentricidad en esa sección.',
        'app': '🛑 <b>Aplicación Real:</b> Discos de freno.',
        'why': '⚠️ <b>Importancia:</b> Evita pulsaciones al frenar.',
        'sim_3d_desc': '🟣 <b>Línea Morada:</b> Trayectoria del palpador.<br>🔴 <b>Líneas Rojas:</b> Máximo y mínimo.',
        'real_desc': '🏭 <b>Montaje:</b> Pieza gira en bloques V. Reloj fijo mide la variación (TIR).'
    },
    'Alabeo Total': {
        'symbol': '⌰',
        'def': '(Total Runout). Variación de TODA la superficie al girar y desplazarse.',
        'compare': '🆚 <b>Diferencia:</b> Suma rectitud + angularidad + redondez + concentricidad.',
        'app': '💧 <b>Aplicación Real:</b> Ejes de bombas (zona de sellos).',
        'why': '⚠️ <b>Importancia:</b> Imperfecciones causan fugas.',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Pieza girando.<br>🔴 <b>Mallas Rojas:</b> Cilindros límite coaxiales.',
        'real_desc': '🏭 <b>Montaje:</b> Reloj se desplaza a lo largo del eje mientras la pieza gira (barrido espiral).'
    },
    'Perfil de una línea': {
        'symbol': '⌒',
        'def': 'Controla la forma de una curva 2D en una sección transversal.',
        'compare': '🆚 <b>Diferencia:</b> Solo aplica al borde cortado.',
        'app': '✈️ <b>Aplicación Real:</b> Perfil de ala de avión.',
        'why': '⚠️ <b>Importancia:</b> Aerodinámica.',
        'sim_3d_desc': '🔵 <b>Línea Azul:</b> Curva real.<br>🟢 <b>Banda Verde:</b> Zona de tolerancia (ancho constante).',
        'real_desc': '🏭 <b>Montaje:</b> Comparador óptico (proyector de perfiles) con plantilla.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓',
        'def': 'Controla la forma, orientación y ubicación de una superficie 3D compleja.',
        'compare': '🆚 <b>Diferencia:</b> Piel tridimensional.',
        'app': '🚗 <b>Aplicación Real:</b> Carrocería de autos.',
        'why': '⚠️ <b>Importancia:</b> Estética y ajuste.',
        'sim_3d_desc': '🌈 <b>Superficie:</b> Forma real.<br>🔵 <b>Capas Azules:</b> Límites (Envelope) superior e inferior.',
        'real_desc': '🏭 <b>Montaje:</b> Escaneo con CMM comparado contra modelo CAD.'
    }
}

# ==========================================
# 2. FUNCIONES DE VISUALIZACIÓN
# ==========================================

def get_plot_layout(title, is_3d=True):
    """Configura el diseño gráfico integrado con el tema"""
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    
    if is_3d:
        # Fondo transparente para que se funda con el gris de la app
        layout['paper_bgcolor'] = MAIN_BG 
        layout['plot_bgcolor'] = MAIN_BG
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#cccccc", showbackground=True)
        )
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.5)", bordercolor="#333", borderwidth=1, font=dict(color="black"))
    else:
        # Fondo blanco para planos técnicos (simulando papel)
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
        layout['xaxis'] = dict(visible=False, showgrid=False)
        layout['yaxis'] = dict(visible=False, showgrid=False)
        # Borde negro para el plano
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
        
    return layout

# --- A. SIMULACIONES 3D ---
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    if feature == 'Rectitud':
        # RECTITUD: Visualización 2D en espacio 3D (Banana)
        x_real = 0.3 * np.sin(z * 0.5); y_real = np.zeros_like(z)
        fig.add_trace(go.Scatter3d(x=x_real, y=y_real, z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real (Doblado)'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.2, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona Tol'))
        fig.add_trace(go.Scatter3d(x=np.zeros_like(z), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje Nominal'))
    
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Sup. Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Plano Sup.'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Plano Inf.'))

    elif feature == 'Redondez':
        r = 5 + 0.2 * np.cos(3*theta)
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='blue', width=6), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Límite Sup.'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(theta), y=(5-tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Límite Inf.'))

    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Sup. Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=6, dash='longdash'), name='Eje Común'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Límites', showlegend=True))

    elif feature == 'Angularidad':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20)); z_nom = x * np.tan(np.radians(45))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom + 0.1*np.sin(y), colorscale='Plasma', name='Sup. Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'green'],[1,'green']], name='Lim. Sup'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'green'],[1,'green']], name='Lim. Inf'))

    elif feature == 'Perpendicularidad':
        z_w = np.linspace(0,8,20); y_w = np.linspace(-3,3,20); Z, Y = np.meshgrid(z_w, y_w)
        fig.add_trace(go.Surface(x=np.linspace(-3,3,20), y=Y, z=np.zeros_like(Y), opacity=0.3, showscale=False, name='Datum'))
        fig.add_trace(go.Surface(x=0.2*(Z/8), y=Y, z=Z, colorscale='Jet', name='Pared Real'))
        fig.add_trace(go.Surface(x=np.full_like(Z, tol/2), y=Y, z=Z, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Zona Tol'))
        fig.add_trace(go.Surface(x=np.full_like(Z, -tol/2), y=Y, z=Z, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Zona Tol'))

    elif feature == 'Paralelismo':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        fig.add_trace(go.Surface(x=x, y=y, z=5+0.05*x, colorscale='Magma', name='Sup. Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5+tol/2), opacity=0.2, showscale=False, colorscale=[[0,'purple'],[1,'purple']], name='Lim. Sup'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5-tol/2), opacity=0.2, showscale=False, colorscale=[[0,'purple'],[1,'purple']], name='Lim. Inf'))

    elif feature == 'Posición':
        z_c = np.linspace(0,4,20); TH, Z = np.meshgrid(theta, z_c)
        fig.add_trace(go.Surface(x=0.5*np.cos(TH)+0.1, y=0.5*np.sin(TH)+0.1, z=Z, colorscale='Ice', showscale=False, name='Agujero Real'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,4], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,4], line=dict(color='black', dash='dash'), name='Eje Teórico'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona Tol'))

    elif feature == 'Concentricidad':
        cx = (0.05 * np.sin(z))[:, np.newaxis]; cy = (0.05 * np.cos(z))[:, np.newaxis]
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, showscale=False, colorscale=[[0,'gray'],[1,'gray']], name='Ref. Datum'))
        fig.add_trace(go.Surface(x=cx+2*np.cos(tg), y=cy+2*np.sin(tg), z=zg, colorscale='Cividis', name='Sup. Real'))
        fig.add_trace(go.Scatter3d(x=cx.flatten(), y=cy.flatten(), z=z.repeat(30), mode='lines', line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.4, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona Tol'))

    elif feature == 'Alabeo Circular':
        fig.add_trace(go.Scatter3d(x=5.3*np.cos(theta)+0.2, y=5.3*np.sin(theta), z=np.zeros_like(theta), line=dict(color='purple', width=6), name='Medición'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot'), name='Límites'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,2], mode='lines', line=dict(color='black', width=5, dash='longdash'), name='Eje Datum'))

    elif feature == 'Perfil de una línea':
        x_v = np.linspace(0,10,50); z_n = 2*np.sin(x_v)
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+0.1*np.random.normal(0,1,x_v.shape), line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+tol/2, line=dict(color='green', width=5, dash='dash'), name='Límite Sup'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n-tol/2, line=dict(color='green', width=5, dash='dash'), name='Límite Inf'))
        xb = np.concatenate([x_v, x_v[::-1]]); zb = np.concatenate([z_n+tol/2, (z_n-tol/2)[::-1]])
        fig.add_trace(go.Mesh3d(x=xb, y=np.zeros_like(xb), z=zb, color='green', opacity=0.1, name='Zona'))

    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3, 3, 30); y = np.linspace(-3, 3, 30); xg, yg = np.meshgrid(x, y)
        zg = 0.5 * (xg**2 + yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9, name='Nominal'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Límite Sup'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Límite Inf'))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# --- B. MONTAJES REALES (ANIMADOS) ---
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Esquema de Inspección: {feature.upper()}", is_3d=False)
    layout['updatemenus'] = [dict(
        type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center",
        buttons=[dict(label="▶️ REPRODUCIR INSPECCIÓN", method="animate", 
        args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True, mode='immediate')])]
    )]
    fig.update_layout(**layout)
    
    frames = []
    
    # GRUPO 1: DESLIZAMIENTO
    if feature in ['Rectitud', 'Paralelismo', 'Planicidad', 'Perfil de una línea', 'Perfil de una superficie']:
        fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#ccc", line=dict(color="black"))
        fig.add_annotation(x=5, y=-0.5, text="DATUM A (Mármol)", font=dict(color="black", size=14), showarrow=False)
        
        x_path = np.linspace(0, 10, 60)
        y_surf = 1.5 + 0.2 * np.sin(x_path * 1.5) if 'Perfil' not in feature else 1.5 + 0.3*np.sin(x_path)
        
        fig.add_trace(go.Scatter(x=x_path, y=y_surf, mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        xi, yi = x_path[0], y_surf[0]; yc = yi + 3; dx=0.5; dy=0
        
        for i in range(len(x_path)):
            xi, yi = x_path[i], y_surf[i]; yc = yi + 3
            dx = 0.5 * np.cos(i*0.5); dy = 0.5 * np.sin(i*0.5)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="#444", width=4), name="Vástago")) 
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj")) 
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja")) 

    # GRUPO 2: ROTACIÓN
    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        fig.add_shape(type="rect", x0=-1, y0=1, x1=1, y1=5, fillcolor="#555", line=dict(color="black"))
        fig.add_annotation(x=0, y=5.5, text="Chuck", font=dict(color="black"), showarrow=False)
        fig.add_shape(type="rect", x0=1, y0=2, x1=9, y1=4, line=dict(color="blue", width=3))
        fig.add_annotation(x=5, y=3, text="Pieza Girando ↺", font=dict(size=18, color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0), showlegend=False)) 

        t = np.linspace(0, 4*np.pi, 60)
        x_pos = np.linspace(2, 8, 60) if feature in ['Cilindricidad', 'Alabeo Total'] else np.full(60, 5)
        xi = x_pos[0]; yi = 4; yc = yi + 2.5; dx=0.5; dy=0

        for i in range(len(t)):
            xi = x_pos[i]; yi = 4; yc = yi + 2.5
            dx = 0.5 * np.cos(t[i]); dy = 0.5 * np.sin(t[i])
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))

        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # GRUPO 3: PERPENDICULARIDAD
    elif feature == 'Perpendicularidad':
        fig.add_shape(type="path", path="M 2,0 L 2,6 L 3,6 L 3,1 L 6,1 L 6,0 Z", fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=4, y=0.5, text="Escuadra", font=dict(color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[7, 6.5], y=[0, 6], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        y_path = np.linspace(0.5, 5.5, 50); x_surf = np.linspace(7, 6.5, 50)
        yi=y_path[0]; xi=x_surf[0]; xc=xi-2.5; dx=0.5; dy=0

        for i in range(len(y_path)):
            yi = y_path[i]; xi = x_surf[i]; xc = xi - 2.5
            dx = 0.5 * np.cos(i*0.2); dy = 0.5 * np.sin(i*0.2)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xc], y=[yi, yi]), go.Scatter(x=[xc], y=[yi]), go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi, xc], y=[yi, yi], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xc], y=[yi], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # GRUPO 4: ANGULARIDAD
    elif feature == 'Angularidad':
        fig.add_shape(type="path", path="M 1,0 L 9,3 L 9,0 Z", fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=5, y=1, text="Seno", font=dict(color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[1,9], y=[3.2, 6.2], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        x_path = np.linspace(1, 9, 50); y_path = np.linspace(3.2, 6.2, 50)
        xi=x_path[0]; yi=y_path[0]; yc=yi+2.5; dx=0.5; dy=0

        for i in range(len(x_path)):
            xi = x_path[i]; yi = y_path[i]; yc = yi + 2.5
            dx = 0.5 * np.cos(i); dy = 0.5 * np.sin(i)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # GRUPO 5: POSICIÓN
    elif feature == 'Posición':
        fig.add_shape(type="rect", x0=2, y0=0, x1=8, y1=3, fillcolor="#ccc", line=dict(color="black"))
        fig.add_annotation(x=3, y=1.5, text="Pieza", font=dict(color="black"), showarrow=False)
        fig.add_shape(type="line", x0=4.5, y0=3, x1=4.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=6.5, y0=3, x1=6.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=4.5, y0=1, x1=6.5, y1=1, line=dict(color="black", width=2, dash="dot"))
        
        y_path = np.concatenate([np.linspace(6, 2, 30), np.linspace(2, 6, 30)])
        x_pos = 5.5; yi = y_path[0]
        
        for i in range(len(y_path)):
            yi = y_path[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4]), go.Scatter(x=[x_pos], y=[yi])
            ], traces=[1, 2]))
            
        fig.add_trace(go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4], mode="lines", line=dict(color="red", width=3), name="Stylus"))
        fig.add_trace(go.Scatter(x=[x_pos, x_pos], y=[yi], mode="markers", marker=dict(size=15, color="red"), name="Tip"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="lines", name="Dummy"))

    fig.frames = frames
    return fig

# ==========================================
# 3. INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

menu_dict = {
    '1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'],
    '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'],
    '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'],
    '4. Control': ['Alabeo Circular', 'Alabeo Total'],
    '5. Posición': ['Posición', 'Concentricidad']
}

cat = st.sidebar.selectbox("Categoría", list(menu_dict.keys()))
feat = st.sidebar.selectbox("Característica", menu_dict[cat])
tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)

st.sidebar.markdown("### 👁️ Vista")
view_mode = st.sidebar.radio("Seleccione una vista:", ["📐 Simulación 3D", "🏭 Plano de Montaje Real"], index=0)

st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- RENDERIZADO ---
def_data = gdt_data.get(feat, {'symbol': '?', 'def': 'Sin definición.', 'compare': '', 'app': '', 'why': ''})

st.markdown(f"""
<div class="gdt-card">
    <div style="display: flex; align-items: center;">
        <div class="big-icon" style="flex: 1;">{def_data['symbol']}</div>
        <div style="flex: 4; padding-left: 20px;">
            <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
            <p><strong>Definición:</strong> {def_data['def']}</p>
            <p>{def_data['compare']}</p>
            <p>{def_data['app']}</p>
            <p>{def_data['why']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if view_mode == "📐 Simulación 3D":
    fig_3d = plot_3d_simulation(feat, tol)
    st.plotly_chart(fig_3d, use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🔍 Explicación Visual:</b><br>{def_data.get('sim_3d_desc', 'Visualización de la tolerancia.')}</div>""", unsafe_allow_html=True)

elif view_mode == "🏭 Plano de Montaje Real":
    fig_real = plot_real_inspection_anim(feat)
    st.plotly_chart(fig_real, use_container_width=True)
    st.markdown(f"""<div class='visual-card'><b>🏭 Explicación del Montaje:</b><br>{def_data.get('real_desc', 'Esquema de inspección estándar.')}</div>""", unsafe_allow_html=True)
