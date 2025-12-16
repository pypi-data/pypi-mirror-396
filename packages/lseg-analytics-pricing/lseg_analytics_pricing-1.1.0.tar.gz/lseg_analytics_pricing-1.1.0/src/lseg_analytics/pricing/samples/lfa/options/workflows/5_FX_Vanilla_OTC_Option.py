from lseg_analytics.pricing.instruments.options import (
    value,
    OptionDefinition,
    OptionDefinitionInstrument,
    OptionPricingParameters,
    UnderlyingDefinition,
    ExerciseDefinition,
    ScheduleDefinition
)

from lseg_analytics.pricing.common import AdjustableDate
from datetime import date
import json as js

definition = OptionDefinition(
    underlying = UnderlyingDefinition(
        code="EURAUD",
        underlying_type="Fx"
    ),
    exercise = ExerciseDefinition(
        strike=1,
        exercise_style="American",
        schedule = ScheduleDefinition(
            end_date = AdjustableDate(
                date = date(2025, 3, 18)
            )
        )
    ),
    option_type="Put",
    notional_amount={
        "value": -1000000,
        "currency": "AUD"
    }
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

print(js.dumps(valuation.as_dict(), indent=4))