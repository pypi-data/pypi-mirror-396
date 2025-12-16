from lseg_analytics.pricing.instruments import bond   as bd

import pandas as pd
import json
import datetime as dt
from IPython.display import display
import matplotlib.pyplot as plt

print("Step 1: Creating Fixed Rate Bond Definitions for Cashflow Analysis...")
print("=" * 70)

# Base Bond Parameters (Common to all scenarios)
BASE_PARAMS = {
    'notional_amount': 1_000_000,                              # $1M face value
    'notional_ccy': "USD",                                     # USD denomination
    'fixed_rate_percent': 5.00,                                # 5.00% annual coupon
    'interest_type': bd.InterestTypeEnum.FIXED,                # Fixed rate
    'issue_date': dt.datetime(2023, 1, 15),                    # Issue date
    'end_date': dt.datetime(2028, 1, 15),                      # 5-year maturity
    'interest_payment_frequency': bd.InterestPaymentFrequencyEnum.SEMI_ANNUAL,  # Coupons paid every 6M
    'first_regular_payment_date': dt.datetime(2023, 7, 15),    # First coupon in July
    'interest_calculation_method': bd.InterestCalculationMethodEnum.DCB_30_360,  # 30/360 interest day count basis
    'payment_business_day_convention': bd.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING,  # Modified following Payment business day convention
    'payment_business_days': "USA"                             # US calendar
}

# =================================================

# Scenario 1: Vanilla Cashflow - Standard Bond with Bullet Repayment
print("\nScenario 1: Vanilla Cashflow - Standard Bond with Bullet Repayment")
bond_vanilla = bd.BondDefinition(
    **BASE_PARAMS,
    instrument_tag="BOND_VANILLA_5Y"
)

print(f"   Structure: Bullet bond with semi-annual coupons")
print(f"   Coupon: {bond_vanilla.fixed_rate_percent}% semi-annually")
print(f"   Expected Cashflows: 10 coupon payments + principal at maturity")
print(f"   Each Coupon: ${bond_vanilla.notional_amount * bond_vanilla.fixed_rate_percent / 200:,.0f}")

# =================================================

# Scenario 2: Amortizing Bond - Linear Principal Reduction
print("\nScenario 2: Amortizing Bond - Linear Principal Reduction")

# Linear amortization: $100k principal payment each period
linear_amortization = [
    bd.AmortizationItemDefinition(
        start_date=dt.datetime(2023, 1, 15),                   # Start of amortization
        end_date=dt.datetime(2028, 1, 15),                     # End of amortization
        amortization_frequency=bd.AmortizationFrequencyEnum.SEMI_ANNUAL,  # Every 6M coupon payment
        amortization_type=bd.IPAAmortizationTypeEnum.LINEAR,   # Linear reduction
        remaining_notional=0.0,                                # Fully amortized at maturity
        amount=100_000                                         # $100k principal payment each period
    )
]

bond_linear_amort = bd.BondDefinition(
    **BASE_PARAMS,
    amortization_schedule=linear_amortization,
    instrument_tag="BOND_LINEAR_AMORT_5Y"
)

print(f"   Structure: Linear amortization with declining interest base")
print(f"   Principal Payment: ${linear_amortization[0].amount:,.0f} per period")
print(f"   Expected Cashflows: 10 payments of interest + principal reduction")
print(f"   First Payment: ${linear_amortization[0].amount + (1_000_000 * 0.05 / 2):,.0f} (interest + principal)")
print(f"   Last Payment: ${linear_amortization[0].amount + (100_000 * 0.05 / 2):,.0f} (interest + principal)")

# =================================================

# Scenario 3: User-Defined Amortization Schedule 
print("\nScenario 3: User-Defined Amortization Schedule")

# Custom amortization: Different amounts in different periods
custom_amortization = [
    # Years 3-5: Accelerated amortization
    bd.AmortizationItemDefinition(
        start_date=dt.datetime(2025, 1, 15),
        end_date=dt.datetime(2028, 1, 15),                     # Last 3 years
        amortization_frequency=bd.AmortizationFrequencyEnum.SEMI_ANNUAL,
        amortization_type=bd.IPAAmortizationTypeEnum.SCHEDULE,
        amount=500_000                                         # $500,000 paid at the end of year 2
    )
]

bond_custom_amort = bd.BondDefinition(
    **BASE_PARAMS,
    amortization_schedule=custom_amortization,
    instrument_tag="BOND_CUSTOM_AMORT_5Y"
)

