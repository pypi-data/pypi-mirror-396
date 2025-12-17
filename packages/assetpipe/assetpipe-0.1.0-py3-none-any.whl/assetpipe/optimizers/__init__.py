"""
AssetPipe Optimizers - Mesh and texture optimization
"""

from typing import Optional, List
from assetpipe.core.asset import Asset
from assetpipe.optimizers.mesh import (
    decimate_mesh,
    merge_vertices,
    remove_degenerate_triangles,
    generate_lods,
)
from assetpipe.optimizers.texture import (
    optimize_textures,
    resize_textures,
    compress_textures,
)


def optimize_asset(
    asset: Asset,
    decimate_ratio: Optional[float] = None,
    max_texture_size: Optional[int] = None,
    generate_lods: bool = False,
    merge_verts: bool = True,
    remove_degenerates: bool = True,
) -> Asset:
    """
    Optimize an asset with various options.
    
    Args:
        asset: Asset to optimize
        decimate_ratio: Target ratio for mesh decimation (0.0-1.0)
        max_texture_size: Maximum texture dimension
        generate_lods: Whether to generate LOD levels
        merge_verts: Whether to merge duplicate vertices
        remove_degenerates: Whether to remove degenerate triangles
        
    Returns:
        Optimized asset (may be same object, modified in place)
    """
    from assetpipe.optimizers.mesh import MeshOptimizer
    from assetpipe.optimizers.texture import TextureOptimizer
    
    # Optimize meshes
    mesh_optimizer = MeshOptimizer()
    
    for mesh_data in asset.get_all_meshes():
        if remove_degenerates:
            mesh_optimizer.remove_degenerate_triangles(mesh_data)
        
        if merge_verts:
            mesh_optimizer.merge_vertices(mesh_data)
        
        if decimate_ratio is not None and decimate_ratio < 1.0:
            mesh_optimizer.decimate(mesh_data, decimate_ratio)
    
    # Optimize textures
    if max_texture_size is not None:
        texture_optimizer = TextureOptimizer()
        
        for i, texture in enumerate(asset.textures):
            if texture.width > max_texture_size or texture.height > max_texture_size:
                asset.textures[i] = texture_optimizer.resize(texture, max_texture_size)
    
    return asset


__all__ = [
    "optimize_asset",
    "decimate_mesh",
    "merge_vertices",
    "remove_degenerate_triangles",
    "generate_lods",
    "optimize_textures",
    "resize_textures",
    "compress_textures",
]
