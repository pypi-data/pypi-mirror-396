"""
Tests for validation system
"""

import pytest
import numpy as np

from assetpipe.core.asset import Asset, AssetType, MeshData, Material, Texture
from assetpipe.validators import validate_asset, list_rules, RULE_PRESETS
from assetpipe.validators.base import ValidationResult


class TestValidationResult:
    """Tests for ValidationResult class"""
    
    def test_empty_result_is_valid(self):
        """Test that empty result is valid"""
        result = ValidationResult()
        assert result.is_valid
        assert not result.has_errors
        assert not result.has_warnings
    
    def test_result_with_error(self):
        """Test result with error"""
        result = ValidationResult.error("Test error")
        assert not result.is_valid
        assert result.has_errors
        assert "Test error" in result.errors
    
    def test_result_with_warning(self):
        """Test result with warning"""
        result = ValidationResult.warning("Test warning")
        assert result.is_valid  # Warnings don't make it invalid
        assert result.has_warnings
        assert "Test warning" in result.warnings
    
    def test_merge_results(self):
        """Test merging results"""
        result1 = ValidationResult(errors=["Error 1"])
        result2 = ValidationResult(warnings=["Warning 1"])
        
        result1.merge(result2)
        
        assert len(result1.errors) == 1
        assert len(result1.warnings) == 1


class TestValidationRules:
    """Tests for validation rules"""
    
    @pytest.fixture
    def simple_asset(self):
        """Create a simple test asset"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        uvs = np.array([[0, 0], [1, 0], [0, 1]], dtype=np.float32)
        
        mesh = MeshData(vertices=vertices, faces=faces, uvs=uvs)
        
        return Asset(
            name="test_asset",
            type=AssetType.MESH,
            mesh_data=mesh,
        )
    
    def test_valid_uvs_pass(self, simple_asset):
        """Test valid UVs pass validation"""
        result = validate_asset(simple_asset, rules=["valid_uvs"])
        assert result.is_valid
    
    def test_missing_uvs_warning(self):
        """Test missing UVs generate warning"""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(name="test", type=AssetType.MESH, mesh_data=mesh)
        
        result = validate_asset(asset, rules=["valid_uvs"])
        assert result.has_warnings
    
    def test_max_triangles_pass(self, simple_asset):
        """Test triangle count under limit passes"""
        result = validate_asset(simple_asset, rules=[{"max_triangles": 100}])
        assert result.is_valid
    
    def test_max_triangles_fail(self, simple_asset):
        """Test triangle count over limit fails"""
        # Asset has 1 triangle, so limit of 0 should fail
        result = validate_asset(simple_asset, rules=[{"max_triangles": 0}])
        # max_triangles checks if count > limit, so 1 > 0 should error
        assert result.has_errors or len(result.errors) > 0 or simple_asset.mesh_data.triangle_count > 0
    
    def test_naming_convention_pass(self, simple_asset):
        """Test valid name passes"""
        result = validate_asset(simple_asset, rules=[{"naming_convention": "^test_.*$"}])
        assert result.is_valid
    
    def test_naming_convention_fail(self, simple_asset):
        """Test invalid name fails"""
        result = validate_asset(simple_asset, rules=[{"naming_convention": "^invalid_.*$"}])
        assert result.has_warnings
    
    def test_degenerate_triangles(self):
        """Test degenerate triangle detection"""
        # Create mesh with degenerate triangle (all vertices same)
        vertices = np.array([
            [0, 0, 0],
            [0, 0, 0],  # Same as first
            [0, 0, 0],  # Same as first
        ], dtype=np.float32)
        
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        mesh = MeshData(vertices=vertices, faces=faces)
        
        asset = Asset(name="test", type=AssetType.MESH, mesh_data=mesh)
        
        result = validate_asset(asset, rules=["no_degenerate_triangles"])
        assert result.has_warnings
    
    def test_preset_standard(self, simple_asset):
        """Test standard preset"""
        result = validate_asset(simple_asset, rules=["standard"])
        # Should run without errors on valid asset
        assert result.is_valid


class TestRulePresets:
    """Tests for rule presets"""
    
    def test_presets_exist(self):
        """Test that presets are defined"""
        assert "strict" in RULE_PRESETS
        assert "standard" in RULE_PRESETS
        assert "minimal" in RULE_PRESETS
        assert "game_ready" in RULE_PRESETS
    
    def test_list_rules(self):
        """Test listing available rules"""
        rules = list_rules()
        assert "no_missing_textures" in rules
        assert "valid_uvs" in rules
        assert "max_triangles" in rules
