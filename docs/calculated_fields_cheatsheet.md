# Tableau Calculated Fields — Quick Reference

*TC26 HoT: Analytics Extensions & TabPy — World Cup Exercise*

---

## Part 3 Calculated Fields

### 1. Total Goals (Actual)

```
[HomeGoals] + [AwayGoals]
```

**Purpose:** Ground truth — the actual number of goals scored in each match.
**Data type:** Integer
**Where to use:** Rows shelf (dual axis with Predicted Total Goals)

---

### 2. Predicted Total Goals

```
SCRIPT_REAL(
  "return tabpy.query('predict_total_goals', _arg1, _arg2)['response']",
  AVG([Year]),
  ATTR([Round])
)
```

**Purpose:** Calls the scikit-learn regression model deployed to TabPy.
**Data type:** Float
**Arguments:**
- `_arg1` → `AVG([Year])` — the tournament year
- `_arg2` → `ATTR([Round])` — the round type (Group, Final, Semi-finals, etc.)

> **Tip:** If you see `null` values, check that the TabPy server is running and `predict_total_goals` is deployed. Open the TabPy terminal for error output.

> **Tip:** If `ATTR([Round])` returns `*` (asterisk), add the `Round` field to the **Detail** shelf to ensure each mark has exactly one Round value.

---

## Part 4 Calculated Fields (Bayesian Extension)

### 3. Posterior Mean

```
SCRIPT_REAL(
  "return tabpy.query('bayesian_goals_forecast', _arg1)['response']",
  AVG([Year])
)
```

**Purpose:** The Bayesian model's best-guess prediction for avg goals/match in a given year.
**Data type:** Float
**Note:** This is the center line of the band chart.

---

### 4. Upper Credible Interval (90th pct)

```
SCRIPT_REAL(
  "return tabpy.query('bayesian_goals_upper', _arg1)['response']",
  AVG([Year])
)
```

**Purpose:** Upper boundary of the 80% credible interval band.
**Data type:** Float
**Note:** Values above this line have only a 10% probability under the posterior.

---

### 5. Lower Credible Interval (10th pct)

```
SCRIPT_REAL(
  "return tabpy.query('bayesian_goals_lower', _arg1)['response']",
  AVG([Year])
)
```

**Purpose:** Lower boundary of the 80% credible interval band.
**Data type:** Float
**Note:** Values below this line have only a 10% probability under the posterior.

---

## Bonus: Prophet Forecast

### 6. Prophet Forecast

```
SCRIPT_REAL(
  "return tabpy.query('prophet_forecast', _arg1)['response']",
  AVG([Year])
)
```

**Purpose:** Facebook Prophet's posterior mean forecast for avg goals/match.
**Data type:** Float
**Note:** Requires `03_deploy_prophet.py` to have been run successfully.

---

## How SCRIPT_REAL() Works

```
SCRIPT_REAL( <python_expression_string>, [field1], [field2], ... )
                      ↑                       ↑
             Python code to evaluate    Tableau fields passed as
             Runs on TabPy server       _arg1, _arg2, _arg3 ...
             Must return a float list
```

**Important rules:**
- The Python string calls `tabpy.query('<function_name>', ...)` — matches the name you used when deploying
- `['response']` extracts the return value from TabPy's response envelope
- Fields are aggregated before being sent — always wrap in `AVG()`, `ATTR()`, `MIN()`, etc.
- The returned list must have the same length as the number of marks in your viz

---

## Other SCRIPT_ Functions

| Function | Return Type | Use Case |
|----------|-------------|----------|
| `SCRIPT_REAL(...)` | Float | Regression predictions, scores, probabilities |
| `SCRIPT_INT(...)` | Integer | Cluster IDs, category codes, counts |
| `SCRIPT_STR(...)` | String | Text classification labels, NLP outputs |
| `SCRIPT_BOOL(...)` | Boolean | Anomaly flags, binary classifiers |

All four follow the same syntax — only the return type differs.

---

## Table Calculation Settings

SCRIPT_ functions are **table calculations** — they compute across marks in your viz, not at the database level.

When building the viz, ensure your table calculation is set to compute by the right dimension:
- **Compute using:** `Year` (for the time series charts in this session)
- Access this by right-clicking the calculated field pill → **Edit Table Calculation**

---

*Keep this file open during the session for quick copy/paste access.*
