import dash
import plotly.graph_objs as go
from dash import dcc, html
import numpy as np

app = dash.Dash(__name__)

# Create a function for the panel
def create_panel(x0, y0, width=2, height=1, thickness=0.2):
    x = np.array([x0, x0 + width])
    y = np.array([y0, y0 + height])
    z = np.array([0, thickness])
    X, Y = np.meshgrid(x, y)
    Z = np.ones_like(X) * z[0]  # Bottom face
    
    return go.Surface(x=X, y=Y, z=Z, colorscale=[[0, 'LightSkyBlue'], [1, 'LightSkyBlue']], showscale=False)

# Create the figure with a single panel
fig = go.Figure(data=[create_panel(1, 1)])

fig.update_layout(
    scene=dict(
        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
        aspectmode='auto'
    ),
    margin=dict(l=0, r=0, t=0, b=0)
)

app.layout = html.Div(
    children=[
        dcc.Graph(id='graph', figure=fig, style={'height': '100%', 'width': '100%'}) 
    ],
    style={'height': '100vh'} 
)
if __name__ == '__main__':
    app.run_server(debug=True)