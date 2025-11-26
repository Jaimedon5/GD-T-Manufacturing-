import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA "ENGINEERING DASHBOARD")
# ==========================================
# Colores
BG_COLOR = "#E6E6EA"  # Gris tenue para el fondo
CARD_COLOR = "#FFFFFF" # Blanco para las tarjetas de info
TEXT_COLOR = "#1F1F1F" # Negro suave para texto
ACCENT_COLOR = "#0d6efd" # Azul ingeniería

st.markdown(f"""
<style>
    /* 1. FORZAR FONDO GRIS EN TODA LA APP */
    .stApp {{
        background-color: {BG_COLOR};
    }}
    
    /* 2. AJUSTAR CONTENEDOR PRINCIPAL */
    .block-container {{
        padding-top: 2rem; 
        padding-bottom: 1rem; 
        padding-left: 2rem; 
        padding-right: 2rem;
    }}

    /* 3. TARJETAS DE DEFINICIÓN (ESTILO ELEGANTE) */
    .gdt-card {{
        background-color: {CARD_COLOR};
        border-left: 6px solid {ACCENT_COLOR};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}
    
    /* 4. FORZAR COLOR DE TEXTO NEGRO EN TÍTULOS Y PÁRRAFOS (ÁREA PRINCIPAL) */
    /* Esto arregla el problema de invisibilidad en modo oscuro */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p, .stMarkdown li {{
        color: {TEXT_COLOR} !important;
    }}
    
    /* 5. ESTILOS DE ICONOS */
    .big-icon {{
        font-size: 60px;
        text-align: center;
        font-weight: bold;
        color: {TEXT_COLOR};
    }}
    
    /* OCULTAR ELEMENTOS DE STREAMLIT */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (TEXTOS TÉCNICOS)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤',
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta perfecta.',
        'compare': '🆚 <b>Diferencia:</b> Es en 2D (una línea). No confundir con <b>Planicidad</b>, que es para toda una superficie 3D.',
        'app': '🔩 <b>Aplicación Real:</b> Vástagos de cilindros hidráulicos.',
        'why': '⚠️ <b>Importancia:</b> Si el vástago no es recto, dañará los sellos al entrar y salir, causando fugas de aceite.'
    },
    'Planicidad': {
        'symbol': '⏥',
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'compare': '🆚 <b>Diferencia:</b> No requiere un Datum. Es una cualidad intrínseca de la superficie.',
        'app': '🚗 <b>Aplicación Real:</b> La cabeza del motor (culata) y el bloque del motor.',
        'why': '⚠️ <b>Importancia:</b> Si no es plana, la junta (empaque) no sellará bien, provocando fugas de compresión.'
    },
    'Redondez': {
        'symbol': '○',
        'def': 'Condición donde todos los puntos de una superficie circular (en cualquier corte transversal) equidistan de un centro.',
        'compare': '🆚 <b>Diferencia:</b> Se mide en cortes 2D. No confundir con <b>Cilindricidad</b> que evalúa todo el cilindro a la vez.',
        'app': '⚙️ <b>Aplicación Real:</b> Pistas de rodamientos (baleros).',
        'why': '⚠️ <b>Importancia:</b> Una mala redondez causa vibraciones y ruido excesivo a alta velocidad.'
    },
    'Cilindricidad': {
        'symbol': '⌭',
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente.',
        'compare': '🆚 <b>Diferencia:</b> Es más estricta que la Redondez. Controla la forma 3D completa.',
        'app': '💉 <b>Aplicación Real:</b> Pistones de inyección diésel.',
        'why': '⚠️ <b>Importancia:</b> Garantiza que el pistón se deslice suavemente sin atorarse y sin perder presión.'
    },
    'Angularidad': {
        'symbol': '∠',
        'def': 'Controla una superficie o eje para que esté a un ángulo específico (diferente a 90°) respecto a un Datum.',
        'compare': '🆚 <b>Diferencia:</b> Define una "zona de tolerancia" entre dos planos paralelos inclinados.',
        'app': '📐 <b>Aplicación Real:</b> Rampas de guías de deslizamiento.',
        'why': '⚠️ <b>Importancia:</b> Asegura contacto uniforme en superficies inclinadas que transmiten carga.'
    },
    'Perpendicularidad': {
        'symbol': '⟂',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'compare': '🆚 <b>Diferencia:</b> Es un caso especial de Angularidad fija a 90°.',
        'app': '🏗️ <b>Aplicación Real:</b> Escuadras de fijación.',
        'why': '⚠️ <b>Importancia:</b> Si no es perpendicular, el ensamble quedará torcido.'
    },
    'Paralelismo': {
        'symbol': '∥',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano Datum.',
        'compare': '🆚 <b>Diferencia:</b> Controla orientación y planicidad simultáneamente.',
        'app': '🛤️ <b>Aplicación Real:</b> Rieles de trenes o guías lineales.',
        'why': '⚠️ <b>Importancia:</b> Si no son paralelos, el carro se amarrará o tendrá juego excesivo.'
    },
    'Concentricidad': {
        'symbol': '◎',
        'def': 'Controla que los puntos medios de secciones opuestas del cilindro caigan dentro de una zona cilíndrica teórica.',
        'compare': '🆚 <b>Diferencia:</b> Es teórica (balanceo). A menudo se prefiere usar <b>Alabeo</b> para superficies.',
        'app': '⚖️ <b>Aplicación Real:</b> Ejes de alta velocidad.',
        'why': '⚠️ <b>Importancia:</b> Reduce la vibración por desbalanceo de masas.'
    },
    'Posición': {
        'symbol': '⌖',
        'def': 'Controla la ubicación exacta del centro de una característica (agujero) respecto a los Datums.',
        'compare': '🆚 <b>Diferencia:</b> Garantiza la intercambiabilidad de partes atornilladas.',
        'app': '🔩 <b>Aplicación Real:</b> Patrones de agujeros en tapas de motor.',
        'why': '⚠️ <b>Importancia:</b> Asegura que los tornillos pasen por los agujeros y coincidan con la contraparte.'
    },
    'Alabeo Circular': {
        'symbol': '↗',
        'def': '(Runout). Controla la variación de la superficie en una sección circular mientras la pieza gira.',
        'compare': '🆚 <b>Diferencia:</b> Mide "corte por corte".',
        'app': '🛑 <b>Aplicación Real:</b> Discos de freno.',
        'why': '⚠️ <b>Importancia:</b> Evita vibraciones en el pedal al frenar.'
    },
    'Alabeo Total': {
        'symbol': '⌰',
        'def': '(Total Runout). Controla toda la superficie cilíndrica simultáneamente mientras la pieza gira y el indicador se desplaza.',
        'compare': '🆚 <b>Diferencia:</b> Controla conicidad, rectitud, redondez y concentricidad a la vez.',
        'app': '💧 <b>Aplicación Real:</b> Ejes de bombas en la zona del sello.',
        'why': '⚠️ <b>Importancia:</b> Imperfecciones causan fugas inmediatas.'
    },
    'Perfil de una línea': {
        'symbol': '⌒',
        'def': 'Controla la forma de una línea curva (2D) en cualquier sección transversal.',
        'compare': '🆚 <b>Diferencia:</b> Solo aplica a la línea de corte.',
        'app': '✈️ <b>Aplicación Real:</b> Perfil de ala de avión.',
        'why': '⚠️ <b>Importancia:</b> Crítico para la aerodinámica.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓',
        'def': 'Controla la forma, orientación y ubicación de una superficie 3D compleja.',
        'compare': '🆚 <b>Diferencia:</b> Crea una "piel" de tolerancia tridimensional.',
        'app': '🚗 <b>Aplicación Real:</b> Carrocería de autos.',
        'why': '⚠️ <b>Importancia:</b> Estética y aerodinámica.'
    }
}

# ==========================================
# 2. FUNCIONES DE VISUALIZACIÓN
# ==========================================

# Función auxiliar para estilos de gráficas (Fondo Gris + Texto Negro)
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=BG_COLOR, # Fondo externo igual a la app
        plot_bgcolor=BG_COLOR,  # Fondo interno igual a la app
        font=dict(color='black'), # Texto negro
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=BG_COLOR),
            yaxis=dict(visible=False, backgroundcolor=BG_COLOR),
            zaxis=dict(visible=True, backgroundcolor=BG_COLOR, gridcolor="#cccccc", showbackground=True)
        )
        # Leyenda visible sobre fondo gris
        layout['legend'] = dict(bgcolor="rgba(255,255,255,0.6)", bordercolor="#333", borderwidth=1)
    else:
        # Para 2D (Blueprints)
        layout['xaxis'] = dict(visible=False, showgrid=False)
        layout['yaxis'] = dict(visible=False, showgrid=False)
        layout['plot_bgcolor'] = 'white' # El plano técnico se ve mejor en papel blanco
        
    return layout

# --- A. SIMULACIONES 3D ---
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    # Lógica gráfica (Simplificada para brevedad, lógica idéntica a la anterior pero con estilos nuevos)
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=np.sin(z/1.5)*0.2, y=np.cos(z/1.5)*0.15, z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona Tol'))
        fig.add_trace(go.Scatter3d(x=np.zeros_like(z), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='black', width=5, dash='dash'), name='Nominal'))
    
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Sup'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Inf'))

    elif feature == 'Redondez':
        r = 5 + 0.2 * np.cos(3*theta)
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(theta), y=(5-tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Min'))

    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=6, dash='longdash'), name='Eje'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Tol'))

    elif feature == 'Angularidad':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20)); z_nom = x * np.tan(np.radians(45))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom + 0.1*np.sin(y), colorscale='Plasma', name='Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'green'],[1,'green']], name='Max'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'green'],[1,'green']], name='Min'))

    elif feature == 'Perpendicularidad':
        z_w = np.linspace(0,8,20); y_w = np.linspace(-3,3,20); Z, Y = np.meshgrid(z_w, y_w)
        fig.add_trace(go.Surface(x=np.linspace(-3,3,20), y=Y, z=np.zeros_like(Y), opacity=0.3, showscale=False, name='Datum'))
        fig.add_trace(go.Surface(x=0.2*(Z/8), y=Y, z=Z, colorscale='Jet', name='Real'))
        fig.add_trace(go.Surface(x=np.full_like(Z, tol/2), y=Y, z=Z, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Tol'))
        fig.add_trace(go.Surface(x=np.full_like(Z, -tol/2), y=Y, z=Z, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Tol'))

    elif feature == 'Paralelismo':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        fig.add_trace(go.Surface(x=x, y=y, z=5+0.05*x, colorscale='Magma', name='Real'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5+tol/2), opacity=0.2, showscale=False, colorscale=[[0,'purple'],[1,'purple']], name='Max'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5-tol/2), opacity=0.2, showscale=False, colorscale=[[0,'purple'],[1,'purple']], name='Min'))

    elif feature == 'Posición':
        z_c = np.linspace(0,4,20); TH, Z = np.meshgrid(theta, z_c)
        fig.add_trace(go.Surface(x=0.5*np.cos(TH)+0.1, y=0.5*np.sin(TH)+0.1, z=Z, colorscale='Ice', showscale=False, name='Agujero'))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,4], line=dict(color='red', width=5), name='Eje Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,4], line=dict(color='black', dash='dash'), name='TP'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona'))

    elif feature == 'Concentricidad':
        cx = (0.05 * np.sin(z))[:, np.newaxis]; cy = (0.05 * np.cos(z))[:, np.newaxis]
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, showscale=False, colorscale=[[0,'gray'],[1,'gray']], name='Datum'))
        fig.add_trace(go.Surface(x=cx+2*np.cos(tg), y=cy+2*np.sin(tg), z=zg, colorscale='Cividis', name='Real'))
        fig.add_trace(go.Scatter3d(x=cx.flatten(), y=cy.flatten(), z=z.repeat(30), mode='lines', line=dict(color='red', width=5), name='Eje Mediano'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.4, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Tol'))

    elif feature == 'Alabeo Circular':
        fig.add_trace(go.Scatter3d(x=5.3*np.cos(theta)+0.2, y=5.3*np.sin(theta), z=np.zeros_like(theta), line=dict(color='purple', width=6), name='Medición'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot'), name='Lim'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,2], mode='lines', line=dict(color='black', width=5, dash='longdash'), name='Datum'))

    elif feature == 'Perfil de una línea':
        x_v = np.linspace(0,10,50); z_n = 2*np.sin(x_v)
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+0.1*np.random.normal(0,1,x_v.shape), line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+tol/2, line=dict(color='green', width=5, dash='dash'), name='Max'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n-tol/2, line=dict(color='green', width=5, dash='dash'), name='Min'))
        xb = np.concatenate([x_v, x_v[::-1]]); zb = np.concatenate([z_n+tol/2, (z_n-tol/2)[::-1]])
        fig.add_trace(go.Mesh3d(x=xb, y=np.zeros_like(xb), z=zb, color='green', opacity=0.1, name='Zona'))

    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3, 3, 30); y = np.linspace(-3, 3, 30); xg, yg = np.meshgrid(x, y)
        zg = 0.5 * (xg**2 + yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9, name='Nominal'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Max'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Min'))

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
        fig.add_trace(go.Scatter(x=[x_pos], y=[yi], mode="markers", marker=dict(size=15, color="red"), name="Tip"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="lines", name="Dummy"))

    fig.frames = frames
    return fig

# ==========================================
# 3. INTERFAZ DE USUARIO (STREAMLIT)
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
# Tarjeta de Definición
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

elif view_mode == "🏭 Plano de Montaje Real":
    fig_real = plot_real_inspection_anim(feat)
    st.plotly_chart(fig_real, use_container_width=True)
