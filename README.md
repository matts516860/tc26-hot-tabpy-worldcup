# TC26 HoT: Analytics Extensions & TabPy — World Cup Exercise

**Tableau Conference 2026 · Hands-On Training Session**
⏱ ~30 minutes · Level: Intermediate

---

## Overview

In this session you will install and configure **TabPy**, deploy a **scikit-learn regression model** trained on historical FIFA World Cup match data, and use Tableau's `SCRIPT_REAL()` function to call it live from a calculated field to **predict total goals scored** in a match.

As a bonus extension, you'll layer in a **Bayesian time series model** using **PyMC** to add uncertainty quantification via credible intervals — surfaced directly in Tableau as a band chart.

---

## Prerequisites

Before the session, please ensure you have:

- [ ] Python 3.9+ installed (`python --version`)
- [ ] Tableau Desktop 2022.1 or newer
- [ ] A text editor or IDE (VS Code recommended)
- [ ] This repository cloned locally

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/matts516860/tc26-hot-tabpy-worldcup.git
cd tc26-hot-tabpy-worldcup

# 2. Install dependencies and apply the TabPy compatibility patch
bash setup.sh

# 3. Start the TabPy server
tabpy

# 4. In a NEW terminal, run the scripts (see Session Flow below)
```

> Use `bash setup.sh` rather than raw `pip install -r requirements.txt`. The setup script also applies a `tabpy-client` compatibility patch required on newer Python versions.

> TabPy starts on **http://localhost:9004** by default. Confirm it's running by opening that URL in a browser — you should see a JSON status response.

---

## Repository Structure

```
tc26-hot-tabpy-worldcup/
├── README.md                          # This file
├── requirements.txt                   # All Python dependencies
├── setup.sh                           # One-command environment setup
│
├── data/
│   └── world_cup_results.xlsx         # Official dataset (3 sheets)
│
├── scripts/                           # ← YOU WORK HERE (guided, with TODOs)
│   ├── 01_deploy_regression.py        # Part 2: scikit-learn goal predictor
│   ├── 02_deploy_bayesian.py          # Part 4: PyMC Bayesian band chart
│   └── 03_deploy_prophet.py           # Bonus: Prophet forecast
│
├── solutions/                         # ← Full working code (solutions branch)
│   ├── 01_deploy_regression_solution.py
│   ├── 02_deploy_bayesian_solution.py
│   └── 03_deploy_prophet_solution.py
│
└── docs/
    └── calculated_fields_cheatsheet.md  # All Tableau SCRIPT_REAL() formulas
```

---

## Branch Guide

| Branch | Contents |
|--------|----------|
| `main` | Guided starter scripts with TODO markers — **use this during the session** |
| `solutions` | Fully completed scripts — reference if you get stuck |

```bash
# Switch to solutions branch
git checkout solutions

# Switch back to main
git checkout main
```

---

## Session Flow

### Part 1 — Environment Setup *(8 min)*

**Step 1:** Start TabPy
```bash
tabpy
```
Visit `http://localhost:9004` — you should see a JSON response confirming it's running.

**Step 2:** Connect Tableau Desktop to TabPy
1. **Help → Settings and Performance → Manage Analytics Extension Connection**
2. Select **TabPy / External API**
3. Hostname: `localhost` · Port: `9004`
4. Click **Test Connection** — look for the green success message ✅

---

### Part 2 — Scikit-learn Regression Model *(7 min)*

**Step 3:** Open `scripts/01_deploy_regression.py` in your IDE and follow the TODOs.

You'll train a `LinearRegression` model on historical World Cup data and deploy it to TabPy as `predict_total_goals`.

---

### Part 3 — Tableau Calculated Fields *(8 min)*

**Step 4:** In Tableau Desktop, connect to `data/world_cup_results.xlsx` → use the **WorldCupMatches** sheet.

Key fields you'll need:
- `Year`
- `Round`
- `HomeGoals` / `AwayGoals`

See `docs/calculated_fields_cheatsheet.md` for all formulas — or follow Steps 5–7 below.

**Step 5:** Create calculated field → **Total Goals (Actual)**
```
[HomeGoals] + [AwayGoals]
```

**Step 6:** Create calculated field → **Predicted Total Goals**
```
SCRIPT_REAL(
  "return tabpy.query('predict_total_goals', _arg1, _arg2)['response']",
  AVG([Year]),
  ATTR([Round])
)
```

**Step 7:** Build the viz
1. Drag `Year` → **Columns**
2. Drag `Total Goals (Actual)` and `Predicted Total Goals` → **Rows** as dual axis
3. Synchronize the axes
4. Color actual line **blue**, predicted line **orange**
5. Add `Round` to the **Detail** shelf

---

### Part 4 — Bayesian Extension: Credible Interval Band Chart *(Bonus)*

**Step 8:** Open `scripts/02_deploy_bayesian.py` and follow the TODOs.

You'll fit a Bayesian linear model using PyMC and deploy three functions:
- `bayesian_goals_forecast` — posterior mean
- `bayesian_goals_upper` — 90th percentile credible interval
- `bayesian_goals_lower` — 10th percentile credible interval

**Step 9:** Create three calculated fields in Tableau (see cheatsheet).

**Step 10:** Build the band chart:
1. Plot **Posterior Mean** as a line
2. Add **Upper** and **Lower** as a reference band (or dual-axis area chart)
3. Overlay actual avg goals per tournament for comparison

> The shaded band = model uncertainty. Notice it's wider in the early years (sparse data) and tighter in the modern era.

---

### Part 5 — Wrap-Up Discussion *(7 min)*

- **What just happened?** Tableau sent data to a live Python server, got back a full posterior distribution, and rendered it as a credible interval band — in real time.
- **Why Bayesian?** Only ~20 World Cups exist. Bayesian methods handle small-N gracefully.
- **Credible interval vs. confidence interval** — the band literally says "there's an 80% probability the true value is in this range."
- **Where this scales:** Swap PyMC for Prophet for automatic seasonality — great for sales forecasting, pipeline trends, etc.
- **Tableau Cloud consideration:** TabPy must be publicly accessible with SSL. Tableau Cloud egress IPs must be allowlisted.

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and fixes.

---

## Facilitator Resources

See [FACILITATOR.md](FACILITATOR.md) — includes timing cues, talking points, and discussion answers.

---

## Data

`data/world_cup_results.xlsx` contains three sheets:

| Sheet | Rows | Description |
|-------|------|-------------|
| `WorldCupMatches` | 852 | Individual match results (1930–2014) |
| `World Cup - Tableau format` | 1,705 | Team-perspective format (each match appears twice) |
| `WorldCups` | 20 | Tournament-level summary stats |

---

*Session materials for Tableau Conference 2026 · Analytics Extensions & TabPy*
