"""
Sistema de despacho de visualizaciones para características GD&T.
Genera visualizaciones 3D, montaje real, zona de tolerancia y planos técnicos
de forma genérica para todas las características geométricas.
"""

import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def plot_generic_3d(feature, tol):
    """Genera visualización 3D genérica según el tipo de característica."""
    
    if feature == 'Rectitud':
        return plot_3d_rectitud(tol)
    elif feature == 'Planicidad':
        return plot_3d_planicidad(tol)
    elif feature == 'Redondez':
        return plot_3d_redondez(tol)
    elif feature == 'Cilindricidad':
        return plot_3d_cilindricidad(tol)
    elif feature in ['Perfil de Línea', 'Perfil de Superficie']:
        return plot_3d_perfil(feature, tol)
    elif feature in ['Angularidad', 'Perpendicularidad', 'Paralelismo']:
        return plot_3d_orientacion(feature, tol)
    elif feature in ['Posición', 'Concentricidad']:
        return plot_3d_ubicacion(feature, tol)
    elif feature in ['Oscilación Circular', 'Oscilación Total']:
        return plot_3d_oscilacion(feature, tol)
    else:
        return create_placeholder_3d(feature)

def plot_3d_rectitud(tol):
    """Visualización 3D específica de Rectitud - ya implementada."""
    # Esta función ya existe en app.py, la mantenemos
    pass

def plot_3d_planicidad(tol):
    """Planicidad: superficie plana entre dos planos paralelos."""
    fig = go.Figure()
    
    # Superficie real con ligera ondulación
    x = np.linspace(-5, 5, 30)
    y = np.linspace(-5, 5, 30)
    X, Y = np.meshgrid(x, y)
    Z = 0.1 * np.sin(X) * np.cos(Y) * tol  # Ondulación controlada por tolerancia
    
    # Superficie real
    fig.add_trace(go.Surface(x=X, y=Y, z=Z, colorscale='Blues', opacity=0.7,
                             name='Superficie Real', showscale=False))
    
    # Planos límite de tolerancia
    Z_upper = np.ones_like(X) * (tol/2)
    Z_lower = np.ones_like(X) * (-tol/2)
    
    fig.add_trace(go.Surface(x=X, y=Y, z=Z_upper, colorscale=[[0, 'rgba(255,100,0,0.3)'], [1, 'rgba(255,100,0,0.3)']], 
                             showscale=False, name='Límite Superior'))
    fig.add_trace(go.Surface(x=X, y=Y, z=Z_lower, colorscale=[[0, 'rgba(255,100,0,0.3)'], [1, 'rgba(255,100,0,0.3)']], 
                             showscale=False, name='Límite Inferior'))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False, range=[-tol*2, tol*2]),
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
        ),
        showlegend=True,
        margin=dict(l=0, r=0, t=30, b=0),
        height=500
    )
    
    return fig

def plot_3d_redondez(tol):
    """Redondez: círculo perfecto en sección transversal."""
    fig = go.Figure()
    
    theta = np.linspace(0, 2*np.pi, 100)
    
    # Círculo real con pequeñas imperfecciones
    r_real = 5 + 0.3 * tol * np.sin(5*theta)
    x_real = r_real * np.cos(theta)
    y_real = r_real * np.sin(theta)
    
    # Círculo teórico
    r_teorico = 5
    x_teorico = r_teorico * np.cos(theta)
    y_teorico = r_teorico * np.sin(theta)
    
    # Límites de tolerancia
    r_upper = r_teorico + tol/2
    r_lower = r_teorico - tol/2
    x_upper = r_upper * np.cos(theta)
    y_upper = r_upper * np.sin(theta)
    x_lower = r_lower * np.cos(theta)
    y_lower = r_lower * np.sin(theta)
    
    fig.add_trace(go.Scatter(x=x_real, y=y_real, mode='lines', line=dict(color='blue', width=3),
                             name='Perfil Real'))
    fig.add_trace(go.Scatter(x=x_teorico, y=y_teorico, mode='lines', line=dict(color='black', width=1, dash='dash'),
                             name='Círculo Teórico'))
    fig.add_trace(go.Scatter(x=x_upper, y=y_upper, mode='lines', line=dict(color='orange', width=2),
                             name='Límite Superior'))
    fig.add_trace(go.Scatter(x=x_lower, y=y_lower, mode='lines', line=dict(color='orange', width=2),
                             name='Límite Inferior'))
    
    fig.update_layout(
        xaxis=dict(scaleanchor='y', scaleratio=1, visible=False),
        yaxis=dict(visible=False),
        showlegend=True,
        height=500,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

def create_placeholder_3d(feature):
    """Placeholder genérico para características en desarrollo."""
    fig = go.Figure()
    
    fig.add_annotation(
        text=f"Visualización 3D de {feature}<br>en desarrollo",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="gray")
    )
    
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=500,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return fig

# Similar pattern for other views...
def plot_generic_montaje(feature):
    """Sistema genérico de montaje real."""
    # Implementar según feature
    pass

def plot_generic_zona(feature, tol):
    """Sistema genérico de zona de tolerancia."""
    # Implementar según feature
    pass

def plot_generic_plano(feature, tol):
    """Sistema genérico de plano técnico."""
    # Implementar según feature
    pass
