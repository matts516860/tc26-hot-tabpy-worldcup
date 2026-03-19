"""
TC26 HoT: Analytics Extensions & TabPy
Part 2 — Scikit-learn Regression Model — SOLUTION
==================================================
Complete, runnable solution. Run with:
    python PythonScripts/01_deploy_regression_solution.py
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import compat_tabpy
import tabpy_client
import pandas as pd
import numpy as np
import requests
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

# ── Training data (tournament-level averages, 1930–2014) ─────────────────────
data = {
    'Year': [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974,
             1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014],
    'Round_Type': [
        'Group', 'Group', 'Group', 'Group', 'Final',
        'Semi-finals', 'Quarter-finals', 'Group', 'Final', 'Group',
        'Semi-finals', 'Quarter-finals', 'Group', 'Final', 'Group',
        'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final', 'Group'
    ],
    'AvgGoals': [3.89, 4.12, 4.67, 4.00, 5.38, 3.60, 2.78, 2.78, 2.97, 2.55,
                 2.68, 2.81, 2.54, 2.21, 2.71, 2.67, 2.52, 2.30, 2.27, 2.67]
}

df = pd.DataFrame(data)

# ── Label-encode round types ──────────────────────────────────────────────────
le = LabelEncoder()
df['Round_Encoded'] = le.fit_transform(df['Round_Type'])

print("Label encoder classes:", list(le.classes_))

# ── Train the regression model ────────────────────────────────────────────────
X = df[['Year', 'Round_Encoded']]
y = df['AvgGoals']

model = LinearRegression()
model.fit(X, y)

print(f"Model trained — R²: {model.score(X, y):.4f}")
print(f"Coefficients: Year={model.coef_[0]:.6f}, Round={model.coef_[1]:.4f}")
print(f"Intercept: {model.intercept_:.4f}")


# ── Prediction function (deployed to TabPy) ───────────────────────────────────
def predict_total_goals(years, rounds):
    """
    Predicts average total goals for a World Cup match.

    Parameters
    ----------
    years  : list of float  — the year for each row (e.g. [2014, 2014, ...])
    rounds : list of str    — the round name for each row (e.g. ['Group', 'Final', ...])

    Returns
    -------
    list of float — predicted avg goals per match
    """
    import pandas as pd

    known_rounds = list(le.classes_)
    encoded = []
    for r in rounds:
        if r in known_rounds:
            encoded.append(le.transform([r])[0])
        else:
            # Unknown round type → default to 0 (graceful degradation)
            encoded.append(0)

    features = pd.DataFrame({
        'Year': years,
        'Round_Encoded': encoded,
    })
    return model.predict(features).tolist()


# ── Quick sanity check before deploying ──────────────────────────────────────
test_result = predict_total_goals([2026, 2026], ['Final', 'Group'])
print(f"\nSanity check — 2026 Final: {test_result[0]:.3f}, 2026 Group: {test_result[1]:.3f}")


# ── Deploy to TabPy ───────────────────────────────────────────────────────────
print("\nConnecting to TabPy at http://localhost:9004/ ...")
connection = tabpy_client.Client('http://localhost:9004/')

try:
    connection.deploy(
        'predict_total_goals',
        predict_total_goals,
        'Predicts average total goals for a match given Year and Round type',
        override=True
    )
except RuntimeError as exc:
    if "Waited more then 10s for deployment" not in str(exc):
        raise

    status = requests.get('http://localhost:9004/status', timeout=5).json()
    endpoint_status = status.get('predict_total_goals', {})
    if endpoint_status.get('status') != 'LoadSuccessful':
        raise

    print("Deployment timed out waiting for TabPy, but the endpoint loaded successfully.")

print("✅  Model deployed successfully!")
print("\nNow go to Tableau and create the calculated field:")
print("""
  SCRIPT_REAL(
    "return tabpy.query('predict_total_goals', _arg1, _arg2)['response']",
    AVG([Year]),
    ATTR([Round])
  )
""")
