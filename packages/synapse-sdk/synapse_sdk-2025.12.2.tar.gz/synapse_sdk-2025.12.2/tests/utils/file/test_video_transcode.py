"""
Tests for video transcoding utilities.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from synapse_sdk.utils.file.video.transcode import (
    FFmpegNotFoundError,
    TranscodeConfig,
    TranscodingFailedError,
    UnsupportedFormatError,
    VideoTranscodeError,
    _check_ffmpeg_available,
    get_video_info,
    optimize_for_web,
    transcode_video,
    validate_video_format,
)


class TestVideoFormatValidation:
    """Test video format validation."""

    def test_supported_formats(self):
        """Test that supported formats return True."""
        supported_formats = [
            'video.mp4',
            'video.avi',
            'video.mov',
            'video.mkv',
            'video.webm',
            'video.flv',
            'video.wmv',
            'video.mpeg',
            'video.mpg',
            'video.m4v',
            'video.3gp',
            'video.ogv',
        ]

        for format_path in supported_formats:
            assert validate_video_format(format_path) is True

    def test_unsupported_formats(self):
        """Test that unsupported formats return False."""
        unsupported_formats = ['audio.mp3', 'image.jpg', 'document.pdf', 'data.txt', 'video.xyz', 'file.unknown']

        for format_path in unsupported_formats:
            assert validate_video_format(format_path) is False

    def test_case_insensitive_validation(self):
        """Test that validation is case insensitive."""
        formats = ['VIDEO.MP4', 'Video.Avi', 'video.MOV']

        for format_path in formats:
            assert validate_video_format(format_path) is True

    def test_path_object_input(self):
        """Test that Path objects work as input."""
        video_path = Path('video.mp4')
        assert validate_video_format(video_path) is True

        invalid_path = Path('document.txt')
        assert validate_video_format(invalid_path) is False


class TestFFmpegAvailability:
    """Test FFmpeg availability checking."""

    @patch('shutil.which')
    def test_ffmpeg_available(self, mock_which):
        """Test when FFmpeg is available."""
        mock_which.return_value = '/usr/bin/ffmpeg'

        # Should not raise exception
        _check_ffmpeg_available()

    @patch('shutil.which')
    def test_ffmpeg_not_available(self, mock_which):
        """Test when FFmpeg is not available."""
        mock_which.return_value = None

        with pytest.raises(FFmpegNotFoundError) as exc_info:
            _check_ffmpeg_available()

        assert 'FFmpeg is not installed' in str(exc_info.value)


class TestTranscodeConfig:
    """Test TranscodeConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TranscodeConfig()

        assert config.vcodec == 'libx264'
        assert config.preset == 'medium'
        assert config.crf == 28
        assert config.acodec == 'aac'
        assert config.audio_bitrate == '128k'
        assert config.movflags == '+faststart'
        assert config.resolution is None
        assert config.fps is None
        assert config.start_time is None
        assert config.duration is None

    def test_custom_config(self):
        """Test custom configuration values."""
        config = TranscodeConfig(
            vcodec='libx265',
            preset='fast',
            crf=20,
            acodec='opus',
            audio_bitrate='256k',
            resolution='1920x1080',
            fps=30,
            start_time=10.0,
            duration=60.0,
        )

        assert config.vcodec == 'libx265'
        assert config.preset == 'fast'
        assert config.crf == 20
        assert config.acodec == 'opus'
        assert config.audio_bitrate == '256k'
        assert config.resolution == '1920x1080'
        assert config.fps == 30
        assert config.start_time == 10.0
        assert config.duration == 60.0


class TestVideoInfo:
    """Test video information extraction."""

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.probe')
    def test_get_video_info_success(self, mock_probe, mock_check_ffmpeg):
        """Test successful video info extraction."""
        mock_check_ffmpeg.return_value = None
        mock_probe.return_value = {
            'format': {'duration': '120.5', 'size': '10485760', 'bit_rate': '1000000'},
            'streams': [
                {'codec_type': 'video', 'codec_name': 'h264', 'width': 1920, 'height': 1080, 'r_frame_rate': '30/1'},
                {'codec_type': 'audio', 'codec_name': 'aac', 'channels': 2, 'sample_rate': '48000'},
            ],
        }

        info = get_video_info('test_video.mp4')

        assert info['duration'] == 120.5
        assert info['size'] == 10485760
        assert info['bitrate'] == 1000000
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['video_codec'] == 'h264'
        assert info['fps'] == 30.0
        assert info['audio_codec'] == 'aac'
        assert info['channels'] == 2
        assert info['sample_rate'] == 48000

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.probe')
    def test_get_video_info_failure(self, mock_probe, mock_check_ffmpeg):
        """Test video info extraction failure."""
        mock_check_ffmpeg.return_value = None
        mock_probe.side_effect = Exception('Probe failed')

        with pytest.raises(VideoTranscodeError) as exc_info:
            get_video_info('invalid_video.mp4')

        assert 'Failed to probe video file' in str(exc_info.value)


