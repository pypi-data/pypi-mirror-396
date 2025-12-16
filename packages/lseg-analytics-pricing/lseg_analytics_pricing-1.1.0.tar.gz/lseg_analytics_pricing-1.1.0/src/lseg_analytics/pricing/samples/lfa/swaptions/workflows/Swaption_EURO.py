from lseg_analytics.pricing.instruments import swaption  as sw

import pandas as pd
import json
import datetime as dt
from IPython.display import display

print("Example 1: 6M x 5Y USD Payer European Swaption")
print("-" * 50)

# Step 1: European Payer Swaption Definition
euro_payer_definition = sw.SwaptionDefinition(
    # European Exercise - Key differentiator
    exercise_style=sw.IPAExerciseStyleEnum.EURO,               # European: exercise ONLY at expiration. Options: EURO, AMER, BERM
    
    # Core Swaption Parameters
    buy_sell=sw.IPABuySellEnum.BUY,                            # Buy protection against rising rates. Options: BUY, SELL
    swaption_type=sw.SwaptionTypeEnum.PAYER,                   # Payer: right to PAY fixed in underlying swap. Options: PAYER, RECEIVER
    
    # Option Timing - 6M into 5Y
    start_date=dt.datetime(2025, 1, 20),                       # Option effective date (T+2 from trade)
    end_date=dt.datetime(2025, 7, 21),                         # Option expiry (ONLY exercise date for European)
    
    # Financial Terms
    notional_amount=50_000_000,                                # $50M notional for corporate hedge
    strike_percent=4.25,                                       # 4.25% strike (fixed rate in underlying swap)
    
    # Settlement Configuration  
    settlement_type=sw.SettlementTypeEnum.PHYSICAL,           # Physical: actually enter swap if exercised. Options: PHYSICAL, CASH, CCP
    premium_settlement_type=sw.PremiumSettlementTypeEnum.SPOT, # Premium paid at trade date. Options: SPOT, FORWARD, SCHEDULE
    delivery_date=dt.datetime(2025, 7, 23),                   # Underlying swap start date (T+2 from expiry)
    
    # European Swaption Specific Parameters
    instrument_tag="EURO_6Mx5Y_PAYER_USD",                    # Tag for identification
    spread_vs_atm_in_bp=0.0,                                  # At-the-money strike (0bp spread from ATM)
    
    # Underlying 5-Year USD SOFR Swap
    underlying_definition=sw.SwapDefinition(
        template="OIS_SOFR",                                   # Standard USD SOFR overnight index swap
        start_date=dt.datetime(2025, 7, 23),                   # Swap effective date (delivery_date)
        end_date=dt.datetime(2030, 7, 23),                     # 5Y maturity from swap start in date format
        instrument_tag="5Y_SOFR_Underlying_Swap"
    )
)

print(f"✓ European Payer Swaption Created:")
print(f"  Swaption Type: {euro_payer_definition.swaption_type} (Right to pay fixed)")
print(f"  Exercise Style: {euro_payer_definition.exercise_style} (Only one exercise opportunity at expiration date)")
print(f"  Position: {euro_payer_definition.buy_sell} (buy protection against rising rates)")
print(f"  Option Period: {euro_payer_definition.start_date.strftime('%Y-%m-%d')} to {euro_payer_definition.end_date.strftime('%Y-%m-%d')} (6M)")
print(f"  Underlying: {(euro_payer_definition.end_date - euro_payer_definition.start_date).days} days into 5Y swap")
print(f"  Strike Rate: {euro_payer_definition.strike_percent}% (fixed rate to pay if exercised)")
print(f"  Settlement: {euro_payer_definition.settlement_type}")
print(f"  ATM Spread: {euro_payer_definition.spread_vs_atm_in_bp}bp (At-the-money)")
print(f"  Premium Settlement: {euro_payer_definition.premium_settlement_type}")

print("Example 2: 1Y x 10Y GBP Receiver European Swaption")
print("-" * 50)

