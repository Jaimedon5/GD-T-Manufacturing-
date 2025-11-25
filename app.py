import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA (Pantalla Completa Real) ---
st.set_page_config(layout="wide", page_title="Simulador GD&T - Ing. Jaime Silva")

# Ocultar elementos de Streamlit para que parezca una app profesional
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .block-container {padding-top: 1rem; padding-bottom: 0rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- FUNCIONES MATEMÁTICAS (Tu lógica GD&T) ---
RESOLUTION = 35

def get_common_layout(title, tolerance):
    return dict(
        title=dict(text=title, font=dict(size=24), x=0.05, y=0.95),
        scene=dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.5)),
            xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=True)
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=750  # Altura fija alta
    )

def plot_figure(category, feature, tol):
    z = np.linspace(0, 10, RESOLUTION)
    theta = np.linspace(0, 2 * np.pi, 30)
    tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    if feature == 'Rectitud':
        x_real = np.sin(z/1.5)*0.2; y_real = np.cos(z/1.5)*0.15
        fig.add_trace(go.Scatter3d(x=x_real, y=y_real, z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.2, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']], name='Tol'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', dash='dash'), name='Nominal'))

    elif feature == 'Planicidad':
        x = np.linspace(-5, 5, RESOLUTION); y = np.linspace(-5, 5, RESOLUTION)
        xg, yg = np.meshgrid(x, y)
        zg_real = 0.15 * np.sin(xg/2) * np.cos(yg/2)
        fig.add_trace(go.Surface(z=zg_real, x=xg, y=yg, colorscale='Viridis'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.1, showscale=False, colorscale=[[0,'red'],[1,'red']]))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.1, showscale=False, colorscale=[[0,'red'],[1,'red']]))

    elif feature == 'Redondez':
        r = 5 + 0.2 * np.cos(3*theta)
        fig.add_trace(go.Scatter3d(x=r*np.cos(theta), y=r*np.sin(theta), z=np.zeros_like(theta), mode='lines', line=dict(color='blue', width=6)))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter3d(x=(5-tol/2)*np.cos(theta), y=(5-tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dash')))

    elif feature == 'Cilindricidad' or feature == 'Alabeo Total':
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(theta), y=(5+tol/2)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red'), showlegend=False))
    
    elif feature == 'Angularidad':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        z_nom = x * np.tan(np.radians(45))
        fig.add_trace(go.Surface(x=x, y=y, z=np.zeros_like(x), opacity=0.5, showscale=False))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom + 0.1*np.sin(y), colorscale='Plasma'))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom+tol/2, opacity=0.1, showscale=False, colorscale=[[0,'green'],[1,'green']]))
        fig.add_trace(go.Surface(x=x, y=y, z=z_nom-tol/2, opacity=0.1, showscale=False, colorscale=[[0,'green'],[1,'green']]))

    elif feature == 'Perpendicularidad':
        z_wall = np.linspace(0, 8, 20); y_wall = np.linspace(-3, 3, 20)
        Z, Y = np.meshgrid(z_wall, y_wall)
        X = 0.2 * (Z/8)
        fig.add_trace(go.Surface(x=np.linspace(-3,3,20), y=Y, z=np.zeros_like(Y), opacity=0.5, showscale=False))
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Jet'))
        fig.add_trace(go.Surface(x=np.full_like(Z, tol/2), y=Y, z=Z, opacity=0.1, showscale=False))
        fig.add_trace(go.Surface(x=np.full_like(Z, -tol/2), y=Y, z=Z, opacity=0.1, showscale=False))

    elif feature == 'Paralelismo':
        x, y = np.meshgrid(np.linspace(0,10,20), np.linspace(0,10,20))
        fig.add_trace(go.Surface(x=x, y=y, z=np.zeros_like(x), opacity=0.5, showscale=False))
        fig.add_trace(go.Surface(x=x, y=y, z=5+0.05*x, colorscale='Magma'))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5+tol/2), opacity=0.1, showscale=False))
        fig.add_trace(go.Surface(x=x, y=y, z=np.full_like(x, 5-tol/2), opacity=0.1, showscale=False))

    elif feature == 'Posición':
        z_cyl = np.linspace(0, 4, 20); TH, Z = np.meshgrid(theta, z_cyl)
        X = 0.5 * np.cos(TH) + 0.1; Y = 0.5 * np.sin(TH) + 0.1
        fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Ice', showscale=False))
        fig.add_trace(go.Scatter3d(x=[0.1, 0.1], y=[0.1, 0.1], z=[0,4], line=dict(color='red', width=5)))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,4], line=dict(color='black', dash='dash')))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(TH), y=(tol/2)*np.sin(TH), z=Z, opacity=0.2, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']]))

    elif feature == 'Concentricidad':
        cx = (0.05 * np.sin(z))[:, np.newaxis]; cy = (0.05 * np.cos(z))[:, np.newaxis]
        fig.add_trace(go.Surface(x=4*np.cos(tg), y=4*np.sin(tg), z=zg, opacity=0.1, showscale=False, colorscale=[[0,'gray'],[1,'gray']]))
        fig.add_trace(go.Surface(x=cx+2*np.cos(tg), y=cy+2*np.sin(tg), z=zg, colorscale='Cividis'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'yellow'],[1,'yellow']]))

    elif feature == 'Alabeo Circular':
        x = 5.3 * np.cos(theta) + 0.2; y = 5.3 * np.sin(theta)
        fig.add_trace(go.Scatter3d(x=x, y=y, z=np.zeros_like(theta), line=dict(color='purple', width=6)))
        fig.add_trace(go.Scatter3d(x=(5+tol)*np.cos(theta), y=(5+tol)*np.sin(theta), z=np.zeros_like(theta), line=dict(color='red', dash='dot')))
        fig.add_trace(go.Scatter3d(x=np.zeros(2), y=np.zeros(2), z=[0, 2], line=dict(color='black', width=5)))

    elif feature == 'Perfil de una línea':
        x_vals = np.linspace(0, 10, 50); z_nom = 2 * np.sin(x_vals)
        fig.add_trace(go.Scatter3d(x=x_vals, y=np.zeros_like(x_vals), z=z_nom + 0.1*np.random.normal(0,1,x_vals.shape), line=dict(color='blue', width=5)))
        xb = np.concatenate([x_vals, x_vals[::-1]])
        zb = np.concatenate([z_nom+tol/2, (z_nom-tol/2)[::-1]])
        fig.add_trace(go.Mesh3d(x=xb, y=np.zeros_like(xb), z=zb, color='green', opacity=0.3))

    elif feature == 'Perfil de una superficie':
        x = np.linspace(-3, 3, 30); y = np.linspace(-3, 3, 30); xg, yg = np.meshgrid(x, y)
        zg = 0.5 * (xg**2 + yg**2)
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg, opacity=0.9))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg+tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']]))
        fig.add_trace(go.Surface(x=xg, y=yg, z=zg-tol/2, opacity=0.2, showscale=False, colorscale=[[0,'blue'],[1,'blue']]))

    fig.update_layout(**get_common_layout(f"{feature} (Tol: {tol} mm)", tol))
    return fig

# --- INTERFAZ LATERAL (SIDEBAR) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103650.png", width=50)
st.sidebar.title("Controles GD&T")
st.sidebar.markdown("---")

# Menús
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

st.sidebar.markdown("---")
st.sidebar.info("Desarrollado para Ingeniería de Manufactura")

# --- ÁREA PRINCIPAL (GRÁFICO) ---
fig = plot_figure(cat, feat, tol)
st.plotly_chart(fig, use_container_width=True)
