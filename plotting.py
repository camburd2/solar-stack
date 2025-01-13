import numpy as np
import plotly.graph_objs as go


def create_surface(x_coords, y_coords, z_coords, colorscale):
    return go.Surface(
        x=x_coords,
        y=y_coords, 
        z=z_coords,
        surfacecolor=np.ones_like(z_coords),
        colorscale=colorscale,
        opacity=1,
        showscale=False,
        lighting=dict(
            ambient=1.0,
            diffuse=0,
            specular=0,
            roughness=1
        ),
        lightposition=dict(x=0, y=0, z=0)
    )

def rect_surfaces(rects, color):
    surfs = []
    for rect_coords in rects:
        x = np.array([rect_coords[0], rect_coords[2]])
        y = np.array([rect_coords[1], rect_coords[3]])
        X, Y = np.meshgrid(x, y)
        Z = np.ones_like(X) * rect_coords[4]
        
        surf = create_surface(X, Y, Z, color)
        surfs.append(surf)
    return surfs

def create_cylinder(panel_width, radius=.3, height=40, resolution=50):
    center = (0,  panel_width/2, 0)
    theta = np.linspace(0, 2 * np.pi, resolution)
    z = np.linspace(center[2], center[2] + height, resolution)
    theta, z = np.meshgrid(theta, z)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    
    return create_surface(x, y, z, 'gray')