import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Optional, List, Type
import logging

from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


class ModelLoader:
    """Dynamically load SQLAlchemy models from user code"""
    
    def __init__(self):
        self.metadata: Optional[MetaData] = None
        self.base_classes: List[Type[DeclarativeBase]] = []
        self.loaded_modules: List[str] = []
    
    def load_from_module(self, module_path: str) -> MetaData:
        """
        Load models from a Python module path
        Example: 'app.models' or 'src.database.models'
        """
        try:
            # Import the module
            module = importlib.import_module(module_path)
            self.loaded_modules.append(module_path)
            
            # Find all SQLAlchemy Base classes and their metadata
            metadata = self._extract_metadata_from_module(module)
            
            logger.info(f"Loaded models from module: {module_path}")
            logger.info(f"Found {len(metadata.tables)} tables")
            
            return metadata
            
        except ImportError as e:
            logger.error(f"Failed to import module {module_path}: {e}")
            raise
    
    def load_from_file(self, file_path: Path) -> MetaData:
        """
        Load models from a specific Python file
        Example: Path('src/models.py')
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Model file not found: {file_path}")
        
        # Create module name from file
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load module from {file_path}")
        
        # Load the module
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        self.loaded_modules.append(module_name)
        
        # Extract metadata
        metadata = self._extract_metadata_from_module(module)
        
        logger.info(f"Loaded models from file: {file_path}")
        logger.info(f"Found {len(metadata.tables)} tables")
        
        return metadata
    
    def load_from_pattern(self, pattern: str = "*/models.py") -> MetaData:
        """
        Load models from files matching a pattern
        Example: '*/models.py', 'app/**/models.py'
        """
        from pathlib import Path
        
        combined_metadata = MetaData()
        
        for model_file in Path.cwd().glob(pattern):
            if '__pycache__' in str(model_file):
                continue
                
            try:
                metadata = self.load_from_file(model_file)
                # Merge metadata
                for table in metadata.tables.values():
                    table.to_metadata(combined_metadata)
            except Exception as e:
                logger.warning(f"Failed to load {model_file}: {e}")
        
        return combined_metadata
    
    def _extract_metadata_from_module(self, module) -> MetaData:
        """Extract SQLAlchemy metadata from a module"""
        metadata = MetaData()
        
        # Look for different patterns
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Pattern 1: Direct metadata object
            if isinstance(attr, MetaData):
                logger.debug(f"Found MetaData: {attr_name}")
                # Copy tables to our metadata
                for table in attr.tables.values():
                    table.to_metadata(metadata)
            
            # Pattern 2: DeclarativeBase class
            elif isinstance(attr, type) and hasattr(attr, 'metadata'):
                if isinstance(getattr(attr, 'metadata'), MetaData):
                    logger.debug(f"Found Base class: {attr_name}")
                    base_metadata = attr.metadata
                    for table in base_metadata.tables.values():
                        table.to_metadata(metadata)
                    self.base_classes.append(attr)
            
            # Pattern 3: SQLAlchemy 2.0 style DeclarativeBase
            elif (isinstance(attr, DeclarativeMeta) and 
                  attr.__name__ != 'Base' and 
                  hasattr(attr, '__tablename__')):
                logger.debug(f"Found model class: {attr_name}")
                # The metadata is already registered through Base
        
        self.metadata = metadata
        return metadata
    
    def get_metadata(self) -> MetaData:
        """Get combined metadata from all loaded models"""
        if not self.metadata:
            raise RuntimeError("No models loaded yet")
        return self.metadata