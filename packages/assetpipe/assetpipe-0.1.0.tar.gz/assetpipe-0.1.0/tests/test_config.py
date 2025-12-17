"""
Tests for configuration system
"""

import pytest
from pathlib import Path
import tempfile

from assetpipe.core.config import (
    PipelineConfig,
    load_config,
    save_config,
    get_default_config,
    DEFAULT_CONFIGS,
)


class TestPipelineConfig:
    """Tests for PipelineConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = PipelineConfig()
        
        assert config.version == 1
        assert config.name == "default"
        assert "fbx" in config.input.formats
        assert config.output.format == "gltf"
    
    def test_config_with_custom_values(self):
        """Test configuration with custom values"""
        config = PipelineConfig(
            name="custom",
            output={"format": "glb", "directory": "./output"},
            optimization={
                "mesh": {"decimate": 0.5},
                "textures": {"max_size": 1024},
            },
        )
        
        assert config.name == "custom"
        assert config.output.format == "glb"
        assert config.optimization.mesh.decimate == 0.5
        assert config.optimization.textures.max_size == 1024
    
    def test_validation_rules_parsing(self):
        """Test parsing validation rules"""
        config = PipelineConfig(
            validation={
                "rules": [
                    "no_missing_textures",
                    {"max_triangles": 50000},
                    {"naming_convention": "^[a-z]+$"},
                ],
            },
        )
        
        rules = config.validation.get_rules()
        
        assert len(rules) == 3
        assert rules[0].name == "no_missing_textures"
        assert rules[1].name == "max_triangles"
        assert rules[1].params == {"value": 50000}


class TestConfigIO:
    """Tests for config loading and saving"""
    
    def test_save_and_load_config(self):
        """Test round-trip save and load"""
        config = PipelineConfig(
            name="test_config",
            output={"format": "glb"},
            validation={"rules": ["valid_uvs"]},
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "pipeline.yaml"
            
            save_config(config, config_path)
            
            assert config_path.exists()
            
            loaded = load_config(config_path)
            
            assert loaded.name == "test_config"
            assert loaded.output.format == "glb"
            assert "valid_uvs" in loaded.validation.rules
    
    def test_load_nonexistent_config(self):
        """Test loading non-existent config raises error"""
        with pytest.raises(FileNotFoundError):
            load_config(Path("/nonexistent/config.yaml"))


class TestDefaultConfigs:
    """Tests for default configurations"""
    
    def test_default_configs_exist(self):
        """Test that default configs are defined"""
        assert "strict" in DEFAULT_CONFIGS
        assert "game_ready" in DEFAULT_CONFIGS
        assert "archviz" in DEFAULT_CONFIGS
    
    def test_get_default_config(self):
        """Test getting default config by name"""
        config = get_default_config("strict")
        
        assert config is not None
        assert config.name == "strict"
        assert config.validation.fail_on_warning is True
    
    def test_get_unknown_config_raises(self):
        """Test getting unknown config raises error"""
        with pytest.raises(ValueError):
            get_default_config("nonexistent")
    
    def test_game_ready_config(self):
        """Test game_ready preset"""
        config = get_default_config("game_ready")
        
        assert config.output.format == "glb"
        assert config.optimization.mesh.decimate == 0.75
        assert config.optimization.textures.max_size == 2048
