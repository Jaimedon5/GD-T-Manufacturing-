import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Interpretación GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL CLARO)
# ==========================================
MAIN_BG = "#F0F2F6"
SIDEBAR_BG = "#1E1E1E"
TEXT_COLOR = "#000000"

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    
    .interpretation-box {{
        background-color: #e8f4f8;
        border-left: 6px solid #0d6efd;
        padding: 20px;
        border-radius: 5px;
        margin-top: 10px;
        font-family: sans-serif;
        color: #000000; /* Texto negro forzado */
    }}
    .tech-text {{ font-family: 'Courier New', monospace; font-weight: bold; }}
    
    h1, h2, h3 {{ color: #000000 !important; }}
    
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS INTELIGENTE
# ==========================================
gdt_data = {
    # Superficie (La flecha toca la superficie)
    'Rectitud': {'sym': '⏤', 'type': 'surf', 'desc': 'rectitud', 'zone': 'dos líneas paralelas'},
    'Planicidad': {'sym': '⏥', 'type': 'surf', 'desc': 'planicidad', 'zone': 'dos planos paralelos'},
    'Perfil de una línea': {'sym': '⌒', 'type': 'surf', 'desc': 'perfil de línea', 'zone': 'una banda uniforme'},
    'Perfil de una superficie': {'sym': '⌓', 'type': 'surf', 'desc': 'perfil de superficie', 'zone': 'dos superficies envolventes'},
    'Angularidad': {'sym': '∠', 'type': 'surf', 'datum': 'A', 'desc': 'angularidad', 'zone': 'dos planos paralelos inclinados'},
    'Perpendicularidad': {'sym': '⟂', 'type': 'surf', 'datum': 'A', 'desc': 'perpendicularidad', 'zone': 'dos planos paralelos a 90°'},
    'Paralelismo': {'sym': '∥', 'type': 'surf', 'datum': 'A', 'desc': 'paralelismo', 'zone': 'dos planos paralelos al Datum'},

    # Eje / Centro (La flecha toca la cota de tamaño)
    'Cilindricidad': {'sym': '⌭', 'type': 'axis', 'desc': 'cilindricidad', 'zone': 'dos cilindros concéntricos'},
    'Redondez': {'sym': '○', 'type': 'axis', 'desc': 'redondez', 'zone': 'dos círculos concéntricos'},
    'Posición': {'sym': '⌖', 'type': 'axis', 'datum': 'A B', 'desc': 'posición', 'zone': 'un cilindro centrado en la posición teórica'},
    'Concentricidad': {'sym': '◎', 'type': 'axis', 'datum': 'A', 'desc': 'concentricidad', 'zone': 'un cilindro coaxial al Datum'},
    'Alabeo Circular': {'sym': '↗', 'type': 'axis', 'datum': 'A-B', 'desc': 'alabeo circular', 'zone': 'la distancia radial entre dos círculos coaxiales'},
    'Alabeo Total': {'sym': '⌰', 'type': 'axis', 'datum': 'A-B', 'desc': 'alabeo total', 'zone': 'la distancia radial entre dos cilindros coaxiales'}
}

# ==========================================
# 2. DIBUJANTE DE PLANOS (ENGINEERING DRAWING)
# ==========================================
def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]
    y = [y0, y0, y1, y1, y0]
    if fill:
        fig.add_trace(go.Scatter(x=x, y=y, fill="toself", fillcolor=fill, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=width), mode='lines', hoverinfo='skip', showlegend=False))

