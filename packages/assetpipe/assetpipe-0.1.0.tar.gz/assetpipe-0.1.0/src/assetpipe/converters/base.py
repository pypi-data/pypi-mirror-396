"""
Base Converter - Abstract base class for format converters
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from assetpipe.core.asset import Asset


class BaseConverter(ABC):
    """
    Abstract base class for asset format converters.
    
    Each converter handles loading and saving assets in a specific format.
    """
    
    # Format identifier (e.g., "gltf", "fbx")
    format_id: str = ""
    
    # File extensions this converter handles
    extensions: List[str] = []
    
    # Human-readable format name
    format_name: str = ""
    
    # Whether this converter supports loading
    can_load: bool = True
    
    # Whether this converter supports saving
    can_save: bool = True
    
    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> "Asset":
        """
        Load an asset from file.
        
        Args:
            path: Path to the asset file
            
        Returns:
            Loaded Asset object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        pass
    
    @classmethod
    @abstractmethod
    def save(cls, asset: "Asset", path: Path) -> None:
        """
        Save an asset to file.
        
        Args:
            asset: Asset to save
            path: Output file path
            
        Raises:
            ValueError: If asset cannot be saved in this format
        """
        pass
    
    @classmethod
    def convert(cls, asset: "Asset", output_path: Path) -> None:
        """
        Convert and save an asset.
        
        This is a convenience method that calls save().
        Subclasses can override for format-specific optimizations.
        """
        cls.save(asset, output_path)
    
    @classmethod
    def supports_extension(cls, extension: str) -> bool:
        """Check if this converter supports a file extension"""
        ext = extension.lower().lstrip(".")
        return ext in cls.extensions
    
    @classmethod
    def get_info(cls) -> dict:
        """Get converter information"""
        return {
            "format_id": cls.format_id,
            "format_name": cls.format_name,
            "extensions": cls.extensions,
            "can_load": cls.can_load,
            "can_save": cls.can_save,
        }
