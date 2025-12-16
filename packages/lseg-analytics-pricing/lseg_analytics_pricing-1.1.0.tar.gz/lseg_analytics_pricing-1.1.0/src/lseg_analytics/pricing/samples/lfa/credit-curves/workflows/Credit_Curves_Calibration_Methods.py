from lseg_analytics.pricing.market_data import credit_curves as cc

import pandas as pd
import json
import datetime as dt
from IPython.display import display
import matplotlib.pyplot as plt

print("Step 1: Configuring Curve Definition...")

calibration_mode_base = cc.CalibrationModelEnum.BASIS_SPLINE

curve_definition = cc.CreditCurveDefinition(
    name = "United States GOV Par Benchmark Curve", # combination of Name | Country | Currency | isCurrencyCountryOriginator, see Appendix 2 in 1_CreditCurves_SDK_Fundamentals for the full list
    issuer_type = cc.IssuerTypeEnum.SOVEREIGN,
    country = "US",
    source = cc.RatingScaleSourceEnum.REFINITIV,
    currency = "USD",
    curve_sub_type=cc.CurveSubTypeEnum.GOVERNMENT_BENCHMARK,
    is_currency_country_originator=True
)

print("Step 2: Configuring Curve Parameters...")

curve_parameters = cc.CreditCurveParameters(
    valuation_date = dt.date(2025, 9, 19),
    calibration_model = calibration_mode_base,
    calibration_parameters = cc.CalibrationParameters(
        is_monotonic = False,
        extrapolation_points_number = 4,
        extrapolation_type = cc.ExtrapolationTypeEnum.EXTRAPOLATION_BOTH_DERIVATIVE
    ),
    use_duration_weighted_minimization = True,
    use_multi_dimensional_solver = True,
    calendar_adjustment = cc.CalendarAdjustmentEnum.CALENDAR,
    use_delayed_data_if_denied = False
)

print("Step 3: Create request item...")

credit_curve_request = cc.CreditCurveRequestItem(
    curve_parameters = curve_parameters,
    curve_definition = curve_definition,
    constituents = None
)

print(f"   Request: {json.dumps(credit_curve_request.as_dict(), indent=4)}")

print(f"Calculating Credit Curve with {calibration_mode_base} calibration model...")
# Execute the credit curve calculation using cc.calculate
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response_basis_spline = cc.calculate(universe=[credit_curve_request])
    print("Credit curve calculation completed")
except Exception as e:
    print("Error during credit curve calculation:", str(e))

calibration_mode_compare = cc.CalibrationModelEnum.NELSON_SIEGEL_SVENSSON
print(f"Adjusting Curve Parameters for {calibration_mode_compare} calibration model...")
curve_parameters.calibration_model = calibration_mode_compare

credit_curve_request = cc.CreditCurveRequestItem(
    curve_parameters = curve_parameters,
    curve_definition = curve_definition,
    constituents = None
)

print(f"   Request: {json.dumps(credit_curve_request.as_dict(), indent=4)}")

print(f"Calculating Credit Curve with {calibration_mode_compare} calibration model...")
# Execute the credit curve calculation using cc.calculate
# The 'universe' parameter accepts a list of request items for batch processing
try:
    response_nelson_siegel = cc.calculate(universe=[credit_curve_request])
    print("Credit curve calculation completed")
except Exception as e:
    print("Error during credit curve calculation:", str(e))

# Format data and join the two curve DataFrames on 'Tenor' and calculate the difference in RatePercent

def curve_response_to_df(response):
    # Load JSON response
    response_json = json.loads(json.dumps(response.as_dict()))
    name = response_json["data"][0]["curveDefinition"]["name"]
    valuation_date = dt.datetime.strptime(response_json["data"][0]["curveParameters"]['valuationDate'], '%Y-%m-%d').date()

    # Collecting results to DataFrame
    curve_points = response_json["data"][0]["curvePoints"]
    rate_vs_tenor = [(point["tenor"], point["ratePercent"]) for point in curve_points]
    return pd.DataFrame(rate_vs_tenor, columns=["Tenor", "RatePercent"]), name, valuation_date

rate_vs_tenor_df_base, name, valuation_date = curve_response_to_df(response_basis_spline)
rate_vs_tenor_df_compare, _, _ = curve_response_to_df(response_nelson_siegel)

rate_vs_tenor_df_base['RatePercent'] = rate_vs_tenor_df_base['RatePercent'].round(2)
rate_vs_tenor_df_compare['RatePercent'] = rate_vs_tenor_df_compare['RatePercent'].round(2)
joined_df = pd.merge(
    rate_vs_tenor_df_base,
    rate_vs_tenor_df_compare,
    on='Tenor',
    suffixes=(f'_{calibration_mode_base}', f'_{calibration_mode_compare}')
)

# Computing the RMSE and Mean Error between basis_spline and nelson_siegel_svensson calibration methods

col_name_base = f'RatePercent_{calibration_mode_base}'
col_name_compare = f'RatePercent_{calibration_mode_compare}'
joined_df['RatePercent_Diff'] = (joined_df[col_name_base] - joined_df[col_name_compare]).round(2)

rmse = ((joined_df[col_name_base] - joined_df[col_name_compare])**2).mean() ** 0.5
mean_error = (joined_df[col_name_base] - joined_df[col_name_compare]).mean()
print(f"Root Mean Squared Rate Error (RMSE) between {calibration_mode_base} and {calibration_mode_compare}: {round(100*rmse)} bp")
print(f"Mean Error between {calibration_mode_base} and {calibration_mode_compare}: {round(100*mean_error)} bp")

# Display results to compare basis_spline and nelson_siegel_svensson calibration methods

display(joined_df)

valuation_date_str = valuation_date.strftime('%d %b %Y')
plt.figure(figsize=(8,5))
plt.plot(rate_vs_tenor_df_base['Tenor'], rate_vs_tenor_df_base['RatePercent'], marker='o', label=f'{calibration_mode_base}')
plt.plot(rate_vs_tenor_df_compare['Tenor'], rate_vs_tenor_df_compare['RatePercent'], marker='x', label=f'{calibration_mode_compare}')
plt.title(f"{name} - Calibration Comparison, as of {valuation_date_str}")
plt.xlabel('Tenor')
plt.ylabel('Rate Percent')
plt.grid(True)
plt.legend()
plt.show()