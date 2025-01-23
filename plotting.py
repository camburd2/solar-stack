import numpy as np
import plotly.graph_objs as go


def create_surface(x_coords, y_coords, z_coords, colorscale):
    """Create basic 3D plotly surface with x,y,z coordinates and color inputs."""
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
    """Create mutliple rectangular plotly surfaces from coordinate sets.
    
    Args:
        rects: list of coordinate tuples (x1, y1, x2, y2, z)
    
    Returns:
        list: list of plotly surface objects
    """
    surfs = []
    for rect_coords in rects:
        x = np.array([rect_coords.x0, rect_coords.x1])
        y = np.array([rect_coords.y0, rect_coords.y1])
        X, Y = np.meshgrid(x, y)
        Z = np.ones_like(X) * rect_coords.z
        
        surf = create_surface(X, Y, Z, color)
        surfs.append(surf)
    return surfs

def create_cylinder(panel_width, x_val, radius=.3, height=40, resolution=50):
    """Create a cylinder surface (sailboat mast).
    
    Args:
        panel_width: width of panels for centering
        x_val: x position of cylinder center (based on boat length)
        radius: radius of cylinder
        height: height of cylinder
        resolution: number of points for cylinder mesh
    
    Returns: 
        cylindrical plotly graph surface
    """
    center = (x_val,  panel_width/2, 0)
    theta = np.linspace(0, 2 * np.pi, resolution)
    z = np.linspace(center[2], center[2] + height, resolution)
    theta, z = np.meshgrid(theta, z)

    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    
    return create_surface(x, y, z, 'gray')


def calc_deck_param(boat_length):
    """Calculate deck shape parameter based on boat length.
    
    This formula was derived from parameterizing the two parabolas that
    form the deck shape curve (left and right sides).
    """
    return (-boat_length*(1-7**.5))/6

def deck(x, p, w):
    """Calculate deck curved poionts for given params.

    Used a graphing calculator (desmos) to find a formula for two parabolas
    (left and right side) to form a deck. One of the intersection points is the front
    tip of the boat and the back of the boat is formed by a straight line between them (before
    the second intersection). Once I found parabolas that looked like a boat shape, I 
    found the correct offsets for positioning and wrote the formulas in a parameterized form.
    Now I can calculate the parameter given a desired boat length and find the correctly 
    scaled functions to make the deck shape.
    
    Args:
        x: x coordinates along boat length
        p: shape parameter from calc_deck_param()
        w: width of panels for centering (offset boat position)
        
    Returns:
        tuple: (left curve, right_curve) Y coordinates
    """
    first_term = (1/(14*p)) * (x-p)**2
    y_offset = w/2
    x_offset = p/2

    return (first_term - x_offset + y_offset,
            -first_term + x_offset + y_offset)

def create_deck(boat_length, width):
    """Create deck surface with realistic sailboat shape.
    
    Args:
        boat_length: length of boat
        width: panel width
    
    Returns:
        tuple: (deck_surface, mast_x_position)
    """
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
    deck = create_deck(boat_length=40, width=2)
    
    fig = go.Figure()
    fig.add_trace(deck)
    fig.show()