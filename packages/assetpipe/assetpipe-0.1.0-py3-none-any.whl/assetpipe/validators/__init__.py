"""
AssetPipe Validators - Asset validation rules
"""

from typing import List, Optional, Dict, Any
from assetpipe.validators.base import ValidationResult, ValidationRule
from assetpipe.validators.rules import (
    NoMissingTexturesRule,
    ValidUVsRule,
    NoDegenerateTrianglesRule,
    MaxTrianglesRule,
    NamingConventionRule,
    CorrectScaleRule,
    ManifoldMeshRule,
    MaxTextureSizeRule,
)
from assetpipe.core.asset import Asset

# Registry of available validation rules
RULES: Dict[str, type] = {
    "no_missing_textures": NoMissingTexturesRule,
    "valid_uvs": ValidUVsRule,
    "no_degenerate_triangles": NoDegenerateTrianglesRule,
    "max_triangles": MaxTrianglesRule,
    "naming_convention": NamingConventionRule,
    "correct_scale": CorrectScaleRule,
    "manifold_mesh": ManifoldMeshRule,
    "max_texture_size": MaxTextureSizeRule,
}

# Preset rule sets
RULE_PRESETS = {
    "strict": [
        "no_missing_textures",
        "valid_uvs",
        "no_degenerate_triangles",
        "manifold_mesh",
        {"max_triangles": 100000},
        {"naming_convention": "^[a-z][a-z0-9_]*$"},
    ],
    "standard": [
        "no_missing_textures",
        "valid_uvs",
        "no_degenerate_triangles",
    ],
    "minimal": [
        "no_missing_textures",
    ],
    "game_ready": [
        "no_missing_textures",
        "valid_uvs",
        "no_degenerate_triangles",
        {"max_triangles": 50000},
        {"max_texture_size": 2048},
    ],
}


def validate_asset(
    asset: Asset,
    rules: Optional[List[str]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> ValidationResult:
    """
    Validate an asset against specified rules.
    
    Args:
        asset: Asset to validate
        rules: List of rule names or preset name (strict, standard, minimal)
        params: Optional parameters for rules
        
    Returns:
        ValidationResult with errors and warnings
    """
    result = ValidationResult()
    params = params or {}
    
    # Determine rules to apply
    if rules is None:
        rules = ["standard"]
    
    # Check if it's a preset (only if first item is a string)
    if len(rules) == 1 and isinstance(rules[0], str) and rules[0] in RULE_PRESETS:
        rules = RULE_PRESETS[rules[0]]
    
    # Apply each rule
    for rule_spec in rules:
        rule_name = rule_spec if isinstance(rule_spec, str) else list(rule_spec.keys())[0]
        rule_params = {} if isinstance(rule_spec, str) else {rule_name: rule_spec[rule_name]}
        
        if rule_name not in RULES:
            result.warnings.append(f"Unknown rule: {rule_name}")
            continue
        
        # Get rule class and instantiate
        rule_class = RULES[rule_name]
        rule_param = rule_params.get(rule_name) or params.get(rule_name)
        
        if rule_param is not None:
            rule = rule_class(rule_param)
        else:
            rule = rule_class()
        
        # Run validation
        rule_result = rule.validate(asset)
        result.merge(rule_result)
    
    return result


def list_rules() -> List[str]:
    """List all available validation rules"""
    return list(RULES.keys())


def get_rule_info(rule_name: str) -> Dict[str, Any]:
    """Get information about a validation rule"""
    if rule_name not in RULES:
        raise ValueError(f"Unknown rule: {rule_name}")
    
    rule_class = RULES[rule_name]
    return {
        "name": rule_name,
        "description": rule_class.__doc__ or "",
        "has_params": rule_class.has_params,
    }


__all__ = [
    "ValidationResult",
    "ValidationRule",
    "validate_asset",
    "list_rules",
    "get_rule_info",
    "RULES",
    "RULE_PRESETS",
]
