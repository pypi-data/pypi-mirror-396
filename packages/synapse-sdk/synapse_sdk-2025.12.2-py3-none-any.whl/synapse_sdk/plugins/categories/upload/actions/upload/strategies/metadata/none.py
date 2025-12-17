from pathlib import Path
from typing import Any, Dict

from ..base import MetadataStrategy, ValidationResult


class NoneMetadataStrategy(MetadataStrategy):
    """Metadata strategy that returns no metadata."""

    def extract(self, source_path: Path) -> Dict[str, Dict[str, Any]]:
        """Return empty metadata."""
        return {}

    def validate(self, metadata: Dict) -> ValidationResult:
        """Always validates successfully for empty metadata."""
        return ValidationResult(valid=True)
