import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA "HIGH CONTRAST ENGINEERING")
# ==========================================
MAIN_BG = "#D5D5D7"
SIDEBAR_BG = "#1E1E1E"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#000000"
TEXT_SIDE = "#FFFFFF"
ACCENT_COLOR = "#0d6efd"

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_COLOR}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: {TEXT_SIDE} !important; }}
    
    .gdt-card {{
        background-color: {CARD_BG};
        border: 1px solid #999;
        border-left: 8px solid {ACCENT_COLOR};
        padding: 20px; border-radius: 8px; color: {TEXT_COLOR}; margin-bottom: 20px;
    }}
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_COLOR}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS
# ==========================================
gdt_data = {
    # Grupo Superficie / Línea
    'Rectitud': {'symbol': '⏤', 'datum': False, 'type': 'surf', 'def': 'Controla la rectitud de una línea.'},
    'Planicidad': {'symbol': '⏥', 'datum': False, 'type': 'surf', 'def': 'Controla la planitud de una superficie.'},
    'Perfil de una línea': {'symbol': '⌒', 'datum': False, 'type': 'surf', 'def': 'Controla la forma de una línea 2D.'},
    'Perfil de una superficie': {'symbol': '⌓', 'datum': False, 'type': 'surf', 'def': 'Controla la forma de una superficie 3D.'},
    'Angularidad': {'symbol': '∠', 'datum': True, 'type': 'surf', 'def': 'Controla el ángulo respecto a un Datum.'},
    'Perpendicularidad': {'symbol': '⟂', 'datum': True, 'type': 'surf', 'def': 'Controla 90° respecto al Datum.'},
    'Paralelismo': {'symbol': '∥', 'datum': True, 'type': 'surf', 'def': 'Controla paralelismo al Datum.'},
    
    # Grupo Eje / Centro / Rotación
    'Redondez': {'symbol': '○', 'datum': False, 'type': 'axis', 'def': 'Controla la circularidad 2D.'},
    'Cilindricidad': {'symbol': '⌭', 'datum': False, 'type': 'axis', 'def': 'Controla la forma cilíndrica 3D.'},
    'Posición': {'symbol': '⌖', 'datum': True, 'type': 'axis', 'def': 'Controla la ubicación exacta.'},
    'Concentricidad': {'symbol': '◎', 'datum': True, 'type': 'axis', 'def': 'Controla el eje mediano.'},
    'Alabeo Circular': {'symbol': '↗', 'datum': True, 'type': 'axis', 'def': 'Controla variación circular al girar.'},
    'Alabeo Total': {'symbol': '⌰', 'datum': True, 'type': 'axis', 'def': 'Controla variación total al girar.'},
}

# ==========================================
# 2. HERRAMIENTAS DE DIBUJO (TRAZOS VISIBLES)
# ==========================================
def draw_rect_trace(fig, x0, y0, x1, y1, color="black", width=2, fill=None):
    """Dibuja rectángulos usando líneas (Scatter) para que siempre se vean"""
    x = [x0, x1, x1, x0, x0]
    y = [y0, y0, y1, y1, y0]
    if fill:
        fig.add_trace(go.Scatter(x=x, y=y, fill="toself", fillcolor=fill, line=dict(color=color, width=width), mode='lines', showlegend=False, hoverinfo='skip'))
    else:
        fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=color, width=width), mode='lines', showlegend=False, hoverinfo='skip'))

def draw_line_trace(fig, x0, y0, x1, y1, color="black", width=2, dash=None, name=None):
    """Dibuja líneas usando Scatter"""
    showleg = True if name else False
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], line=dict(color=color, width=width, dash=dash), mode='lines', showlegend=showleg, name=name, hoverinfo='skip'))

