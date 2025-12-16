from lseg_analytics.pricing.instruments import swaption  as sw

import pandas as pd
import json
import datetime as dt
from IPython.display import display

print("Example 1: 2Y x 5Y USD Payer Bermudan Swaption")
print("-" * 50)

# Step 1: Bermudan Payer Swaption Definition
berm_payer_definition = sw.SwaptionDefinition(
    # Bermudan Exercise Style - Key differentiator
    exercise_style=sw.IPAExerciseStyleEnum.BERM,               # Bermudan: exercise on multiple specified dates

    # Bermudan Specific Configuration
    bermudan_swaption_definition=sw.BermudanSwaptionDefinition(
        exercise_schedule_type=sw.ExerciseScheduleTypeEnum.FIXED_LEG,  # Use fixed leg coupon dates as exercise dates
        notification_days=5,                                   # 5 business days notice required for exercise
    ),
    
    # Core Swaption Parameters  
    buy_sell=sw.IPABuySellEnum.BUY,                            # Buy protection against rising rates
    swaption_type=sw.SwaptionTypeEnum.PAYER,                   # Payer: right to PAY fixed in underlying swap
    
    # Option Timing - 2Y into 5Y with quarterly exercise opportunities
    start_date=dt.datetime(2025, 1, 20),                       # Option effective date (T+2 from trade)
    end_date=dt.datetime(2027, 1, 20),                         # 2-year option period in date format
    
    # Financial Terms
    notional_amount=75_000_000,                                # $75M notional for institutional portfolio
    strike_percent=4.50,                                       # 4.50% strike (fixed rate in underlying swap)
    
    # Settlement Configuration  
    settlement_type=sw.SettlementTypeEnum.PHYSICAL,           # Physical: actually enter swap if exercised
    premium_settlement_type=sw.PremiumSettlementTypeEnum.SPOT, # Premium paid at trade date
    delivery_date=dt.datetime(2027, 1, 22),                   # Underlying swap start date (T+2 from expiry)
    
    # General Swaption Parameters
    instrument_tag="BERM_2Yx5Y_PAYER_USD",                    # Tag for identification
    spread_vs_atm_in_bp=25.0,                                 # 25bp above ATM (in-the-money payer)
    
    # Underlying 5-Year USD SOFR Swap
    underlying_definition=sw.SwapDefinition(
        template="OIS_SOFR",                                   # Standard USD SOFR overnight index swap
        start_date=dt.datetime(2027, 1, 22),                   # Swap effective date (delivery_date)
        end_date=dt.datetime(2032, 1, 22),                     # 5Y maturity from swap start in date format
        instrument_tag="5Y_SOFR_Underlying_Swap"
    )
)

print(f"✓ Bermudan Payer Swaption Created:")
print(f"  Swaption Type: {berm_payer_definition.swaption_type} (Right to pay fixed)")
print(f"  Exercise Style: {berm_payer_definition.exercise_style} (Multiple exercise opportunities)")
print(f"  Position: {berm_payer_definition.buy_sell} (buy protection against rising rates)")
print(f"  Exercise Schedule: {berm_payer_definition.bermudan_swaption_definition.exercise_schedule_type} coupon dates")
print(f"  Option Period: {berm_payer_definition.start_date.strftime('%Y-%m-%d')} to {berm_payer_definition.end_date.strftime('%Y-%m-%d')} (2Y)")
print(f"  Underlying: 2Y option period into 5Y swap")
print(f"  Strike Rate: {berm_payer_definition.strike_percent}% (fixed rate to pay if exercised)")
print(f"  Notification Period: {berm_payer_definition.bermudan_swaption_definition.notification_days} business days")
print(f"  Settlement: {berm_payer_definition.settlement_type}")
print(f"  ATM Spread: {berm_payer_definition.spread_vs_atm_in_bp}bp (In-the-money)")
print(f"  Premium Settlement: {berm_payer_definition.premium_settlement_type}")

print("Example 2: 1Y x 7Y EUR Receiver Bermudan Swaption")
print("-" * 50)

