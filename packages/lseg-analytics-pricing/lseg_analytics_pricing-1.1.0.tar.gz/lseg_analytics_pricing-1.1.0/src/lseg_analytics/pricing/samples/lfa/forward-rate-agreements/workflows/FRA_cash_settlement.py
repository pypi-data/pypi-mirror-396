from lseg_analytics.pricing.instruments import forward_rate_agreement as fra
import datetime as dt
import json

# Create FRA defintion object
fra_definition = fra.ForwardRateAgreementDefinition(
    start_tenor="5M", # mandatory
    fixed_rate_percent=4,
    end_tenor="8M", # mandatory
    notional_ccy="JPY", # mandatory
    index_name="TONAR",
    notional_amount=1000000
)

# Create FRA instrument defintion object
fra_instrument = fra.ForwardRateAgreementDefinitionInstrument(
    definition = fra_definition
)

# Create FRA pricing parameters object - optional
fra_parameters = fra.ForwardRateAgreementPricingParameters(
    valuation_date  = dt.datetime.strptime("2025-07-21", "%Y-%m-%d")
)

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instruments definitions for batch processing

fra_response = fra.price(
    definitions = [fra_instrument], 
    pricing_preferences = fra_parameters
)

# Access the description object
description = fra_response.data.analytics[0].description
print(json.dumps(description.as_dict(), indent=4))

# Access to cash settlement
cash_settlement = fra_response.data.analytics[0].cashflows.cash_flows[0]["payments"][0]
print(json.dumps(cash_settlement, indent=4))

# Access the pricing analysis object
pricing_analysis = fra_response.data.analytics[0].pricing_analysis
print(json.dumps(pricing_analysis.as_dict(), indent=4))

# Access the valuation object
valuation = fra_response.data.analytics[0].valuation
print(json.dumps(valuation.as_dict(), indent=4))

print("RatePercent difference computed x 100:", 100 * (pricing_analysis.fixed_rate_percent - pricing_analysis.par_rate_percent))
print("SpreadBp returned:", pricing_analysis.spread_bp)
print("Difference:", 100 * (pricing_analysis.fixed_rate_percent - pricing_analysis.par_rate_percent) - pricing_analysis.spread_bp)

cash_settlement_amount = cash_settlement["amount"]
nb_days = (description.end_date - description.start_date).days
computed_cash_settlement_amount = description.notional_amount * ((pricing_analysis.par_rate_percent - pricing_analysis.fixed_rate_percent) / 100) * (nb_days / 360)
print("Day count convention:", description.interest_calculation_method)
print("Computed cash settlement:", computed_cash_settlement_amount)
print("Cash settlement returned by pricer:", cash_settlement_amount)
print("Difference:", computed_cash_settlement_amount - cash_settlement_amount)

computed_fra_valuation = computed_cash_settlement_amount * pricing_analysis.discount_factor
print("Computed valuation:", computed_fra_valuation)
print("Valuation returned by pricer:", valuation.market_value_in_deal_ccy)
print("Difference:", computed_fra_valuation - valuation.market_value_in_deal_ccy)