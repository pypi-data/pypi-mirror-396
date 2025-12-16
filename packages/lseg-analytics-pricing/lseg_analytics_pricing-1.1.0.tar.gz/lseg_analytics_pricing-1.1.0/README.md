# LSEG Analytics SDK for Python

The LSEG Analytics SDK for Python provides access to LSEG Financials Analytics Services.

## Getting Started

```shell
$ pip install lseg-analytics-pricing
```

### Migrating from Previous Package Names

**Important:** This package was previously named  `lseg-analytics`. If you have old package installed, please uninstall it first to avoid conflicts:

```shell
# Remove old packages (if installed)
$ pip uninstall lseg-analytics -y

# Install the new package
$ pip install lseg-analytics-pricing
```

Or in a single command:

```shell
$ pip uninstall lseg-analytics -y && pip install lseg-analytics-pricing
```

**What changed:**
- Package name: `lseg-analytics` → `lseg-analytics-pricing`
- Import path: `from lseg_analytics import ...` → `from lseg_analytics.pricing import ...`
- All functionality and APIs remain compatible


## Usage Examples

An example to create a FX Forward Curve.

```python
from lseg_analytics.pricing.common import (
    TenorType
)

from lseg_analytics.pricing.market_data.fx_forward_curves import (
    create_from_fx_forwards,
    IndirectSourcesSwaps
)

create_from_fx_forwards(
            cross_currency="EURGBP",
            reference_currency="USD",
            sources=IndirectSourcesSwaps(base_fx_forwards="RFB"),
            additional_tenor_types=[TenorType.LONG, TenorType.END_OF_MONTH],
)
```

## Modules Structure

- `common` - contains models that can be used in different API modules
- `helpers` - utility functions
- API modules
  - `reference_data`
    - `calendars`
    - `floating_rate_indices`
  - `market_data`
    - `fx_forward_curves`
    - `commodities_curves`
    - `credit_curves`
    - `eq_volatility`
    - `fx_volatility`
    - `inflation_curves`
    - `interest_rate_curves`
    - `ipa_interest_rate_curves`
    - `ircaplet_volatility`
    - `irswaption_volatility`
  - `instruments`
    - `fx_spots`
    - `fx_forwards`
    - `bond`
    - `bond_future`
    - `cap_floor`
    - `cds`
    - `forward_rate_agreement`
    - `ir_swaps`
    - `loans`
    - `options`
    - `repo`
    - `structured_products`
    - `swaption`
    - `term_deposit`
  - `templates`
    - `instrument_templates`
  - `yield_book_rest`
