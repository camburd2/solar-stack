import dash
from dash import dcc, html

LAYOUT = html.Div(className='container', children=[

    dcc.Location(id='url', refresh=False),  # Track the current page URL
    
    # Navigation bar
        html.Div(className='navigation', children=[
            html.Div(className='nav-container', children=[
                html.A('Home', href='/', className='nav-link'),
                html.A('Analysis', href='/analysis', className='nav-link')
            ])
        ]),

    html.Div(id='home-page', className='container', children=[
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
                    html.Label('Panel Efficiency', className='input-label'),
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
                html.Div(style={
                    'position': 'relative', 
                    'height': '100%', 
                    'width': '100%'
                }, children=[
                    html.Button(
                        "Toggle Heatmap", 
                        id="plot-toggle-button", 
                        style={
                            'position': 'absolute', 
                            'bottom': '10px', 
                            'right': '10px', 
                            'zIndex': '10',
                            'background-color': '#2c3e50', 
                            'color': 'white', 
                            'border': 'none', 
                            'padding': '8px 15px', 
                            'borderRadius': '20px', 
                            'cursor': 'pointer', 
                            'boxShadow': '0 2px 5px rgba(0,0,0,0.2)', 
                            'transition': 'background-color 0.3s ease'
                        },
                        n_clicks=0
                    ),
                dcc.Graph(id='sun-shadow-plot', style={'height': '100%', 'width': '100%'})
                ])
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
    ]),



    # Analysis Page Layout
    html.Div(id='analysis-page', className='main-content', children=[
        html.Div(className='side-panel', children=[
            html.H3("Analysis Inputs", style={'margin-bottom': '50px'}),

            html.Div(className='input-group', children=[
                html.Label('mast height (from deck)', className='input-label'),
                dcc.Input(id='mast-height', type='number', value=40, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('mast base offset', className='input-label'),
                dcc.Input(id='mast-base-offset', type='number', value=3, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('base length', className='input-label'),
                dcc.Input(id='base-length', type='number', value=5, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('cost frame $', className='input-label'),
                dcc.Input(id='cost-frame', type='number', value=5, step=.5, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('cost panel $', className='input-label'),
                dcc.Input(id='cost-panel', type='number', value=5, step=.5, className='input-field')
            ]),

            # search ranges
            html.Div(className='input-group', children=[
                html.Label('panel width min', className='input-label'),
                dcc.Input(id='panel-width-min', type='number', value=12, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('panel width max', className='input-label'),
                dcc.Input(id='panel-width-max', type='number', value=36, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('panel spacing min', className='input-label'),
                dcc.Input(id='panel-spacing-min', type='number', value=12, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('panel spacing max', className='input-label'),
                dcc.Input(id='panel-spacing-max', type='number', value=36, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('panel num min', className='input-label'),
                dcc.Input(id='panel-num-min', type='number', value=1, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Label('panel num max', className='input-label'),
                dcc.Input(id='panel-num-max', type='number', value=6, step=0.1, className='input-field')
            ]),
            html.Div(className='input-group', children=[
                html.Button("Generate Plot", id="generate-plot-button", className="button", n_clicks=0)
            ])

        ]),
        html.Div(className='plot-column', children=[
            dcc.Graph(id='analysis-plot', style={'height': '100%', 'width': '100%'})
        ])
    ])
])


INDEX_STRING = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body, html {
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
                background-color: white;
                font-family: Arial, sans-serif;
            }
            #react-entry-point {
                height: 100%;
            }
            .nav-link {
                color: #2c3e50;
                text-decoration: none;
                padding: 10px 15px;
                margin: 0 10px;
                border-radius: 20px;
                transition: background-color 0.3s ease;
                font-weight: bold;
            }
            .navigation {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 5px 0;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .container {
                display: flex;
                flex-direction: column;
                height: 100%;
            }
            .main-content {
                display: flex;
                flex-grow: 1;
                overflow: hidden;
            }
            .side-panel {
                width: 270px;
                padding: 20px;
                background-color: white;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                z-index: 1;
                display: flex;
                flex-direction: column;
            }
            .plot-column {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
            }
            .slider-container {
                padding: 20px;
                background-color: white;
                display: flex;
                gap: 20px;
            }
            .slider-group {
                flex: 1;
                display: flex;
                flex-direction: column;
                min-height: 100px;
            }

            .slider {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .slider-label {
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
            }
            .slider-component {
                width: 100%;
            }
            .input-group {
                display: flex;
                flex-direction: row_reverse;
                justify-content: flex-end;
                align-items: center;
                gap: 10px;
                margin-bottom: 15px;
            }
            .input-label {
                font-weight: bold;
                flex-shrink: 0;
                margin: 0;
            }
            .input-field {
                width: 80px;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }

            .estimated-power {
                font-size: 16px;
                font-weight: bold;
                margin-top: 80px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }

            .power-estimate-container {
                margin-top: auto;
                padding: 15px;
                background-color: #f5f5f5;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }

            .power-estimate-title {
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .power-estimate-value {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }

            .power-estimate-unit {
                font-size: 14px;
                color: #666;
                margin-left: 4px;
            }

            .nav-link:hover {
                background-color: #f0f0f0;
            }

        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''