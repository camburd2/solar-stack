from config import Params
import plotly.graph_objs as go
import numpy as np

from plotting import create_surface, rect_surfaces

class Panel:
    # TODO: rewrite this and intersection fucntions
    def __init__(self, panel_dims):
        self.x0 = panel_dims[0]
        self.y0 = panel_dims[1]
        self.x1 = panel_dims[2]
        self.y1 = panel_dims[3]
        self.z = panel_dims[4]

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
        self.params = Params()
        self.num_panels = num_panels
        self.panel_spacing = panel_spacing
        self.panel_width = panel_width
        
        self.total_panel_area = 0
        self.shadow_dims = []

        self.sun_direction_vector = (0,0,0)
        self.azimuth = 0
        self.heading = 0

        self.boat_length = boat_length
        self.mast_height=1.1*boat_length

        self.eff=eff
        self.cost_panel=cost_panel
        self.cost_frame=cost_frame
        
        # Create elements
        self.panel_dims = self._calc_all_panel_dims(
            base_mast_offset=base_mast_offset,
            base_length=base_length,
            base_height=base_height,
            mast_height=self.mast_height
        )
        self.panel_midpoints = self._calc_panel_midpoints()

    def _calc_offsets(self, mast_offset, mast_to_basex1, mast_height):
        front_offset = (self.panel_spacing * mast_to_basex1) / mast_height
        back_offset = (self.panel_spacing * mast_offset) / mast_height
        return front_offset, back_offset
    
    def _calc_all_panel_dims(self, base_mast_offset, base_length, base_height, mast_height):
        # mast radius is .3
        # mast center is (0.55*boat_length, panel_width/2) so we need to move panels in x
        deck_x_offset = self.boat_length*.55  # deal with this input later - don't leave hardcoded

        base_x0 = base_mast_offset  # base start x
        base_x1 = base_mast_offset + base_length

        # offsets based on geometry of sailboat
        front_offset, back_offset = self._calc_offsets(base_mast_offset, base_x1, mast_height)


        panel_dims = []
        for i in range(self.num_panels):
            x0 = base_x0 - i * back_offset + deck_x_offset
            x1 = base_x1 - i * front_offset + deck_x_offset
            y0 = 0
            y1 = self.panel_width
            
            z = i * self.panel_spacing + base_height

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
        if elevation_angle == 0: return 0

        # solar constant is amount of solar energy that reaches a unit area perpendicular to the sun's rays, measured at a distance of one astronomical unit from the sun
        solar_constant = 1361  # W/m²  
        elev_rad = np.radians(elevation_angle)
        AM= 1 / np.sin(elev_rad)
        irradiance = solar_constant * np.sin(elev_rad) * 0.7**(AM**0.678)

        return irradiance

    @property
    def power(self):
        exposed_area = self.total_panel_area - self.total_shadow_area
        irradiance = self._solar_irradiance(self.azimuth)

        print(self.total_panel_area)

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