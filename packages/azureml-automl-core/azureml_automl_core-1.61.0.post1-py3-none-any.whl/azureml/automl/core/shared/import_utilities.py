# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Utility methods for validation and conversion."""
import logging
from typing import Any


class _NoPlotlyFilter(logging.Filter):
    """The filter to remove the errors about forecast visualization."""

    def filter(self, record):
        return not (
            record.getMessage() == 'Importing plotly failed. Interactive plots will not work.' or record.getMessage() == 'Imp\
            orting matplotlib failed. Plotting will not work.')


def import_fbprophet(raise_on_fail: bool = True) -> Any:
    """Import and return the fbprophet module.

    :param raise_on_fail: whether an exception should be raise if import fails, defaults to False
    :type raise_on_fail: bool
    :return: prophet module if it's installed, otherwise None
    """
    logger = logging.getLogger('prophet')
    logger.addFilter(_NoPlotlyFilter())
    try:
        import prophet
        # ensure we can create the model
        prophet.Prophet()
        return prophet
    except ImportError:
        if raise_on_fail:
            raise
        else:
            return None
    except Exception as e:
        if raise_on_fail:
            raise RuntimeError("Prophet instantiation failed") from e
        else:
            return None
