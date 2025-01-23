import plotly.graph_objs as go
import numpy as np
import plotting


class Panel:
    def __init__(self, x0, x1, y0, y1, z):
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        self.z = z
    
    @property
    def midpoint(self):
        mid_x = (self.x1 + self.x0)/2
        mid_y = self.y1/2
        return (mid_x, mid_y, self.z)
    
    @property
    def area(self):
        return (self.x1-self.x0)*(self.y1-self.y0)
        

class Stack:
    def __init__(self, 
                 num_panels, 
                 panel_spacing, 
                 panel_width, 
                 boat_length,
                 base_mast_offset,
                 base_length,
                 base_height,
                 eff,
                 cost_panel,
                 cost_frame
        ):
        self.num_panels = num_panels
        self.panel_spacing = panel_spacing
        self.panel_width = panel_width
        
        self.total_panel_area = 0
        self.shadows = []

        self.sun_direction_vector = (0,0,0)
        self.elevation = 0
        self.azimuth = 0

        self.boat_length= boat_length
        self.mast_height= 1.1 * boat_length

        self.eff=eff
        self.cost_panel=cost_panel
        self.cost_frame=cost_frame
        
        # Create elements
        self.panels = self._calc_all_panels(
            base_mast_offset=base_mast_offset,
            base_length=base_length,
            base_height=base_height,
        )
        self.panel_midpoints = [panel.midpoint for panel in self.panels]

    def _calc_offsets(self, mast_offset, mast_to_basex1):
        front_offset = (self.panel_spacing * mast_to_basex1) / self.mast_height
        back_offset = (self.panel_spacing * mast_offset) / self.mast_height
        return front_offset, back_offset
    
    def _calc_all_panels(self, base_mast_offset, base_length, base_height):
        # mast center is (0.55*boat_length, panel_width/2) so we need to move panels in +x direction
        # mast radius is .3
        mast_x = 0.55 * self.boat_length + .3

        # base panel starts at some offset from mast
        base_x0 = mast_x + base_mast_offset
        base_x1 = base_x0 + base_length

        # offsets based on geometry of sailboat
        front_offset, back_offset = self._calc_offsets(mast_offset= base_mast_offset,
                                                       mast_to_basex1= base_x1 - mast_x)
        
        panels = []
        for i in range(self.num_panels):
            x0 = base_x0 - i * back_offset
            x1 = base_x1 - i * front_offset
            y0 = 0
            y1 = self.panel_width
            z = i * self.panel_spacing + base_height

            panel = Panel(x0, x1, y0, y1, z)
            self.total_panel_area += panel.area
            panels.append(panel)

        return panels
    
    def update_sun_direction_vector(self, azimuth, elevation):
        theta = np.radians(azimuth)
        phi = np.radians(elevation)
        dx = np.cos(phi) * np.sin(theta)
        dy = np.cos(phi) * np.cos(theta)
        dz = np.sin(phi)

        self.sun_direction_vector = (dx, dy, dz)
        self.elevation = elevation
        self.azimuth = azimuth

        self._update_shadows()

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
    
    def _calc_intersection_pt(self, point, h):
        z0 = point[2]
        dz = self.sun_direction_vector[2]
        t = (h-z0)/dz

        new_x = point[0] + t*self.sun_direction_vector[0]
        new_y = point[1] + t*self.sun_direction_vector[1]
        new_z = point[2] + t*self.sun_direction_vector[2]

        return (new_x, new_y, new_z)
    
    def _calc_shadow(self, intersect_pt, len_upper, lower):       
        sx0 = intersect_pt[0]
        sx1 = sx0 + len_upper
        sy0 = intersect_pt[1]
        sy1 = intersect_pt[1] + self.panel_width

        shadow_x0 = max(sx0, lower.x0)
        shadow_y0 = max(sy0, lower.y0)
        shadow_x1 = min(sx1, lower.x1)
        shadow_y1 = min(sy1, lower.y1)

        if (shadow_x0 > shadow_x1) or (shadow_y0 > shadow_y1): 
            return False
        
        return Panel(shadow_x0, shadow_x1, shadow_y0, shadow_y1, lower.z+.001)    

    def _update_shadows(self):
        self.shadows = []

        for i in range(len(self.panels) - 1):
            lower = self.panels[i]
            upper = self.panels[i+1]
            point = (upper.x0, upper.y0, upper.z)
            shadow = False

            if self.elevation > 0:
                pt_lower = self._calc_intersection_pt(point, lower.z)
                len_upper = upper.x1-upper.x0
                shadow = self._calc_shadow(pt_lower, len_upper, lower)

                if shadow:
                    self.shadows.append(shadow)

    def create_panel_surfaces(self):
        return plotting.rect_surfaces(self.panels, 'greens')
    
    def create_shadow_surfaces(self):
        self._update_shadows()
        return plotting.rect_surfaces(self.shadows, 'gray')

    @property
    def total_shadow_area(self):
        area = 0
        for shadow in self.shadows:
            area += shadow.area
        return area
  
    @property
    def _solar_irradiance(self):
        if self.elevation == 0: return 0

        # solar constant is amount of solar energy that reaches a unit area perpendicular to the sun's rays, measured at a distance of one astronomical unit from the sun
        solar_constant = 1361  # W/m²  
        elev_rad = np.radians(self.elevation)
        AM= 1 / np.sin(elev_rad)
        irradiance = solar_constant * np.sin(elev_rad) * 0.7**(AM**0.678)

        return irradiance

    @property
    def power(self):
        exposed_area = self.total_panel_area - self.total_shadow_area
        irradiance = self._solar_irradiance
        exposed_area *= 0.092903 #m^2
        
        power = exposed_area * self.eff * irradiance
        return int(power)
    
    @property
    def cost(self):
        # width is same for all panels
        sum_panel_lengths = self.total_panel_area / self.panel_width
        perimeter = 2 * (sum_panel_lengths + self.panel_width)

        frame_cost = self.cost_frame * perimeter
        panel_cost = self.cost_panel * self.total_panel_area

        return int(panel_cost + frame_cost)