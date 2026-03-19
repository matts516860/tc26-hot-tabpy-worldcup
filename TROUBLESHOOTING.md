# Troubleshooting Guide

*TC26 HoT: Analytics Extensions & TabPy — World Cup Exercise*

---

## TabPy Issues

### ❌ `tabpy: command not found` after install

TabPy's CLI entry point may not be on your PATH.

**Fix:**
```bash
# Option 1 — run as a Python module
python -m tabpy

# Option 2 — find the binary
python -c "import tabpy; import os; print(os.path.dirname(tabpy.__file__))"

# Option 3 — if using a virtual environment, make sure it's activated
source .venv/bin/activate
tabpy
```

---

### ❌ TabPy server won't start / port already in use

```
OSError: [Errno 98] Address already in use
```

Another process is using port 9004 (possibly a previous TabPy session).

**Fix:**
```bash
# Find and kill the process using port 9004
lsof -i :9004
kill -9 <PID>

# Then restart
tabpy
```

On Windows:
```powershell
netstat -ano | findstr :9004
taskkill /PID <PID> /F
```

---

### ❌ Tableau says "Unable to connect to the Analytics Extension"

1. Confirm TabPy is actually running — open `http://localhost:9004` in a browser. You should see JSON.
2. Confirm you're using the correct settings in Tableau:
   - **Help → Settings and Performance → Manage Analytics Extension Connection**
   - Type: **TabPy / External API**
   - Host: `localhost`
   - Port: `9004`
3. Try clicking **Test Connection** again after restarting TabPy.
4. Check firewall rules — on some corporate machines, localhost traffic may be blocked.

---

### ❌ `SCRIPT_REAL` returns `null` or `#VALUE!`

This usually means TabPy received the call but the function threw an error.

**Check the TabPy server terminal window** — Python exceptions are printed there in real time.

Common causes:
- Function not deployed yet → run the `01_deploy_regression.py` script first
- Function name typo → make sure the name in `tabpy.query('...')` exactly matches what you deployed
- Wrong number of arguments → `predict_total_goals` needs exactly two args (`_arg1`, `_arg2`)
- The Round field contains values the LabelEncoder doesn't know → handled gracefully (defaults to 0), but verify your data

---

### ❌ Model deployed but Tableau returns wrong values

Check the level of detail in your viz:

- `AVG([Year])` works correctly when you have **Year** on the Rows/Columns shelf
- `ATTR([Round])` requires that every row in the current mark has the **same** Round value — if mixed, it returns `*`

**Fix:** Add `Round` to the Detail shelf, or use `MIN([Round])` instead of `ATTR([Round])` if you're seeing `*`.

---

## Python / Package Issues

### ❌ `pip install pymc` fails

PyMC has C extension dependencies. Common fixes:

```bash
# Try upgrading pip first
pip install --upgrade pip

# Install with explicit extras
pip install "pymc[dev]"

# On Apple Silicon (M1/M2/M3) — use conda instead
conda install -c conda-forge pymc
```

If conda isn't available, try the conda-forge miniforge installer.

---

### ❌ PyMC import error: `ModuleNotFoundError: No module named 'pytensor'`

PyMC v5 depends on PyTensor (not Theano). Reinstall cleanly:

```bash
pip uninstall pymc pytensor theano -y
pip install pymc
```

---

### ❌ `prophet` install fails on Windows

Prophet requires `pystan`, which needs a C++ compiler on Windows.

**Easiest fix:** Use conda:
```bash
conda install -c conda-forge prophet
```

**Alternative:** Use the pre-built wheel:
```bash
pip install prophet --only-binary :all:
```

---

### ❌ `ImportError: cannot import name 'Prophet' from 'prophet'`

Make sure you installed `prophet` (not `fbprophet`, which is the old deprecated package name):

```bash
pip uninstall fbprophet -y
pip install prophet
```

---

## MCMC / Sampling Issues

### ❌ PyMC sampling is very slow (>5 minutes)

The default `pm.sample(1000, tune=500)` should finish in ~30–60 sec on a modern machine.

If it's hanging:
1. Check CPU usage — MCMC is CPU-bound. Close other applications.
2. Add `cores=1` to avoid multiprocessing overhead:
   ```python
   trace = pm.sample(1000, tune=500, cores=1, return_inferencedata=True, progressbar=False)
   ```
3. Reduce the samples for a quick demo:
   ```python
   trace = pm.sample(500, tune=200, cores=1, return_inferencedata=True, progressbar=False)
   ```

---

### ❌ PyMC divergences warning

```
There were X divergences after tuning.
```

This is a sampler health warning, not a failure. For this exercise it's fine to proceed.

If you want to fix it, add `target_accept=0.9`:
```python
trace = pm.sample(1000, tune=500, target_accept=0.9, return_inferencedata=True)
```

---

## Tableau Cloud / Server Considerations

### TabPy not reachable from Tableau Cloud

Tableau Cloud sends requests **outbound from Salesforce data centers** to your TabPy server. Requirements:

1. TabPy must be on a **publicly accessible** server (not localhost)
2. TabPy must use **HTTPS / SSL** (Tableau Cloud rejects plaintext HTTP)
3. Your server's firewall must **allowlist Tableau Cloud egress IPs** — see [Tableau Cloud IP addresses](https://help.tableau.com/current/online/en-us/to_tableau_server_requirements.htm)

For this conference session, everything runs locally on your laptop — no cloud config needed.

---

## Getting More Help

- Open an issue on this repo
- TabPy docs: https://tableau.github.io/TabPy/
- PyMC docs: https://www.pymc.io/
- Tableau Analytics Extensions docs: https://help.tableau.com/current/pro/desktop/en-us/r_connection_manage.htm
