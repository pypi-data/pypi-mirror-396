"""
Pipeline - Asset processing pipeline
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

from assetpipe.core.asset import Asset
from assetpipe.core.config import PipelineConfig

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Results from pipeline execution"""
    success_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    processed_files: List[Path] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def total_count(self) -> int:
        return self.success_count + self.error_count


@dataclass
class ProcessingJob:
    """Single asset processing job"""
    input_path: Path
    output_path: Optional[Path] = None
    status: str = "pending"  # pending, processing, success, error
    error: Optional[str] = None


class Pipeline:
    """
    Asset processing pipeline.
    Handles discovery, validation, conversion, and optimization of assets.
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self._plugins: List[Any] = []
        self._load_plugins()
    
    def _load_plugins(self) -> None:
        """Load configured plugins"""
        for plugin_config in self.config.plugins:
            if not plugin_config.enabled:
                continue
            try:
                from assetpipe.plugins import load_plugin
                plugin = load_plugin(plugin_config.path, plugin_config.config)
                self._plugins.append(plugin)
                logger.info(f"Loaded plugin: {plugin_config.path}")
            except Exception as e:
                logger.warning(f"Failed to load plugin {plugin_config.path}: {e}")
    
    def discover_assets(self, directory: Path) -> List[Path]:
        """
        Discover assets in a directory based on config filters.
        """
        directory = Path(directory)
        assets = []
        
        # Build list of extensions to look for
        extensions = [f".{fmt.lower()}" for fmt in self.config.input.formats]
        
        # Search pattern
        if self.config.input.recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for path in directory.glob(pattern):
            if not path.is_file():
                continue
            
            # Check extension
            if path.suffix.lower() not in extensions:
                continue
            
            # Check exclude patterns
            excluded = False
            for exclude in self.config.input.exclude_patterns:
                if path.match(exclude):
                    excluded = True
                    break
            
            if not excluded:
                assets.append(path)
        
        return sorted(assets)
    
    def process_single(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
    ) -> ProcessingJob:
        """
        Process a single asset through the pipeline.
        """
        job = ProcessingJob(input_path=input_path, output_path=output_path)
        job.status = "processing"
        
        try:
            # Load asset
            asset = Asset.load(input_path)
            logger.info(f"Loaded: {input_path.name}")
            
            # Validate
            if self.config.validation.rules:
                from assetpipe.validators import validate_asset
                
                rules = [r if isinstance(r, str) else list(r.keys())[0] 
                        for r in self.config.validation.rules]
                results = validate_asset(asset, rules=rules)
                
                if results.has_errors:
                    job.status = "error"
                    job.error = f"Validation failed: {results.errors[0]}"
                    return job
            
            # Optimize
            if self._should_optimize():
                from assetpipe.optimizers import optimize_asset
                
                asset = optimize_asset(
                    asset,
                    decimate_ratio=self.config.optimization.mesh.decimate,
                    max_texture_size=self.config.optimization.textures.max_size,
                    generate_lods=self.config.optimization.mesh.generate_lods is not None,
                )
                logger.info(f"Optimized: {input_path.name}")
            
            # Determine output path
            if output_path is None:
                output_dir = self.config.output.directory
                if output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                else:
                    output_dir = input_path.parent
                
                output_name = self._format_output_name(input_path)
                output_path = output_dir / output_name
            
            job.output_path = output_path
            
            # Check overwrite
            if output_path.exists() and not self.config.output.overwrite:
                job.status = "error"
                job.error = f"Output exists and overwrite=False: {output_path}"
                return job
            
            # Save
            asset.save(output_path)
            logger.info(f"Saved: {output_path.name}")
            
            job.status = "success"
            
        except Exception as e:
            job.status = "error"
            job.error = str(e)
            logger.error(f"Error processing {input_path}: {e}")
        
        return job
    
    def process_batch(
        self,
        assets: List[Path],
        output_dir: Optional[Path] = None,
        parallel: int = 4,
        progress_callback: Optional[Callable[[], None]] = None,
    ) -> PipelineResult:
        """
        Process multiple assets in parallel.
        """
        result = PipelineResult()
        
        # Override output directory if provided
        if output_dir:
            self.config.output.directory = str(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        def process_one(asset_path: Path) -> ProcessingJob:
            job = self.process_single(asset_path)
            if progress_callback:
                progress_callback()
            return job
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {executor.submit(process_one, path): path for path in assets}
            
            for future in as_completed(futures):
                job = future.result()
                
                if job.status == "success":
                    result.success_count += 1
                    if job.output_path:
                        result.processed_files.append(job.output_path)
                else:
                    result.error_count += 1
                    if job.error:
                        result.errors.append(f"{job.input_path.name}: {job.error}")
        
        # Send notifications
        self._send_notifications(result)
        
        return result
    
    def _should_optimize(self) -> bool:
        """Check if any optimization is configured"""
        opt = self.config.optimization
        return (
            opt.mesh.decimate is not None or
            opt.mesh.generate_lods is not None or
            opt.textures.max_size < 4096
        )
    
    def _format_output_name(self, input_path: Path) -> str:
        """Format output filename based on config template"""
        template = self.config.output.naming
        ext = self.config.output.format
        
        name = template.format(
            name=input_path.stem,
            ext=ext,
            date="",  # TODO: Add date formatting
            hash="",  # TODO: Add content hash
        )
        
        # Ensure extension
        if not name.endswith(f".{ext}"):
            name = f"{input_path.stem}.{ext}"
        
        return name
    
    def _send_notifications(self, result: PipelineResult) -> None:
        """Send notifications based on config"""
        notifications = self.config.notifications
        
        if notifications.slack and notifications.slack.get("webhook"):
            try:
                from assetpipe.utils.notifications import send_slack_notification
                send_slack_notification(
                    webhook=notifications.slack["webhook"],
                    result=result,
                    on_events=notifications.slack.get("on", ["error", "complete"]),
                )
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
        
        if notifications.discord and notifications.discord.get("webhook"):
            try:
                from assetpipe.utils.notifications import send_discord_notification
                send_discord_notification(
                    webhook=notifications.discord["webhook"],
                    result=result,
                    on_events=notifications.discord.get("on", ["error", "complete"]),
                )
            except Exception as e:
                logger.warning(f"Failed to send Discord notification: {e}")
