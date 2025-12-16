from typing import Any

from pyuson.config.models import BinaryFile

from .models import Metadata, Nexus, Parameters, Settings


class tConfig:
    
    files: dict[str, BinaryFile]
    parameters: Parameters
    settings: Settings
    metadata: Metadata

    nx: dict[str, dict[str, Any]]
    nexus: Nexus
