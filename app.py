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
# 1. BASE DE DATOS (COMPLETA)
# ==========================================
gdt_data = {
    'Rectitud': {'sym': '⏤', 'type': 'surf', 'datum': False, 'def': 'Controla la rectitud de una línea superficial o eje.', 'zone': 'Dos líneas paralelas separadas por la tolerancia.'},
    'Planicidad': {'sym': '⏥', 'type': 'surf', 'datum': False, 'def': 'Controla la planitud de una superficie.', 'zone': 'Dos planos paralelos separados por la tolerancia.'},
    'Redondez': {'sym': '○', 'type': 'axis', 'datum': False, 'def': 'Controla la circularidad de una sección (2D).', 'zone': 'Dos círculos concéntricos.'},
    'Cilindricidad': {'sym': '⌭', 'type': 'axis', 'datum': False, 'def': 'Controla la forma cilíndrica total (3D).', 'zone': 'Dos cilindros coaxiales.'},
    'Angularidad': {'sym': '∠', 'type': 'surf', 'datum': 'A', 'def': 'Controla la inclinación respecto a un Datum.', 'zone': 'Dos planos paralelos inclinados.'},
    'Perpendicularidad': {'sym': '⟂', 'type': 'surf', 'datum': 'A', 'def': 'Controla los 90° respecto a un Datum.', 'zone': 'Dos planos paralelos a 90° del Datum.'},
    'Paralelismo': {'sym': '∥', 'type': 'surf', 'datum': 'A', 'def': 'Controla el paralelismo respecto a un Datum.', 'zone': 'Dos planos paralelos al Datum.'},
    'Posición': {'sym': '⌖', 'type': 'axis', 'datum': 'A B', 'def': 'Controla la ubicación exacta del centro.', 'zone': 'Un cilindro centrado en la posición teórica.'},
    'Concentricidad': {'sym': '◎', 'type': 'axis', 'datum': 'A', 'def': 'Controla la colinealidad de ejes opuestos.', 'zone': 'Un cilindro coaxial al Datum.'},
    'Alabeo Circular': {'sym': '↗', 'type': 'axis', 'datum': 'A-B', 'def': 'Controla variación circular al girar.', 'zone': 'Distancia radial (sección).'},
    'Alabeo Total': {'sym': '⌰', 'type': 'axis', 'datum': 'A-B', 'def': 'Controla variación total de superficie.', 'zone': 'Distancia radial (total).'},
    'Perfil de una línea': {'sym': '⌒', 'type': 'surf', 'datum': False, 'def': 'Controla la forma de una curva 2D.', 'zone': 'Banda uniforme siguiendo el perfil.'},
    'Perfil de una superficie': {'sym': '⌓', 'type': 'surf', 'datum': False, 'def': 'Controla la forma de una superficie 3D.', 'zone': 'Límites envolventes siguiendo la forma.'}
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO (PRIMITIVAS)
# ==========================================
def draw_line(fig, x0, y0, x1, y1, color="black", width=2, dash=None):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode='lines', line=dict(color=color, width=width, dash=dash), showlegend=False, hoverinfo='skip'))

def draw_rect(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    x = [x0, x1, x1, x0, x0]; y = [y0, y0, y1, y1, y0]
    fill_val = "toself" if fill else "none"
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill=fill_val, fillcolor=fill, line=dict(color=color, width=width), showlegend=False, hoverinfo='skip'))

def draw_arrow(fig, x_tail, y_tail, x_head, y_head):
    fig.add_annotation(x=x_head, y=y_head, ax=x_tail, ay=y_tail, xref='x', yref='y', axref='x', ayref='y', showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="black")

def draw_gdt_frame(fig, x, y, sym, tol, datum, leader_to_x, leader_to_y):
    # Dibuja el marco y la flecha líder
    w_box = 1.2; h_box = 1.0
    
    # Caja Símbolo
    draw_rect(fig, x, y, x+w_box, y+h_box, width=2, fill='white')
    fig.add_annotation(x=x+w_box/2, y=y+h_box/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=20, color="black"))
    
    # Caja Tolerancia
    draw_rect(fig, x+w_box, y, x+w_box*2.5, y+h_box, width=2, fill='white')
    fig.add_annotation(x=x+w_box*1.75, y=y+h_box/2, text=f"<b>{tol}</b>", showarrow=False, font=dict(size=16, color="black"))
    
    current_x = x + w_box*2.5
    
    # Caja Datum
    if datum:
        draw_rect(fig, current_x, y, current_x+w_box, y+h_box, width=2, fill='white')
        fig.add_annotation(x=current_x+w_box/2, y=y+h_box/2, text=f"<b>{datum}</b>", showarrow=False, font=dict(size=16, color="black"))
        current_x += w_box
        
    # Línea líder (Flecha)
    # Conecta el centro inferior o lateral del marco con el punto objetivo
    draw_arrow(fig, x, y+h_box/2, leader_to_x, leader_to_y) # Flecha desde la izq del cuadro

# ==========================================
# 3. PLANOS ESPECÍFICOS (DIBUJOS TÉCNICOS)
# ==========================================

