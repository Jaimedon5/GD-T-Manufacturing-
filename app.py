import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# Estilos CSS
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem; padding-left: 1rem; padding-right: 1rem;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. MOTOR DE ESQUEMAS REALES (BLUEPRINTS)
# ==========================================

def create_base_blueprint(title):
    """Lienzo base para el plano técnico"""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=f"Esquema de Inspección: {title}", font=dict(size=20)),
        xaxis=dict(range=[-2, 12], showgrid=False, visible=False),
        yaxis=dict(range=[-2, 8], showgrid=False, visible=False),
        height=600,
        plot_bgcolor='white',
        updatemenus=[dict(
            type="buttons", showactive=False, x=0.05, y=0, xanchor="left", yanchor="top",
            buttons=[dict(label="▶️ Iniciar Inspección", method="animate", 
            args=[None, dict(frame=dict(duration=40, redraw=True), fromcurrent=True, mode='immediate')])]
        )]
    )
    return fig

def plot_real_inspection_anim(feature):
    """Genera la animación del montaje real según el tipo de característica"""
    
    fig = create_base_blueprint(feature.upper())
    frames = []
    
    # --- GRUPO 1: DESLIZAMIENTO HORIZONTAL (Mármol + Reloj) ---
    # Aplica a: Rectitud, Paralelismo, Planicidad, Perfiles
    if feature in ['Rectitud', 'Paralelismo', 'Planicidad', 'Perfil de una línea', 'Perfil de una superficie']:
        # Mármol
        fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#e0e0e0", line=dict(color="black"))
        fig.add_annotation(x=5, y=-0.5, text="DATUM A (Mármol)", showarrow=False)
        
        # Pieza
        x_path = np.linspace(0, 10, 60)
        if feature == 'Rectitud' or feature == 'Planicidad':
            y_surf = 1.5 + 0.2 * np.sin(x_path * 1.5)
        elif 'Perfil' in feature:
            y_surf = 1.5 + 0.3 * np.sin(x_path) + 0.1 * np.cos(x_path*3)
        else: # Paralelismo
            y_surf = 1.5 + 0.1 * x_path 

        fig.add_trace(go.Scatter(x=x_path, y=y_surf, mode="lines", line=dict(color="blue", width=4), name="Pieza"))
        
        # Animación Reloj
        for i in range(len(x_path)):
            xi, yi = x_path[i], y_surf[i]
            yc = yi + 3
            dx = 0.5 * np.cos(i*0.5); dy = 0.5 * np.sin(i*0.5)
            
            frames.append(go.Frame(data=[
                go.Scatter(x=[xi, xi], y=[yi, yc], mode="lines", line=dict(color="gray", width=4)), # Vástago
                go.Scatter(x=[xi], y=[yc], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2))), # Cuerpo
                go.Scatter(x=[xi, xi+dx], y=[yc, yc+dy], mode="lines", line=dict(color="red", width=2)) # Aguja
            ]))
            
        # Trazas iniciales (Placeholders)
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="gray", width=4), name="Vástago")) 
        fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj")) 
        fig.add_trace(go.Scatter(x=[0,0], y=[0,0], mode="lines", line=dict(color="red", width=2), name="Aguja")) 

    # --- GRUPO 2: ROTACIÓN (Chuck + Reloj) ---