def draw_engineering_blueprint(feature, tol_val):
    info = gdt_data[feature]
    ftype = info['type']
    sym = info['sym']
    datum = info.get('datum', None)
    
    fig = go.Figure()
    
    # --- 1. LA PIEZA (Eje Escalonado Simplificado) ---
    # Cuerpo Principal
    draw_rect_trace(fig, 2, 2, 10, 6, width=3)
    # Eje Central
    fig.add_trace(go.Scatter(x=[1, 11], y=[4, 4], mode='lines', line=dict(color='black', width=1, dash='longdashdot'), showlegend=False))
    
    # --- 2. COTAS DE TAMAÑO (DIMENSIONES) ---
    # Cota de diámetro (arriba) - TEXTO NEGRO FORZADO
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[6, 6], mode='lines', line=dict(color='black', width=1), showlegend=False)) # Extensión
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[2, 2], mode='lines', line=dict(color='black', width=1), showlegend=False)) # Extensión
    
    # Flecha de cota
    fig.add_annotation(x=10.25, y=4, text="Ø 40 ±0.1", font=dict(size=14, color="black"), showarrow=False)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.2, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.8, arrowhead=2, arrowwidth=1, arrowcolor="black")

    # --- 3. DATUM (Si aplica) ---
    if datum:
        # Triángulo de Datum en la base
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14, color="black"), showarrow=False)

    # --- 4. MARCO DE CONTROL (FEATURE CONTROL FRAME) ---
    
    # Lógica de Ubicación
    if ftype == 'surf':
        # Apunta a la SUPERFICIE (Arriba)
        leader_x_start, leader_y_start = 6, 6 # Toca la línea de la pieza
        frame_x, frame_y = 6, 7.5
    else:
        # Apunta a la COTA DE TAMAÑO (Derecha) - Regla de Oro GD&T para Ejes
        leader_x_start, leader_y_start = 10.25, 3.8 # Toca el texto de la cota
        frame_x, frame_y = 10.25, 1.5

    # Dibujar el Marco (Cajitas)
    w_box = 1.5
    start_x_box = frame_x - w_box # Centrar
    
    # Caja 1: Símbolo
    draw_rect_trace(fig, start_x_box, frame_y, start_x_box+w_box, frame_y+1, width=2, fill='white')
    fig.add_annotation(x=start_x_box+w_box/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=28, color="black"), showarrow=False)
    
    # Caja 2: Tolerancia
    draw_rect_trace(fig, start_x_box+w_box, frame_y, start_x_box+w_box*2.5, frame_y+1, width=2, fill='white')
    # Agregar símbolo de diámetro si es de eje
    tol_str = f"Ø {tol_val}" if ftype == 'axis' else f"{tol_val}"
    fig.add_annotation(x=start_x_box+w_box*1.75, y=frame_y+0.5, text=f"<b>{tol_str}</b>", font=dict(size=22, color="black"), showarrow=False)
    
    # Caja 3: Datum (Opcional)
    if datum:
        draw_rect_trace(fig, start_x_box+w_box*2.5, frame_y, start_x_box+w_box*3.5, frame_y+1, width=2, fill='white')
        fig.add_annotation(x=start_x_box+w_box*3, y=frame_y+0.5, text=f"<b>{datum}</b>", font=dict(size=22, color="black"), showarrow=False)

    # Líder (Flecha conectora)
    fig.add_annotation(
        x=leader_x_start, y=leader_y_start,
        ax=frame_x, ay=frame_y if ftype == 'surf' else frame_y+1,
        axref="x", ayref="y", arrowhead=2, arrowwidth=2, arrowcolor="black"
    )

    # --- CONFIGURACIÓN DE LA "HOJA DE PAPEL" ---
    fig.update_layout(
        title=dict(text=f"Plano de Ingeniería: {feature}", font=dict(size=20, color="black")),
        xaxis=dict(range=[0, 14], showgrid=False, visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[0, 9], showgrid=False, visible=False),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20),
        height=500,
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))] # Marco del plano
    )
    
    return fig

# ==========================================
# 3. INTERFAZ Y LÓGICA DE INTERPRETACIÓN
# ==========================================
st.sidebar.title("🎛️ Controles de Plano")
st.sidebar.markdown("---")

menu = {
    '1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'],
    '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'],
    '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'],
    '4. Control/Loc': ['Posición', 'Concentricidad', 'Alabeo Circular', 'Alabeo Total']
}

cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
feat = st.sidebar.selectbox("Característica", menu[cat])
tol = st.sidebar.slider("Tolerancia (mm)", 0.01, 1.0, 0.1)

st.sidebar.info("Profesor: Ing. Jaime Silva")

# --- GRÁFICO (PLANO) ---
# Config staticPlot=True para que parezca una imagen y no se mueva
fig = draw_engineering_blueprint(feat, tol)
st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

# --- EL "INTERPRÉTE" (TEXTO EDUCATIVO) ---
info = gdt_data[feat]
tol_str = f"Ø {tol} mm" if info['type'] == 'axis' else f"{tol} mm"
datum_text = f" con respecto al Datum <b>{info.get('datum', '')}</b>" if 'datum' in info else "."

st.markdown(f"""
<div class="interpretation-box">
    <h4>🤓 Interpretación del Plano:</h4>
    <p style="font-size: 1.1em;">
        "Esta línea/superficie tiene una característica de <span class="tech-text" style="color: #d63384;">{feat.upper()}</span>, 
        con una tolerancia de <b>{tol_str}</b>{datum_text}"
    </p>
    <ul>
        <li><b>Controla:</b> {info['desc'].capitalize()}.</li>
        <li><b>Zona de Tolerancia:</b> El error debe estar contenido dentro de <b>{info['zone']}</b>.</li>
    </ul>
</div>
""", unsafe_allow_html=True)
