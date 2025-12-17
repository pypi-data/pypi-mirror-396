import json
from pathlib import Path
from typing import Generator

import requests

from synapse_sdk.plugins.categories.export.actions.export.enums import ExportStatus


class BaseExporter:
    """Base class for export plugins with common functionality.

    This class handles common tasks like progress tracking, logging, and metrics
    that are shared across all export plugins. Plugin developers should inherit
    from this class and implement the required methods for their specific logic.

    Core Methods:
        export(): Main export method - handles the complete export workflow
        process_data_conversion(): Handle data conversion pipeline
        process_file_saving(): Handle file saving operations (can be overridden)
        setup_output_directories(): Setup output directories (can be overridden)

    Required Methods (should be implemented by subclasses):
        convert_data(): Transform data during export

    Optional Methods (can be overridden by subclasses):
        save_original_file(): Save original files from export items
        save_as_json(): Save data as JSON files
        before_convert(): Pre-process data before conversion
        after_convert(): Post-process data after conversion
        process_file_saving(): Custom file saving logic

    Helper Methods:
        _process_original_file_saving(): Handle original file saving with metrics
        _process_json_file_saving(): Handle JSON file saving with metrics

    Auto-provided Utilities:
        Progress tracking via self.run.set_progress()
        Logging via self.run.log_message() and other run methods
        Error handling and metrics collection via self.run methods
    """

    def __init__(self, run, export_items: Generator, path_root: Path, **params):
        """Initialize the base export class.

        Args:
            run: Plugin run object with logging capabilities.
            export_items (generator): Export items generator
            path_root: pathlib object, the path to export
            **params: Additional parameters
        """
        self.run = run
        self.export_items = export_items
        self.path_root = path_root
        self.params = params

    def _create_unique_export_path(self, base_name: str) -> Path:
        """Create a unique export path to avoid conflicts."""
        export_path = self.path_root / base_name
        unique_export_path = export_path
        counter = 1
        while unique_export_path.exists():
            unique_export_path = export_path.with_name(f'{export_path.name}({counter})')
            counter += 1
        unique_export_path.mkdir(parents=True)
        return unique_export_path

    def _save_error_list(self, export_path: Path, errors_json_file_list: list, errors_original_file_list: list):
        """Save error list files if there are any errors."""
        if len(errors_json_file_list) > 0 or len(errors_original_file_list) > 0:
            export_error_file = {'json_file_name': errors_json_file_list, 'origin_file_name': errors_original_file_list}
            with (export_path / 'error_file_list.json').open('w', encoding='utf-8') as f:
                json.dump(export_error_file, f, indent=4, ensure_ascii=False)

    def get_original_file_name(self, files):
        """Retrieve the original file path from the given file information.

        Args:
            files (dict): A dictionary containing file information

        Returns:
            file_name (str): The original file name extracted from the file information.
        """
        return files['file_name_original']

    def save_original_file(self, result, base_path, error_file_list):
        """Saves the original file.

        Args:
            result (dict): API response data containing file information.
            base_path (Path): The directory where the file will be saved.
            error_file_list (list): A list to store error files.
        """
        file_url = result['files']['url']
        file_name = self.get_original_file_name(result['files'])
        response = requests.get(file_url)
        file_info = {'file_name': file_name}
        error_msg = ''
        try:
            with (base_path / file_name).open('wb') as file:
                file.write(response.content)
            status = ExportStatus.SUCCESS
        except Exception as e:
            error_msg = str(e)
            error_file_list.append([file_name, error_msg])
            status = ExportStatus.FAILED

        self.run.export_log_original_file(result['id'], file_info, status, error_msg)
        return status

    def save_as_json(self, result, base_path, error_file_list):
        """Saves the data as a JSON file.

        Args:
            result (dict): API response data containing file information.
            base_path (Path): The directory where the file will be saved.
            error_file_list (list): A list to store error files.
        """
        file_name = Path(self.get_original_file_name(result['files'])).stem
        json_data = result['data']
        file_info = {'file_name': f'{file_name}.json'}

        if json_data is None:
            error_msg = 'data is Null'
            error_file_list.append([f'{file_name}.json', error_msg])
            status = ExportStatus.FAILED
            self.run.log_export_event('NULL_DATA_DETECTED', result['id'])
            self.run.export_log_json_file(result['id'], file_info, status, error_msg)
            return status

        error_msg = ''
        try:
            with (base_path / f'{file_name}.json').open('w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4, ensure_ascii=False)
            status = ExportStatus.SUCCESS
        except Exception as e:
            error_msg = str(e)
            error_file_list.append([f'{file_name}.json', str(e)])
            status = ExportStatus.FAILED

        self.run.export_log_json_file(result['id'], file_info, status, error_msg)
        return status

    # Abstract methods that should be implemented by subclasses
    def convert_data(self, data):
        """Converts the data. Should be implemented by subclasses."""
        return data

    def before_convert(self, data):
        """Preprocesses the data before conversion. Should be implemented by subclasses."""
        return data

    def after_convert(self, data):
        """Post-processes the data after conversion. Should be implemented by subclasses."""
        return data

    def _process_original_file_saving(
        self, final_data, origin_files_output_path, errors_original_file_list, original_file_metrics_record, no
    ):
        """Process original file saving with metrics tracking.

        Args:
            final_data: Converted data to save
            origin_files_output_path: Path to save original files
            errors_original_file_list: List to collect errors
            original_file_metrics_record: Metrics record for tracking
            no: Current item number for logging

        Returns:
            bool: True if processing should continue, False if should skip to next item
        """
        if no == 1:
            self.run.log_message('Saving original file.')
        original_status = self.save_original_file(final_data, origin_files_output_path, errors_original_file_list)

        original_file_metrics_record.stand_by -= 1
        if original_status == ExportStatus.FAILED:
            original_file_metrics_record.failed += 1
            return False  # Skip to next item
        else:
            original_file_metrics_record.success += 1
            return True  # Continue processing

    def _process_json_file_saving(
        self, final_data, json_output_path, errors_json_file_list, data_file_metrics_record, no
    ):
        """Process JSON file saving with metrics tracking.

        Args:
            final_data: Converted data to save
            json_output_path: Path to save JSON files
            errors_json_file_list: List to collect errors
            data_file_metrics_record: Metrics record for tracking
            no: Current item number for logging

        Returns:
            bool: True if processing should continue, False if should skip to next item
        """
        if no == 1:
            self.run.log_message('Saving json file.')
        data_status = self.save_as_json(final_data, json_output_path, errors_json_file_list)

        data_file_metrics_record.stand_by -= 1
        if data_status == ExportStatus.FAILED:
            data_file_metrics_record.failed += 1
            return False  # Skip to next item
        else:
            data_file_metrics_record.success += 1
            return True  # Continue processing

    def setup_output_directories(self, unique_export_path, save_original_file_flag):
        """Setup output directories for export.

        This method can be overridden by subclasses to customize directory structure.
        The default implementation creates 'json' and 'origin_files' directories.

        Args:
            unique_export_path: Base path for export
            save_original_file_flag: Whether original files will be saved

        Returns:
            dict: Dictionary containing paths for different file types
                 Example: {'json_output_path': Path, 'origin_files_output_path': Path}
        """
        # Path to save JSON files
        json_output_path = unique_export_path / 'json'
        json_output_path.mkdir(parents=True, exist_ok=True)

        output_paths = {'json_output_path': json_output_path}

        # Path to save original files
        if save_original_file_flag:
            origin_files_output_path = unique_export_path / 'origin_files'
            origin_files_output_path.mkdir(parents=True, exist_ok=True)
            output_paths['origin_files_output_path'] = origin_files_output_path

        return output_paths

    def process_data_conversion(self, export_item):
        """Process data conversion pipeline for a single export item.

        This method handles the complete data conversion process:
        before_convert -> convert_data -> after_convert

        Args:
            export_item: Single export item to process

        Returns:
            Final processed data ready for saving
        """
        preprocessed_data = self.before_convert(export_item)
        converted_data = self.convert_data(preprocessed_data)
        final_data = self.after_convert(converted_data)
        return final_data

    def process_file_saving(
        self,
        final_data,
        unique_export_path,
        save_original_file_flag,
        errors_json_file_list,
        errors_original_file_list,
        original_file_metrics_record,
        data_file_metrics_record,
        no,
    ):
        """Process file saving operations for a single export item.

        This method can be overridden by subclasses to implement custom file saving logic.
        The default implementation saves original files and JSON files based on configuration.

        Args:
            final_data: Converted data ready for saving
            unique_export_path: Base path for export
            save_original_file_flag: Whether to save original files
            errors_json_file_list: List to collect JSON file errors
            errors_original_file_list: List to collect original file errors
            original_file_metrics_record: Metrics record for original files
            data_file_metrics_record: Metrics record for JSON files
            no: Current item number for logging

        Returns:
            bool: True if processing should continue, False if should skip to next item
        """
        # Get paths from setup (directories already created)
        json_output_path = unique_export_path / 'json'
        origin_files_output_path = unique_export_path / 'origin_files' if save_original_file_flag else None

        if save_original_file_flag:
            should_continue = self._process_original_file_saving(
                final_data, origin_files_output_path, errors_original_file_list, original_file_metrics_record, no
            )
            if not should_continue:
                return False

        self.run.log_metrics(record=original_file_metrics_record, category='original_file')

        # Extract data as JSON files
        should_continue = self._process_json_file_saving(
            final_data, json_output_path, errors_json_file_list, data_file_metrics_record, no
        )
        if not should_continue:
            return False

        self.run.log_metrics(record=data_file_metrics_record, category='data_file')

        return True

    def additional_file_saving(self, unique_export_path):
        """Save additional files after processing all export items.

        This method is called after the main export loop completes and is intended
        for saving files that need to be created based on the collective data from
        all processed export items (e.g., metadata files, configuration files,
        summary files, etc.).

        Args:
            unique_export_path (str): The unique export directory path where
                additional files should be saved.
        """
        pass

    def export(self, export_items=None, results=None, **_kwargs) -> dict:
        """Main export method that can be overridden by subclasses for custom logic.

        This default implementation provides standard file saving functionality.
        Subclasses can override this method to implement custom export logic
        while still using the helper methods for specific operations.


        Subclasses can override process_file_saving() method to implement custom file saving logic.

        Args:
            export_items: Optional export items to process. If not provided, uses self.export_items.
            results: Optional results data to process alongside export_items.
            **kwargs: Additional parameters for export customization.

        Returns:
            dict: Export result containing export path and status information.
        """
        # Use provided export_items or fall back to instance variable
        items_to_process = export_items if export_items is not None else self.export_items

        unique_export_path = self._create_unique_export_path(self.params['name'])

        self.run.log_message('Starting export process.')

        save_original_file_flag = self.params.get('save_original_file')
        errors_json_file_list = []
        errors_original_file_list = []

        # Setup output directories (can be customized by subclasses)
        self.setup_output_directories(unique_export_path, save_original_file_flag)

        total = self.params['count']

        original_file_metrics_record = self.run.MetricsRecord(stand_by=total, success=0, failed=0)
        data_file_metrics_record = self.run.MetricsRecord(stand_by=total, success=0, failed=0)

        # progress init
        self.run.set_progress(0, total, category='dataset_conversion')

        for no, export_item in enumerate(items_to_process, start=1):
            self.run.set_progress(min(no, total), total, category='dataset_conversion')
            if no == 1:
                self.run.log_message('Converting dataset.')

            final_data = self.process_data_conversion(export_item)

            # Process file saving (can be overridden by subclasses)
            should_continue = self.process_file_saving(
                final_data,
                unique_export_path,
                save_original_file_flag,
                errors_json_file_list,
                errors_original_file_list,
                original_file_metrics_record,
                data_file_metrics_record,
                no,
            )
            if not should_continue:
                continue

        self.additional_file_saving(unique_export_path)
        self.run.end_log()

        # Save error list files
        self._save_error_list(unique_export_path, errors_json_file_list, errors_original_file_list)

        return {'export_path': str(self.path_root)}
