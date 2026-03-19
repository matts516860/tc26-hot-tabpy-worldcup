"""
TC26 HoT: Analytics Extensions & TabPy
Capstone — 2026 World Cup Goal Prediction
==========================================
Run with:
    python PythonScripts/04_deploy_2026_prediction.py

The 2026 World Cup introduces a format the model has never seen:
  - 48 teams (up from 32)
  - 104 matches (up from 64)
  - A brand-new Round of 32 stage with no historical equivalent

This script:
  1. Retrains the regression model on the same 1930–2014 data
  2. Maps the new Round of 32 to 'Round of 16' (closest historical analogue)
  3. Predicts avg goals/match and total goals for every round of the 2026 tournament
  4. Exports data/2026_match_schedule.xlsx — connect this directly to Tableau
  5. Deploys predict_2026_goals to TabPy for live SCRIPT_REAL() queries

Tableau calculated field (after running this script):
  SCRIPT_REAL(
    "return tabpy.query('predict_2026_goals', _arg1, _arg2)['response']",
    AVG([Year]),
    ATTR([Round])
  )
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


# ── Training data (same as 01_deploy_regression_solution.py) ─────────────────
# One row per World Cup, 1930–2014.
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

le = LabelEncoder()
df['Round_Encoded'] = le.fit_transform(df['Round_Type'])

X = df[['Year', 'Round_Encoded']]
y = df['AvgGoals']

model = LinearRegression()
model.fit(X, y)

print(f"Model trained — R²: {model.score(X, y):.4f}")
print(f"Year coefficient: {model.coef_[0]:.6f}  (negative = goals declining over time)")
print(f"Known rounds: {list(le.classes_)}")


# ── 2026 World Cup format ──────────────────────────────────────────────────────
# 48 teams, 16 groups of 3 → 48 group-stage matches, then single-elimination.
# The Round of 32 is entirely new — no historical data. We map it to Round of 16
# as the closest analogue (same knockout pressure, similar match count era).

ROUND_MAPPING_2026 = {
    'Group Stage':    'Group',           # map to training label
    'Round of 32':    'Round of 16',     # NEW in 2026 — no historical equivalent
    'Round of 16':    'Round of 16',
    'Quarter-finals': 'Quarter-finals',
    'Semi-finals':    'Semi-finals',
    'Third Place':    'Semi-finals',     # closest structural analogue
    'Final':          'Final',
}

SCHEDULE_2026 = [
    {'Round': 'Group Stage',    'Matches': 48},   # 16 groups × 3 matches
    {'Round': 'Round of 32',    'Matches': 16},   # 32 qualifiers → 16 winners
    {'Round': 'Round of 16',    'Matches':  8},
    {'Round': 'Quarter-finals', 'Matches':  4},
    {'Round': 'Semi-finals',    'Matches':  2},
    {'Round': 'Third Place',    'Matches':  1},
    {'Round': 'Final',          'Matches':  1},
]
# Total: 80 matches  (2014 had 64)


# ── Generate predictions ───────────────────────────────────────────────────────
rows = []
for item in SCHEDULE_2026:
    round_name   = item['Round']
    mapped_round = ROUND_MAPPING_2026[round_name]
    encoded      = le.transform([mapped_round])[0]
    features     = pd.DataFrame({
        'Year': [2026],
        'Round_Encoded': [encoded],
    })
    pred_avg     = float(model.predict(features)[0])

    rows.append({
        'Year':                  2026,
        'Round':                 round_name,
        'Mapped_To_Training':    mapped_round,
        'Matches':               item['Matches'],
        'Predicted_Avg_Goals':   round(pred_avg, 3),
        'Predicted_Total_Goals': round(pred_avg * item['Matches'], 1),
        'Note': '⚠ No historical data — mapped to Round of 16'
                if round_name == 'Round of 32' else '',
    })

df_2026 = pd.DataFrame(rows)

print("\n── 2026 Predictions ─────────────────────────────────────────────────────")
print(df_2026[['Round', 'Matches', 'Predicted_Avg_Goals',
               'Predicted_Total_Goals']].to_string(index=False))

total_predicted = df_2026['Predicted_Total_Goals'].sum()
print(f"\nPredicted total goals for 2026 tournament: {total_predicted:.0f}")
print(f"  Actual 2014 total: 171  (64 matches)")
print(f"  Actual 1990 total: 115  (52 matches) — lowest avg ever: 2.21/match")
print(f"  2026 has 80 matches — tournament scale has changed dramatically.")
print()

# Key talking point for discussion
avg_2026 = total_predicted / df_2026['Matches'].sum()
print(f"Predicted avg goals/match across all 2026 rounds: {avg_2026:.2f}")
print("  → The negative Year coefficient pushes this below any historical WC.")
print("  → Discussion: Is that realistic? What feature is this model missing?")
print("     (Hint: 48-team expansion means more mismatches in the group stage.)")


# ── Export to Excel for direct Tableau connection ─────────────────────────────
# Sheet 1: 2026 predictions  (connect this to Tableau)
# Sheet 2: Historical data   (for comparison in a blended or dual-axis viz)

df_historical = pd.DataFrame({
    'Year':     data['Year'],
    'Round':    data['Round_Type'],
    'AvgGoals': data['AvgGoals'],
    'Matches':  [18,17,18,22,26,35,32,32,32,38,38,52,52,52,52,64,64,64,64,64],
})
df_historical['TotalGoals'] = (
    df_historical['AvgGoals'] * df_historical['Matches']
).round(0)

output_path = Path(__file__).resolve().parent.parent / 'data' / '2026_match_schedule.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_2026.to_excel(writer, sheet_name='2026_Predictions', index=False)
    df_historical.to_excel(writer, sheet_name='Historical_Actuals', index=False)

print(f"\n✅  Exported: data/2026_match_schedule.xlsx")
print(f"     Sheet 1 — 2026_Predictions   ({len(df_2026)} rounds)")
print(f"     Sheet 2 — Historical_Actuals ({len(df_historical)} tournaments)")


# ── Deploy to TabPy ────────────────────────────────────────────────────────────
def predict_2026_goals(years, rounds):
    """
    Predicts average total goals for a World Cup match.
    Extends predict_total_goals to handle the new 2026 'Round of 32'.

    Tableau calculated field:
      SCRIPT_REAL(
        "return tabpy.query('predict_2026_goals', _arg1, _arg2)['response']",
        AVG([Year]),
        ATTR([Round])
      )

    Parameters
    ----------
    years  : list of float — the year for each row (e.g. [2026, 2026, ...])
    rounds : list of str   — the round name (e.g. ['Group Stage', 'Round of 32', ...])

    Returns
    -------
    list of float — predicted avg goals per match
    """
    import pandas as pd

    round_map = {
        'Group Stage':    'Group',
        'Round of 32':    'Round of 16',
        'Round of 16':    'Round of 16',
        'Quarter-finals': 'Quarter-finals',
        'Semi-finals':    'Semi-finals',
        'Third Place':    'Semi-finals',
        'Final':          'Final',
        # Pass-through for original training labels
        'Group':          'Group',
    }

    known_rounds = list(le.classes_)
    encoded = []
    for r in rounds:
        mapped = round_map.get(r, r)          # apply 2026 mapping
        if mapped in known_rounds:
            encoded.append(le.transform([mapped])[0])
        else:
            encoded.append(0)                 # graceful fallback

    features = pd.DataFrame({'Year': years, 'Round_Encoded': encoded})
    return model.predict(features).tolist()


# Sanity check
test = predict_2026_goals(
    [2026, 2026, 2026, 2026, 2026],
    ['Group Stage', 'Round of 32', 'Round of 16', 'Semi-finals', 'Final']
)
print("\nSanity check — 2026 predictions:")
for rnd, pred in zip(['Group Stage', 'Round of 32', 'Round of 16',
                      'Semi-finals', 'Final'], test):
    print(f"  {rnd:20s}: {pred:.3f} goals/match")


print("\nConnecting to TabPy at http://localhost:9004/ ...")
connection = tabpy_client.Client('http://localhost:9004/')

try:
    connection.deploy(
        'predict_2026_goals',
        predict_2026_goals,
        'Predicts avg goals/match for any year+round. Handles 2026 Round of 32 via mapping.',
        override=True
    )
except RuntimeError as exc:
    if 'Waited more then 10s for deployment' not in str(exc):
        raise
    status = requests.get('http://localhost:9004/status', timeout=5).json()
    if status.get('predict_2026_goals', {}).get('status') != 'LoadSuccessful':
        raise
    print("Deployment timed out but endpoint loaded successfully.")

print("✅  predict_2026_goals deployed!")
print("""
Tableau calculated field:
  SCRIPT_REAL(
    "return tabpy.query('predict_2026_goals', _arg1, _arg2)['response']",
    AVG([Year]),
    ATTR([Round])
  )

Tableau visualization steps:
  1. File → New Data Source → data/2026_match_schedule.xlsx
  2. Use the '2026_Predictions' sheet
  3. Drag Round to Columns. Sort manually: Group Stage → Round of 32 →
     Round of 16 → Quarter-finals → Semi-finals → Final
  4. Drag Predicted_Avg_Goals to Rows → bar chart
  5. Drag Predicted_Total_Goals to Label
  6. Add a Reference Line at 2.27 (2010 — the lowest historical avg)
  7. For a comparison view: blend with Historical_Actuals sheet on Year

Discussion prompt:
  The model predicts ~2.1 goals/match — lower than any WC in history.
  Is that realistic? What feature is the model missing?
  (The 48-team expansion means more lopsided group-stage matches,
   which historically INCREASES goals — the opposite of what the
   linear time trend predicts.)
""")
