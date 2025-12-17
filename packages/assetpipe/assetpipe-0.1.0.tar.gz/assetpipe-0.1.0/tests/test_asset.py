"""
Tests for Asset core functionality
"""

import pytest
import numpy as np
from pathlib import Path

from assetpipe.core.asset import Asset, AssetType, MeshData, Material, Texture


class TestMeshData:
    """Tests for MeshData class"""
    
    def test_create_mesh_data(self):
        """Test creating basic mesh data"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        
        assert mesh.vertex_count == 3
        assert mesh.triangle_count == 1
        assert not mesh.has_uvs
        assert not mesh.has_normals
    
    def test_mesh_with_uvs_and_normals(self):
        """Test mesh with UVs and normals"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        uvs = np.array([
            [0, 0],
            [1, 0],
            [0, 1],
        ], dtype=np.float32)
        
        normals = np.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
        ], dtype=np.float32)
        
        mesh = MeshData(
            vertices=vertices,
            faces=faces,
            uvs=uvs,
            normals=normals,
        )
        
        assert mesh.has_uvs
        assert mesh.has_normals
    
    def test_compute_normals(self):
        """Test automatic normal computation"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        mesh.compute_normals()
        
        assert mesh.has_normals
        # Normal should point in +Z direction for this triangle
        assert np.allclose(mesh.normals[0], [0, 0, 1], atol=0.01)


class TestAsset:
    """Tests for Asset class"""
    
    def test_create_asset(self):
        """Test creating basic asset"""
        asset = Asset(
            name="test_asset",
            type=AssetType.MESH,
        )
        
        assert asset.name == "test_asset"
        assert asset.type == AssetType.MESH
        assert asset.mesh_data is None
        assert len(asset.materials) == 0
        assert len(asset.textures) == 0
    
    def test_asset_with_mesh(self):
        """Test asset with mesh data"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(
            name="test_mesh",
            type=AssetType.MESH,
            mesh_data=mesh,
        )
        
        assert asset.mesh_data is not None
        assert asset.mesh_data.vertex_count == 3
    
    def test_get_stats(self):
        """Test getting asset statistics"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],
            [1, 3, 2],
        ], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(
            name="test",
            type=AssetType.MESH,
            mesh_data=mesh,
            materials=[Material(name="mat1")],
        )
        
        stats = asset.get_stats()
        
        assert stats["vertices"] == 4
        assert stats["triangles"] == 2
        assert stats["material_count"] == 1
    
    def test_get_bounding_box(self):
        """Test bounding box calculation"""
        vertices = np.array([
            [-1, -2, -3],
            [1, 2, 3],
            [0, 0, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(
            name="test",
            type=AssetType.MESH,
            mesh_data=mesh,
        )
        
        bbox = asset.get_bounding_box()
        
        assert bbox is not None
        min_pt, max_pt = bbox
        assert np.allclose(min_pt, [-1, -2, -3])
        assert np.allclose(max_pt, [1, 2, 3])


class TestMaterial:
    """Tests for Material class"""
    
    def test_create_material(self):
        """Test creating material"""
        mat = Material(
            name="test_material",
            base_color=(1.0, 0.0, 0.0, 1.0),
            metallic=0.5,
            roughness=0.3,
        )
        
        assert mat.name == "test_material"
        assert mat.base_color == (1.0, 0.0, 0.0, 1.0)
        assert mat.metallic == 0.5
        assert mat.roughness == 0.3


class TestTexture:
    """Tests for Texture class"""
    
    def test_create_texture(self):
        """Test creating texture"""
        tex = Texture(
            name="test_texture",
            width=512,
            height=512,
            channels=4,
        )
        
        assert tex.name == "test_texture"
        assert tex.width == 512
        assert tex.height == 512
        assert tex.resolution == "512x512"
    
    def test_texture_with_data(self):
        """Test texture with pixel data"""
        data = np.zeros((256, 256, 4), dtype=np.uint8)
        
        tex = Texture(
            name="test",
            width=256,
            height=256,
            channels=4,
            data=data,
        )
        
        assert tex.size_bytes == 256 * 256 * 4
