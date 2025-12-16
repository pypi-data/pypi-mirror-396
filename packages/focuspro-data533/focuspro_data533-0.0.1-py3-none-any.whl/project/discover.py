"""
Simple unittest discovery runner.

Run from the repo root:
    python discover.py
This discovers tests under `test/` using unittest's built-in loader and
executes them with a text runner.
"""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

# Ensure project root is on sys.path so imports like `core.task` work.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run() -> unittest.result.TestResult:
    suite = unittest.defaultTestLoader.discover("test")
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == "__main__":
    run()
