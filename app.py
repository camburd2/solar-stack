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
            panel_spacing=3,
            panel_width=2,
            boat_length=40,
            base_mast_offset=4,
            base_length=5,
            base_height=1,
            eff=0.15,
            cost_panel=5,
            cost_frame=5
        )

        self.app = dash.Dash(__name__)
        self.app.index_string = layout.index_string
        self.setup_layout()
        self.setup_callbacks()

    def _create_stack(self, 
                      num_panels, 
                      panel_spacing, 
                      panel_width, 
                      boat_length,
                      base_mast_offset,
                      base_length,
                      base_height,
                      eff,
                      cost_panel,
                      cost_frame):
        """Create a new active solar panel stack and static surfaces (panels, mast, deck)"""
        
        
        self.active_stack = Stack(
            num_panels=num_panels,
            panel_spacing=panel_spacing,
            panel_width=panel_width,
            boat_length=boat_length,
            base_mast_offset=base_mast_offset,
            base_length=base_length,
            base_height=base_height,
            eff=eff,
            cost_panel=cost_panel,
            cost_frame=cost_frame
        )

        panels = self.active_stack.create_panel_surfaces()

        deck, mast_x = plotting.create_deck(
            boat_length=boat_length, 
            width=panel_width,
        )

        cylinder = plotting.create_cylinder(
            panel_width=panel_width,
            x_val=mast_x,
            height=boat_length*1.2
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
                        dcc.Input(id='num-panels-input', type='number', value=6, min=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Spacing (ft)', className='input-label'),
                        dcc.Input(id='panel-spacing-input', type='number', value=3, step=0.1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Width (ft)', className='input-label'),
                        dcc.Input(id='panel-width-input', type='number', value=2, step=0.1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Boat Length (ft)', className='input-label'),
                        dcc.Input(id='boat-length-input', type='number', value=40, step=1, className='input-field')
                    ]),
                    

                    html.Div(className='input-group', children=[
                        html.Label('Base Mast Offset (ft)', className='input-label'),
                        dcc.Input(id='base-mast-offset-input', type='number', value=4, step=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Base Panel Length (ft)', className='input-label'),
                        dcc.Input(id='base-panel-length-input', type='number', value=5, step=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Base Panel Height (ft)', className='input-label'),
                        dcc.Input(id='base-panel-height-input', type='number', value=1, step=1, className='input-field')
                    ]),

                    html.Div(className='input-group', children=[
                        html.Label('Cost Panel Frame ($/ft)', className='input-label'),
                        dcc.Input(id='cost-frame-input', type='number', value=5, step=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Cost Panel ($/ft^2)', className='input-label'),
                        dcc.Input(id='cost-panel-input', type='number', value=5, step=1, className='input-field')
                    ]),
                    html.Div(className='input-group', children=[
                        html.Label('Panel Efficiency ($/ft^2)', className='input-label'),
                        dcc.Input(id='eff-panel-input', type='number', value=.15, step=.01, className='input-field')
                    ]),

                    html.Div(className='power-estimate-container', children=[
                        html.Div("Power Estimate", className='power-estimate-title'),
                            html.Div(children=[
                                html.Span(id='estimated-power', className='power-estimate-value'),
                                html.Span("W", className='power-estimate-unit')
                            ])
                    ]),
                    html.Div(className='power-estimate-container', children=[
                        html.Div("Cost Estimate", className='power-estimate-title'),
                            html.Div(children=[
                                html.Span('$', className='power-estimate-unit'),
                                html.Span(id='estimated-cost', className='power-estimate-value')
                            ])
                    ]),
                ]),

                # Plot column
                html.Div(className='plot-column', children=[
                    dcc.Graph(id='sun-shadow-plot', style={'height': '100%', 'width': '100%'})
                ]),
            ]),

            # Bottom slider section
            html.Div(className='slider-container', children=[
                # First slider group
                html.Div(className='slider-group', children=[
                    html.Label('Sun Elevation (°)', className='slider-label'),
                    html.Div(className='slider-component', children=[
                        dcc.Slider(
                            id='elevation-slider',
                            min=0,
                            max=90,
                            value=45,
                            marks={i: str(i) for i in range(0, 91, 15)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ])
                ]),
                
                # Second slider group
                html.Div(className='slider-group', children=[
                    html.Label('Sun Azimuth (°)', className='slider-label'),
                    html.Div(className='slider-component', children=[
                        dcc.Slider(
                            id='azimuth-slider',
                            min=0,
                            max=360,
                            value=180,
                            marks={i: str(i) for i in range(0, 361, 30)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ])
                ])
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
        return fig


    def setup_callbacks(self):

        @self.app.callback(
            [Output('sun-shadow-plot', 'figure'),
             Output('estimated-power', 'children'),
             Output('estimated-cost', 'children')],

            [Input('num-panels-input', 'value'),
            Input('panel-spacing-input', 'value'),
            Input('panel-width-input', 'value'),
            Input('boat-length-input', 'value'),

            Input('base-mast-offset-input', 'value'),
            Input('base-panel-length-input', 'value'),
            Input('base-panel-height-input', 'value'),

            Input('elevation-slider', 'value'),
            Input('azimuth-slider', 'value'),
            
            Input('eff-panel-input', 'value'),
            Input('cost-panel-input', 'value'),
            Input('cost-frame-input', 'value')
            ]
        )
        def update_plot(num, 
                        spacing, 
                        width, 
                        boat_len,                     
                        base_mast_offset,
                        base_length,
                        base_height,
                        heading, azimuth, 
                        eff, cost_panel, cost_frame):


            ctx = dash.callback_context
            
            if any(trigger['prop_id'].split('.')[0] in [
                    'num-panels-input', 'panel-spacing-input',
                    'panel-width-input', 'boat-length-input',
                    'base-mast-offset-input', 'base-panel-length-input', 'base-panel-height-input',
                    'eff-panel-input', 'cost-panel-input', 'cost-frame-input'
                ] for trigger in ctx.triggered):
                self._create_stack(
                    num_panels=num,
                    panel_spacing=spacing,
                    panel_width=width,
                    boat_length=boat_len,
                    base_mast_offset=base_mast_offset,
                    base_length=base_length,
                    base_height=base_height,
                    eff=eff,
                    cost_panel=cost_panel,
                    cost_frame=cost_frame
                )
            

            self.active_stack.update_sun_direction_vector(azimuth=heading, heading=azimuth) # the names, they are mixed up in new stack
            sun_lines = self.active_stack.create_sun_lines()
            shadows = self.active_stack.create_shadow_surfaces()
            data = self.static_surfaces + sun_lines + shadows

            estimated_power = self.active_stack.power
            cost = self.active_stack.cost
            
            return self.new_fig(data), f"{estimated_power}", f'{cost}'

    

    def run(self):
        self.app.run_server(debug=False)
        
        
if __name__ == '__main__':
    solar_app = App()
    solar_app.run()