# Step 2: European Receiver Swaption Definition  
euro_receiver_definition = sw.SwaptionDefinition(
    # European Exercise Style
    exercise_style=sw.IPAExerciseStyleEnum.EURO,               # European style - single exercise date
    
    # Receiver Swaption Parameters
    buy_sell=sw.IPABuySellEnum.BUY,                            # Buy protection against falling rates
    swaption_type=sw.SwaptionTypeEnum.RECEIVER,                # Receiver: right to RECEIVE fixed in underlying swap
    
    # Extended Option Period
    start_date=dt.datetime(2025, 1, 20),                       # Option start
    end_date=dt.datetime(2026, 1, 20),                         # 1-year option expiry in date format
    
    # Larger Notional
    notional_amount=100_000_000,                               # £100M notional
    strike_percent=3.75,                                       # 3.75% receiver strike
    
    # Cash Settlement Configuration
    settlement_type=sw.SettlementTypeEnum.CASH,               # Cash settlement: receive PnL without entering swap
    premium_settlement_type=sw.PremiumSettlementTypeEnum.SPOT, # Upfront premium payment
    delivery_date=dt.datetime(2026, 1, 22),                   # Cash settlement calculation date
    
    # European Swaption Specific Parameters
    instrument_tag="EURO_1Yx10Y_RECEIVER_GBP",
    spread_vs_atm_in_bp=-25.0,                                # 25bp below ATM (out-of-the-money receiver)

    # Underlying 10-Year GBP SONIA Swap
    underlying_definition=sw.SwapDefinition(
        template="OIS_SONIA", 
        start_date=dt.datetime(2026, 1, 22),                   # 10Y swap starts at option expiry
        end_date=dt.datetime(2036, 1, 22),                     # 10Y tenor in date format
        instrument_tag="10Y_SONIA_Underlying_Swap"
    )
)

print(f"✓ European Receiver Swaption Created:")
print(f"  Swaption Type: {euro_receiver_definition.swaption_type} (Right to receive fixed)")
print(f"  Exercise Style: {euro_receiver_definition.exercise_style} (Only one exercise opportunity at expiration date)")
print(f"  Position: {euro_receiver_definition.buy_sell} (buy protection against falling rates)")
print(f"  Option Period: {euro_receiver_definition.start_date.strftime('%Y-%m-%d')} to {euro_receiver_definition.end_date.strftime('%Y-%m-%d')} (1Y)")
print(f"  Underlying: 10Y SONIA swap")
print(f"  Strike rate: {euro_receiver_definition.strike_percent}% (fixed rate to receive if exercised)")
print(f"  Settlement: {euro_receiver_definition.settlement_type} (no physical swap delivery)")
print(f"  ATM Spread: {euro_receiver_definition.spread_vs_atm_in_bp}bp (Out-of-the-money)")
print(f"  Premium Settlement: {euro_receiver_definition.premium_settlement_type}")

print("Example 3: 3M x 2Y EUR Payer European Swaption")
print("-" * 50)

