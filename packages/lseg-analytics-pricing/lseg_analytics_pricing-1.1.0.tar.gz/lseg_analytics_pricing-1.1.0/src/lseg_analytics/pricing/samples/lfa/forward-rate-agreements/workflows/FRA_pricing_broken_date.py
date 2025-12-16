from lseg_analytics.pricing.instruments import forward_rate_agreement as fra
import datetime as dt

# Create FRA defintion object
fra_definition = fra.ForwardRateAgreementDefinition(
    start_date=dt.datetime.strptime("2026-03-01", "%Y-%m-%d"), # mandatory
    fixed_rate_percent=4,
    end_date=dt.datetime.strptime("2026-08-08", "%Y-%m-%d"), # mandatory
    notional_ccy="EUR", # mandatory
    index_name="ESTR",
    notional_amount=1000000
)

# Create FRA instrument defintion object
fra_instrument = fra.ForwardRateAgreementDefinitionInstrument(
    definition = fra_definition
)

# Create FRA pricing parameters object - optional
fra_parameters = fra.ForwardRateAgreementPricingParameters(
    valuation_date  = dt.datetime.strptime("2025-07-21", "%Y-%m-%d"),
    report_ccy="AUD"
)

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

fra_response = fra.price(
    definitions = [fra_instrument], 
    pricing_preferences = fra_parameters
)

valuation = fra_response.data.analytics[0].valuation
print("valuation in EUR:", valuation.market_value_in_deal_ccy)
print("valuation in AUD:", valuation.market_value_in_report_ccy)