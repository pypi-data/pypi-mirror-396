from lseg_analytics.pricing.instruments import ir_swaps as irs
from lseg_analytics.pricing.common import AdjustableDate, RelativeAdjustableDate, ReferenceDate, FrequencyEnum, DateMovingConvention
import lseg_analytics.pricing.reference_data.floating_rate_indices as fri
import pandas as pd
from IPython.display import display

ccs_first_leg = irs.InterestRateLegDefinition(
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
    payment_offset = irs.OffsetDefinition( # Defines difference between the actual payment date and the interest period reference date
        tenor = "2D",
        direction = irs.DirectionEnum.FORWARD,
        reference_date = irs.CouponReferenceDateEnum.PERIOD_END_DATE,
        business_day_adjustment = irs.BusinessDayAdjustmentDefinition(calendars = ["USA", "CHN"], convention = DateMovingConvention.MODIFIED_FOLLOWING)
        
    ),
    principal = irs.PrincipalDefinition(
        currency = "CNY",
        amount = 1000000,
        final_principal_exchange = True
    ),
    payer = irs.PartyEnum.PARTY1,
    receiver = irs.PartyEnum.PARTY2
)

# avaibale IR curves for USD
print(fri.search(tags=["currency:USD"]))

# to get the correct index name, one need to use index space then the index name as below
sofr_index = [usd_index for usd_index in fri.search(tags=["currency:USD", "indexTenor:ON"]) if "SOFR" in usd_index.location.name][0]
sofr_index_name = sofr_index.location.space + "/" + sofr_index.location.name

ccs_second_leg = irs.InterestRateLegDefinition(
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
    payment_offset = irs.OffsetDefinition( # Defines difference between the actual payment date and the interest period reference date
        tenor = "2D",
        direction = irs.DirectionEnum.FORWARD,
        reference_date = irs.CouponReferenceDateEnum.PERIOD_END_DATE,
        business_day_adjustment = irs.BusinessDayAdjustmentDefinition(calendars = ["USA", "CHN"], convention = DateMovingConvention.MODIFIED_FOLLOWING)
        
    ),
    principal = irs.PrincipalDefinition(
        currency = "USD",
        final_principal_exchange = True
    ),
    payer = irs.PartyEnum.PARTY2,
    receiver = irs.PartyEnum.PARTY1
)

# Define the swap using the legs defined before
ccs_definition = irs.IrSwapDefinition(
    first_leg = ccs_first_leg,
    second_leg = ccs_second_leg
)

# Create the instrument from the definition
ccs_instrument = irs.IrSwapDefinitionInstrument(
    definition = ccs_definition
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
        definitions=[ccs_instrument],
        pricing_preferences = pricing_params
        
    )
    errors = [a.error for a in response.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Cross Currency IR Swap pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

valuation = response.analytics[0].valuation
print("Market value : ", valuation["marketValue"]["value"])
print("Accrued value : ", valuation["accrued"]["value"])
print("Clean market value : ", valuation["cleanMarketValue"]["value"])

print("Deal Currency : ", valuation["marketValue"]["dealCurrency"]["currency"])
print("Report Currency : ", valuation["marketValue"]["reportCurrency"]["currency"])

fixed_cfs = response.analytics[0].first_leg["cashflows"]
start_dates = [cf['startDate'] for cf in fixed_cfs]
end_dates = [cf['endDate'] for cf in fixed_cfs]
fixed_rates = [cf['annualRate']['value'] for cf in fixed_cfs]
currency = [cf['amount']['currency'] for cf in fixed_cfs]
amounts = [cf['amount']['value'] for cf in fixed_cfs]
paymentTypes = [cf['paymentType'] for cf in fixed_cfs]

fixed_cfs_df = pd.DataFrame({"Start Dates": start_dates, "End Dates": end_dates, 
                                "Fixed Rates": fixed_rates, "Currency": currency, "CashFlow Amounts": amounts,
                                "Payment Type": paymentTypes})
display(fixed_cfs_df)

floating_cfs = response.analytics[0].second_leg["cashflows"]
start_dates = [cf['startDate'] for cf in floating_cfs]
end_dates = [cf['endDate'] for cf in floating_cfs]
floating_rates = [cf['annualRate']['value'] for cf in floating_cfs]
currency = [cf['amount']['currency'] for cf in floating_cfs]
amounts = [cf['amount']['value'] for cf in floating_cfs]
paymentTypes = [cf['paymentType'] for cf in floating_cfs]

floating_cfs_df = pd.DataFrame({"Start Dates": start_dates, "End Dates": end_dates, 
                                "Floating Rates": floating_rates, "Currency": currency, "CashFlow Amounts": amounts,
                                "Payment Type": paymentTypes})
display(floating_cfs_df)

risks = response.analytics[0].risk
risk_df = pd.DataFrame({"Fields": list(risks.keys()), "Values": [risks[item]["value"] for item in risks]})
display(risk_df)