#!/usr/bin/env python3
"""Patch legacy tabpy_client imports for Python 3.13+."""

from pathlib import Path
import sys
import sysconfig


LEGACY_IMPORT = "from collections import MutableMapping as _MutableMapping"
PATCHED_IMPORT = "\n".join(
    [
        "try:",
        "    from collections.abc import MutableMapping as _MutableMapping",
        "except ImportError:",
        "    from collections import MutableMapping as _MutableMapping",
    ]
)


def candidate_paths():
    seen = set()

    purelib = Path(sysconfig.get_paths()["purelib"])
    candidates = [purelib / "tabpy_client" / "rest.py"]

    prefix = Path(sys.prefix)
    candidates.extend(prefix.glob("lib/python*/site-packages/tabpy_client/rest.py"))

    for path in candidates:
        if path not in seen:
            seen.add(path)
            yield path


def patch_file(path):
    if not path.exists():
        return False, "missing"

    content = path.read_text()
    if PATCHED_IMPORT in content:
        return False, "already patched"
    if LEGACY_IMPORT not in content:
        return False, "unexpected contents"

    path.write_text(content.replace(LEGACY_IMPORT, PATCHED_IMPORT))
    return True, "patched"


def main():
    changed = 0
    checked = 0

    for path in candidate_paths():
        checked += 1
        updated, status = patch_file(path)
        if updated:
            changed += 1
        print(f"{path}: {status}")

    if checked == 0:
        print("No tabpy_client installations found.")
        return

    if changed == 0:
        print("No changes needed.")
    else:
        print(f"Patched {changed} file(s).")


if __name__ == "__main__":
    main()