# Step 3: Short-dated European Swaption (Different Currency)
euro_short_definition = sw.SwaptionDefinition(
    exercise_style=sw.IPAExerciseStyleEnum.EURO,               # European exercise
    buy_sell=sw.IPABuySellEnum.SELL,                           # Sell swaption (receive premium)
    swaption_type=sw.SwaptionTypeEnum.PAYER,                   # Payer swaption: right to pay fixed in underlying swap for buyer.
    
    # Short Option Period
    start_date=dt.datetime(2025, 1, 20),
    end_date=dt.datetime(2025, 4, 21),                         # 3-month option in date format
    
    # EUR Denominated
    notional_amount=25_000_000,                                # €25M notional
    strike_percent=3.00,                                       # 3.00% EUR strike

    # Cash Settlement Configuration
    settlement_type=sw.SettlementTypeEnum.CASH,                # Cash settlement
    premium_settlement_type=sw.PremiumSettlementTypeEnum.FORWARD, # Forward premium settlement
    delivery_date=dt.datetime(2025, 4, 23),
    
    # Short-dated Strategy
    instrument_tag="EURO_3Mx2Y_PAYER_EUR_SELL",
    spread_vs_atm_in_bp=15.0,                                 # 15bp above ATM (in-the-money payer)
    
    # EUR 2Y ESTR Swap - Custom Definition 
    underlying_definition=sw.SwapDefinition(
        start_date=dt.datetime(2025, 4, 23),                   # Swap effective date
        end_date=dt.datetime(2027, 4, 23),                     # 2Y swap maturity in date format
        instrument_tag="2Y_ESTR_Full_Custom_Swap",
        
        legs=[
            # Fixed Rate Leg (Payer Leg) - What swaption holder pays if exercised
            sw.SwapLegDefinition(
                direction=sw.IPADirectionEnum.PAID,                     
                notional_amount=25_000_000,                            # €25M notional
                notional_ccy="EUR",                                   
                interest_type=sw.InterestTypeEnum.FIXED,               
                fixed_rate_percent=3.00,                               # 3.00% fixed rate (matches strike)
                interest_payment_frequency=sw.InterestPaymentFrequencyEnum.ANNUAL,  # Annual payments
                interest_calculation_method=sw.InterestCalculationMethodEnum.DCB_30_360,  # 30/360 day count
                payment_business_day_convention=sw.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING, # Modified following payment business day convention 

                leg_tag="FixedLeg",                                 
 
            ),
            
            # Floating Rate Leg (Receiver Leg) - What swaption holder receives if exercised
            sw.SwapLegDefinition(
                direction=sw.IPADirectionEnum.RECEIVED,               
                notional_amount=25_000_000,                            # €25M notional (same as fixed leg)
                notional_ccy="EUR",                                  
                interest_type=sw.InterestTypeEnum.FLOAT,             
                
                # ESTR (Euro Short Term Rate) Index Configuration
                index_name="ESTR",                                     # European Short Term Rate
                index_tenor="1D",                                      # Daily rate (overnight)
                interest_payment_frequency=sw.InterestPaymentFrequencyEnum.ANNUAL,  # Annual payments
                index_reset_frequency=sw.IndexResetFrequencyEnum.EVERY_WORKING_DAY, 
                
                # EUR Market Conventions
                interest_calculation_method=sw.InterestCalculationMethodEnum.DCB_ACTUAL_360,  # ACT/360 for ESTR
                payment_business_day_convention=sw.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING, # Modified following payment business day convention 
                
                # Date Settings  
                leg_tag="FloatingLeg",                                

            )
        ]
    )
)

print(f"✓ Short European Swaption with Full Swap Definition Created:")
print(f"  Swaption Type: {euro_short_definition.swaption_type} (Right to pay fixed)")
print(f"  Exercise Style: {euro_short_definition.exercise_style} (Only one exercise opportunity at expiration date)")
print(f"  Position: {euro_short_definition.buy_sell} (premium received)")
print(f"  Option Period: {euro_short_definition.start_date.strftime('%Y-%m-%d')} to {euro_short_definition.end_date.strftime('%Y-%m-%d')} (3M)")
print(f"  Underlying: customed 2Y ESTR Swap (see details below)")
print(f"  Settlement: {euro_short_definition.settlement_type}")
print(f"  ATM Spread: {euro_short_definition.spread_vs_atm_in_bp}bp (In-the-money)")
print(f"  Premium Settlement: {euro_short_definition.premium_settlement_type}")
print()
print(f"  Underlying Swap Details:")
print(f"    Fixed Leg: PAY {euro_short_definition.underlying_definition.legs[0].fixed_rate_percent}% annually")
print(f"    Floating Leg: RECEIVE ESTR compounded annually")
print(f"    Day Count: Fixed=30/360, Floating=ACT/360")
print(f"    Payment Frequency: {euro_short_definition.underlying_definition.legs[0].interest_payment_frequency}")
print(f"    Business Day Convention: {euro_short_definition.underlying_definition.legs[0].payment_business_day_convention}")

print("Creating Instrument Objects for Batch Pricing...")
print("-" * 50)

