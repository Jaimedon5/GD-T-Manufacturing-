## (Línea eliminada: remanente de código viejo que causaba error de sintaxis)
import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio
import streamlit.components.v1 as components
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ===================== CONFIGURACIÓN GENERAL =====================
st.set_page_config(layout="wide", page_title="GD&T Master Lab - Nueva Versión")

# ===================== ESTILOS Y LEYENDAS =====================
st.markdown("""<style>
.symbol-box{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:120px;width:120px;margin:0 auto;margin-top:18px;margin-bottom:18px;padding:8px;overflow:hidden;}
.symbol-box img,.symbol-box svg{max-width:100%;max-height:100%;height:auto;width:auto;display:block;}
.legend-stack{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}
.legend-box,.pedagogic-box{margin-bottom:0!important;}
.stApp{background-color:#e5e7eb!important;color:#222!important;}
[data-testid="stSidebar"]{background-color:#23272e!important;}
[data-testid="stSidebar"] *{color:#f3f4f6!important;}
.legend-box{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}
.info-card{background:#f3f4f6;border-left:8px solid #004B87;padding:16px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:200px;overflow:hidden;display:flex;gap:16px;}
.pedagogic-box{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:'Courier New',monospace;margin-top:15px;}
.category-label{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}
h1,h2,h3,h4,h5,h6{color:#23272e!important;}
</style>""", unsafe_allow_html=True)
ST_SYMBOL_SIZE = 200
st.markdown(f"""<style>.symbol-box{{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:{ST_SYMBOL_SIZE}px;width:{ST_SYMBOL_SIZE}px;margin:0 auto;margin-top:18px;margin-bottom:18px;}}.legend-stack{{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}}.legend-box,.pedagogic-box{{margin-bottom:0!important;}}.stApp{{background-color:#e5e7eb!important;color:#222!important;}}[data-testid=\"stSidebar\"]{{background-color:#23272e!important;}}[data-testid=\"stSidebar\"] *{{color:#f3f4f6!important;}}.legend-box{{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}}.info-card{{background:#f3f4f6;border-left:8px solid #004B87;padding:12px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:{ST_SYMBOL_SIZE}px;overflow:auto;display:flex;align-items:flex-start;}}.info-card table{{line-height:1.3;}}.pedagogic-box{{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:\'Courier New\',monospace;margin-top:15px;}}.category-label{{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}}h1,h2,h3,h4,h5,h6{{color:#23272e!important;}}</style>""", unsafe_allow_html=True)

# ===================== BASE DE DATOS DE CARACTERÍSTICAS =====================
# Incluye puntos clave y diferenciadores pedagógicos
def get_gd_data():
    return {
        'Rectitud': {
            'symbol': '⏤',
            'def': 'Condición donde un elemento lineal es una línea recta.',
            'zona_tol': 'Líneas paralelas, dónde debe estar el elemento de superficie.',
            'app': 'Vástagos, ejes largos, rieles.',
            'medicion': 'comparador o proyector de perfiles.',
            'key_points': [
                'Solo controla la línea central o generatriz, no la forma completa.',
                'No requiere datum.'
            ],
            'diff': 'No confundir con planicidad: la rectitud es 1D, la planicidad es 2D.',
            'pedagogic': 'Rectitud evalúa si un eje o borde es perfectamente recto, útil para piezas largas.',
            'legend': 'Línea azul: eje real. Cilindro naranja: zona de tolerancia.',
        },
        'Planicidad': {
            'symbol': '⏥',
            'def': 'Todos los puntos de una superficie están en un solo plano.',
            'app': 'Mesas de granito, culatas, sellos.',
            'key_points': [
                'Controla toda la superficie, no solo una línea.',
                'No requiere datum.',
                'Se mide con palpador o láser.'
            ],
            'diff': 'No confundir con rectitud: planicidad es para superficies, rectitud para líneas.',
            'pedagogic': 'Planicidad asegura que una superficie no tenga picos o valles fuera de tolerancia.',
            'legend': 'Superficie verde: real. Planos rojos: límites de tolerancia.'
        },
        # ...agrega el resto de características siguiendo el PDF...
    }

GD_DATA = get_gd_data()

# ===================== FUNCIONES DE LEYENDA Y EXPLICACIÓN PEDAGÓGICA =====================
def show_legend(feature, view="Simulación 3D"):
    info = GD_DATA[feature]
    if view == "Montaje Real":
        legend_text = "Línea azul: eje real. Círculo amarillo: comparador dial con aguja cian.<br>Punto rojo: posición del palpador. Escala blanca (derecha): lectura amplificada de desviación."
        diff_text = "En montaje real ves el <em>instrumento de medición</em> (comparador) recorriendo la pieza, replicando exactamente lo que ocurre en un laboratorio de metrología."
    elif view == "Zona de Tolerancia":
        legend_text = "Líneas naranjas: límites superior e inferior de la zona de tolerancia.<br>Línea azul: eje real ideal. Área gris: zona permitida para el eje."
        diff_text = "La zona de tolerancia es un <em>espacio geométrico</em> definido por límites paralelos. Si el eje permanece dentro, cumple rectitud."
    elif view == "Plano Técnico Real":
        legend_text = "Líneas continuas negras: contorno de la pieza.<br>Líneas punteadas azules: líneas de referencia y acotación.<br>Texto azul: dimensiones y tolerancias GD&T."
        diff_text = "Un plano técnico <em>real</em> incluye cotas, líneas de referencia, símbolos GD&T y anotaciones, como en documentación industrial estándar."
    else:
        legend_text = info['legend']
        diff_text = info['diff']
    st.markdown(f"""
    <div class="legend-box">
        <b>Leyenda visual:</b> {legend_text}<br>
        <b>Diferenciador clave:</b> {diff_text}
    </div>
    """, unsafe_allow_html=True)
    # Asegura que la info-card tenga altura fija y el .sim-box la misma apariencia
    try:
        current_box = ST_SYMBOL_SIZE
    except NameError:
        current_box = 200
    st.markdown(f"""<style>
    .symbol-box{{background:#fff;border:2.5px solid #23272e;border-radius:8px;display:flex;align-items:center;justify-content:center;height:{current_box}px;width:{current_box}px;margin:0 auto;margin-top:18px;margin-bottom:18px;padding:12px;overflow:hidden;}}
    .symbol-box img,.symbol-box svg{{max-width:100%;max-height:100%;height:auto;width:auto;display:block;}}
    .legend-stack{{display:flex;flex-direction:column;gap:18px;margin-top:0;margin-bottom:0;}}
    .legend-box,.pedagogic-box{{margin-bottom:0!important;}}
    .stApp{{background-color:#e5e7eb!important;color:#222!important;}}
    [data-testid="stSidebar"]{{background-color:#23272e!important;}}
    [data-testid="stSidebar"] *{{color:#f3f4f6!important;}}
    .legend-box{{background:#f3f4f6;border-left:6px solid #1976d2;padding:16px;border-radius:8px;margin-bottom:18px;font-size:1.05em;color:#23272e;}}
    .info-card{{background:#f3f4f6;border-left:8px solid #004B87;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.08);margin-bottom:20px;color:#23272e;height:200px;overflow:auto;}}
    .pedagogic-box{{background:#e0e7ef;border:1px solid #2196f3;border-left:6px solid #2196f3;padding:15px;border-radius:4px;color:#0d47a1;font-family:'Courier New',monospace;margin-top:15px;}}
    .category-label{{font-weight:bold;color:#004B87;background:#e0e7ef;border-radius:6px;padding:2px 8px;margin-right:8px;}}
    h1,h2,h3,h4,h5,h6{{color:#23272e!important;}}
    .sim-box{{border:2.5px solid #23272e;border-radius:8px;padding:16px;background:#fff;margin:0;box-shadow:0 2px 4px rgba(0,0,0,0.08);display:block !important;}}
    </style>""", unsafe_allow_html=True)
