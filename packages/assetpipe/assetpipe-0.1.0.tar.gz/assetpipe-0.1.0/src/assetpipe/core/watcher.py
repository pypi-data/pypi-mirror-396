"""
File Watcher - Watch directories for new assets
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Set
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from assetpipe.core.config import PipelineConfig
from assetpipe.core.pipeline import Pipeline

logger = logging.getLogger(__name__)


class AssetEventHandler(FileSystemEventHandler):
    """Handle file system events for assets"""
    
    def __init__(
        self,
        pipeline: Pipeline,
        config: PipelineConfig,
        output_dir: Optional[Path] = None,
    ):
        self.pipeline = pipeline
        self.config = config
        self.output_dir = output_dir
        self._processing: Set[Path] = set()
        self._extensions = {f".{fmt.lower()}" for fmt in config.input.formats}
    
    def _should_process(self, path: Path) -> bool:
        """Check if file should be processed"""
        if not path.is_file():
            return False
        if path.suffix.lower() not in self._extensions:
            return False
        if path in self._processing:
            return False
        return True
    
    def _process_file(self, path: Path) -> None:
        """Process a single file"""
        if not self._should_process(path):
            return
        
        self._processing.add(path)
        
        try:
            # Wait a bit for file to be fully written
            time.sleep(0.5)
            
            logger.info(f"Processing: {path.name}")
            
            output_path = None
            if self.output_dir:
                ext = self.config.output.format
                output_path = self.output_dir / f"{path.stem}.{ext}"
            
            job = self.pipeline.process_single(path, output_path)
            
            if job.status == "success":
                logger.info(f"✓ Completed: {path.name} → {job.output_path}")
            else:
                logger.error(f"✗ Failed: {path.name} - {job.error}")
                
        except Exception as e:
            logger.error(f"Error processing {path}: {e}")
        finally:
            self._processing.discard(path)
    
    def on_created(self, event: FileCreatedEvent) -> None:
        if not event.is_directory:
            self._process_file(Path(event.src_path))
    
    def on_modified(self, event: FileModifiedEvent) -> None:
        # Only process modifications if file wasn't just created
        if not event.is_directory:
            path = Path(event.src_path)
            if path not in self._processing:
                self._process_file(path)


class AssetWatcher:
    """
    Watch a directory for new/modified assets and process them automatically.
    """
    
    def __init__(
        self,
        config: PipelineConfig,
        watch_dir: Path,
        output_dir: Optional[Path] = None,
    ):
        self.config = config
        self.watch_dir = Path(watch_dir)
        self.output_dir = Path(output_dir) if output_dir else None
        
        self.pipeline = Pipeline(config)
        self._observer: Optional[Observer] = None
    
    def start(self, blocking: bool = True) -> None:
        """Start watching the directory"""
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        handler = AssetEventHandler(
            pipeline=self.pipeline,
            config=self.config,
            output_dir=self.output_dir,
        )
        
        self._observer = Observer()
        self._observer.schedule(
            handler,
            str(self.watch_dir),
            recursive=self.config.input.recursive,
        )
        
        self._observer.start()
        logger.info(f"Watching: {self.watch_dir}")
        
        if blocking:
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
    
    def stop(self) -> None:
        """Stop watching"""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            logger.info("Stopped watching")
    
    def __enter__(self) -> "AssetWatcher":
        self.start(blocking=False)
        return self
    
    def __exit__(self, *args) -> None:
        self.stop()
