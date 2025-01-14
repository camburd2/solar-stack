import numpy as np
from stack import Stack
from config import Opt
import pandas as pd

data = []

for n_panels in range(Opt.NUM_PANELS['min'], Opt.NUM_PANELS['max']+1):
    
    for w_panels in range(Opt.panel_width['min'], Opt.panel_width['max']+1, Opt.panel_width['step']):
        w_panels /= 12 # ft to in
        
        for s_panels in range(Opt.panel_spacing['min'], Opt.panel_spacing['max']+1, Opt.panel_spacing['step']):
            s_panels /= 12 # ft to in

            stack = Stack(num_panels=n_panels,
                          panel_spacing=s_panels,
                          panel_width=w_panels)
                        
            # rotate heading and azimuth and calculate power at each, sum all
            total_power = 0
            n = 0

            for heading in range(0, 361, 5):
                for azimuth in range(15, 91, 5):
                    n+=1 

                    # update sun vector which also calculates the correct shadows
                    stack.update_sun_direction_vector(heading, azimuth)

                    # calculate the power based on panel area not in shadow
                    total_power += stack.calc_power(efficiency=.15)

            avg_power = total_power / n

            row = {'num': n_panels, 'width': w_panels, 'spacing': s_panels, 'power': avg_power, 'cost': stack.cost(20)}
            data.append(row)

df = pd.DataFrame(data)

import plotly.express as px
import plotly.graph_objects as go
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
"""
# Assuming `df` is created as described in your initial script
# Normalize width for opacity scaling
df['width_normalized'] = (df['width'] - df['width'].min()) / (df['width'].max() - df['width'].min())

# Unique values for discrete color mapping
unique_nums = sorted(df['num'].unique())
color_map = {num: color for num, color in zip(unique_nums, px.colors.qualitative.Set2)}

# Initialize figure
fig = go.Figure()

# Add scatter plots for each `num` value
for num in unique_nums:
    subset = df[df['num'] == num]
    fig.add_trace(go.Scatter(
        x=subset['cost'],
        y=subset['power'],
        mode='markers',
        marker=dict(
            size=5 + (15 * (subset['spacing'] - df['spacing'].min()) / (df['spacing'].max() - df['spacing'].min())),
            color=color_map[num],
            opacity=subset['width_normalized'],
            line=dict(width=1, color='DarkSlateGrey')
        ),
        name=f"Num: {num}",
        legendgroup='num',
        legendgrouptitle=dict(text="Number of Panels") if num == unique_nums[0] else None,
        showlegend=True,
        text=[
            f"Num: {row['num']}<br>Spacing: {row['spacing']:.2f}<br>Width: {row['width']:.2f}<br>Cost: {row['cost']:.2f}<br>Power: {row['power']:.2f}"
            for _, row in subset.iterrows()
        ],
        hoverinfo='text'

    ))

# Add size (spacing) reference points to legend
spacing_values = np.linspace(df['spacing'].min(), df['spacing'].max(), 3)
for spacing in spacing_values:
    size = 5 + (15 * (spacing - df['spacing'].min()) / (df['spacing'].max() - df['spacing'].min()))
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=size, color='black'),
        name=f"Spacing: {spacing:.2f} in",
        legendgroup='spacing',
        legendgrouptitle=dict(text="Spacing (Point Size)") if spacing == spacing_values[0] else None,
        showlegend=True
    ))

# Add opacity (width) reference points to legend
width_values = np.linspace(df['width'].min(), df['width'].max(), 3)
for width in width_values:
    opacity = (width - df['width'].min()) / (df['width'].max() - df['width'].min())
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(size=10, color='black', opacity=opacity),
        name=f"Width: {width:.2f} in",
        legendgroup='width',
        legendgrouptitle=dict(text="Width (Opacity)") if width == width_values[0] else None,
        showlegend=True
    ))

# Layout updates
fig.update_layout(
    title="Cost vs Power Analysis",
    xaxis_title="Cost (USD)",
    yaxis_title="Power (W)",
    legend=dict(
        groupclick="toggleitem",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.02,
        itemsizing="constant"
    ),
    template="plotly_white"
)

fig.show()
"""

import numpy as np
import pandas as pd

# Assuming your dataframe is called 'df'

# Create array of budgets to analyze
min_budget = df['cost'].min()
max_budget = df['cost'].max()
budgets = np.linspace(min_budget, max_budget, 100)  # 50 points, adjust as needed
power_amts = set()

# Find max P and parameters for each budget
results = []
for budget in budgets:
    # Filter points within budget
    valid_points = df[df['cost'] <= budget]
    
    if len(valid_points) > 0:
        # Get row with maximum P for this budget
        best_row = valid_points.loc[valid_points['power'].idxmax()]
        p = best_row['power']

        if p not in power_amts:
            power_amts.add(p)
            results.append({
                'budget': budget,
                'max_P': best_row['power'],
                'num': best_row['num'],
                'width': best_row['width'],
                'spacing': best_row['spacing'],
                'actual_cost': best_row['cost']
            })

# Convert to DataFrame
results_df = pd.DataFrame(results)

"""
fig = go.Figure()

# Add the line with color gradient based on x
fig.add_trace(
    go.Scatter(
        x=results_df['budget'],
        y=results_df['max_P'],
        mode='markers',
        marker=dict(
            color=results_df['num'],  # Use 'num' for color
            colorscale='Plasma',        # Red-Blue colorscale
            size=15,                  # Marker size
            showscale=True            # Show color scale legend
        ),
        text=[  # Add hover information
            f"Budget: {b:.2f}<br>Max P: {p:.2f}<br>Num: {n}"
            for b, p, n in zip(results_df['budget'], results_df['max_P'], results_df['num'])
        ],
        hoverinfo='text'  # Display custom hover info
    )
)"""

# Unique values for discrete color mapping
unique_nums = sorted(results_df['num'].unique())
color_map = {num: color for num, color in zip(unique_nums, px.colors.qualitative.Set2)}

# Initialize figure
fig = go.Figure()

for num in unique_nums:
    subset = results_df[results_df['num'] == num]
    fig.add_trace(go.Scatter(
        x=subset['budget'],
        y=subset['max_P'],
        mode='markers',
        marker=dict(
            size= 15,
            color=color_map[num],
        ),
        name=f"Num: {num}",
        legendgroup='num',
        legendgrouptitle=dict(text="Number of Panels") if num == unique_nums[0] else None,
        showlegend=True,
        text=[
            f"Num: {row['num']}<br>Spacing: {row['spacing']:.2f}<br>Width: {row['width']:.2f}<br>Cost: {row['budget']:.2f}<br>Power: {row['max_P']:.2f}"
            for _, row in subset.iterrows()
        ],
        hoverinfo='text'

    ))

# Update layout
fig.update_layout(
    title='Budget vs Maximum Achievable Power Based on Sailboat Contraints (width, length, height of panels) and Costs (panel size, frame size)',
    xaxis_title='Budget',
    yaxis_title='Maximum Power',
    hovermode='x unified',
    coloraxis_colorbar_title='x value'
)

# Show the figure
fig.show()

# This also assumes a fixed cost per panel, panel perimeter (frame) cost and panel area cost