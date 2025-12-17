"""Tests for extension filtering functionality in BaseUploader."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from synapse_sdk.plugins.categories.upload.actions.upload.enums import LogCode
from synapse_sdk.plugins.categories.upload.templates.plugin import BaseUploader


class TestExtensionFiltering:
    """Test extension filtering functionality."""

    @pytest.fixture
    def mock_run(self):
        """Create a mock run object."""
        run = Mock()
        run.log_message_with_code = Mock()
        run.log_message = Mock()
        return run

    @pytest.fixture
    def base_uploader(self, mock_run, tmp_path):
        """Create a BaseUploader instance for testing."""
        uploader = BaseUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )
        return uploader

    @pytest.fixture
    def sample_organized_files(self, tmp_path):
        """Create sample organized files for testing."""
        return [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': tmp_path / 'video2.MP4'}},
            {'files': {'video': tmp_path / 'video3.avi'}},
            {'files': {'video': tmp_path / 'video4.mkv'}},
            {'files': {'video': tmp_path / 'video5.webm'}},
            {'files': {'video': tmp_path / 'audio.mp3'}},
        ]

    def test_default_backend_config(self, base_uploader):
        """Test that backend default configuration is used when allowed_extensions is None."""
        config = base_uploader.get_file_extensions_config()

        # Verify backend defaults
        assert config['video'] == ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        assert config['image'] == ['.jpg', '.jpeg', '.png']
        assert config['audio'] == ['.mp3', '.wav']
        assert config['pcd'] == ['.pcd']
        assert config['text'] == ['.txt', '.html']
        assert config['data'] == ['.xml', '.bin', '.json', '.fbx']

    def test_method_override(self, mock_run, tmp_path):
        """Test that overriding get_file_extensions_config() works."""

        class CustomUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4', '.avi']}

        uploader = CustomUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        config = uploader.get_file_extensions_config()
        assert config == {'video': ['.mp4', '.avi']}

    def test_validate_with_backend_defaults(self, base_uploader, sample_organized_files):
        """Test validation with backend default configuration."""
        result = base_uploader.validate_file_types(sample_organized_files)

        # Backend default allows .mp4, .avi, .mkv, .webm for video
        # Should filter out .mp3 (audio file)
        assert len(result) == 5

    def test_validate_with_restricted_extensions(self, mock_run, tmp_path, sample_organized_files):
        """Test validation with restricted extensions."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}  # Only MP4 allowed

        uploader = RestrictedUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        result = uploader.validate_file_types(sample_organized_files)

        # Only .mp4 files should pass
        assert len(result) == 2  # video1.mp4 and video2.MP4

    def test_case_insensitive_matching(self, mock_run, tmp_path):
        """Test that extension matching is case-insensitive."""

        class VideoUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}

        uploader = VideoUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': tmp_path / 'video2.MP4'}},
            {'files': {'video': tmp_path / 'video3.Mp4'}},
            {'files': {'video': tmp_path / 'video4.mP4'}},
        ]

        result = uploader.validate_file_types(organized_files)

        # All should pass (case-insensitive)
        assert len(result) == 4

    def test_logging_filtered_files(self, mock_run, tmp_path):
        """Test that filtered files are logged correctly."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}

        uploader = RestrictedUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': tmp_path / 'video2.avi'}},
            {'files': {'video': tmp_path / 'video3.mkv'}},
        ]

        result = uploader.validate_file_types(organized_files)

        # Verify logging was called
        mock_run.log_message_with_code.assert_called_once()
        call_args = mock_run.log_message_with_code.call_args[0]

        assert call_args[0] == LogCode.FILES_FILTERED_BY_EXTENSION
        assert call_args[1] == 2  # 2 files filtered
        assert call_args[2] == 'video'  # file type

    def test_multiple_file_types(self, mock_run, tmp_path):
        """Test filtering with multiple file types (both required)."""

        class MultiTypeUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg']}

        uploader = MultiTypeUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'image', 'file_type': 'image', 'is_required': True},
            ],
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4', 'image': tmp_path / 'image1.jpg'}},
            {'files': {'video': tmp_path / 'video2.avi', 'image': tmp_path / 'image2.jpg'}},
            {'files': {'video': tmp_path / 'video3.mp4', 'image': tmp_path / 'image3.png'}},
        ]

        result = uploader.validate_file_types(organized_files)

        # Only first group should pass (both files valid and required)
        assert len(result) == 1

    def test_file_type_not_in_config(self, mock_run, tmp_path):
        """Test handling when file type is not in config."""

        class PartialUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}  # Only video configured

        uploader = PartialUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video'},
                {'name': 'unknown', 'file_type': 'unknown'},
            ],
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'unknown': tmp_path / 'unknown.xyz'}},  # Unknown type
        ]

        result = uploader.validate_file_types(organized_files)

        # Video should pass, unknown should also pass (no restriction)
        assert len(result) == 2

    def test_empty_extensions_config(self, mock_run, tmp_path):
        """Test with empty extensions list (filter all)."""

        class EmptyUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': []}  # Empty = filter all

        uploader = EmptyUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': tmp_path / 'video2.avi'}},
        ]

        result = uploader.validate_file_types(organized_files)

        # All should be filtered
        assert len(result) == 0

    def test_file_without_extension(self, mock_run, tmp_path):
        """Test handling of files without extensions."""

        class VideoUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}

        uploader = VideoUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': tmp_path / 'video_no_ext'}},
        ]

        result = uploader.validate_file_types(organized_files)

        # Only .mp4 should pass
        assert len(result) == 1

    def test_file_path_as_list(self, mock_run, tmp_path):
        """Test handling of file paths provided as lists."""

        class VideoUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}

        uploader = VideoUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': [tmp_path / 'video1.mp4']}},  # List with one item
            {'files': {'video': [tmp_path / 'video2.avi']}},
        ]

        result = uploader.validate_file_types(organized_files)

        # Only .mp4 should pass
        assert len(result) == 1

    def test_none_file_path(self, mock_run, tmp_path):
        """Test handling of None file paths."""

        class VideoUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4']}

        uploader = VideoUploader(
            run=mock_run, path=tmp_path, file_specification=[{'name': 'video', 'file_type': 'video'}]
        )

        organized_files = [
            {'files': {'video': tmp_path / 'video1.mp4'}},
            {'files': {'video': None}},  # None path
        ]

        result = uploader.validate_file_types(organized_files)

        # Should handle None gracefully
        assert len(result) >= 1


class TestMainFilePriority:
    """Test main file priority functionality (SYN-5972)."""

    @pytest.fixture
    def mock_run(self):
        """Create a mock run object."""
        run = Mock()
        run.log_message_with_code = Mock()
        run.log_message = Mock()
        return run

    def test_main_file_uploaded_when_sub_file_filtered(self, mock_run, tmp_path):
        """TC1: Main file should be uploaded even when sub file is filtered."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {'video': tmp_path / 'sample.mp4', 'thumbnail': tmp_path / 'sample.gif'},
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Only video uploaded, thumbnail filtered
        assert len(result) == 1
        assert 'video' in result[0]['files']
        assert 'thumbnail' not in result[0]['files']
        assert result[0]['files']['video'] == tmp_path / 'sample.mp4'

    def test_main_file_uploaded_when_all_sub_files_filtered(self, mock_run, tmp_path):
        """TC2: Main file should be uploaded even when all sub files are filtered."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png'], 'text': ['.txt']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
                {'name': 'subtitle', 'file_type': 'text', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {
                    'video': tmp_path / 'sample.mp4',
                    'thumbnail': tmp_path / 'sample.gif',
                    'subtitle': tmp_path / 'sample.srt',
                },
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Only video uploaded
        assert len(result) == 1
        assert result[0]['files'] == {'video': tmp_path / 'sample.mp4'}

    def test_entire_group_filtered_when_main_file_invalid(self, mock_run, tmp_path):
        """TC3: Entire group should be filtered when main file is invalid."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {'video': tmp_path / 'sample.avi', 'thumbnail': tmp_path / 'sample.jpg'},
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Entire group filtered (no valid main file)
        assert len(result) == 0

    def test_entire_group_filtered_when_all_files_invalid(self, mock_run, tmp_path):
        """TC4: Entire group should be filtered when all files are invalid."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {'video': tmp_path / 'sample.avi', 'thumbnail': tmp_path / 'sample.gif'},
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Entire group filtered
        assert len(result) == 0

    def test_multiple_groups_with_mixed_validity(self, mock_run, tmp_path):
        """TC5: Multiple groups with different validation states."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {  # Group 1: Main valid, sub invalid
                'files': {'video': tmp_path / 'sample1.mp4', 'thumbnail': tmp_path / 'sample1.gif'},
                'meta': {'dataset_key': 'sample1'},
            },
            {  # Group 2: All valid
                'files': {'video': tmp_path / 'sample2.mp4', 'thumbnail': tmp_path / 'sample2.jpg'},
                'meta': {'dataset_key': 'sample2'},
            },
            {  # Group 3: Main invalid, sub valid
                'files': {'video': tmp_path / 'sample3.avi', 'thumbnail': tmp_path / 'sample3.jpg'},
                'meta': {'dataset_key': 'sample3'},
            },
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Group 1 (video only), Group 2 (both), Group 3 filtered
        assert len(result) == 2

        # Group 1: Only video
        assert 'video' in result[0]['files']
        assert 'thumbnail' not in result[0]['files']

        # Group 2: Both files
        assert 'video' in result[1]['files']
        assert 'thumbnail' in result[1]['files']

    def test_metadata_preserved_in_partial_groups(self, mock_run, tmp_path):
        """Test that metadata is preserved when sub files are filtered."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {'video': tmp_path / 'sample.mp4', 'thumbnail': tmp_path / 'sample.gif'},
                'meta': {
                    'dataset_key': 'sample',
                    'origin_file_stem': 'sample',
                    'custom_field': 'custom_value',
                },
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Metadata preserved
        assert len(result) == 1
        assert result[0]['meta']['dataset_key'] == 'sample'
        assert result[0]['meta']['origin_file_stem'] == 'sample'
        assert result[0]['meta']['custom_field'] == 'custom_value'

    def test_multiple_main_files_all_valid(self, mock_run, tmp_path):
        """Test with multiple main files, all valid."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'audio': ['.mp3'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'audio', 'file_type': 'audio', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {
                    'video': tmp_path / 'sample.mp4',
                    'audio': tmp_path / 'sample.mp3',
                    'thumbnail': tmp_path / 'sample.gif',
                },
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Both main files uploaded, thumbnail filtered
        assert len(result) == 1
        assert 'video' in result[0]['files']
        assert 'audio' in result[0]['files']
        assert 'thumbnail' not in result[0]['files']

    def test_multiple_main_files_one_invalid(self, mock_run, tmp_path):
        """Test with multiple main files, one invalid - should filter entire group."""

        class RestrictedUploader(BaseUploader):
            def get_file_extensions_config(self):
                return {'video': ['.mp4'], 'audio': ['.mp3'], 'image': ['.jpg', '.png']}

        uploader = RestrictedUploader(
            run=mock_run,
            path=tmp_path,
            file_specification=[
                {'name': 'video', 'file_type': 'video', 'is_required': True},
                {'name': 'audio', 'file_type': 'audio', 'is_required': True},
                {'name': 'thumbnail', 'file_type': 'image', 'is_required': False},
            ],
        )

        organized_files = [
            {
                'files': {
                    'video': tmp_path / 'sample.avi',  # Invalid
                    'audio': tmp_path / 'sample.mp3',  # Valid
                    'thumbnail': tmp_path / 'sample.jpg',  # Valid
                },
                'meta': {'dataset_key': 'sample'},
            }
        ]

        result = uploader.validate_file_types(organized_files)

        # Expected: Entire group filtered (one main file invalid)
        assert len(result) == 0
