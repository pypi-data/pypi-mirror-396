"""
Beluga API Wrapper.

Beluga is an open source game control panel.  Pyluga is a Python package
that provides a simplified interface to the API.
"""

from .api_client import BelugaClient  # noqa
from .async_api_client import AsyncBelugaClient  # noqa
from .constants import __version__  # noqa
