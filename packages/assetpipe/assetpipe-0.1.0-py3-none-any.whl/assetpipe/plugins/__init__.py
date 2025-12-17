"""
AssetPipe Plugin System

Allows extending AssetPipe with custom converters, validators, and processors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, List, Dict, Any, Optional, Type
import importlib.util
import logging

if TYPE_CHECKING:
    from assetpipe.core.asset import Asset
    from assetpipe.validators.base import ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class PluginInfo:
    """Plugin metadata"""
    name: str
    version: str
    type: str  # converter, validator, processor
    description: str = ""
    author: str = ""


class BasePlugin(ABC):
    """Base class for all plugins"""
    
    # Plugin metadata
    name: str = "unnamed_plugin"
    version: str = "0.1.0"
    plugin_type: str = "generic"
    description: str = ""
    author: str = ""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
    
    @classmethod
    def get_info(cls) -> PluginInfo:
        return PluginInfo(
            name=cls.name,
            version=cls.version,
            type=cls.plugin_type,
            description=cls.description,
            author=cls.author,
        )


class ConverterPlugin(BasePlugin):
    """Plugin for adding new format converters"""
    
    plugin_type = "converter"
    
    # Formats this converter handles
    input_formats: List[str] = []
    output_formats: List[str] = []
    
    @abstractmethod
    def load(self, path: Path) -> "Asset":
        """Load asset from file"""
        pass
    
    @abstractmethod
    def save(self, asset: "Asset", path: Path) -> None:
        """Save asset to file"""
        pass
    
    def can_load(self, path: Path) -> bool:
        """Check if this converter can load the file"""
        return path.suffix.lower().lstrip('.') in self.input_formats
    
    def can_save(self, format: str) -> bool:
        """Check if this converter can save to format"""
        return format.lower() in self.output_formats


class ValidatorPlugin(BasePlugin):
    """Plugin for adding custom validation rules"""
    
    plugin_type = "validator"
    
    # Rule name for config
    rule_name: str = ""
    
    @abstractmethod
    def validate(self, asset: "Asset") -> "ValidationResult":
        """Validate asset against this rule"""
        pass


class ProcessorPlugin(BasePlugin):
    """Plugin for adding custom processing steps"""
    
    plugin_type = "processor"
    
    # When to run: pre_convert, post_convert, pre_validate, post_validate
    run_stage: str = "post_convert"
    
    @abstractmethod
    def process(self, asset: "Asset") -> "Asset":
        """Process asset and return modified version"""
        pass


# Plugin registry
_plugins: Dict[str, BasePlugin] = {}
_converter_plugins: Dict[str, ConverterPlugin] = {}
_validator_plugins: Dict[str, ValidatorPlugin] = {}
_processor_plugins: Dict[str, ProcessorPlugin] = {}


def load_plugin(path: str, config: Dict[str, Any] = None) -> BasePlugin:
    """
    Load a plugin from file path.
    
    Args:
        path: Path to plugin Python file
        config: Plugin configuration
        
    Returns:
        Loaded plugin instance
    """
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Plugin not found: {path}")
    
    # Load module
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load plugin: {path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Find plugin class
    plugin_class = None
    for name in dir(module):
        obj = getattr(module, name)
        if (
            isinstance(obj, type) and
            issubclass(obj, BasePlugin) and
            obj not in (BasePlugin, ConverterPlugin, ValidatorPlugin, ProcessorPlugin)
        ):
            plugin_class = obj
            break
    
    if plugin_class is None:
        raise ValueError(f"No plugin class found in {path}")
    
    # Instantiate
    plugin = plugin_class(config)
    
    # Register
    register_plugin(plugin)
    
    logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
    
    return plugin


def register_plugin(plugin: BasePlugin) -> None:
    """Register a plugin instance"""
    _plugins[plugin.name] = plugin
    
    if isinstance(plugin, ConverterPlugin):
        _converter_plugins[plugin.name] = plugin
        for fmt in plugin.input_formats + plugin.output_formats:
            _converter_plugins[fmt] = plugin
    
    elif isinstance(plugin, ValidatorPlugin):
        _validator_plugins[plugin.name] = plugin
        if plugin.rule_name:
            _validator_plugins[plugin.rule_name] = plugin
    
    elif isinstance(plugin, ProcessorPlugin):
        _processor_plugins[plugin.name] = plugin


def unregister_plugin(name: str) -> None:
    """Unregister a plugin by name"""
    if name in _plugins:
        plugin = _plugins.pop(name)
        
        if isinstance(plugin, ConverterPlugin):
            _converter_plugins.pop(name, None)
        elif isinstance(plugin, ValidatorPlugin):
            _validator_plugins.pop(name, None)
        elif isinstance(plugin, ProcessorPlugin):
            _processor_plugins.pop(name, None)


def get_plugin(name: str) -> Optional[BasePlugin]:
    """Get a plugin by name"""
    return _plugins.get(name)


def get_converter_plugin(format: str) -> Optional[ConverterPlugin]:
    """Get a converter plugin for format"""
    return _converter_plugins.get(format.lower())


def get_validator_plugin(rule_name: str) -> Optional[ValidatorPlugin]:
    """Get a validator plugin by rule name"""
    return _validator_plugins.get(rule_name)


def list_plugins() -> List[PluginInfo]:
    """List all registered plugins"""
    return [p.get_info() for p in _plugins.values()]


def list_converter_plugins() -> List[PluginInfo]:
    """List converter plugins"""
    seen = set()
    result = []
    for p in _converter_plugins.values():
        if p.name not in seen:
            result.append(p.get_info())
            seen.add(p.name)
    return result


def list_validator_plugins() -> List[PluginInfo]:
    """List validator plugins"""
    seen = set()
    result = []
    for p in _validator_plugins.values():
        if p.name not in seen:
            result.append(p.get_info())
            seen.add(p.name)
    return result


__all__ = [
    "BasePlugin",
    "ConverterPlugin",
    "ValidatorPlugin",
    "ProcessorPlugin",
    "PluginInfo",
    "load_plugin",
    "register_plugin",
    "unregister_plugin",
    "get_plugin",
    "get_converter_plugin",
    "get_validator_plugin",
    "list_plugins",
]
