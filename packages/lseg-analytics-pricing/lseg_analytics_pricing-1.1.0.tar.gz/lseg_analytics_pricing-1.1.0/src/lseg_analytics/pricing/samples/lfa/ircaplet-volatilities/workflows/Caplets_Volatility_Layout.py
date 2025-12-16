from lseg_analytics.pricing.market_data import ircaplet_volatility as cv

import pandas as pd
import numpy as np
import json
import datetime as dt
from IPython.display import display

print("Step 1: Creating Surface Definition...")

currency = "USD"
index_name = "SOFR"

# Create surface definition object
surface_definition = cv.CapletsStrippingDefinition(
        instrument_code = currency,
        index_name = index_name,
        reference_caplet_tenor = "ON"
        )
print(f"   ✓ Instrument: {surface_definition.instrument_code}")

print("Step 2: Configuring Surface Parameters...") 
surface_parameters = cv.CapletsStrippingSurfaceParameters(
        calculation_date = dt.datetime.strptime("2025-01-18", "%Y-%m-%d"),
        x_axis = cv.XAxisEnum.STRIKE,                                    # Options: DATE, DELTA, EXPIRY, MONEYNESS, STRIKE, TENOR
        y_axis = cv.YAxisEnum.TENOR                                      # Options: same as X-axis
    )
print(f"   ✓ Surface Parameters: {surface_parameters}")

print("Step 3: Create request item...")
# Create the main request object with basic configuration
request_item = cv.CapletsStrippingSurfaceRequestItem(
        surface_tag = f"{currency}_CAPLET_VOLSURFACE",
        underlying_definition = surface_definition,
        surface_parameters = surface_parameters,
        underlying_type = cv.CurvesAndSurfacesUnderlyingTypeEnum.Cap,
        surface_layout = cv.SurfaceOutput(
            format = cv.FormatEnum.Matrix,  # Options: List, Matrix 
        )
    )
print(f"   ✓ Request Item: {json.dumps(request_item.as_dict(), indent=4)}")

# Execute the calculation using the calculate function
try:
    response = cv.calculate(universe=[request_item])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Surface data points available: {len(surface_data['surface']) - 1} x {len(surface_data['surface'][0]) - 1}")
    else:
        print("   No surface data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Access surface matrix data from the response
surface_data = response['data'][0]['surface']

# Extract strikes (column headers) and tenors (row headers)
strikes = surface_data[0][1:]  # First row, excluding first element
tenors = [row[0] for row in surface_data[1:]]  # First column, excluding header row
volatility_matrix = np.array([[float(val) for val in row[1:]] for row in surface_data[1:]])

# Create DataFrame for easier manipulation and display
surface_df = pd.DataFrame(volatility_matrix, index=tenors, columns=strikes)

# Extract axis names for labeling plots
x_axis = surface_parameters.x_axis.name
y_axis = surface_parameters.y_axis.name

print("Surface DataFrame Info:") 
print(f"   Shape: {surface_df.shape} (rows × columns)") 
print(f"   x_axis: {x_axis}") 
print(f"   y_axis: {y_axis}") 

# Display all columns using context manager (temporary setting)
with pd.option_context('display.max_columns', None, 'display.width', None):
    display(surface_df)

# Change the format from Matrix to List
request_item.surface_layout.format = cv.FormatEnum.List
print(f"   ✓ Format changed to: {request_item.surface_layout.format.name}")

# Execute the calculation using the calculate function
try:
    response = cv.calculate(universe=[request_item])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Surface data points available: {len(surface_data['surface'])}")
    else:
        print("   No surface data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Access surface data from the response
surface_data = response['data'][0]['surface']
headers = response['data'][0]['headers']

print(f"Headers: {headers}")
print(f"Data format: List with {len(surface_data)} data points")

# Convert list format to DataFrame
surface_df = pd.DataFrame(surface_data, columns=headers)

# Display data types and structure
print("Surface DataFrame Info:")
print(f"   Shape: {surface_df.shape} (rows × columns)")
print(f"   Columns: {list(surface_df.columns)}")
print(f"   Data types: {surface_df.dtypes.to_dict()}")

# Display first 10 rows for readability
# To display all data, use: display(surface_df)
display(surface_df.head(10))

# Change input volatility type using string value
surface_parameters.input_volatility_type = "LogNormalVolatility"
print(f"   ✓ Input Volatility Type changed to: {surface_parameters.input_volatility_type}")

# Change format back to Matrix for LogNormalVolatility demonstration
request_item.surface_layout.format = cv.FormatEnum.Matrix
print(f"   ✓ Format changed to: {request_item.surface_layout.format.name}")

# Execute the calculation using the calculate function
try:
    response = cv.calculate(universe=[request_item])

    # Display response structure information
    surface_data = response['data'][0]
    if 'surface' in surface_data:
        print(f"   Calculation successful!")
        print(f"   Surface data points available: {len(surface_data['surface']) - 1} x {len(surface_data['surface'][0]) - 1}")
    else:
        print("   No surface data found in response")
    
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Access surface matrix data from the response
surface_data = response['data'][0]['surface']

# Extract strikes (column headers) and tenors (row headers)
strikes = surface_data[0][1:]  # First row, excluding first element
tenors = [row[0] for row in surface_data[1:]]  # First column, excluding header row
volatility_matrix = np.array([[float(val) for val in row[1:]] for row in surface_data[1:]])

# Create DataFrame for easier manipulation and display
surface_df = pd.DataFrame(volatility_matrix, index=tenors, columns=strikes)

# Extract axis names for labeling plots
x_axis = surface_parameters.x_axis.name
y_axis = surface_parameters.y_axis.name

print("Surface DataFrame Info:") 
print(f"   Shape: {surface_df.shape} (rows × columns)") 
print(f"   x_axis: {x_axis}") 
print(f"   y_axis: {y_axis}") 

# Display all columns using context manager (temporary setting)
with pd.option_context('display.max_columns', None, 'display.width', None):
    display(surface_df)