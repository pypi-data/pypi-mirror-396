"""Tests for file discovery strategies."""

import tempfile
from pathlib import Path

import pytest

from synapse_sdk.plugins.categories.upload.actions.upload.strategies.file_discovery.flat import (
    FlatFileDiscoveryStrategy,
)
from synapse_sdk.plugins.categories.upload.actions.upload.strategies.file_discovery.recursive import (
    RecursiveFileDiscoveryStrategy,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)

        # Create directory structure
        image_dir = base / 'image_1'
        image_dir.mkdir()
        meta_dir = base / 'image_meta_1'
        meta_dir.mkdir()
        text_dir = base / 'text_meta_1'
        text_dir.mkdir()

        # Create test files with same stems
        (image_dir / 'file_001.jpg').write_text('image1')
        (image_dir / 'file_002.jpg').write_text('image2')
        (meta_dir / 'file_001.xml').write_text('meta1')
        (text_dir / 'file_002.txt').write_text('text2')

        # Create system files (should be excluded)
        (image_dir / '.DS_Store').write_text('system')
        (meta_dir / 'Thumbs.db').write_text('system')

        yield base


class TestRecursiveFileDiscoveryStrategy:
    """Test RecursiveFileDiscoveryStrategy."""

    def test_discover_excludes_system_directories(self, temp_dir):
        """Test that system directories are excluded during discovery."""
        strategy = RecursiveFileDiscoveryStrategy()

        # Create @eaDir system directory
        eadir = temp_dir / 'image_1' / '@eaDir'
        eadir.mkdir()
        (eadir / 'thumbnail.jpg').write_text('thumb')

        files = strategy.discover(temp_dir / 'image_1', recursive=True)

        # Should not include files from @eaDir
        file_names = [f.name for f in files]
        assert 'thumbnail.jpg' not in file_names
        assert '.DS_Store' not in file_names
        assert 'file_001.jpg' in file_names

    def test_organize_groups_matching_stems(self, temp_dir):
        """Test that files with matching stems are grouped together."""
        strategy = RecursiveFileDiscoveryStrategy()

        # Collect all files
        all_files = []
        all_files.extend(strategy.discover(temp_dir / 'image_1', recursive=True))
        all_files.extend(strategy.discover(temp_dir / 'image_meta_1', recursive=True))
        all_files.extend(strategy.discover(temp_dir / 'text_meta_1', recursive=True))

        specs = [
            {'name': 'image_1', 'is_required': True},
            {'name': 'image_meta_1', 'is_required': False},
            {'name': 'text_meta_1', 'is_required': False},
        ]

        type_dirs = {
            'image_1': temp_dir / 'image_1',
            'image_meta_1': temp_dir / 'image_meta_1',
            'text_meta_1': temp_dir / 'text_meta_1',
        }

        organized = strategy.organize(all_files, specs, {}, type_dirs)

        # Should create 2 data units (file_001 and file_002)
        assert len(organized) == 2

        # Find file_001 group
        file_001_group = next(g for g in organized if 'file_001' in str(g['files'].get('image_1', '')))
        assert 'image_1' in file_001_group['files']
        assert 'image_meta_1' in file_001_group['files']  # Optional, but matching stem
        assert 'text_meta_1' not in file_001_group['files']  # No matching file

        # Find file_002 group
        file_002_group = next(g for g in organized if 'file_002' in str(g['files'].get('image_1', '')))
        assert 'image_1' in file_002_group['files']
        assert 'image_meta_1' not in file_002_group['files']  # No matching file
        assert 'text_meta_1' in file_002_group['files']  # Optional, but matching stem

    def test_organize_skips_optional_only_files(self, temp_dir):
        """Test that files with only optional specs are skipped."""
        strategy = RecursiveFileDiscoveryStrategy()

        # Create file that only exists in optional spec
        text_dir = temp_dir / 'text_meta_1'
        (text_dir / 'file_003.txt').write_text('text3')

        all_files = []
        all_files.extend(strategy.discover(temp_dir / 'image_1', recursive=True))
        all_files.extend(strategy.discover(temp_dir / 'text_meta_1', recursive=True))

        specs = [
            {'name': 'image_1', 'is_required': True},
            {'name': 'text_meta_1', 'is_required': False},
        ]

        type_dirs = {
            'image_1': temp_dir / 'image_1',
            'text_meta_1': temp_dir / 'text_meta_1',
        }

        organized = strategy.organize(all_files, specs, {}, type_dirs)

        # Should only create 2 data units (file_001, file_002), NOT file_003
        assert len(organized) == 2

        # Verify file_003 is not in any group
        for group in organized:
            files = group['files']
            for file_path in files.values():
                assert 'file_003' not in str(file_path)

    def test_origin_file_stem_extraction(self, temp_dir):
        """Test that origin_file_stem is correctly extracted from complex filenames."""
        strategy = RecursiveFileDiscoveryStrategy()

        # Create files with underscores in names
        image_dir = temp_dir / 'image_1'
        (image_dir / 'DJI_20250519161858_0009.jpg').write_text('image')

        all_files = strategy.discover(image_dir, recursive=True)

        specs = [{'name': 'image_1', 'is_required': True}]
        type_dirs = {'image_1': image_dir}

        organized = strategy.organize(all_files, specs, {}, type_dirs)

        # Should have 3 data units (file_001, file_002, DJI_20250519161858_0009)
        assert len(organized) == 3

        # Find the DJI file group
        dji_group = next((g for g in organized if 'DJI' in g['meta']['origin_file_stem']), None)
        assert dji_group is not None
        # Should extract full stem, not just last part after underscore
        assert dji_group['meta']['origin_file_stem'] == 'DJI_20250519161858_0009'


