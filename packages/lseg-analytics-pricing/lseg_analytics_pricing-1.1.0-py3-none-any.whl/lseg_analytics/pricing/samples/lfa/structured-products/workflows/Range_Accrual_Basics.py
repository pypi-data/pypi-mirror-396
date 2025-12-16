from lseg_analytics.pricing.instruments import structured_products as sp

import datetime as dt
import pandas as pd
import json
from IPython.display import display

# 1. Create SP definition object

print("Step 1: Configuring instrument definition...")

range_accrual_definition = sp.StructuredProductsDefinition(
    deal_ccy = "EUR",
    instrument_tag = "RangeAccrual",
    inputs = [
        sp.NameTypeValue(name="StartDate", type = "date", value=dt.date(2025, 9, 15)),
        sp.NameTypeValue(name="EndDate", type = "date", value= dt.date(2035, 9, 15)),
        sp.NameTypeValue(name="Underlying", type = "string", value="EUR"),
        sp.NameTypeValue(name="Notional", type = "string", value="1000000"),
        sp.NameTypeValue(name="Frequency", type = "string", value="SemiAnnual"),
		sp.NameTypeValue(name="ObservationFrequency", type = "string", value="Daily"),
        sp.NameTypeValue(name="IndexTenor", type = "string", value="6M"),
        sp.NameTypeValue(name="IndexRate", type = "string", value="Libor(Underlying,PeriodStart(),IndexTenor)"),
        sp.NameTypeValue(name="UpperBound", type = "string", value="2.75%"),
        sp.NameTypeValue(name="LowerBound", type = "string", value="0.25%"),
        sp.NameTypeValue(name="Coupon", type = "string", value="3.428%"),
        sp.NameTypeValue(name="DayCount", type = "string", value="30/360"),
        
    ],
    payoff_description = [
			[
				"Schedule type",
				"Schedule description",
				"RangeAccrualLeg",
                "Reinitialisation",
				"Price",
				"PricePercent"
			],
			[
				"AllTheTime",
				"FromTo(DateTable(StartDate,EndDate,Frequency),ObservationFrequency)",
				"$n1 = if(abs(IndexRate)>LowerBound and IndexRate<UpperBound, $n1+1, $n1); $n2 =$n2+1",
				"",
				"",
                ""
			],
            [
				"OnSchedule PeriodEnd",
				"DateTable(StartDate, EndDate, Frequency, Daycount)",
				"Coupon*$n1/$n2*InterestTerm()*Notional",
				"$n1 = 0; $n2 = 0",
				"Coupon*$n1/$n2*InterestTerm()*Notional",
                "Coupon*$n1/$n2*InterestTerm()*100"
			],
            [
				"AtDate",
				"EndDate",
				"",
				"",
				"Notional",
				"100"
			]
		]
)
print("	Instrument definition configured")

# 2. Create SP instrument definition object
print("Step 2: Creating instrument definition object...")
range_accrual = sp.StructuredProductsDefinitionInstrument(definition = range_accrual_definition)
print("	Instrument definition created")

# 3. Create SP parameters object - optional
print("Step 3: Configuring pricing parameters...")

range_accrual_pricing_params = sp.StructuredProductsPricingParameters(
    valuation_date= dt.date(2025, 9, 12),  # Set your desired valuation date
    numerical_method = sp.GenericNumericalMethod(method="MonteCarlo"),
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
        definitions=[range_accrual],
        pricing_preferences=range_accrual_pricing_params,
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
df_range_accrual_valuation = pd.DataFrame(list(valuation.items()), columns=["Field", "Value"])

display(df_range_accrual_valuation)

# Extract Greeks from the response
greeks = response.data.analytics[0].greeks

# Convert the dictionary to a DataFrame
df_greeks = pd.DataFrame(list(greeks.items()), columns=["Greeks", "Value"])

display(df_greeks)