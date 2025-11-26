import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL ESTABLE)
# ==========================================
MAIN_BG = "#F0F2F6"
SIDEBAR_BG = "#1E1E1E"
TEXT_COLOR = "#000000"
ACCENT = "#0d6efd"

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    .gdt-card {{
        background-color: #FFFFFF;
        border-left: 8px solid {ACCENT};
        padding: 20px; border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: {TEXT_COLOR}; margin-bottom: 20px;
    }}
    
    .interpretation-box {{
        background-color: #e8f4f8;
        border-left: 6px solid {ACCENT};
        padding: 20px; border-radius: 5px;
        margin-top: 10px; font-family: sans-serif; color: {TEXT_COLOR};
    }}
    
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    h1, h2, h3, p, li, span, label {{ color: {TEXT_COLOR} !important; }}
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS (VERIFICADA)
# ==========================================
gdt_data = {
    'Rectitud': {'symbol': '⏤', 'type': 'surf', 'datum': False, 'def': 'Controla la rectitud de una línea.', 'desc': 'rectitud', 'zone': 'dos líneas paralelas'},
    'Planicidad': {'symbol': '⏥', 'type': 'surf', 'datum': False, 'def': 'Controla la planitud de una superficie.', 'desc': 'planicidad', 'zone': 'dos planos paralelos'},
    'Redondez': {'symbol': '○', 'type': 'axis', 'datum': False, 'def': 'Controla la circularidad (2D).', 'desc': 'redondez', 'zone': 'dos círculos concéntricos'},
    'Cilindricidad': {'symbol': '⌭', 'type': 'axis', 'datum': False, 'def': 'Controla la forma cilíndrica (3D).', 'desc': 'cilindricidad', 'zone': 'dos cilindros coaxiales'},
    'Angularidad': {'symbol': '∠', 'type': 'surf', 'datum': 'A', 'def': 'Controla ángulo respecto a Datum.', 'desc': 'angularidad', 'zone': 'dos planos inclinados'},
    'Perpendicularidad': {'symbol': '⟂', 'type': 'surf', 'datum': 'A', 'def': 'Controla 90° respecto a Datum.', 'desc': 'perpendicularidad', 'zone': 'dos planos a 90°'},
    'Paralelismo': {'symbol': '∥', 'type': 'surf', 'datum': 'A', 'def': 'Controla paralelismo a Datum.', 'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum'},
    'Posición': {'symbol': '⌖', 'type': 'axis', 'datum': 'A B', 'def': 'Controla ubicación exacta.', 'desc': 'posición', 'zone': 'cilindro en posición teórica'},
    'Concentricidad': {'symbol': '◎', 'type': 'axis', 'datum': 'A', 'def': 'Controla eje mediano.', 'desc': 'concentricidad', 'zone': 'cilindro coaxial'},
    'Alabeo Circular': {'symbol': '↗', 'type': 'axis', 'datum': 'A-B', 'def': 'Variación circular al girar.', 'desc': 'alabeo circular', 'zone': 'distancia radial (sección)'},
    'Alabeo Total': {'symbol': '⌰', 'type': 'axis', 'datum': 'A-B', 'def': 'Variación total al girar.', 'desc': 'alabeo total', 'zone': 'distancia radial (total)'},
    'Perfil de una línea': {'symbol': '⌒', 'type': 'surf', 'datum': False, 'def': 'Forma de línea 2D.', 'desc': 'perfil de línea', 'zone': 'banda uniforme'},
    'Perfil de una superficie': {'symbol': '⌓', 'type': 'surf', 'datum': False, 'def': 'Forma de superficie 3D.', 'desc': 'perfil de superficie', 'zone': 'dos superficies envolventes'}
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO (TRAZOS REALES)
# ==========================================
def get_plot_layout(title, is_3d=True):
    layout = dict(
        title=dict(text=title, font=dict(size=18, color='black')),
        font=dict(color='black'),
        margin=dict(l=20, r=20, t=50, b=20),
        height=600,
        autosize=True
    )
    if is_3d:
        layout['paper_bgcolor'] = MAIN_BG
        layout['plot_bgcolor'] = MAIN_BG
        layout['scene'] = dict(
            aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6),
            xaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            yaxis=dict(visible=False, backgroundcolor=MAIN_BG),
            zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#ccc")
        )
    else:
        layout['paper_bgcolor'] = 'white'
        layout['plot_bgcolor'] = 'white'
        layout['xaxis'] = dict(visible=False, showgrid=False, range=[-1, 14])
        layout['yaxis'] = dict(visible=False, showgrid=False, range=[-2, 9])
        layout['shapes'] = [dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=2))]
    return layout

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=False, hoverinfo='skip'))

