import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(layout="wide", page_title="Interpretación de Planos GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA INDUSTRIAL CLARO)
# ==========================================
# Usamos un fondo claro para simular papel de ingeniería
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
    'Rectitud': {'sym': '⏤', 'type': 'surf', 'desc': 'la rectitud de la línea superior', 'zone': 'dos líneas paralelas'},
    'Planicidad': {'sym': '⏥', 'type': 'surf', 'desc': 'la planicidad de la superficie superior', 'zone': 'dos planos paralelos'},
    'Perfil de una línea': {'sym': '⌒', 'type': 'surf', 'desc': 'la forma 2D de la curva', 'zone': 'una banda uniforme'},
    'Perfil de una superficie': {'sym': '⌓', 'type': 'surf', 'desc': 'la forma 3D de la superficie', 'zone': 'dos superficies envolventes'},
    'Angularidad': {'sym': '∠', 'type': 'surf', 'datum': 'A', 'desc': 'la inclinación de la superficie', 'zone': 'dos planos paralelos inclinados'},
    'Perpendicularidad': {'sym': '⟂', 'type': 'surf', 'datum': 'A', 'desc': 'la perpendicularidad de la cara', 'zone': 'dos planos paralelos a 90°'},
    'Paralelismo': {'sym': '∥', 'type': 'surf', 'datum': 'A', 'desc': 'el paralelismo de la cara superior', 'zone': 'dos planos paralelos al Datum'},

    # Eje / Centro (La flecha toca la cota de tamaño)
    'Cilindricidad': {'sym': '⌭', 'type': 'axis', 'desc': 'la forma cilíndrica total', 'zone': 'dos cilindros concéntricos'},
    'Redondez': {'sym': '○', 'type': 'axis', 'desc': 'la circularidad en cualquier sección', 'zone': 'dos círculos concéntricos'},
    'Posición': {'sym': '⌖', 'type': 'axis', 'datum': 'A B', 'desc': 'la ubicación exacta del centro del agujero', 'zone': 'un cilindro centrado en la posición teórica'},
    'Concentricidad': {'sym': '◎', 'type': 'axis', 'datum': 'A', 'desc': 'la colinealidad de los ejes', 'zone': 'un cilindro coaxial al Datum'},
    'Alabeo Circular': {'sym': '↗', 'type': 'axis', 'datum': 'A-B', 'desc': 'la variación circular al girar', 'zone': 'la distancia entre dos círculos coaxiales'},
    'Alabeo Total': {'sym': '⌰', 'type': 'axis', 'datum': 'A-B', 'desc': 'la variación total de la superficie', 'zone': 'la distancia entre dos cilindros coaxiales'}
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
    
    # --- 1. LA PIEZA (Eje Escalonado) ---
    # Cuerpo Principal
    draw_rect_trace(fig, 2, 2, 10, 6, width=3)
    # Eje Central
    fig.add_trace(go.Scatter(x=[1, 11], y=[4, 4], mode='lines', line=dict(color='black', width=1, dash='longdashdot'), showlegend=False))
    
    # Vista Lateral (Círculo a la derecha) para dar contexto 3D
    theta = np.linspace(0, 2*np.pi, 50)
    fig.add_trace(go.Scatter(x=12 + np.cos(theta), y=4 + np.sin(theta)*2, mode='lines', line=dict(color='black', width=2), showlegend=False))
    # Cruz de centro
    fig.add_trace(go.Scatter(x=[11.5, 12.5], y=[4, 4], mode='lines', line=dict(color='black', width=1), showlegend=False))
    fig.add_trace(go.Scatter(x=[12, 12], y=[3, 5], mode='lines', line=dict(color='black', width=1), showlegend=False))

    # --- 2. COTAS DE TAMAÑO (DIMENSIONES) ---
    # Cota de diámetro (arriba)
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[6, 6], mode='lines', line=dict(color='black', width=1), showlegend=False)) # Extensión
    fig.add_trace(go.Scatter(x=[10, 10.5], y=[2, 2], mode='lines', line=dict(color='black', width=1), showlegend=False)) # Extensión
    # Flecha de cota
    fig.add_annotation(x=10.25, y=4, text="Ø 40 ±0.1", font=dict(size=14), showarrow=False)
    fig.add_annotation(x=10.25, y=6, ax=10.25, ay=4.2, arrowhead=2, arrowwidth=1, arrowcolor="black")
    fig.add_annotation(x=10.25, y=2, ax=10.25, ay=3.8, arrowhead=2, arrowwidth=1, arrowcolor="black")

    # --- 3. DATUM (Si aplica) ---
    if datum:
        # Triángulo de Datum en la base
        fig.add_trace(go.Scatter(x=[3, 4, 3.5, 3], y=[2, 2, 1.2, 2], fill="toself", fillcolor="black", line=dict(color="black"), showlegend=False))
        draw_rect_trace(fig, 3.1, 0.4, 3.9, 1.2, width=1)
        fig.add_annotation(x=3.5, y=0.8, text="<b>A</b>", font=dict(size=14), showarrow=False)

    # --- 4. MARCO DE CONTROL (FEATURE CONTROL FRAME) ---
    
    # Lógica de Ubicación Inteligente
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
    fig.add_annotation(x=start_x_box+w_box/2, y=frame_y+0.5, text=f"<b>{sym}</b>", font=dict(size=24), showarrow=False)
    
    # Caja 2: Tolerancia
    draw_rect_trace(fig, start_x_box+w_box, frame_y, start_x_box+w_box*2.5, frame_y+1, width=2, fill='white')
    # Agregar símbolo de diámetro si es de eje
    tol_str = f"Ø {tol_val}" if ftype == 'axis' else f"{tol_val}"
    fig.add_annotation(x=start_x_box+w_box*1.75, y=frame_y+0.5, text=f"<b>{tol_str}</b>", font=dict(size=20), showarrow=False)
    
    # Caja 3: Datum (Opcional)
    if datum:
        draw_rect_trace(fig, start_x_box+w_box*2.5, frame_y, start_x_box+w_box*3.5, frame_y+1, width=2, fill='white')
        fig.add_annotation(x=start_x_box+w_box*3, y=frame_y+0.5, text=f"<b>{datum}</b>", font=dict(size=20), showarrow=False)

    # Líder (Flecha conectora)
    fig.add_annotation(
        x=leader_x_start, y=leader_y_start,
        ax=frame_x, ay=frame_y if ftype == 'surf' else frame_y+1,
        axref="x", ayref="y", arrowhead=2, arrowwidth=2, arrowcolor="black"
    )

    # --- CONFIGURACIÓN DE LA "HOJA DE PAPEL" ---
    fig.update_layout(
        xaxis=dict(range=[0, 14], showgrid=False, visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[0, 9], showgrid=False, visible=False),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=20, b=20),
        height=500,
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=4))] # Marco del plano
    )
    
    return fig

