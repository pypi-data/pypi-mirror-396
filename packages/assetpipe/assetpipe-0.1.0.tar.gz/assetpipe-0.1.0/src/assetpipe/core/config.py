"""
Pipeline Configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import os

import yaml
from pydantic import BaseModel, Field


class MeshOptimizationConfig(BaseModel):
    """Mesh optimization settings"""
    decimate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Decimation ratio")
    generate_lods: Optional[List[float]] = Field(None, description="LOD levels to generate")
    merge_vertices: bool = Field(True, description="Merge duplicate vertices")
    remove_degenerates: bool = Field(True, description="Remove degenerate triangles")


class TextureOptimizationConfig(BaseModel):
    """Texture optimization settings"""
    max_size: int = Field(4096, description="Maximum texture dimension")
    format: str = Field("png", description="Output format")
    quality: int = Field(85, ge=1, le=100, description="Compression quality")
    generate_mipmaps: bool = Field(False, description="Generate mipmaps")


class OptimizationConfig(BaseModel):
    """Combined optimization settings"""
    mesh: MeshOptimizationConfig = Field(default_factory=MeshOptimizationConfig)
    textures: TextureOptimizationConfig = Field(default_factory=TextureOptimizationConfig)


class ValidationRule(BaseModel):
    """Single validation rule"""
    name: str
    enabled: bool = True
    params: Dict[str, Any] = Field(default_factory=dict)


class ValidationConfig(BaseModel):
    """Validation settings"""
    rules: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    fail_on_warning: bool = False
    
    def get_rules(self) -> List[ValidationRule]:
        """Parse rules into ValidationRule objects"""
        parsed = []
        for rule in self.rules:
            if isinstance(rule, str):
                parsed.append(ValidationRule(name=rule))
            elif isinstance(rule, dict):
                for name, params in rule.items():
                    if isinstance(params, dict):
                        parsed.append(ValidationRule(name=name, params=params))
                    else:
                        parsed.append(ValidationRule(name=name, params={"value": params}))
        return parsed


class NotificationConfig(BaseModel):
    """Notification settings"""
    slack: Optional[Dict[str, Any]] = None
    discord: Optional[Dict[str, Any]] = None
    email: Optional[Dict[str, Any]] = None


class InputConfig(BaseModel):
    """Input configuration"""
    formats: List[str] = Field(default_factory=lambda: ["fbx", "obj", "gltf", "glb"])
    recursive: bool = True
    exclude_patterns: List[str] = Field(default_factory=list)


class OutputConfig(BaseModel):
    """Output configuration"""
    format: str = "gltf"
    directory: Optional[str] = None
    naming: str = "{name}.{ext}"  # Supports {name}, {ext}, {date}, {hash}
    overwrite: bool = False


class PluginConfig(BaseModel):
    """Plugin configuration"""
    path: str
    enabled: bool = True
    config: Dict[str, Any] = Field(default_factory=dict)


class PipelineConfig(BaseModel):
    """
    Complete pipeline configuration.
    Loaded from YAML file.
    """
    version: int = 1
    name: str = "default"
    
    input: InputConfig = Field(default_factory=InputConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    optimization: OptimizationConfig = Field(default_factory=OptimizationConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    notifications: NotificationConfig = Field(default_factory=NotificationConfig)
    plugins: List[PluginConfig] = Field(default_factory=list)
    
    # Custom variables
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    def resolve_env_vars(self) -> None:
        """Resolve environment variables in config values"""
        def resolve(value: Any) -> Any:
            if isinstance(value, str) and value.startswith("$"):
                env_var = value[1:]
                return os.environ.get(env_var, value)
            elif isinstance(value, dict):
                return {k: resolve(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve(v) for v in value]
            return value
        
        # Resolve in notifications
        if self.notifications.slack:
            self.notifications.slack = resolve(self.notifications.slack)
        if self.notifications.discord:
            self.notifications.discord = resolve(self.notifications.discord)


def load_config(path: Path) -> PipelineConfig:
    """Load pipeline configuration from YAML file"""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    config = PipelineConfig(**data)
    config.resolve_env_vars()
    
    return config


def save_config(config: PipelineConfig, path: Path) -> None:
    """Save pipeline configuration to YAML file"""
    path = Path(path)
    
    with open(path, 'w') as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)


# Default configurations for common use cases
DEFAULT_CONFIGS = {
    "strict": PipelineConfig(
        name="strict",
        validation=ValidationConfig(
            rules=[
                "no_missing_textures",
                "valid_uvs",
                "no_degenerate_triangles",
                {"max_triangles": 100000},
                {"naming_convention": "^[a-z][a-z0-9_]*$"},
            ],
            fail_on_warning=True,
        ),
    ),
    "game_ready": PipelineConfig(
        name="game_ready",
        output=OutputConfig(format="glb"),
        optimization=OptimizationConfig(
            mesh=MeshOptimizationConfig(
                decimate=0.75,
                generate_lods=[1.0, 0.5, 0.25],
                merge_vertices=True,
            ),
            textures=TextureOptimizationConfig(
                max_size=2048,
                format="webp",
                quality=85,
            ),
        ),
        validation=ValidationConfig(
            rules=[
                "no_missing_textures",
                "valid_uvs",
                {"max_triangles": 50000},
            ],
        ),
    ),
    "archviz": PipelineConfig(
        name="archviz",
        output=OutputConfig(format="gltf"),
        optimization=OptimizationConfig(
            textures=TextureOptimizationConfig(
                max_size=4096,
                format="png",
                quality=95,
            ),
        ),
        validation=ValidationConfig(
            rules=[
                "no_missing_textures",
                "valid_uvs",
                "correct_scale",
            ],
        ),
    ),
}


def get_default_config(name: str) -> PipelineConfig:
    """Get a default configuration by name"""
    if name not in DEFAULT_CONFIGS:
        raise ValueError(f"Unknown default config: {name}. Available: {list(DEFAULT_CONFIGS.keys())}")
    return DEFAULT_CONFIGS[name].model_copy(deep=True)
