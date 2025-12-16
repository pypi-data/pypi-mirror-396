__all__ = ["FakeDF_IO"]

import importlib.util

if importlib.util.find_spec("pandas") is None:
    raise ImportError(
        "Unable to import pandas, this may be because it is not installed. Pandas tooling is only available when pandas is installed."
    )

from .mock import FakeDF_IO
