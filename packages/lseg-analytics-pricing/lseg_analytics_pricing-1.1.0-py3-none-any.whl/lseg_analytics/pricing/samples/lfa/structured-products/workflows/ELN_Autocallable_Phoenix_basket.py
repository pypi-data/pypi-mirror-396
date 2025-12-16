from lseg_analytics.pricing.instruments import structured_products as sp 

import json
import datetime as dt
import pandas as pd
from IPython.display import display

# 1. Create SP definition object

SN_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "Phoenix_basket",
    inputs = [
        sp.NameTypeValue(name="notional", type = "string", value="1000"),
        sp.NameTypeValue(name="Basket", type = "string", value="MBGn_DE|BMWG_DE"),
        sp.NameTypeValue(name="FirstAsset", type = "string", value="Perf_MBGn_DE"),
        sp.NameTypeValue(name="LastAsset", type = "string", value="Perf_BMWG_DE"),
        sp.NameTypeValue(name="BasketFunction", type = "string", value="Average"),
        sp.NameTypeValue(name="BasketPerf", type = "string", value="If(\"BasketFunction\" == \"WorstOf\", Min(FirstAsset[t]:LastAsset[t]), IF(\"BasketFunction\" == \"Average\", Average(FirstAsset[t]:LastAsset[t],True), 0))"),
        sp.NameTypeValue(name="StrikeDate", type = "date", value="26/08/2025"),
        sp.NameTypeValue(name="MaturityDate", type = "date", value="04/09/2034"),
        sp.NameTypeValue(name="LastValuationDate", type = "date", value="28/08/2034"),
        sp.NameTypeValue(name="Schedule", type = "schedule", value=[
                    ["26/02/2026", "26/02/2026", "05/03/2026", "05/03/2026"],
                    ["26/08/2026", "26/08/2026", "02/09/2026", "02/09/2026"],
                    ["26/02/2027", "26/02/2027", "05/03/2027", "05/03/2027"],
                    ["26/08/2027", "26/08/2027", "02/09/2027", "02/09/2027"],
                    ["28/02/2028", "28/02/2028", "06/03/2028", "06/03/2028"],
                    ["28/08/2028", "28/08/2028", "04/09/2028", "04/09/2028"],
                    ["26/02/2029", "26/02/2029", "05/03/2029", "05/03/2029"],
                    ["27/08/2029", "27/08/2029", "03/09/2029", "03/09/2029"],
                    ["26/02/2030", "26/02/2030", "05/03/2030", "05/03/2030"],
                    ["26/08/2030", "26/08/2030", "02/09/2030", "02/09/2030"],
                    ["26/02/2031", "26/02/2031", "05/03/2031", "05/03/2031"],
                    ["26/08/2031", "26/08/2031", "02/09/2031", "02/09/2031"],
                    ["26/02/2032", "26/02/2032", "04/03/2032", "04/03/2032"],
                    ["26/08/2032", "26/08/2032", "02/09/2032", "02/09/2032"],
                    ["28/02/2033", "28/02/2033", "07/03/2033", "07/03/2033"],
                    ["26/08/2033", "26/08/2033", "02/09/2033", "02/09/2033"],
                    ["27/02/2034", "27/02/2034", "06/03/2034", "06/03/2034"]]),
        sp.NameTypeValue(name="CouponBarrier", type = "curve", value=[["26/08/2025","70%"]]),
        sp.NameTypeValue(name="FinalCouponBarrier", type = "string", value="70%"),
        sp.NameTypeValue(name="AutocallBarrier", type = "curve", value=[
                    ["26/02/2027","100%"],
                    ["26/08/2027","97.5%"],
                    ["28/02/2028","95%"],
                    ["28/08/2028","92.5%"],
                    ["26/02/2029","90%"],
                    ["27/08/2029","87.5%"],
                    ["26/02/2030","85%"],
                    ["26/08/2030","82.5%"],
                    ["26/02/2031","80%"],
                    ["26/08/2031","80%"],
                    ["26/02/2032","80%"],
                    ["26/08/2032","80%"],
                    ["28/02/2033","80%"],
                    ["26/08/2033","80%"],
                    ["27/02/2034","80%"]]),
        sp.NameTypeValue(name="RedemptionBarrier", type = "string", value="50%"),
        sp.NameTypeValue(name="CouponRate", type = "string", value="4.50%"),
        sp.NameTypeValue(name="Leverage", type = "string", value="100%"),
        sp.NameTypeValue(name="VarInit", type = "string", value="0"),
        sp.NameTypeValue(name="NbPeriodNoCallable", type = "string", value="2")
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
            "#[t]/#[StrikeDate]",
            "BasketPerf",
            "If($n<NbPeriodNocallable,1,If(Performance[t]>=Interpol(AutocallBarrier,PS()),0,Alive[LastDate]))",
            "(1 - Alive[t]) * Alive[LastDate(-1)]",
            "$n=$n+1;$n",
            "Receive If(Performance[t]>=Interpol(CouponBarrier,PS()),CouponRate,0)*Alive[LastDate(-1)]",
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
            "Receive (MaturityDate, If(Performance[t]>=FinalCouponBarrier, CouponRate, 0) * Alive[LastDate])",
            "Receive (MaturityDate, Alive[LastDate])",
            "Receive (MaturityDate, If(Performance[t]>=RedemptionBarrier,0,(Performance[t] / Leverage -1)*Alive[LastDate]))",
            "Report((columnval(Coupon)+columnval(OptionAtMaturity)+columnval(Settlement))*100)",
            "Report(columnval(PriceIn%)/100*Notional)"
          ]
        ]
)

# 2. Create SP instrument definition object

phoenix_basket = sp.StructuredProductsDefinitionInstrument(definition = SN_definition)
print("Instrument definition created")

# 3. Create SP parameters object - optional

phoenix_basket_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 10, 15),  # Set your desired valuation date
    report_ccy="EUR",  # Set your reporting currency
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
    models=[sp.ModelDefinition(
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
                  model_name= "Dupire")
          ]
)

print("Pricing parameters configured")

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing
try:
    response = sp.price(
        definitions=[phoenix_basket],
        pricing_preferences=phoenix_basket_pricing_params,
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
df_phoenix_basket_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_phoenix_basket_valuation)

# Extract cashflows from response
cashflows = response.data.analytics[0].cashflows["cashFlows"]

# Extract underlyings
model_df = pd.DataFrame(data=phoenix_basket_pricing_params.models)
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
df_phoenix_basket_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_phoenix_basket_greeks)