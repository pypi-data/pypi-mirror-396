from lseg_analytics.pricing.instruments import structured_products as sp 

import json
import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

SN_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "Athena_basket",
    inputs = [
        sp.NameTypeValue(name="notional", type = "string", value="1000"),
        sp.NameTypeValue(name="Basket", type = "string", value="RACE_MI|MBGn_DE|BMWG_DE|VOWG_DE"),
        sp.NameTypeValue(name="FirstAsset", type = "string", value="Perf_RACE_MI"),
        sp.NameTypeValue(name="LastAsset", type = "string", value="Perf_VOWG_DE"),
        sp.NameTypeValue(name="BasketFunction", type = "string", value="Average"),
        sp.NameTypeValue(name="BasketPerf", type = "string", value="If(\"BasketFunction\" == \"WorstOf\", Min(FirstAsset[t]:LastAsset[t]), IF(\"BasketFunction\" == \"Average\", Average(FirstAsset[t]:LastAsset[t],True), 0))"),
        sp.NameTypeValue(name="StrikeDate", type = "date", value="10/07/2025"),
        sp.NameTypeValue(name="MaturityDate", type = "date", value="24/07/2029"),
        sp.NameTypeValue(name="LastValuationDate", type = "date", value="10/07/2029"),
        sp.NameTypeValue(name="Schedule", type = "schedule", value=[
                    ["10/10/2025", "10/10/2025", "24/10/2025", "24/10/2025"],
                    ["12/01/2026", "12/01/2026", "26/01/2026", "26/01/2026"],
                    ["10/04/2026", "10/04/2026", "24/04/2026", "24/04/2026"],
                    ["10/07/2026", "10/07/2026", "24/07/2026", "24/07/2026"],
                    ["12/10/2026", "12/10/2026", "26/10/2026", "26/10/2026"],
                    ["11/01/2027", "11/01/2027", "25/01/2027", "25/01/2027"],
                    ["12/04/2027", "12/04/2027", "26/04/2027", "26/04/2027"],
                    ["12/07/2027", "12/07/2027", "26/07/2027", "26/07/2027"],
                    ["11/10/2027", "11/10/2027", "25/10/2027", "25/10/2027"],
                    ["10/01/2028", "10/01/2028", "24/01/2028", "24/01/2028"],
                    ["10/04/2028", "10/04/2028", "24/04/2028", "24/04/2028"],
                    ["10/07/2028", "10/07/2028", "24/07/2028", "24/07/2028"],
                    ["10/10/2028", "10/10/2028", "24/10/2028", "24/10/2028"],
                    ["10/01/2029", "10/01/2029", "24/01/2029", "24/01/2029"],
                    ["10/04/2029", "10/04/2029", "24/04/2029", "24/04/2029"]]),
        sp.NameTypeValue(name="FinalCouponBarrier", type = "string", value="100%"),
        sp.NameTypeValue(name="AutocallBarrier", type = "curve", value=[["10/07/2025","100%"]]),
        sp.NameTypeValue(name="RedemptionBarrier", type = "string", value="50%"),
        sp.NameTypeValue(name="CouponRate", type = "string", value="1.875%"),
        sp.NameTypeValue(name="Leverage", type = "string", value="100%"),
        sp.NameTypeValue(name="VarInit", type = "string", value="0")
    ],
    payoff_description = [
          [
            "Schedule type",
            "Schedule description",
            "Repeat(Basket,#)",
            "Repeat(Basket,Perf_#)",
            "Performance",
            "Alive",
            "Early",
            "Count",
            "Coupon",
            "Settlement",
            "OptionAtMaturity",
            "PriceIn%",
            "Price"
          ],
          [
            "AtDate",
            "StrikeDate",
            "EqSpot(#)",
            "",
            "",
            "1",
            "",
            "$n=VarInit;$n",
            "",
            "",
            "",
            "",
            ""
          ],
          [
            "OnUserSchedule",
            "Schedule",
            "EqSpot(#)",
            "#[LastDate]/#[StrikeDate]",
            "BasketPerf",
            "If(Performance[t] >= Interpol(AutocallBarrier,PS()), 0, Alive[LastDate])",
            "(1 - Alive[t]) * Alive[LastDate(-1)]",
            "$n=$n+1;$n",
            "Receive $n*CouponRate * Early[t]",
            "Receive Early[t]",
            "",
            "",
            ""
          ],
          [
            "AtDate",
            "LastValuationDate",
            "EqSpot(#)",
            "#[LastDate]/#[StrikeDate]",
            "BasketPerf",
            "",
            "",
            "$n=$n+1;$n",
            "Receive (MaturityDate, If(Performance[t]>=FinalCouponBarrier, $n*CouponRate, 0) * Alive[LastDate])",
            "Receive (MaturityDate, Alive[LastDate])",
            "Receive (MaturityDate, If(Performance[t]>=RedemptionBarrier,0,(Performance[t] / Leverage -1)*Alive[LastDate]))",
            "Report((columnval(Coupon)+columnval(OptionAtMaturity)+columnval(Settlement))*100)",
            "Report(columnval(PriceIn%)/100*Notional)"
          ]
        ]
)

# 2. Create SP instrument definition object

athena_basket = sp.StructuredProductsDefinitionInstrument(definition = SN_definition)
print("Instrument definition created")

# 3. Create SP parameters object - optional

athena_basket_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 8, 25),  # Set your desired valuation date
    report_ccy="USD",  # Set your reporting currency
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    models=[sp.ModelDefinition(
                  underlying_code = "RACE.MI",
                  underlying_name = "RACE_MI",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire"),
            sp.ModelDefinition(
                  underlying_code = "MBGn.DE",
                  underlying_name = "MBGn_DE",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire"),
            sp.ModelDefinition(
                  underlying_code = "BMWG.DE",
                  underlying_name = "BMWG_DE",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire"),
            sp.ModelDefinition(
                  underlying_code = "VOWG.DE",
                  underlying_name = "VOWG_DE",
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
        definitions=[athena_basket],
        pricing_preferences=athena_basket_pricing_params,
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
df_athena_basket_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_athena_basket_valuation)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows["cashFlows"]

# Extract underlyings
model_df = pd.DataFrame(data=athena_basket_pricing_params.models)
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

common_cols = ['date', 'discountFactor', 'Performance', 'Alive', 'Early', 'Coupon', 'Settlement', 'OptionAtMaturity', 'Price', 'currency', 'occurence']
indv_perf = [f'PERF_{underlying}' for underlying in underlying_list if len(underlying_list) > 1]
cols_to_display = common_cols[0:2] + underlying_list + indv_perf + common_cols[2:]

# Leave only columns to display
combined_df = combined_df.loc[:,[*cols_to_display]]

# Display the combined dataframe
display(combined_df)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_athena_basket_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_athena_basket_greeks)