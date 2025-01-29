import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import layout as layout
from stack import Stack, StackConfig
import plot_interactive
import plot_analysis

class App:

    def __init__(self):
        self.active_stack = None
        self.static_surfaces = None  # contains panels, deck and mast
        self._create_stack(StackConfig())  # initial stack with default config
        self._initialize_app()

    def _initialize_app(self):
        """init app with layout and callbacks"""
        self.app = dash.Dash(__name__)
        self.app.index_string = layout.INDEX_STRING
        self.app.layout = layout.LAYOUT
        self.setup_callbacks()                           

    def _create_stack(self, cfg):
        """create a new active solar panel stack and static surfaces (panels, mast, deck)"""
        self.active_stack = Stack(cfg)

        panels = self.active_stack.create_panel_surfaces()
        deck, mast_x = plot_interactive.create_deck(cfg.boat_length, cfg.panel_width)
        cylinder = plot_interactive.create_cylinder(cfg.panel_width, mast_x, 
                                            height=self.active_stack.mast_height)

        self.static_surfaces = panels + [cylinder] + [deck]

    def new_fig(self, data):
        """create new plotly fig with correct camera angles and styles"""
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
        """set up dash callbacks for interactive updates"""

        @self.app.callback(
            [Output('home-page', 'style'),
            Output('analysis-page', 'style')],
            [Input('url', 'pathname')]
        )
        def display_page(pathname):
            if pathname == '/analysis':
                return {'display': 'none'}, {'display': 'flex'}
            return {'display': 'flex'}, {'display': 'none'}


        @self.app.callback(
            [Output('sun-shadow-plot', 'figure'),
             Output('estimated-power', 'children'),
             Output('estimated-cost', 'children')],
            [Input('plot-toggle-button', 'n_clicks')],
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
            Input('cost-frame-input', 'value')]
        )
        def update_main_plot(n_clicks, num, spacing, width, boat_len, 
                             base_mast_offset, base_length, base_height, 
                             elevation, azimuth, eff, cost_panel, cost_frame):
            
            # create new stack
            new_config = StackConfig(
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
            self._create_stack(new_config)
            
            if n_clicks % 2 == 0:
                # update dynamic elements
                self.active_stack.update_sun_direction_vector(elevation, azimuth)
                sun_lines = self.active_stack.create_sun_lines()
                shadows = self.active_stack.create_shadow_surfaces()
                data = self.static_surfaces + sun_lines + shadows
                
                return (
                    self.new_fig(data), 
                    f"{self.active_stack.power}", 
                    f'{self.active_stack.cost}'
                )
            else:
                # heatmap
                heatmap = plot_analysis.create_heatmap(self.active_stack)
                return (heatmap, '', '')

      
        @self.app.callback(
            Output('analysis-plot', 'figure'),
            [Input('panel-num-min', 'value'),
            Input('panel-num-max', 'value'),
            Input('panel-spacing-min', 'value'),
            Input('panel-spacing-max', 'value'),
            Input('panel-width-min', 'value'),
            Input('panel-width-max', 'value'),
            Input('boat-length-input-2', 'value'),
            Input('base-mast-offset-input-2', 'value'),
            Input('base-panel-length-input-2', 'value'),
            Input('base-panel-height-input-2', 'value'),
            Input('cost-frame-input-2', 'value'),
            Input('cost-panel-input-2', 'value'),
            Input('eff-panel-input-2', 'value')],
            prevent_initial_call=False
        )
        def generate_analysis_plot(num_min, num_max,
                                   space_min, space_max, 
                                   width_min, width_max,
                                   boat_len, base_mast_offset,
                                   base_panel_len, base_panel_height,
                                   cost_frame, cost_panel, eff_panel
                                   ):
            
            config = StackConfig(
                num_panels = None,  # set iteratively to make fig data
                panel_spacing = None,  # set iteratively to make fig data
                panel_width = None,  # set iteratively to make fig data
                boat_length = boat_len,
                base_mast_offset = base_mast_offset,
                base_length = base_panel_len,
                base_height = base_panel_height,
                eff = eff_panel,
                cost_panel = cost_panel,
                cost_frame = cost_frame
            )

            budget_pow_fig = plot_analysis.create_budget_pow_fig(
                config = config,
                num_range = (num_min, num_max),
                width_range = (width_min, width_max),  # ft
                spacing_range = (space_min, space_max),  # ft
                n_step = 1,  
                w_step = .5,  # ft
                s_step = .5,  # ft
                azimuth_range = (90,270),  # front to back (side to side is symmetrical, front to back is not)
                elevation_range = (15,90),  # start at 15deg for more realistic avg pow
                degree_step = 5
            )
            return budget_pow_fig


    def run(self):
        self.app.run_server(debug=False)
        

solar_app = App()
server = solar_app.app.server

if __name__ == '__main__':
    solar_app.run()