def show_info_card(feature):
    info = GD_DATA[feature]
    # Construir puntos clave como texto simple
    puntos_html = '<br>'.join([f'• {pt}' for pt in info['key_points']])
    # HTML en formato tabla: fila 1 título, fila 2 encabezados, fila 3 datos
    html = f"""
    <div class="info-card">
        <table style="width:100%;border-collapse:collapse;font-size:0.85em;">
            <tr>
                <th colspan="6" style="text-align:left;padding:10px;font-size:1.4em;font-weight:bold;color:#004B87;border-bottom:2px solid #004B87;">{feature}</th>
            </tr>
            <tr style="background:#e0e7ef;">
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Definición</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Zona de tolerancia</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Aplicación</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Medición</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;border-right:1px solid #ccc;">Puntos clave para identificar</th>
                <th style="padding:6px;text-align:left;font-size:0.9em;">¿Cómo NO confundirlo?</th>
            </tr>
            <tr>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info['def']}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info.get('zona_tol', 'N/A')}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info['app']}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{info.get('medicion', 'N/A')}</td>
                <td style="padding:8px;vertical-align:top;border-right:1px solid #ddd;">{puntos_html}</td>
                <td style="padding:8px;vertical-align:top;color:#1976d2;">{info['diff']}</td>
            </tr>
        </table>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def get_symbol_image_path(feature):
    """Devuelve la ruta relativa a la imagen del símbolo para la característica.
    Busca archivos en `Docs/simbolo_<slug>.png`. Si no existe, devuelve None.
    """
    slug = feature.replace(' ', '_').lower()
    import os
    # Buscar en varios formatos: png, svg, jpg, jpeg
    for ext in ('png', 'svg', 'jpg', 'jpeg'):
        candidate = os.path.join('Docs', f'simbolo_{slug}.{ext}')
        if os.path.exists(candidate):
            return candidate.replace('\\', '/')
    return None

# ===================== SIMULACIONES =====================
def plot_3d_rectitud(tol):
    z = np.linspace(0, 10, 35)
    x_r = 0.4 * np.sin(z * 0.5)
    fig = go.Figure()
    fig.add_trace(go.Scatter3d(x=x_r, y=np.zeros_like(z), z=z, mode='lines', line=dict(color='blue', width=10), name='Eje real'))
    theta = np.linspace(0, 2 * np.pi, 35)
    tg, zg = np.meshgrid(theta, z)
    fig.add_trace(go.Surface(x=tol * np.cos(tg), y=tol * np.sin(tg), z=zg, opacity=0.3, colorscale='Oranges', name='Zona de tolerancia', showscale=True, colorbar=dict(tickfont=dict(color='#fff'))))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0), height=500,
        scene=dict(
            xaxis=dict(visible=False, backgroundcolor='#4a5568'),
            yaxis=dict(visible=False, backgroundcolor='#4a5568'),
            zaxis=dict(visible=True, backgroundcolor='#4a5568', gridcolor='#94a3b8', color='#fff'),
            bgcolor='#4a5568'
        ),
        paper_bgcolor='#4a5568', plot_bgcolor='#4a5568', font=dict(color='#fff')
    )
    return fig

def plot_real_rectitud():
    x = np.linspace(0, 10, 100)
    y = 0.4 * np.sin(x * 0.5)
    palpador_h = 0.8
    dial_radius = 0.35
    def comparator_shapes(cx, cy):
        body_top = cy + palpador_h + 0.15
        dial_center_y = body_top + 0.45
        angle_deg = (cy / 0.4) * 90
        angle_rad = np.radians(90 + angle_deg)
        needle_len = dial_radius - 0.1
        needle_x = cx + needle_len * np.cos(angle_rad)
        needle_y = dial_center_y + needle_len * np.sin(angle_rad)
        shapes = [
            dict(type='rect', x0=cx-0.06, x1=cx+0.06, y0=cy, y1=cy+palpador_h, fillcolor='#64748b', line=dict(color='#475569', width=1)),
            dict(type='rect', x0=cx-0.15, x1=cx+0.15, y0=cy+palpador_h, y1=body_top, fillcolor='#71717a', line=dict(color='#52525b', width=1)),
            dict(type='circle', x0=cx-dial_radius-0.05, x1=cx+dial_radius+0.05, y0=dial_center_y-dial_radius-0.05, y1=dial_center_y+dial_radius+0.05, fillcolor='#eab308', line=dict(color='#a16207', width=2)),
            dict(type='circle', x0=cx-dial_radius, x1=cx+dial_radius, y0=dial_center_y-dial_radius, y1=dial_center_y+dial_radius, fillcolor='#fef9c3', line=dict(color='#222', width=1))
        ]
        for ang in range(0, 360, 30):
            a = np.radians(ang)
            mx = cx + (dial_radius - 0.08) * np.cos(a)
            my = dial_center_y + (dial_radius - 0.08) * np.sin(a)
            shapes.append(dict(type='circle', x0=mx-0.02, x1=mx+0.02, y0=my-0.02, y1=my+0.02, fillcolor='#222', line=dict(width=0)))
        shapes.append(dict(type='line', x0=cx, x1=needle_x, y0=dial_center_y, y1=needle_y, line=dict(color='#22d3ee', width=3)))
        shapes.append(dict(type='circle', x0=cx-0.04, x1=cx+0.04, y0=dial_center_y-0.04, y1=dial_center_y+0.04, fillcolor='#374151', line=dict(width=0)))
        shapes.append(dict(type='rect', x0=cx-0.08, x1=cx+0.08, y0=dial_center_y+dial_radius+0.05, y1=dial_center_y+dial_radius+0.15, fillcolor='#52525b', line=dict(color='#3f3f46', width=1)))
        return shapes
    base_shapes = []
    for gy in np.arange(-0.8, 2.4, 0.2):
        base_shapes.append(dict(type='line', x0=-0.5, x1=12, y0=gy, y1=gy, line=dict(color='rgba(148,163,184,0.15)', width=1), layer='below'))
    for gx in np.arange(0, 12, 1):
        base_shapes.append(dict(type='line', x0=gx, x1=gx, y0=-0.8, y1=2.3, line=dict(color='rgba(148,163,184,0.15)', width=1), layer='below'))
    base_shapes.append(dict(type='rect', x0=0, x1=10, y0=-0.8, y1=-0.65, fillcolor='#94a3b8', line=dict(color='#cbd5e1', width=1), layer='below'))
    base_shapes.append(dict(type='rect', x0=10.8, x1=11.2, y0=-0.5, y1=0.5, fillcolor='#fff', line=dict(color='#222', width=2)))
    scale_values = np.linspace(-0.5, 0.5, 11)
    for tick in scale_values:
        base_shapes.append(dict(type='line', x0=10.8, x1=11.0, y0=tick, y1=tick, line=dict(color='#222', width=2)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line=dict(color='#60a5fa', width=6), showlegend=False))
    fig.add_trace(go.Scatter(x=[x[0]], y=[y[0]], mode='markers', marker=dict(size=14, color='#ef4444', symbol='circle', line=dict(color='#991b1b', width=1)), showlegend=False))
    fig.add_trace(go.Scatter(x=[11.0], y=[y[0]], mode='markers', marker=dict(size=12, color='#10b981', symbol='triangle-right', line=dict(color='#059669', width=1)), showlegend=False))
    fig.update_layout(shapes=base_shapes + comparator_shapes(x[0], y[0]))
    frames = []
    for idx in range(0, len(x), 2):
        shapes_frame = base_shapes + comparator_shapes(x[idx], y[idx])
        frame_data = [
            go.Scatter(x=x, y=y, mode='lines', line=dict(color='#60a5fa', width=6)),
            go.Scatter(x=[x[idx]], y=[y[idx]], mode='markers', marker=dict(size=14, color='#ef4444', symbol='circle', line=dict(color='#991b1b', width=1))),
            go.Scatter(x=[11.0], y=[y[idx]], mode='markers', marker=dict(size=12, color='#10b981', symbol='triangle-right', line=dict(color='#059669', width=1)))
        ]
        frames.append(go.Frame(data=frame_data, layout=dict(shapes=shapes_frame), name=str(idx)))
    fig.frames = frames
    fig.update_layout(
        margin=dict(l=0, r=10, t=40, b=0), height=400,
        xaxis=dict(range=[-0.5, 12], visible=False),
        yaxis=dict(range=[-1.0, 2.5], visible=False),
        paper_bgcolor='#4a5568', plot_bgcolor='#4a5568', font=dict(color='#fff'), showlegend=False,
        updatemenus=[dict(
            type='buttons', showactive=False,
            direction='left',
            x=0.02, y=0.94, xanchor='left', yanchor='top',
            pad=dict(r=6, t=0, b=0, l=0),
            buttons=[
                dict(label='⏮️ Inicio', method='animate', args=[[str(0)], dict(mode='immediate', frame=dict(duration=0, redraw=True), transition=dict(duration=0))]),
                dict(label='▶️ Reproducir', method='animate', args=[None, dict(frame=dict(duration=80, redraw=True), fromcurrent=True, mode='immediate')]),
                dict(label='⏸️ Pausa', method='animate', args=[[None], dict(mode='immediate', frame=dict(duration=0, redraw=False))])
            ],
            bgcolor='#fbbf24', bordercolor='#fff', borderwidth=2, font=dict(size=13)
        )]
    )
    # Números de la escala (coordenadas del gráfico, fuera a la derecha)
    for tick in scale_values:
        fig.add_annotation(x=11.35, y=float(tick), xref='x', yref='y',
                           text=f"{tick:.1f}", showarrow=False,
                           font=dict(size=10, color='#fff'),
                           xanchor='left', yanchor='middle')
    return fig

def plot_blueprint_rectitud(tol):
    fig = go.Figure()
    x = np.linspace(0, 10, 2)
    y1 = tol/2 * np.ones_like(x)
    y2 = -tol/2 * np.ones_like(x)
    
    # Shapes base: cuadrícula tenue + escala lateral derecha
    shapes = []
    # Cuadrícula horizontal
    for gy in np.arange(-1.0, 1.2, 0.2):
        shapes.append(dict(type='line', x0=-0.5, x1=10.5, y0=gy, y1=gy,
                          line=dict(color='rgba(148,163,184,0.15)', width=1), layer='below'))
    # Cuadrícula vertical
    for gx in np.arange(0, 11, 1):
        shapes.append(dict(type='line', x0=gx, x1=gx, y0=-1.0, y1=1.0,
                          line=dict(color='rgba(148,163,184,0.15)', width=1), layer='below'))
    # Área de tolerancia (zona gris)
    shapes.append(dict(type='rect', x0=0, x1=10, y0=-tol/2, y1=tol/2,
                      fillcolor='rgba(209,213,219,0.3)', line=dict(color='#94a3b8', width=1), layer='below'))
    # Escala vertical derecha
    shapes.append(dict(type='rect', x0=10.8, x1=11.2, y0=-0.5, y1=0.5,
                      fillcolor='#fff', line=dict(color='#222', width=2)))
    scale_values = np.linspace(-0.5, 0.5, 11)
    for tick in scale_values:
        shapes.append(dict(type='line', x0=10.8, x1=11.0, y0=tick, y1=tick,
                          line=dict(color='#222', width=2)))
    
    # Líneas de límite de tolerancia
    fig.add_trace(go.Scatter(x=x, y=y1, mode='lines', line=dict(color='#ff9800', width=5), name='Límite sup.', showlegend=False))
    fig.add_trace(go.Scatter(x=x, y=y2, mode='lines', line=dict(color='#ff9800', width=5), name='Límite inf.', showlegend=False))
    # Eje real ideal
    fig.add_trace(go.Scatter(x=x, y=np.zeros_like(x), mode='lines', line=dict(color='#1976d2', width=4), name='Eje real', showlegend=False))
    
    fig.update_layout(
        shapes=shapes,
        margin=dict(l=0, r=10, t=10, b=0), height=350,
        xaxis=dict(range=[-0.5, 11.5], visible=False),
        yaxis=dict(range=[-1.0, 1.0], visible=False),
        paper_bgcolor='#4a5568', plot_bgcolor='#4a5568',
        font=dict(color='#fff'), showlegend=False
    )
    # Números de escala
    for tick in scale_values:
        fig.add_annotation(x=11.35, y=float(tick), xref='x', yref='y',
                          text=f"{tick:.1f}", showarrow=False,
                          font=dict(size=10, color='#fff'),
                          xanchor='left', yanchor='middle')
    return fig

def plot_technical_drawing_rectitud(tol):
    """Plano técnico usando matplotlib (adaptado de tolerancias.txt)."""
    # Configuración estética
    ANCHO_PIEZA = 40
    ALTO_PIEZA = 15
    C_ESTATICO = 'black'
    C_DINAMICO_NUM = '#D00000'
    C_ZONA = '#e6007e'
    C_EXPLICACION = '#009fe3'
    C_FONDO_MARCO = 'white'
    C_REFERENCIA = '#1e40af'  # Azul para referencias numeradas
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(-25, ANCHO_PIEZA + 35)
    ax.set_ylim(-35, ALTO_PIEZA + 15)
    ax.set_aspect('equal')
    ax.axis('off')
    
    y_sup = ALTO_PIEZA / 2
    y_inf = -ALTO_PIEZA / 2
    
    # Pieza rectangular
    ax.add_patch(patches.Rectangle((0, y_inf), ANCHO_PIEZA, ALTO_PIEZA, 
                                   lw=2, ec=C_ESTATICO, fc='none'))
    # Eje central
    ax.plot([-5, ANCHO_PIEZA + 5], [0, 0], color=C_ESTATICO, ls='--', lw=1)
    
    # ② Símbolo de la característica geométrica (símbolo de rectitud en el FCF)
    # CUADRO DE CONTROL DE TOLERANCIA (GD&T)
    x_marco = ANCHO_PIEZA - 5
    y_marco = y_inf - 25
    h_marco = 8
    w_simbolo = 8
    w_valor = 14
    
    ax.add_patch(patches.Rectangle((x_marco, y_marco), w_simbolo, h_marco, 
                                   fc=C_FONDO_MARCO, ec=C_ESTATICO, lw=2))
    ax.text(x_marco + w_simbolo/2, y_marco + h_marco/2, '—', 
            fontsize=20, va='center', ha='center', color=C_ESTATICO)
    
    # Referencia ③ arriba del símbolo (ahora es el 3)
    ax.add_patch(patches.Circle((x_marco + w_simbolo/2, y_marco + h_marco + 5), 2.2, fc='white', ec=C_REFERENCIA, lw=2.5))
    ax.text(x_marco + w_simbolo/2, y_marco + h_marco + 5, '3', fontsize=20, color=C_REFERENCIA, ha='center', va='center', fontweight='bold')
    
    # ③ Símbolo Ø (diámetro)
    # COTA DIMENSIONAL (IZQUIERDA)
    x_cota = -12
    ax.plot([0, x_cota], [y_sup, y_sup], color=C_ESTATICO, lw=0.8)
    ax.plot([0, x_cota], [y_inf, y_inf], color=C_ESTATICO, lw=0.8)
    ax.annotate('', xy=(x_cota, y_sup), xytext=(x_cota, y_inf),
                arrowprops=dict(arrowstyle='<->', color=C_ESTATICO, lw=1.5))
    ax.text(x_cota, y_sup + 2, 'Ø 10 ±', fontsize=22, color=C_ESTATICO, ha='right')
    ax.text(x_cota + 1, y_sup + 2, f'{tol*2:.1f}', 
            fontsize=24, color=C_DINAMICO_NUM, ha='left', fontweight='bold')
    
    # Referencia ① arriba del texto Ø10+-
    ax.add_patch(patches.Circle((x_cota - 1, y_sup + 7), 2.2, fc='white', ec=C_REFERENCIA, lw=2.5))
    ax.text(x_cota - 1, y_sup + 7, '1', fontsize=20, color=C_REFERENCIA, ha='center', va='center', fontweight='bold')
    
    # ④ Valor de tolerancia en el FCF
    ax.add_patch(patches.Rectangle((x_marco + w_simbolo, y_marco), w_valor, h_marco, 
                                   fc=C_FONDO_MARCO, ec=C_ESTATICO, lw=2))
    ax.text(x_marco + w_simbolo + w_valor/2, y_marco + h_marco/2, 
            f'{tol:.1f}', 
            fontsize=24, va='center', ha='center', color=C_DINAMICO_NUM, fontweight='bold')
    
    # Referencia ④ arriba del valor
    ax.add_patch(patches.Circle((x_marco + w_simbolo + w_valor/2, y_marco + h_marco + 5), 2.2, fc='white', ec=C_REFERENCIA, lw=2.5))
    ax.text(x_marco + w_simbolo + w_valor/2, y_marco + h_marco + 5, '4', fontsize=20, color=C_REFERENCIA, ha='center', va='center', fontweight='bold')
    
    # LÍNEA QUEBRADA (LEADER LINE)
    start_x, start_y = x_marco, y_marco + h_marco/2
    elbow_x, elbow_y = x_marco - 10, start_y
    end_x, end_y = x_marco - 25, y_inf
    ax.plot([start_x, elbow_x, end_x], [start_y, elbow_y, end_y], color=C_ESTATICO, lw=1.5)
    ax.annotate('', xy=(end_x, end_y), xytext=(elbow_x, elbow_y),
                arrowprops=dict(arrowstyle='->', color=C_ESTATICO, lw=1.5))
    
    # Referencia ② en la línea de líder (ahora es el 2)
    ax.add_patch(patches.Circle((elbow_x - 6, elbow_y + 3), 2.2, fc='white', ec=C_REFERENCIA, lw=2.5))
    ax.text(elbow_x - 6, elbow_y + 3, '2', fontsize=20, color=C_REFERENCIA, ha='center', va='center', fontweight='bold')
    
    # ZONA DE TOLERANCIA (LÍNEAS ROSAS)
    offset = tol * 10
    ax.plot([-2, ANCHO_PIEZA+2], [y_inf + offset, y_inf + offset], 
            color=C_ZONA, ls=':', lw=2.5)
    ax.plot([-2, ANCHO_PIEZA+2], [y_inf - offset, y_inf - offset], 
            color=C_ZONA, ls=':', lw=2.5)
    
    # EXPLICACIÓN LATERAL (AZUL)
    x_azul = ANCHO_PIEZA + 15
    ax.annotate('', xy=(x_azul, y_inf + offset), xytext=(x_azul, y_inf + offset + 4),
                arrowprops=dict(arrowstyle='->', color=C_EXPLICACION, lw=1.5))
    ax.annotate('', xy=(x_azul, y_inf - offset), xytext=(x_azul, y_inf - offset - 4),
                arrowprops=dict(arrowstyle='->', color=C_EXPLICACION, lw=1.5))
    ax.text(x_azul + 3, y_inf, f'{tol:.1f} zona de tolerancia', 
            color=C_EXPLICACION, fontsize=14, va='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

    # Contorno principal de la pieza (rectángulo sólido - vista frontal del eje)
    fig.add_shape(type='rect', x0=2, x1=10, y0=3.5, y1=5.5, 
                  fillcolor='#f8f9fa', line=dict(color='#000', width=2.5))
    
    # Línea de eje central (dash-dot pattern, más delgada)
    for i in range(5):
        # Segmentos cortos punteados simulando línea de centro
        x_start = 0.5 + i * 2.5
        if i % 2 == 0:
            fig.add_shape(type='line', x0=x_start, x1=x_start+1, y0=4.5, y1=4.5,
                         line=dict(color='#000', width=1, dash='dot'))
        else:
            fig.add_shape(type='line', x0=x_start, x1=x_start+1, y0=4.5, y1=4.5,
                         line=dict(color='#000', width=1))
    
    # ========== COTAS DIMENSIONALES ==========
    # Cota horizontal principal (longitud del eje: 80.00 mm)
    # Líneas de extensión verticales desde los extremos de la pieza
    fig.add_shape(type='line', x0=2, x1=2, y0=5.5, y1=6.2,
                  line=dict(color='#000', width=1))
    fig.add_shape(type='line', x0=10, x1=10, y0=5.5, y1=6.2,
                  line=dict(color='#000', width=1))
    # Línea de cota horizontal
    fig.add_shape(type='line', x0=2, x1=10, y0=6.0, y1=6.0,
                  line=dict(color='#000', width=1.5))
    # Flechas de cota en los extremos
    fig.add_annotation(x=2, y=6.0, ax=2.35, ay=6.0, showarrow=True,
                       arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor='#000')
    fig.add_annotation(x=10, y=6.0, ax=9.65, ay=6.0, showarrow=True,
                       arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor='#000')
    # Texto de la cota
    fig.add_annotation(x=6, y=6.3, text="80.00", showarrow=False,
                       font=dict(size=13, color='#000', family='Arial', weight='bold'))
    
    # Cota vertical (diámetro del eje: Ø20±0.2)
    # Líneas de extensión horizontales
    fig.add_shape(type='line', x0=10, x1=10.7, y0=3.5, y1=3.5,
                  line=dict(color='#000', width=1))
    fig.add_shape(type='line', x0=10, x1=10.7, y0=5.5, y1=5.5,
                  line=dict(color='#000', width=1))
    # Línea de cota vertical
    fig.add_shape(type='line', x0=10.5, x1=10.5, y0=3.5, y1=5.5,
                  line=dict(color='#000', width=1.5))
    # Flechas
    fig.add_annotation(x=10.5, y=3.5, ax=10.5, ay=3.85, showarrow=True,
                       arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor='#000')
    fig.add_annotation(x=10.5, y=5.5, ax=10.5, ay=5.15, showarrow=True,
                       arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor='#000')
    # Texto de cota con tolerancia dimensional
    fig.add_annotation(x=11.2, y=4.5, text="Ø20±0.2", showarrow=False,
                       font=dict(size=12, color='#000', family='Arial', weight='bold'),
                       textangle=-90)
    
    # ========== MARCO DE CONTROL DE CARACTERÍSTICA (Feature Control Frame) ==========
    # Rectángulo principal del marco
    frame_x0, frame_y0 = 3.5, 2.3
    frame_width = 3.0
    frame_height = 0.5
    fig.add_shape(type='rect', x0=frame_x0, x1=frame_x0+frame_width, 
                  y0=frame_y0, y1=frame_y0+frame_height,
                  fillcolor='#fff', line=dict(color='#000', width=2.5))
    
    # Divisores verticales del marco (3 compartimentos)
    fig.add_shape(type='line', x0=frame_x0+0.7, x1=frame_x0+0.7, 
                  y0=frame_y0, y1=frame_y0+frame_height,
                  line=dict(color='#000', width=2.5))
    fig.add_shape(type='line', x0=frame_x0+1.5, x1=frame_x0+1.5, 
                  y0=frame_y0, y1=frame_y0+frame_height,
                  line=dict(color='#000', width=2.5))
    
    # Compartimento 1: Símbolo de característica geométrica (rectitud = línea horizontal)
    fig.add_shape(type='line', x0=frame_x0+0.15, x1=frame_x0+0.55, 
                  y0=frame_y0+0.25, y1=frame_y0+0.25,
                  line=dict(color='#000', width=3))
    
    # Compartimento 2: Zona de tolerancia (símbolo Ø + valor)
    fig.add_annotation(x=frame_x0+1.1, y=frame_y0+0.25, text=f"Ø {tol}", 
                       showarrow=False, font=dict(size=12, color='#000', family='Arial'),
                       xanchor='center', yanchor='middle')
    
    # Compartimento 3: Datum de referencia (ejemplo: A)
    fig.add_annotation(x=frame_x0+2.25, y=frame_y0+0.25, text="A", 
                       showarrow=False, font=dict(size=13, color='#000', family='Arial', weight='bold'),
                       xanchor='center', yanchor='middle')
    
    # Flecha líder desde el marco hacia la superficie controlada
    fig.add_annotation(x=5, y=2.3, ax=5, ay=3.5, showarrow=True,
                       arrowhead=1, arrowsize=1.3, arrowwidth=2.5, arrowcolor='#000')

    # ========== CALLOUTS NUMERADOS (1-8) REFERENCIANDO ELEMENTOS DEL FCF ==========
    callout_style = dict(font=dict(size=12, color='#2563eb', family='Arial', weight='bold'),
                         arrowcolor='#2563eb', arrowwidth=2, arrowhead=2)
    # 1: Flecha guía
    fig.add_annotation(x=5.0, y=2.9, text="1", showarrow=True, ax=4.3, ay=3.2, **callout_style)
    # 2: Símbolo geométrico (rectitud)
    fig.add_annotation(x=frame_x0+0.35, y=frame_y0+0.6, text="2", showarrow=True, ax=frame_x0+0.35, ay=frame_y0+0.9, **callout_style)
    # 3: Símbolo de diámetro
    fig.add_annotation(x=frame_x0+1.05, y=frame_y0+0.6, text="3", showarrow=True, ax=frame_x0+1.05, ay=frame_y0+0.9, **callout_style)
    # 4: Tolerancia (valor)
    fig.add_annotation(x=frame_x0+1.4, y=frame_y0+0.25, text="4", showarrow=True, ax=frame_x0+1.4, ay=frame_y0+0.6, **callout_style)
    # 5: Modificador (ej: M) — placeholder
    fig.add_annotation(x=frame_x0+1.9, y=frame_y0+0.25, text="5", showarrow=True, ax=frame_x0+1.9, ay=frame_y0+0.6, **callout_style)
    # 6: Datum primario (A)
    fig.add_annotation(x=frame_x0+2.25, y=frame_y0+0.6, text="6", showarrow=True, ax=frame_x0+2.25, ay=frame_y0+0.9, **callout_style)
    # 7: Datum secundario (B) — placeholder
    fig.add_annotation(x=frame_x0+2.7, y=frame_y0+0.25, text="7", showarrow=True, ax=frame_x0+2.7, ay=frame_y0+0.6, **callout_style)
    # 8: Datum terciario (C) — placeholder
    fig.add_annotation(x=frame_x0+3.1, y=frame_y0+0.25, text="8", showarrow=True, ax=frame_x0+3.1, ay=frame_y0+0.6, **callout_style)
    
    # ========== SÍMBOLO DE DATUM (triángulo de referencia) ==========
    # Datum A identificado en el borde izquierdo
    # Línea de extensión del datum
    fig.add_shape(type='line', x0=2, x1=2, y0=5.5, y1=6.8,
                  line=dict(color='#000', width=2))
    # Triángulo del datum (simulado con líneas)
    datum_x, datum_y = 2, 6.8
    fig.add_shape(type='line', x0=datum_x-0.15, x1=datum_x+0.15, y0=datum_y, y1=datum_y,
                  line=dict(color='#000', width=2))
    fig.add_shape(type='line', x0=datum_x-0.15, x1=datum_x, y0=datum_y, y1=datum_y+0.2,
                  line=dict(color='#000', width=2))
    fig.add_shape(type='line', x0=datum_x+0.15, x1=datum_x, y0=datum_y, y1=datum_y+0.2,
                  line=dict(color='#000', width=2))
    # Letra del datum
    fig.add_annotation(x=datum_x, y=datum_y+0.4, text="A", showarrow=False,
                       font=dict(size=13, color='#000', family='Arial', weight='bold'))
    
    # ========== TÍTULO Y NOTAS DEL PLANO ==========
    # Cajetín de título (esquina superior izquierda)
    fig.add_annotation(x=0.5, y=7.5, text="<b>PLANO TÉCNICO: EJE RECTIFICADO</b>", 
                       showarrow=False, font=dict(size=14, color='#000', family='Arial'),
                       xanchor='left', yanchor='top')
    
    # Bloque de notas técnicas (esquina inferior derecha con recuadro)
    fig.add_shape(type='rect', x0=8.5, x1=11.5, y0=0.3, y1=1.3,
                  fillcolor='#fff', line=dict(color='#000', width=1.5))
    fig.add_annotation(x=10, y=1.1, text="<b>NOTAS TÉCNICAS</b>", showarrow=False,
                       font=dict(size=10, color='#000', family='Arial'))
    fig.add_annotation(x=10, y=0.85, text="Material: AISI 1045", showarrow=False,
                       font=dict(size=9, color='#000', family='Arial'), xanchor='center')
    fig.add_annotation(x=10, y=0.65, text="Acabado: Rectificado", showarrow=False,
                       font=dict(size=9, color='#000', family='Arial'), xanchor='center')
    fig.add_annotation(x=10, y=0.45, text="Escala 1:1", showarrow=False,
                       font=dict(size=9, color='#000', family='Arial'), xanchor='center')
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20), height=520,
        xaxis=dict(range=[0, 12], visible=False),
        yaxis=dict(range=[0, 8], visible=False),
        paper_bgcolor='#f5f5f5', plot_bgcolor='#ffffff',
        font=dict(color='#000')
    )
    # Añadir líneas punteadas magenta para la zona de tolerancia y etiqueta (ajustadas al ejemplo)
    magenta = "#d946ef"  # fucsia
    cyan = "#0ea5e9"     # azul annotation
    # El borde inferior de la pieza es y=3.5; ponemos las líneas justo debajo
    y_top = 3.30
    y_bot = y_top - 0.25
    y_mid = (y_top + y_bot) / 2
    fig.add_shape(type='line', x0=2.0, x1=10.0, y0=y_top, y1=y_top,
                  line=dict(color=magenta, width=2, dash='dot'))
    fig.add_shape(type='line', x0=2.0, x1=10.0, y0=y_bot, y1=y_bot,
                  line=dict(color=magenta, width=2, dash='dot'))
    # Línea negra horizontal al centro de la zona de tolerancia
    fig.add_shape(type='line', x0=2.0, x1=10.0, y0=y_mid, y1=y_mid,
                  line=dict(color='#000', width=2))

    # Bracket azul indicando la separación entre líneas (como en la imagen)
    # Pequeñas líneas horizontales de referencia a la derecha y flechitas verticales
    x_ref = 10.3
    fig.add_shape(type='line', x0=x_ref-0.2, x1=x_ref+0.2, y0=y_top, y1=y_top,
                  line=dict(color=cyan, width=2))
    fig.add_shape(type='line', x0=x_ref-0.2, x1=x_ref+0.2, y0=y_bot, y1=y_bot,
                  line=dict(color=cyan, width=2))
    # Flechas/segmentos verticales conectando el bracket
    fig.add_shape(type='line', x0=x_ref, x1=x_ref, y0=y_bot+0.03, y1=y_top-0.03,
                  line=dict(color=cyan, width=2))
    # Etiqueta azul
    fig.add_annotation(x=11.0, y=y_mid, text=f"{tol:.2f} zona de tolerancia",
                       showarrow=False,
                       font=dict(color=cyan, size=12))
    return fig



# ===================== INTERFAZ PRINCIPAL =====================
st.sidebar.title("Menú GD&T")
main_mode = st.sidebar.radio("Modo:", ["Análisis Individual", "Constructor de Plano"])

if main_mode == "Análisis Individual":
    menu = list(GD_DATA.keys())
    cat = st.sidebar.selectbox("Característica", menu)
    # Símbolo con tamaño fijo (200x200)
    st.sidebar.markdown("<div style='color:#f3f4f6; font-size:13px; margin-bottom:0px;'>Tolerancia (mm)</div>", unsafe_allow_html=True)
    tol = st.sidebar.slider("", 0.1, 2.0, 0.5, key="slider_tol")
    st.sidebar.markdown(f"<div style='color:#fff; background:transparent; display:inline-block; padding:2px 10px; margin-top:4px; margin-bottom:10px; font-size:15px; font-weight:bold;'>Valor: {tol:.2f} mm</div>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    <style>
    /* Oculta los valores del slider (min, max, actual) */
    .stSlider .css-1aumxhk,
    .stSlider .css-1r6slb0,
    .stSlider .css-14xtw13,
    .stSlider .css-1gv0vcd,
    .stSlider .st-c2,
    .stSlider label[data-testid=\"stWidgetLabel\"] + div > div > div > span {
        display: none !important;
    }
    /* SOLO en el sidebar: fondo oscuro para el slider y contorno oscuro */
    [data-testid=\"stSidebar\"] .stSlider > div[data-baseweb=\"slider\"] {
        background: #23272e !important;
        border-radius: 16px !important;
        box-shadow: none !important;
        border: 1.5px solid #181a1b !important;
    }
    [data-testid=\"stSidebar\"] .stSlider .css-13cymwt, [data-testid=\"stSidebar\"] .stSlider .st-c1, [data-testid=\"stSidebar\"] .stSlider [role=\"slider\"] ~ div > div {
        background: #444 !important;
    }
    [data-testid=\"stSidebar\"] .stSlider label, [data-testid=\"stSidebar\"] .stSlider div, [data-testid=\"stSidebar\"] .stSlider span {
        color: #fff !important;
    }
    [data-testid=\"stSidebar\"] .stSlider .css-1gv0vcd, [data-testid=\"stSidebar\"] .stSlider .css-14xtw13, [data-testid=\"stSidebar\"] .stSlider .css-1r6slb0 {
        color: #fff !important;
    }
    </style>
    """, unsafe_allow_html=True)
    view = st.sidebar.radio("Vista:", ["Simulación 3D", "Montaje Real", "Zona de Tolerancia", "Plano Técnico Real"])

    # --- LAYOUT CORREGIDO: SÍMBOLO COMO IMAGEN EN RECUADRO BLANCO CON BORDE NEGRO ---
    # Arriba: símbolo a la izquierda (solo imagen), info-card a la derecha
    # CSS adicional para alinear verticalmente arriba y ajustar spacing
    st.markdown("""<style>
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        align-items: stretch !important;
    }
    .symbol-box {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        align-self: flex-start !important;
    }
    .info-card {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    </style>""", unsafe_allow_html=True)
    top1, top2 = st.columns([1, 5], gap="small")
    with top1:
        # Mostrar la imagen del símbolo según la característica seleccionada.
        img_path = get_symbol_image_path(cat)
        box_px = ST_SYMBOL_SIZE
        if img_path:
            # si es SVG, incrustar el contenido para asegurar renderizado correcto
            if img_path.lower().endswith('.svg'):
                try:
                    with open(img_path, 'r', encoding='utf-8') as f:
                        svg_text = f.read()
                    st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>{svg_text}</div>", unsafe_allow_html=True)
                except Exception:
                    st.image(img_path, width=box_px-20)
            else:
                st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>", unsafe_allow_html=True)
                st.image(img_path, width=box_px-20)
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Fallback SVG simple y en negro (sin fondo). Línea centrada para mantener estilo.
            stub_svg = f"<svg viewBox='0 0 120 120' xmlns='http://www.w3.org/2000/svg'>" \
                       f"<line x1='12' y1='60' x2='108' y2='60' stroke='#000' stroke-width='8' stroke-linecap='round'/>" \
                       f"</svg>"
            st.markdown(f"<div class='symbol-box' style='height:{box_px}px;width:{box_px}px'>{stub_svg}</div>", unsafe_allow_html=True)
    with top2:
        show_info_card(cat)

    st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)

    # Abajo: simulación a la izquierda, leyenda y ¿Qué ves? apilados a la derecha
    bot1, bot2 = st.columns([2.5, 1.5], gap="medium")
    with bot1:
        # Agregar CSS para envolver el iframe con borde
        st.markdown("""
        <style>
        .plot-container {
            border: 2.5px solid #23272e;
            border-radius: 8px;
            padding: 16px;
            background: #fff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
            margin-top: 0;
            margin-bottom: 0;
        }
        .plot-container iframe {
            border: none !important;
            display: block;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if view == "Simulación 3D":
            fig = plot_3d_rectitud(tol)
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            # Envolver con div y clase para CSS
            wrapped_html = f'<div class="plot-container">{html_plot}</div>'
            components.html(wrapped_html, height=540, scrolling=False)
        elif view == "Montaje Real":
            fig = plot_real_rectitud()
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            wrapped_html = f'<div class="plot-container">{html_plot}</div>'
            components.html(wrapped_html, height=460, scrolling=False)
        elif view == "Zona de Tolerancia":
            fig = plot_blueprint_rectitud(tol)
            html_plot = pio.to_html(fig, include_plotlyjs='cdn', full_html=False)
            wrapped_html = f'<div class="plot-container">{html_plot}</div>'
            components.html(wrapped_html, height=400, scrolling=False)
        elif view == "Plano Técnico Real":
            fig = plot_technical_drawing_rectitud(tol)
            st.pyplot(fig, use_container_width=True)
    with bot2:
        st.markdown("<div class='legend-stack'>", unsafe_allow_html=True)
        show_legend(cat, view)
        if view == "Simulación 3D":
            st.markdown(f"<div class='pedagogic-box'><b>¿Qué ves?</b> El eje azul representa el elemento real, el cilindro naranja la zona de tolerancia. Si el eje azul permanece dentro del cilindro, la pieza cumple rectitud.</div>", unsafe_allow_html=True)
        elif view == "Montaje Real":
            st.markdown("""
                <div class='pedagogic-box'>
                    <b>¿Qué ves?</b> El palpador recorre el eje y la aguja <span style="color:#22d3ee">(cian)</span> traduce ese movimiento<br>
                    en una lectura amplificada (desviación de rectitud visible en la escala).
                </div>
            """, unsafe_allow_html=True)
        elif view == "Zona de Tolerancia":
            st.markdown(f"""
                <div class='pedagogic-box'>
                    <b>¿Qué ves?</b> Zona gris clara: área permitida de tolerancia ({tol} mm de ancho).<br>
                    Líneas naranjas: límites superior e inferior. Línea azul: eje ideal.<br>
                    Escala derecha: referencia de desviación permitida.<br><br>
                    <b>Interpretación:</b> El eje debe permanecer dentro de la zona para cumplir rectitud.
                </div>
            """, unsafe_allow_html=True)
        elif view == "Plano Técnico Real":
            st.markdown(f"""
                <div class='pedagogic-box'>
                    <b>¿Qué ves?</b> Dibujo técnico estándar con:<br>
                    1) Valor y símbolo que representa la acotación y la tolerancia total (Ø10±{tol*2:.1f}).<br>
                    2) Flecha guía al área controlada.<br>
                    3) Símbolo de la característica que controla (rectitud).<br>
                    4) Valor de tolerancia ({tol}).<br><br>
                    <b>Interpretación:</b> El marco de control (FCF) comunica qué controlar, cuánto, y contra qué referencias (datums).<br>
                    Las cotas (80.00, Ø10±{tol*2:.1f}) describen tamaño; el FCF especifica la forma/tolerancia geométrica.
                </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif main_mode == "Constructor de Plano":
    st.markdown("## Constructor de Plano Técnico")
    st.info("Agrega cotas y tolerancias para construir un plano técnico completo. Por ahora solo disponible para 'Rectitud'.")
    # Estado de plano (solo para 'Rectitud' por ahora)
    if 'plano_rectitud' not in st.session_state:
        st.session_state['plano_rectitud'] = []
    nueva_tol = st.slider("Tolerancia de rectitud a agregar (mm)", 0.1, 2.0, 0.5)
    if st.button("Agregar cota de rectitud"):
        st.session_state['plano_rectitud'].append(nueva_tol)
    st.markdown("### Vista del plano construido")
    # Mostrar todas las cotas agregadas
    if st.session_state['plano_rectitud']:
        for idx, tol in enumerate(st.session_state['plano_rectitud']):
            st.plotly_chart(plot_blueprint_rectitud(tol), use_container_width=True)
            st.markdown(f"<div class='pedagogic-box'>Cota {idx+1}: Zona de tolerancia de rectitud de {tol:.2f} mm</div>", unsafe_allow_html=True)
    else:
        st.warning("Agrega al menos una cota para ver el plano.")
## Así cada simulación será independiente, robusta y pedagógica.
