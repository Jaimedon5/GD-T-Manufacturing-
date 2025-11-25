import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

st.markdown("""
<style>
    .block-container {padding-top: 3rem; padding-bottom: 0rem; padding-left: 2rem; padding-right: 2rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 0. DICCIONARIO DE DEFINICIONES
# ==========================================
definitions = {
    'Rectitud': "Es una condición en la que todos los puntos forman una línea recta. La tolerancia se especifica con la representación de dos líneas paralelas.",
    'Planicidad': "Todos los puntos en una superficie están en un plano. La tolerancia se especifica con dos planos paralelos.",
    'Redondez': "Todos los puntos de una superficie forman un círculo. La tolerancia se especifica con la definición de dos círculos concéntricos.",
    'Cilindricidad': "Todos los puntos de una superficie son equidistantes a un eje común. Una tolerancia cilíndrica especifica una zona de tolerancia definida por dos cilindros concéntricos.",
    'Angularidad': "Es la condición de una superficie o eje que forma un ángulo específico (aparte de 90°) con otro eje o plano. La zona de tolerancia está definida por dos planos paralelos al ángulo básico específico desde el eje o plano de un dato.",
    'Perpendicularidad': "Es la condición de una superficie o eje que forma un ángulo recto con otro plano o eje. La tolerancia especifica una zona definida por dos planos perpendiculares al dato.",
    'Paralelismo': "Es la condición de una superficie o eje equidistantes a todos los puntos desde el plano o eje del dato. La tolerancia especifica una zona definida por dos planos o líneas paralelas al dato.",
    'Concentricidad': "Los ejes de todos los elementos locales cruzados de una superficie de revolución son comunes a la característica del eje del dato. La tolerancia especifica una zona cilíndrica cuyo eje coincide con el dato.",
    'Posición': "Define una zona en la que el eje central o plano central puede variar desde la posición real (teóricamente exacta). Las dimensiones básicas establecen la posición real a partir de los datos.",
    'Alabeo Circular': "(Control Circular). Permite controlar los elementos circulares de una superficie. La tolerancia se aplica de manera independiente a cualquier posición circular de medición ya que la pieza se puede rotar 360°.",
    'Alabeo Total': "(Control Total). Ofrece control de todos los elementos de la superficie. La tolerancia se aplica de forma simultánea a elementos circulares y longitudinales ya que la pieza se rota 360°.",
    'Perfil de una línea': "Método para controlar superficies irregulares, líneas o arcos. La tolerancia especifica un límite uniforme a lo largo del perfil real dentro del que se deben situar los elementos de la línea.",
    'Perfil de una superficie': "Método para controlar superficies irregulares. La tolerancia especifica un límite uniforme (zona tridimensional) a lo largo del perfil real dentro del que se deben situar los elementos de la superficie."
}

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
        height=600,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor='#f4f4f4', # Gris tenue
        paper_bgcolor='#f4f4f4',
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.8)"),
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center",
            buttons=[dict(label="▶️ REPRODUCIR INSPECCIÓN", method="animate", 
            args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True, mode='immediate')])]
        )]
    )
    return fig

def plot_real_inspection_anim(feature):
    """Genera la animación del montaje real según el tipo de característica"""
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
        
        # Animación
        for i in range(len(x_path)):
            xi, yi = x_path[i], y_surf[i]
            yc = yi + 3
            dx = 0.5 * np.cos(i*0.5); dy = 0.5 * np.sin(i*0.5)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]),
                go.Scatter(x=[xi], y=[yc]),
                go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
            
        # Trazas iniciales
        xi, yi = x_path[0], y_surf[0]; yc = yi + 3; dx=0.5; dy=0
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="gray", width=4), name="Vástago")) 
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj")) 
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja")) 

    # --- GRUPO 2: ROTACIÓN ---
    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        fig.add_shape(type="rect", x0=-1, y0=1, x1=1, y1=5, fillcolor="#555", line=dict(color="black"))
        fig.add_annotation(x=0, y=5.5, text="Chuck", font=dict(color="black", size=14), showarrow=False)
        fig.add_shape(type="rect", x0=1, y0=2, x1=9, y1=4, line=dict(color="blue", width=3))
        fig.add_annotation(x=5, y=3, text="Pieza Girando ↺", font=dict(size=18, color="black"), showarrow=False)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0), showlegend=False)) # Fantasma

        t = np.linspace(0, 4*np.pi, 60)
        x_pos = np.linspace(2, 8, 60) if feature in ['Cilindricidad', 'Alabeo Total'] else np.full(60, 5)

        for i in range(len(t)):
            xi = x_pos[i]; yi = 4; yc = yi + 2.5
            dx = 0.5 * np.cos(t[i]); dy = 0.5 * np.sin(t[i])
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]),
                go.Scatter(x=[xi], y=[yc]),
                go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))

        xi = x_pos[0]; yi = 4; yc = yi + 2.5; dx=0.5; dy=0
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 3: PERPENDICULARIDAD ---
    elif feature == 'Perpendicularidad':
        fig.add_shape(type="path", path="M 2,0 L 2,6 L 3,6 L 3,1 L 6,1 L 6,0 Z", fillcolor="lightgray", line=dict(color="black"))
        fig.add_annotation(x=4, y=0.5, text="Escuadra Patrón", font=dict(color="black", size=14), showarrow=False)
        fig.add_trace(go.Scatter(x=[7, 6.5], y=[0, 6], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        y_path = np.linspace(0.5, 5.5, 50); x_surf = np.linspace(7, 6.5, 50)
        for i in range(len(y_path)):
            yi = y_path[i]; xi = x_surf[i]; xc = xi - 2.5
            dx = 0.5 * np.cos(i*0.2); dy = 0.5 * np.sin(i*0.2)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xc], y=[yi, yi]),
                go.Scatter(x=[xc], y=[yi]),
                go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy])
            ], traces=[1, 2, 3]))
        
        yi=y_path[0]; xi=x_surf[0]; xc=xi-2.5; dx=0.5; dy=0
        fig.add_trace(go.Scatter(x=[xi, xc], y=[yi, yi], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xc], y=[yi], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 4: ANGULARIDAD ---
    elif feature == 'Angularidad':
        fig.add_shape(type="path", path="M 1,0 L 9,3 L 9,0 Z", fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=5, y=1, text="Mesa de Senos", font=dict(color="black", size=14), showarrow=False)
        fig.add_trace(go.Scatter(x=[1,9], y=[3.2, 6.2], mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        x_path = np.linspace(1, 9, 50); y_path = np.linspace(3.2, 6.2, 50)
        for i in range(len(x_path)):
            xi = x_path[i]; yi = y_path[i]; yc = yi + 2.5
            dx = 0.5 * np.cos(i); dy = 0.5 * np.sin(i)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]),
                go.Scatter(x=[xi], y=[yc]),
                go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))
        
        xi=x_path[0]; yi=y_path[0]; yc=yi+2.5; dx=0.5; dy=0
        fig.add_trace(go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2), name="Aguja"))

    # --- GRUPO 5: POSICIÓN ---
    elif feature == 'Posición':
        fig.add_shape(type="rect", x0=2, y0=0, x1=8, y1=3, fillcolor="lightgray", line=dict(color="black"))
        fig.add_annotation(x=3, y=1.5, text="Pieza", font=dict(color="black", size=14), showarrow=False)
        fig.add_shape(type="line", x0=4.5, y0=3, x1=4.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=6.5, y0=3, x1=6.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=4.5, y0=1, x1=6.5, y1=1, line=dict(color="black", width=2, dash="dot"))
        
        y_path = np.concatenate([np.linspace(6, 2, 30), np.linspace(2, 6, 30)])
        x_pos = 5.5
        for i in range(len(y_path)):
            yi = y_path[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4]),
                go.Scatter(x=[x_pos], y=[yi])
            ], traces=[1, 2]))
            
        yi = y_path[0]
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", name="Dummy", showlegend=False))
        fig.add_trace(go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4], mode="lines", line=dict(color="red", width=3), name="Vástago"))
        fig.add_trace(go.Scatter(x=[x_pos], y=[yi], mode="markers", marker=dict(size=15, color="red"), name="Punta"))

    fig.frames = frames
    return fig

# ==========================================
# 2. SIMULACIONES 3D (TEÓRICAS)
# ==========================================
RESOLUTION = 30

def get_3d_layout(title):
    """Configuración de fondo GRIS TENUE para confort visual"""
    return dict(
        title=dict(text=title, font=dict(size=20, color='black')),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor="#f4f4f4"),
            yaxis=dict(visible=False, backgroundcolor="#f4f4f4"),
            zaxis=dict(visible=True, backgroundcolor="#f4f4f4", gridcolor="#ddd", showbackground=True),
            bgcolor="#f4f4f4"
        ),
        paper_bgcolor='#f4f4f4', # Fondo gris tenue
        plot_bgcolor='#f4f4f4',
        legend=dict(bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1), # Leyenda visible
        height=650, margin=dict(l=0, r=0, t=40, b=0)
    )

def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, RESOLUTION)
    theta = np.linspace(0, 2 * np.pi, 30)
    tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()

    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=np.sin(z/1.5)*0.2, y=np.cos(z/1.5)*0.15, z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real (Desviado)'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona Tolerancia'))
        fig.add_trace(go.Scatter3d(x=np.zeros_like(z), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje Nominal'))
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
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), name='Tolerancia', showlegend=True))
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
        fig.add_trace(go.Scatter3d(x=cx.flatten(), y=cy.flatten(), z=z.repeat(30), mode='lines', line=dict(color='red', width=5), name='Eje Real Derivado'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.4, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Zona Tol'))
    elif feature == 'Alabeo Circular':
        fig.add_trace(go.Scatter3d(x=5.3*np.cos(theta)+0.2, y=5.3*np.sin(theta), z=np.zeros_like(theta), line=dict(color='purple', width=6), name='Trayectoria Medida'))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot'), name='Límites Tolerancia'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,2], mode='lines', line=dict(color='black', width=5, dash='longdash'), name='Eje Datum'))
    elif feature == 'Perfil de una línea':
        x_v = np.linspace(0,10,50); z_n = 2*np.sin(x_v)
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+0.1*np.random.normal(0,1,x_v.shape), line=dict(color='blue', width=6), name='Perfil Real'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+tol/2, line=dict(color='green', width=5, dash='dash'), name='Límite Sup'))
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n-tol/2, line=dict(color='green', width=5, dash='dash'), name='Límite Inf'))
    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3,3,30); y = np.linspace(-3,3,30); xg, yg = np.meshgrid(x,y); zg = 0.5*(xg**2+yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9, name='Sup. Nominal'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Límite Sup'))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']], name='Límite Inf'))

    fig.update_layout(**get_3d_layout(f"{feature} (Tol: {tol} mm)"))
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

# --- SELECTOR DE VISTA EN SIDEBAR ---
st.sidebar.markdown("### 👁️ Vista")
view_mode = st.sidebar.radio(
    "Seleccione una vista:",
    ["📐 Simulación 3D", "🏭 Plano de Montaje Real"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- LÓGICA DE VISUALIZACIÓN ---

description_text = definitions.get(feat, "Definición técnica estándar de GD&T.")
st.info(f"**📖 Definición de {feat}:** {description_text}")

if view_mode == "📐 Simulación 3D":
    st.subheader(f"Simulación 3D: {feat}")
    fig_3d = plot_3d_simulation(feat, tol)
    st.plotly_chart(fig_3d, use_container_width=True)

elif view_mode == "🏭 Plano de Montaje Real":
    st.subheader(f"Montaje Físico: {feat}")
    fig_real = plot_real_inspection_anim(feat)
    st.plotly_chart(fig_real, use_container_width=True)
    st.caption("ℹ️ Instrucción: Haga clic en el botón '▶️ REPRODUCIR INSPECCIÓN' (dentro del gráfico) para ver la animación.")
