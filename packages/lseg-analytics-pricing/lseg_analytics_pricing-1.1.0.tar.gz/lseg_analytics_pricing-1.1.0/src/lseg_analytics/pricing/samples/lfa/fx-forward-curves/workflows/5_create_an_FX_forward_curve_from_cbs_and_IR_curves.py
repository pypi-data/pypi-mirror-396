# ==============================================================================
# MARKET DATA CONFIGURATION
# ==============================================================================

# Trading date for all calculations
valuation_date = "2024-03-11"

# FX Spot Rate
USD_ILS_spot = 3.627

# ==============================================================================
# TENOR STRUCTURE (Common for all instruments)
# ==============================================================================
tenor_list = [
    # Short-term tenors
    "ON", "TN", "SN", "1W", "2W", "3W",
    
    # Monthly tenors
    "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M",
    
    # Yearly tenors
    "1Y", "1Y3M", "1Y6M", "1Y9M", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y",
    
    # Long-term tenors
    "11Y", "12Y", "13Y", "14Y", "15Y", "16Y", "17Y", "18Y", "19Y", "20Y",
    "21Y", "22Y", "23Y", "24Y", "25Y", "26Y", "27Y", "28Y", "29Y", "30Y"
]

# ==============================================================================
# USD INTEREST RATE SWAP SPREADS (%)
# ==============================================================================

# USD SOFR Overnight Index Swap rates (used for forward projections)
USD_sofr_swap_rate_list = [
    # Short-term (ON-3W)
    5.308, 5.308, 5.308, 5.313, 5.317, 5.322,
    # Monthly (1M-11M)  
    5.326, 5.328, 5.325, 5.293, 5.265, 5.234, 5.191, 5.155, 5.113, 5.069, 5.022,
    # Yearly (1Y-10Y)
    4.98, 4.794, 4.638, 4.51, 4.407, 4.101, 3.935, 3.839, 3.787, 3.755, 3.736, 3.725, 3.721,
    # Long-term (11Y-30Y)
    3.721, 3.723, 3.726, 3.729, 3.73, 3.7298, 3.7254, 3.7181, 3.7092, 3.7,
    3.6884, 3.6723, 3.6536, 3.6339, 3.615, 3.5971, 3.5787, 3.5599, 3.541, 3.522
]

# USD Fed Funds Overnight Index Swap rates (used for USD discounting)
USD_fedfunds_swap_rate_list = [
    # Short-term (ON-3W)
    5.33, 5.33, 5.33, 5.33, 5.3314, 5.3333,
    # Monthly (1M-11M)
    5.3354, 5.3355, 5.3319, 5.2971, 5.2681, 5.2368, 5.1922, 5.155, 5.1126, 5.0657, 5.0164,
    # Yearly (1Y-10Y)
    4.973, 4.7832, 4.625, 4.4954, 4.3907, 4.0799, 3.909, 3.8105, 3.7562, 3.7226, 3.7023, 3.69, 3.6848,
    # Long-term (11Y-30Y)
    3.6845, 3.6842, 3.6863, 3.6882, 3.69, 3.6825, 3.6754, 3.6687, 3.6624, 3.6564,
    3.6372, 3.6189, 3.6013, 3.5845, 3.5683, 3.5477, 3.5278, 3.5085, 3.49, 3.472
]

# ==============================================================================
# ILS INTEREST RATE SWAP RATES (%)
# ==============================================================================

# ILS Telbor 3M Interest Rate Swap rates (used for ILS discounting and projections)
ILS_telbor_swap_rate_list = [
    # Short-term (ON-3W) 
    4.5, 4.5, 4.5, 4.5, 4.5, 4.5,
    # Monthly (1M-11M)
    4.49, 4.43, 4.39, 4.35, 4.3125, 4.275, 4.2258, 4.1812, 4.135, 4.0868, 4.0386,
    # Yearly (1Y-10Y)
    3.995, 3.9206, 3.8447, 3.7711, 3.7, 3.61, 3.615, 3.65, 3.715, 3.775, 3.83, 3.885, 3.925,
    # Long-term (11Y-30Y)
    3.9799, 4.035, 4.0683, 4.1018, 4.135, 4.151, 4.167, 4.1829, 4.1989, 4.215,
    4.2309, 4.2469, 4.2629, 4.2789, 4.295, 4.309, 4.3229, 4.337, 4.351, 4.365
]

# ==============================================================================
# CURRENCY BASIS SWAP SPREADS (basis points)
# ==============================================================================

