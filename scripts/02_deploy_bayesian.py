"""
TC26 HoT: Analytics Extensions & TabPy
Part 4 — Bayesian Extension: Credible Interval Band Chart (Bonus)
=================================================================
Goal: Fit a Bayesian linear model using PyMC on tournament-level goal data.
Deploy THREE functions to TabPy:
  • bayesian_goals_forecast  — posterior mean prediction
  • bayesian_goals_upper     — 90th percentile credible interval (upper bound)
  • bayesian_goals_lower     — 10th percentile credible interval (lower bound)

These three values let Tableau draw a band chart showing model uncertainty.

Instructions: Complete each TODO block. Run with:
    python scripts/02_deploy_bayesian.py

This script takes ~30–60 seconds due to MCMC sampling.

Reference: solutions/02_deploy_bayesian_solution.py
"""

# ── Imports ───────────────────────────────────────────────────────────────────
import pymc as pm
import numpy as np
import tabpy_client


# =============================================================================
# TODO 1 — Set up the training data
# =============================================================================
# We work at the TOURNAMENT level here (one row per World Cup).
# Each tournament has:
#   years    — the year the tournament was held
#   goals    — total goals scored across all matches
#   matches  — total number of matches played
#
# Compute avg_goals = goals / matches  (element-wise numpy division)
# Then normalize years: year_norm = (years - mean) / std
# (Normalization helps the MCMC sampler converge faster)
#
# The data arrays are provided — just do the math.

years   = np.array([1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966,
                    1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998,
                    2002, 2006, 2010, 2014], dtype=float)

goals   = np.array([70,  70,  84,  88, 140, 126,  89,  89,  95,  97,
                   102, 146, 132, 115, 141, 171, 161, 147, 145, 171], dtype=float)

matches = np.array([18, 17, 18, 22, 26, 35, 32, 32, 32, 38,
                    38, 52, 52, 52, 52, 64, 64, 64, 64, 64], dtype=float)

# YOUR CODE HERE ↓
avg_goals = None   # goals / matches
year_norm = None   # (years - years.mean()) / years.std()


# =============================================================================
# TODO 2 — Build and sample the PyMC Bayesian model
# =============================================================================
# Define a Bayesian linear regression:
#   alpha ~ Normal(mu=2.8, sigma=0.5)   ← prior on intercept
#   beta  ~ Normal(mu=0.0, sigma=0.3)   ← prior on slope (trend over time)
#   sigma ~ HalfNormal(sigma=0.3)        ← observation noise
#   mu    = alpha + beta * year_norm
#   obs   ~ Normal(mu=mu, sigma=sigma, observed=avg_goals)
#
# Sample with: pm.sample(1000, tune=500, return_inferencedata=True, progressbar=False)
# Store the result in `trace`.

# YOUR CODE HERE ↓
with pm.Model() as bayes_model:
    pass  # replace with your model definition


# =============================================================================
# TODO 3 — Extract posterior summary statistics
# =============================================================================
# From `trace.posterior`, extract:
#   alpha_mean, alpha_std   ← mean and std of the alpha samples
#   beta_mean,  beta_std    ← mean and std of the beta samples
#
# Also store year_mean and year_std (needed inside the deployed functions
# to normalize incoming year values at query time).
#
# Hint: float(trace.posterior['alpha'].mean())

# YOUR CODE HERE ↓
alpha_mean = None
beta_mean  = None
alpha_std  = None
beta_std   = None
year_mean  = float(years.mean())
year_std   = float(years.std())


# =============================================================================
# TODO 4 — Define the three deployment functions
# =============================================================================
# All three functions accept input_years (a list of floats) and return a list.
# They normalize input years using year_mean / year_std computed above.
# Remember: TabPy deploys functions in isolation — capture the variables
# you need as default arguments (e.g., def fn(x, _am=alpha_mean): ...).
#
# bayesian_goals_forecast  → posterior mean:  alpha_mean + beta_mean * norm
# bayesian_goals_upper     → upper 90th pct:
#     (alpha_mean + 1.645 * alpha_std) + (beta_mean + 1.645 * beta_std) * norm
# bayesian_goals_lower     → lower 10th pct:
#     (alpha_mean - 1.645 * alpha_std) + (beta_mean - 1.645 * beta_std) * norm
#
# Why 1.645? That's the z-score for a one-tailed 90% interval.

def bayesian_goals_forecast(input_years,
                            _am=alpha_mean, _bm=beta_mean,
                            _ym=year_mean,  _ys=year_std):
    # YOUR CODE HERE ↓
    pass


def bayesian_goals_upper(input_years,
                         _am=alpha_mean, _bm=beta_mean,
                         _as=alpha_std,  _bs=beta_std,
                         _ym=year_mean,  _ys=year_std):
    # YOUR CODE HERE ↓
    pass


def bayesian_goals_lower(input_years,
                         _am=alpha_mean, _bm=beta_mean,
                         _as=alpha_std,  _bs=beta_std,
                         _ym=year_mean,  _ys=year_std):
    # YOUR CODE HERE ↓
    pass


# =============================================================================
# TODO 5 — Deploy all three functions to TabPy
# =============================================================================
# Connect to http://localhost:9004/ and deploy all three functions.
# Use descriptive names matching what you'll call in Tableau:
#   'bayesian_goals_forecast' — 'Posterior mean goals/match for a given year'
#   'bayesian_goals_upper'    — '90th pct credible interval upper bound'
#   'bayesian_goals_lower'    — '10th pct credible interval lower bound'
# Use override=True for all three.

# YOUR CODE HERE ↓
