import numpy as np
import plotly.graph_objs as go
from stack import Stack, StackConfig
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def calc_power(stack, azimuth_range, elevation_range, degree_step, avg=True):
        """calculate average power over range or creates dataset for power values over range"""
        azimuths = range(azimuth_range[0], azimuth_range[1] + 1, degree_step)
        elevations = range(elevation_range[0], elevation_range[1] + 1, degree_step)

        results = []
        for azimuth in azimuths:
                for elevation in elevations:
                    stack.update_sun_direction_vector(elevation, azimuth)
                    results.append({'azimuth': azimuth, 'elevation': elevation, 'power': stack.power})

        if avg: 
            return sum(r['power'] for r in results) / len(results)
        else:
            return pd.DataFrame(results)

def max_power_budget(df, n_budget_samples=100):
     
    # Create array of budgets
    min_budget = df['cost'].min()
    max_budget = df['cost'].max()
    budgets = np.linspace(min_budget, max_budget, n_budget_samples)
    power_amts = set()

    # find max power and params for each budget
    results = []
    for budget in budgets:
        valid_points = df[df['cost'] <= budget]  # points within budget
        
        if len(valid_points) > 0:
            # row with maximum P for this budget
            best_row = valid_points.loc[valid_points['power'].idxmax()]
            power_val = best_row['power']

            if power_val not in power_amts:
                power_amts.add(power_val)
                results.append({
                    'budget': budget,
                    'max_P': power_val,
                    'num': best_row['num'],
                    'width': best_row['width'],
                    'spacing': best_row['spacing'],
                    'actual_cost': best_row['cost']
                })
    return pd.DataFrame(results)

def pow_budget_fig(df):
    unique_nums = sorted(df['num'].unique())
    color_map = {num: color for num, color in zip(unique_nums, px.colors.qualitative.Set2)}
    fig = go.Figure()
    last_point = None

    for num in unique_nums:
        subset = df[df['num'] == num]

        if last_point:
            fig.add_trace(go.Scatter(
                x=[last_point['x'], subset['budget'].iloc[0]],
                y=[last_point['y'], last_point['y']],
                mode='lines',
                line=dict(color=color_map[num-1]),
                showlegend=False,
            ))

        hover_texts = [
            f"Num: {row['num']}<br>Spacing: {row['spacing']:.2f}<br>Width: {row['width']:.2f}<br>Cost: {row['budget']:.2f}<br>Power: {row['max_P']:.2f}"
            for _, row in subset.iterrows()
        ]
        
        # Add markers
        fig.add_trace(go.Scatter(
            x=subset['budget'],
            y=subset['max_P'],
            mode='markers',
            marker=dict(size=15, color=color_map[num]),
            name=f"{int(num)}",
            legendgroup='num',
            legendgrouptitle=dict(text="Number of Panels") if num == unique_nums[0] else None,
            showlegend=True,
            text=hover_texts,
            hoverinfo='text'
        ))
        
    # Add horizontal lines to next points
    for i in range(len(df)-1):
        curr, next = df.iloc[i], df.iloc[i+1]
        fig.add_trace(go.Scatter(
            x=[curr['budget'], next['budget']],
            y=[curr['max_P'], curr['max_P']],
            mode='lines',
            line=dict(color=color_map[curr['num']]),
            showlegend=False
        ))

    fig.update_layout(
        title='Budget vs Maximum Achievable Power For Solar Stack',
        xaxis_title='Budget',
        yaxis_title='Maximum Average Power',
        coloraxis_colorbar_title='x value'
    )

    return fig

def create_budget_pow_fig(
        config: StackConfig,
        num_range,
        width_range, 
        spacing_range, 
        n_step=1, w_step=1, s_step=1,
        azimuth_range = (90, 270),  # front to back (side to side is symmetrical, front to back is not)
        elevation_range = (0, 90),
        degree_step = 15
    ):

    data = []
    for num_panels in range(num_range[0], num_range[1]+1, n_step):
        for width_panels in np.arange(width_range[0], width_range[1], w_step):
            for space_panels in np.arange(spacing_range[0], spacing_range[1], s_step):
                
                config.num_panels = num_panels
                config.panel_spacing = space_panels
                config.panel_width = width_panels
                stack = Stack(config)
                
                avg_power = calc_power(stack, azimuth_range, elevation_range, degree_step, avg=True)
                data.append({'num': num_panels, 
                             'width': width_panels, 
                             'spacing': space_panels,
                             'power': avg_power,
                             'cost': stack.cost})
    avg_power_cost_df = pd.DataFrame(data)
    max_power_budget_df = max_power_budget(avg_power_cost_df)
    fig = pow_budget_fig(max_power_budget_df)
    return fig

def create_heatmap(
        stack,
        azimuth_range = (90, 270),  # front to back
        elevation_range = (0, 90),
        degree_step = 1
    ):

    df = calc_power(stack, azimuth_range, elevation_range, degree_step, avg=False)

    fig = go.Figure(data=go.Heatmap(
        z=df['power'],
        x=df['azimuth'],
        y=df['elevation'],
        colorscale='Viridis',
        colorbar=dict(title='Power')
    ))
    
    fig.update_layout(
        title='Power Distribution by Sun Position For Current Stack Configuration',
        xaxis_title='Azimuth',
        yaxis_title='Elevation'
    )
    
    return fig


if __name__ == "__main__":
    default_config = StackConfig()

    budget_pow_fig = create_budget_pow_fig(
        config=default_config,
        num_range=(1,5),
        width_range=(1,2),
        spacing_range=(1,3),
        n_step=1, w_step=.5, s_step=.5,
        azimuth_range=(90,270),  # front to back of boat
        elevation_range=(15,90),  # start at 15deg for more realisitc avg pow
        degree_step=5
    )

    heatmap_fig = create_heatmap(stack=Stack(default_config))

    heatmap_fig.show()