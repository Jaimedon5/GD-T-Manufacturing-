import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Estilo para las tarjetas de definición */
    .gdt-card {
        background-color: #f8f9fa;
        border-left: 5px solid #0d6efd;
        padding: 15px;
        border-radius: 5px;
        color: black;
    }
    .big-icon {
        font-size: 80px;
        text-align: center;
        line-height: 100px;
        display: block;
    }
    .section-title {
        font-weight: bold;
        color: #0d6efd;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 0. BASE DE DATOS DE CONOCIMIENTO (DICCIONARIO ENRIQUECIDO)
# ==========================================
gdt_data = {
    'Rectitud': {
        'symbol': '⏤',
        'def': 'Condición donde cada elemento lineal de una superficie debe estar dentro de una línea recta perfecta.',
        'compare': '🆚 **Diferencia:** Es en 2D (una línea). No confundir con **Planicidad**, que es para toda una superficie 3D.',
        'app': '🔩 **Aplicación Real:** Vástagos de cilindros hidráulicos.',
        'why': '⚠️ **¿Por qué importa?** Si el vástago no es recto, dañará los sellos al entrar y salir, causando fugas de aceite.'
    },
    'Planicidad': {
        'symbol': '⏥',
        'def': 'Condición donde todos los puntos de una superficie deben estar contenidos entre dos planos paralelos.',
        'compare': '🆚 **Diferencia:** No requiere un "Datum" (referencia). Es una cualidad intrínseca de la superficie.',
        'app': '🚗 **Aplicación Real:** La cabeza del motor (culata) y el bloque del motor.',
        'why': '⚠️ **¿Por qué importa?** Si no es plana, la junta (empaque) no sellará bien, provocando fugas de compresión o mezcla de aceite y agua.'
    },
    'Redondez': {
        'symbol': '○',
        'def': 'Condición donde todos los puntos de una superficie circular (en cualquier corte transversal) equidistan de un centro.',
        'compare': '🆚 **Diferencia:** Se mide en cortes 2D. No confundir con **Cilindricidad** que evalúa todo el cilindro a la vez.',
        'app': '⚙️ **Aplicación Real:** Pistas de rodamientos (baleros).',
        'why': '⚠️ **¿Por qué importa?** Una mala redondez causa vibraciones, ruido excesivo y desgaste prematuro al girar a alta velocidad.'
    },
    'Cilindricidad': {
        'symbol': '⌭',
        'def': 'Controla la redondez, rectitud y conicidad de todo el cilindro simultáneamente. La superficie debe estar entre dos cilindros concéntricos.',
        'compare': '🆚 **Diferencia:** Es más estricta que la Redondez. Controla la forma 3D completa.',
        'app': '💉 **Aplicación Real:** Pistones de inyección diésel o pernos maestros.',
        'why': '⚠️ **¿Por qué importa?** Garantiza que el pistón se deslice suavemente sin atorarse y sin perder presión en toda su carrera.'
    },
    'Angularidad': {
        'symbol': '∠',
        'def': 'Controla una superficie o eje para que esté a un ángulo específico (diferente a 90°) respecto a un Datum.',
        'compare': '🆚 **Diferencia:** A diferencia de la tolerancia dimensional de ángulo (±1°), aquí se define una "zona de tolerancia" milimétrica entre dos planos.',
        'app': '📐 **Aplicación Real:** Rampas de guías de deslizamiento o bloques en V.',
        'why': '⚠️ **¿Por qué importa?** Asegura contacto uniforme en superficies inclinadas que transmiten carga.'
    },
    'Perpendicularidad': {
        'symbol': '⟂',
        'def': 'Condición donde una superficie o eje debe estar a 90° exactos respecto a un Datum.',
        'compare': '🆚 **Diferencia:** Es un caso especial de Angularidad fija a 90°. Controla qué tan "chueca" está una pared respecto al piso.',
        'app': '🏗️ **Aplicación Real:** Escuadras de fijación o la base de una columna de taladro.',
        'why': '⚠️ **¿Por qué importa?** Si un agujero no es perpendicular, el tornillo entrará torcido y la cabeza no asentará bien.'
    },
    'Paralelismo': {
        'symbol': '∥',
        'def': 'Condición donde todos los puntos de una superficie deben estar a la misma distancia de un plano de referencia (Datum).',
        'compare': '🆚 **Diferencia:** Controla tanto la orientación (ángulo 0) como la forma (planicidad) indirectamente.',
        'app': '🛤️ **Aplicación Real:** Rieles de trenes o guías lineales de máquinas CNC.',
        'why': '⚠️ **¿Por qué importa?** Si los rieles no son paralelos, el carro se amarrará o tendrá juego excesivo en ciertos puntos.'
    },
    'Concentricidad': {
        'symbol': '◎',
        'def': 'Controla que los puntos medios (medianos) de secciones opuestas del cilindro caigan dentro de una zona cilíndrica teórica.',
        'compare': '🆚 **Diferencia:** Es difícil de medir. A menudo se prefiere usar **Alabeo (Runout)** porque la concentricidad es teórica (balanceo), no de superficie.',
        'app': '⚖️ **Aplicación Real:** Ejes de alta velocidad que requieren balanceo dinámico.',
        'why': '⚠️ **¿Por qué importa?** Reduce la vibración por desbalanceo de masas.'
    },
    'Posición': {
        'symbol': '⌖',
        'def': 'Controla la ubicación exacta del centro de una característica (como un agujero) respecto a los Datums.',
        'compare': '🆚 **Diferencia:** Es la tolerancia más poderosa. Permite usar "Condición de Máximo Material" (bonus tolerance) para salvar piezas.',
        'app': '🔩 **Aplicación Real:** Patrones de agujeros para atornillar la tapa de una caja de cambios.',
        'why': '⚠️ **¿Por qué importa?** Garantiza la **Intercambiabilidad**. Asegura que los tornillos pasen por los agujeros y coincidan con la contraparte.'
    },
    'Alabeo Circular': {
        'symbol': '↗',
        'def': '(Runout). Controla la variación de la superficie en una sección circular específica mientras la pieza gira 360° sobre su eje Datum.',
        'compare': '🆚 **Diferencia:** Mide "corte por corte". Controla errores de redondez y concentricidad combinados en ese punto.',
        'app': '🛑 **Aplicación Real:** Discos de freno.',
        'why': '⚠️ **¿Por qué importa?** Si el disco tiene alabeo, el pedal del freno vibrará al frenar.'
    },
    'Alabeo Total': {
        'symbol': '⌰',
        'def': '(Total Runout). Controla toda la superficie cilíndrica simultáneamente mientras la pieza gira y el indicador se desplaza longitudinalmente.',
        'compare': '🆚 **Diferencia:** Es más estricto que el Circular. Controla conicidad, rectitud, redondez y concentricidad, todo a la vez.',
        'app': '💧 **Aplicación Real:** Ejes de bombas hidráulicas en la zona del sello mecánico.',
        'why': '⚠️ **¿Por qué importa?** Cualquier imperfección en toda la superficie causará fugas inmediatas en el sello.'
    },
    'Perfil de una línea': {
        'symbol': '⌒',
        'def': 'Controla la forma de una línea curva (2D) en cualquier sección transversal de la pieza.',
        'compare': '🆚 **Diferencia:** Solo aplica a la línea de corte, no a toda la superficie 3D.',
        'app': '✈️ **Aplicación Real:** El borde de ataque de un ala de avión (sección transversal).',
        'why': '⚠️ **¿Por qué importa?** Crítico para la aerodinámica en perfiles extruidos.'
    },
    'Perfil de una superficie': {
        'symbol': '⌓',
        'def': 'Controla la forma, orientación y ubicación de una superficie 3D compleja (curva).',
        'compare': '🆚 **Diferencia:** Crea una "piel" o zona de tolerancia tridimensional alrededor de la forma ideal.',
        'app': '🚗 **Aplicación Real:** El cofre (capó) de un auto o moldes de inyección de plástico.',
        'why': '⚠️ **¿Por qué importa?** Asegura que las piezas estéticas y complejas encajen visualmente y funcionalmente con la carrocería.'
    }
}

# Color de fondo agradable (Gris Ingeniería)
BG_COLOR = "#E3E3E3"

# ==========================================
# 1. MOTOR DE ESQUEMAS REALES (BLUEPRINTS)
# ==========================================

def create_base_blueprint(title):
    """Lienzo base para el plano técnico"""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=f"Esquema de Inspección: {title}", font=dict(size=20, color="black")),
        xaxis=dict(range=[-2, 12], showgrid=False, visible=False),
        yaxis=dict(range=[-1, 9], showgrid=False, visible=False),
        height=550,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="black"),
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center",
            buttons=[dict(label="▶️ REPRODUCIR INSPECCIÓN", method="animate", 
            args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True, mode='immediate')])]
        )]
    )
    return fig

