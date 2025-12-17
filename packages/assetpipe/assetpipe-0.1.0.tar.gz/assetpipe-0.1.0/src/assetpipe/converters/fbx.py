"""
FBX Converter - Load and save Autodesk FBX files

Note: Full FBX support requires the Autodesk FBX SDK.
This implementation provides basic support using trimesh as a fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Optional
import logging

import numpy as np

from assetpipe.converters.base import BaseConverter
from assetpipe.core.asset import Asset, AssetType, MeshData, Material

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class FbxConverter(BaseConverter):
    """
    Converter for Autodesk FBX format.
    
    FBX is the industry standard for 3D content exchange.
    Full support requires the Autodesk FBX SDK Python bindings.
    """
    
    format_id = "fbx"
    extensions = ["fbx"]
    format_name = "Autodesk FBX"
    can_load = True
    can_save = False  # FBX export requires SDK
    
    @classmethod
    def load(cls, path: Path) -> Asset:
        """Load an FBX file"""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Try to use FBX SDK first
        try:
            return cls._load_with_fbx_sdk(path)
        except ImportError:
            logger.debug("FBX SDK not available, falling back to trimesh")
        
        # Fallback to trimesh
        return cls._load_with_trimesh(path)
    
    @classmethod
    def _load_with_fbx_sdk(cls, path: Path) -> Asset:
        """Load FBX using Autodesk FBX SDK"""
        import fbx
        
        # Create SDK manager
        manager = fbx.FbxManager.Create()
        
        # Create IO settings
        ios = fbx.FbxIOSettings.Create(manager, fbx.IOSROOT)
        manager.SetIOSettings(ios)
        
        # Create importer
        importer = fbx.FbxImporter.Create(manager, "")
        
        if not importer.Initialize(str(path), -1, manager.GetIOSettings()):
            raise ValueError(f"Failed to initialize FBX importer: {importer.GetStatus().GetErrorString()}")
        
        # Create scene
        scene = fbx.FbxScene.Create(manager, "scene")
        importer.Import(scene)
        importer.Destroy()
        
        # Extract data
        asset = Asset(
            name=path.stem,
            type=AssetType.SCENE,
            source_path=path,
        )
        
        # Process nodes
        root = scene.GetRootNode()
        if root:
            cls._process_fbx_node(root, asset)
        
        # Cleanup
        manager.Destroy()
        
        return asset
    
    @classmethod
    def _process_fbx_node(cls, node, asset: Asset) -> None:
        """Process FBX node recursively"""
        import fbx
        
        # Get mesh attribute
        mesh_attr = node.GetNodeAttribute()
        if mesh_attr and mesh_attr.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
            mesh = mesh_attr
            mesh_data = cls._extract_fbx_mesh(mesh)
            
            if asset.mesh_data is None:
                asset.mesh_data = mesh_data
            else:
                child = Asset(
                    name=node.GetName() or f"mesh_{len(asset.children)}",
                    type=AssetType.MESH,
                    mesh_data=mesh_data,
                )
                asset.children.append(child)
        
        # Process children
        for i in range(node.GetChildCount()):
            cls._process_fbx_node(node.GetChild(i), asset)
    
    @classmethod
    def _extract_fbx_mesh(cls, mesh) -> MeshData:
        """Extract mesh data from FBX mesh"""
        import fbx
        
        # Get control points (vertices)
        control_points = mesh.GetControlPoints()
        vertices = np.array([
            [cp[0], cp[1], cp[2]] for cp in control_points
        ], dtype=np.float32)
        
        # Get polygon indices
        faces = []
        polygon_count = mesh.GetPolygonCount()
        
        for i in range(polygon_count):
            polygon_size = mesh.GetPolygonSize(i)
            
            if polygon_size == 3:
                # Triangle
                faces.append([
                    mesh.GetPolygonVertex(i, 0),
                    mesh.GetPolygonVertex(i, 1),
                    mesh.GetPolygonVertex(i, 2),
                ])
            elif polygon_size == 4:
                # Quad - split into two triangles
                faces.append([
                    mesh.GetPolygonVertex(i, 0),
                    mesh.GetPolygonVertex(i, 1),
                    mesh.GetPolygonVertex(i, 2),
                ])
                faces.append([
                    mesh.GetPolygonVertex(i, 0),
                    mesh.GetPolygonVertex(i, 2),
                    mesh.GetPolygonVertex(i, 3),
                ])
            else:
                # N-gon - fan triangulation
                for j in range(1, polygon_size - 1):
                    faces.append([
                        mesh.GetPolygonVertex(i, 0),
                        mesh.GetPolygonVertex(i, j),
                        mesh.GetPolygonVertex(i, j + 1),
                    ])
        
        faces_array = np.array(faces, dtype=np.int32)
        
        # Get normals
        normals = None
        normal_element = mesh.GetElementNormal()
        if normal_element:
            normals_list = []
            for i in range(len(control_points)):
                normal = normal_element.GetDirectArray().GetAt(i)
                normals_list.append([normal[0], normal[1], normal[2]])
            normals = np.array(normals_list, dtype=np.float32)
        
        # Get UVs
        uvs = None
        uv_element = mesh.GetElementUV()
        if uv_element:
            uvs_list = []
            for i in range(uv_element.GetDirectArray().GetCount()):
                uv = uv_element.GetDirectArray().GetAt(i)
                uvs_list.append([uv[0], uv[1]])
            uvs = np.array(uvs_list, dtype=np.float32)
        
        return MeshData(
            vertices=vertices,
            faces=faces_array,
            normals=normals,
            uvs=uvs,
        )
    
    @classmethod
    def _load_with_trimesh(cls, path: Path) -> Asset:
        """Load FBX using trimesh (fallback)"""
        import trimesh
        
        # Load with trimesh
        scene = trimesh.load(str(path), force='scene')
        
        asset = Asset(
            name=path.stem,
            type=AssetType.SCENE,
            source_path=path,
        )
        
        if isinstance(scene, trimesh.Scene):
            # Multiple meshes
            for name, geometry in scene.geometry.items():
                if isinstance(geometry, trimesh.Trimesh):
                    mesh_data = cls._trimesh_to_mesh_data(geometry)
                    
                    if asset.mesh_data is None:
                        asset.mesh_data = mesh_data
                        asset.type = AssetType.MESH
                    else:
                        child = Asset(
                            name=name,
                            type=AssetType.MESH,
                            mesh_data=mesh_data,
                        )
                        asset.children.append(child)
        
        elif isinstance(scene, trimesh.Trimesh):
            # Single mesh
            asset.mesh_data = cls._trimesh_to_mesh_data(scene)
            asset.type = AssetType.MESH
        
        return asset
    
    @classmethod
    def _trimesh_to_mesh_data(cls, mesh) -> MeshData:
        """Convert trimesh to MeshData"""
        import trimesh
        
        vertices = np.array(mesh.vertices, dtype=np.float32)
        faces = np.array(mesh.faces, dtype=np.int32)
        
        normals = None
        if hasattr(mesh, 'vertex_normals') and mesh.vertex_normals is not None:
            normals = np.array(mesh.vertex_normals, dtype=np.float32)
        
        uvs = None
        if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None:
            uvs = np.array(mesh.visual.uv, dtype=np.float32)
        
        return MeshData(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs,
        )
    
    @classmethod
    def save(cls, asset: Asset, path: Path) -> None:
        """Save asset as FBX (requires FBX SDK)"""
        raise NotImplementedError(
            "FBX export requires the Autodesk FBX SDK. "
            "Please export to glTF or OBJ format instead."
        )
