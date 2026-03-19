"""
TC26 HoT: Analytics Extensions & TabPy
Part 2 — Scikit-learn Regression Model (7 min)
===============================================
Goal: Train a LinearRegression model on historical World Cup data and deploy
it to TabPy so Tableau can call it via SCRIPT_REAL().

The model predicts average total goals scored in a match based on:
  - Year       (continuous)
  - Round type (categorical → label-encoded)

Instructions: Complete each TODO block in order. Run the script with:
    python scripts/01_deploy_regression.py

Reference: solutions/01_deploy_regression_solution.py
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import tabpy_client
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder


# =============================================================================
# TODO 1 — Build the training DataFrame
# =============================================================================
# The data below is derived from WorldCupMatches (tournament-level averages).
# Create a pandas DataFrame called `df` with three columns:
#   'Year'       → the list of years below
#   'Round_Type' → the list of round labels below
#   'AvgGoals'   → the list of average goals below
#
# Hint: pd.DataFrame({'col': [...]})

years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974,
         1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014]

round_types = [
    'Group', 'Group', 'Group', 'Group', 'Final',
    'Semi-finals', 'Quarter-finals', 'Group', 'Final', 'Group',
    'Semi-finals', 'Quarter-finals', 'Group', 'Final', 'Group',
    'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final', 'Group'
]

avg_goals = [3.89, 4.12, 4.67, 4.00, 5.38, 3.60, 2.78, 2.78, 2.97, 2.55,
             2.68, 2.81, 2.54, 2.21, 2.71, 2.67, 2.52, 2.30, 2.27, 2.67]

# YOUR CODE HERE ↓
df = None  # replace with your DataFrame


# =============================================================================
# TODO 2 — Label-encode the Round_Type column
# =============================================================================
# sklearn's LinearRegression requires numeric inputs.
# Use LabelEncoder to convert 'Round_Type' strings to integers.
# Store the fitted encoder in `le` and save encoded values as a new column
# called 'Round_Encoded' in the DataFrame.
#
# Hint: le = LabelEncoder()
#       df['Round_Encoded'] = le.fit_transform(df['Round_Type'])

le = LabelEncoder()
# YOUR CODE HERE ↓


# =============================================================================
# TODO 3 — Define features (X) and target (y), then train the model
# =============================================================================
# X should be a DataFrame with columns ['Year', 'Round_Encoded']
# y should be the 'AvgGoals' column
# Train a LinearRegression model and fit it to X, y.

model = LinearRegression()
# YOUR CODE HERE ↓
X = None
y = None


# =============================================================================
# TODO 4 — Define the prediction function
# =============================================================================
# Write a function called `predict_total_goals(years, rounds)` that:
#   1. Accepts two lists: a list of year values and a list of round-type strings
#   2. Encodes the round strings using `le` (handle unknown values gracefully
#      by defaulting to 0 if the round isn't in le.classes_)
#   3. Stacks years and encoded rounds into a feature matrix
#   4. Returns model.predict(...).tolist()
#
# IMPORTANT: The function must import numpy inside the function body.
# TabPy serializes and deploys the function in isolation — imports at the top
# of this script will NOT be available inside the deployed function.

def predict_total_goals(years, rounds):
    # YOUR CODE HERE ↓
    pass


# =============================================================================
# TODO 5 — Connect to TabPy and deploy the function
# =============================================================================
# Connect to the TabPy server running at http://localhost:9004/
# Deploy `predict_total_goals` with:
#   - name:        'predict_total_goals'
#   - description: 'Predicts average total goals for a match given Year and Round type'
#   - override=True  (so you can re-run without errors)
# Print a confirmation message when done.
#
# Hint: connection = tabpy_client.Client('http://localhost:9004/')
#       connection.deploy(name, func, description, override=True)

# YOUR CODE HERE ↓
