import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL CLARO)
# ==========================================
MAIN_BG = "#F0F2F6"
SIDEBAR_BG = "#1E1E1E"
TEXT_COLOR = "#000000"
ACCENT_COLOR = "#0d6efd"

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    /* Tarjeta de Definición */
    .gdt-card {{
        background-color: #FFFFFF;
        border-left: 8px solid {ACCENT_COLOR};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: {TEXT_COLOR};
        margin-bottom: 20px;
    }}
    
    /* Caja de Interpretación Azul */
    .interpretation-box {{
        background-color: #e8f4f8;
        border-left: 6px solid #0d6efd;
        padding: 20px;
        border-radius: 5px;
        margin-top: 10px;
        font-family: sans-serif;
        color: #000000;
    }}
    
    .tech-text {{ font-family: 'Courier New', monospace; font-weight: bold; }}
    h1, h2, h3 {{ color: #000000 !important; }}
    
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS UNIFICADA
# ==========================================
gdt_data = {
    # Superficie (Flecha a superficie)
    'Rectitud': {'sym': '⏤', 'type': 'surf', 'datum': False, 'desc': 'rectitud de la línea', 'zone': 'dos líneas paralelas'},
    'Planicidad': {'sym': '⏥', 'type': 'surf', 'datum': False, 'desc': 'planicidad de la superficie', 'zone': 'dos planos paralelos'},
    'Perfil de una línea': {'sym': '⌒', 'type': 'surf', 'datum': False, 'desc': 'forma del perfil 2D', 'zone': 'una banda uniforme'},
    'Perfil de una superficie': {'sym': '⌓', 'type': 'surf', 'datum': False, 'desc': 'forma de la superficie 3D', 'zone': 'dos superficies envolventes'},
    'Angularidad': {'sym': '∠', 'type': 'surf', 'datum': 'A', 'desc': 'inclinación exacta', 'zone': 'dos planos paralelos inclinados'},
    'Perpendicularidad': {'sym': '⟂', 'type': 'surf', 'datum': 'A', 'desc': 'perpendicularidad (90°)', 'zone': 'dos planos paralelos a 90°'},
    'Paralelismo': {'sym': '∥', 'type': 'surf', 'datum': 'A', 'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum'},

    # Eje / Centro (Flecha a cota)
    'Cilindricidad': {'sym': '⌭', 'type': 'axis', 'datum': False, 'desc': 'forma cilíndrica total', 'zone': 'dos cilindros concéntricos'},
    'Redondez': {'sym': '○', 'type': 'axis', 'datum': False, 'desc': 'circularidad (sección)', 'zone': 'dos círculos concéntricos'},
    'Posición': {'sym': '⌖', 'type': 'axis', 'datum': 'A B', 'desc': 'ubicación exacta del centro', 'zone': 'un cilindro en posición teórica'},
    'Concentricidad': {'sym': '◎', 'type': 'axis', 'datum': 'A', 'desc': 'coaxialidad de ejes', 'zone': 'un cilindro coaxial al Datum'},
    'Alabeo Circular': {'sym': '↗', 'type': 'axis', 'datum': 'A-B', 'desc': 'variación circular al girar', 'zone': 'distancia radial (sección)'},
    'Alabeo Total': {'sym': '⌰', 'type': 'axis', 'datum': 'A-B', 'desc': 'variación total al girar', 'zone': 'distancia radial (total)'}
}

# ==========================================
# 2. FUNCIONES DE DIBUJO (COMMON)
# ==========================================
def get_common_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG,
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    if is_3d:
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.5)),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc", showbackground=True)
        )
    else:
        layout['xaxis'] = dict(visible=False, showgrid=False)
        layout['yaxis'] = dict(visible=False, showgrid=False)
        layout['plot_bgcolor'] = 'white' # Papel blanco para 2D
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
    return layout

