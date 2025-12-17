"""
OBJ Converter - Load and save Wavefront OBJ files
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, List, Dict
import re

import numpy as np

from assetpipe.converters.base import BaseConverter
from assetpipe.core.asset import Asset, AssetType, MeshData, Material

if TYPE_CHECKING:
    pass


class ObjConverter(BaseConverter):
    """
    Converter for Wavefront OBJ format.
    
    OBJ is a simple, widely-supported text format for 3D geometry.
    """
    
    format_id = "obj"
    extensions = ["obj"]
    format_name = "Wavefront OBJ"
    can_load = True
    can_save = True
    
    @classmethod
    def load(cls, path: Path) -> Asset:
        """Load an OBJ file"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        vertices = []
        normals = []
        uvs = []
        faces = []
        face_normals = []
        face_uvs = []
        
        current_material = None
        materials: Dict[str, Material] = {}
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                
                if cmd == 'v':
                    # Vertex position
                    vertices.append([float(x) for x in parts[1:4]])
                
                elif cmd == 'vn':
                    # Vertex normal
                    normals.append([float(x) for x in parts[1:4]])
                
                elif cmd == 'vt':
                    # Texture coordinate
                    uv = [float(parts[1]), float(parts[2]) if len(parts) > 2 else 0.0]
                    uvs.append(uv)
                
                elif cmd == 'f':
                    # Face
                    face_verts = []
                    face_uvs_idx = []
                    face_normals_idx = []
                    
                    for vert in parts[1:]:
                        indices = vert.split('/')
                        
                        # Vertex index (1-based in OBJ)
                        v_idx = int(indices[0]) - 1
                        if v_idx < 0:
                            v_idx = len(vertices) + v_idx + 1
                        face_verts.append(v_idx)
                        
                        # UV index
                        if len(indices) > 1 and indices[1]:
                            uv_idx = int(indices[1]) - 1
                            if uv_idx < 0:
                                uv_idx = len(uvs) + uv_idx + 1
                            face_uvs_idx.append(uv_idx)
                        
                        # Normal index
                        if len(indices) > 2 and indices[2]:
                            n_idx = int(indices[2]) - 1
                            if n_idx < 0:
                                n_idx = len(normals) + n_idx + 1
                            face_normals_idx.append(n_idx)
                    
                    # Triangulate if needed (fan triangulation)
                    for i in range(1, len(face_verts) - 1):
                        faces.append([face_verts[0], face_verts[i], face_verts[i + 1]])
                        
                        if face_uvs_idx:
                            face_uvs.append([face_uvs_idx[0], face_uvs_idx[i], face_uvs_idx[i + 1]])
                        
                        if face_normals_idx:
                            face_normals.append([face_normals_idx[0], face_normals_idx[i], face_normals_idx[i + 1]])
                
                elif cmd == 'mtllib':
                    # Material library
                    mtl_path = path.parent / parts[1]
                    if mtl_path.exists():
                        materials = cls._load_mtl(mtl_path)
                
                elif cmd == 'usemtl':
                    # Use material
                    current_material = parts[1]
        
        # Convert to numpy arrays
        vertices_array = np.array(vertices, dtype=np.float32) if vertices else np.zeros((0, 3), dtype=np.float32)
        faces_array = np.array(faces, dtype=np.int32) if faces else np.zeros((0, 3), dtype=np.int32)
        
        normals_array = None
        if normals and face_normals:
            # Expand normals to per-vertex
            normals_array = np.array(normals, dtype=np.float32)
        
        uvs_array = None
        if uvs and face_uvs:
            uvs_array = np.array(uvs, dtype=np.float32)
        
        mesh_data = MeshData(
            vertices=vertices_array,
            faces=faces_array,
            normals=normals_array,
            uvs=uvs_array,
        )
        
        # Compute normals if not present
        if not mesh_data.has_normals and len(vertices_array) > 0:
            mesh_data.compute_normals()
        
        asset = Asset(
            name=path.stem,
            type=AssetType.MESH,
            source_path=path,
            mesh_data=mesh_data,
            materials=list(materials.values()),
        )
        
        return asset
    
    @classmethod
    def _load_mtl(cls, path: Path) -> Dict[str, Material]:
        """Load materials from MTL file"""
        materials = {}
        current_material = None
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                cmd = parts[0].lower()
                
                if cmd == 'newmtl':
                    name = parts[1] if len(parts) > 1 else "material"
                    current_material = Material(name=name)
                    materials[name] = current_material
                
                elif current_material:
                    if cmd == 'kd':
                        # Diffuse color
                        current_material.base_color = (
                            float(parts[1]),
                            float(parts[2]),
                            float(parts[3]),
                            1.0
                        )
                    elif cmd == 'ns':
                        # Specular exponent -> roughness
                        ns = float(parts[1])
                        current_material.roughness = 1.0 - min(ns / 1000.0, 1.0)
                    elif cmd == 'map_kd':
                        # Diffuse texture
                        current_material.base_color_texture = parts[1]
                    elif cmd == 'map_bump' or cmd == 'bump':
                        # Normal map
                        current_material.normal_texture = parts[-1]
        
        return materials
    
    @classmethod
    def save(cls, asset: Asset, path: Path) -> None:
        """Save asset as OBJ file"""
        path = Path(path)
        
        lines = []
        lines.append(f"# AssetPipe OBJ Export")
        lines.append(f"# {asset.name}")
        lines.append("")
        
        # Write MTL reference if we have materials
        if asset.materials:
            mtl_path = path.with_suffix(".mtl")
            lines.append(f"mtllib {mtl_path.name}")
            lines.append("")
            cls._save_mtl(asset.materials, mtl_path)
        
        vertex_offset = 1  # OBJ is 1-indexed
        normal_offset = 1
        uv_offset = 1
        
        all_meshes = asset.get_all_meshes()
        
        for mesh_idx, mesh_data in enumerate(all_meshes):
            if mesh_data is None:
                continue
            
            lines.append(f"o mesh_{mesh_idx}")
            
            # Vertices
            for v in mesh_data.vertices:
                lines.append(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")
            
            # Normals
            if mesh_data.has_normals:
                for n in mesh_data.normals:
                    lines.append(f"vn {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}")
            
            # UVs
            if mesh_data.has_uvs:
                for uv in mesh_data.uvs:
                    lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
            
            lines.append("")
            
            # Use first material if available
            if asset.materials:
                lines.append(f"usemtl {asset.materials[0].name}")
            
            # Faces
            for face in mesh_data.faces:
                face_str = "f"
                for v_idx in face:
                    v = v_idx + vertex_offset
                    
                    if mesh_data.has_uvs and mesh_data.has_normals:
                        face_str += f" {v}/{v_idx + uv_offset}/{v_idx + normal_offset}"
                    elif mesh_data.has_uvs:
                        face_str += f" {v}/{v_idx + uv_offset}"
                    elif mesh_data.has_normals:
                        face_str += f" {v}//{v_idx + normal_offset}"
                    else:
                        face_str += f" {v}"
                
                lines.append(face_str)
            
            # Update offsets for next mesh
            vertex_offset += len(mesh_data.vertices)
            if mesh_data.has_normals:
                normal_offset += len(mesh_data.normals)
            if mesh_data.has_uvs:
                uv_offset += len(mesh_data.uvs)
            
            lines.append("")
        
        # Write file
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    @classmethod
    def _save_mtl(cls, materials: List[Material], path: Path) -> None:
        """Save materials to MTL file"""
        lines = []
        lines.append("# AssetPipe MTL Export")
        lines.append("")
        
        for mat in materials:
            lines.append(f"newmtl {mat.name}")
            lines.append(f"Kd {mat.base_color[0]:.6f} {mat.base_color[1]:.6f} {mat.base_color[2]:.6f}")
            lines.append(f"Ns {(1.0 - mat.roughness) * 1000:.1f}")
            lines.append(f"d 1.0")
            lines.append(f"illum 2")
            
            if mat.base_color_texture:
                lines.append(f"map_Kd {mat.base_color_texture}")
            if mat.normal_texture:
                lines.append(f"map_bump {mat.normal_texture}")
            
            lines.append("")
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