print(f"   Structure: Interest-only for 2 years, then accelerated amortization")
print(f"   Years 1-2 (except year 2 last payment): Interest only (${25_000:,.0f} per payment)")
print(f"   Year 2 Last payment: Principal (${500_000:,.0f} payment) + interest (${25_000:,.0f})")
print(f"   Years 3-5: Interest only (${12_500:,.0f} per payment)")
print(f"   Expected Cashflows: 9 interest-only + 1 amortizing payment with interest")

print("Step 2: Creating Bond Instrument Object...")

# Create instrument containers for all bond scenarios

bond_instruments = [
    bd.BondDefinitionInstrument(definition=bond_vanilla),
    bd.BondDefinitionInstrument(definition=bond_linear_amort),
    bd.BondDefinitionInstrument(definition=bond_custom_amort)
]

print("   Bond instrument containers created for pricing")

print("Step 3: Configuring Pricing Parameters...")
pricing_params = bd.BondPricingParameters(
    valuation_date=dt.datetime(2023, 7, 18),                   # Pricing date (greater than bonds issuances and first cash-flow date => 9 Cash-flow dates)
)

print(f"   Valuation Date: {pricing_params.valuation_date.strftime('%Y-%m-%d')}")

basic_fields = "InstrumentTag, NotionalCcy, MarketValueInDealCcy, ReportCcy, MarketValueInReportCcy"
additional_fields = "cleanPricePercent, dirtyPricePercent, yieldPercent, ModifiedDuration, convexity, DV01Bp"
cashflow_fields = "CashFlows"
fields = basic_fields + "," + additional_fields + "," + cashflow_fields

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instrument definitions for batch processing

try:
    response = bd.price(
        definitions=bond_instruments,
        pricing_preferences=pricing_params,
        fields=fields
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

# Prepare CF dataframes for display
# Reminder: valuation date is greater than bonds issuances and first cash-flow date => 9 Cash-flow dates are showed

bonds_cashflows_dict = {}
for bond_index in range(len(response_df_rounded)):

    cashflows_df = pd.DataFrame(response['data']['analytics'][bond_index]['cashflows']['cashFlows'][0]['payments'])
    
    for col in cashflows_df.columns:
        if cashflows_df[col].dtype in ['float64', 'int64']:
            cashflows_df[col] = cashflows_df[col].round(2)

    bonds_cashflows_dict[response_df_rounded.T.columns[bond_index]] = cashflows_df

display(bonds_cashflows_dict.keys())

df = bonds_cashflows_dict['BOND_VANILLA_5Y']
display(df)

# Separate principal and interest payments
principal_df = df[df['event'] == 'Principal']
interest_df = df[df['event'] == 'Interest']

# Create a combined dataframe for plotting
plot_data = pd.DataFrame({
    'Date': df['date'].unique(),
    'Interest': df[df['event'] == 'Interest'].groupby('date')['amount'].sum(),
    'Principal': df[df['event'] == 'Principal'].groupby('date')['amount'].sum()
}).fillna(0)

# Create stacked column chart
plot_data.set_index('Date')[['Interest', 'Principal']].plot(kind='bar', stacked=True, figsize=(12, 6))
plt.show()

df = bonds_cashflows_dict['BOND_LINEAR_AMORT_5Y']
display(df)

# Separate principal and interest payments
principal_df = df[df['event'] == 'Principal']
interest_df = df[df['event'] == 'Interest']

# Create a combined dataframe for plotting
plot_data = pd.DataFrame({
    'Date': df['date'].unique(),
    'Interest': df[df['event'] == 'Interest'].groupby('date')['amount'].sum(),
    'Principal': df[df['event'] == 'Principal'].groupby('date')['amount'].sum()
}).fillna(0)

# Create stacked column chart
plot_data.set_index('Date')[['Interest', 'Principal']].plot(kind='bar', stacked=True, figsize=(12, 6))
plt.show()

df = bonds_cashflows_dict['BOND_CUSTOM_AMORT_5Y']
display(df)

# Separate principal and interest payments
principal_df = df[df['event'] == 'Principal']
interest_df = df[df['event'] == 'Interest']

# Create a combined dataframe for plotting
plot_data = pd.DataFrame({
    'Date': df['date'].unique(),
    'Interest': df[df['event'] == 'Interest'].groupby('date')['amount'].sum(),
    'Principal': df[df['event'] == 'Principal'].groupby('date')['amount'].sum()
}).fillna(0)

# Create stacked column chart
plot_data.set_index('Date')[['Interest', 'Principal']].plot(kind='bar', stacked=True, figsize=(12, 6))
plt.show()