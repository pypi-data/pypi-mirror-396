"""
Texture Optimization - Resizing, compression, format conversion
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import io

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from assetpipe.core.asset import Texture, Asset


class TextureOptimizer:
    """
    Texture optimization utilities.
    """
    
    def resize(
        self,
        texture: "Texture",
        max_size: int,
        resample: int = Image.Resampling.LANCZOS,
    ) -> "Texture":
        """
        Resize texture to fit within max_size.
        
        Args:
            texture: Texture to resize
            max_size: Maximum dimension (width or height)
            resample: PIL resampling filter
            
        Returns:
            New resized Texture (or original if no resize needed)
        """
        from assetpipe.core.asset import Texture as TextureClass
        
        if texture.data is None:
            return texture
        
        # Check if resize needed
        if texture.width <= max_size and texture.height <= max_size:
            return texture
        
        # Calculate new size maintaining aspect ratio
        aspect = texture.width / texture.height
        
        if texture.width > texture.height:
            new_width = max_size
            new_height = int(max_size / aspect)
        else:
            new_height = max_size
            new_width = int(max_size * aspect)
        
        # Ensure minimum size of 1
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # Resize
        img = Image.fromarray(texture.data)
        img = img.resize((new_width, new_height), resample=resample)
        
        return TextureClass(
            name=texture.name,
            path=texture.path,
            width=new_width,
            height=new_height,
            channels=texture.channels,
            data=np.array(img, dtype=np.uint8),
            format=texture.format,
        )
    
    def compress(
        self,
        texture: "Texture",
        format: str = "webp",
        quality: int = 85,
    ) -> bytes:
        """
        Compress texture to bytes.
        
        Args:
            texture: Texture to compress
            format: Output format (webp, jpg, png)
            quality: Compression quality (1-100)
            
        Returns:
            Compressed image bytes
        """
        if texture.data is None:
            raise ValueError("Texture has no data")
        
        img = Image.fromarray(texture.data)
        
        # Convert to RGB for JPEG (no alpha)
        if format.lower() in ('jpg', 'jpeg') and img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
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
    
    def convert_format(
        self,
        texture: "Texture",
        target_format: str,
        quality: int = 85,
    ) -> "Texture":
        """
        Convert texture to different format.
        
        Args:
            texture: Texture to convert
            target_format: Target format (webp, jpg, png)
            quality: Compression quality
            
        Returns:
            New Texture in target format
        """
        from assetpipe.core.asset import Texture as TextureClass
        
        if texture.data is None:
            raise ValueError("Texture has no data")
        
        # Compress to target format
        compressed = self.compress(texture, target_format, quality)
        
        # Reload to get proper data
        img = Image.open(io.BytesIO(compressed))
        
        # Convert to RGBA for consistency
        if img.mode != 'RGBA':
            if img.mode == 'RGB':
                img = img.convert('RGBA')
            else:
                img = img.convert('RGBA')
        
        return TextureClass(
            name=texture.name,
            path=texture.path,
            width=img.width,
            height=img.height,
            channels=4,
            data=np.array(img, dtype=np.uint8),
            format=target_format.lower(),
        )
    
    def generate_mipmaps(
        self,
        texture: "Texture",
    ) -> List["Texture"]:
        """
        Generate mipmap chain.
        
        Args:
            texture: Source texture
            
        Returns:
            List of textures from largest to smallest
        """
        from assetpipe.core.asset import Texture as TextureClass
        
        if texture.data is None:
            return [texture]
        
        mipmaps = [texture]
        current = texture
        level = 1
        
        while current.width > 1 or current.height > 1:
            new_width = max(1, current.width // 2)
            new_height = max(1, current.height // 2)
            
            img = Image.fromarray(current.data)
            img = img.resize(
                (new_width, new_height),
                resample=Image.Resampling.LANCZOS
            )
            
            mip = TextureClass(
                name=f"{texture.name}_mip{level}",
                width=new_width,
                height=new_height,
                channels=texture.channels,
                data=np.array(img, dtype=np.uint8),
                format=texture.format,
            )
            mipmaps.append(mip)
            current = mip
            level += 1
        
        return mipmaps
    
    def make_power_of_two(
        self,
        texture: "Texture",
        round_up: bool = True,
    ) -> "Texture":
        """
        Resize texture to power-of-two dimensions.
        
        Args:
            texture: Texture to resize
            round_up: If True, round up to next power of 2
            
        Returns:
            Resized texture
        """
        from assetpipe.core.asset import Texture as TextureClass
        
        if texture.data is None:
            return texture
        
        def next_power_of_two(n: int) -> int:
            if n <= 0:
                return 1
            p = 1
            while p < n:
                p *= 2
            return p
        
        def prev_power_of_two(n: int) -> int:
            if n <= 1:
                return 1
            p = 1
            while p * 2 <= n:
                p *= 2
            return p
        
        if round_up:
            new_width = next_power_of_two(texture.width)
            new_height = next_power_of_two(texture.height)
        else:
            new_width = prev_power_of_two(texture.width)
            new_height = prev_power_of_two(texture.height)
        
        if new_width == texture.width and new_height == texture.height:
            return texture
        
        img = Image.fromarray(texture.data)
        img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
        
        return TextureClass(
            name=texture.name,
            path=texture.path,
            width=new_width,
            height=new_height,
            channels=texture.channels,
            data=np.array(img, dtype=np.uint8),
            format=texture.format,
        )
    
    def estimate_vram_usage(self, texture: "Texture", with_mipmaps: bool = True) -> int:
        """
        Estimate VRAM usage for texture.
        
        Args:
            texture: Texture to estimate
            with_mipmaps: Include mipmap chain in estimate
            
        Returns:
            Estimated bytes of VRAM
        """
        base_size = texture.width * texture.height * texture.channels
        
        if with_mipmaps:
            # Mipmaps add approximately 33% overhead
            return int(base_size * 1.33)
        
        return base_size


# Convenience functions
def optimize_textures(
    asset: "Asset",
    max_size: int = 2048,
    format: str = "webp",
    quality: int = 85,
) -> None:
    """Optimize all textures in asset"""
    optimizer = TextureOptimizer()
    
    for i, texture in enumerate(asset.textures):
        # Resize if needed
        if texture.width > max_size or texture.height > max_size:
            texture = optimizer.resize(texture, max_size)
        
        # Convert format if needed
        if texture.format != format.lower():
            texture = optimizer.convert_format(texture, format, quality)
        
        asset.textures[i] = texture


def resize_textures(asset: "Asset", max_size: int) -> None:
    """Resize all textures in asset"""
    optimizer = TextureOptimizer()
    
    for i, texture in enumerate(asset.textures):
        if texture.width > max_size or texture.height > max_size:
            asset.textures[i] = optimizer.resize(texture, max_size)


def compress_textures(
    asset: "Asset",
    format: str = "webp",
    quality: int = 85,
) -> None:
    """Compress all textures in asset"""
    optimizer = TextureOptimizer()
    
    for i, texture in enumerate(asset.textures):
        asset.textures[i] = optimizer.convert_format(texture, format, quality)
