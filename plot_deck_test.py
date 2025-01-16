import numpy as np
import plotly.graph_objects as go

# Input is length of sailboat L, the rest of the shape scales with parameterized functions
L = 40

x = np.linspace(0, L, 100)

def f1(x, p):
    return (1/(14*p)) * (x-p)**2 - p/2

def f2(x, p):
    return -(1/(14*p)) * (x-p)**2 - p/2 + p

def calc_p(l):
    return (-l*(1-7**.5))/6

p = calc_p(L)

X = np.array([x, x])  # two rows for top and bottom curves
Y = np.array([f1(x, p), f2(x, p)])  #  function values
Z = np.zeros_like(X)  # z-values for the flat surface

# Create the visualization
fig = go.Figure()

# Add the surface directly
fig.add_trace(
    go.Surface(
        x=X,
        y=Y,
        z=Z,
        colorscale=[[0, 'blue'], [1, 'blue']],
        showscale=False,
        opacity=0.5
    )
)

fig.update_layout(
    scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        xaxis=dict(range=[0, L]),
        yaxis=dict(range=[-L*.5, L*.5]),
        zaxis=dict(range=[0, L]),
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=1.5)
        )
    ),
    showlegend=True,
    title='Area Between Two Functions'
)

fig.show()
