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
                width: 250px;
                padding: 20px;
                background-color: white;
                box-shadow: 2px 0 5px rgba(0,0,0,0.1);
                z-index: 1;
            }
            .plot-column {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
            }
            .slider-container {
                padding: 20px;
                background-color: white;
            }
            .slider {
                display: flex;
                align-items: center;
                margin-bottom: 15px;
            }
            .slider-label {
                width: 80px;
                font-weight: bold;
                margin-right: 15px;
                white-space: nowrap;
            }
            .slider-component {
                flex-grow: 1;
            }
            .input-group {
                margin-bottom: 15px;
            }
            .input-label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .input-field {
                width: 75%;
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