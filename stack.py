from config import Params
import plotly.graph_objs as go
import numpy as np

from plotting import create_surface, rect_surfaces

class Panel:
    def __init__(self, panel_dims):
        self.x0 = panel_dims[0]
        self.y0 = panel_dims[1]
        self.x1 = panel_dims[2]
        self.y1 = panel_dims[3]
        self.z = panel_dims[4]

class Stack:
    def __init__(self, num_panels, panel_spacing, panel_width):
        self.params = Params()
        self.num_panels = num_panels
        self.panel_spacing = panel_spacing
        self.panel_width = panel_width
        
        self.total_panel_area = 0
        self.shadow_dims = []

        self.sun_direction_vector = (0,0,0)
        self.azimuth = 0
        self.heading = 0
        
        # Create elements
        self.panel_dims = self._calc_all_panel_dims()
        self.panel_midpoints = self._calc_panel_midpoints()

    def _calc_offsets(self):
        front_offset = (self.panel_spacing * self.params.X_MAX) / self.params.MAST_HEIGHT
        back_offset = (self.panel_spacing * self.params.MAST_OFFSET) / self.params.MAST_HEIGHT
        return front_offset, back_offset
    
    def _calc_all_panel_dims(self):
        front_offset, back_offset = self._calc_offsets()
        base_x0 = self.params.MAST_OFFSET
        base_x1 = self.params.X_MAX

        panel_dims = []
        for i in range(self.num_panels):
            x0 = base_x0 - i * back_offset
            x1 = base_x1 - i * front_offset
            y0, y1 = 0, self.panel_width
            z = i * self.panel_spacing

            self.total_panel_area += (x1-x0)*self.panel_width
            panel_dims.append((x0, y0, x1, y1, z))
        return panel_dims
    
    def create_panel_surfaces(self):
        return rect_surfaces(self.panel_dims, 'greens')

    def update_sun_direction_vector(self, heading, azimuth):
        theta = np.radians(heading)
        phi = np.radians(azimuth)
        dx = np.cos(phi) * np.sin(theta)
        dy = np.cos(phi) * np.cos(theta)
        dz = np.sin(phi)

        self.sun_direction_vector = (dx, dy, dz)
        self.azimuth = azimuth
        self.heading = heading

        self._update_shadow_dims()

    def _calc_panel_midpoints(self):
        mids = []
        for panel in self.panel_dims:
            mid_x = (panel[0] + panel[2]) / 2
            mid_y = self.panel_width / 2
            mids.append({'x': mid_x, 'y': mid_y, 'z': panel[4]}) 
        return mids

    def create_sun_lines(self):
        dx, dy, dz = self.sun_direction_vector
        line_length = self.panel_spacing
        lines = []

        for mid in self.panel_midpoints:
            line = go.Scatter3d(
                x=[mid['x'], mid['x'] + dx * line_length],
                y=[mid['y'], mid['y'] + dy * line_length],
                z=[mid['z'], mid['z'] + dz * line_length],
                mode='lines',
                line=dict(color='yellow', width=3),
                showlegend=False
            )
            lines.append(line)
        
        return lines
    
    def _calc_intersection_pt(self, point, h):
        z0 = point[2]
        dz = self.sun_direction_vector[2]
        t = (h-z0)/dz

        new_x = point[0] + t*self.sun_direction_vector[0]
        new_y = point[1] + t*self.sun_direction_vector[1]
        new_z = point[2] + t*self.sun_direction_vector[2]

        return (new_x, new_y, new_z)
    
    def calc_shadow(self, intersect_pt, panel_num, lower):
        x0, y0, x1, y1, z = self.panel_dims[panel_num]
        len_upper = x1 - x0
        
        sx0 = intersect_pt[0]
        sx1 = sx0 + len_upper
        sy0 = intersect_pt[1]
        sy1 = intersect_pt[1] + self.panel_width

        shadow_x0 = max(sx0, lower.x0)
        shadow_y0 = max(sy0, lower.y0)
        shadow_x1 = min(sx1, lower.x1)
        shadow_y1 = min(sy1, lower.y1)

        if shadow_x0 > shadow_x1: 
            return False
        if shadow_y0 > shadow_y1:
            return False
        
        return (shadow_x0, shadow_y0, shadow_x1, shadow_y1, z+.001)    

    def _update_shadow_dims(self):
        self.shadow_dims = []

        for i in range(len(self.panel_dims) - 1):
            lower = Panel(self.panel_dims[i])
            upper = Panel(self.panel_dims[i+1])
            point = (upper.x0, upper.y0, upper.z)

            shadow = False

            if self.azimuth > 0:
                pt_lower = self._calc_intersection_pt(point, lower.z)
                shadow = self.calc_shadow(pt_lower, i, lower)

                if shadow:
                    self.shadow_dims.append(shadow)

    def create_shadow_surfaces(self):
        self._update_shadow_dims()
        return rect_surfaces(self.shadow_dims, 'gray')

    @property
    def total_shadow_area(self):
        area = 0
        for shadow in self.shadow_dims:
            length = shadow[2] - shadow[0]
            width = shadow[3] - shadow[1]
            area += length * width   
        return area

    def _solar_irradiance(self, elevation_angle):
        '''Calculate solar irradiance.

        Args:
            elevation_angle (int): Angle above horizon [degrees]
        
        Returns:
            float: Solar irradiance [W/m^2] 
        '''
        # solar constant is amount of solar energy that reaches a unit area perpendicular to the sun's rays, measured at a distance of one astronomical unit from the sun

        # to account for rays through atmosphere:
        max_normal_irradiance_ground = 1000 # W/m^2
        elevation_radians = np.radians(elevation_angle)
        irradiance = max_normal_irradiance_ground * np.sin(elevation_radians)
        return irradiance

    def calc_power(self, efficiency):
        exposed_area = self.total_panel_area - self.total_shadow_area
        irradiance = self._solar_irradiance(self.azimuth)

        exposed_area *= 0.092903 #m^2
        
        power = exposed_area * efficiency * irradiance
        return power
    
    def cost(self, fixed_per_panel):
        # width is same for all panels
        sum_panel_lengths = self.total_panel_area / self.panel_width
        perimeter = 2 * (sum_panel_lengths + self.panel_width)

        return self.total_panel_area * Params.COST_PANEL + perimeter * Params.COST_FRAME + fixed_per_panel*self.num_panels