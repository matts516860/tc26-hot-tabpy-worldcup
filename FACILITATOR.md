# Facilitator Guide

*TC26 HoT: Analytics Extensions & TabPy — World Cup Exercise*
*Tableau Conference 2026 · Internal use only*

---

## Session at a Glance

| Part | Topic | Time | Key Deliverable |
|------|-------|------|-----------------|
| 1 | Environment Setup | 8 min | TabPy running, Tableau connected |
| 2 | Scikit-learn Regression | 7 min | `predict_total_goals` deployed |
| 3 | Tableau Calculated Fields | 8 min | Dual-axis line chart (actual vs predicted) |
| 4 | Bayesian Extension (Bonus) | — | Band chart with credible intervals |
| 5 | Wrap-Up Discussion | 7 min | Conceptual understanding + Q&A |

**Total:** ~30 min core · +15 min if doing bonus

---

## Pre-Session Checklist

Do this **before participants arrive**:

- [ ] Clone the repo on your own machine and verify all scripts run end-to-end
- [ ] Confirm TabPy starts on port 9004 and Tableau connects successfully
- [ ] Have `solutions/` branch checked out on a separate machine as a reference
- [ ] Confirm the Wi-Fi at the venue won't block localhost traffic (rare but happens)
- [ ] Pre-install all packages so any live demos don't wait on pip
- [ ] Know the PyMC sampling time on your machine so you can set expectations
- [ ] Load `data/world_cup_results.xlsx` in Tableau and verify fields are readable

---

## Part 1 — Environment Setup *(8 min)*

### Talking Points

**What is TabPy?**
> "TabPy is Tableau's Analytics Extensions server for Python. It runs as a local (or remote) process and exposes a REST API. When Tableau evaluates a `SCRIPT_REAL()` calculated field, it's making an HTTP POST to that API — sending the values from your viz and getting back a list of floats."

**Why bother? Doesn't Tableau have built-in forecasting?**
> "Built-in forecasting is exponential smoothing — great for many cases. But TabPy unlocks arbitrary Python: scikit-learn, PyMC, Prophet, transformers, custom business logic, real-time inference. You're not limited to Tableau's model menu."

### Timing Cues

- ⏱ **0:00** — Ask participants to open a terminal and run `tabpy`
- ⏱ **1:00** — While TabPy starts, do the Tableau connection steps together
- ⏱ **3:00** — "Green checkmark? Great. If not, raise your hand — check TROUBLESHOOTING.md"
- ⏱ **5:00** — Explain what TabPy is (talking points above)
- ⏱ **8:00** — Transition: "Open scripts/01_deploy_regression.py"

### Common Issues at This Stage

- **tabpy not found** → `python -m tabpy` as fallback
- **Tableau connection fails** → confirm TabPy terminal shows "Starting TabPy..."
- **Port 9004 in use** → kill old TabPy process (see TROUBLESHOOTING.md)

---

## Part 2 — Scikit-learn Regression Model *(7 min)*

### Talking Points

**Why LabelEncoder?**
> "LinearRegression expects numbers. LabelEncoder maps strings to integers: 'Final' → 1, 'Group' → 2, etc. The encoding is alphabetical — there's no ordinal meaning here, which is a limitation of this approach. In a real pipeline you'd use one-hot encoding or target encoding. But for this exercise it gets us running fast."

**What does the model actually learn?**
> "Two coefficients: one for Year (slope over time) and one for encoded Round. The Year coefficient should be negative — goals per match have generally declined since 1954. The Round coefficient captures that knockout rounds (Final, Semi-finals) tend to have fewer goals than group matches."

**Why deploy to TabPy instead of just using Tableau's built-in trend line?**
> "The built-in trend line can't use external features — it only looks at what's already in the viz. Our model takes Round as an input, which Tableau's built-in can't do. More importantly, this pattern — 'any Python function, callable from a calculated field' — scales to any model you can imagine."

### Timing Cues

