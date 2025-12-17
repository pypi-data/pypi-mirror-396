from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..base import FileDiscoveryStrategy


class RecursiveFileDiscoveryStrategy(FileDiscoveryStrategy):
    """Recursive file discovery strategy."""

    def discover(self, path: Path, recursive: bool) -> List[Path]:
        """Discover files recursively in the given path."""
        # Exclude system directories
        excluded_dirs = {'@eaDir', '.@__thumb', '@Recycle', '#recycle', '.DS_Store', 'Thumbs.db', '.synology'}

        def exclude_dirs(file_path: Path) -> bool:
            """Check if file path contains excluded directories."""
            return any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs)

        return [file_path for file_path in path.rglob('*') if file_path.is_file() and not exclude_dirs(file_path)]

    def organize(self, files: List[Path], specs: Dict, metadata: Dict, type_dirs: Dict = None) -> List[Dict]:
        """Organize files according to specifications with metadata."""
        organized_files = []

        # Use provided type_dirs or create fallback mapping
        if type_dirs is None:
            type_dirs = {}
            for spec in specs:
                spec_name = spec['name']
                # Fallback: extract spec directory from file paths
                for file_path in files:
                    # Check if this file's path contains the spec_name as a directory
                    path_parts = file_path.parts
                    if spec_name in path_parts:
                        # Find the index of spec_name and reconstruct the path up to that directory
                        spec_index = path_parts.index(spec_name)
                        spec_dir = Path(*path_parts[: spec_index + 1])
                        if spec_dir.exists() and spec_dir.is_dir():
                            type_dirs[spec_name] = spec_dir
                            break

        if not type_dirs:
            return organized_files

        # Performance optimization 1: Path caching - avoid repeated string conversions
        path_cache = {dir_path: str(dir_path) for dir_path in type_dirs.values()}

        # Performance optimization 2: Build metadata index for faster lookups
        metadata_index = self._build_metadata_index(metadata)

        # Group files by dataset_key (stem-based matching)
        # Strategy:
        # 1. Group all files (required + optional) by their file stem
        # 2. Only create data units for groups that have ALL required files
        # 3. Optional files are automatically included if they match the stem
        dataset_files = {}
        required_specs = [spec['name'] for spec in specs if spec.get('is_required', False)]

        for file_path in files:
            # Find all matching directories for this file
            matched_specs = []
            for spec_name, dir_path in type_dirs.items():
                # Check if file is under this spec's directory
                # Use try/except for relative_to to ensure proper path matching
                try:
                    relative_path = file_path.relative_to(dir_path)
                    matched_specs.append((spec_name, dir_path, relative_path))
                except ValueError:
                    # File is not under this directory
                    continue

            # If no matches found, skip this file
            if not matched_specs:
                continue

            # Select the most specific (deepest) directory match
            # This prevents files in subdirectories from being assigned to parent directory specs
            best_match = max(matched_specs, key=lambda x: len(x[1].parts))
            spec_name, dir_path, relative_path = best_match

            # Create unique dataset key using relative path from spec directory
            # Use parent directory + stem as unique key to group related files
            if relative_path.parent != Path('.'):
                dataset_key = f'{relative_path.parent}_{file_path.stem}'
            else:
                dataset_key = file_path.stem

            if dataset_key not in dataset_files:
                dataset_files[dataset_key] = {}

            if spec_name not in dataset_files[dataset_key]:
                dataset_files[dataset_key][spec_name] = file_path
            else:
                # Keep the most recent file - only stat when needed
                existing_file = dataset_files[dataset_key][spec_name]
                try:
                    if file_path.stat().st_mtime > existing_file.stat().st_mtime:
                        dataset_files[dataset_key][spec_name] = file_path
                except (OSError, IOError):
                    # If stat fails, keep existing file
                    pass

        # Create organized files ONLY for datasets with ALL required files
        # Optional files are included automatically if they match the stem
        for dataset_key, files_dict in sorted(dataset_files.items()):
            # Check if all required files are present
            has_all_required = all(req in files_dict for req in required_specs)

            if has_all_required:
                # Extract original file stem from actual file paths (more reliable than parsing dataset_key)
                # Collect stems from all files in the group
                file_stems = {}
                file_extensions = {}

                for file_path in files_dict.values():
                    stem = file_path.stem
                    ext = file_path.suffix.lower()

                    # Count stems (to handle multiple files with slightly different names)
                    if stem:
                        file_stems[stem] = file_stems.get(stem, 0) + 1

                    # Count extensions
                    if ext:
                        file_extensions[ext] = file_extensions.get(ext, 0) + 1

                # Use the most common stem (usually they're all the same)
                original_stem = max(file_stems, key=file_stems.get) if file_stems else dataset_key
                origin_file_extension = max(file_extensions, key=file_extensions.get) if file_extensions else ''

                meta_data = {
                    'origin_file_stem': original_stem,
                    'origin_file_extension': origin_file_extension,
                    'created_at': datetime.now().isoformat(),
                    'dataset_key': dataset_key,  # Add dataset key for debugging
                }

                # Add metadata if available - using optimized index lookup
                if metadata_index:
                    matched_metadata = self._find_matching_metadata_optimized(original_stem, files_dict, metadata_index)
                    if matched_metadata:
                        meta_data.update(matched_metadata)

                organized_files.append({'files': files_dict, 'meta': meta_data})

        return organized_files

    def _build_metadata_index(self, metadata: Dict) -> Dict:
        """Build metadata index for faster lookups."""
        if not metadata:
            return {}

        metadata_index = {'exact_stem': {}, 'exact_name': {}, 'stem_lookup': {}, 'partial_paths': {}, 'full_paths': {}}

        for meta_key, meta_value in metadata.items():
            meta_path = Path(meta_key)

            # Index by stem
            stem = meta_path.stem
            if stem:
                metadata_index['exact_stem'][stem] = meta_value
                metadata_index['stem_lookup'][stem] = meta_value

            # Index by full name
            name = meta_path.name
            if name:
                metadata_index['exact_name'][name] = meta_value

            # Index for partial path matching
            metadata_index['partial_paths'][meta_key] = meta_value

            # Index for full path matching
            metadata_index['full_paths'][meta_key] = meta_value

        return metadata_index

    def _find_matching_metadata_optimized(self, file_name: str, files_dict: Dict, metadata_index: Dict) -> Dict:
        """Find matching metadata using optimized index lookups."""
        if not metadata_index:
            return {}

        # Strategy 1: Exact stem match (O(1) lookup)
        if file_name in metadata_index['exact_stem']:
            return metadata_index['exact_stem'][file_name]

        # Strategy 2: Exact filename match with extension (O(1) lookup)
        sample_file = list(files_dict.values())[0] if files_dict else None
        if sample_file:
            full_filename = f'{file_name}{sample_file.suffix}'
            if full_filename in metadata_index['exact_name']:
                return metadata_index['exact_name'][full_filename]

            # Try sample file name
            sample_filename = sample_file.name
            if sample_filename in metadata_index['exact_name']:
                return metadata_index['exact_name'][sample_filename]

        # Strategy 3: Stem lookup (already optimized above)
        # This is covered by exact_stem lookup

        # Strategy 4 & 5: Partial and full path matching (fallback to original logic for complex cases)
        if sample_file:
            file_path_str = str(sample_file)
            file_path_posix = sample_file.as_posix()

            # Check partial paths
            for meta_key in metadata_index['partial_paths']:
                if (
                    meta_key in file_path_str
                    or meta_key in file_path_posix
                    or file_path_str in meta_key
                    or file_path_posix in meta_key
                ):
                    return metadata_index['partial_paths'][meta_key]

        return {}

    def _find_matching_metadata(self, file_name: str, files_dict: Dict, metadata: Dict) -> Dict:
        """Find matching metadata using comprehensive pattern matching.

        Matching priority:
        1. Exact stem match (highest priority)
        2. Exact filename match (with extension)
        3. Metadata key stem matches file stem
        4. Partial path matching
        5. Full path matching
        """
        if not metadata:
            return {}

        # Get sample file for extension and path information
        sample_file = list(files_dict.values())[0] if files_dict else None

        # Strategy 1: Exact stem match (highest priority)
        if file_name in metadata:
            return metadata[file_name]

        # Strategy 2: Exact filename match (with extension)
        if sample_file:
            full_filename = f'{file_name}{sample_file.suffix}'
            if full_filename in metadata:
                return metadata[full_filename]

            # Also try with sample file name
            sample_filename = sample_file.name
            if sample_filename in metadata:
                return metadata[sample_filename]

        # Strategy 3: Metadata key stem matches file stem
        for meta_key in metadata.keys():
            meta_stem = Path(meta_key).stem
            if meta_stem == file_name:
                return metadata[meta_key]

        # Strategy 4: Partial path matching
        if sample_file:
            file_path_parts = sample_file.parts
            for meta_key in metadata.keys():
                meta_path = Path(meta_key)
                # Check if any part of the metadata key matches our file path parts
                for part in file_path_parts:
                    if part in str(meta_path) or str(meta_path) in part:
                        # Additional validation: ensure it's a reasonable match
                        if meta_path.stem == file_name or meta_path.name == sample_file.name or part == meta_path.stem:
                            return metadata[meta_key]

        # Strategy 5: Full path matching
        if sample_file:
            full_path_str = str(sample_file)
            full_path_posix = sample_file.as_posix()

            for meta_key in metadata.keys():
                # Direct path match
                if meta_key == full_path_str or meta_key == full_path_posix:
                    return metadata[meta_key]

                # Relative path match (check if meta_key is contained in our path)
                if meta_key in full_path_str or meta_key in full_path_posix:
                    return metadata[meta_key]

                # Reverse match (check if our path is contained in meta_key)
                if full_path_str in meta_key or full_path_posix in meta_key:
                    return metadata[meta_key]

        # No match found
        return {}