class TestVideoTranscoding:
    """Test video transcoding functionality."""

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.run')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_transcode_video_success(self, mock_validate, mock_ffmpeg_run, mock_check_ffmpeg):
        """Test successful video transcoding."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = True
        mock_ffmpeg_run.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / 'input.mp4'
            output_path = Path(temp_dir) / 'output.mp4'

            result = transcode_video(input_path, output_path)

            assert result == output_path
            mock_ffmpeg_run.assert_called_once()

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_transcode_unsupported_format(self, mock_validate, mock_check_ffmpeg):
        """Test transcoding with unsupported format."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = False

        with pytest.raises(UnsupportedFormatError) as exc_info:
            transcode_video('input.txt', 'output.mp4')

        assert 'Unsupported video format' in str(exc_info.value)

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.run')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_transcode_with_custom_config(self, mock_validate, mock_ffmpeg_run, mock_check_ffmpeg):
        """Test transcoding with custom configuration."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = True
        mock_ffmpeg_run.return_value = None

        config = TranscodeConfig(preset='fast', crf=20, resolution='1280x720')

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / 'input.mp4'
            output_path = Path(temp_dir) / 'output.mp4'

            result = transcode_video(input_path, output_path, config)

            assert result == output_path
            mock_ffmpeg_run.assert_called_once()

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.run')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_transcode_with_progress_callback(self, mock_validate, mock_ffmpeg_run, mock_check_ffmpeg):
        """Test transcoding with progress callback."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = True

        # Mock ffmpeg.run_async to simulate progress
        mock_process = Mock()
        mock_process.poll.return_value = 0
        mock_process.stderr.readline.side_effect = [
            b'frame=100 fps=30 time=00:01:30.00 bitrate=1000kbits/s\n',
            b'frame=200 fps=30 time=00:03:00.00 bitrate=1000kbits/s\n',
            b'',  # End of output
        ]
        mock_process.returncode = 0

        with (
            patch('ffmpeg.run_async', return_value=mock_process),
            patch('synapse_sdk.utils.file.video.transcode.get_video_info', return_value={'duration': 180.0}),
        ):
            progress_values = []

            def progress_callback(progress):
                progress_values.append(progress)

            with tempfile.TemporaryDirectory() as temp_dir:
                input_path = Path(temp_dir) / 'input.mp4'
                output_path = Path(temp_dir) / 'output.mp4'

                result = transcode_video(input_path, output_path, progress_callback=progress_callback)

                assert result == output_path
                assert len(progress_values) > 0

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.run')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_transcode_ffmpeg_error(self, mock_validate, mock_ffmpeg_run, mock_check_ffmpeg):
        """Test transcoding with FFmpeg error."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = True

        import ffmpeg

        error = ffmpeg.Error('cmd', 'stdout', b'FFmpeg error message')
        mock_ffmpeg_run.side_effect = error

        with pytest.raises(TranscodingFailedError) as exc_info:
            transcode_video('input.mp4', 'output.mp4')

        assert 'Transcoding failed' in str(exc_info.value)


class TestOptimizeForWeb:
    """Test web optimization functionality."""

    @patch('synapse_sdk.utils.file.video.transcode.transcode_video')
    def test_optimize_for_web(self, mock_transcode):
        """Test web optimization with correct settings."""
        mock_transcode.return_value = Path('output.mp4')

        result = optimize_for_web('input.mp4', 'output.mp4')

        assert result == Path('output.mp4')

        # Check that transcode_video was called with web-optimized config
        mock_transcode.assert_called_once()
        args, kwargs = mock_transcode.call_args
        config = args[2] if len(args) > 2 else kwargs.get('config')

        assert config.preset == 'fast'
        assert config.crf == 23
        assert '+faststart+frag_keyframe+empty_moov' in config.movflags


class TestExceptions:
    """Test custom exception classes."""

    def test_video_transcode_error(self):
        """Test base VideoTranscodeError."""
        error = VideoTranscodeError('Test error')
        assert str(error) == 'Test error'
        assert isinstance(error, Exception)

    def test_unsupported_format_error(self):
        """Test UnsupportedFormatError inheritance."""
        error = UnsupportedFormatError('Unsupported format')
        assert isinstance(error, VideoTranscodeError)
        assert isinstance(error, Exception)

    def test_ffmpeg_not_found_error(self):
        """Test FFmpegNotFoundError inheritance."""
        error = FFmpegNotFoundError('FFmpeg not found')
        assert isinstance(error, VideoTranscodeError)
        assert isinstance(error, Exception)

    def test_transcoding_failed_error(self):
        """Test TranscodingFailedError inheritance."""
        error = TranscodingFailedError('Transcoding failed')
        assert isinstance(error, VideoTranscodeError)
        assert isinstance(error, Exception)


class TestPathHandling:
    """Test path handling in video functions."""

    @patch('synapse_sdk.utils.file.video.transcode._check_ffmpeg_available')
    @patch('ffmpeg.run')
    @patch('synapse_sdk.utils.file.video.transcode.validate_video_format')
    def test_string_and_path_objects(self, mock_validate, mock_ffmpeg_run, mock_check_ffmpeg):
        """Test that both string and Path objects work."""
        mock_check_ffmpeg.return_value = None
        mock_validate.return_value = True
        mock_ffmpeg_run.return_value = None

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with string paths
            input_str = str(Path(temp_dir) / 'input.mp4')
            output_str = str(Path(temp_dir) / 'output.mp4')

            result1 = transcode_video(input_str, output_str)
            assert isinstance(result1, Path)

            # Test with Path objects
            input_path = Path(temp_dir) / 'input2.mp4'
            output_path = Path(temp_dir) / 'output2.mp4'

            result2 = transcode_video(input_path, output_path)
            assert isinstance(result2, Path)
            assert result2 == output_path

    def test_validate_format_with_paths(self):
        """Test format validation with different path types."""
        # String path
        assert validate_video_format('video.mp4') is True

        # Path object
        assert validate_video_format(Path('video.mp4')) is True

        # Complex path
        complex_path = Path('/home/user/videos/movie.mkv')
        assert validate_video_format(complex_path) is True
