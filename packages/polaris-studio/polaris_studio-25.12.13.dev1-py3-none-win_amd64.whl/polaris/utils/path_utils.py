# Copyright (c) 2025, UChicago Argonne, LLC
# BSD OPEN SOURCE LICENSE. Full license can be found in LICENSE.md
from pathlib import Path
import tempfile


def tempdirpath() -> Path:
    return Path(tempfile.gettempdir())
