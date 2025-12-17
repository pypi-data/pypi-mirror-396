"""
glTF/GLB Converter - Load and save glTF 2.0 assets
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional, List
import struct
import json

import numpy as np
from pygltflib import GLTF2, BufferFormat, Accessor, BufferView, Buffer, Mesh, Primitive, Node, Scene

from assetpipe.converters.base import BaseConverter
from assetpipe.core.asset import Asset, AssetType, MeshData, Material, Texture

if TYPE_CHECKING:
    pass


class GltfConverter(BaseConverter):
    """
    Converter for glTF 2.0 and GLB formats.
    
    glTF is the "JPEG of 3D" - widely supported, efficient, and web-friendly.
    """
    
    format_id = "gltf"
    extensions = ["gltf", "glb"]
    format_name = "glTF 2.0"
    can_load = True
    can_save = True
    
    @classmethod
    def load(cls, path: Path) -> Asset:
        """Load a glTF/GLB file"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Load glTF
        gltf = GLTF2().load(str(path))
        
        # Convert to internal format
        asset = Asset(
            name=path.stem,
            type=AssetType.SCENE if len(gltf.meshes or []) > 1 else AssetType.MESH,
            source_path=path,
        )
        
        # Extract mesh data
        if gltf.meshes:
            for mesh in gltf.meshes:
                mesh_data = cls._extract_mesh(gltf, mesh)
                if mesh_data:
                    if asset.mesh_data is None:
                        asset.mesh_data = mesh_data
                    else:
                        # Create child asset for additional meshes
                        child = Asset(
                            name=mesh.name or f"mesh_{len(asset.children)}",
                            type=AssetType.MESH,
                            mesh_data=mesh_data,
                        )
                        asset.children.append(child)
        
        # Extract materials
        if gltf.materials:
            for mat in gltf.materials:
                material = cls._extract_material(gltf, mat)
                asset.materials.append(material)
        
        # Extract textures
        if gltf.textures:
            for i, tex in enumerate(gltf.textures):
                texture = cls._extract_texture(gltf, tex, i, path.parent)
                asset.textures.append(texture)
        
        return asset
    
    @classmethod
    def _extract_mesh(cls, gltf: GLTF2, mesh: Mesh) -> Optional[MeshData]:
        """Extract mesh data from glTF mesh"""
        if not mesh.primitives:
            return None
        
        # Get first primitive (most common case)
        primitive = mesh.primitives[0]
        
        vertices = None
        faces = None
        normals = None
        uvs = None
        
        # Extract vertices (POSITION)
        if primitive.attributes.POSITION is not None:
            vertices = cls._get_accessor_data(gltf, primitive.attributes.POSITION)
        
        # Extract indices
        if primitive.indices is not None:
            indices = cls._get_accessor_data(gltf, primitive.indices)
            if indices is not None:
                # Reshape to triangles
                faces = indices.reshape(-1, 3).astype(np.int32)
        
        # Extract normals
        if primitive.attributes.NORMAL is not None:
            normals = cls._get_accessor_data(gltf, primitive.attributes.NORMAL)
        
        # Extract UVs
        if primitive.attributes.TEXCOORD_0 is not None:
            uvs = cls._get_accessor_data(gltf, primitive.attributes.TEXCOORD_0)
        
        if vertices is None:
            return None
        
        # If no indices, create sequential faces
        if faces is None:
            num_verts = len(vertices)
            faces = np.arange(num_verts).reshape(-1, 3).astype(np.int32)
        
        return MeshData(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs,
        )
    
    @classmethod
    def _get_accessor_data(cls, gltf: GLTF2, accessor_index: int) -> Optional[np.ndarray]:
        """Get data from a glTF accessor"""
        if accessor_index is None or accessor_index >= len(gltf.accessors or []):
            return None
        
        accessor = gltf.accessors[accessor_index]
        buffer_view = gltf.bufferViews[accessor.bufferView]
        buffer = gltf.buffers[buffer_view.buffer]
        
        # Get buffer data
        if hasattr(gltf, '_glb_data') and gltf._glb_data:
            data = gltf._glb_data
        elif buffer.uri:
            # External buffer - would need to load from file
            return None
        else:
            return None
        
        # Calculate offsets
        byte_offset = (buffer_view.byteOffset or 0) + (accessor.byteOffset or 0)
        
        # Determine numpy dtype
        component_type_map = {
            5120: np.int8,
            5121: np.uint8,
            5122: np.int16,
            5123: np.uint16,
            5125: np.uint32,
            5126: np.float32,
        }
        dtype = component_type_map.get(accessor.componentType, np.float32)
        
        # Determine element size
        type_size_map = {
            "SCALAR": 1,
            "VEC2": 2,
            "VEC3": 3,
            "VEC4": 4,
            "MAT2": 4,
            "MAT3": 9,
            "MAT4": 16,
        }
        num_components = type_size_map.get(accessor.type, 1)
        
        # Extract data
        element_size = np.dtype(dtype).itemsize * num_components
        byte_length = accessor.count * element_size
        
        raw_data = data[byte_offset:byte_offset + byte_length]
        array = np.frombuffer(raw_data, dtype=dtype)
        
        if num_components > 1:
            array = array.reshape(-1, num_components)
        
        return array
    
    @classmethod
    def _extract_material(cls, gltf: GLTF2, mat) -> Material:
        """Extract material from glTF"""
        material = Material(name=mat.name or "material")
        
        if mat.pbrMetallicRoughness:
            pbr = mat.pbrMetallicRoughness
            
            if pbr.baseColorFactor:
                material.base_color = tuple(pbr.baseColorFactor)
            
            if pbr.metallicFactor is not None:
                material.metallic = pbr.metallicFactor
            
            if pbr.roughnessFactor is not None:
                material.roughness = pbr.roughnessFactor
            
            if pbr.baseColorTexture:
                material.base_color_texture = str(pbr.baseColorTexture.index)
        
        if mat.normalTexture:
            material.normal_texture = str(mat.normalTexture.index)
        
        if mat.emissiveFactor:
            material.emissive = tuple(mat.emissiveFactor)
        
        return material
    
    @classmethod
    def _extract_texture(cls, gltf: GLTF2, tex, index: int, base_path: Path) -> Texture:
        """Extract texture from glTF"""
        name = f"texture_{index}"
        
        if tex.source is not None and gltf.images:
            image = gltf.images[tex.source]
            if image.name:
                name = image.name
            elif image.uri:
                name = Path(image.uri).stem
        
        return Texture(name=name)
    
    @classmethod
    def save(cls, asset: Asset, path: Path) -> None:
        """Save asset as glTF/GLB"""
        path = Path(path)
        is_glb = path.suffix.lower() == ".glb"
        
        # Create glTF structure
        gltf = GLTF2()
        gltf.asset = {"version": "2.0", "generator": "AssetPipe"}
        
        # Collect all binary data
        binary_data = bytearray()
        
        # Add meshes
        gltf.meshes = []
        gltf.accessors = []
        gltf.bufferViews = []
        gltf.nodes = []
        
        all_meshes = asset.get_all_meshes()
        
        for i, mesh_data in enumerate(all_meshes):
            mesh, mesh_binary = cls._create_gltf_mesh(
                gltf, mesh_data, len(binary_data), i
            )
            gltf.meshes.append(mesh)
            binary_data.extend(mesh_binary)
            
            # Create node for mesh
            node = Node(mesh=i, name=f"node_{i}")
            gltf.nodes.append(node)
        
        # Create scene
        gltf.scenes = [Scene(nodes=list(range(len(gltf.nodes))))]
        gltf.scene = 0
        
        # Add materials
        if asset.materials:
            gltf.materials = []
            for mat in asset.materials:
                gltf_mat = cls._create_gltf_material(mat)
                gltf.materials.append(gltf_mat)
        
        # Create buffer
        if binary_data:
            if is_glb:
                gltf.buffers = [Buffer(byteLength=len(binary_data))]
                gltf._glb_data = bytes(binary_data)
            else:
                buffer_path = path.with_suffix(".bin")
                gltf.buffers = [Buffer(
                    byteLength=len(binary_data),
                    uri=buffer_path.name
                )]
                with open(buffer_path, "wb") as f:
                    f.write(binary_data)
        
        # Save
        if is_glb:
            gltf.save_binary(str(path))
        else:
            gltf.save_json(str(path))
    
    @classmethod
    def _create_gltf_mesh(
        cls,
        gltf: GLTF2,
        mesh_data: MeshData,
        buffer_offset: int,
        mesh_index: int,
    ) -> tuple:
        """Create glTF mesh from MeshData"""
        binary_data = bytearray()
        accessor_start = len(gltf.accessors)
        buffer_view_start = len(gltf.bufferViews)
        
        # Vertices
        vertices_bytes = mesh_data.vertices.astype(np.float32).tobytes()
        gltf.bufferViews.append(BufferView(
            buffer=0,
            byteOffset=buffer_offset + len(binary_data),
            byteLength=len(vertices_bytes),
            target=34962,  # ARRAY_BUFFER
        ))
        
        # Calculate bounds
        v_min = mesh_data.vertices.min(axis=0).tolist()
        v_max = mesh_data.vertices.max(axis=0).tolist()
        
        gltf.accessors.append(Accessor(
            bufferView=buffer_view_start,
            componentType=5126,  # FLOAT
            count=len(mesh_data.vertices),
            type="VEC3",
            max=v_max,
            min=v_min,
        ))
        binary_data.extend(vertices_bytes)
        
        # Indices
        indices_bytes = mesh_data.faces.flatten().astype(np.uint32).tobytes()
        gltf.bufferViews.append(BufferView(
            buffer=0,
            byteOffset=buffer_offset + len(binary_data),
            byteLength=len(indices_bytes),
            target=34963,  # ELEMENT_ARRAY_BUFFER
        ))
        gltf.accessors.append(Accessor(
            bufferView=buffer_view_start + 1,
            componentType=5125,  # UNSIGNED_INT
            count=len(mesh_data.faces) * 3,
            type="SCALAR",
        ))
        binary_data.extend(indices_bytes)
        
        # Normals (if present)
        normal_accessor = None
        if mesh_data.has_normals:
            normals_bytes = mesh_data.normals.astype(np.float32).tobytes()
            gltf.bufferViews.append(BufferView(
                buffer=0,
                byteOffset=buffer_offset + len(binary_data),
                byteLength=len(normals_bytes),
                target=34962,
            ))
            normal_accessor = len(gltf.accessors)
            gltf.accessors.append(Accessor(
                bufferView=len(gltf.bufferViews) - 1,
                componentType=5126,
                count=len(mesh_data.normals),
                type="VEC3",
            ))
            binary_data.extend(normals_bytes)
        
        # UVs (if present)
        uv_accessor = None
        if mesh_data.has_uvs:
            uvs_bytes = mesh_data.uvs.astype(np.float32).tobytes()
            gltf.bufferViews.append(BufferView(
                buffer=0,
                byteOffset=buffer_offset + len(binary_data),
                byteLength=len(uvs_bytes),
                target=34962,
            ))
            uv_accessor = len(gltf.accessors)
            gltf.accessors.append(Accessor(
                bufferView=len(gltf.bufferViews) - 1,
                componentType=5126,
                count=len(mesh_data.uvs),
                type="VEC2",
            ))
            binary_data.extend(uvs_bytes)
        
        # Create primitive
        attributes = {"POSITION": accessor_start}
        if normal_accessor is not None:
            attributes["NORMAL"] = normal_accessor
        if uv_accessor is not None:
            attributes["TEXCOORD_0"] = uv_accessor
        
        primitive = Primitive(
            attributes=attributes,
            indices=accessor_start + 1,
        )
        
        mesh = Mesh(
            name=f"mesh_{mesh_index}",
            primitives=[primitive],
        )
        
        return mesh, binary_data
    
    @classmethod
    def _create_gltf_material(cls, material: Material):
        """Create glTF material from Material"""
        from pygltflib import Material as GltfMaterial, PbrMetallicRoughness
        
        pbr = PbrMetallicRoughness(
            baseColorFactor=list(material.base_color),
            metallicFactor=material.metallic,
            roughnessFactor=material.roughness,
        )
        
        return GltfMaterial(
            name=material.name,
            pbrMetallicRoughness=pbr,
            emissiveFactor=list(material.emissive),
        )