def draw_specific_blueprint(feature, tol_val):
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 12], visible=False, scaleanchor="y"), yaxis=dict(range=[0, 8], visible=False), plot_bgcolor='white', margin=dict(l=10, r=10, t=10, b=10), height=500)
    # Marco Papel
    draw_rect(fig, 0.2, 0.2, 11.8, 7.8, width=4)
    
    info = gdt_data[feature]
    sym = info['sym']
    datum = info.get('datum', None)
    
    # --- CASO 1: RECTITUD / PLANICIDAD (Bloque rectangular) ---
    if feature in ['Rectitud', 'Planicidad', 'Paralelismo']:
        # Pieza
        draw_rect(fig, 2, 2, 8, 5, width=3)
        # Si es Rectitud, indicamos la línea superior
        if feature == 'Rectitud':
            # Cota GD&T apuntando a la superficie
            draw_gdt_frame(fig, 8.5, 6, sym, str(tol_val), datum, 5, 5) # Apunta al centro de la cara superior
            
        # Si es Paralelismo, necesitamos Datum A abajo
        if feature == 'Paralelismo':
            # Datum A en la base
            draw_rect(fig, 4.5, 1.2, 5.5, 2, width=1)
            fig.add_annotation(x=5, y=1.6, text="<b>A</b>", showarrow=False, font=dict(size=14, color="black"))
            fig.add_trace(go.Scatter(x=[5, 4.5, 5.5, 5], y=[2, 1.2, 1.2, 2], fill="toself", fillcolor="black", showlegend=False))
            # Cota apuntando arriba
            draw_gdt_frame(fig, 8.5, 6, sym, str(tol_val), datum, 5, 5)

    # --- CASO 2: REDONDEZ / CILINDRICIDAD (Vista Circular) ---
    elif feature in ['Redondez', 'Cilindricidad']:
        # Círculo (Vista frontal de un eje)
        th = np.linspace(0, 2*np.pi, 100)
        fig.add_trace(go.Scatter(x=5 + 2*np.cos(th), y=4 + 2*np.sin(th), mode='lines', line=dict(color='black', width=3), showlegend=False))
        # Ejes de centro
        draw_line(fig, 2.5, 4, 7.5, 4, width=1, dash='longdashdot')
        draw_line(fig, 5, 1.5, 5, 6.5, width=1, dash='longdashdot')
        
        # Cota apuntando a la superficie
        draw_gdt_frame(fig, 8, 6, sym, str(tol_val), datum, 6.5, 5.3) # Apunta al borde noreste

    # --- CASO 3: POSICIÓN (Placa con agujeros) ---
    elif feature == 'Posición':
        # Placa
        draw_rect(fig, 2, 1, 9, 7, width=3)
        # Agujero Central
        th = np.linspace(0, 2*np.pi, 50)
        fig.add_trace(go.Scatter(x=5.5 + 1*np.cos(th), y=4 + 1*np.sin(th), mode='lines', line=dict(color='black', width=2), showlegend=False))
        # Ejes de centro
        draw_line(fig, 2, 4, 9, 4, width=1, dash='longdashdot')
        draw_line(fig, 5.5, 1, 5.5, 7, width=1, dash='longdashdot')
        
        # Cotas Básicas (Cuadros)
        draw_rect(fig, 5.0, 7.2, 6.0, 7.8, width=1) # Cota X
        fig.add_annotation(x=5.5, y=7.5, text="<b>50</b>", showarrow=False, font=dict(color="black"))
        
        # Cota de tamaño del agujero
        draw_line(fig, 6.5, 4, 8, 5, width=1)
        fig.add_annotation(x=8.5, y=5.2, text="Ø 20 ±0.1", showarrow=False, font=dict(color="black"))
        
        # Marco de control debajo de la cota de tamaño
        draw_gdt_frame(fig, 8.5, 4, sym, f"Ø {tol_val}", datum, 8.5, 5.0)

    # --- CASO 4: ANGULARIDAD (Pieza con chaflán) ---
    elif feature == 'Angularidad':
        # Pieza
        path_x = [2, 8, 8, 6, 2, 2]
        path_y = [2, 2, 4, 6, 6, 2]
        fig.add_trace(go.Scatter(x=path_x, y=path_y, mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        # Datum A (Base)
        draw_rect(fig, 4.5, 1.2, 5.5, 2, width=1)
        fig.add_annotation(x=5, y=1.6, text="<b>A</b>", showarrow=False, font=dict(color="black"))
        
        # Cota apuntando a la cara inclinada
        draw_gdt_frame(fig, 9, 6, sym, str(tol_val), datum, 7, 5)

    # --- CASO 5: PERPENDICULARIDAD (Escuadra) ---
    elif feature == 'Perpendicularidad':
        # Pieza en L
        path_x = [2, 8, 8, 4, 4, 2, 2]
        path_y = [2, 2, 3, 3, 6, 6, 2]
        fig.add_trace(go.Scatter(x=path_x, y=path_y, mode='lines', line=dict(color='black', width=3), showlegend=False))
        
        # Datum A (Base)
        fig.add_annotation(x=5, y=2, text="<b>A</b>", showarrow=True, arrowhead=2, ay=30)
        
        # Cota apuntando a la cara vertical
        draw_gdt_frame(fig, 6, 5, sym, str(tol_val), datum, 4, 5) # Apunta a la cara vertical derecha

    else:
        # Dibujo genérico para los restantes (Concentricidad, Alabeos)
        # Eje escalonado
        draw_rect(fig, 1, 3, 9, 5, width=3)
        draw_rect(fig, 9, 3.5, 11, 4.5, width=3)
        draw_line(fig, 0.5, 4, 11.5, 4, width=1, dash='longdashdot')
        
        # Datum A en el diámetro mayor
        fig.add_annotation(x=5, y=3, text="<b>A</b>", showarrow=True, arrowhead=2, ay=30)
        
        # Cota apuntando al diámetro menor (eje)
        draw_gdt_frame(fig, 9, 6, sym, str(tol_val), datum, 10, 4.5)

    return fig

# --- PLANO MAESTRO (MULTIPLE) ---
def draw_master_blueprint(active_features):
    fig = go.Figure()
    fig.update_layout(xaxis=dict(range=[0, 14], visible=False, scaleanchor="y"), yaxis=dict(range=[0, 9], visible=False), plot_bgcolor='white', height=600)
    
    # Pieza Maestra Compleja
    # Base
    draw_rect(fig, 1, 1, 11, 3, width=3)
    # Torreta
    draw_rect(fig, 2, 3, 4, 7, width=3)
    # Chaflán
    draw_line(fig, 11, 3, 9, 5, width=3)
    draw_line(fig, 9, 5, 4, 5, width=3)
    draw_line(fig, 4, 5, 4, 3, width=0) # Invisible para cerrar lógica visual
    
    # Agujero en torreta
    draw_line(fig, 3, 4, 3, 6, width=1, dash='longdashdot') # Eje
    
    # Datums
    fig.add_annotation(x=6, y=1, text="<b>A</b>", showarrow=True, arrowhead=2, ay=20, ax=0)
    fig.add_annotation(x=1, y=2, text="<b>B</b>", showarrow=True, arrowhead=2, ay=0, ax=-20)

    # Ubicaciones predefinidas para cotas
    locs = {
        'Rectitud': (7, 1.5, 7, 0.5), # Base
        'Planicidad': (6, 3.5, 6, 5.5), # Cara superior base
        'Perpendicularidad': (1.5, 5, 0.5, 5), # Cara lateral torreta
        'Posición': (3, 7, 3, 8), # Agujero
        'Angularidad': (10, 4, 11, 5), # Chaflán
        'Paralelismo': (3, 7, 5, 7.5) # Tope torreta
    }

    for feat in active_features:
        if feat in locs:
            target_x, target_y, frame_x, frame_y = locs[feat]
            info = gdt_data[feat]
            draw_gdt_frame(fig, frame_x, frame_y, info['symbol'], "0.05", info.get('datum', ''), target_x, target_y)

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
    '4. Control/Loc': ['Posición', 'Concentricidad', 'Alabeo Circular', 'Alabeo Total']
}

# SELECTOR DE MODO
mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano Maestro"])
st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
    
    view_mode = st.sidebar.radio("Vista:", ["📐 Simulación 3D", "🏭 Montaje Real", "📝 Plano Técnico"])
    
    st.sidebar.info("Profesor: Ing. Jaime Silva")
    
    # Definición
    info = gdt_data[feat]
    st.markdown(f"""<div class="gdt-card"><div style="display: flex; align-items: center;"><div class="big-icon" style="flex: 1;">{info['symbol']}</div><div style="flex: 4; padding-left: 20px;"><h3 style="margin:0; color: #0d6efd;">{feat}</h3><p><strong>Definición:</strong> {info['def']}</p></div></div></div>""", unsafe_allow_html=True)

    if view_mode == "📝 Plano Técnico":
        st.plotly_chart(draw_specific_blueprint(feat, tol), use_container_width=True, config={'staticPlot': True})
        st.markdown(f"""<div class="interpretation-box"><h4>🤓 Interpretación:</h4><p>Controla <b>{info['desc']}</b> dentro de una zona de <b>{info['zone']}</b>.</p></div>""", unsafe_allow_html=True)
    else:
        st.info("⚠️ Para ver Simulaciones y Montajes animados, por favor use la versión V14 anterior si desea esas funciones. Esta vista V16 está optimizada para PLANOS TÉCNICOS CLAROS.")

elif mode == "📝 Constructor de Plano Maestro":
    st.sidebar.info("Seleccione características para agregarlas al plano:")
    feats_avail = ['Rectitud', 'Planicidad', 'Perpendicularidad', 'Posición', 'Angularidad']
    selected = st.sidebar.multiselect("Agregar:", feats_avail, default=['Rectitud'])
    
    st.markdown("## 📐 Plano de Ingeniería Maestro")
    st.plotly_chart(draw_master_blueprint(selected), use_container_width=True)