# USD SOFR vs ILS Telbor Currency Basis Swap spreads
USD_sofr_ILS_telbor_cbs_spread_list = [
    # Short-term (ON-3W)
    -15, -15, -15, -20, -20, -20,
    # Monthly (1M-11M)
    -25, -30, -35, -42, -48, -50, -52, -54, -56, -57.4, -58,
    # Yearly (1Y-10Y) 
    -60, -64, -68.2, -72, -76, -93, -101, -106, -108, -110, -110.7, -111.3, -112,
    # Long-term (11Y-30Y)
    -112, -112, -112, -112, -112, -112, -112, -112, -112, -112,
    -112, -112, -112, -112, -112, -109.2, -106.4, -103.6, -100.8, -98
]

import pandas as pd
from IPython.display import display

def display_zc_curve_response(swap_curve_response):   
    """
    Display the zero-coupon curve response data in a DataFrame format.

    """
    zc_curve = [
        {
            "tenor": swap_curve_response.analytics[0].zc_curves[0].points[i].tenor,
            "endDate": swap_curve_response.analytics[0].zc_curves[0].points[i].end_date,
            "discountFactor": swap_curve_response.analytics[0].zc_curves[0].points[i].discount_factor.value,
            "rate": swap_curve_response.analytics[0].zc_curves[0].points[i].rate.value
        }
        for i in range(len(swap_curve_response.analytics[0].zc_curves[0].points))
    ]
    df = pd.DataFrame(zc_curve)
    display(df)

import json as js
from lseg_analytics.pricing.market_data import interest_rate_curves
from lseg_analytics.pricing.market_data.interest_rate_curves import *
from lseg_analytics.pricing.common import *
from lseg_analytics.pricing.reference_data import *
from lseg_analytics.pricing.reference_data import floating_rate_indices
from lseg_analytics.pricing.reference_data.floating_rate_indices import search, load

# Create constituents for USD SOFR curve using the tenor list and rate values
constituents = []

# Get SOFR index name from usd_templates
usd_indexes_ON_templates = floating_rate_indices.search(tags=["currency:USD", "indexTenor:ON"], spaces=["LSEG"])
sofr_index_name = [item["location"]["name"] for item in usd_indexes_ON_templates if "SOFR" in item["location"]["name"]][0]

# Create Overnight Index Swap (OIS) constituents for each tenor and corresponding rate
for i, (tenor, rate) in enumerate(zip(tenor_list, USD_sofr_swap_rate_list)):
    # Create quote object with bid/ask values set to the same rate value
    ois_quote_values_ask_bid = FieldValue(value = rate)
    ois_quote_values = Values(bid = ois_quote_values_ask_bid, ask = ois_quote_values_ask_bid)
    ois_quote = Quote(values_property = ois_quote_values)

    # Create constituent definition using LSEG SOFR OIS template
    ois_constituent_definition = OvernightIndexSwapConstituentDefinition(tenor=tenor, template="LSEG/OIS_SOFR")
    
    # Create the OIS constituent with USD SOFR overnight index
    ois_constituent = OvernightIndexSwapConstituent(
        index=sofr_index_name, 
        quote=ois_quote, 
        definition=ois_constituent_definition
    )
    constituents.append(ois_constituent)

# Create the USD SOFR interest rate curve definition
usd_sofr_curve_definition = IrCurveDefinition(
    index=sofr_index_name, 
    constituents=constituents
)

# Create the interest rate curve instrument for calculation
usd_sofr_irCurve = IrCurveDefinitionInstrument(definition=usd_sofr_curve_definition)

# Calculate the zero-coupon curve using the specified valuation date
usd_sofr_response = calculate( definitions= [usd_sofr_irCurve],
    pricing_preferences=InterestRateCurveCalculationParameters(valuation_date=valuation_date)
)

# Display the calculated zero-coupon curve response for USD SOFR
display_zc_curve_response(usd_sofr_response)

# Create constituents for USD FedFunds curve using the tenor list and spread values
constituents = []

# Get FedFunds index name from usd_templates
usd_indexes_ON_templates = floating_rate_indices.search(tags=["currency:USD", "indexTenor:ON"], spaces=["LSEG"])
fedfunds_index_name = [item["location"]["name"] for item in usd_indexes_ON_templates if "FFER" in item["location"]["name"]][0]

# Create Overnight Index Swap (OIS) constituents for each tenor and corresponding rate
for i, (tenor, rate) in enumerate(zip(tenor_list, USD_fedfunds_swap_rate_list)):
    # Create quote object with bid/ask values set to the same rate value
    ois_quote_values_ask_bid = FieldValue(value = rate)
    ois_quote_values = Values(bid = ois_quote_values_ask_bid, ask = ois_quote_values_ask_bid)
    ois_quote = Quote(values_property = ois_quote_values)

    # Create constituent definition using LSEG Fed Funds OIS template
    ois_constituent_definition = OvernightIndexSwapConstituentDefinition(tenor=tenor, template="LSEG/OIS_FFER")
    
    # Create the OIS constituent with USD Fed Funds overnight index
    ois_constituent = OvernightIndexSwapConstituent(
        index=fedfunds_index_name, 
        quote=ois_quote, 
        definition=ois_constituent_definition
    )
    
    constituents.append(ois_constituent)

