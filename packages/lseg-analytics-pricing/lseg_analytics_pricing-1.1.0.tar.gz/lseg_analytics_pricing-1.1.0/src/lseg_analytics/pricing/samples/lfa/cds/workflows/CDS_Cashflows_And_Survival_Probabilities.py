from lseg_analytics.pricing.instruments import cds

import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime as dt
from IPython.display import display

# Create CDS definition with instrument code (RIC)
cds_definition = cds.CdsDefinition(
    instrument_code="BNPP5YEUAM=R"                                          # BNP Paribas 5Y EUR CDS RIC
)

# Create CDS instrument from definition
cds_instrument = cds.CdsDefinitionInstrument(
    definition=cds_definition
)

print("CDS instrument created from RIC")

# Configure pricing parameters, optional
pricing_params = cds.CdsPricingParameters(
    valuation_date = dt.datetime.strptime("2023-03-01", "%Y-%m-%d"),          # Valuation date
    market_data_date = dt.datetime.strptime("2023-03-01", "%Y-%m-%d"),        # Market data date
    report_ccy = "USD"                                                        # Report currency
)
print("Pricing parameters configured")

# Execute the calculation using the price() function with error handling
try:
    # The 'definitions' parameter accepts a list of request items for batch processing
    response = cds.price(
        definitions=[cds_instrument],
        pricing_preferences=pricing_params
    )
    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("CDS pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

# Extract analytics section from response
analytics = response.data.analytics[0]

# Access description data from response
description_dict = analytics.description.as_dict()
df_description = pd.DataFrame(list(description_dict.items()), columns=["Field", "Value"])
display(df_description)

# Display valuation as DataFrame (if available)
valuation = analytics.valuation
if valuation:
    display(pd.DataFrame(valuation.as_dict().items(), columns=["Field", "Value"]))
else:
    print("No valuation data available")

# Access nominal measures from response
nominal_dict = analytics.nominal_measures.as_dict()
df_nominal = pd.DataFrame(list(nominal_dict.items()), columns=["Field", "Value"])
display(df_nominal)

# Access pricing analysis from response
pricing_dict = analytics.pricing_analysis.as_dict()
df_pricing = pd.DataFrame(list(pricing_dict.items()), columns=["Field", "Value"])
display(df_pricing)

# Access spread measures from response
spread_dict = analytics.spread_measures.as_dict()
df_spread = pd.DataFrame(list(spread_dict.items()), columns=["Field", "Value"])
display(df_spread)

# Access cashflows from response
cashflow_dict = analytics.cashflows.as_dict()

# Keys to group together
main_keys = ["nextCouponDate", "cashAmountInDealCcy", "cashAmountInReportCcy"]
main_cashflows = {k: cashflow_dict[k] for k in main_keys if k in cashflow_dict}

# DataFrame for main cashflow fields
df_main_cashflows = pd.DataFrame(list(main_cashflows.items()), columns=["Field", "Value"])
display(df_main_cashflows)

# Extract other Cap/Floor cashflow fields (array values)
other_cashflows_data = {key: value for key, value in cashflow_dict.items() if key not in main_keys and isinstance(value, list)}

# Convert to DataFrame
df_other_cashflows = pd.DataFrame(other_cashflows_data)

# Other cashflows DataFrame
display(df_other_cashflows)

df = df_other_cashflows.copy()
df["cashFlowDatesArray"] = pd.to_datetime(df["cashFlowDatesArray"])

fig, ax1 = plt.subplots(figsize=(12, 6))

# Primary axis: Cashflow Amounts
ax1.plot(df["cashFlowDatesArray"], df["cashFlowTotalAmountsInDealCcyArray"],
         label="Cashflow Amount", color="blue", marker="o")
ax1.set(xlabel="Date", ylabel="Cashflow Amount (EUR)")
ax1.tick_params(axis="y", labelcolor="tab:blue")

# Secondary axis: Discount Factors & Survival Probabilities
ax2 = ax1.twinx()
ax2.plot(df["cashFlowDatesArray"], df["cashFlowDiscountFactorsArray"],
         label="Discount Factor", color="green", linestyle="--", marker="x")
ax2.plot(df["cashFlowDatesArray"], df["cashFlowSurvivalProbabilitiesArray"],
         label="Survival Probability", color="red", linestyle=":", marker="s")
ax2.set_ylabel("Discount Factor (green) / Survival Probability (red)", color="black")
ax2.tick_params(axis="y", labelcolor="black")

ax1.legend(ax1.get_lines() + ax2.get_lines(), [l.get_label() for l in ax1.get_lines() + ax2.get_lines()], loc="upper right")
plt.title("CDS Cashflows Characteristics Over Time")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()