# Step 2: Bermudan Receiver Swaption Definition  
berm_receiver_definition = sw.SwaptionDefinition(
    # Bermudan Exercise Style - Key differentiator
    exercise_style=sw.IPAExerciseStyleEnum.BERM,               # Bermudan: exercise on multiple specified dates

    # Bermudan Specific Configuration
    bermudan_swaption_definition=sw.BermudanSwaptionDefinition(
        exercise_schedule_type=sw.ExerciseScheduleTypeEnum.FLOAT_LEG,  # Use floating leg reset dates
        notification_days=3,                                   # 3 business days notice for exercise
    ),
    
    # Receiver Swaption Parameters
    buy_sell=sw.IPABuySellEnum.BUY,                            # Buy protection against falling rates
    swaption_type=sw.SwaptionTypeEnum.RECEIVER,                # Receiver: right to RECEIVE fixed in underlying swap
    
    # Extended Option Period with Multiple Exercise Dates
    start_date=dt.datetime(2025, 1, 20),                       # Option start
    end_date=dt.datetime(2026, 1, 20),                         # 1-year option expiry in date format
    
    # Larger Notional
    notional_amount=150_000_000,                               # €150M notional
    strike_percent=3.25,                                       # 3.25% receiver strike
    
    # Cash Settlement Configuration
    settlement_type=sw.SettlementTypeEnum.CASH,               # Cash settlement: receive PnL without entering swap
    premium_settlement_type=sw.PremiumSettlementTypeEnum.SPOT, # Upfront premium payment
    delivery_date=dt.datetime(2026, 1, 22),                   # Cash settlement calculation date
    
    # General Swaption Parameters
    instrument_tag="BERM_1Yx7Y_RECEIVER_EUR",
    spread_vs_atm_in_bp=-15.0,                                # 15bp below ATM (out-of-the-money receiver)

    # Underlying 7-Year EUR ESTR Swap
    underlying_definition=sw.SwapDefinition(
        template="OIS_ESTR", 
        start_date=dt.datetime(2026, 1, 22),                   # 7Y swap starts at option expiry
        end_date=dt.datetime(2033, 1, 22),                     # 7Y tenor in date format
        instrument_tag="7Y_ESTR_Underlying_Swap"
    )
)

print(f"✓ Bermudan Receiver Swaption Created:")
print(f"  Swaption Type: {berm_receiver_definition.swaption_type} (Right to receive fixed)")
print(f"  Exercise Style: {berm_receiver_definition.exercise_style} (Multiple exercise opportunities)")
print(f"  Position: {berm_receiver_definition.buy_sell} (buy protection against falling rates)")
print(f"  Exercise Schedule: {berm_receiver_definition.bermudan_swaption_definition.exercise_schedule_type} coupon dates")
print(f"  Option Period: {berm_receiver_definition.start_date.strftime('%Y-%m-%d')} to {berm_receiver_definition.end_date.strftime('%Y-%m-%d')} (1Y)")
print(f"  Underlying: 1Y option period into 7Y swap")
print(f"  Strike Rate: {berm_receiver_definition.strike_percent}% (fixed rate to receive if exercised)")
print(f"  Notification Period: {berm_receiver_definition.bermudan_swaption_definition.notification_days} business days")
print(f"  Settlement: {berm_receiver_definition.settlement_type}")
print(f"  ATM Spread: {berm_receiver_definition.spread_vs_atm_in_bp}bp (Out-of-the-money)")
print(f"  Premium Settlement: {berm_receiver_definition.premium_settlement_type}")

print("Example 3: 6M x 10Y GBP Payer Bermudan Swaption (Custom Exercise Schedule)")
print("-" * 50)

# Define custom quarterly exercise dates
custom_exercise_dates = [
    dt.datetime(2025, 7, 21),   # 6M from start (first exercise opportunity)
    dt.datetime(2025, 10, 21),  # 9M from start
    dt.datetime(2026, 1, 21),   # 12M from start (final exercise opportunity)
]

