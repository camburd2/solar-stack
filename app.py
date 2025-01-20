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
        self.static_surfaces = None  # contains panels, deck and mast

        # create initial stack with default config
        self._create_initial_stack()
        self._initialize_app()

    def _create_initial_stack(self):
        """Initialize solar panel stack with default params."""
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

    def _initialize_app(self):
        """Initialize app with layout and callbacks."""
        self.app = dash.Dash(__name__)
        self.app.index_string = layout.INDEX_STRING
        self.app.layout = layout.LAYOUT
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

    def new_fig(self, data):
        """Create new Plotly figure with correct camera angles and styles."""
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
            showlegend=True,
            legend=dict(y=0.9)
        )        
        return fig

    def setup_callbacks(self):
        """Set up dash callbacks for interactive updates."""
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
        def update_plot(num, spacing, width, boat_len, 
                        base_mast_offset, base_length, base_height,
                        heading, azimuth, 
                        eff, cost_panel, cost_frame):
            
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
            
            # update sun position and a
                # TODO: switch names everywhere (az is heading, so az-> elevation, heading->az)
            self.active_stack.update_sun_direction_vector(
                azimuth=heading, 
                heading=azimuth
            )
            sun_lines = self.active_stack.create_sun_lines()
            shadows = self.active_stack.create_shadow_surfaces()
            data = self.static_surfaces + sun_lines + shadows
            
            return (
                self.new_fig(data), 
                f"{self.active_stack.power}", 
                f'{self.active_stack.cost}'
            )

    def run(self):
        self.app.run_server(debug=False)
        
        
if __name__ == '__main__':
    solar_app = App()
    solar_app.run()