# ==========================================
# VISTA 1: SIMULACIÓN 3D
# ==========================================
def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    
    # Lógica Simplificada para demostración (Cubre todas las geometrías básicas)
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, showscale=False, colorscale=[[0,'orange'],[1,'orange']], name='Zona'))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Lim'))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, showscale=False, colorscale=[[0,'red'],[1,'red']], name='Lim'))
    else:
        # Cilindro Genérico para las demás
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje'))
    
    fig.update_layout(**get_common_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ANIMADO)
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_common_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ REPRODUCIR", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    # Montaje Genérico (Mesa + Pieza + Reloj)
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#ccc", line=dict(color="black"))
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
    # Frames básicos de animación
    frames = []
    for i in range(50):
        x = i/5; y = 1.5+0.2*np.sin(x)
        frames.append(go.Frame(data=[
            go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50))), # Pieza
            go.Scatter(x=[x, x], y=[y, y+3], mode="lines", line=dict(color="#444", width=4)), # Vástago
            go.Scatter(x=[x], y=[y+3], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2))), # Reloj
            go.Scatter(x=[x, x+0.5*np.cos(i)], y=[y+3, y+3+0.5*np.sin(i)], mode="lines", line=dict(color="red", width=2)) # Aguja
        ]))
    
    # Estado inicial
    fig.add_trace(go.Scatter(x=[0,0], y=[1.5, 4.5], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
    fig.add_trace(go.Scatter(x=[0], y=[4.5], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
    fig.add_trace(go.Scatter(x=[0,0.5], y=[4.5, 4.5], mode="lines", line=dict(color="red", width=2), name="Aguja"))
    
    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO DE INTERPRETACIÓN (ESTÁTICO)
# ==========================================
def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    if fill: fig.add_trace(go.Scatter(x=x, y=y, fill="toself", fillcolor=fill, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))
    else: fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))

def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data[feature]
    ftype = info['type']
    sym = info['sym']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', margin=dict(l=20, r=20, t=20, b=20), height=500, shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))])
    
    # --- PIEZA (EJE) ---
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) # Cuerpo
    fig.add_trace(go.Scatter(x=[1, 11], y=[4, 4], mode='lines', line=dict(color='black', width=1, dash='longdashdot'), showlegend=False)) # Centro

    # --- COTA DE TAMAÑO (CORREGIDA: TEXTO ARRIBA) ---
    # Líneas de extensión
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[6, 6], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[2, 2], mode='lines', line=dict(color='black', width=1), showlegend=False))
    # Flechas
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.5, arrowhead=2, arrowwidth=1, arrowcolor="black")
    # TEXTO (Mover a Y=5 para que no corte la línea de centro Y=4)
    fig.add_annotation(x=10.25, y=5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    # --- DATUM (Si aplica) ---
    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # --- MARCO DE CONTROL ---
    if ftype == 'surf':
        leader_x, leader_y = 6, 6; frame_x, frame_y = 6, 7.5 # Apunta superficie
    else:
        leader_x, leader_y = 10.25, 4.8; frame_x, frame_y = 10.25, 1.5 # Apunta cota (ajustado)

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
# ¡AQUÍ ESTÁN LAS 3 OPCIONES!
view_mode = st.sidebar.radio("Seleccione una vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Interpretación de Plano"], index=0)

st.sidebar.markdown("---")
st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- RENDERIZADO ---
info = gdt_data[feat]

st.markdown(f"""
<div class="gdt-card">
    <div style="display: flex; align-items: center;">
        <div class="big-icon" style="flex: 1;">{info['sym']}</div>
        <div style="flex: 4; padding-left: 20px;">
            <h3 style="margin:0; color: #0d6efd;">{feat}</h3>
            <p><strong>Definición:</strong> {info['def']}</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if view_mode == "📐 Simulación 3D":
    st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
    st.caption(f"🔍 Visualización 3D de la zona de tolerancia.")

elif view_mode == "🏭 Montaje Real":
    st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)
    st.caption("ℹ️ Haga clic en '▶️ REPRODUCIR' para ver la animación del palpador.")

elif view_mode == "📝 Interpretación de Plano":
    st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
    tol_str = f"Ø {tol} mm" if info['type'] == 'axis' else f"{tol} mm"
    st.markdown(f"""
    <div class="interpretation-box">
        <h4>🤓 Interpretación del Plano:</h4>
        <p style="font-size: 1.1em;">
            "Esta característica de <span class="tech-text" style="color: #d63384;">{feat.upper()}</span> 
            tiene una tolerancia de <b>{tol_str}</b>."
        </p>
        <ul>
            <li><b>Controla:</b> {info['desc'].capitalize()}.</li>
            <li><b>Zona de Tolerancia:</b> {info['zone'].capitalize()}.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
