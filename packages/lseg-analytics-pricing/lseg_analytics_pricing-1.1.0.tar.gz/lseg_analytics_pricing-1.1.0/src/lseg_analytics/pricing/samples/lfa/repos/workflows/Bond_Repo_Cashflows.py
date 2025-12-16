from lseg_analytics.pricing.instruments import repo as rp

import pandas as pd
import json
import datetime as dt
from IPython.display import display

# 1.Define an underlying Bond instrument
fixed_bond_definition = rp.BondDefinition(
    notional_ccy = "USD",
    issue_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),
    end_date = dt.datetime.strptime("2030-01-01", "%Y-%m-%d"),
    fixed_rate_percent = 2,
    interest_payment_frequency = rp.InterestPaymentFrequencyEnum.QUARTERLY,
    interest_calculation_method = rp.InterestCalculationMethodEnum.DCB_ACTUAL_ACTUAL

)

underlying_bond = rp.RepoUnderlyingContract(
        instrument_definition = fixed_bond_definition,
        instrument_type = "Bond"
)
print("Underlying Bond definition created")

# 2.Define Repo instrument
repo_definition = rp.RepoDefinition(
    buy_sell = rp.IPABuySellEnum.BUY,
    start_date = dt.datetime.strptime("2025-01-01", "%Y-%m-%d"),
    tenor = "1Y",
    repo_rate_percent = 2, # Override repo rate instead of implying from repo curve
    underlying_instruments = [underlying_bond],
    is_coupon_exchanged = False
)

# 3.Create the Repo Instrument from the defintion
repo_instrument = rp.RepoDefinitionInstrument (definition = repo_definition)
print("Repo Instrument definition created")

# 4. Configure pricing parameters, optional
pricing_params = rp.RepoPricingParameters(
    valuation_date = dt.datetime.strptime("2025-07-18", "%Y-%m-%d"),                
)
print("Pricing parameters configured")

# Execute the calculation using the price function
try:
    # The 'definitions' parameter accepts a list of request items for batch processing
    response = rp.price(
    definitions = [repo_instrument],
    pricing_preferences = pricing_params
)
    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Pricing Execution Successful!")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

# Access the description object
description = response.data.analytics[0].description
print(json.dumps(description.as_dict(), indent=4))

# Access the pricing analysis object
pricing_analysis = response.data.analytics[0]["pricingAnalysis"]
# Convert to DataFrame
df_pricing_analysis = pd.DataFrame(list(pricing_analysis.items()), columns=["Fields", "Value"])
# Display the DataFrame
display(df_pricing_analysis.head(5))

# Access to payments/cash-flows
payments = response.data.analytics[0].cashflows.cash_flows[0]["payments"]
df_payments = pd.DataFrame(payments)
display(df_payments)

print("purchasePrice", response.data.analytics[0]["pricingAnalysis"]["purchasePrice"])
print("repurchasePrice", response.data.analytics[0]["pricingAnalysis"]["repurchasePrice"])

repo_definition.is_coupon_exchanged = True
repo_definition.tenor = "2Y" # tenor extended only to visualize several cashflows

# Execute the calculation using the price function
try:
    # The 'definitions' parameter accepts a list of request items for batch processing
    response = rp.price(
    definitions = [repo_instrument],
    pricing_preferences = pricing_params
)
    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Pricing Execution Successful!")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

# Access to payments/cash-flows
payments = response.data.analytics[0].cashflows.cash_flows[0]["payments"]
df_payments = pd.DataFrame(payments)
display(df_payments)