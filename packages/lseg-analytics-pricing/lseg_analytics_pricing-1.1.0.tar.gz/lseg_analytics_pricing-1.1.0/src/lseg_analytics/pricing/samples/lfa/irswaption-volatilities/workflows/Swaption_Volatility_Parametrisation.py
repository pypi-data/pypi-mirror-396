from lseg_analytics.pricing.market_data import irswaption_volatility  as sv

import plotly.graph_objects as go
import pandas as pd
import datetime as dt
import json
from IPython.display import display

print("Step 1: Creating Cube Definition...")
# Select currency and reference rate for caplets
currency = "USD"
index_name = "SOFR"

# Create surface definition object
cube_definition = sv.VolatilityCubeDefinition(
        instrument_code = currency,
        index_name = index_name,
        index_tenor  = "ON",
  
        # discounting_type = sv.DiscountingTypeEnum.OisDiscounting  # Options: LiborDiscounting, OisDiscounting
        )
print(f"   Instrument: {cube_definition.underlying_swap_structure}")

print("Step 2: Advanced Cube Parameters Configuration...")

# This section demonstrates how cube parameters can be configured for different market conditions

cube_parameters = sv.VolatilityCubeSurfaceParameters(
    calculation_date=dt.datetime(2025, 1, 18),
    
    # SABR Model Parameters
    beta=0.45,                                    # SABR beta parameter (0-1, default 0.45), Controls volatility smile shape
    
    # Volatility Configuration
    input_volatility_type=sv.InputVolatilityTypeEnum.NORMAL_VOLATILITY, #Options: LOG_NORMAL_VOLATILITY, NORMAL_VOLATILITY
    output_volatility_type=sv.OutputVolatilityTypeEnum.NORMAL_VOLATILITY, #Options: same as above

    # Volatility Sources
    include_caplets_volatility=True,              # Use both swaptions and caplets
    
    # Negative Rates Handling
    shift_percent=1.0,                            # 1% shift for negative rates support
    stripping_shift_percent=0.5,                 # Additional shift for caplet stripping

    # Market Data Sources
    source="ICAP",                           # Specific volatility source
    
    # Surface Layout
    x_axis=sv.XAxisEnum.STRIKE,
    y_axis=sv.YAxisEnum.TENOR, 
    z_axis=sv.ZAxisEnum.EXPIRY
)
print(f"   Cube Parameters: {json.dumps(cube_parameters.as_dict(), indent=4)}")

print("Step 3: Create request item...")
# Create the main request object with basic configuration
request_item = sv.VolatilityCubeSurfaceRequestItem(
        surface_tag = f"{currency}_{index_name}_Swaption_volatility_cube",
        underlying_definition = cube_definition,
        underlying_type = sv.CurvesAndSurfacesUnderlyingTypeEnum.Swaption,
        surface_parameters=cube_parameters,
        surface_layout = sv.SurfaceOutput(
            format = sv.FormatEnum.LIST,  # Options: LIST (MATRIX and NDIMENSIONAL_ARRAY return an error)
        )
    )
print(f"   Request Item: {json.dumps(request_item.as_dict(), indent=4)}")