def plot_real_inspection_anim(feature):
    fig = create_base_blueprint(feature.upper())
    frames = []
    
    # --- GRUPO 1: DESLIZAMIENTO HORIZONTAL ---
    if feature in ['Rectitud', 'Paralelismo', 'Planicidad', 'Perfil de una línea', 'Perfil de una superficie']:
        fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#cccccc", line=dict(color="black"))
        fig.add_annotation(x=5, y=-0.5, text="DATUM A (Mármol)", font=dict(color="black", size=14), showarrow=False)
        
        x_path = np.linspace(0, 10, 60)
        if feature == 'Rectitud' or feature == 'Planicidad':
            y_surf = 1.5 + 0.2 * np.sin(x_path * 1.5)
        elif 'Perfil' in feature:
            y_surf = 1.5 + 0.3 * np.sin(x_path) + 0.1 * np.cos(x_path*3)
        else: 
            y_surf = 1.5 + 0.1 * x_path 

        fig.add_trace(go.Scatter(x=x_path, y=y_surf, mode="lines", line=dict(color="blue", width=4), name="Pieza Real"))
        
        xi, yi = x_path[0], y_surf[0]; yc = yi + 3; dx=0.5; dy=0
        
        for i in range(len(x_path)):
            xi, yi = x_path[i], y_surf[i]; yc = yi + 3
            dx = 0.5 * np.cos(i*0.5); dy = 0.5 * np.sin(i*0.5)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="gray", width=4), name="Vástago")) 
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj")) 
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja")) 

    # --- GRUPO 2: ROTACIÓN ---
    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        fig.add_shape(type="rect", x0=-1, y0=1, x1=1, y1=5, fillcolor="#555", line=dict(color="black"))
        fig.add_annotation(x=0, y=5.5, text="Chuck", font=dict(color="black"), showarrow=False)
        fig.add_shape(type="rect", x0=1, y0=2, x1=9, y1=4, line=dict(color="blue", width=3))
        fig.add_annotation(x=5, y=3, text="Pieza Girando ↺", font=dict(size=18, color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0), showlegend=False)) 

        t = np.linspace(0, 4*np.pi, 60)
        x_pos = np.linspace(2, 8, 60) if feature in ['Cilindricidad', 'Alabeo Total'] else np.full(60, 5)
        xi_s = x_pos[0]; yi_s = 4; yc_s = yi_s + 2.5; dx_s = 0.5; dy_s = 0

        for i in range(len(t)):
            xi = x_pos[i]; yi = 4; yc = yi + 2.5
            dx = 0.5 * np.cos(t[i]); dy = 0.5 * np.sin(t[i])
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))

        fig.add_trace(go.Scatter(x=[xi_s, xi_s], y=[yi_s, yc_s], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi_s], y=[yc_s], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi_s, xi_s+dx_s], y=[yc_s, yc_s+dy_s], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 3: PERPENDICULARIDAD ---
    elif feature == 'Perpendicularidad':
        fig.add_shape(type="path", path="M 2,0 L 2,6 L 3,6 L 3,1 L 6,1 L 6,0 Z", fillcolor="lightgray", line=dict(color="black"))
        fig.add_annotation(x=4, y=0.5, text="Escuadra", font=dict(color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[7, 6.5], y=[0, 6], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        y_path = np.linspace(0.5, 5.5, 50); x_surf = np.linspace(7, 6.5, 50)
        yi_s = y_path[0]; xi_s = x_surf[0]; xc_s = xi_s - 2.5; dx_s = 0.5; dy_s = 0

        for i in range(len(y_path)):
            yi = y_path[i]; xi = x_surf[i]; xc = xi - 2.5
            dx = 0.5 * np.cos(i*0.2); dy = 0.5 * np.sin(i*0.2)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xc], y=[yi, yi]), go.Scatter(x=[xc], y=[yi]), go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi_s, xc_s], y=[yi_s, yi_s], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xc_s], y=[yi_s], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xc_s, xc_s+dx_s], y=[yi_s, yi_s+dy_s], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 4: ANGULARIDAD ---
    elif feature == 'Angularidad':
        fig.add_shape(type="path", path="M 1,0 L 9,3 L 9,0 Z", fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=5, y=1, text="Seno", font=dict(color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[1,9], y=[3.2, 6.2], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        x_path = np.linspace(1, 9, 50); y_path = np.linspace(3.2, 6.2, 50)
        xi_s = x_path[0]; yi_s = y_path[0]; yc_s = yi_s + 2.5; dx_s = 0.5; dy_s = 0

        for i in range(len(x_path)):
            xi = x_path[i]; yi = y_path[i]; yc = yi + 2.5
            dx = 0.5 * np.cos(i); dy = 0.5 * np.sin(i)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]), go.Scatter(x=[xi], y=[yc]), go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
            
        fig.add_trace(go.Scatter(x=[xi_s, xi_s], y=[yi_s, yc_s], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi_s], y=[yc_s], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi_s, xi_s+dx_s], y=[yc_s, yc_s+dy_s], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 5: POSICIÓN ---
    elif feature == 'Posición':
        fig.add_shape(type="rect", x0=2, y0=0, x1=8, y1=3, fillcolor="lightgray", line=dict(color="black"))
        fig.add_annotation(x=3, y=1.5, text="Pieza", font=dict(color="black"), showarrow=False)
        fig.add_shape(type="line", x0=4.5, y0=3, x1=4.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=6.5, y0=3, x1=6.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=4.5, y0=1, x1=6.5, y1=1, line=dict(color="black", width=2, dash="dot"))
        
        y_path = np.concatenate([np.linspace(6, 2, 30), np.linspace(2, 6, 30)])
        x_pos = 5.5; yi_s = y_path[0]
        
        for i in range(len(y_path)):
            yi = y_path[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4]), go.Scatter(x=[x_pos], y=[yi])
            ], traces=[1, 2]))
            
        fig.add_trace(go.Scatter(x=[x_pos, x_pos], y=[yi_s, yi_s+4], mode="lines", line=dict(color="red", width=3), name="Stylus"))
        fig.add_trace(go.Scatter(x=[x_pos], y=[yi_s], mode="markers", marker=dict(size=15, color="red"), name="Tip"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="lines", name="Dummy"))

    fig.frames = frames
    return fig