class TestFlatFileDiscoveryStrategy:
    """Test FlatFileDiscoveryStrategy."""

    def test_discover_excludes_system_files(self, temp_dir):
        """Test that system files are excluded during discovery."""
        strategy = FlatFileDiscoveryStrategy()

        files = strategy.discover(temp_dir / 'image_1', recursive=False)

        # Should not include system files
        file_names = [f.name for f in files]
        assert '.DS_Store' not in file_names
        assert 'Thumbs.db' not in file_names
        assert 'file_001.jpg' in file_names

    def test_organize_groups_by_stem(self, temp_dir):
        """Test that files are grouped by stem in flat mode."""
        strategy = FlatFileDiscoveryStrategy()

        all_files = []
        all_files.extend(strategy.discover(temp_dir / 'image_1', recursive=False))
        all_files.extend(strategy.discover(temp_dir / 'image_meta_1', recursive=False))

        specs = [
            {'name': 'image_1', 'is_required': True},
            {'name': 'image_meta_1', 'is_required': False},
        ]

        type_dirs = {
            'image_1': temp_dir / 'image_1',
            'image_meta_1': temp_dir / 'image_meta_1',
        }

        organized = strategy.organize(all_files, specs, {}, type_dirs)

        # Should create 2 data units
        assert len(organized) == 2

        # Verify file_001 group includes optional matching file
        file_001_group = next(g for g in organized if g['meta']['origin_file_stem'] == 'file_001')
        assert 'image_1' in file_001_group['files']
        assert 'image_meta_1' in file_001_group['files']

    def test_discover_recursive_mode(self, temp_dir):
        """Test that recursive mode discovers files in subdirectories."""
        strategy = FlatFileDiscoveryStrategy()

        # Create nested directory structure
        image_dir = temp_dir / 'image_1'
        sub_dir = image_dir / 'subdir'
        sub_dir.mkdir()
        (sub_dir / 'nested_file.jpg').write_text('nested')

        # Non-recursive should only find files in root
        files_flat = strategy.discover(image_dir, recursive=False)
        file_names_flat = [f.name for f in files_flat]
        assert 'nested_file.jpg' not in file_names_flat
        assert 'file_001.jpg' in file_names_flat

        # Recursive should find files in subdirectories
        files_recursive = strategy.discover(image_dir, recursive=True)
        file_names_recursive = [f.name for f in files_recursive]
        assert 'nested_file.jpg' in file_names_recursive
        assert 'file_001.jpg' in file_names_recursive

    def test_discover_recursive_excludes_system_directories(self, temp_dir):
        """Test that recursive mode excludes system directories."""
        strategy = FlatFileDiscoveryStrategy()

        image_dir = temp_dir / 'image_1'

        # Create system directory
        eadir = image_dir / '@eaDir'
        eadir.mkdir()
        (eadir / 'thumbnail.jpg').write_text('thumb')

        files = strategy.discover(image_dir, recursive=True)
        file_names = [f.name for f in files]

        # Should not include files from @eaDir
        assert 'thumbnail.jpg' not in file_names
        assert 'file_001.jpg' in file_names

    def test_organize_recursive_files_in_subdirectories(self, temp_dir):
        """Test that organize works with files discovered recursively in subdirectories."""
        strategy = FlatFileDiscoveryStrategy()

        # Create directory structure with nested files
        text_dir = temp_dir / 'text_1'
        text_dir.mkdir()
        sub_dir = text_dir / 'subdir'
        sub_dir.mkdir()

        # Create files in both root and subdirectory
        (text_dir / 'file_001.txt').write_text('root file')
        (sub_dir / 'file_002.txt').write_text('nested file')

        # Discover files recursively
        files = strategy.discover(text_dir, recursive=True)
        assert len(files) == 2

        # Organize files
        specs = [{'name': 'text_1', 'file_type': 'text', 'is_required': True}]
        type_dirs = {'text_1': text_dir}
        organized = strategy.organize(files, specs, {}, type_dirs)

        # Should have 2 organized groups (one for each file)
        assert len(organized) == 2
        file_stems = [g['meta']['origin_file_stem'] for g in organized]
        assert 'file_001' in file_stems
        assert 'file_002' in file_stems
