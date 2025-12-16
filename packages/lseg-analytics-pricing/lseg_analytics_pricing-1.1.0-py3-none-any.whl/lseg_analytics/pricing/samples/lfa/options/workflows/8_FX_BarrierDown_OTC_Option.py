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
import json as js

definition = OptionDefinition(
    underlying = UnderlyingDefinition(
        code="EURUSD",
        underlying_type="Fx"
    ),
    exercise= ExerciseDefinition(
        strike=1.01,
        schedule = ScheduleDefinition(
            end_date = AdjustableDate(
                date = date(2025, 3, 18)
            )
        )
    ),
    barrier_down= BarrierDefinition(
        barrier_mode="European",
        level=1.2,
        in_or_out="In"
    ),
    option_type="Call",
    notional_amount={
        "value": 1000000,
        "currency": "EUR"
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