# Create the USD Fed Funds interest rate curve definition
usd_ffer_curve_definition = IrCurveDefinition(
    index=fedfunds_index_name, 
    constituents=constituents
)

# Create the interest rate curve instrument for calculation
usd_ffer_irCurve = IrCurveDefinitionInstrument(definition=usd_ffer_curve_definition)

# Calculate the zero-coupon curve using the specified valuation date
usd_ffer_response =  calculate( definitions= [usd_ffer_irCurve],
    pricing_preferences=InterestRateCurveCalculationParameters(valuation_date=valuation_date)
)

# Display the calculated zero-coupon curve response for USD FedFunds
display_zc_curve_response(usd_ffer_response)

# Create constituents for ILS Telbor curve using the tenor list and spread values
constituents = []

# Get telbor index name from ILS index templates²
ils_indexes_3M_templates = floating_rate_indices.search(tags=["currency:ILS", "indexTenor:3M"], spaces=["LSEG"])
telbor_3M_index_name = [item["location"]["name"] for item in ils_indexes_3M_templates if "TELBOR" in item["location"]["name"]][0]

# Create Interest Rate Swap (IRS) constituents for each tenor and corresponding rate
for i, (tenor, rate) in enumerate(zip(tenor_list, ILS_telbor_swap_rate_list)):
    # Create quote object with bid/ask values set to the same rate value
    irs_quote_values_ask_bid = FieldValue(value = rate)
    irs_quote_values = Values(bid = irs_quote_values_ask_bid, ask = irs_quote_values_ask_bid)
    irs_quote = Quote(values_property = irs_quote_values)

    # Create constituent definition using ILS 3M Telbor template
    irs_constituent_definition = InterestRateSwapConstituentDefinition(tenor=tenor, template="ILS_AM3T")
    
    # Create the IRS constituent with ILS TELBOR 3M index
    irs_constituent = InterestRateSwapConstituent(
        index=telbor_3M_index_name, 
        quote=irs_quote, 
        definition=irs_constituent_definition
    )
    
    constituents.append(irs_constituent)

# Create the ILS Telbor interest rate curve definition
ils_Telbor_curve_definition = IrCurveDefinition(
    index=telbor_3M_index_name, 
    constituents=constituents
)

# Create the interest rate curve instrument for calculation
ils_Telbor_irCurve = IrCurveDefinitionInstrument(definition=ils_Telbor_curve_definition)

# Calculate the zero-coupon curve using the specified valuation date
ils_Telbor_response =  calculate( definitions= [ils_Telbor_irCurve],
    pricing_preferences=InterestRateCurveCalculationParameters(valuation_date=valuation_date)
)

# Display the calculated zero-coupon curve response for ILS Telbor
display_zc_curve_response(ils_Telbor_response)

# Import the FX forward curve modules from LSEG Analytics
from lseg_analytics.pricing.market_data.fx_forward_curves import *
from lseg_analytics.pricing.market_data import fx_forward_curves

# ==============================================================================
# STEP 1: Save the previously calculated interest rate curves to workspace
# ==============================================================================

# Save USD SOFR curve (used as forward curve for currency basis swaps)
my_usd_sofr_curve = interest_rate_curves.InterestRateCurve(definition=usd_sofr_curve_definition)
curves = interest_rate_curves.search(spaces=["HOME"], names=["USD_SOFR_IRCurve"])
if (curves):
    interest_rate_curves.delete(space="HOME", name="USD_SOFR_IRCurve")
my_usd_sofr_curve.save(name="USD_SOFR_IRCurve", space="HOME")

# Save USD Fed Funds curve (used as discount curve for USD currency)
my_usd_ffer_curve = interest_rate_curves.InterestRateCurve(definition=usd_ffer_curve_definition)
curves = interest_rate_curves.search(spaces=["HOME"], names=["USD_FFER_IRCurve"])
if (curves):
    interest_rate_curves.delete(space="HOME", name="USD_FFER_IRCurve")
my_usd_ffer_curve.save(name="USD_FFER_IRCurve", space="HOME")

# Save ILS Telbor curve (used as discount curve for ILS currency)
my_ils_telbor_curve = interest_rate_curves.InterestRateCurve(definition=ils_Telbor_curve_definition)
curves = interest_rate_curves.search(spaces=["HOME"], names=["ILS_TELBOR_IRCurve"])
if (curves):
    interest_rate_curves.delete(space="HOME", name="ILS_TELBOR_IRCurve")
