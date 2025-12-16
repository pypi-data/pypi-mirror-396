from lseg_analytics.pricing.instruments import ir_swaps as irs
from lseg_analytics.pricing.common import AdjustableDate, RelativeAdjustableDate, ReferenceDate, FrequencyEnum
import lseg_analytics.pricing.reference_data.floating_rate_indices as fri
import pandas as pd
from IPython.display import display

# All the attributes below are the required ones for the class "InterestRateLegDefinition".
irs_first_leg = irs.InterestRateLegDefinition(
    rate = irs.FixedRateDefinition(
        rate = irs.Rate(
            value = 3,
            unit = irs.UnitEnum.PERCENTAGE
        )
    ),
    interest_periods = irs.ScheduleDefinition(
        start_date = AdjustableDate(  # Adjustable Date could be modified depending on the conventions
            date = "2025-01-01"
        ),
        end_date = RelativeAdjustableDate( # Relative Adjustable Date could be modified depending on the conventions and tenor
            tenor = "1Y", 
            reference_date = ReferenceDate.START_DATE
        ),
        frequency = FrequencyEnum.QUARTERLY
    ),
    principal = irs.PrincipalDefinition(amount = 1E6, currency = 'USD'),
    payer = irs.PartyEnum.PARTY1,
    receiver = irs.PartyEnum.PARTY2
)

# avaibale IR curves for USD
print(fri.search(tags=["currency:USD"]))

# to get the correct index name, one need to use index space then the index name as below
sofr_index = [usd_index for usd_index in fri.search(tags=["currency:USD", "indexTenor:ON"]) if "SOFR" in usd_index.location.name][0]
sofr_index_name = sofr_index.location.space + "/" + sofr_index.location.name

irs_second_leg = irs.InterestRateLegDefinition(
    rate = irs.FloatingRateDefinition(
        index = sofr_index_name
    ),
    interest_periods = irs.ScheduleDefinition(
        start_date = AdjustableDate(  # Adjustable Date could be modified depending on the conventions
            date = "2025-01-01"
        ),
        end_date = RelativeAdjustableDate( # Relative Adjustable Date could be modified depending on the conventions and tenor
            tenor = "1Y", 
            reference_date = ReferenceDate.START_DATE
        ),
        frequency = FrequencyEnum.QUARTERLY
    ),
    principal = irs.PrincipalDefinition(amount = 1E6, currency = 'USD'),
    payer = irs.PartyEnum.PARTY2,
    receiver = irs.PartyEnum.PARTY1
)

# Define the swap using the legs defined before
ir_swap_definition = irs.IrSwapDefinition(
    first_leg = irs_first_leg,
    second_leg = irs_second_leg
)

# Create the instrument from the definition
irs_instrument = irs.IrSwapDefinitionInstrument(
    definition = ir_swap_definition
)

# Instantiate the pricing parameters
pricing_params = irs.IrPricingParameters(
    valuation_date = "2025-07-18",
    report_currency = "USD"
)

#  Execute the calculation using the value() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

# Execute the calculation using the value() function with error handling
try:
    response = irs.value(
        definitions=[irs_instrument],
        pricing_preferences = pricing_params
        
    )
    errors = [a.error for a in response.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("IR Swap pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

valuation = response.analytics[0].valuation
print("Market value", valuation["marketValue"]["value"])
print("Accrued value", valuation["accrued"]["value"])
print("Clean market value", valuation["cleanMarketValue"]["value"])

fixed_cfs = response.analytics[0].first_leg["cashflows"]
start_dates = [cf['startDate'] for cf in fixed_cfs]
end_dates = [cf['endDate'] for cf in fixed_cfs]
fixed_rates = [cf['annualRate']['value'] for cf in fixed_cfs]
dfs = [cf['discountFactor'] for cf in fixed_cfs]
amounts = [cf['amount']['value'] for cf in fixed_cfs]

fixed_cfs_df = pd.DataFrame({"Start Dates": start_dates, "End Dates": end_dates, 
                                "Floating Rates": fixed_rates, "Discount Factors": dfs, "CashFlow Amounts": amounts})
display(fixed_cfs_df)

floating_cfs = response.analytics[0].second_leg["cashflows"]
start_dates = [cf['startDate'] for cf in floating_cfs]
end_dates = [cf['endDate'] for cf in floating_cfs]
floating_rates = [cf['annualRate']['value'] for cf in floating_cfs]
dfs = [cf['discountFactor'] for cf in floating_cfs]
amounts = [cf['amount']['value'] for cf in floating_cfs]

floating_cfs_df = pd.DataFrame({"Start Dates": start_dates, "End Dates": end_dates, 
                                "Floating Rates": floating_rates, "Discount Factors": dfs, "CashFlow Amounts": amounts})
display(floating_cfs_df)

response.analytics[0].risk.duration.value
risks = response.analytics[0].risk
risk_df = pd.DataFrame({"Fields": list(risks.keys()), "Values": [risks[item]["value"] for item in risks]})
display(risk_df)

irs_second_leg.rate.spread_schedule = [irs.DatedRate(
    rate = irs.Rate(value = 5, unit = irs.UnitEnum.BASIS_POINT) # spread if 5 Bps
)]

# Reprice the swap to visualize the impact of the spread
try:
    response = irs.value(
        definitions=[irs_instrument],
        pricing_preferences = pricing_params
        
    )
    errors = [a.error for a in response.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("IR Swap pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

floating_rates_with_spread = [cf['annualRate']['value'] for cf in response.analytics[0].second_leg["cashflows"]]
compare_floating_rates_df = pd.DataFrame({"Floating Rates Without Spread": floating_rates,
                                          "Floating Rates Wiht 5bp Sperad": floating_rates_with_spread})
display(compare_floating_rates_df)

availabel_indexes = fri.search()
indexes = [item['location']['name'] for item in availabel_indexes]
currencies = [item['description']['tags'][0][9:] for item in availabel_indexes]
available_indexes_df = pd.DataFrame({"Index Name": indexes, "Currency": currencies})
display(available_indexes_df.head(10))

availabel_indexes = fri.search(tags=["currency:USD"])
indexes = [item['location']['name'] for item in availabel_indexes]
currencies = [item['description']['tags'][0][9:] for item in availabel_indexes]
available_indexes_df = pd.DataFrame({"Index Name": indexes, "Currency": currencies})
display(available_indexes_df.head(10))