# --- A. PLANO INDIVIDUAL (Modo Análisis) ---
def draw_static_blueprint(feature, tol_val, sym, has_datum, feat_type):
    fig = go.Figure()
    fig.update_layout(
        xaxis=dict(range=[-1, 10], visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(range=[-2, 6], visible=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=500, margin=dict(l=10, r=10, t=40, b=10),
        title=dict(text=f"Plano de Ingeniería: {feature.upper()}", font=dict(color="black", size=20), y=0.95)
    )
    draw_rect_trace(fig, -0.5, -2.5, 9.5, 5.5, width=1) # Marco papel
    draw_rect_trace(fig, 1, 0, 8, 4, width=3) # Pieza
    draw_line_trace(fig, 0.5, 2, 8.5, 2, width=1, dash="longdashdot") # Eje
    draw_line_trace(fig, 1, 1.2, 8, 1.2, width=1, dash="dash") # Oculta
    draw_line_trace(fig, 1, 2.8, 8, 2.8, width=1, dash="dash") # Oculta

    if has_datum: # Datum A
        fig.add_trace(go.Scatter(x=[2, 3, 2.5, 2], y=[0, 0, -0.8, 0], fill="toself", fillcolor="black", line=dict(color="black"), mode='lines', showlegend=False))
        draw_rect_trace(fig, 2.1, -1.8, 2.9, -0.8, width=2)
        fig.add_annotation(x=2.5, y=-1.3, text="<b>A</b>", font=dict(size=18, color="black"), showarrow=False)

    if feat_type == 'surf':
        arrow_x, arrow_y = 6, 4; frame_y = 5.0
    else:
        draw_line_trace(fig, 8, 2.8, 9, 2.8, width=1); draw_line_trace(fig, 8, 1.2, 9, 1.2, width=1)
        fig.add_annotation(x=8.7, y=2, text="Ø 15 ±0.1", ax=0, ay=0, font=dict(size=14, color="black"), xanchor="left") 
        arrow_x, arrow_y = 8.5, 1.5; frame_y = 0.0

    fig.add_annotation(x=arrow_x, y=arrow_y, ax=arrow_x, ay=frame_y, arrowhead=2, arrowsize=1.5, arrowwidth=2, arrowcolor="black")
    
    frame_width = 3 if has_datum else 2
    fx0 = arrow_x - frame_width/2
    
    draw_rect_trace(fig, fx0, frame_y-0.5, fx0+1, frame_y+0.5, width=2) # Símbolo
    fig.add_annotation(x=fx0+0.5, y=frame_y, text=f"<b>{sym}</b>", font=dict(size=24, color="black"), showarrow=False)
    draw_rect_trace(fig, fx0+1, frame_y-0.5, fx0+2, frame_y+0.5, width=2) # Valor
    tol_text = f"Ø {tol_val}" if feat_type == 'axis' else f"{tol_val}"
    fig.add_annotation(x=fx0+1.5, y=frame_y, text=f"<b>{tol_text}</b>", font=dict(size=20, color="black"), showarrow=False)
    
    if has_datum:
        draw_rect_trace(fig, fx0+2, frame_y-0.5, fx0+3, frame_y+0.5, width=2)
        fig.add_annotation(x=fx0+2.5, y=frame_y, text="<b>A</b>", font=dict(size=20, color="black"), showarrow=False)

    return fig

# --- B. PLANO MAESTRO (Modo Constructor) ---
def draw_interactive_blueprint(active_features):
    fig = go.Figure()
    
    # --- PIEZA MAESTRA (DIBUJADA CON LÍNEAS, NO SHAPES) ---
    # Contorno: (1,0) -> (9,0) -> (9,4) -> (7,6) -> (1,6) -> (1,0)
    x_contorno = [1, 9, 9, 7, 1, 1]
    y_contorno = [0, 0, 4, 6, 6, 0]
    fig.add_trace(go.Scatter(x=x_contorno, y=y_contorno, mode="lines", line=dict(color="black", width=3), showlegend=False))
    
    # Agujero y Eje
    draw_line_trace(fig, 1, 3, 9, 3, width=1, dash="longdashdot", name="Eje Central")
    draw_line_trace(fig, 1, 2, 9, 2, width=2, dash="dash", name="Líneas Ocultas")
    draw_line_trace(fig, 1, 4, 9, 4, width=2, dash="dash")
    
    # Arista Visible (para el chaflán)
    draw_line_trace(fig, 1, 0, 1, 6, width=3) 

    # Datum A (Base) - Triángulo y Caja dibujados manualmente
    fig.add_trace(go.Scatter(x=[2,3,2.5,2], y=[0,0,-0.8,0], fill="toself", fillcolor="black", line=dict(color="black"), mode='lines', showlegend=False))
    draw_rect_trace(fig, 2.1, -1.6, 2.9, -0.8, width=2)
    fig.add_annotation(x=2.5, y=-1.2, text="<b>A</b>", showarrow=False, font=dict(size=16, color="black"))

    # Posiciones predefinidas para las cotas
    locs = {
        'Rectitud': (3, 6, 3, 7.5, ''), 'Planicidad': (5, 6, 5, 8.5, ''), 'Posición': (9, 3, 11, 3, 'A B'),
        'Perpendicularidad': (1, 3, -1.5, 3, 'A'), 'Paralelismo': (1, 6, 0, 7.5, 'A'),
        'Cilindricidad': (9, 2, 11, 0, ''), 'Redondez': (9, 4, 11, 4.5, ''), 'Angularidad': (8, 5, 9.5, 6.5, 'A')
    }

    for feat in active_features:
        if feat in locs:
            x_arrow, y_arrow, ax_box, ay_box, dat_txt = locs[feat]
            sym = gdt_data[feat]['symbol']
            
            # Dibujar Cota (Rectángulos manuales)
            w, h = 1.2, 1.0
            # Caja 1: Simbolo
            draw_rect_trace(fig, ax_box, ay_box, ax_box+w, ay_box+h, width=2)
            fig.add_annotation(x=ax_box+w/2, y=ay_box+h/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=18, color="black"))
            # Caja 2: Valor
            draw_rect_trace(fig, ax_box+w, ay_box, ax_box+w*2, ay_box+h, width=2)
            fig.add_annotation(x=ax_box+w*1.5, y=ay_box+h/2, text="<b>0.1</b>", showarrow=False, font=dict(size=14, color="black"))
            # Caja 3: Datum (si aplica)
            if dat_txt:
                draw_rect_trace(fig, ax_box+w*2, ay_box, ax_box+w*3, ay_box+h, width=2)
                fig.add_annotation(x=ax_box+w*2.5, y=ay_box+h/2, text=f"<b>{dat_txt}</b>", showarrow=False, font=dict(size=14, color="black"))
            
            # Flecha conectora
            fig.add_annotation(x=x_arrow, y=y_arrow, ax=ax_box, ay=ay_box, axref="x", ayref="y", arrowhead=2, arrowcolor="black")

    fig.update_layout(
        title=dict(text="Plano de Ingeniería Maestro", font=dict(size=22, color="black")),
        xaxis=dict(range=[-3, 13], visible=False), yaxis=dict(range=[-3, 9], visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        height=700, margin=dict(l=10, r=10, t=50, b=10),
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1, font=dict(color="black")),
        # Marco de la hoja
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))]
    )
    return fig

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.sidebar.title("🎛️ Panel de Control")

