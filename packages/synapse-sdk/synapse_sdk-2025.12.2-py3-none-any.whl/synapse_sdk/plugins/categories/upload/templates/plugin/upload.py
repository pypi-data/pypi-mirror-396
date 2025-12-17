from pathlib import Path
from typing import Any, Dict, List

from . import BaseUploader


class Uploader(BaseUploader):
    """Plugin upload action interface for organizing files.

    This class provides a template for plugin developers to implement
    their own file organization logic by inheriting from BaseUploader.

    Important: This plugin extension works with already-organized files from the
    main upload workflow. Files are provided via organized_files parameter regardless
    of whether single-path or multi-path mode was used in the upload configuration.

    Example usage:
        Override process_files() to implement custom file processing logic.
        Override validate_file_types() to implement custom validation rules.
        Override setup_directories() to create custom directory structures.
    """

    def __init__(
        self, run, path: Path, file_specification: List = None, organized_files: List = None, extra_params: Dict = None
    ):
        """Initialize the uploader with required parameters.

        Args:
            run: Plugin run object with logging capabilities.
            path: Path object pointing to the upload target directory.
                  - In single-path mode: Base directory path (Path object)
                  - In multi-path mode: None (use self.assets_config instead)
            file_specification: List of specifications that define the structure of files to be uploaded.
            organized_files: List of pre-organized files from the main upload workflow.
                            Works transparently with both single-path and multi-path modes.
            extra_params: Additional parameters for customization.
        """
        super().__init__(run, path, file_specification, organized_files, extra_params)

    def process_files(self, organized_files: List) -> List:
        """Process and transform files during upload.

        Override this method to implement custom file processing logic.
        This is the main method where plugin-specific logic should be implemented.

        Args:
            organized_files: List of organized file dictionaries from the workflow.

        Returns:
            List: The processed list of files ready for upload.
        """
        # Default implementation: return files as-is
        # Plugin developers should override this method for custom logic
        return organized_files

    def validate_file_types(self, organized_files: List) -> List:
        """Validate file types against specifications.

        This example shows how to use the BaseUploader's comprehensive validation logic.
        You can override this method for custom validation or call super() to use the base implementation.

        Args:
            organized_files: List of organized file dictionaries to validate.

        Returns:
            List: Filtered list containing only valid files that match specifications.
        """
        return super().validate_file_types(organized_files)

    def handle_upload_files(self) -> List[Dict[str, Any]]:
        """Executes the upload task using the base class implementation.

        Returns:
            List: The final list of organized files ready for upload
        """
        return super().handle_upload_files()

    def organize_files(self, organized_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform and organize files based on plugin logic.

        Override this method to implement custom file organization logic.

        Args:
            organized_files: List of organized files from the default logic

        Returns:
            List of transformed organized files
        """
        return organized_files

    def filter_files(self, organized_file: Dict[str, Any]) -> bool:
        """Filter files based on custom criteria.

        Override this method to implement custom filtering logic.

        Args:
            organized_file: Single organized file to filter

        Returns:
            bool: True to include the file, False to filter it out
        """
        return True
