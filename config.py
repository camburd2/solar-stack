class Params:
    # Sailboat parameters
    MAST_HEIGHT = 40
    MAST_OFFSET = 3
    X_MAX = 8

    # Cost parameters
    COST_FRAME = 10  # $/ft
    COST_PANEL = 10  # $/ft^2

class OptBounds:
    PANEL_WIDTH_BOUNDS = (12, 36)    # min, max [in]
    PANEL_SPACING_BOUNDS = (12, 48)  # min, max [in]
    NUM_PANELS_BOUNDS = (1, 6)       # min, max panels