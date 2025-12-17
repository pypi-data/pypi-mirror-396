from ..context import StepResult, UploadContext
from ..enums import LogCode
from .base import BaseStep


class OrganizeFilesStep(BaseStep):
    """Organize files according to specifications using file discovery strategy."""

    @property
    def name(self) -> str:
        return 'organize_files'

    @property
    def progress_weight(self) -> float:
        return 0.15

    def execute(self, context: UploadContext) -> StepResult:
        """Execute file organization step."""
        file_discovery_strategy = context.strategies.get('file_discovery')
        if not file_discovery_strategy:
            return self.create_error_result('File discovery strategy not found')

        if not context.file_specifications:
            return self.create_error_result('File specifications not available')

        try:
            # Check which mode we're in
            use_single_path = context.get_param('use_single_path', True)

            if use_single_path:
                # Single path mode: all assets use same base path
                return self._execute_single_path_mode(context, file_discovery_strategy)
            else:
                # Multi-path mode: each asset has its own path
                return self._execute_multi_path_mode(context, file_discovery_strategy)

        except Exception as e:
            return self.create_error_result(f'File organization failed: {str(e)}')

    def _execute_single_path_mode(self, context: UploadContext, file_discovery_strategy) -> StepResult:
        """Execute file organization in single path mode (traditional)."""
        # Create type directories mapping
        type_dirs = {}
        for spec in context.file_specifications:
            spec_name = spec['name']
            spec_dir = context.pathlib_cwd / spec_name
            if spec_dir.exists() and spec_dir.is_dir():
                type_dirs[spec_name] = spec_dir

        if type_dirs:
            context.run.log_message_with_code(LogCode.TYPE_DIRECTORIES_FOUND, list(type_dirs.keys()))
        else:
            context.run.log_message_with_code(LogCode.NO_TYPE_DIRECTORIES)
            return self.create_success_result(data={'organized_files': []})

        context.run.log_message_with_code(LogCode.TYPE_STRUCTURE_DETECTED)
        context.run.log_message_with_code(LogCode.FILE_ORGANIZATION_STARTED)

        # Discover files in type directories
        all_files = []
        is_recursive = context.get_param('is_recursive', True)

        for spec_name, dir_path in type_dirs.items():
            files_in_dir = file_discovery_strategy.discover(dir_path, is_recursive)
            all_files.extend(files_in_dir)

        if not all_files:
            context.run.log_message_with_code(LogCode.NO_FILES_FOUND_WARNING)
            return self.create_success_result(data={'organized_files': []})

        # Organize files using strategy
        organized_files = file_discovery_strategy.organize(
            all_files, context.file_specifications, context.metadata or {}, type_dirs
        )

        if organized_files:
            context.run.log_message_with_code(LogCode.FILES_DISCOVERED, len(organized_files))
            context.add_organized_files(organized_files)

        return self.create_success_result(
            data={'organized_files': organized_files},
            rollback_data={'files_count': len(organized_files), 'type_dirs': list(type_dirs.keys())},
        )

    def _execute_multi_path_mode(self, context: UploadContext, file_discovery_strategy) -> StepResult:
        """Execute file organization in multi-path mode (each asset has own path)."""
        from synapse_sdk.utils.storage import get_pathlib

        assets = context.get_param('assets', {})
        if not assets:
            return self.create_error_result('Multi-path mode requires assets configuration')

        # Validate that all required specs have asset paths
        required_specs = [spec['name'] for spec in context.file_specifications if spec.get('is_required', False)]
        missing_required = [spec for spec in required_specs if spec not in assets]

        if missing_required:
            return self.create_error_result(
                f'Multi-path mode requires asset paths for required specs: {", ".join(missing_required)}'
            )

        context.run.log_message_with_code(LogCode.MULTI_PATH_MODE_ENABLED, len(assets))
        context.run.log_message_with_code(LogCode.FILE_ORGANIZATION_STARTED)

        # Collect all files and specs first
        all_files = []
        type_dirs = {}
        specs_with_files = []

        for spec in context.file_specifications:
            spec_name = spec['name']
            is_required = spec.get('is_required', False)

            # Skip if no asset configuration for this spec (only allowed for optional specs)
            if spec_name not in assets:
                if is_required:
                    # This should not happen due to validation above, but double-check
                    return self.create_error_result(f'Required spec {spec_name} missing asset path')
                context.run.log_message_with_code(LogCode.OPTIONAL_SPEC_SKIPPED, spec_name)
                continue

            asset_config = assets[spec_name]

            # Get the asset path from storage
            try:
                asset_path = get_pathlib(context.storage, asset_config.get('path', ''))
                type_dirs[spec_name] = asset_path
            except Exception as e:
                context.run.log_message_with_code(LogCode.ASSET_PATH_ACCESS_ERROR, spec_name, str(e))
                continue

            if not asset_path.exists():
                context.run.log_message_with_code(LogCode.ASSET_PATH_NOT_FOUND, spec_name, asset_config.get('path', ''))
                continue

            # Discover files for this asset
            is_recursive = asset_config.get('is_recursive', True)
            context.run.log_message_with_code(LogCode.DISCOVERING_FILES_FOR_ASSET, spec_name, is_recursive)

            files = file_discovery_strategy.discover(asset_path, is_recursive)

            if not files:
                context.run.log_message_with_code(LogCode.NO_FILES_FOUND_FOR_ASSET, spec_name)
                continue

            all_files.extend(files)
            specs_with_files.append(spec)
            context.run.log_message_with_code(LogCode.FILES_FOUND_FOR_ASSET, len(files), spec_name)

        # Organize all files together to group by dataset_key
        all_organized_files = []
        if all_files and specs_with_files:
            context.run.log_message_with_code(
                LogCode.ORGANIZING_FILES_MULTI_PATH, len(all_files), len(specs_with_files)
            )
            context.run.log_message_with_code(LogCode.TYPE_DIRECTORIES_MULTI_PATH, list(type_dirs.keys()))

            all_organized_files = file_discovery_strategy.organize(
                all_files, specs_with_files, context.metadata or {}, type_dirs
            )

        if all_organized_files:
            context.run.log_message_with_code(LogCode.FILES_DISCOVERED, len(all_organized_files))
            context.run.log_message_with_code(
                LogCode.DATA_UNITS_CREATED_FROM_FILES, len(all_organized_files), len(all_files)
            )
            context.add_organized_files(all_organized_files)
        else:
            context.run.log_message_with_code(LogCode.NO_FILES_FOUND_WARNING)

        return self.create_success_result(
            data={'organized_files': all_organized_files},
            rollback_data={'files_count': len(all_organized_files), 'type_dirs': list(type_dirs.keys())},
        )

    def can_skip(self, context: UploadContext) -> bool:
        """File organization cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback file organization."""
        # Clear organized files
        context.organized_files.clear()
        context.run.log_message_with_code(LogCode.ROLLBACK_FILE_ORGANIZATION)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for file organization."""
        use_single_path = context.get_param('use_single_path', True)

        # In single-path mode, pathlib_cwd is required
        if use_single_path and not context.pathlib_cwd:
            raise ValueError('Working directory path not set in single-path mode')

        # In multi-path mode, pathlib_cwd is optional (each asset has its own path)
        if not use_single_path:
            assets = context.get_param('assets', {})
            if not assets:
                raise ValueError('Multi-path mode requires assets configuration')

        if not context.file_specifications:
            raise ValueError('File specifications not available')
