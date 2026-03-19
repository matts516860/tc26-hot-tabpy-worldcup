"""
TC26 HoT: Analytics Extensions & TabPy
Bonus — Prophet Forecast — SOLUTION
=====================================
Complete, runnable solution. Run with:
    python solutions/03_deploy_prophet_solution.py
"""

from prophet import Prophet
import pandas as pd
import tabpy_client

# ── Training data ─────────────────────────────────────────────────────────────
years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966,
         1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998,
         2002, 2006, 2010, 2014]

avg_goals_per_match = [3.89, 4.12, 4.67, 4.00, 5.38, 3.60, 2.78, 2.78,
                       2.97, 2.55, 2.68, 2.81, 2.54, 2.21, 2.71, 2.67,
                       2.52, 2.30, 2.27, 2.67]

# Prophet requires columns named 'ds' (datetime) and 'y' (target)
df = pd.DataFrame({
    'ds': pd.to_datetime([f'{y}-01-01' for y in years]),
    'y':  avg_goals_per_match
})

print("Training Prophet model...")

# ── Fit Prophet ───────────────────────────────────────────────────────────────
prophet_model = Prophet(
    interval_width=0.80,        # 80% credible interval
    yearly_seasonality=False    # Not applicable — data is every 4 years
)
prophet_model.fit(df)

print("✅  Prophet model trained!")


# ── Deployment function ───────────────────────────────────────────────────────
def prophet_forecast(years, _model=prophet_model):
    """
    Prophet Bayesian forecast of avg goals/match.

    Parameters
    ----------
    years : list of int/float — years to forecast

    Returns
    -------
    list of float — yhat (posterior mean) for each year
    """
    import pandas as pd
    future = pd.DataFrame({
        'ds': pd.to_datetime([f'{int(y)}-01-01' for y in years])
    })
    forecast = _model.predict(future)
    return forecast['yhat'].tolist()


# ── Quick sanity check ────────────────────────────────────────────────────────
test = prophet_forecast([2018, 2022, 2026])
print(f"\nSanity check — Prophet forecast:")
for year, pred in zip([2018, 2022, 2026], test):
    print(f"  {year}: {pred:.3f} avg goals/match")


# ── Deploy to TabPy ───────────────────────────────────────────────────────────
print("\nConnecting to TabPy at http://localhost:9004/ ...")
conn = tabpy_client.Client('http://localhost:9004/')

conn.deploy(
    'prophet_forecast',
    prophet_forecast,
    'Prophet Bayesian forecast of avg goals/match',
    override=True
)

print("✅  Prophet model deployed!")
print("\nTableau calculated field:")
print("""
  Prophet Forecast:
    SCRIPT_REAL("return tabpy.query('prophet_forecast', _arg1)['response']",
    AVG([Year]))
""")
print("Extension challenge: also deploy yhat_lower and yhat_upper for a full band chart!")
