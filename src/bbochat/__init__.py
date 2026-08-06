"""Initialise the application."""

from importlib.metadata import metadata, version

from psiutils.utilities import psi_logger

from bbochat.constants import APP_NAME

# must be package name i.e. directory under /src/
__app_name__ = APP_NAME

logger = psi_logger(__app_name__)

meta = metadata(__app_name__)
__summary__: str = meta["Summary"]
__author__: str = meta["Author"]
__version__: str = version(__app_name__)
