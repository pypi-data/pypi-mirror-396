"""
Built-in Validation Rules
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np

from assetpipe.validators.base import ValidationRule, ValidationResult

if TYPE_CHECKING:
    from assetpipe.core.asset import Asset


class NoMissingTexturesRule(ValidationRule):
    """Check that all referenced textures exist"""
    
    name = "no_missing_textures"
    description = "Ensures all material texture references point to existing textures"
    has_params = False
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        # Get all texture names
        texture_names = {tex.name for tex in asset.get_all_textures()}
        
        # Check material references
        for material in asset.materials:
            for tex_ref in [
                material.base_color_texture,
                material.normal_texture,
                material.metallic_roughness_texture,
                material.emissive_texture,
                material.occlusion_texture,
            ]:
                if tex_ref and tex_ref not in texture_names:
                    # Check if it's an index reference
                    try:
                        idx = int(tex_ref)
                        if idx >= len(asset.textures):
                            result.add_error(
                                f"Material '{material.name}' references missing texture index: {tex_ref}"
                            )
                    except ValueError:
                        result.add_warning(
                            f"Material '{material.name}' references texture not in asset: {tex_ref}"
                        )
        
        return result


class ValidUVsRule(ValidationRule):
    """Check that UV coordinates are valid"""
    
    name = "valid_uvs"
    description = "Ensures UV coordinates are present and within valid range"
    has_params = False
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        for mesh in asset.get_all_meshes():
            if not mesh.has_uvs:
                result.add_warning("Mesh has no UV coordinates")
                continue
            
            # Check for NaN or Inf
            if np.any(np.isnan(mesh.uvs)) or np.any(np.isinf(mesh.uvs)):
                result.add_error("UV coordinates contain NaN or Inf values")
            
            # Check range (warn if outside 0-1, but not an error)
            if np.any(mesh.uvs < -10) or np.any(mesh.uvs > 10):
                result.add_warning("UV coordinates significantly outside 0-1 range")
        
        return result


class NoDegenerateTrianglesRule(ValidationRule):
    """Check for degenerate (zero-area) triangles"""
    
    name = "no_degenerate_triangles"
    description = "Ensures no triangles have zero area"
    has_params = False
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        for mesh in asset.get_all_meshes():
            if mesh.vertices is None or mesh.faces is None:
                continue
            
            degenerate_count = 0
            
            for face in mesh.faces:
                if len(face) < 3:
                    degenerate_count += 1
                    continue
                
                v0 = mesh.vertices[face[0]]
                v1 = mesh.vertices[face[1]]
                v2 = mesh.vertices[face[2]]
                
                # Calculate area using cross product
                edge1 = v1 - v0
                edge2 = v2 - v0
                cross = np.cross(edge1, edge2)
                area = np.linalg.norm(cross) / 2
                
                if area < 1e-10:
                    degenerate_count += 1
            
            if degenerate_count > 0:
                result.add_warning(
                    f"Mesh contains {degenerate_count} degenerate triangles"
                )
        
        return result


class MaxTrianglesRule(ValidationRule):
    """Check that triangle count is within limit"""
    
    name = "max_triangles"
    description = "Ensures mesh triangle count is below specified limit"
    has_params = True
    
    def __init__(self, params=None):
        super().__init__(params)
        self.max_triangles = params if isinstance(params, int) else 100000
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        total_triangles = 0
        for mesh in asset.get_all_meshes():
            if mesh.faces is not None:
                total_triangles += len(mesh.faces)
        
        if total_triangles > self.max_triangles:
            result.add_error(
                f"Triangle count ({total_triangles:,}) exceeds limit ({self.max_triangles:,})"
            )
        
        return result


class NamingConventionRule(ValidationRule):
    """Check that asset name matches convention"""
    
    name = "naming_convention"
    description = "Ensures asset name matches specified regex pattern"
    has_params = True
    
    def __init__(self, params=None):
        super().__init__(params)
        self.pattern = params if isinstance(params, str) else r"^[a-zA-Z][a-zA-Z0-9_]*$"
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        if not re.match(self.pattern, asset.name):
            result.add_warning(
                f"Asset name '{asset.name}' doesn't match naming convention: {self.pattern}"
            )
        
        # Check child names too
        for child in asset.children:
            if not re.match(self.pattern, child.name):
                result.add_warning(
                    f"Child name '{child.name}' doesn't match naming convention"
                )
        
        return result


class CorrectScaleRule(ValidationRule):
    """Check that asset is at reasonable scale"""
    
    name = "correct_scale"
    description = "Ensures asset dimensions are within reasonable bounds"
    has_params = True
    
    def __init__(self, params=None):
        super().__init__(params)
        if isinstance(params, dict):
            self.min_size = params.get("min", 0.01)
            self.max_size = params.get("max", 1000)
        else:
            self.min_size = 0.01
            self.max_size = 1000
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        bbox = asset.get_bounding_box()
        if bbox is None:
            return result
        
        min_point, max_point = bbox
        dimensions = max_point - min_point
        max_dim = np.max(dimensions)
        
        if max_dim < self.min_size:
            result.add_warning(
                f"Asset is very small (max dimension: {max_dim:.4f}). "
                f"Expected at least {self.min_size}"
            )
        elif max_dim > self.max_size:
            result.add_warning(
                f"Asset is very large (max dimension: {max_dim:.1f}). "
                f"Expected at most {self.max_size}"
            )
        
        return result


class ManifoldMeshRule(ValidationRule):
    """Check that mesh is manifold (watertight)"""
    
    name = "manifold_mesh"
    description = "Checks for non-manifold edges and vertices"
    has_params = False
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        for mesh in asset.get_all_meshes():
            if mesh.faces is None:
                continue
            
            # Count edge usage
            edge_count = {}
            
            for face in mesh.faces:
                for i in range(len(face)):
                    v1 = face[i]
                    v2 = face[(i + 1) % len(face)]
                    
                    # Normalize edge direction
                    edge = tuple(sorted([v1, v2]))
                    edge_count[edge] = edge_count.get(edge, 0) + 1
            
            # Check for non-manifold edges (used by more than 2 faces)
            non_manifold_edges = sum(1 for count in edge_count.values() if count > 2)
            
            # Check for boundary edges (used by only 1 face)
            boundary_edges = sum(1 for count in edge_count.values() if count == 1)
            
            if non_manifold_edges > 0:
                result.add_warning(
                    f"Mesh has {non_manifold_edges} non-manifold edges"
                )
            
            if boundary_edges > 0:
                result.add_info(
                    f"Mesh has {boundary_edges} boundary edges (not watertight)"
                )
        
        return result


class MaxTextureSizeRule(ValidationRule):
    """Check that textures are within size limit"""
    
    name = "max_texture_size"
    description = "Ensures texture dimensions are below specified limit"
    has_params = True
    
    def __init__(self, params=None):
        super().__init__(params)
        self.max_size = params if isinstance(params, int) else 4096
    
    def validate(self, asset: "Asset") -> ValidationResult:
        result = ValidationResult()
        
        for texture in asset.get_all_textures():
            if texture.width > self.max_size or texture.height > self.max_size:
                result.add_warning(
                    f"Texture '{texture.name}' ({texture.width}x{texture.height}) "
                    f"exceeds max size ({self.max_size})"
                )
        
        return result
