"""
Asset - Core asset representation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any
import numpy as np


class AssetType(Enum):
    """Supported asset types"""
    MESH = "mesh"
    TEXTURE = "texture"
    MATERIAL = "material"
    SCENE = "scene"
    ANIMATION = "animation"
    UNKNOWN = "unknown"


@dataclass
class MeshData:
    """Mesh geometry data"""
    vertices: np.ndarray
    faces: np.ndarray
    normals: Optional[np.ndarray] = None
    uvs: Optional[np.ndarray] = None
    vertex_colors: Optional[np.ndarray] = None
    
    @property
    def vertex_count(self) -> int:
        return len(self.vertices)
    
    @property
    def triangle_count(self) -> int:
        return len(self.faces)
    
    @property
    def has_uvs(self) -> bool:
        return self.uvs is not None and len(self.uvs) > 0
    
    @property
    def has_normals(self) -> bool:
        return self.normals is not None and len(self.normals) > 0
    
    def compute_normals(self) -> None:
        """Compute vertex normals from faces"""
        if self.vertices is None or self.faces is None:
            return
        
        normals = np.zeros_like(self.vertices)
        
        for face in self.faces:
            v0, v1, v2 = self.vertices[face]
            normal = np.cross(v1 - v0, v2 - v0)
            norm = np.linalg.norm(normal)
            if norm > 0:
                normal = normal / norm
            normals[face] += normal
        
        # Normalize
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0] = 1
        self.normals = normals / norms


@dataclass
class Texture:
    """Texture data"""
    name: str
    path: Optional[Path] = None
    width: int = 0
    height: int = 0
    channels: int = 4
    data: Optional[np.ndarray] = None
    format: str = "png"
    
    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return ""
    
    @property
    def size_bytes(self) -> int:
        if self.data is not None:
            return self.data.nbytes
        return 0


@dataclass
class Material:
    """Material definition"""
    name: str
    base_color: tuple = (0.8, 0.8, 0.8, 1.0)
    metallic: float = 0.0
    roughness: float = 0.5
    emissive: tuple = (0.0, 0.0, 0.0)
    
    # Texture references
    base_color_texture: Optional[str] = None
    normal_texture: Optional[str] = None
    metallic_roughness_texture: Optional[str] = None
    emissive_texture: Optional[str] = None
    occlusion_texture: Optional[str] = None
    
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Asset:
    """
    Universal asset representation.
    Can hold mesh data, textures, materials, and metadata.
    """
    name: str
    type: AssetType
    source_path: Optional[Path] = None
    
    # Geometry
    mesh_data: Optional[MeshData] = None
    
    # Materials and textures
    materials: List[Material] = field(default_factory=list)
    textures: List[Texture] = field(default_factory=list)
    
    # Scene hierarchy (for complex assets)
    children: List["Asset"] = field(default_factory=list)
    transform: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def load(cls, path: Path) -> "Asset":
        """Load an asset from file"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Asset not found: {path}")
        
        suffix = path.suffix.lower()
        
        # Import the appropriate loader
        if suffix in ['.gltf', '.glb']:
            from assetpipe.converters.gltf import GltfConverter
            return GltfConverter.load(path)
        elif suffix == '.obj':
            from assetpipe.converters.obj import ObjConverter
            return ObjConverter.load(path)
        elif suffix == '.fbx':
            from assetpipe.converters.fbx import FbxConverter
            return FbxConverter.load(path)
        elif suffix in ['.png', '.jpg', '.jpeg', '.tga', '.bmp']:
            from assetpipe.converters.texture import TextureConverter
            return TextureConverter.load(path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")
    
    def save(self, path: Path) -> None:
        """Save asset to file"""
        path = Path(path)
        suffix = path.suffix.lower()
        
        if suffix in ['.gltf', '.glb']:
            from assetpipe.converters.gltf import GltfConverter
            GltfConverter.save(self, path)
        elif suffix == '.obj':
            from assetpipe.converters.obj import ObjConverter
            ObjConverter.save(self, path)
        else:
            raise ValueError(f"Unsupported output format: {suffix}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get asset statistics"""
        stats = {
            "name": self.name,
            "type": self.type.value,
        }
        
        if self.mesh_data:
            stats["vertices"] = self.mesh_data.vertex_count
            stats["triangles"] = self.mesh_data.triangle_count
            stats["has_uvs"] = self.mesh_data.has_uvs
            stats["has_normals"] = self.mesh_data.has_normals
        
        stats["material_count"] = len(self.materials)
        stats["texture_count"] = len(self.textures)
        stats["child_count"] = len(self.children)
        
        return stats
    
    def get_all_meshes(self) -> List[MeshData]:
        """Get all mesh data including from children"""
        meshes = []
        if self.mesh_data:
            meshes.append(self.mesh_data)
        for child in self.children:
            meshes.extend(child.get_all_meshes())
        return meshes
    
    def get_all_textures(self) -> List[Texture]:
        """Get all textures including from children"""
        textures = list(self.textures)
        for child in self.children:
            textures.extend(child.get_all_textures())
        return textures
    
    def get_bounding_box(self) -> Optional[tuple]:
        """Calculate bounding box of all geometry"""
        all_vertices = []
        for mesh in self.get_all_meshes():
            if mesh.vertices is not None:
                all_vertices.append(mesh.vertices)
        
        if not all_vertices:
            return None
        
        combined = np.vstack(all_vertices)
        return (combined.min(axis=0), combined.max(axis=0))
    
    def __repr__(self) -> str:
        stats = self.get_stats()
        return f"Asset(name='{self.name}', type={self.type.value}, triangles={stats.get('triangles', 0)})"
