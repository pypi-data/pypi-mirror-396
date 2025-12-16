import logging
import os
import uuid
import shutil
from typing import Dict, Type, Optional, Any, List
from concurrent.futures import Future
from converter.base.converter_base import BaseConverter
from converter.base.format_detector import FormatDetector
from core.worker_pool import WorkerPool
from core.progress_tracker import ProgressTracker
from core.cache_manager import CacheManager

logger = logging.getLogger(__name__)

class ConversionEngine:
    """
    Orchestrates the document conversion process.
    Manages converter registration, selection, and parallel execution.
    """

    def __init__(self, worker_pool: Optional[WorkerPool] = None, 
                 progress_tracker: Optional[ProgressTracker] = None,
                 cache_manager: Optional[CacheManager] = None):
        self.format_detector = FormatDetector()
        self._converters: Dict[str, Type[BaseConverter]] = {}
        self.worker_pool = worker_pool or WorkerPool()
        self.progress_tracker = progress_tracker or ProgressTracker()
        self.cache_manager = cache_manager

    def register_converter(self, format_name: str, converter_class: Type[BaseConverter]):
        """
        Register a converter for a specific format.
        
        Args:
            format_name: The format identifier (e.g., 'pdf', 'docx').
            converter_class: The converter class to handle this format.
        """
        self._converters[format_name] = converter_class
        logger.info(f"Registered converter for format: {format_name}")

    def submit_conversion(self, input_path: str, output_path: str, **kwargs) -> str:
        """
        Submit a document conversion task to the worker pool.
        
        Args:
            input_path: Path to the input file.
            output_path: Path to the output file.
            **kwargs: Additional arguments passed to the converter.
            
        Returns:
            The task ID.
        """
        task_id = str(uuid.uuid4())
        
        # Register task with progress tracker
        self.progress_tracker.add_task(task_id, total=100, desc=f"Converting {os.path.basename(input_path)}")
        
        # Submit to worker pool
        self.worker_pool.submit(
            self._execute_conversion,
            task_id, input_path, output_path, **kwargs
        )
        
        return task_id

    def _execute_conversion(self, task_id: str, input_path: str, output_path: str, **kwargs) -> bool:
        """
        Internal method to execute conversion and update progress.
        """
        try:
            self.progress_tracker.update_progress(task_id, 10, status="Starting")
            result = self.convert(input_path, output_path, **kwargs)
            if result:
                self.progress_tracker.update_progress(task_id, 100, status="Completed")
            else:
                self.progress_tracker.update_progress(task_id, 0, status="Failed")
            return result
        except Exception as e:
            self.progress_tracker.update_progress(task_id, 0, status=f"Error: {str(e)}")
            raise

    def convert(self, input_path: str, output_path: str, **kwargs) -> bool:
        """
        Convert a document synchronously.
        
        Args:
            input_path: Path to the input file.
            output_path: Path to the output file.
            **kwargs: Additional arguments passed to the converter.
            
        Returns:
            True if conversion was successful, False otherwise.
            
        Raises:
            ValueError: If format is not supported or detection fails.
            Exception: If conversion fails.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Check cache if available
        if self.cache_manager:
            cached_path = self.cache_manager.get(input_path, kwargs)
            if cached_path:
                logger.info(f"Cache hit for {input_path}")
                try:
                    # Ensure output directory exists before copying
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    shutil.copy2(cached_path, output_path)
                    logger.info(f"Restored from cache to {output_path}")
                    return True
                except Exception as e:
                    logger.warning(f"Failed to restore from cache: {e}")
                    # Fallthrough to normal conversion

        # Detect format
        detected_format = self.format_detector.detect(input_path)
        if not detected_format:
            raise ValueError(f"Could not detect format for file: {input_path}")
            
        logger.info(f"Detected format '{detected_format}' for file: {input_path}")

        # Select converter
        converter_class = self._converters.get(detected_format)
        if not converter_class:
            raise ValueError(f"No converter registered for format: {detected_format}")

        # Instantiate and execute
        try:
            converter = converter_class()
            logger.info(f"Starting conversion using {converter.__class__.__name__}...")
            result = converter.convert(input_path, output_path, **kwargs)
            if result:
                logger.info(f"Conversion successful: {output_path}")
                # Save to cache if successful
                if self.cache_manager:
                    self.cache_manager.set(input_path, output_path, kwargs)
            else:
                logger.error("Conversion failed.")
            return result
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            raise