# ==========================================
# 3. INTERFAZ Y LÓGICA DE INTERPRETACIÓN
# ==========================================
st.sidebar.title("🎛️ GD&T Explorer")
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

# --- TÍTULO Y GRÁFICO ---
st.markdown(f"## 📐 Plano de Ingeniería: {feat}")
st.markdown("A continuación se muestra cómo se especifica esta característica en un dibujo técnico real.")

# Dibujar el plano
fig = draw_engineering_blueprint(feat, tol)
st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

# --- EL "INTERPRÉTE" (LO QUE PIDIÓ EL USUARIO) ---
info = gdt_data[feat]
tol_str = f"Ø {tol} mm" if info['type'] == 'axis' else f"{tol} mm"
datum_str = f" con respecto al Datum <b>{info.get('datum', '')}</b>" if 'datum' in info else " (No requiere Datum)"

st.markdown(f"""
<div class="interpretation-box">
    <h4>🤓 ¿Cómo se lee este plano?</h4>
    <p style="font-size: 1.1em;">
        "Esta cota indica una característica de <span class="tech-text" style="color: #d63384;">{feat.upper()}</span>. 
        Controla <b>{info['desc']}</b>."
    </p>
    <ul>
        <li><b>Zona de Tolerancia:</b> El error permitido debe estar contenido dentro de <b>{info['zone']}</b> de ancho <b>{tol_str}</b>{datum_str}.</li>
        <li><b>Significado:</b> Si fabricas esta pieza y el error de {feat} supera los {tol} mm, la pieza <b>NO PASA</b> (es rechazo).</li>
    </ul>
</div>
""", unsafe_allow_html=True)
