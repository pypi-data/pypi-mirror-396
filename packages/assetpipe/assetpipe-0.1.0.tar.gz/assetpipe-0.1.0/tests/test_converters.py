"""
Tests for format converters
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from assetpipe.core.asset import Asset, AssetType, MeshData, Material
from assetpipe.converters import get_converter, list_converters, can_convert
from assetpipe.converters.obj import ObjConverter
from assetpipe.converters.gltf import GltfConverter


class TestConverterRegistry:
    """Tests for converter registry"""
    
    def test_list_converters(self):
        """Test listing available converters"""
        converters = list_converters()
        assert "gltf" in converters
        assert "glb" in converters
        assert "obj" in converters
        assert "fbx" in converters
    
    def test_get_converter(self):
        """Test getting converter by format"""
        converter = get_converter(AssetType.MESH, "gltf")
        assert converter is not None
        assert isinstance(converter, GltfConverter)
    
    def test_can_convert(self):
        """Test conversion capability check"""
        assert can_convert("obj", "gltf")
        assert can_convert("fbx", "glb")
        assert not can_convert("xyz", "gltf")


class TestObjConverter:
    """Tests for OBJ converter"""
    
    @pytest.fixture
    def simple_asset(self):
        """Create a simple test asset"""
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
        
        uvs = np.array([
            [0, 0], [1, 0], [0, 1], [1, 1],
        ], dtype=np.float32)
        
        normals = np.array([
            [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
        ], dtype=np.float32)
        
        mesh = MeshData(
            vertices=vertices,
            faces=faces,
            uvs=uvs,
            normals=normals,
        )
        
        return Asset(
            name="test_quad",
            type=AssetType.MESH,
            mesh_data=mesh,
            materials=[Material(name="default")],
        )
    
    def test_save_obj(self, simple_asset):
        """Test saving to OBJ format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.obj"
            
            ObjConverter.save(simple_asset, output_path)
            
            assert output_path.exists()
            
            # Check content
            content = output_path.read_text()
            assert "v " in content  # Has vertices
            assert "f " in content  # Has faces
            assert "vn " in content  # Has normals
            assert "vt " in content  # Has UVs
    
    def test_save_and_load_obj(self, simple_asset):
        """Test round-trip save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.obj"
            
            # Save
            ObjConverter.save(simple_asset, output_path)
            
            # Load
            loaded = ObjConverter.load(output_path)
            
            assert loaded is not None
            assert loaded.mesh_data is not None
            assert loaded.mesh_data.vertex_count == 4
            assert loaded.mesh_data.triangle_count == 2


class TestGltfConverter:
    """Tests for glTF converter"""
    
    @pytest.fixture
    def simple_asset(self):
        """Create a simple test asset"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        
        return Asset(
            name="test_triangle",
            type=AssetType.MESH,
            mesh_data=mesh,
        )
    
    def test_save_gltf(self, simple_asset):
        """Test saving to glTF format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.gltf"
            
            GltfConverter.save(simple_asset, output_path)
            
            assert output_path.exists()
            
            # Should also create .bin file
            bin_path = output_path.with_suffix(".bin")
            assert bin_path.exists()
    
    def test_save_glb(self, simple_asset):
        """Test saving to GLB format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.glb"
            
            GltfConverter.save(simple_asset, output_path)
            
            assert output_path.exists()
            
            # GLB is binary, should have reasonable size
            assert output_path.stat().st_size > 100


class TestTextureConverter:
    """Tests for texture converter"""
    
    def test_save_and_load_png(self):
        """Test PNG round-trip"""
        from assetpipe.converters.texture import TextureConverter
        from assetpipe.core.asset import Texture
        
        # Create test texture
        data = np.random.randint(0, 255, (64, 64, 4), dtype=np.uint8)
        texture = Texture(
            name="test",
            width=64,
            height=64,
            channels=4,
            data=data,
            format="png",
        )
        
        asset = Asset(
            name="test_texture",
            type=AssetType.TEXTURE,
            textures=[texture],
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test.png"
            
            TextureConverter.save(asset, output_path)
            
            assert output_path.exists()
            
            # Load back
            loaded = TextureConverter.load(output_path)
            
            assert loaded is not None
            assert len(loaded.textures) == 1
            assert loaded.textures[0].width == 64
            assert loaded.textures[0].height == 64
