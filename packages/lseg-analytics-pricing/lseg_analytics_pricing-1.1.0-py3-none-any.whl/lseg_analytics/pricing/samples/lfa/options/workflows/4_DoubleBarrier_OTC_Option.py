from lseg_analytics.pricing.instruments.options import (
    value,
    OptionDefinition,
    OptionDefinitionInstrument,
    OptionPricingParameters,
    UnderlyingDefinition,
    ExerciseDefinition,
    ScheduleDefinition,
    BarrierDefinition
)

from lseg_analytics.pricing.common import AdjustableDate
from datetime import date
import pandas as pd
import json as js

definition = OptionDefinition(
    underlying = UnderlyingDefinition(
        code="ASML.AS",
        underlying_type="Equity"
    ),
    exercise = ExerciseDefinition(
        strike=240,
        exercise_style="European",
        schedule = ScheduleDefinition(
            end_date = AdjustableDate(
                date = date(2025, 8, 13)
            )
        )
    ),
    barrier_up= BarrierDefinition(
        barrier_mode="European",
        level=250,
        in_or_out="Out"
    ),
    barrier_down= BarrierDefinition(
        barrier_mode="European",
        level=220,
        in_or_out="Out"
    ),
    option_type="Call"
)

pricing_parameters=OptionPricingParameters(
    valuation_date=date(2024, 12, 18)
)

response = value(
    definitions=[OptionDefinitionInstrument(definition=definition)],
    pricing_preferences=pricing_parameters
)

print(js.dumps(response.as_dict(), indent=4))

valuation = response.analytics[0].valuation

import pandas as pd

def flatten(data):
    rows = []

    for key, section in data.items():
        row = {"metric": key}

        # Start with raw values
        value = section.get("value")
        unit = section.get("unit")
        percent = section.get("percent")

        # Handle dealCurrency override
        dc = section.get("dealCurrency")
        if dc is not None:
            value = getattr(dc, "value", value)
            unit = getattr(dc, "currency", unit)

        # Round and assign
        if value is not None:
            row["value"] = round(value, 3)
        if unit is not None:
            row["unit"] = unit
        if percent is not None:
            row["percent"] = round(percent, 3)

        rows.append(row)

    return pd.DataFrame(rows).set_index("metric")

flatten(valuation)