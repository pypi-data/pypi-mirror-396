"""
Texture Converter - Load and save texture files
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional
import io

import numpy as np
from PIL import Image

from assetpipe.converters.base import BaseConverter
from assetpipe.core.asset import Asset, AssetType, Texture

if TYPE_CHECKING:
    pass


class TextureConverter(BaseConverter):
    """
    Converter for texture/image files.
    
    Supports common formats: PNG, JPG, TGA, BMP, WebP, etc.
    """
    
    format_id = "texture"
    extensions = ["png", "jpg", "jpeg", "tga", "bmp", "webp", "tiff", "gif"]
    format_name = "Texture Image"
    can_load = True
    can_save = True
    
    @classmethod
    def load(cls, path: Path) -> Asset:
        """Load a texture file"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Load with PIL
        img = Image.open(path)
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            if img.mode == 'RGB':
                img = img.convert('RGBA')
            elif img.mode in ('L', 'LA', 'P'):
                img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img, dtype=np.uint8)
        
        texture = Texture(
            name=path.stem,
            path=path,
            width=img.width,
            height=img.height,
            channels=4 if img.mode == 'RGBA' else 3,
            data=data,
            format=path.suffix[1:].lower(),
        )
        
        asset = Asset(
            name=path.stem,
            type=AssetType.TEXTURE,
            source_path=path,
            textures=[texture],
        )
        
        return asset
    
    @classmethod
    def save(cls, asset: Asset, path: Path) -> None:
        """Save texture to file"""
        path = Path(path)
        
        if not asset.textures:
            raise ValueError("Asset has no textures to save")
        
        texture = asset.textures[0]
        
        if texture.data is None:
            raise ValueError("Texture has no data to save")
        
        # Convert numpy array to PIL Image
        img = Image.fromarray(texture.data)
        
        # Determine format from extension
        fmt = path.suffix[1:].upper()
        if fmt == 'JPG':
            fmt = 'JPEG'
        
        # Convert to RGB for JPEG (no alpha)
        if fmt == 'JPEG' and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Save
        img.save(path, format=fmt)
    
    @classmethod
    def resize(
        cls,
        texture: Texture,
        max_size: int,
        resample: int = Image.Resampling.LANCZOS,
    ) -> Texture:
        """
        Resize texture to fit within max_size while maintaining aspect ratio.
        """
        if texture.data is None:
            return texture
        
        # Check if resize needed
        if texture.width <= max_size and texture.height <= max_size:
            return texture
        
        # Calculate new size
        aspect = texture.width / texture.height
        if texture.width > texture.height:
            new_width = max_size
            new_height = int(max_size / aspect)
        else:
            new_height = max_size
            new_width = int(max_size * aspect)
        
        # Resize
        img = Image.fromarray(texture.data)
        img = img.resize((new_width, new_height), resample=resample)
        
        return Texture(
            name=texture.name,
            path=texture.path,
            width=new_width,
            height=new_height,
            channels=texture.channels,
            data=np.array(img, dtype=np.uint8),
            format=texture.format,
        )
    
    @classmethod
    def compress(
        cls,
        texture: Texture,
        format: str = "webp",
        quality: int = 85,
    ) -> bytes:
        """
        Compress texture to specified format.
        Returns compressed bytes.
        """
        if texture.data is None:
            raise ValueError("Texture has no data")
        
        img = Image.fromarray(texture.data)
        
        # Convert to RGB for JPEG
        if format.lower() in ('jpg', 'jpeg') and img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Compress to bytes
        buffer = io.BytesIO()
        
        if format.lower() == 'webp':
            img.save(buffer, format='WEBP', quality=quality)
        elif format.lower() in ('jpg', 'jpeg'):
            img.save(buffer, format='JPEG', quality=quality)
        elif format.lower() == 'png':
            img.save(buffer, format='PNG', optimize=True)
        else:
            img.save(buffer, format=format.upper())
        
        return buffer.getvalue()
    
    @classmethod
    def generate_mipmaps(cls, texture: Texture) -> list[Texture]:
        """
        Generate mipmap chain for texture.
        Returns list of textures from largest to smallest.
        """
        if texture.data is None:
            return [texture]
        
        mipmaps = [texture]
        
        current = texture
        while current.width > 1 or current.height > 1:
            new_width = max(1, current.width // 2)
            new_height = max(1, current.height // 2)
            
            img = Image.fromarray(current.data)
            img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
            
            mip = Texture(
                name=f"{texture.name}_mip{len(mipmaps)}",
                width=new_width,
                height=new_height,
                channels=texture.channels,
                data=np.array(img, dtype=np.uint8),
                format=texture.format,
            )
            mipmaps.append(mip)
            current = mip
        
        return mipmaps
    
    @classmethod
    def convert_format(
        cls,
        texture: Texture,
        target_format: str,
        quality: int = 85,
    ) -> Texture:
        """
        Convert texture to different format.
        """
        if texture.data is None:
            raise ValueError("Texture has no data")
        
        # Compress to target format
        compressed = cls.compress(texture, target_format, quality)
        
        # Reload to get proper data
        img = Image.open(io.BytesIO(compressed))
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        return Texture(
            name=texture.name,
            width=img.width,
            height=img.height,
            channels=4,
            data=np.array(img, dtype=np.uint8),
            format=target_format.lower(),
        )
