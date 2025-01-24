import plotly.graph_objs as go
import numpy as np
import plotting
from dataclasses import dataclass

@dataclass
class StackConfig:
    num_panels: int = 6
    panel_spacing: float = 3
    panel_width: float = 2
    boat_length: float = 40
    base_mast_offset: float = 4
    base_length: float = 5
    base_height: float = 1
    eff: float = 0.15
    cost_panel: float = 5
    cost_frame: float = 5
        
class Panel:
    def __init__(self, x0, x1, y0, y1, z):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.z = z
    
    def midpoint(self):
        mid_x = (self.x1 + self.x0)/2
        mid_y = self.y1/2
        return mid_x, mid_y, self.z
    
    def area(self):
        return (self.x1 - self.x0) * (self.y1 - self.y0)
        
class Stack:
    def __init__(self, config):
        self.num_panels = config.num_panels
        self.panel_spacing = config.panel_spacing
        self.panel_width = config.panel_width
        self.boat_length = config.boat_length
        self.base_mast_offset = config.base_mast_offset
        self.base_length = config.base_length
        self.base_height = config.base_height
        self.eff = config.eff
        self.cost_panel = config.cost_panel
        self.cost_frame = config.cost_frame

        self.shadows = []
        self.sun_direction_vector = (0,0,0)
        self.elevation = 0
        self.azimuth = 0
        self.total_panel_area = 0
        self.mast_height = 1.1 * config.boat_length

        # create panels and midpoints for sun vectors
        self.panels = self._create_panels()
        self.panel_midpoints = [panel.midpoint() for panel in self.panels]

    def _calc_offsets(self, mast_to_basex1):
        """calculate front and back offsets based on mast and base panel geometry"""
        front_offset = self.panel_spacing * mast_to_basex1 / self.mast_height
        back_offset  = self.panel_spacing * self.base_mast_offset / self.mast_height
        return front_offset, back_offset
    
    def _create_panels(self):
        """create all panels based on sailboat geometry and spacing"""
        mast_x = 0.55 * self.boat_length + .3  # mast center, radius = .3

        # base panel positions
        base_x0 = mast_x + self.base_mast_offset
        base_x1 = base_x0 + self.base_length

        # front and back offsets based on angles from base panel to mast top
        front_offset, back_offset = self._calc_offsets(base_x1 - mast_x)
        
        panels = []
        for i in range(self.num_panels):
            # panel positions based on index (move back toward mast as i increases)
            x0 = base_x0 - i * back_offset
            x1 = base_x1 - i * front_offset
            z = i * self.panel_spacing + self.base_height  # panel height

            # create panel and accumulate total area
            panel = Panel(x0, x1, 0, self.panel_width, z)
            self.total_panel_area += panel.area()
            panels.append(panel)

        return panels
        
    def _calc_intersection_pt(self, upper_point, lower_z):
        """calculate where an upper panel intersects with a lower panel using a direction vector"""
        upper_z = upper_point[2]
        direction_vec_z = self.sun_direction_vector[2]
        t = (lower_z - upper_z) / direction_vec_z

        res_x = upper_point[0] + t * self.sun_direction_vector[0]
        res_y = upper_point[1] + t * self.sun_direction_vector[1]

        return res_x, res_y
    
    def _calc_shadow(self, intersect_pt, len_upper, lower):   
        """calculate the corner locations for a single shadow
        
        args:
            intersect_pt: pt on lower panel plane where upper panel corner intersects 
            len_upper: length of upper panel
            lower: lower panel

        returns:
            panel object to represent shadow
        """    
        sx0, sy0 = intersect_pt
        sx1 = sx0 + len_upper
        sy1 = sy0 + self.panel_width

        shadow_x0 = max(sx0, lower.x0)
        shadow_y0 = max(sy0, lower.y0)
        shadow_x1 = min(sx1, lower.x1)
        shadow_y1 = min(sy1, lower.y1)

        if (shadow_x0 >= shadow_x1) or (shadow_y0 >= shadow_y1): 
            return False
        
        return Panel(shadow_x0, shadow_x1, shadow_y0, shadow_y1, lower.z+.001)    

    def _update_shadows(self): 
        """update the shadow locations based on sun position relative to panel stack"""   
        if self.elevation <= 0: 
            return   
          
        self.shadows = []

        for i in range(len(self.panels) - 1):
            lower_panel = self.panels[i]
            upper_panel = self.panels[i+1]
            upper_corner_pt = (upper_panel.x0, upper_panel.y0, upper_panel.z)
            
            # use sun vector to find intersection point of upper panel corner on lower panel
            intersection_pt = self._calc_intersection_pt(upper_corner_pt, lower_panel.z)
            length_upper = upper_panel.x1 - upper_panel.x0
            shadow = self._calc_shadow(intersection_pt, length_upper, lower_panel)

            if shadow:
                self.shadows.append(shadow)

    def update_sun_direction_vector(self, elevation, azimuth):
        """update sun direction vector and update shadows"""
        theta = np.radians(azimuth)
        phi = np.radians(elevation)

        # calc direction components
        dx = np.cos(phi) * np.sin(theta)
        dy = np.cos(phi) * np.cos(theta)
        dz = np.sin(phi)

        # update sun direction vector and sun angles
        self.sun_direction_vector = (dx, dy, dz)
        self.elevation = elevation
        self.azimuth = azimuth

        # recalc shadows with new direction
        self._update_shadows()

    def create_panel_surfaces(self):
        """return a list of 3d plotly surfaces for the solar panels"""
        return plotting.rect_surfaces(self.panels, 'greens')
    
    def create_shadow_surfaces(self):
        """update shadows and return shadows as a list of 3d ploty surfaces"""
        return plotting.rect_surfaces(self.shadows, 'gray')
    
    def create_sun_lines(self):
        dx, dy, dz = self.sun_direction_vector
        line_length = self.panel_spacing
        lines = []

        for i, mid in enumerate(self.panel_midpoints):
            line = go.Scatter3d(
                x=[mid[0], mid[0] + dx * line_length],
                y=[mid[1], mid[1] + dy * line_length],
                z=[mid[2], mid[2] + dz * line_length],
                mode='lines',
                line=dict(color='yellow', width=3),
                showlegend=(i==0),
                name='Sun Direction Vector'
            )
            lines.append(line)
        
        return lines
    
    @property
    def total_shadow_area(self):
        return sum(shadow.area() for shadow in self.shadows)
  
    @property
    def solar_irradiance(self):
        """calculate solar irradiance based on elevation"""
        if self.elevation == 0: 
            return 0

        solar_constant = 1361  # W/m²  
        elev_rad = np.radians(self.elevation)
        air_mass = 1 / np.sin(elev_rad)
        irradiance = solar_constant * np.sin(elev_rad) * 0.7 ** (air_mass ** 0.678)

        return irradiance

    @property
    def power(self):
        """calculate total power of stack with current sun position"""
        exposed_area = (self.total_panel_area - self.total_shadow_area) * 0.092903  # convert ft^2 to m^2        
        power = exposed_area * self.eff * self.solar_irradiance
        return int(power)
    
    @property
    def cost(self):
        """total cost of all panels and frames"""
        sum_panel_lengths = self.total_panel_area / self.panel_width
        perimeter = 2 * (sum_panel_lengths + self.panel_width)

        frame_cost = self.cost_frame * perimeter
        panel_cost = self.cost_panel * self.total_panel_area

        return int(panel_cost + frame_cost)