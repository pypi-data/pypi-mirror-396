# This notebook uses external libraries *pandas, IPython*; 
# please ensure they are installed in your Python environment (e.g. 'pip install pandas') before running the code."

from lseg_analytics.pricing.instruments import bond as bd

import pandas as pd
import datetime as dt
from IPython.display import display

bond_definition_isin = bd.BondDefinition(
    instrument_code = "US064159YN00", # ISIN code
    issue_date = dt.datetime(2023, 1, 15), # Optional, if not defined the value comes from the instrument reference data
    end_date = dt.datetime(2028, 1, 15), # Optional, if not defined the value comes from the instrument reference data
    instrument_tag = "BOND_FRN_ISIN" # A user defined string to identify the instrument
)

bond_definition_index = bd.BondDefinition(
    index_fixing_ric = "USDSOFR=", # RIC of the index
    interest_type = bd.InterestTypeEnum.FLOAT, # Floating rate
    interest_payment_frequency = bd.InterestPaymentFrequencyEnum.SEMI_ANNUAL, # Coupons paid every 6M
    notional_ccy = "USD", # USD denomination
    notional_amount = 1E6, # $1M face value
    interest_calculation_method = bd.InterestCalculationMethodEnum.DCB_30_360, # 30/360 interest day count basis
    payment_business_day_convention = bd.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING,
    issue_date = dt.datetime(2023, 1, 15), # Optional, if not defined the value comes from the instrument reference data
    end_date = dt.datetime(2028, 1, 15), # Optional, if not defined the value comes from the instrument reference data
    instrument_tag = "BOND_FRN_INDEX", # A user defined string to identify the instrument
    payment_business_days = "USA" # US calendar
)

bond_instruments = [
    bd.BondDefinitionInstrument(definition = bond_definition_isin),
    bd.BondDefinitionInstrument(definition = bond_definition_index)
]

# Configuring Pricing Parameters
pricing_params = bd.BondPricingParameters(
    valuation_date=dt.datetime(2023, 7, 18)
)

basic_fields = "InstrumentTag, NotionalCcy, MarketValueInDealCcy, ReportCcy, MarketValueInReportCcy"
additional_fields = "cleanPricePercent, dirtyPricePercent, yieldPercent, ModifiedDuration, convexity, DV01Bp"
cashflow_fields = "CashFlows"
fields = basic_fields + "," + additional_fields + "," + cashflow_fields

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instrument definitions for batch processing

try:
    response = bd.price(
        definitions = bond_instruments,
        pricing_preferences = pricing_params,
        fields = fields # If not set, all the possible fields will be displayed
    )

    # Display response structure information
    analytics_data = response['data']['analytics'][0]
    if analytics_data['error'] == {}:
        print("   Calculation successful!")
    else:
        print(f"   Pricing error: {analytics_data['error']}")
        
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Convert multi-bond analytics to DataFrame for better visualization
print("Multi-Bond Analytics Summary:")
columns = [item['name'] for item in response['data']['analytics'][0]['tabularData']['headers']]
response_data = [item['tabularData']['data'] for item in response['data']['analytics']]

response_df = pd.DataFrame(response_data, columns=columns)

# Set InstrumentTag as index for better readability
response_df.set_index('InstrumentTag', inplace=True)

# Round numerical values to 4 decimal places while keeping strings unchanged
response_df_rounded = response_df.copy()
response_df_rounded = response_df_rounded.drop('CashFlows', axis=1)
for col in response_df_rounded.columns:
    if response_df_rounded[col].dtype in ['float64', 'int64']:
        response_df_rounded[col] = response_df_rounded[col].round(4)

display(response_df_rounded.T)

display(pd.DataFrame(response['data']['analytics'][0]['tabularData']['headers']))

# Helper function to extract the cashflows from the response
def display_cashflows(bond_index):
    cashflows = response['data']['analytics'][bond_index]['cashflows']['cashFlows'][0]["payments"]
    dates = [cf['date'] for cf in cashflows]
    amounts = [cf['amount'] for cf in cashflows]
    events = [cf['event'] for cf in cashflows]
    events_type = [cf['type'] for cf in cashflows]
    rates = [cf['indexFixings'][0]["couponRatePercent"] if "indexFixings" in cf else 0 for cf in cashflows]

    cashflows_df = pd.DataFrame({'Dates': dates, "Cashflows": events, "Cashflow type": events_type, "Rate Percent": rates, "Amounts": amounts})
    display(cashflows_df)

display_cashflows(0) # 0 is the index as the bond with ISIN was passed at the first position in the price method

display_cashflows(1) # 1 is the index as the bond with Index RIC was passed at the seconde position in the price method