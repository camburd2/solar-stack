import numpy as np
from stack import Stack
from config import Opt, Params
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

data = []


for n_panels in range(Opt.NUM_PANELS['min'], Opt.NUM_PANELS['max']+1):
    
    for w_panels in range(Opt.panel_width['min'], Opt.panel_width['max']+1, Opt.panel_width['step']):
        w_panels /= 12 # ft to in
        
        for s_panels in range(Opt.panel_spacing['min'], Opt.panel_spacing['max']+1, Opt.panel_spacing['step']):
            s_panels /= 12 # ft to in

            base_length = Params.X_MAX - Params.MAST_OFFSET

            # TODO: better config method/file, eventually inputs to interactive plotly graph too

            stack = Stack(num_panels=n_panels,
                          panel_spacing=s_panels,
                          panel_width=w_panels,
                          boat_length=40,
                          base_mast_offset=Params.MAST_OFFSET,
                          base_length=base_length,
                          base_height=1,
                          eff=.15,
                          cost_panel=Params.COST_PANEL,
                          cost_frame=Params.COST_FRAME)
            
                        
            # rotate heading and azimuth and calculate power at each, sum all
            total_power = 0
            n = 0

            for heading in range(0, 361, 5):
                for azimuth in range(15, 91, 5):
                    n+=1 

                    # update sun vector which also calculates the correct shadows
                    stack.update_sun_direction_vector(heading, azimuth)

                    # calculate the power based on panel area not in shadow
                    total_power += stack.power

            avg_power = total_power / n

            row = {'num': n_panels, 'width': w_panels, 'spacing': s_panels, 'power': avg_power, 'cost': stack.cost}
            data.append(row)


df = pd.DataFrame(data)

# Create array of budgets
min_budget = df['cost'].min()
max_budget = df['cost'].max()
budgets = np.linspace(min_budget, max_budget, 100)
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

results_df = pd.DataFrame(results)

# Unique values for discrete color mapping
unique_nums = sorted(results_df['num'].unique())
color_map = {num: color for num, color in zip(unique_nums, px.colors.qualitative.Set2)}

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
    title='Budget vs Maximum Achievable Power For Solar Stack Based on Sailboat Size Contraints and Estimated Panel Costs',
    xaxis_title='Budget',
    yaxis_title='Maximum Average Power',
    hovermode='x unified',
    coloraxis_colorbar_title='x value'
)

fig.show()