# Execute the calculation using the calculate function
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response = sv.calculate(universe=[request_item])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Cube data points available: {len(surface_data['surface'])}")
    else:
        print("   No cube data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Plotting utils

def prepare_volatility_surface_from_list(surface_data, slice_by = 'Expiry', slice_target = '1M', x_axis = 'Relative Strike (%)', y_axis = 'SwapTenor', point_value = 'Normal Vol (bp)'):
    """
    Prepare the volatility surface DataFrame from the provided surface data.
    """

    def sort_tenor_index(tenor_list):
        """Sort tenors in proper chronological order (months first, then years)"""
        def tenor_to_months(tenor):
            if 'M' in tenor:
                return int(tenor.replace('M', ''))
            elif 'Y' in tenor:
                return int(tenor.replace('Y', '')) * 12
            else:
                return float('inf')  # Put unknown formats at the end
        
        return sorted(tenor_list, key=tenor_to_months)

    vol_cube_points_df = pd.DataFrame(surface_data['surface'], columns = surface_data['headers'])

    surface_slice_df = vol_cube_points_df[vol_cube_points_df[slice_by] == slice_target]

    # Convert the filtered slice into a pivot table with the desired structure
    surface_slice_df = surface_slice_df.pivot(index=y_axis, columns=x_axis, values=point_value)

    # Sort columns first (x_axis values) - convert to float and sort ascending
    surface_slice_df.columns = surface_slice_df.columns.astype(float)
    surface_slice_df = surface_slice_df.sort_index(axis=1)  # Sort columns

    # Then sort the index (y_axis values) properly using tenor sorting logic
    sorted_index = sort_tenor_index(surface_slice_df.index.tolist())
    surface_slice_df = surface_slice_df.reindex(sorted_index)

    # Convert point values to float and round to 2 decimal places
    surface_slice_df = surface_slice_df.astype(float).round(2)

    surface_slice_df.index.name = f'{slice_by} = {slice_target}'

    return surface_slice_df

def plot_volatility_surface_plot(surf_table, x_axis, y_axis, colorscale="Turbo"):
    """
    Create an interactive 3D surface plot of the volatility surface with contour lines.
    
    This function generates a three-dimensional visualization where the x-axis represents
    moneyness/strikes, y-axis represents expiries, and z-axis represents volatility values.
    Contour lines are added for better depth perception.

    Parameters
    ----------
    surf_table : pd.DataFrame
        A DataFrame representing the volatility surface with expiries as index
        and strike prices/moneyness as columns. Values should be volatility levels.
    colorscale : str or list, optional
        Plotly colorscale name (e.g., 'Viridis', 'Turbo', 'Plasma') or custom colorscale list.
        Default is "Turbo".

    Returns
    -------
    plotly.graph_objects.Figure
  
    """
    if len(surf_table) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Not enough data to display 3D surface",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18),
            align="center"
        )
        fig.update_layout(
            title=dict(
                text="3D Surface Plot of Volatility Surface",
                x=0.5,
                xanchor="center",
                yanchor="top",
                y=0.95,
                font=dict(size=16)
            ),
            autosize=True,
            height=450,
            margin={"l": 0, "r": 0, "b": 0, "t": 50},
            dragmode=False,
        )
        return fig

    x = surf_table.columns
    y = surf_table.index
    z = surf_table.values

    fig = go.Figure(data=[go.Surface(
        z=z, 
        x=x, 
        y=y, 
        colorscale=colorscale,
        showscale=False,
        contours={
            "y": {
                "show": True,
                "color": "black",
                "highlightcolor": "black",
                "size": 0.05
            },
            "z": {
                "show": True,
                "color": "black",
                "highlightcolor": "black",
                "size": 0.05
            }
        }
    )])

    fig.update_layout(
        title=dict(
            text="3D Surface Plot of Volatility Surface",
            x=0.5,
            xanchor="center",
            yanchor="top",
            y=0.95,
            font=dict(size=16)
        ),
        scene={
            "xaxis_title": x_axis,
            "yaxis_title": y_axis,
            "zaxis_title": "Volatility",
            "xaxis": {"showgrid": True},
            "yaxis": {"showgrid": True},
            "zaxis": {"showgrid": True},
            "camera": {
                "eye": {"x": 0.96, "y": -1.53, "z": 0.39},
                "center": {"x": 0.02, "y": -0.07, "z": -0.21},
                "up": {"x": -0.18, "y": 0.27, "z": 0.95},
                "projection": {"type": "perspective"}
            }
        },
        dragmode=False,
        autosize=True,
        height=450,
        width=800,
    )

    return fig

def plot_surface_smile_by_expiry(surf_table, x_axis, y_axis):
    """
    Create a 2D line plot showing volatility smiles for different expiry dates.
    
    This function plots multiple volatility smile curves, with each curve representing
    a different expiry date. The x-axis shows moneyness/strikes and the y-axis shows
    volatility levels.

    Parameters
    ----------
    surf_table : pd.DataFrame
        A DataFrame with expiries as index and strike prices/moneyness as columns.
        Values should be volatility levels for each expiry-strike combination.

    Returns
    -------
    plotly.graph_objects.Figure
        Interactive line plot with each expiry represented as a separate trace.
        
    """
    fig = go.Figure()

    for expiry in surf_table.index:
        fig.add_trace(go.Scatter(
            x=surf_table.columns.astype(float),
            y=surf_table.loc[expiry],
            mode='lines+markers',
            name=expiry
        ))

    fig.update_layout(
        title=dict(
            text='Surface Smile by Expiry',
            x=0.5,
            xanchor="center",
            yanchor="top",
            y=0.95,
            font=dict(size=16)
        ),
        xaxis_title=x_axis,
        yaxis_title='Volatility',
        legend_title=y_axis,
        template='plotly_white',
        dragmode=False,
        autosize=True,
        height=450,
        width=800,
    )

    return fig

# In this plotting example, we will demonstrate how Swaption Volatility Cube can be visualized slice by slice.

# Setup input parameters for slicing the Volatility Cube
slice_by = 'SwapTenor'
point_value = 'Normal Vol (bp)'
x_axis = 'Relative Strike (%)'
y_axis = 'Expiry'

vol_cube_points_df = pd.DataFrame(surface_data['surface'], columns = surface_data['headers'])
display(vol_cube_points_df[slice_by].unique())

slice_target = '2Y' #get surface for 2Y swap

surface_df = prepare_volatility_surface_from_list(surface_data, slice_by = slice_by, slice_target = slice_target, x_axis=x_axis, y_axis=y_axis, point_value=point_value)

# Create interactive 3D surface plot using the same DataFrame
# The plot allows rotation, zoom, and hover to explore volatility patterns
plot_volatility_surface_plot(surface_df, x_axis, y_axis)

plot_surface_smile_by_expiry(surface_df, x_axis, y_axis)

# Create filenames with timestamp
timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
excel_filename = f"volatility_surface_{timestamp}.xlsx"
json_filename = f"response_{timestamp}.json"

# Save DataFrame to Excel
surface_df.to_excel(excel_filename, index=False)

# Save response to JSON
with open(json_filename, 'w') as f:
    json.dump(dict(response), f, indent=2, default=str)

print(f"Files saved: {excel_filename}, {json_filename}")