# --- SELECTOR DE MODO ---
mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano"])

st.sidebar.markdown("---")

if mode == "🔬 Análisis Individual":
    # ... (Código de menús individuales se mantiene igual) ...
    menu = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu.keys()))
    feat = st.sidebar.selectbox("Característica", menu[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5)
    
    info = gdt_data.get(feat, gdt_data['Rectitud'])
    st.markdown(f"""<div class="gdt-card"><div style="display: flex; align-items: center;"><div class="big-icon" style="flex: 1;">{info['symbol']}</div><div style="flex: 4; padding-left: 20px;"><h3 style="margin:0; color: #0d6efd;">{feat}</h3><p><b>Definición:</b> {info['def']}</p></div></div></div>""", unsafe_allow_html=True)

    st.plotly_chart(draw_static_blueprint(feat, tol, info['symbol'], info['datum'], info['type']), use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
    st.caption("ℹ️ Representación esquemática en un plano de ingeniería estándar.")

elif mode == "📝 Constructor de Plano":
    st.sidebar.info("Seleccione múltiples características para agregarlas al plano:")
    
    # Multiselección
    feats_avail = list(gdt_data.keys())
    # Eliminamos las que no están en el mapa de coordenadas para evitar errores
    feats_avail = [f for f in feats_avail if f in ['Rectitud', 'Planicidad', 'Paralelismo', 'Perpendicularidad', 'Angularidad', 'Perfil de una línea', 'Perfil de una superficie', 'Posición', 'Concentricidad', 'Cilindricidad', 'Redondez', 'Alabeo Circular', 'Alabeo Total']]
    
    selected = st.sidebar.multiselect("Agregar Cotas:", feats_avail, default=['Rectitud', 'Posición'])
    
    st.markdown("## 📐 Plano de Ingeniería Interactivo")
    st.plotly_chart(draw_interactive_blueprint(selected), use_container_width=True)
    
    if selected:
        st.markdown("### 📋 Especificaciones Activas:")
        for f in selected:
            i = gdt_data[f]
            st.info(f"**{f} ({i['symbol']}):** {i['def']}")
