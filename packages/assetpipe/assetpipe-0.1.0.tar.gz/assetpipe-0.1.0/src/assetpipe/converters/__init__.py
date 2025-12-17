"""
AssetPipe Converters - Format conversion modules
"""

from typing import Dict, Type, List
from assetpipe.converters.base import BaseConverter
from assetpipe.converters.gltf import GltfConverter
from assetpipe.converters.obj import ObjConverter
from assetpipe.converters.fbx import FbxConverter
from assetpipe.converters.texture import TextureConverter

# Registry of available converters
CONVERTERS: Dict[str, Type[BaseConverter]] = {
    "gltf": GltfConverter,
    "glb": GltfConverter,
    "obj": ObjConverter,
    "fbx": FbxConverter,
    "png": TextureConverter,
    "jpg": TextureConverter,
    "jpeg": TextureConverter,
    "webp": TextureConverter,
}


def get_converter(source_type: str, target_format: str) -> BaseConverter:
    """
    Get appropriate converter for source type to target format.
    """
    target_format = target_format.lower()
    
    if target_format not in CONVERTERS:
        raise ValueError(f"Unsupported target format: {target_format}")
    
    converter_class = CONVERTERS[target_format]
    return converter_class()


def list_converters() -> List[str]:
    """List all available converter formats"""
    return list(CONVERTERS.keys())


def can_convert(source_format: str, target_format: str) -> bool:
    """Check if conversion between formats is supported"""
    source_format = source_format.lower().lstrip(".")
    target_format = target_format.lower().lstrip(".")
    
    # Check if both formats are supported
    return source_format in CONVERTERS and target_format in CONVERTERS


__all__ = [
    "BaseConverter",
    "GltfConverter",
    "ObjConverter",
    "FbxConverter",
    "TextureConverter",
    "get_converter",
    "list_converters",
    "can_convert",
]
