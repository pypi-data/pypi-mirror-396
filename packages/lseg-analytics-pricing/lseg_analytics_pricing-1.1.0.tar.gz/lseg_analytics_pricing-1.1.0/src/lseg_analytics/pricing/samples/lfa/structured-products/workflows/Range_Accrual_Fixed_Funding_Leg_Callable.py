import lseg_analytics.pricing.instruments.structured_products as sp

import datetime as dt
import pandas as pd
import json
from IPython.display import display

# 1. Create SP definition object

print("Step 1: Configuring instrument definition...")

callable_RA_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "Callable_RangeAccrual",
    inputs = [
        sp.NameTypeValue(name="StartDate", type = "date", value=dt.date(2025, 9, 15)),
        sp.NameTypeValue(name="EndDate", type = "date", value= dt.date(2030, 9, 15)),
        sp.NameTypeValue(name="Underlying", type = "string", value="EUR"),
        sp.NameTypeValue(name="Notional", type = "string", value="1000000"),
        sp.NameTypeValue(name="PayOrReceiveRA", type = "string", value="Receive"),
        sp.NameTypeValue(name="CMSTenor", type = "string", value="10Y"),
        sp.NameTypeValue(name="CMSRate", type = "string", value="Cmsrate(Underlying,PeriodStart(),CMSTenor)"),
        sp.NameTypeValue(name="UpperBound", type = "string", value="3.2%"),
        sp.NameTypeValue(name="LowerBound", type = "string", value="1.15%"),
        sp.NameTypeValue(name="Coupon", type = "string", value="3.9%"),
        sp.NameTypeValue(name="Frequency", type = "string", value="SemiAnnual"),
		sp.NameTypeValue(name="ObservationFrequency", type = "string", value="Monthly"),
        sp.NameTypeValue(name="DayCount", type = "string", value="30/360"),
        sp.NameTypeValue(name="PayOrReceiveFixed", type = "string", value="Pay"),
        sp.NameTypeValue(name="FixedFrequency", type = "string", value="SemiAnnual"),
        sp.NameTypeValue(name="FixedDayCount", type = "string", value="30/360"),
        sp.NameTypeValue(name="FixedCoupon", type = "string", value="0.9%"),
        sp.NameTypeValue(name="FirstCallDate", type = "date", value=dt.date(2025, 9, 15)),
		sp.NameTypeValue(name="CallFrequency", type = "string", value="SemiAnnual"),
        sp.NameTypeValue(name="CallNoticeGap", type = "string", value="-5b"),
        sp.NameTypeValue(name="CallOwner", type = "string", value="Counterparty"),
        
    ],
    payoff_description = [
			[
				"Schedule type",
				"Schedule description",
				"RangeAccrualLeg",
				"FixedRateLeg",
                "Reinitialisation",
				"Price",
				"PricePercent"
			],
			[
				"AllTheTime",
				"FromTo(DateTable(StartDate,EndDate,Frequency),ObservationFrequency)",
				"$n1 = if(abs(CMSRate)>LowerBound and CMSRate<UpperBound, $n1+1, $n1); $n2 =$n2+1",
				"",
				"",
				"",
                ""
			],
            [
				"OnSchedule PeriodEnd",
				"DateTable(StartDate, EndDate, Frequency, Daycount)",
				"PayOrReceiveRA Coupon*$n1/$n2*InterestTerm()*Notional",
				"",
				"$n1 = 0; $n2 = 0",
				"PayOrReceiveRA Coupon*$n1/$n2*InterestTerm()*Notional",
                "PayOrReceiveRA Coupon*$n1/$n2*InterestTerm()*100"
			],
            [
				"OnSchedule PeriodEnd",
				"DateTable(StartDate, EndDate, FixedFrequency, FixedDaycount)",
				"",
				"PayOrReceiveFixed FixedCoupon*InterestTerm()*Notional",
				"",
				"PayOrReceiveFixed FixedCoupon*InterestTerm()*Notional",
                "PayOrReceiveFixed FixedCoupon*InterestTerm()*100"
			],
            [
				"OnSchedule",
				"DateTable(FirstCallDate, EndDate, CallFrequency,  ResetGap:= CallNoticeGap, Arrear:=Yes)",
				"",
				"",
				"",
				"CallableBy(CallOwner,0)",
                "CallableBy(CallOwner,0)/Notional*100"
			],
            [
                "AtDate",
                "AsOfDate()",
                "",
                "",
                "",
                "",
                "Report(ColumnVal(Price)/Notional*100)"
            ]
		]
)

print("	Instrument definition configured")

# 2. Create SP instrument definition object
print("Step 2: Creating instrument definition object...")

callable_RA = sp.StructuredProductsDefinitionInstrument(definition = callable_RA_definition)
print("	Instrument definition created")

# 3. Create SP parameters object - optional
print("Step 3: Configuring pricing parameters...")

callable_RA_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 9, 12),  # Set your desired valuation date
    numerical_method = sp.GenericNumericalMethod(method="AmericanMonteCarlo"),
    models=[sp.ModelDefinition(
            underlying_code = "EUR",
            underlying_tag = "EUR",
            underlying_currency = "EUR",
            asset_class = "InterestRate",
            model_name= "HullWhite1Factor",
            calibration_list = [
								{
									"StartDate": "2025-09-15",
									"EndDate": "2030-09-15",
									"Frequency": "SemiAnnual",
									"Tenor": "ENDDATE",
									"UserTenor": "",
									"Calendar": "Target",
									"ProductType": "Swaption",
									"Strike": "ATM",
									"CalibrationType": "Bootstrap",
									"Parameter": "Volatility"
								}
                        	]
			)]
)
print("	Pricing parameters configured")

# Execute the calculation using the price() function with error handling
try:
    # The 'definitions' parameter accepts a list of request items for batch processing
    response = sp.price(
        definitions=[callable_RA],
        pricing_preferences=callable_RA_pricing_params,
        market_data=None,
        return_market_data=True,  # or False
        fields=None  # or specify fields as a string
    )
    errors = [a.error for a in response.data.analytics if a.error]
    if errors:
        raise Exception(errors[0].message)
    print("Pricing execution completed")
except Exception as e:
    print(f"Price Calculation failed: {str(e)}")
    raise

# Extract description from response
description = response.data.analytics[0].description

# Convert to dictionary for display
print(json.dumps(description.as_dict(), indent=4))

# Extract vauation from the response
valuation = response.data.analytics[0].valuation

# Convert the dictionary to a DataFrame
df_callable_RA_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_callable_RA_valuation)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_greeks)