- ⏱ **8:00** — Participants open `scripts/01_deploy_regression.py`
- ⏱ **9:00** — Read through the TODO blocks together (don't solve them yet)
- ⏱ **10:00** — "Work through TODO 1 and 2 — build the DataFrame and label encode"
- ⏱ **11:30** — "Now TODO 3 — fit the model. `model.fit(X, y)` is one line"
- ⏱ **12:30** — Walk through the predict function structure (the tricky part: imports inside the function)
- ⏱ **14:30** — "Run the script — you should see 'Model deployed successfully!'"
- ⏱ **15:00** — Transition to Tableau

### Key Teaching Moment: Imports Inside the Function

> "Notice we import numpy **inside** `predict_total_goals`, not at the top of the file. This is a TabPy gotcha: when you deploy a function, TabPy serializes it and runs it in its own context on the server. Module-level imports aren't available inside deployed functions — you have to import inside. Same rule applies to the Bayesian and Prophet functions."

### Answer Key

```python
# TODO 1
df = pd.DataFrame({'Year': years, 'Round_Type': round_types, 'AvgGoals': avg_goals})

# TODO 2
df['Round_Encoded'] = le.fit_transform(df['Round_Type'])

# TODO 3
X = df[['Year', 'Round_Encoded']]
y = df['AvgGoals']
model.fit(X, y)

# TODO 4 (core logic)
def predict_total_goals(years, rounds):
    import numpy as np
    known_rounds = list(le.classes_)
    encoded = [le.transform([r])[0] if r in known_rounds else 0 for r in rounds]
    features = np.column_stack([years, encoded])
    return model.predict(features).tolist()

# TODO 5
connection = tabpy_client.Client('http://localhost:9004/')
connection.deploy('predict_total_goals', predict_total_goals,
                  'Predicts average total goals for a match given Year and Round type',
                  override=True)
print("Model deployed successfully!")
```

---

## Part 3 — Tableau Calculated Fields *(8 min)*

### Talking Points

**What is `SCRIPT_REAL()`?**
> "Tableau has four SCRIPT_ functions: SCRIPT_REAL, SCRIPT_INT, SCRIPT_STR, and SCRIPT_BOOL. The suffix is the return type. Each function takes a string of Python code as the first argument, followed by any Tableau fields to pass as arguments — accessed as `_arg1`, `_arg2`, etc. inside the Python string."

**Why `AVG([Year])` and not just `[Year]`?**
> "SCRIPT_ functions work at the mark level, not the row level. Tableau aggregates before sending. Using AVG([Year]) ensures we send one value per mark. If you dragged Year to Columns, each mark already IS a single year, so AVG just passes it through."

**Why `ATTR([Round])` instead of `[Round]`?**
> "ATTR is Tableau's way of saying 'this dimension should have exactly one value per mark.' If a mark has multiple Round values (which shouldn't happen if Round is on Detail), ATTR returns `*`. If you're seeing asterisks, add Round to the Detail shelf — or use MIN([Round]) as a workaround."

### Timing Cues

- ⏱ **15:00** — "Open Tableau, connect to data/world_cup_results.xlsx → WorldCupMatches sheet"
- ⏱ **16:00** — Create Total Goals (Actual) together: `[HomeGoals] + [AwayGoals]`
- ⏱ **17:30** — Walk through SCRIPT_REAL syntax (talking points above)
- ⏱ **18:30** — Participants create Predicted Total Goals calc
- ⏱ **20:00** — "Drag Year to Columns, both measures to Rows as dual axis"
- ⏱ **22:00** — Color the lines. "Anyone see the prediction tracking the actual well?"
- ⏱ **23:00** — Transition: "The prediction is decent, but there's no uncertainty. That's where Bayesian comes in."

### Discussion Prompt for the Viz

> "Look at the gap between actual and predicted in the 1950s. Total goals spiked heavily in 1954 (the highest-scoring World Cup ever: 5.38 avg goals/match). Why might a linear model miss this? What would you add as a feature to capture it?"

*Good answers: Tournament format changes, number of teams, era effects, whether extra time was used.*

---

## Part 4 — Bayesian Extension *(Bonus)*

### Talking Points

**Why Bayesian for this dataset?**
> "We have exactly 20 data points — one per World Cup. That's tiny. Frequentist methods give you a point estimate and confidence intervals derived from asymptotic theory. Bayesian methods give you a full posterior distribution — every parameter has a distribution, not just a value. With small N, that uncertainty representation is much more honest."

**What is the credible interval actually saying?**
> "The band in the viz says: 'Given this data and our priors, there is an 80% probability that the true average goals per match for this year falls within this band.' That's fundamentally different from a frequentist confidence interval, which says: 'If we ran this experiment 100 times, 80% of the resulting intervals would contain the true parameter.' The Bayesian statement is what most people actually want."

**Why is the band wider in early years?**
> "Data is sparse — only 13–22 matches in the early World Cups vs 64 today. The model is more uncertain about early trends. The posterior reflects that. This is the Bayesian model 'being honest' about what it doesn't know."

**The `1.645` magic number:**
> "1.645 is the z-score for the 90th percentile of a standard normal. We're approximating the credible interval by taking `mean ± 1.645 × std` of the posterior samples. This works because the posteriors here are approximately normal. For skewed posteriors you'd use `np.percentile(samples, [10, 90])` directly."

### Timing Cues (if doing the bonus)

- ⏱ **23:00** — "Open scripts/02_deploy_bayesian.py"
- ⏱ **24:00** — Explain the data structure (tournament-level, not match-level)
- ⏱ **25:30** — Explain PyMC model definition (alpha, beta, sigma, obs)
- ⏱ **27:00** — Run the script: "This takes ~30-60 sec — talk amongst yourselves"
- ⏱ **28:30** — Explain why default args are used in the deployment functions
- ⏱ **30:00** — Switch to Tableau, create the three calculated fields
- ⏱ **33:00** — Build the band chart together

---

## Part 5 — Wrap-Up Discussion *(7 min)*

### Suggested Discussion Questions

1. **"What just happened?"** (Let participants explain it back to you — teaches better than lecturing)
2. **"When would you use TabPy vs Tableau's built-in forecasting?"**
   - Built-in: quick, no setup, good enough for standard ETS/ARIMA trends
   - TabPy: custom features, advanced models, non-time-series ML, ensemble methods, NLP
3. **"What would you build with this at your company?"**
   - Good prompts: churn prediction, lead scoring, demand forecasting, anomaly detection
4. **"What are the production gotchas?"**
   - TabPy must stay running (process management: systemd, Docker, cloud deploy)
   - Tableau Cloud needs public TabPy endpoint with SSL
   - Model retraining → redeploy function with `override=True`

### Prophet Teaser (if time)

> "Prophet is a drop-in upgrade for time series use cases. `scripts/03_deploy_prophet.py` shows how. The key difference: Prophet gives you `yhat_lower` and `yhat_upper` for free without any Bayesian math on your part. For sales forecasting, pipeline trends, or any business time series — it's usually your first call."

### Closing Line

> "Everything you built today is production-ready architecture. TabPy + Tableau is how data science teams at companies like Chevron, Lufthansa, and Salesforce are embedding ML models directly into executive dashboards. The World Cup data was just the fun part — the pattern is universally applicable."

---

## If You Run Out of Time

**Cut first:** The Prophet bonus (it's a wrap-up demo, not core content)

**Cut second:** The full Bayesian band chart build in Tableau (show yours instead)

**Never cut:** The core regression deploy + SCRIPT_REAL calculated field (Parts 1–3) — that's the fundamental skill

---

## Q&A Cheat Sheet

| Question | Answer |
|----------|--------|
| Can TabPy run in the cloud? | Yes — any Python server with a public IP. AWS EC2, GCP, Azure all work. Needs SSL for Tableau Cloud. |
| Does Tableau Server support this? | Yes, with TabPy configured in TSC settings. IT needs to whitelist the TabPy host. |
| Can you deploy R models? | Yes, via RServe (Tableau's Analytics Extension for R). Same pattern. |
| What's the latency? | Depends on model complexity. Linear regression: <50ms. MCMC: not recommended at query time — sample offline, deploy the summary stats (as we did here). |
| Can I deploy a neural net? | Yes. Load a TensorFlow/PyTorch model, wrap it in a function, deploy. Works great for image classification or NLP inference on text fields. |
| Is this secure? | TabPy has optional auth (username/password). For production, put it behind a reverse proxy with TLS. |