def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    fill_val = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, fill=fill_val, fillcolor=fill, line=dict(color=color, width=width), mode='lines', showlegend=False, hoverinfo='skip'))

# ==========================================
# VISTA 1: SIMULACIÓN 3D (RESETEADA)
# ==========================================
def plot_3d_simulation(feature, tol):
    fig = go.Figure() # Nueva figura siempre
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2 * np.pi, 30); tg, zg = np.meshgrid(theta, z)
    
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False, name='Zona'))
    elif feature == 'Planicidad':
        x = np.linspace(-5,5,30); y = np.linspace(-5,5,30); xg,yg = np.meshgrid(x,y)
        fig.add_trace(go.Surface(z=0.15*np.sin(xg/2)*np.cos(yg/2), x=xg, y=yg, colorscale='Viridis', name='Real'))
        fig.add_trace(go.Surface(z=np.full_like(xg, tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False))
        fig.add_trace(go.Surface(z=np.full_like(xg, -tol/2), x=xg, y=yg, opacity=0.2, colorscale=[[0,'red'],[1,'red']], showscale=False))
    elif feature in ['Cilindricidad', 'Alabeo Total']:
        r = 5 + 0.2 * np.sin(zg * np.pi / 5)
        fig.add_trace(go.Surface(x=r*np.cos(tg), y=r*np.sin(tg), z=zg, colorscale='Spectral', name='Real'))
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', line=dict(color='black', width=5, dash='dash'), name='Eje'))
    elif feature == 'Redondez':
        th = np.linspace(0, 2*np.pi, 100); r = 5 + 0.2 * np.cos(3*th)
        fig.add_trace(go.Scatter3d(x=r*np.cos(th), y=r*np.sin(th), z=np.zeros_like(th), mode='lines', line=dict(color='blue', width=6), name='Real'))
        fig.add_trace(go.Scatter3d(x=(5+tol/2)*np.cos(th), y=(5+tol/2)*np.sin(th), z=np.zeros_like(th), line=dict(color='red', dash='dash'), name='Lim'))
    else:
        fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Eje'))
        fig.add_trace(go.Surface(x=2*np.cos(tg), y=2*np.sin(tg), z=zg, opacity=0.1, showscale=False))

    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}", is_3d=True))
    return fig

# ==========================================
# VISTA 2: MONTAJE REAL (ESTÁTICO + ANIMACIÓN)
# ==========================================
def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ PLAY", method="animate", args=[None])])]
    fig.update_layout(**layout)
    
    draw_rect_trace(fig, -1, -1, 11, 0, color="black", fill="#ccc") # Mesa
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    
    # Animación simple
    frames = []
    for i in range(0, 50, 2):
        x = i/5; y = 1.5+0.2*np.sin(x)
        frames.append(go.Frame(data=[
            go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50))),
            go.Scatter(x=[x, x], y=[y, y+3], mode="lines", line=dict(color="#444", width=4)),
            go.Scatter(x=[x], y=[y+3], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2))),
            go.Scatter(x=[x, x+0.5*np.cos(i)], y=[y+3, y+3+0.5*np.sin(i)], mode="lines", line=dict(color="red", width=2))
        ]))
    
    # Inicial
    fig.add_trace(go.Scatter(x=[0,0], y=[1.5, 4.5], mode="lines", line=dict(color="#444", width=4), name="Vástago"))
    fig.add_trace(go.Scatter(x=[0], y=[4.5], mode="markers", marker=dict(size=40, color="white", line=dict(color="black", width=2)), name="Reloj"))
    fig.add_trace(go.Scatter(x=[0,0.5], y=[4.5, 4.5], mode="lines", line=dict(color="red", width=2), name="Aguja"))
    
    fig.frames = frames
    return fig

