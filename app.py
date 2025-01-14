from stack import Stack
import plotly.graph_objs as go
import dash
from dash import dcc, html
from plotting import create_cylinder

if __name__ == "__main__":

    stack = Stack(num_panels=6, 
                 panel_spacing=2,
                 panel_width=1,
                 plot=True)
    
    cylinder = create_cylinder(stack.panel_width)
    panels = stack.create_panel_surfaces()


    app = dash.Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(id='graph', style={'height': '80vh'}),
        html.Div(id='power-display', style={'fontSize': '18px', 'textAlign': 'center'}),
        html.Div([
            html.Label('Sun Heading (degrees):'),
            dcc.Slider(
                id='heading-slider',
                min=0,
                max=360,
                value=180,
                marks={i: str(i) for i in range(0, 361, 45)}
            ),
            html.Label('Sun Azimuth (degrees):'),
            dcc.Slider(
                id='azimuth-slider',
                min=0,
                max=90,
                value=65,
                marks={i: str(i) for i in range(0, 91, 15)}
            )
        ])
    ])

    @app.callback(
        [dash.Output('graph', 'figure'),
        dash.Output('power-display', 'children')],
        [dash.Input('heading-slider', 'value'),
        dash.Input('azimuth-slider', 'value')]
    )
    def update_figure(heading, azimuth):
        stack.update_sun_direction_vector(heading, azimuth) # d vector used by sun lines and shadows
        sun_lines = stack.create_sun_lines()
        shadows = stack.create_shadow_surfaces()

        power = stack.calc_power(efficiency=.15)
        
        fig = go.Figure(data=[cylinder] + panels + sun_lines + shadows)

        fig.update_layout(
            scene=dict(
                camera=dict(eye=dict(x=1, y=1, z=1)),
                aspectmode='manual',
                xaxis=dict(range=[-2, 9]),
                yaxis=dict(range=[-6, 5]),
                zaxis=dict(range=[0, 13])
            ),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        power_text = f"Calculated Power: {power:.2f} W"
        return fig, power_text

    app.run_server(debug=True)