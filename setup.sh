#!/usr/bin/env bash
# =============================================================================
# TC26 HoT: Analytics Extensions & TabPy — Environment Setup
# =============================================================================
# Run this script once before the session to install all dependencies.
# Usage: bash setup.sh
# =============================================================================

set -e

echo ""
echo "============================================================"
echo "  TC26 HoT: Analytics Extensions & TabPy"
echo "  Environment Setup"
echo "============================================================"
echo ""

# ── 1. Check Python version ──────────────────────────────────────────────────
echo "▶ Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "  Found: $python_version"

required_major=3
required_minor=9
actual_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
major=$(echo $actual_version | cut -d. -f1)
minor=$(echo $actual_version | cut -d. -f2)

if [ "$major" -lt "$required_major" ] || { [ "$major" -eq "$required_major" ] && [ "$minor" -lt "$required_minor" ]; }; then
  echo ""
  echo "❌  Python $required_major.$required_minor+ is required. Please upgrade Python and re-run."
  exit 1
fi
echo "  ✅ Python version OK"
echo ""

# ── 2. (Optional) Create a virtual environment ───────────────────────────────
read -p "▶ Create a virtual environment? (recommended) [y/N]: " create_venv
if [[ "$create_venv" =~ ^[Yy]$ ]]; then
  echo "  Creating virtual environment: .venv"
  python3 -m venv .venv
  source .venv/bin/activate
  echo "  ✅ Virtual environment activated"
  echo "  (To activate later: source .venv/bin/activate)"
else
  echo "  Skipping virtual environment — installing globally"
fi
echo ""

# ── 3. Upgrade pip ───────────────────────────────────────────────────────────
echo "▶ Upgrading pip..."
python3 -m pip install --upgrade pip -q
echo "  ✅ pip up to date"
echo ""

# ── 4. Install dependencies ──────────────────────────────────────────────────
echo "▶ Installing dependencies from requirements.txt..."
python3 -m pip install -r requirements.txt
echo ""
echo "  ✅ All packages installed"
echo ""

# ── 4b. Patch tabpy-client for Python 3.13+ ─────────────────────────────────
echo "▶ Applying TabPy client compatibility patch..."
python3 fix_tabpy_client.py
echo "  ✅ Compatibility patch applied"
echo ""

# ── 5. Verify TabPy import ───────────────────────────────────────────────────
echo "▶ Verifying TabPy installation..."
python3 -c "import tabpy; from importlib.metadata import version; print('  tabpy:', version('tabpy'))" 2>/dev/null || echo "  ⚠️  tabpy version check failed — try importing manually"
python3 -c "import tabpy_client; print('  tabpy-client: OK')" 2>/dev/null || echo "  ⚠️  tabpy_client import failed"
echo ""

# ── 6. Verify scikit-learn ───────────────────────────────────────────────────
echo "▶ Verifying scikit-learn..."
python3 -c "import sklearn; print('  scikit-learn:', sklearn.__version__)"
echo ""

# ── 7. Verify PyMC ───────────────────────────────────────────────────────────
echo "▶ Verifying PyMC..."
python3 -c "import pymc; print('  pymc:', pymc.__version__)" 2>/dev/null || echo "  ⚠️  PyMC import failed — see TROUBLESHOOTING.md"
echo ""

# ── 8. Verify Excel export dependency ────────────────────────────────────────
echo "▶ Verifying Excel export support..."
python3 -c "import openpyxl; print('  openpyxl:', openpyxl.__version__)" 2>/dev/null || echo "  ⚠️  openpyxl import failed"
echo ""

# ── 9. Done ──────────────────────────────────────────────────────────────────
echo "============================================================"
echo "  ✅ Setup complete!"
echo ""
echo "  Next step: start the TabPy server in a NEW terminal:"
echo "    bash start_tabpy.sh"
echo ""
echo "  Then open Tableau Desktop and connect:"
echo "    Help → Settings and Performance →"
echo "    Manage Analytics Extension Connection"
echo "    Host: localhost  |  Port: 9004"
echo "============================================================"
echo ""