# ==========================================
# VISTA 3: PLANO DE INGENIERÍA (TRAZOS BLINDADOS)
# ==========================================
def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data.get(feature, gdt_data['Rectitud'])
    ftype = info['type']; sym = info['symbol']; datum = info.get('datum', None)
    
    fig = go.Figure()
    fig.update_layout(**get_plot_layout(f"Plano de Ingeniería: {feature}", is_3d=False))

    # --- PIEZA (Dibujo por trazos) ---
    draw_rect_trace(fig, 2, 2, 10, 6, width=3) 
    draw_line_trace(fig, 1, 4, 11, 4, width=1, dash='longdashdot')

    # --- COTA DE TAMAÑO ---
    draw_line_trace(fig, 10, 6, 10.5, 6, width=1)
    draw_line_trace(fig, 10, 2, 10.5, 2, width=1)
    # Flecha Manual
    fig.add_trace(go.Scatter(x=[10.25, 10.25], y=[2, 6], mode='lines+markers', marker=dict(symbol='arrow-up', size=10, color='black'), line=dict(color='black')))
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=5, arrowhead=2, arrowcolor="black") 
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3, arrowhead=2, arrowcolor="black")
    fig.add_annotation(x=10.25, y=5.5, text="Ø 40 ±0.1", font=dict(size=14, color="black", weight="bold"), bgcolor="white", showarrow=False)

    # --- DATUM ---
    if datum:
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # --- MARCO Y LÍDER ---
    if ftype == 'surf':
        # Apunta Superficie
        leader_start_x, leader_start_y = 6, 6
        box_x, box_y = 6, 7.5
    else:
        # Apunta Cota
        leader_start_x, leader_start_y = 10.25, 4.5
        box_x, box_y = 12, 4.5
        
    # Línea Conectora (Líder)
    draw_line_trace(fig, leader_start_x, leader_start_y, box_x, box_y, width=2)
    # Punta de flecha manual en el inicio
    fig.add_annotation(x=leader_start_x, y=leader_start_y, ax=leader_start_x + (box_x-leader_start_x)*0.2, ay=leader_start_y + (box_y-leader_start_y)*0.2, arrowhead=2, arrowcolor="black")

    # Cajas del Marco
    w_box = 1.5
    if ftype == 'surf': start_x = box_x - w_box
    else: start_x = box_x
    
    # Caja 1
    draw_rect_trace(fig, start_x, box_y, start_x+w_box, box_y+1, width=2, fill='white')
    fig.add_annotation(x=start_x+w_box/2, y=box_y+0.5, text=f"<b>{sym}</b>", font=dict(size=24, color="black"), showarrow=False)
    
    # Caja 2
    draw_rect_trace(fig, start_x+w_box, box_y, start_x+w_box*2.5, box_y+1, width=2, fill='white')
    t_str = f"Ø {tol_val}" if ftype == 'axis' else f"{tol_val}"
    fig.add_annotation(x=start_x+w_box*1.75, y=box_y+0.5, text=f"<b>{t_str}</b>", font=dict(size=20, color="black"), showarrow=False)

    if datum:
        draw_rect_trace(fig, start_x+w_box*2.5, box_y, start_x+w_box*3.5, box_y+1, width=2, fill='white')
        fig.add_annotation(x=start_x+w_box*3, y=box_y+0.5, text=f"<b>{datum}</b>", font=dict(size=20, color="black"), showarrow=False)

    return fig

# ==========================================
# 4. INTERFAZ
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
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# CLAVE ÚNICA PARA EVITAR CONGELAMIENTO
chart_key = f"{feat}_{view_mode}_{tol}"

if view_mode == "📐 Simulación 3D":
    st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True, key=chart_key)
elif view_mode == "🏭 Montaje Real":
    st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True, key=chart_key)
elif view_mode == "📝 Interpretación de Plano":
    st.plotly_chart(draw_engineering_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True}, key=chart_key)
    t_str = f"Ø {tol} mm" if info.get('type') == 'axis' else f"{tol} mm"
    st.markdown(f"""<div class='interpretation-box'><h4>🤓 Interpretación:</h4><p>Controla <b>{info.get('desc', '')}</b> dentro de una zona de <b>{info.get('zone', '')}</b>.</p></div>""", unsafe_allow_html=True)
