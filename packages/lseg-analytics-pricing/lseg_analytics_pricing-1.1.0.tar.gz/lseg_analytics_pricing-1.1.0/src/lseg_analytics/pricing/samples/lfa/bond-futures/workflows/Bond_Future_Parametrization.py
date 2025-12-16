from lseg_analytics.pricing.instruments import bond_future as bf

import pandas as pd
import json
import datetime as dt
from IPython.display import display

# 1.Define an underlying Bond instrument
bond_definition_1 = bf.BondDefinition(
    notional_ccy = "EUR",
    issue_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),
    end_date = dt.datetime.strptime("2030-01-01", "%Y-%m-%d"),
    fixed_rate_percent = 2,
    interest_payment_frequency = bf.InterestPaymentFrequencyEnum.QUARTERLY,
    interest_calculation_method = bf.InterestCalculationMethodEnum.DCB_ACTUAL_ACTUAL
)
bond_definition_2 = bf.BondDefinition(
    notional_ccy = "EUR",
    issue_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),
    end_date = dt.datetime.strptime("2035-01-01", "%Y-%m-%d"),
    fixed_rate_percent = 3,
    interest_payment_frequency = bf.InterestPaymentFrequencyEnum.QUARTERLY,
    interest_calculation_method = bf.InterestCalculationMethodEnum.DCB_ACTUAL_ACTUAL
)
underlying_bond_1 = bf.BondFutureUnderlyingContract(
        instrument_definition = bond_definition_1,
        instrument_type = "Bond"
)
underlying_bond_2 = bf.BondFutureUnderlyingContract(
        instrument_definition = bond_definition_2,
        instrument_type = "Bond"
)
print("1 - Underlying Bonds definition created")

# 2.Define Future instrument
future_definition = bf.BondFutureDefinition(
    instrument_code = "FOATc1",  # Mandatory field, RIC of the bond future
    underlying_instruments = [underlying_bond_1, underlying_bond_2],
    notional_amount = 2000000  # Override notional amount
)
print("2 - Future instrument defined")

# 3.Create the Future Instrument from the defintion
future_instrument = bf.BondFutureDefinitionInstrument(definition = future_definition)
print("3 - Future Instrument created")

# 4. Configure pricing parameters
pricing_params = bf.BondFuturePricingParameters(
    valuation_date = dt.datetime.strptime("2025-07-18", "%Y-%m-%d"),                
)
print("4 - Pricing parameters configured")

#  Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

# Execute the calculation using the price() function with error handling
try:
    # The 'definitions' parameter accepts a list of request items for batch processing
    response = bf.price(
        definitions=[future_instrument],
        pricing_preferences=pricing_params
    )
    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Bond Future pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

# Access the description object
description = response.data.analytics[0].description
print(json.dumps(description.as_dict(), indent=4))

# Access the pricing analysis object
pricing_analysis = response.data.analytics[0]["pricingAnalysis"]
df_pricing_analysis = pd.DataFrame(list(pricing_analysis.items()), columns=["Fields", "Value"])
display(df_pricing_analysis.head(9))

# Access the first underlying bond pricing analysis object
bond_1_pricing_analysis = response.data.analytics[0]["pricingAnalysis"]["deliveryBasket"][0]
df_bond_1_pricing_analysis = pd.DataFrame(list(bond_1_pricing_analysis.items()), columns=["Fields", "Value"])
display(df_bond_1_pricing_analysis.head(10))

# Access the second underlying bond pricing analysis object
bond_2_pricing_analysis = response.data.analytics[0]["pricingAnalysis"]["deliveryBasket"][1]
df_bond_2_pricing_analysis = pd.DataFrame(list(bond_2_pricing_analysis.items()), columns=["Fields", "Value"])
display(df_bond_2_pricing_analysis.head(10))

# Access the nominal measures object
nominal_measures = response.data.analytics[0]["nominalMeasures"]
df_nominal_measures = pd.DataFrame(list(nominal_measures.items()), columns=["Fields", "Value"])
display(df_nominal_measures)

valuation = response.data.analytics[0].valuation
df_valuation = pd.DataFrame(list(valuation.items()), columns=["Fields", "Value"])
display(df_valuation)