from lseg_analytics.pricing.instruments import structured_products as sp 

import json
import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

SN_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "Phoenix_Memory_basket",
    inputs = [
        sp.NameTypeValue(name="notional", type = "string", value="1000"),
        sp.NameTypeValue(name="Basket", type = "string", value="TTEF_PA|IBE_MC|ENEI_MI"),
        sp.NameTypeValue(name="FirstAsset", type = "string", value="Perf_TTEF_PA"),
        sp.NameTypeValue(name="LastAsset", type = "string", value="Perf_ENEI_MI"),
        sp.NameTypeValue(name="BasketFunction", type = "string", value="WorstOf"),
        sp.NameTypeValue(name="BasketPerf", type = "string", value="If(\"BasketFunction\" == \"WorstOf\", Min(FirstAsset[t]:LastAsset[t]), IF(\"BasketFunction\" == \"Average\", Average(FirstAsset[t]:LastAsset[t],True), 0))"),
        sp.NameTypeValue(name="StrikeDate", type = "date", value="02/05/2025"),
        sp.NameTypeValue(name="MaturityDate", type = "date", value="16/05/2030"),
        sp.NameTypeValue(name="LastValuationDate", type = "date", value="02/05/2030"),
        sp.NameTypeValue(name="Schedule", type = "schedule", value=[
                    ["04/08/2025", "04/08/2025", "04/08/2025", "04/08/2025"],
                    ["03/11/2025", "03/11/2025", "03/11/2025", "03/11/2025"],
                    ["02/02/2026", "02/02/2026", "02/02/2026", "02/02/2026"],
                    ["04/05/2026", "04/05/2026", "04/05/2026", "04/05/2026"],
                    ["03/08/2026", "03/08/2026", "03/08/2026", "03/08/2026"],
                    ["02/11/2026", "02/11/2026", "02/11/2026", "02/11/2026"],
                    ["02/02/2027", "02/02/2027", "02/02/2027", "02/02/2027"],
                    ["03/05/2027", "03/05/2027", "03/05/2027", "03/05/2027"],
                    ["02/08/2027", "02/08/2027", "02/08/2027", "02/08/2027"],
                    ["02/11/2027", "02/11/2027", "02/11/2027", "02/11/2027"],
                    ["02/02/2028", "02/02/2028", "02/02/2028", "02/02/2028"],
                    ["02/05/2028", "02/05/2028", "02/05/2028", "02/05/2028"],
                    ["02/08/2028", "02/08/2028", "02/08/2028", "02/08/2028"],
                    ["02/11/2028", "02/11/2028", "02/11/2028", "02/11/2028"],
                    ["02/02/2029", "02/02/2029", "02/02/2029", "02/02/2029"],
                    ["02/05/2029", "02/05/2029", "02/05/2029", "02/05/2029"],
                    ["02/08/2029", "02/08/2029", "02/08/2029", "02/08/2029"],
                    ["02/11/2029", "02/11/2029", "02/11/2029", "02/11/2029"],
                    ["04/02/2030", "04/02/2030", "04/02/2030", "04/02/2030"]]),
        sp.NameTypeValue(name="CouponBarrier", type = "curve", value=[["02/05/2025","70%"]]),
        sp.NameTypeValue(name="FinalCouponBarrier", type = "string", value="70%"),
        sp.NameTypeValue(name="AutocallBarrier", type = "curve", value=[["02/05/2025","100%"]]),
        sp.NameTypeValue(name="RedemptionBarrier", type = "string", value="55%"),
        sp.NameTypeValue(name="CouponRate", type = "string", value="3.55%"),
        sp.NameTypeValue(name="Leverage", type = "string", value="100%"),
        sp.NameTypeValue(name="VarInit", type = "string", value="0"),
        sp.NameTypeValue(name="NbPeriodNoCallable", type = "string", value="3")
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
            "SumOfCoupons",
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
            "0",
            "",
            "",
            "",
            ""
          ],
          [
            "OnUserSchedule",
            "Schedule",
            "EqSpot(#)",
            "#[t]/#[StrikeDate]",
            "BasketPerf",
            "If($n<NbPeriodNocallable,1,If(Performance[t]>=Interpol(AutocallBarrier,PS()),0,Alive[LastDate]))",
            "(1 - Alive[t]) * Alive[LastDate(-1)]",
            "$n=$n+1;$n",
            "Receive If(Performance[t]>=Interpol(CouponBarrier,PS()),$n*CouponRate-SumOfCoupons[LastDate(-1)],0)*Alive[LastDate(-1)]",
            "Coupon[t]+SumOfCoupons[LastDate]",
            "Receive Early[t]",
            "",
            "",
            ""
          ],
          [
            "AtDate",
            "LastValuationDate",
            "EqSpot(#)",
            "#[t]/#[StrikeDate]",
            "BasketPerf",
            "",
            "",
            "$n=$n+1;$n",
            "Receive (MaturityDate, If(Performance[t]>=FinalCouponBarrier, $n*CouponRate-SumOfCoupons[LastDate], 0) * Alive[LastDate])",
            "",
            "Receive (MaturityDate, Alive[LastDate])",
            "Receive (MaturityDate, If(Performance[t]>=RedemptionBarrier,0,(Performance[t] / Leverage -1)*Alive[LastDate]))",
            "Report((columnval(Coupon)+columnval(OptionAtMaturity)+columnval(Settlement))*100)",
            "Report(columnval(PriceIn%)/100*Notional)"
          ]
        ]
)

# 2. Create SP instrument definition object

phoenix_memory_basket = sp.StructuredProductsDefinitionInstrument(definition = SN_definition)
print("Instrument definition created")

# 3. Create SP parameters object - optional

phoenix_memory_basket_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 10, 15),  # Set your desired valuation date
    report_ccy="EUR",  # Set your reporting currency
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    models=[sp.ModelDefinition(
                  underlying_code = "TTEF.PA",
                  underlying_name = "TTEF_PA",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire"),
            sp.ModelDefinition(
                  underlying_code = "IBE.MC",
                  underlying_name = "IBE_MC",
                  underlying_currency = "EUR",
                  asset_class = "Equity",
                  model_name= "Dupire"),
            sp.ModelDefinition(
                  underlying_code = "ENEI.MI",
                  underlying_name = "ENEI_MI",
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
        definitions=[phoenix_memory_basket],
        pricing_preferences=phoenix_memory_basket_pricing_params,
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
df_phoenix_memory_basket_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_phoenix_memory_basket_valuation)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows["cashFlows"]

# Extract underlyings
model_df = pd.DataFrame(data=phoenix_memory_basket_pricing_params.models)
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
df_phoenix_memory_basket_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_phoenix_memory_basket_greeks)