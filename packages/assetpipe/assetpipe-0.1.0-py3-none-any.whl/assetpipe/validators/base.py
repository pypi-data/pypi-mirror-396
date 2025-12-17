"""
Validation Base Classes
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Any

if TYPE_CHECKING:
    from assetpipe.core.asset import Asset


@dataclass
class ValidationResult:
    """
    Result of validation checks.
    """
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    @property
    def is_valid(self) -> bool:
        return not self.has_errors
    
    def add_error(self, message: str) -> None:
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
    
    def add_info(self, message: str) -> None:
        self.info.append(message)
    
    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
    
    @classmethod
    def ok(cls) -> "ValidationResult":
        """Create a passing result"""
        return cls()
    
    @classmethod
    def error(cls, message: str) -> "ValidationResult":
        """Create a failing result with error"""
        return cls(errors=[message])
    
    @classmethod
    def warning(cls, message: str) -> "ValidationResult":
        """Create a result with warning"""
        return cls(warnings=[message])
    
    def __str__(self) -> str:
        parts = []
        if self.errors:
            parts.append(f"Errors: {len(self.errors)}")
        if self.warnings:
            parts.append(f"Warnings: {len(self.warnings)}")
        if not parts:
            return "Valid"
        return ", ".join(parts)


class ValidationRule(ABC):
    """
    Abstract base class for validation rules.
    """
    
    # Rule identifier
    name: str = ""
    
    # Human-readable description
    description: str = ""
    
    # Whether this rule accepts parameters
    has_params: bool = False
    
    def __init__(self, params: Any = None):
        self.params = params
    
    @abstractmethod
    def validate(self, asset: "Asset") -> ValidationResult:
        """
        Validate an asset against this rule.
        
        Args:
            asset: Asset to validate
            
        Returns:
            ValidationResult with any errors/warnings
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(params={self.params})"
