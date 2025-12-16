from lseg_analytics.pricing.instruments import structured_products as sp 

import json
import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

SN_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "Reverse_Convertible",
    inputs = [
        sp.NameTypeValue(name="notional", type = "string", value="1000"),
        sp.NameTypeValue(name="Underlying", type = "string", value="ASML"),
        sp.NameTypeValue(name="StrikeDate", type = "date", value="14/08/2025"),
        sp.NameTypeValue(name="MaturityDate", type = "date", value="21/08/2030"),
        sp.NameTypeValue(name="LastValuationDate", type = "date", value="14/08/2030"),
        sp.NameTypeValue(name="Schedule", type = "schedule", value=[
                    ["14/08/2026", "14/08/2026", "21/08/2026", "21/08/2026"],
                    ["16/08/2027", "16/08/2027", "23/08/2027", "23/08/2027"],
                    ["14/08/2028", "14/08/2028", "21/08/2028", "21/08/2028"],
                    ["14/08/2029", "14/08/2029", "21/08/2029", "21/08/2029"]]),
        sp.NameTypeValue(name="RedemptionBarrier", type = "string", value="30%"),
        sp.NameTypeValue(name="CouponRate", type = "string", value="1.75%"),
        sp.NameTypeValue(name="Leverage", type = "string", value="100%")
    ],
    payoff_description = [
          [
            "Schedule type",
            "Schedule description",
            "Index",
            "Performance",
            "Coupon",
            "Settlement",
            "OptionAtMaturity",
            "PriceIn%",
            "Price"
          ],
          [
            "AtDate",
            "StrikeDate",
            "EqSpot(Underlying)",
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          [
            "OnUserSchedule",
            "Schedule",
            "EqSpot(Underlying)",
            "",
            "Receive CouponRate",
            "",
            "",
            "",
            ""
          ],
          [
            "AtDate",
            "LastValuationDate",
            "EqSpot(Underlying)",
            "Index[t] / Index[StrikeDate]",
            "Receive (MaturityDate, CouponRate)",
            "Receive (MaturityDate, 100%)",
            "Receive (MaturityDate, If(Performance[t]>=RedemptionBarrier,0,(Performance[t] / Leverage -1)))",
            "Report((columnval(Coupon)+columnval(OptionAtMaturity)+columnval(Settlement))*100)",
            "Report(columnval(PriceIn%)/100*Notional)"
          ]
        ]
)

# 2. Create SP instrument definition object

rev_convert_single = sp.StructuredProductsDefinitionInstrument(definition = SN_definition)
print("Instrument definition created")

# 3. Create SP parameters object - optional

rev_convert_single_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 9, 10),  # Set your desired valuation date
    report_ccy="EUR",  # Set your reporting currency
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    models=[sp.ModelDefinition(
                  underlying_code = "ASML.AS",
                  underlying_name = "ASML",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire")
          ]
)

print("Pricing parameters configured")

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

try:
    response = sp.price(
        definitions=[rev_convert_single],
        pricing_preferences=rev_convert_single_pricing_params,
        market_data=None,
        return_market_data=True,  # or False
        fields=None  # or specify fields as a string
    )

    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Pricing execution completed")
    
except Exception as e:
    print(f"Price calculation failed: {str(e)}")
    raise

# Extract description from response
description = response.data.analytics[0].description

# Convert to dictionary for display
print(json.dumps(description.as_dict(), indent=4))

# Extract vauation from the response
valuation = response.data.analytics[0].valuation

# Convert the dictionary to a DataFrame
df_rev_convert_single_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_rev_convert_single_valuation)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows["cashFlows"]

# Extract underlyings
model_df = pd.DataFrame(data=rev_convert_single_pricing_params.models)
underlying_list = model_df['underlyingName'].to_list()

# Build dataframes for all cash flow types
output = []
for cf_type in cashflows:
    cashflow_df = pd.DataFrame(cf_type['payments'])
    if cf_type['legTag'] == 'Index':
        cashflow_df = cashflow_df.rename(columns={'amount': underlying_list[0]})
    else:
        cashflow_df = cashflow_df.rename(columns={'amount': cf_type['legTag']})
    cashflow_df['discountFactor'] = cashflow_df['discountFactor'].round(4)
    output.append(cashflow_df)

# Merge all dataframes on the 'date' column
combined_df = pd.concat([*output],axis=1)

# Remove duplicated columns with the same values
combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

common_cols = ['date', 'discountFactor', 'Performance', 'Coupon', 'Settlement', 'OptionAtMaturity', 'Price', 'currency', 'occurence']
indv_perf = [f'PERF_{underlying}' for underlying in underlying_list if len(underlying_list) > 1]
cols_to_display = common_cols[0:2] + underlying_list + indv_perf + common_cols[2:]

# Leave only columns to display
combined_df = combined_df.loc[:,[*cols_to_display]]

# Display the combined dataframe
display(combined_df)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_df_rev_convert_single_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_df_rev_convert_single_greeks)