# ==========================================
# 2. SIMULACIONES 3D (TEÓRICAS)
# ==========================================
RESOLUTION = 30

def get_3d_layout(title):
    return dict(
        title=dict(text=title, font=dict(size=20, color='black')),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=BG_COLOR),
            yaxis=dict(visible=False, backgroundcolor=BG_COLOR),
            zaxis=dict(visible=True, backgroundcolor=BG_COLOR, gridcolor="#bbb", showbackground=True),
            bgcolor=BG_COLOR
        ),
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=BG_COLOR,
        font=dict(color="black"),
        legend=dict(bgcolor="rgba(255,255,255,0.6)", bordercolor="black", borderwidth=1, font=dict(color="black")),
        height=650, margin=dict(l=0, r=0, t=40, b=0)
    )

def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, RESOLUTION)
    theta = np.linspace(0, 2 * np.pi, 30)
    tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()

    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=np.sin(z/1.5)*0.2, y=np.cos(z/1.5)*0.15, z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona Tolerancia'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje Nominal'))

    elif feature == 'Planicidad':
        x = np.linspace(-5,5,RESOLUTION); y = np.linspace(-5,5,RESOLUTION); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Sup. Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Plano Sup.'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Plano Inf.'))

    elif feature == 'Redondez':
        r = 5 + 0.2 * np.cos(3*theta)
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='blue', width=6), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Límite Sup.'))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(theta), y=(5-tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash'), name='Límite Inf.'))

    elif feature == 'Cilindricidad' or feature == 'Alabeo Total':
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
        z_w = np.linspace(0, 8, 20); y_w = np.linspace(-3, 3, 20); Z, Y = np.meshgrid(z_w, y_w)
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

    fig.update_layout(**get_3d_layout(f"{feature} (Tol: {tol} mm)"))
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
view_mode = st.sidebar.radio("Seleccione una vista:", ["📐 Simulación 3D", "🏭 Plano de Montaje Real"])

st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- DESCRIPCIÓN ---
def_data = gdt_data.get(feat, {'symbol': '?', 'def': 'Sin definición.', 'compare': '', 'app': '', 'why': ''})

# CARD DE DEFINICIÓN
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
<br>
""", unsafe_allow_html=True)

if view_mode == "📐 Simulación 3D":
    st.markdown(f"<h3 style='text-align: center; color: black;'>Simulación 3D: {feat}</h3>", unsafe_allow_html=True)
    fig_3d = plot_3d_simulation(feat, tol)
    st.plotly_chart(fig_3d, use_container_width=True)

elif view_mode == "🏭 Plano de Montaje Real":
    st.markdown(f"<h3 style='text-align: center; color: black;'>Montaje Físico: {feat}</h3>", unsafe_allow_html=True)
    fig_real = plot_real_inspection_anim(feat)
    st.plotly_chart(fig_real, use_container_width=True)
    st.caption("ℹ️ Haga clic en el botón '▶️ REPRODUCIR INSPECCIÓN' dentro del gráfico.")