# Create instrument containers
euro_payer_instrument = sw.SwaptionDefinitionInstrument(definition=euro_payer_definition)
euro_receiver_instrument = sw.SwaptionDefinitionInstrument(definition=euro_receiver_definition) 
euro_short_instrument = sw.SwaptionDefinitionInstrument(definition=euro_short_definition)

# Batch instrument list for simultaneous pricing
european_swaptions_batch = [euro_payer_instrument, euro_receiver_instrument, euro_short_instrument]

print(f"✓ Created {len(european_swaptions_batch)} European swaption instruments")
print("  - 6M x 5Y USD Payer (Physical settlement)")
print("  - 1Y x 10Y GBP Receiver (Cash settlement)")
print("  - 3M x 2Y EUR Payer Sold (Cash settlement)")
print()

print("Configuring European Swaption Pricing Parameters...")
print("-" * 50)

# Pricing parameters optimized for European swaption analytics
euro_pricing_params = sw.SwaptionPricingParameters(
    valuation_date=dt.datetime(2025, 1, 18),                   # Current valuation date
    price_side=sw.PriceSideEnum.MID,                           # Mid-market pricing for fair value
    report_ccy="USD"                                           # Optional: force USD reporting
)

print(f"✓ European Swaption Pricing Configuration:")
print(f"  Valuation Date: {euro_pricing_params.valuation_date.strftime('%Y-%m-%d')}")
print(f"  Price Side: {euro_pricing_params.price_side}")
print(f"  Report Currency: {euro_pricing_params.report_ccy}")
print()

basic_fields="InstrumentTag, NotionalCcy, MarketValueInDealCcy, ReportCcy, MarketValueInReportCcy, premiumPercent, premiumBp, ImpliedVolatilityPercent, ImpliedVolatilityBp"
sensitivity_fields_percent="deltaPercent, gammaPercent, vegaPercent, thetaPercent"
sensitivity_fields_absolute="DeltaAmountInReportCcy, GammaAmountInReportCcy, VegaAmountInReportCcy, ThetaAmountInReportCcy, HedgeNotionalAmountInReportCcy"

# combine basic and sensitivity fields
fields=basic_fields + "," + sensitivity_fields_percent + "," + sensitivity_fields_absolute

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instrument definitions for batch processing

try:
    response = sw.price(
        definitions=european_swaptions_batch,
        pricing_preferences=euro_pricing_params,
        fields=fields
    )
    
    all_calculations_ok = True
    for item in response['data']['analytics']:
        analytics_data = item
        if analytics_data['error'] == {}:
            valuation_data = analytics_data.get('valuation', {})
        else:
            all_calculations_ok = False
            print("   - InstrumentTag:", analytics_data['tabularData']['data'][0])
            print(f"   Pricing error: {analytics_data['error']}")
    if all_calculations_ok:
        print("Calculation successful!")
except Exception as e:
    print(f"   Calculation failed: {str(e)}")
    raise

# Access the valuation object for #1 deal
valuation = response.data.analytics[0].valuation
print("Swaption Valuation Results:")
print(json.dumps(valuation.as_dict(), indent=4))

# Access the greeks object for #1 deal
print("Swaption Greeks Results:")
print(json.dumps(response.data.analytics[0].greeks.as_dict(), indent=4))

# Convert swaption analytics to DataFrame for better visualization
print("Swaption Analytics Summary:")
columns = [item['name'] for item in response['data']['analytics'][0]['tabularData']['headers']]
response_data = [item['tabularData']['data'] for item in response['data']['analytics']]

response_df = pd.DataFrame(response_data, columns=columns)

# Set InstrumentTag as index for better readability
response_df.set_index('InstrumentTag', inplace=True)

# Round numerical values to 2 decimal places while keeping strings unchanged
response_df_rounded = response_df.copy()
for col in response_df_rounded.columns:
    if response_df_rounded[col].dtype in ['float64', 'int64']:
        response_df_rounded[col] = response_df_rounded[col].round(2)

display(response_df_rounded.T)