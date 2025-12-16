import pandas as pd
import json
from lseg_analytics.pricing.templates.instrument_templates import search, load 
from lseg_analytics.pricing.instruments.ir_swaps import load, Rate, UnitEnum
from lseg_analytics.pricing.instruments.ir_swaps import value, IrPricingParameters, IrSwapDefinitionInstrument
from lseg_analytics.pricing.instruments.ir_swaps import solve, IrPricingParameters, IrSwapSolvingParameters, IrSwapSolvingTarget, IrSwapSolvingVariable, IrMeasure, IrSwapDefinitionInstrument
from lseg_analytics.pricing.instruments.ir_swaps import create_from_ccs_template, CrossCurencySwapOverride
from lseg_analytics.pricing.common import PaidLegEnum, ReferenceDate, RelativeAdjustableDate
from datetime import date
from IPython.display import display
import matplotlib.pyplot as plt

def extract_tag_key(tag):
    return tag.split(":")[0] if ":" in tag else tag

def list_unique_tags(all_swaps):
    unique_tags = set()
    for item in all_swaps:
        tags = item.get("description", {}).get("tags", [])
        for tag in tags:
            key = extract_tag_key(tag)
            unique_tags.add(key)
    return unique_tags

def display_templates(templates):
    unique_tag_keys = list(list_unique_tags(templates))

    rows = []
    for item in templates:
        row = {
            "Space": item.get("location", {}).get("space", ""),
            "Id": item.get("id", ""),
            "Name": item.get("location", {}).get("name", ""),
            "Summary": item.get("description", {}).get("summary", ""),
        }
        tags = item.get("description", {}).get("tags", [])
        tag_dict = {extract_tag_key(tag): tag for tag in tags}
        for key in unique_tag_keys:
            tag_val = tag_dict.get(key, None)
            if tag_val is not None and ":" in tag_val:
                row[key] = tag_val.split(":", 1)[1]
            else:
                row[key] = tag_val
        rows.append(row)

    display(pd.DataFrame(rows))

def build_legs_comparison_df(first_leg, second_leg):
    """Builds a DataFrame comparing key fields of first_leg and second_leg."""
    def get_nested_attr(obj, attrs, default=None):
        for attr in attrs:
            obj = getattr(obj, attr, None)
            if obj is None:
                return default
        return obj

    rows = [
        {
            "Field": "description",
            "First Leg": get_nested_attr(first_leg, ["description", "leg_description"]),
            "Second Leg": get_nested_attr(second_leg, ["description", "leg_description"]),
        },
        {
            "Field": "market value",
            "First Leg": get_nested_attr(first_leg, ["valuation", "market_value", "deal_currency", "value"]),
            "Second Leg": get_nested_attr(second_leg, ["valuation", "market_value", "deal_currency", "value"]),
        },
        {
            "Field": "DV01",
            "First Leg": get_nested_attr(first_leg, ["risk", "dv01", "value"]),
            "Second Leg": get_nested_attr(second_leg, ["risk", "dv01", "value"]),
        },
    ]

    display(pd.DataFrame(rows))

#search function to find NDCCS templates
ndccs_templates = search(
    item_per_page= 5,
    tags=["instrumentType:CrossCurrencySwap","isNonDeliverable:true"],
    spaces=["LSEG"])

display_templates(ndccs_templates)

swap_template = [item["location"]["name"] for item in ndccs_templates if any("SOFR" in tag for tag in item["description"]["tags"])][0]

print(swap_template)

# define a spot starting NDCCS
start_date = RelativeAdjustableDate(tenor = "0D", reference_date= ReferenceDate.VALUATION_DATE)

# setup a 2Y swap maturity from the start date
end_date = RelativeAdjustableDate(tenor = "2Y", reference_date= ReferenceDate.START_DATE)

# override the NDCCS template with a 10M notional on first leg, 1.409M notional on the second leg, the previous start_date and end_date, and a 0bp spread on the float leg
par_overrides = CrossCurencySwapOverride(
    start_date = start_date,
    end_date=end_date,
    amount=10000000,
    contra_amount=1409000,
    spread = Rate(value=0.0, unit = UnitEnum.BASIS_POINT),
    paid_leg= PaidLegEnum.FIRST_LEG)

# build the swap from selected template and previously defined overrides
fwd_start_ccs = create_from_ccs_template(template_reference = swap_template, overrides = par_overrides)

fwd_start_ccs_def = IrSwapDefinitionInstrument(definition = fwd_start_ccs.definition)

print(json.dumps(fwd_start_ccs.definition.as_dict(), indent=4))

# As expected on NDCCS, you should see:
#  - on both legs the properties 'initialPrincipalExchange': 'false', and 'finalPrincipalExchange': 'true'
#  - settlement is set to USD on both legs
# For NDIRS pricing you set 'finalPrincipalExchange' to 'false'

# define solving parameters in order to compute the par fixed rate
solving_params = IrSwapSolvingParameters(
    target=IrSwapSolvingTarget(market_value=IrMeasure(value=0.0)),
    variable= IrSwapSolvingVariable(leg = "FirstLeg", name = "FixedRate"))

# define a solving date
solving_date = date(2025, 11, 13)

# solve the swap fixed rate
valuation_response = solve(
    definitions=[fwd_start_ccs_def],
    pricing_preferences= IrPricingParameters(
        solving_parameters = solving_params,
        valuation_date=solving_date
    ),
    return_market_data=True
)

# print the solved spread
solved_rate = valuation_response.analytics[0].solving.result

print(
    "\t Solved fixed rate, in %:", solved_rate,
)

build_legs_comparison_df(valuation_response.analytics[0].first_leg, valuation_response.analytics[0].second_leg)

print(json.dumps(valuation_response.as_dict(), indent=4))

# Create figure
fig, ax = plt.subplots(figsize=(12, 6))

for ir_curve in valuation_response.market_data.ir_curves:
    dates = [point.date for point in ir_curve.curve.points]
    rates = [point.value for point in ir_curve.curve.points]
    
    ax.plot(dates, rates, marker='o', label=ir_curve.curve.index_reference)

ax.set_xlabel('Date')
ax.set_ylabel('Rate (%)')
ax.set_title('IR Curves')
ax.legend()
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()