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

def create_cylinder(panel_width, x_val, radius=.3, height=40, resolution=50):
    center = (x_val,  panel_width/2, 0)
    theta = np.linspace(0, 2 * np.pi, resolution)
    z = np.linspace(center[2], center[2] + height, resolution)
    theta, z = np.meshgrid(theta, z)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    
    return create_surface(x, y, z, 'gray')


def calc_deck_param(boat_length):
    return (-boat_length*(1-7**.5))/6

def deck(x, p, w):
    first_term = (1/(14*p)) * (x-p)**2
    y_offset = w/2
    x_offset = p/2

    return (first_term - x_offset + y_offset,
            -first_term + x_offset + y_offset)

def create_deck(boat_length, width):
    param = calc_deck_param(boat_length=boat_length)

    x = np.linspace(0, boat_length, 100)

    left, right = deck(x, param, width)

    X = np.array([x, x])  # two rows for left and right curves
    Y = np.array([left, right])
    Z = np.zeros_like(X) 

    deck_surface = go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=[[0, 'gray'], [1, 'gray']],
        showscale=False,
        opacity=.3
    )

    mast_x = boat_length * .55

    return deck_surface, mast_x

if __name__ == "__main__":
    deck = create_deck(boat_length=40,
                       width=2)
    
    fig = go.Figure()
    fig.add_trace(deck)
    fig.show()
    

