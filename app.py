import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import layout
from stack import Stack
import plotting

class App:

    def __init__(self):
        self.active_stack = None
        self.static_surfaces = None  # panels, deck, mast

        # initial stack'
        self._create_stack(
            num_panels=6,
            panel_spacing=2,
            panel_width=1
        )

        self.app = dash.Dash(__name__)
        self.app.index_string = layout.index_string
        self.setup_layout()
        self.setup_callbacks()

    def _create_stack(self, num_panels, panel_spacing, panel_width):
        """Create a new active solar panel stack and static surfaces (panels, mast, deck)"""
        
        
        self.active_stack = Stack(
            num_panels=num_panels,
            panel_spacing=panel_spacing,
            panel_width=panel_width,
            boat_length=40
        )

        panels = self.active_stack.create_panel_surfaces()

        deck, mast_x = plotting.create_deck(
            boat_length=40, 
            width=panel_width,
        )

        cylinder = plotting.create_cylinder(
            panel_width=panel_width,
            x_val=mast_x,
            height=40
        )

        self.static_surfaces = panels + [cylinder] + [deck]

    def setup_layout(self):
        self.app.layout = html.Div(className='container', children=[
            # Main content area
            html.Div(className='main-content', children=[
                # Side panel for input
                html.Div(className='side-panel', children=[
                    html.H3("Panel Configuration", style={'margin-bottom': '50px'}),
                    html.Div(className='input-group', children=[
                        html.Label('Number of Panels', className='input-label'),
                        dcc.Input(id='num-panels-input', type='number', value=5, min=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Spacing (ft)', className='input-label'),
                        dcc.Input(id='panel-spacing-input', type='number', value=1.5, step=0.1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Width (ft)', className='input-label'),
                        dcc.Input(id='panel-width-input', type='number', value=2, step=0.1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Length (ft)', className='input-label'),
                        dcc.Input(id='panel-length-input', type='number', value=6, step=0.1, className='input-field')
                    ]),
                    html.Div(id='estimated-power', className='estimate-power')
                ]),

                # Plot column
                html.Div(className='plot-column', children=[
                    dcc.Graph(id='sun-shadow-plot', style={'height': '100%', 'width': '100%'})
                ]),
            ]),

            # Bottom slider section
            html.Div(className='slider-container', children=[
                html.Div(className='slider', children=[
                    html.Label('Elevation (°)', className='slider-label'),
                    html.Div(className='slider-component', children=[
                        dcc.Slider(id='elevation-slider', min=0, max=90, value=45,
                                marks={i: str(i) for i in range(0, 91, 15)},
                                tooltip={"placement": "bottom", "always_visible": True})
                    ])
                ]),
                html.Div(className='slider', children=[
                    html.Label('Azimuth (°)', className='slider-label'),
                    html.Div(className='slider-component', children=[
                        dcc.Slider(id='azimuth-slider', min=0, max=360, value=180,
                                marks={i: str(i) for i in range(0, 361, 30)},
                                tooltip={"placement": "bottom", "always_visible": True})
                    ])
                ]),
            ])
        ])


    def new_fig(self, data):
        L = self.active_stack.boat_length
        W = self.active_stack.panel_width

        D = L*.1 + L*1.1

        fig = go.Figure(data)

        fig.update_layout(
            paper_bgcolor='#ADD8E6',
            plot_bgcolor='#ADD8E6',
            scene=dict(
                bgcolor='#ADD8E6',
                xaxis=dict(range=[-L*.1, L*1.1]),
                yaxis=dict(range=[-D/2+W/2, D/2+W/2]),
                zaxis=dict(range=[0, D]),
                aspectmode='manual',
                aspectratio=dict(x=1, y=1, z=1),
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            scene_camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1)
            ),
            showlegend=False
        )        
        return [fig]


    def setup_callbacks(self):

        @self.app.callback(
            [Output('sun-shadow-plot', 'figure')],
            [Input('num-panels-input', 'value'),
            Input('panel-spacing-input', 'value'),
            Input('panel-width-input', 'value'),
            Input('elevation-slider', 'value'),
            Input('azimuth-slider', 'value')]
        )
        def update_plot(num, spacing, width, heading, azimuth):
            ctx = dash.callback_context
            
            trigger = ctx.triggered[0]['prop_id']
            if 'num-panels-input' in trigger or 'panel-spacing-input' in trigger or 'panel-width-input' in trigger:
                # Inputs related to the stack
                self._create_stack(num_panels=num, panel_spacing=spacing, panel_width=width)
            
            #elif 'elevation-slider' in trigger or 'azimuth-slider' in trigger:
            #    # Inputs related to the sun position
            self.active_stack.update_sun_direction_vector(azimuth=heading, heading=azimuth) # the names, they are mixed up in new stack
            sun_lines = self.active_stack.create_sun_lines()
            shadows = self.active_stack.create_shadow_surfaces()
            data = self.static_surfaces + sun_lines + shadows
            
            return self.new_fig(data)

    

    def run(self):
        self.app.run_server(debug=False)
        
        
if __name__ == '__main__':
    solar_app = App()
    solar_app.run()