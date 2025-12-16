"""
The TDO package.

Implements classes and functions to process TDO experiments.
"""

import logging
from pathlib import Path

import nexusformat.nexus as nx
from rich.logging import RichHandler

from . import config, gui, sp
from .processors import TDOProcessor

__all__ = ["config", "TDOProcessor", "sp", "gui"]


# Setup logging
APPDIR = Path.home() / ".pytdo"
APPDIR.mkdir(parents=True, exist_ok=True)

fmt = "{asctime}.{msecs:3g} [{levelname}] : {message}"
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

console_handler = RichHandler(log_time_format="%H:%M:%S.%f")
console_handler.setLevel("DEBUG")

file_handler = logging.FileHandler(
    APPDIR / "processors.log", mode="a", encoding="utf-8"
)
file_handler.setLevel("INFO")

file_formatter = logging.Formatter(
    fmt,
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(file_formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Configure NeXus
nx.nxsetconfig(compression=None, encoding="utf-8", lock=0, memory=8000, recursive=True)