my_ils_telbor_curve.save(name="ILS_TELBOR_IRCurve", space="HOME")

# ==============================================================================
# STEP 2: Define curve assignments for FX forward curve construction
# ==============================================================================

# Define which curves to use for discounting each currency's cash flows
discount_curves = [
    {
        "currency": "USD",
        "curve": "HOME/USD_FFER_IRCurve"  # USD Fed Funds for USD discounting
    },
    {
        "currency": "ILS", 
        "curve": "HOME/ILS_TELBOR_IRCurve"  # ILS Telbor for ILS discounting
     }
]

# Define which curves to use for forward rate projections by index
forward_curves = [
    {
        "index": "SOFR", 
        "curve": "HOME/USD_SOFR_IRCurve"    # SOFR curve for SOFR projections
    },
    {
        "index": "TELBOR", 
        "curve": "HOME/ILS_TELBOR_IRCurve"  # Telbor curve for Telbor projections
    }
]

# ==============================================================================
# STEP 3: Create FX Spot constituent
# ==============================================================================

# Create FX spot rate constituent using USD/ILS template
fx_spot_definition = FxSpotConstituentDefinition(template = "USDILS")
fx_spot_quote_definition = QuoteDefinition(instrument_code="ILS=")
fx_spot_quote_values = FieldValue(value=USD_ILS_spot)
fx_spot_quote_values_obj = Values(bid=fx_spot_quote_values, ask=fx_spot_quote_values)
fx_spot_quote = Quote(definition=fx_spot_quote_definition, values_property=fx_spot_quote_values_obj)
fx_spot_constituent = FxSpotConstituent(quote=fx_spot_quote, definition=fx_spot_definition)

# ==============================================================================
# STEP 4: Create Currency Basis Swap constituents
# ==============================================================================

# Create currency basis swap constituents for each tenor
cbs_constituents = []
for i, (tenor, spread) in enumerate(zip(tenor_list, USD_sofr_ILS_telbor_cbs_spread_list)):
    # Create quote for currency basis swap spread
    cbs_quote_definition = QuoteDefinition(instrument_code=f"CBS_{tenor}")
    cbs_quote_values = FieldValue(value=spread)
    cbs_quote_values_obj = Values(bid=cbs_quote_values, ask=cbs_quote_values)
    cbs_quote = Quote(definition=cbs_quote_definition, values_property=cbs_quote_values_obj)
    
    # Create currency basis swap constituent definition
    cbs_constituent_definition = CurrencyBasisSwapConstituentDefinition(
        tenor=tenor, 
        template="LSEG/ILUS3TSRBS"  # USD SOFR vs ILS Telbor basis swap template
    )
    
    # Create the currency basis swap constituent
    cbs_constituent = CurrencyBasisSwapConstituent(
        quote=cbs_quote,
        definition=cbs_constituent_definition
    )
    cbs_constituents.append(cbs_constituent)

# ==============================================================================
# STEP 5: Construct and calculate the FX forward curve
# ==============================================================================

# Combine FX spot and currency basis swap constituents
fx_constituents = [fx_spot_constituent] + cbs_constituents

# Create FX forward curve definition with all components
fx_curve_definition = fx_forward_curves.FxForwardCurveDefinition(
    cross_currency="USDILS",           # Currency pair
    discount_curves=discount_curves,   # Curves for discounting
    forward_curves=forward_curves,     # Curves for forward projections
    constituents=fx_constituents       # Market instruments (spot + basis swaps)
)

# Create FX curve instrument for calculation
fx_curve_definition_instrument = fx_forward_curves.FxForwardCurveDefinitionInstrument(definition=fx_curve_definition)

# Calculate the FX forward curve
print(f"fx_curve_definition_instrument: {fx_curve_definition_instrument}")
fx_curve_response = fx_forward_curves.calculate(
    definitions=[fx_curve_definition_instrument],
    pricing_preferences=fx_forward_curves.FxForwardCurveCalculationParameters(valuation_date=valuation_date)
)

# ==============================================================================
# STEP 6: Extract and display results
# ==============================================================================

# Extract FX forward curve data points (tenor, end date, outright forward rate)
fx_curve = []
for i in range(len(fx_curve_response.analytics[0].outright_curve.points)):
    fx_curve.append({
        "tenor": fx_curve_response.analytics[0].outright_curve.points[i].tenor,
        "endDate": fx_curve_response.analytics[0].outright_curve.points[i].end_date,
        "outright": fx_curve_response.analytics[0].outright_curve.points[i].outright.mid
    })

# Display the calculated FX forward curve as a DataFrame
df = pd.DataFrame(fx_curve)
display(df)