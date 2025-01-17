index_string = '''
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