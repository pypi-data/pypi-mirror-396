from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class ValidationResult:
    """Result of validation operations."""

    def __init__(self, valid: bool, errors: List[str] = None):
        self.valid = valid
        self.errors = errors or []

    def __bool__(self):
        return self.valid


class ValidationStrategy(ABC):
    """Strategy interface for validation operations."""

    @abstractmethod
    def validate_params(self, params: Dict) -> ValidationResult:
        """Validate action parameters."""
        pass

    @abstractmethod
    def validate_files(self, files: List[Dict], specs: Dict) -> ValidationResult:
        """Validate organized files against specifications."""
        pass


class FileDiscoveryStrategy(ABC):
    """Strategy interface for file discovery and organization."""

    @abstractmethod
    def discover(self, path: Path, recursive: bool) -> List[Path]:
        """Discover files in the given path."""
        pass

    @abstractmethod
    def organize(self, files: List[Path], specs: Dict, metadata: Dict, type_dirs: Dict = None) -> List[Dict]:
        """Organize files according to specifications."""
        pass


class MetadataStrategy(ABC):
    """Strategy interface for metadata extraction and processing."""

    @abstractmethod
    def extract(self, source_path: Path) -> Dict[str, Dict[str, Any]]:
        """Extract metadata from source (e.g., Excel file)."""
        pass

    @abstractmethod
    def validate(self, metadata: Dict) -> ValidationResult:
        """Validate extracted metadata."""
        pass


class UploadConfig:
    """Configuration for upload operations."""

    def __init__(self, chunked_threshold_mb: int = 50, batch_size: int = 1):
        self.chunked_threshold_mb = chunked_threshold_mb
        self.batch_size = batch_size


class UploadStrategy(ABC):
    """Strategy interface for file upload operations."""

    @abstractmethod
    def upload(self, files: List[Dict], config: UploadConfig) -> List[Dict]:
        """Upload files to storage."""
        pass


class DataUnitStrategy(ABC):
    """Strategy interface for data unit generation."""

    @abstractmethod
    def generate(self, uploaded_files: List[Dict], batch_size: int) -> List[Dict]:
        """Generate data units from uploaded files."""
        pass
