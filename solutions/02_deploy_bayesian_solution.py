"""
TC26 HoT: Analytics Extensions & TabPy
Part 4 — Bayesian Extension: Credible Interval Band Chart — SOLUTION
=====================================================================
Complete, runnable solution. Run with:
    python solutions/02_deploy_bayesian_solution.py

Note: MCMC sampling takes ~30–60 seconds. This is normal.
"""

import pymc as pm
import numpy as np
import tabpy_client

# ── Tournament-level data (one row per World Cup, 1930–2014) ──────────────────
years   = np.array([1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966,
                    1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998,
                    2002, 2006, 2010, 2014], dtype=float)

goals   = np.array([70,  70,  84,  88, 140, 126,  89,  89,  95,  97,
                   102, 146, 132, 115, 141, 171, 161, 147, 145, 171], dtype=float)

matches = np.array([18, 17, 18, 22, 26, 35, 32, 32, 32, 38,
                    38, 52, 52, 52, 52, 64, 64, 64, 64, 64], dtype=float)

avg_goals = goals / matches
year_norm = (years - years.mean()) / years.std()

print(f"Data loaded: {len(years)} tournaments, avg goals range "
      f"{avg_goals.min():.2f}–{avg_goals.max():.2f}")


# ── Bayesian linear regression via PyMC ──────────────────────────────────────
print("\nFitting Bayesian model (MCMC sampling ~30–60 sec)...")

with pm.Model() as bayes_model:
    # Priors
    alpha = pm.Normal('alpha', mu=2.8, sigma=0.5)   # intercept: ~2.8 goals/match
    beta  = pm.Normal('beta',  mu=0.0, sigma=0.3)   # slope: weak prior (could go either way)
    sigma = pm.HalfNormal('sigma', sigma=0.3)        # observation noise

    # Linear model
    mu = alpha + beta * year_norm

    # Likelihood
    obs = pm.Normal('obs', mu=mu, sigma=sigma, observed=avg_goals)

    # Sample posterior
    trace = pm.sample(1000, tune=500, return_inferencedata=True, progressbar=False)

print("✅  Sampling complete!")


# ── Extract posterior summary statistics ──────────────────────────────────────
alpha_mean = float(trace.posterior['alpha'].mean())
beta_mean  = float(trace.posterior['beta'].mean())
alpha_std  = float(trace.posterior['alpha'].std())
beta_std   = float(trace.posterior['beta'].std())
year_mean  = float(years.mean())
year_std   = float(years.std())

print(f"\nPosterior summary:")
print(f"  alpha: {alpha_mean:.4f} ± {alpha_std:.4f}")
print(f"  beta:  {beta_mean:.4f} ± {beta_std:.4f}")
print(f"  (negative beta = downward trend in goals over time)")


# ── Deployment functions ───────────────────────────────────────────────────────
# We capture posterior stats as default arguments because TabPy serializes
# and deploys each function independently — module-level variables won't
# be available at query time.

def bayesian_goals_forecast(input_years,
                            _am=alpha_mean, _bm=beta_mean,
                            _ym=year_mean,  _ys=year_std):
    """Posterior mean: best-guess average goals/match for a given year."""
    norm = [(y - _ym) / _ys for y in input_years]
    return [_am + _bm * n for n in norm]


def bayesian_goals_upper(input_years,
                         _am=alpha_mean, _bm=beta_mean,
                         _as=alpha_std,  _bs=beta_std,
                         _ym=year_mean,  _ys=year_std):
    """Upper credible interval (90th percentile)."""
    norm = [(y - _ym) / _ys for y in input_years]
    return [((_am + 1.645 * _as) + (_bm + 1.645 * _bs) * n) for n in norm]


def bayesian_goals_lower(input_years,
                         _am=alpha_mean, _bm=beta_mean,
                         _as=alpha_std,  _bs=beta_std,
                         _ym=year_mean,  _ys=year_std):
    """Lower credible interval (10th percentile)."""
    norm = [(y - _ym) / _ys for y in input_years]
    return [((_am - 1.645 * _as) + (_bm - 1.645 * _bs) * n) for n in norm]


# ── Quick sanity check ────────────────────────────────────────────────────────
test_years = [1930, 1970, 2014, 2026]
forecast   = bayesian_goals_forecast(test_years)
upper      = bayesian_goals_upper(test_years)
lower      = bayesian_goals_lower(test_years)

print("\nSanity check (mean | lower | upper):")
for y, f, lo, hi in zip(test_years, forecast, lower, upper):
    print(f"  {y}: {f:.3f}  [{lo:.3f}, {hi:.3f}]")


# ── Deploy all three functions to TabPy ───────────────────────────────────────
print("\nConnecting to TabPy at http://localhost:9004/ ...")
conn = tabpy_client.Client('http://localhost:9004/')

conn.deploy(
    'bayesian_goals_forecast',
    bayesian_goals_forecast,
    'Posterior mean goals/match for a given tournament year',
    override=True
)

conn.deploy(
    'bayesian_goals_upper',
    bayesian_goals_upper,
    '90th pct credible interval upper bound for goals/match',
    override=True
)

conn.deploy(
    'bayesian_goals_lower',
    bayesian_goals_lower,
    '10th pct credible interval lower bound for goals/match',
    override=True
)

print("✅  Bayesian model deployed! (3 functions)")
print("\nNow create these calculated fields in Tableau:")
print("""
  Posterior Mean:
    SCRIPT_REAL("return tabpy.query('bayesian_goals_forecast', _arg1)['response']",
    AVG([Year]))

  Upper Credible Interval (90th pct):
    SCRIPT_REAL("return tabpy.query('bayesian_goals_upper', _arg1)['response']",
    AVG([Year]))

  Lower Credible Interval (10th pct):
    SCRIPT_REAL("return tabpy.query('bayesian_goals_lower', _arg1)['response']",
    AVG([Year]))
""")
