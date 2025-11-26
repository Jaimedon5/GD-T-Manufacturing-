import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PANTALLA COMPLETA ---
st.set_page_config(layout="wide", page_title="Laboratorio Virtual GD&T")

# ==========================================
# 0. ESTILOS CSS (TEMA "HIGH CONTRAST ENGINEERING")
# ==========================================
MAIN_BG = "#D5D5D7"      # Gris Acero
SIDEBAR_BG = "#1E1E1E"   # Negro Carbón
CARD_BG = "#FFFFFF"      # Blanco Puro
TEXT_MAIN = "#000000"    # Negro
TEXT_SIDE = "#FFFFFF"    # Blanco
ACCENT = "#0d6efd"       # Azul Ingeniería

st.markdown(f"""
<style>
    .stApp {{ background-color: {MAIN_BG}; color: {TEXT_MAIN}; }}
    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG}; }}
    [data-testid="stSidebar"] * {{ color: {TEXT_SIDE} !important; }}
    
    /* Tarjetas */
    .gdt-card {{
        background-color: {CARD_BG};
        border-left: 8px solid {ACCENT};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        color: {TEXT_MAIN};
        margin-bottom: 20px;
    }}
    
    /* Iconos */
    .big-icon {{
        font-size: 100px; text-align: center; font-weight: bold;
        color: {TEXT_MAIN}; display: flex; align-items: center; justify-content: center; height: 100%;
    }}
    
    /* Forzar texto negro en área principal */
    .main h1, .main h2, .main h3, .main p, .main li, .main span, .main label {{
        color: {TEXT_MAIN} !important;
    }}
    
    /* Ajustes */
    .block-container {{padding-top: 2rem; padding-bottom: 2rem;}}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. BASE DE DATOS
# ==========================================
gdt_data = {
    'Rectitud': {'symbol': '⏤', 'def': 'Controla la rectitud de una línea superficial.'},
    'Planicidad': {'symbol': '⏥', 'def': 'Controla la planitud de toda la superficie.'},
    'Redondez': {'symbol': '○', 'def': 'Controla la circularidad de la sección transversal.'},
    'Cilindricidad': {'symbol': '⌭', 'def': 'Controla la forma cilíndrica completa.'},
    'Angularidad': {'symbol': '∠', 'def': 'Controla la inclinación de la superficie (Datum A).'},
    'Perpendicularidad': {'symbol': '⟂', 'def': 'Controla los 90° respecto al Datum A.'},
    'Paralelismo': {'symbol': '∥', 'def': 'Controla paralelismo respecto al Datum A.'},
    'Concentricidad': {'symbol': '◎', 'def': 'Controla el eje mediano respecto al Datum.'},
    'Posición': {'symbol': '⌖', 'def': 'Controla la ubicación exacta del agujero.'},
    'Alabeo Circular': {'symbol': '↗', 'def': 'Variación circular al girar.'},
    'Alabeo Total': {'symbol': '⌰', 'def': 'Variación total de superficie al girar.'},
    'Perfil de una línea': {'symbol': '⌒', 'def': 'Controla la forma 2D del perfil.'},
    'Perfil de una superficie': {'symbol': '⌓', 'def': 'Controla la forma 3D de la superficie.'}
}

# ==========================================
# 2. MOTOR DE BLUEPRINT INTERACTIVO (MULTIPLE)
# ==========================================
def draw_interactive_blueprint(active_features):
    """Dibuja una pieza maestra y agrega las cotas seleccionadas"""
    fig = go.Figure()
    
    # --- A. DIBUJO DE LA PIEZA MAESTRA (Bloque con Agujero y Chaflán) ---
    # Contorno
    fig.add_shape(type="path", path="M 1,0 L 9,0 L 9,4 L 7,6 L 1,6 Z", line=dict(color="black", width=3))
    
    # Agujero (Líneas ocultas y eje)
    fig.add_trace(go.Scatter(x=[1,9], y=[3,3], mode="lines", line=dict(color="black", width=1, dash="longdashdot"), name="Eje de Centro"))
    fig.add_trace(go.Scatter(x=[1,9], y=[2,2], mode="lines", line=dict(color="black", width=2, dash="dash"), name="Línea Oculta"))
    fig.add_trace(go.Scatter(x=[1,9], y=[4,4], mode="lines", line=dict(color="black", width=2, dash="dash"), showlegend=False))
    
    # Arista Visible (Línea sólida para referencia)
    fig.add_trace(go.Scatter(x=[1,1], y=[0,6], mode="lines", line=dict(color="black", width=3), name="Arista Visible"))

    # Datums
    # Datum A (Base)
    fig.add_trace(go.Scatter(x=[2,3,2.5,2], y=[0,0,-0.8,0], fill="toself", fillcolor="black", line=dict(color="black"), mode='lines', showlegend=False))
    fig.add_shape(type="rect", x0=2.1, y0=-1.6, x1=2.9, y1=-0.8, line=dict(color="black", width=2))
    fig.add_annotation(x=2.5, y=-1.2, text="<b>A</b>", showarrow=False, font=dict(size=16, color="black"))

    # --- B. LÓGICA DE POSICIONAMIENTO DE COTAS ---
    # Coordenadas predefinidas para que no se encimen
    locs = {
        'Rectitud': {'x': 3, 'y': 6, 'ax': 3, 'ay': 7.5, 'datum': ''},
        'Planicidad': {'x': 5, 'y': 6, 'ax': 5, 'ay': 8.5, 'datum': ''},
        'Paralelismo': {'x': 1, 'y': 6, 'ax': 0, 'ay': 7.5, 'datum': 'A'},
        'Perpendicularidad': {'x': 1, 'y': 3, 'ax': -1.5, 'ay': 3, 'datum': 'A'},
        'Angularidad': {'x': 8, 'y': 5, 'ax': 9.5, 'ay': 6.5, 'datum': 'A'},
        'Perfil de una línea': {'x': 7.5, 'y': 5.5, 'ax': 8.5, 'ay': 7.5, 'datum': ''},
        'Perfil de una superficie': {'x': 8.5, 'y': 4.5, 'ax': 10, 'ay': 5.5, 'datum': ''},
        'Posición': {'x': 9, 'y': 3, 'ax': 11, 'ay': 3, 'datum': 'A B'},
        'Concentricidad': {'x': 9, 'y': 3, 'ax': 11, 'ay': 1.5, 'datum': 'A'},
        'Cilindricidad': {'x': 9, 'y': 2, 'ax': 11, 'ay': 0, 'datum': ''},
        'Redondez': {'x': 9, 'y': 4, 'ax': 11, 'ay': 4.5, 'datum': ''},
        'Alabeo Circular': {'x': 8, 'y': 4, 'ax': 10, 'ay': -1.5, 'datum': 'A-B'},
        'Alabeo Total': {'x': 6, 'y': 2, 'ax': 6, 'ay': -2.5, 'datum': 'A-B'}
    }

    # Dibujar cada característica activa
    for feat in active_features:
        if feat in locs:
            cfg = locs[feat]
            sym = gdt_data[feat]['symbol']
            
            # Dibujar Marco
            draw_gdt_frame(fig, cfg['ax'], cfg['ay'], sym, "0.05", cfg['datum'])
            
            # Dibujar Flecha
            fig.add_annotation(
                x=cfg['x'], y=cfg['y'],
                ax=cfg['ax'], ay=cfg['ay'],
                axref="x", ayref="y",
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="black"
            )

    # Configuración Final
    fig.update_layout(
        title=dict(text="Plano de Ingeniería Maestro", font=dict(size=22, color="black")),
        xaxis=dict(range=[-3, 13], showgrid=False, visible=False),
        yaxis=dict(range=[-3, 9], showgrid=False, visible=False),
        plot_bgcolor="white", paper_bgcolor="white",
        height=700, margin=dict(l=10, r=10, t=50, b=10),
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255,255,255,0.8)", bordercolor="black", borderwidth=1, font=dict(color="black")),
        shapes=[dict(type='rect', xref='paper', yref='paper', x0=0, y0=0, x1=1, y1=1, line=dict(color='black', width=3))]
    )
    return fig

def draw_gdt_frame(fig, x, y, sym, tol, datum):
    """Dibuja el rectangulito GD&T en X, Y"""
    w = 1.2 # Ancho celda
    h = 1.0 # Alto celda
    
    # Celda 1: Simbolo
    fig.add_shape(type="rect", x0=x, y0=y, x1=x+w, y1=y+h, line=dict(color="black", width=2), fillcolor="white")
    fig.add_annotation(x=x+w/2, y=y+h/2, text=f"<b>{sym}</b>", showarrow=False, font=dict(size=18, color="black"))
    
    # Celda 2: Tolerancia
    fig.add_shape(type="rect", x0=x+w, y0=y, x1=x+w*2, y1=y+h, line=dict(color="black", width=2), fillcolor="white")
    fig.add_annotation(x=x+w*1.5, y=y+h/2, text=f"<b>{tol}</b>", showarrow=False, font=dict(size=14, color="black"))
    
    # Celda 3: Datum (Si hay)
    if datum:
        fig.add_shape(type="rect", x0=x+w*2, y0=y, x1=x+w*3, y1=y+h, line=dict(color="black", width=2), fillcolor="white")
        fig.add_annotation(x=x+w*2.5, y=y+h/2, text=f"<b>{datum}</b>", showarrow=False, font=dict(size=14, color="black"))


# ==========================================
# 3. FUNCIONES SIMULACIÓN 3D / REAL (V8)
# ==========================================
# (Reutilizamos las funciones de la V8 para los modos individuales, simplificadas aquí para el bloque maestro)
def get_plot_layout(title, is_3d=True):
    layout = dict(title=dict(text=title, font=dict(size=18, color='black')), paper_bgcolor=MAIN_BG, plot_bgcolor=MAIN_BG, font=dict(color='black'), margin=dict(l=20, r=20, t=50, b=20), height=550)
    if is_3d:
        layout['scene'] = dict(aspectmode='manual', aspectratio=dict(x=1, y=1, z=0.6), xaxis=dict(visible=False, backgroundcolor=MAIN_BG), yaxis=dict(visible=False, backgroundcolor=MAIN_BG), zaxis=dict(visible=True, backgroundcolor=MAIN_BG, gridcolor="#bbb"))
    else:
        layout['xaxis'] = dict(visible=False); layout['yaxis'] = dict(visible=False); layout['plot_bgcolor'] = 'white'
    return layout

def plot_3d_simulation(feature, tol):
    z = np.linspace(0, 10, 30); theta = np.linspace(0, 2*np.pi, 30); tg, zg = np.meshgrid(theta, z)
    fig = go.Figure()
    # Lógica genérica para visualización rápida (se mantiene la lógica detallada V8 si se desea)
    if feature == 'Rectitud':
        fig.add_trace(go.Scatter3d(x=0.3*np.sin(z*0.5), y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje Real'))
        fig.add_trace(go.Surface(x=(tol/2)*np.cos(tg), y=(tol/2)*np.sin(tg), z=zg, opacity=0.3, colorscale=[[0,'orange'],[1,'orange']], showscale=False))
    else: # Fallback genérico para el ejemplo
         fig.add_trace(go.Scatter3d(x=[0,0], y=[0,0], z=[0,10], mode='lines', name='Ejemplo'))
    fig.update_layout(**get_plot_layout(f"Simulación 3D: {feature}"))
    return fig

def plot_real_inspection_anim(feature):
    fig = go.Figure()
    layout = get_plot_layout(f"Montaje: {feature}", is_3d=False)
    layout['updatemenus'] = [dict(type="buttons", showactive=False, x=0.5, y=0.05, xanchor="center", buttons=[dict(label="▶️ Play", method="animate", args=[None])])]
    fig.update_layout(**layout)
    fig.add_shape(type="rect", x0=-1, y0=-1, x1=11, y1=0, fillcolor="#ccc", line=dict(color="black"))
    fig.add_trace(go.Scatter(x=np.linspace(0,10,50), y=1.5+0.2*np.sin(np.linspace(0,10,50)), mode='lines', line=dict(color='blue', width=4), name='Pieza'))
    fig.add_trace(go.Scatter(x=[5], y=[4.5], mode='markers+text', marker=dict(size=40, color='white', line=dict(color='black', width=2)), text=['0']))
    return fig

# ==========================================
# 4. INTERFAZ DE USUARIO
# ==========================================
st.sidebar.title("🎛️ Controles GD&T")
st.sidebar.markdown("---")

# MODO DE VISTA PRINCIPAL
mode = st.sidebar.radio("Modo de Trabajo:", ["🔬 Análisis Individual", "📝 Constructor de Plano (Blueprint)"])

if mode == "🔬 Análisis Individual":
    menu_dict = {'1. Forma': ['Rectitud', 'Planicidad', 'Redondez', 'Cilindricidad'], '2. Orientación': ['Angularidad', 'Perpendicularidad', 'Paralelismo'], '3. Perfil': ['Perfil de una línea', 'Perfil de una superficie'], '4. Control': ['Alabeo Circular', 'Alabeo Total'], '5. Posición': ['Posición', 'Concentricidad']}
    cat = st.sidebar.selectbox("Categoría", list(menu_dict.keys()))
    feat = st.sidebar.selectbox("Característica", menu_dict[cat])
    tol = st.sidebar.slider("Tolerancia (mm)", 0.1, 2.0, 0.5, 0.1)
    
    view_mode = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real"])
    
    # Renderizado Individual
    info = gdt_data.get(feat, gdt_data['Rectitud'])
    st.markdown(f"""<div class="gdt-card"><div style="display: flex; align-items: center;"><div class="big-icon" style="flex: 1;">{info['symbol']}</div><div style="flex: 4; padding-left: 20px;"><h3 style="margin:0; color: #0d6efd;">{feat}</h3><p><b>Definición:</b> {info['def']}</p></div></div></div>""", unsafe_allow_html=True)
    
    if view_mode == "Simulación 3D":
        st.plotly_chart(plot_3d_simulation(feat, tol), use_container_width=True)
    else:
        st.plotly_chart(plot_real_inspection_anim(feat), use_container_width=True)

elif mode == "📝 Constructor de Plano (Blueprint)":
    st.sidebar.markdown("---")
    st.sidebar.info("Seleccione las características que desea agregar al plano maestro.")
    
    # Multiselección
    all_feats = list(gdt_data.keys())
    selected = st.sidebar.multiselect("Agregar Cotas GD&T:", all_feats, default=['Rectitud'])
    
    st.markdown("## 📐 Plano de Ingeniería Interactivo")
    st.markdown("Agregue múltiples características para ver cómo se acotan en conjunto.")
    
    fig_blue = draw_interactive_blueprint(selected)
    st.plotly_chart(fig_blue, use_container_width=True)
    
    # Lista de descripciones activas
    if selected:
        st.markdown("### 📋 Especificaciones Activas:")
        for f in selected:
            info = gdt_data[f]
            st.info(f"**{f} ({info['symbol']}):** {info['def']}")
