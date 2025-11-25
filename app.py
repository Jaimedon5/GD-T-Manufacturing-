import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. MOTOR DE BLUEPRINTS (CORREGIDO)
# ==========================================

def create_base_blueprint(title):
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=f"Esquema Técnico: {title}", font=dict(size=20)),
        xaxis=dict(range=[-2, 12], showgrid=False, visible=False),
        yaxis=dict(range=[-2, 8], showgrid=False, visible=False),
        height=650,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='#f4f4f4', # Gris muy suave para descanso visual
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
    
    # --- GRUPO 1: DESLIZAMIENTO HORIZONTAL (Rectitud, etc.) ---
    if feature in ['Rectitud', 'Paralelismo', 'Planicidad', 'Perfil de una línea', 'Perfil de una superficie']:
        # 1. ELEMENTOS ESTÁTICOS (No se mueven)
        # Mármol (Datum)
        fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#666", line=dict(color="black"))
        fig.add_annotation(x=5, y=-0.5, text="DATUM A (Mármol)", font=dict(color="white"), showarrow=False)
        
        # Pieza (LÍNEA GRUESA Y VISIBLE) - TRACE 0
        x_path = np.linspace(0, 10, 60)
        y_surf = 1.5 + 0.2 * np.sin(x_path * 1.5) if 'Perfil' not in feature else 1.5 + 0.3*np.sin(x_path)
        
        fig.add_trace(go.Scatter(x=x_path, y=y_surf, mode="lines", line=dict(color="black", width=6), name="Pieza"))
        
        # 2. ELEMENTOS MÓVILES (Inicialización) - TRACES 1, 2, 3
        # Vástago Inicial
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        # Reloj Inicial
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        # Aguja Inicial
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=2), name="Aguja"))

        # 3. ANIMACIÓN
        for i in range(len(x_path)):
            xi, yi = x_path[i], y_surf[i]
            yc = yi + 3 # Centro del reloj
            
            # Simulación aguja
            angle = (yi - 1.5) * 5 # Amplificar movimiento
            dx = 0.5 * np.cos(angle); dy = 0.5 * np.sin(angle)
            
            frames.append(go.Frame(
                data=[
                    # Actualizamos SOLO los traces móviles (1, 2, 3)
                    go.Scatter(x=[xi, xi], y=[yi, yc]), # Trace 1: Vástago
                    go.Scatter(x=[xi], y=[yc]),         # Trace 2: Reloj
                    go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy]) # Trace 3: Aguja
                ],
                traces=[1, 2, 3] # ¡CRUCIAL! Decimos a Plotly que solo toque estos traces
            ))

    # --- GRUPO 2: ROTACIÓN (Redondez, etc.) ---
    elif feature in ['Redondez', 'Cilindricidad', 'Alabeo Circular', 'Alabeo Total', 'Concentricidad']:
        # Estáticos
        fig.add_shape(type="rect", x0=-1, y0=1, x1=1, y1=5, fillcolor="#333", line=dict(color="black")) # Chuck
        fig.add_annotation(x=0, y=5.5, text="Chuck", showarrow=False)
        # Pieza (Rectángulo giratorio simulado)
        fig.add_shape(type="rect", x0=1, y0=2, x1=9, y1=4, line=dict(color="black", width=3))
        fig.add_annotation(x=5, y=3, text="Pieza Girando ↺", showarrow=False, font=dict(size=20))
        
        # Trace Fantasma (Para mantener índice 0 ocupado y no romper lógica)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0), showlegend=False))

        # Móviles Iniciales (Traces 1, 2, 3)
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers+text", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=2), name="Aguja"))

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

    # --- GRUPO 3: PERPENDICULARIDAD ---
    elif feature == 'Perpendicularidad':
        # Estáticos
        fig.add_shape(type="path", path="M 2,0 L 2,6 L 3,6 L 3,1 L 6,1 L 6,0 Z", fillcolor="#aaa", line=dict(color="black")) # Escuadra
        fig.add_annotation(x=4, y=0.5, text="Escuadra Patrón", showarrow=False)
        # Pieza (Trace 0)
        fig.add_trace(go.Scatter(x=[7, 6.5], y=[0, 6], mode="lines", line=dict(color="black", width=6), name="Pieza"))
        
        # Móviles Iniciales
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="gray", width=4), name="Vástago"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", name="Reloj"))
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=2), name="Aguja"))

        y_path = np.linspace(0.5, 5.5, 50); x_surf = np.linspace(7, 6.5, 50)
        for i in range(len(y_path)):
            yi = y_path[i]; xi = x_surf[i]; xc = xi - 2.5
            dx = 0.5 * np.cos(i*0.2); dy = 0.5 * np.sin(i*0.2)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xc], y=[yi, yi]),
                go.Scatter(x=[xc], y=[yi]),
                go.Scatter(x=[xc, xc+dx], y=[yi, yi+dy])
            ], traces=[1, 2, 3]))

    # --- GRUPO 4: ANGULARIDAD ---
    elif feature == 'Angularidad':
        fig.add_shape(type="path", path="M 1,0 L 9,3 L 9,0 Z", fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=5, y=1, text="Mesa de Senos", showarrow=False)
        # Pieza (Trace 0)
        fig.add_trace(go.Scatter(x=[1,9], y=[3.2, 6.2], mode="lines", line=dict(color="black", width=6), name="Pieza"))
        
        # Móviles
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="gray", width=4)))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", name="Reloj"))
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=2)))

        x_path = np.linspace(1, 9, 50); y_path = np.linspace(3.2, 6.2, 50)
        for i in range(len(x_path)):
            xi = x_path[i]; yi = y_path[i]; yc = yi + 2.5
            dx = 0.5 * np.cos(i); dy = 0.5 * np.sin(i)
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc]),
                go.Scatter(x=[xi], y=[yc]),
                go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy])
            ], traces=[1, 2, 3]))

    # --- GRUPO 5: POSICIÓN ---
    elif feature == 'Posición':
        fig.add_shape(type="rect", x0=2, y0=0, x1=8, y1=3, fillcolor="#ddd", line=dict(color="black"))
        fig.add_annotation(x=3, y=1.5, text="Pieza", showarrow=False)
        fig.add_shape(type="line", x0=4.5, y0=3, x1=4.5, y1=1, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=6.5, y0=3, x1=6.5, y1=1, line=dict(color="black", width=2))
        
        # Trace Fantasma (0)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(opacity=0)))
        
        # Móviles (1, 2)
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=3), name="Vástago"))
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=15, color="red"), name="Punta"))

        y_path = np.concatenate([np.linspace(6, 2, 30), np.linspace(2, 6, 30)])
        x_pos = 5.5
        for i in range(len(y_path)):
            yi = y_path[i]
            frames.append(go.Frame(data=[
                go.Scatter(x=[x_pos, x_pos], y=[yi, yi+4]),
                go.Scatter(x=[x_pos], y=[yi])
            ], traces=[1, 2]))

    fig.frames = frames
    return fig

