"""
TC26 HoT: Analytics Extensions & TabPy
Bonus — Prophet Forecast (Wrap-Up Demo)
========================================
Goal: Deploy a Facebook Prophet model to TabPy as a drop-in alternative to
the PyMC model. Prophet handles time series automatically and gives you
yhat, yhat_lower, yhat_upper out of the box.

This is the "one-liner upgrade" discussed in the wrap-up.

Instructions: Complete each TODO block. Run with:
    python scripts/03_deploy_prophet.py

Reference: solutions/03_deploy_prophet_solution.py
"""

# ── Imports ───────────────────────────────────────────────────────────────────
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import compat_tabpy
from prophet import Prophet
import pandas as pd
import tabpy_client


# =============================================================================
# TODO 1 — Build the Prophet training DataFrame
# =============================================================================
# Prophet requires a DataFrame with exactly two columns:
#   'ds'  → datetime column (use pd.to_datetime([f'{y}-01-01' for y in years]))
#   'y'   → the value to forecast (avg goals per match)
#
# The years and avg_goals_per_match lists are provided below.

years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966,
         1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998,
         2002, 2006, 2010, 2014]

avg_goals_per_match = [3.89, 4.12, 4.67, 4.00, 5.38, 3.60, 2.78, 2.78,
                       2.97, 2.55, 2.68, 2.81, 2.54, 2.21, 2.71, 2.67,
                       2.52, 2.30, 2.27, 2.67]

# YOUR CODE HERE ↓
df = None  # replace with your Prophet DataFrame


# =============================================================================
# TODO 2 — Instantiate and fit the Prophet model
# =============================================================================
# Use interval_width=0.80 to get an 80% credible interval.
# Set yearly_seasonality=False (the data is every 4 years, not yearly).
# Fit the model on `df`.

# YOUR CODE HERE ↓
prophet_model = None  # Prophet(...)


# =============================================================================
# TODO 3 — Define the prophet_forecast function
# =============================================================================
# The function accepts a list of year values (integers or floats).
# Inside the function:
#   1. Build a future DataFrame with column 'ds' from the input years
#   2. Call prophet_model.predict(future)
#   3. Return forecast['yhat'].tolist()
#
# Note: As always with TabPy deployments, capture prophet_model via a default
# argument so it's available when the function runs on the server.

def prophet_forecast(years, _model=prophet_model):
    # YOUR CODE HERE ↓
    pass


# =============================================================================
# TODO 4 — Deploy to TabPy
# =============================================================================
# Connect to http://localhost:9004/ and deploy `prophet_forecast` with:
#   name:        'prophet_forecast'
#   description: 'Prophet Bayesian forecast of avg goals/match'
#   override=True

# YOUR CODE HERE ↓


# =============================================================================
# Discussion: Why Prophet?
# =============================================================================
# Prophet is ideal when you want:
#   ✅ Built-in seasonality decomposition
#   ✅ Automatic changepoint detection
#   ✅ yhat_lower / yhat_upper for free
#   ✅ Minimal configuration
#
# For World Cup data it's overkill (only 20 points, no weekly seasonality)
# but for sales forecasting, pipeline trends, or daily metrics it shines.
#
# Next step: try deploying yhat_lower and yhat_upper as separate functions
# and build the full band chart in Tableau — same as the PyMC exercise!
