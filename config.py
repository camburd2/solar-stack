
class Params:
    # Sailboat parameters
    MAST_HEIGHT = 40
    MAST_OFFSET = 3
    X_MAX = 8

    # Cost parameters
    COST_FRAME = 5  # $/ft
    COST_PANEL = 15  # $/ft^2

class Opt:
    panel_width = {
        'min': 12, 
        'max': 36, 
        'step': 4
    }
    
    panel_spacing = {
        'min': 8,
        'max': 36,
        'step': 2
    }
    
    NUM_PANELS = {
        'min': 1, 
        'max': 6
    }