# ==========================================
# 2. SIMULACIONES 3D (TEÓRICAS)
# ==========================================
RESOLUTION = 30
def get_3d_layout(title):
    return dict(
        title=dict(text=title, font=dict(size=20)),
        scene=dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6), camera=dict(eye=dict(x=1.4, y=1.4, z=0.5))),
        height=650, margin=dict(l=0, r=0, t=40, b=0)
    )

def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, RESOLUTION); theta = np.linspace(0, 2 * np.pi, 30)
    tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()

    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=np.sin(z/1.5)*0.2, y=np.cos(z/1.5)*0.15, z=z, mode='lines', line=dict(color='blue', width=10), name='Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.2, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']]))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,RESOLUTION); y = np.linspace(-5,5,RESOLUTION); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.1, showscale=False, colorscale=[[0,'red'],[1,'red']]))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.1, showscale=False, colorscale=[[0,'red'],[1,'red']]))
    elif feature == 'Redondez':
        r = 5 + 0.2 * np.cos(3*theta)
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='blue', width=6)))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(theta), y=(5-tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash')))
    elif feature == 'Cilindricidad' or feature == 'Alabeo Total':
        fig.add_trace(go.Surface(x=(5+0.2*np.sin(zg*np.pi/5))*np.cos(tg), y=(5+0.2*np.sin(zg*np.pi/5))*np.sin(tg), z=zg, colorscale='Spectral'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red')))
    elif feature == 'Angularidad':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20)); z_nom = x * np.tan(np.radians(45))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom + 0.1*np.sin(y), colorscale='Plasma'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol/2, opacity=0.1, showscale=False, colorscale=[[0,'green'],[1,'green']]))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol/2, opacity=0.1, showscale=False, colorscale=[[0,'green'],[1,'green']]))
    elif feature == 'Perpendicularidad':
        z_w = np.linspace(0,8,20); y_w = np.linspace(-3,3,20); Z, Y = np.meshgrid(z_w, y_w)
        fig.add_trace(go.Surface(x=np.linspace(-3,3,20), y=Y, z=np.zeros_like(Y), opacity=0.5, showscale=False))
        fig.add_trace(go.Surface(x=0.2*(Z/8), y=Y, z=Z, colorscale='Jet'))
        fig.add_trace(go.Surface(x=np.full_like(Z, tol/2), y=Y, z=Z, opacity=0.1, showscale=False))
        fig.add_trace(go.Surface(x=np.full_like(Z, -tol/2), y=Y, z=Z, opacity=0.1, showscale=False))
    elif feature == 'Paralelismo':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        fig.add_trace(go.Surface(x=x, y=y, z=5+0.05*x, colorscale='Magma'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5+tol/2), opacity=0.1, showscale=False))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5-tol/2), opacity=0.1, showscale=False))
    elif feature == 'Posición':
        z_c = np.linspace(0,4,20); TH, Z = np.meshgrid(theta, z_c)
        fig.add_trace(go.Surface(x=0.5*np.cos(TH)+0.1, y=0.5*np.sin(TH)+0.1, z=Z, colorscale='Ice', showscale=False))
        fig.add_trace(go.Scatter3d(x=[0.1,0.1], y=[0.1,0.1], z=[0,4], line=dict(color='red', width=5)))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,4], line=dict(color='black', dash='dash')))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.2, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']]))
    elif feature == 'Concentricidad':
        cx = (0.05 * np.sin(z))[:, np.newaxis]; cy = (0.05 * np.cos(z))[:, np.newaxis]
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, showscale=False, colorscale=[[0,'gray'],[1,'gray']]))
        fig.add_trace(go.Surface(x=cx+2*np.cos(tg), y=cy+2*np.sin(tg), z=zg, colorscale='Cividis'))
        fig.add_trace(go.Scatter3d(x=cx.flatten(), y=cy.flatten(), z=z.repeat(30), mode='lines', line=dict(color='red', width=5)))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']]))
    elif feature == 'Alabeo Circular':
        fig.add_trace(go.Scatter3d(x=5.3*np.cos(theta)+0.2, y=5.3*np.sin(theta), z=np.zeros_like(theta), line=dict(color='purple', width=6)))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot')))
    elif feature == 'Perfil de una línea':
        x_v = np.linspace(0,10,50); z_n = 2*np.sin(x_v)
        fig.add_trace(go.Scatter3d(x=x_v, y=np.zeros_like(x_v), z=z_n+0.1*np.random.normal(0,1,x_v.shape), line=dict(color='blue', width=5)))
        xb = np.concatenate([x_v, x_v[::-1]]); zb = np.concatenate([z_n+tol/2, (z_n-tol/2)[::-1]])
        fig.add_trace(go.Mesh3d(x=xb, y=np.zeros_like(xb), z=zb, color='green', opacity=0.3))
    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3,3,30); y = np.linspace(-3,3,30); xg, yg = np.meshgrid(x,y); zg = 0.5*(xg**2+yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']]))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']]))

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

# --- SELECTOR DE VISTA EN SIDEBAR (MÁS ROBUSTO) ---
st.sidebar.markdown("### 👁️ Vista")
view_mode = st.sidebar.radio(
    "Seleccione una vista:",
    ["📐 Simulación 3D", "🏭 Plano de Montaje Real"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- LÓGICA DE VISUALIZACIÓN ---
if view_mode == "📐 Simulación 3D":
    st.subheader(f"Simulación 3D: {feat}")
    fig_3d = plot_3d_simulation(feat, tol)
    st.plotly_chart(fig_3d, use_container_width=True)

elif view_mode == "🏭 Plano de Montaje Real":
    st.subheader(f"Montaje Físico: {feat}")
    fig_real = plot_real_inspection_anim(feat)
    st.plotly_chart(fig_real, use_container_width=True)
    st.info("ℹ️ Instrucción: Haga clic en el botón '▶️ REPRODUCIR ANIMACIÓN' debajo del título para ver la inspección.")