# Step 3: Bermudan Swaption with User-Defined Exercise Schedule
berm_custom_definition = sw.SwaptionDefinition(
    # Bermudan Exercise Style - Key differentiator
    exercise_style=sw.IPAExerciseStyleEnum.BERM,               # Bermudan: exercise on multiple specified dates

    # Bermudan Specific Configuration
    bermudan_swaption_definition=sw.BermudanSwaptionDefinition(
        exercise_schedule_type=sw.ExerciseScheduleTypeEnum.USER_DEFINED,  # User-defined exercise dates
        exercise_schedule=custom_exercise_dates,               # Explicitly defined exercise opportunities
        notification_days=10,                                  # 10 business days notice (longer period)
    ),
    
    buy_sell=sw.IPABuySellEnum.SELL,                           # Sell swaption (receive premium)
    swaption_type=sw.SwaptionTypeEnum.PAYER,                   # Payer swaption
    
    # Short Option Period with Custom Exercises
    start_date=dt.datetime(2025, 1, 20),
    end_date=dt.datetime(2025, 7, 21),                         # 6M total option period in date format
    
    # GBP Denominated
    notional_amount=50_000_000,                                # £50M notional
    strike_percent=4.75,                                       # 4.75% GBP strike

    # Cash Settlement Configuration
    settlement_type=sw.SettlementTypeEnum.CASH,                # Cash settlement
    premium_settlement_type=sw.PremiumSettlementTypeEnum.FORWARD, # Forward premium settlement
    delivery_date=dt.datetime(2025, 7, 21),
    
    # General Swaption Parameters
    instrument_tag="BERM_6Mx10Y_PAYER_GBP_CUSTOM",
    spread_vs_atm_in_bp=35.0,                                 # 35bp above ATM (deep in-the-money payer)
    
    # Underlying 10Y GBP SONIA Swap with Custom Definition
    underlying_definition=sw.SwapDefinition(
        start_date=dt.datetime(2025, 7, 21),                   # Swap effective date
        end_date=dt.datetime(2035, 7, 21),                     # 10Y swap maturity
        instrument_tag="10Y_SONIA_Full_Custom_Swap",
        
        legs=[
            # Fixed Rate Leg (Payer Leg) - What swaption holder pays if exercised
            sw.SwapLegDefinition(
                direction=sw.IPADirectionEnum.PAID,                     
                notional_amount=50_000_000,                            # £50M notional
                notional_ccy="GBP",                                   
                interest_type=sw.InterestTypeEnum.FIXED,               
                fixed_rate_percent=4.75,                               # 4.75% fixed rate (matches strike)
                interest_payment_frequency=sw.InterestPaymentFrequencyEnum.ANNUAL,  # Annual payments
                interest_calculation_method=sw.InterestCalculationMethodEnum.DCB_ACTUAL_365,  # ACT/365 for GBP
                payment_business_day_convention=sw.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING,
                leg_tag="FixedLeg",                                 
            ),
            
            # Floating Rate Leg (Receiver Leg) - What swaption holder receives if exercised
            sw.SwapLegDefinition(
                direction=sw.IPADirectionEnum.RECEIVED,               
                notional_amount=50_000_000,                            # £50M notional (same as fixed leg)
                notional_ccy="GBP",                                  
                interest_type=sw.InterestTypeEnum.FLOAT,             
                
                # SONIA (Sterling Overnight Index Average) Configuration
                index_name="SONIA",                                    # Sterling overnight rate
                index_tenor="1D",                                      # Daily rate (overnight)
                interest_payment_frequency=sw.InterestPaymentFrequencyEnum.ANNUAL,  # Annual payments
                index_reset_frequency=sw.IndexResetFrequencyEnum.EVERY_WORKING_DAY, 
                
                # GBP Market Conventions
                interest_calculation_method=sw.InterestCalculationMethodEnum.DCB_ACTUAL_365,  # ACT/365 for GBP
                payment_business_day_convention=sw.PaymentBusinessDayConventionEnum.MODIFIED_FOLLOWING,
                
                leg_tag="FloatingLeg",                                
            )
        ]
    )
)

print(f"✓ Custom Bermudan Swaption with User-Defined Exercise Schedule Created:")
print(f"  Swaption Type: {berm_custom_definition.swaption_type} (Right to pay fixed)")
print(f"  Exercise Style: {berm_custom_definition.exercise_style} (Multiple exercise opportunities)")
print(f"  Position: {berm_custom_definition.buy_sell} (premium received)")
print(f"  Exercise Schedule: {berm_custom_definition.bermudan_swaption_definition.exercise_schedule_type}")
for i, date in enumerate(custom_exercise_dates, 1):
    print(f"    Exercise {i}: {date.strftime('%Y-%m-%d')}")
print(f"  Option Period: {berm_custom_definition.start_date.strftime('%Y-%m-%d')} to {berm_custom_definition.end_date.strftime('%Y-%m-%d')} (6M)")
print(f"  Underlying: 6M option period into 10Y customed swap (see details below)")
print(f"  Strike Rate: {berm_custom_definition.strike_percent}% (fixed rate to receive if exercised)")
print(f"  Notification Period: {berm_custom_definition.bermudan_swaption_definition.notification_days} business days")
print(f"  Settlement: {berm_custom_definition.settlement_type}")
print(f"  ATM Spread: {berm_custom_definition.spread_vs_atm_in_bp}bp (In-the-money)")
print(f"  Premium Settlement: {berm_custom_definition.premium_settlement_type}")
print()
print(f"  Underlying Swap Details:")
print(f"    Fixed Leg: PAY {berm_custom_definition.underlying_definition.legs[0].fixed_rate_percent}% annually")
print(f"    Floating Leg: RECEIVE SONIA compounded annually")
print(f"    Day Count: ACT/365 for both legs (GBP convention)")
print(f"    Payment Frequency: {berm_custom_definition.underlying_definition.legs[0].interest_payment_frequency}")
print()

