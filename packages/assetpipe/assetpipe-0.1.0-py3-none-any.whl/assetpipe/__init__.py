"""
AssetPipe - Universal Asset Pipeline CLI

Convert, optimize, and validate 3D/2D assets across formats.
"""

__version__ = "0.1.0"
__author__ = "AssetPipe Team"

from assetpipe.core.asset import Asset, AssetType
from assetpipe.core.pipeline import Pipeline
from assetpipe.core.config import PipelineConfig

__all__ = [
    "__version__",
    "Asset",
    "AssetType",
    "Pipeline",
    "PipelineConfig",
]
