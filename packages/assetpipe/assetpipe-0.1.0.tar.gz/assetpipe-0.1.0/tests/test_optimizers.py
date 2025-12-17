"""
Tests for optimization functionality
"""

import pytest
import numpy as np

from assetpipe.core.asset import Asset, AssetType, MeshData, Texture
from assetpipe.optimizers import optimize_asset
from assetpipe.optimizers.mesh import MeshOptimizer
from assetpipe.optimizers.texture import TextureOptimizer


class TestMeshOptimizer:
    """Tests for mesh optimization"""
    
    @pytest.fixture
    def cube_mesh(self):
        """Create a simple cube mesh"""
        # 8 vertices of a unit cube
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
        ], dtype=np.float32)
        
        # 12 triangles (2 per face)
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # Front
            [4, 6, 5], [4, 7, 6],  # Back
            [0, 4, 5], [0, 5, 1],  # Bottom
            [2, 6, 7], [2, 7, 3],  # Top
            [0, 3, 7], [0, 7, 4],  # Left
            [1, 5, 6], [1, 6, 2],  # Right
        ], dtype=np.int32)
        
        return MeshData(vertices=vertices, faces=faces)
    
    def test_merge_vertices(self, cube_mesh):
        """Test vertex merging"""
        optimizer = MeshOptimizer()
        
        # Add duplicate vertices
        cube_mesh.vertices = np.vstack([
            cube_mesh.vertices,
            cube_mesh.vertices[0:1],  # Duplicate first vertex
        ])
        
        original_count = len(cube_mesh.vertices)
        removed = optimizer.merge_vertices(cube_mesh)
        
        assert removed >= 1
        assert len(cube_mesh.vertices) < original_count
    
    def test_remove_degenerate_triangles(self):
        """Test degenerate triangle removal"""
        # Create mesh with one good and one degenerate triangle
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 0],  # Same as vertex 0
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],  # Good triangle
            [0, 3, 3],  # Degenerate (duplicate indices)
        ], dtype=np.int32)
        
        mesh = MeshData(vertices=vertices, faces=faces)
        
        optimizer = MeshOptimizer()
        removed = optimizer.remove_degenerate_triangles(mesh)
        
        assert removed >= 1
        assert len(mesh.faces) == 1
    
    def test_center_mesh(self, cube_mesh):
        """Test mesh centering"""
        optimizer = MeshOptimizer()
        
        # Offset the mesh
        cube_mesh.vertices += np.array([10, 20, 30])
        
        offset = optimizer.center_mesh(cube_mesh)
        
        # Check that mesh is now centered
        center = cube_mesh.vertices.mean(axis=0)
        assert np.allclose(center, [0, 0, 0], atol=0.01)
    
    def test_normalize_scale(self, cube_mesh):
        """Test scale normalization"""
        optimizer = MeshOptimizer()
        
        # Scale up the mesh
        cube_mesh.vertices *= 100
        
        scale = optimizer.normalize_scale(cube_mesh, target_size=1.0)
        
        # Check that mesh fits in unit cube
        min_v = cube_mesh.vertices.min(axis=0)
        max_v = cube_mesh.vertices.max(axis=0)
        size = np.max(max_v - min_v)
        
        assert np.isclose(size, 1.0, atol=0.01)
    
    def test_compute_normals(self, cube_mesh):
        """Test normal computation"""
        optimizer = MeshOptimizer()
        
        assert cube_mesh.normals is None
        
        optimizer.compute_vertex_normals(cube_mesh)
        
        assert cube_mesh.normals is not None
        assert len(cube_mesh.normals) == len(cube_mesh.vertices)
        
        # Check normals are unit length
        norms = np.linalg.norm(cube_mesh.normals, axis=1)
        assert np.allclose(norms, 1.0, atol=0.01)


class TestTextureOptimizer:
    """Tests for texture optimization"""
    
    @pytest.fixture
    def test_texture(self):
        """Create a test texture"""
        data = np.random.randint(0, 255, (512, 512, 4), dtype=np.uint8)
        return Texture(
            name="test_texture",
            width=512,
            height=512,
            channels=4,
            data=data,
            format="png",
        )
    
    def test_resize_texture(self, test_texture):
        """Test texture resizing"""
        optimizer = TextureOptimizer()
        
        resized = optimizer.resize(test_texture, max_size=256)
        
        assert resized.width == 256
        assert resized.height == 256
    
    def test_resize_maintains_aspect(self):
        """Test that resize maintains aspect ratio"""
        data = np.random.randint(0, 255, (256, 512, 4), dtype=np.uint8)
        texture = Texture(
            name="test",
            width=512,
            height=256,
            channels=4,
            data=data,
        )
        
        optimizer = TextureOptimizer()
        resized = optimizer.resize(texture, max_size=256)
        
        # Should be 256x128 to maintain 2:1 aspect
        assert resized.width == 256
        assert resized.height == 128
    
    def test_no_resize_if_smaller(self, test_texture):
        """Test that smaller textures aren't resized"""
        optimizer = TextureOptimizer()
        
        resized = optimizer.resize(test_texture, max_size=1024)
        
        # Should return same texture
        assert resized.width == 512
        assert resized.height == 512
    
    def test_compress_webp(self, test_texture):
        """Test WebP compression"""
        optimizer = TextureOptimizer()
        
        compressed = optimizer.compress(test_texture, format="webp", quality=80)
        
        assert isinstance(compressed, bytes)
        assert len(compressed) > 0
        # WebP should be smaller than raw
        assert len(compressed) < test_texture.size_bytes
    
    def test_generate_mipmaps(self, test_texture):
        """Test mipmap generation"""
        optimizer = TextureOptimizer()
        
        mipmaps = optimizer.generate_mipmaps(test_texture)
        
        assert len(mipmaps) > 1
        assert mipmaps[0].width == 512
        assert mipmaps[1].width == 256
        assert mipmaps[2].width == 128
    
    def test_power_of_two(self):
        """Test power-of-two conversion"""
        data = np.random.randint(0, 255, (300, 500, 4), dtype=np.uint8)
        texture = Texture(
            name="test",
            width=500,
            height=300,
            channels=4,
            data=data,
        )
        
        optimizer = TextureOptimizer()
        pot = optimizer.make_power_of_two(texture, round_up=True)
        
        assert pot.width == 512
        assert pot.height == 512


class TestOptimizeAsset:
    """Tests for the optimize_asset function"""
    
    def test_optimize_asset_basic(self):
        """Test basic asset optimization"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0],
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(
            name="test",
            type=AssetType.MESH,
            mesh_data=mesh,
        )
        
        optimized = optimize_asset(asset, merge_verts=True, remove_degenerates=True)
        
        assert optimized is not None
        assert optimized.mesh_data is not None