print("Creating Bermudan Swaption Instruments for Batch Pricing...")
print("-" * 50)

# Create Bermudan swaption instrument containers for pricing operations
berm_payer_instrument = sw.SwaptionDefinitionInstrument(definition=berm_payer_definition)
berm_receiver_instrument = sw.SwaptionDefinitionInstrument(definition=berm_receiver_definition) 
berm_custom_instrument = sw.SwaptionDefinitionInstrument(definition=berm_custom_definition)

# Batch instrument list for simultaneous Bermudan swaption pricing
bermudan_swaptions_batch = [berm_payer_instrument, berm_receiver_instrument, berm_custom_instrument]

print(f"✓ Created {len(bermudan_swaptions_batch)} Bermudan swaption instruments for portfolio pricing:")
print(f"     - 2Y x 5Y USD Payer Bermudan (Physical settlement, FIXED_LEG exercise schedule)")
print(f"     - 1Y x 7Y EUR Receiver Bermudan (Cash settlement, FLOAT_LEG exercise schedule)")
print(f"     - 6M x 10Y GBP Payer Bermudan SOLD (Cash settlement, USER_DEFINED exercise schedule)")
print()

print("Configuring Bermudan Swaption Pricing Parameters...")
print("-" * 50)

# Pricing parameters for swaption analytics
berm_pricing_params = sw.SwaptionPricingParameters(
    valuation_date=dt.datetime(2025, 1, 18),                   # Current valuation date
    price_side=sw.PriceSideEnum.MID,                           # Mid-market pricing for fair value
    report_ccy="USD"                                           # Optional: force USD reporting
)

print(f"✓ Bermudan Swaption Pricing Configuration:")
print(f"  Valuation Date: {berm_pricing_params.valuation_date.strftime('%Y-%m-%d')}")
print(f"  Price Side: {berm_pricing_params.price_side}")
print(f"  Report Currency: {berm_pricing_params.report_ccy}")
print()

basic_fields="InstrumentTag, NotionalCcy, MarketValueInDealCcy, ReportCcy, MarketValueInReportCcy, premiumPercent, premiumBp"
excercise_schedule_field = "ExerciseScheduleArray"
sensitivity_fields_percent="deltaPercent, gammaPercent, vegaPercent, thetaPercent"
sensitivity_fields_absolute="DeltaAmountInReportCcy, GammaAmountInReportCcy, VegaAmountInReportCcy, ThetaAmountInReportCcy, HedgeNotionalAmountInReportCcy"

# combine basic and sensitivity fields
fields=basic_fields + "," + excercise_schedule_field + "," + sensitivity_fields_percent + "," + sensitivity_fields_absolute

# Execute the calculation using the price() function
# The 'definitions' parameter accepts a list of instrument definitions for batch processing

try:
    response = sw.price(
        definitions=bermudan_swaptions_batch,
        pricing_preferences=berm_pricing_params,
        fields=fields
    )

    # Display response structure information
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

response_df = response_df_rounded.drop(columns=['ExerciseScheduleArray'], errors='ignore')

display(response_df.T)

# Extract ExerciseScheduleArray into separate DataFrame for Bermudan analysis

if 'ExerciseScheduleArray' in response_df_rounded.columns:
    # Convert exercise dates to proper format and create DataFrame directly
    exercise_data = {}
    
    for instrument_tag, row in response_df_rounded.iterrows():
        exercise_array = row['ExerciseScheduleArray']
        if exercise_array and isinstance(exercise_array, list):
            # Convert ISO datetime strings to clean date format
            exercise_dates = [pd.to_datetime(date_str).strftime('%Y-%m-%d') for date_str in exercise_array]
            exercise_data[instrument_tag] = exercise_dates
    
    # Create DataFrame with automatic padding (pandas handles different list lengths)
    exercise_df = pd.DataFrame.from_dict(exercise_data, orient='index').T
    exercise_df.index = [f'Exercise_{i+1}' for i in range(len(exercise_df))]
    
    print(f"✓ Extracted Exercise Schedules for {len(exercise_data)} Bermudan Swaptions:")
    
    # Display the exercise schedule matrix
    display(exercise_df)
else:
    print("- ExerciseScheduleArray not found in results")