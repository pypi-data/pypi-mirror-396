import asyncio
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import ffmpeg


# Exception classes
class VideoTranscodeError(Exception):
    """Base exception for video transcoding errors."""

    pass


class UnsupportedFormatError(VideoTranscodeError):
    """Raised when input format is not supported."""

    pass


class FFmpegNotFoundError(VideoTranscodeError):
    """Raised when FFmpeg is not installed or not in PATH."""

    pass


class TranscodingFailedError(VideoTranscodeError):
    """Raised when FFmpeg transcoding process fails."""

    pass


@dataclass
class TranscodeConfig:
    """Video transcoding configuration."""

    vcodec: str = 'libx264'  # Video codec
    preset: str = 'medium'  # Encoding preset (ultrafast to veryslow)
    crf: int = 28  # Constant Rate Factor (0-51, lower=better quality)
    acodec: str = 'aac'  # Audio codec
    audio_bitrate: str = '128k'  # Audio bitrate
    movflags: str = '+faststart'  # MP4 optimization flags
    resolution: Optional[str] = None  # Target resolution (e.g., '1920x1080')
    fps: Optional[int] = None  # Target frame rate
    start_time: Optional[float] = None  # Trim start time in seconds
    duration: Optional[float] = None  # Trim duration in seconds


# Supported input formats
SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.mpeg', '.mpg', '.m4v', '.3gp', '.ogv'}


def _check_ffmpeg_available():
    """Check if FFmpeg is available in PATH."""
    if not shutil.which('ffmpeg'):
        raise FFmpegNotFoundError(
            'FFmpeg is not installed or not found in PATH. Please install FFmpeg to use video transcoding features.'
        )


def validate_video_format(video_path: str | Path) -> bool:
    """
    Check if video format is supported for transcoding.

    Args:
        video_path (str | Path): Path to the video file

    Returns:
        bool: True if format is supported, False otherwise
    """
    path = Path(video_path)
    return path.suffix.lower() in SUPPORTED_FORMATS


def get_video_info(video_path: str | Path) -> dict:
    """
    Extract video metadata (resolution, duration, codecs, etc.).

    Args:
        video_path (str | Path): Path to the video file

    Returns:
        dict: Video metadata information

    Raises:
        VideoTranscodeError: If unable to probe video file
    """
    _check_ffmpeg_available()

    try:
        probe = ffmpeg.probe(str(video_path))

        video_info = {}

        # Get format information
        if 'format' in probe:
            format_info = probe['format']
            video_info['duration'] = float(format_info.get('duration', 0))
            video_info['size'] = int(format_info.get('size', 0))
            video_info['bitrate'] = int(format_info.get('bit_rate', 0))

        # Get stream information
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']

        if video_streams:
            video_stream = video_streams[0]
            video_info['width'] = int(video_stream.get('width', 0))
            video_info['height'] = int(video_stream.get('height', 0))
            video_info['video_codec'] = video_stream.get('codec_name', '')
            video_info['fps'] = eval(video_stream.get('r_frame_rate', '0/1'))

        if audio_streams:
            audio_stream = audio_streams[0]
            video_info['audio_codec'] = audio_stream.get('codec_name', '')
            video_info['channels'] = int(audio_stream.get('channels', 0))
            video_info['sample_rate'] = int(audio_stream.get('sample_rate', 0))

        return video_info

    except Exception as e:
        raise VideoTranscodeError(f'Failed to probe video file: {str(e)}')


def _build_ffmpeg_stream(input_path: str | Path, output_path: str | Path, config: TranscodeConfig):
    """Build FFmpeg stream with configuration."""
    stream = ffmpeg.input(str(input_path))

    # Apply start time and duration trimming
    if config.start_time is not None or config.duration is not None:
        kwargs = {}
        if config.start_time is not None:
            kwargs['ss'] = config.start_time
        if config.duration is not None:
            kwargs['t'] = config.duration
        stream = ffmpeg.input(str(input_path), **kwargs)

    # Apply video filters
    if config.resolution or config.fps:
        if config.resolution:
            width, height = config.resolution.split('x')
            stream = ffmpeg.filter(stream, 'scale', width, height)
        if config.fps:
            stream = ffmpeg.filter(stream, 'fps', fps=config.fps)

    # Build output with encoding parameters
    output_kwargs = {
        'vcodec': config.vcodec,
        'preset': config.preset,
        'crf': config.crf,
        'acodec': config.acodec,
        'audio_bitrate': config.audio_bitrate,
        'movflags': config.movflags,
    }

    return ffmpeg.output(stream, str(output_path), **output_kwargs)


def transcode_video(
    input_path: str | Path,
    output_path: str | Path,
    config: Optional[TranscodeConfig] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> Path:
    """
    Transcode video with specified configuration.

    Args:
        input_path (str | Path): Path to input video file
        output_path (str | Path): Path to output video file
        config (Optional[TranscodeConfig]): Transcoding configuration
        progress_callback (Optional[Callable[[float], None]]): Progress callback function

    Returns:
        Path: Path to the transcoded video file

    Raises:
        UnsupportedFormatError: If input format is not supported
        FFmpegNotFoundError: If FFmpeg is not available
        TranscodingFailedError: If transcoding fails
    """
    _check_ffmpeg_available()

    input_path = Path(input_path)
    output_path = Path(output_path)

    if not validate_video_format(input_path):
        raise UnsupportedFormatError(f'Unsupported video format: {input_path.suffix}')

    if config is None:
        config = TranscodeConfig()

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Build FFmpeg command
        stream = _build_ffmpeg_stream(input_path, output_path, config)

        # Run FFmpeg
        if progress_callback:
            # Get video duration for progress calculation
            video_info = get_video_info(input_path)
            total_duration = video_info.get('duration', 0)

            # Run with progress monitoring
            process = ffmpeg.run_async(stream, pipe_stderr=True, overwrite_output=True)

            while True:
                output = process.stderr.readline()
                if output == b'' and process.poll() is not None:
                    break
                if output:
                    line = output.decode('utf-8')
                    # Parse progress from FFmpeg output
                    if 'time=' in line and total_duration > 0:
                        try:
                            time_str = line.split('time=')[1].split()[0]
                            hours, minutes, seconds = time_str.split(':')
                            current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                            progress = min(current_time / total_duration, 1.0)
                            progress_callback(progress)
                        except (ValueError, IndexError):
                            pass

            if process.returncode != 0:
                raise TranscodingFailedError('FFmpeg process failed')
        else:
            # Run without progress monitoring
            ffmpeg.run(stream, overwrite_output=True, quiet=True)

        return output_path

    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
        raise TranscodingFailedError(f'Transcoding failed: {error_message}')
    except Exception as e:
        raise VideoTranscodeError(f'Unexpected error during transcoding: {str(e)}')


def optimize_for_web(video_path: str | Path, output_path: str | Path) -> Path:
    """
    Quick optimization for web streaming with default settings.

    Args:
        video_path (str | Path): Path to input video file
        output_path (str | Path): Path to output video file

    Returns:
        Path: Path to the optimized video file
    """
    config = TranscodeConfig(
        preset='fast',  # Faster encoding for web optimization
        crf=23,  # Better quality for web
        movflags='+faststart+frag_keyframe+empty_moov',  # Advanced web optimization
    )
    return transcode_video(video_path, output_path, config)


async def atranscode_video(
    input_path: str | Path, output_path: str | Path, config: Optional[TranscodeConfig] = None
) -> Path:
    """
    Async version of transcode_video.

    Args:
        input_path (str | Path): Path to input video file
        output_path (str | Path): Path to output video file
        config (Optional[TranscodeConfig]): Transcoding configuration

    Returns:
        Path: Path to the transcoded video file
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, transcode_video, input_path, output_path, config)


def transcode_batch(
    video_paths: list[Path], output_dir: Path, config: Optional[TranscodeConfig] = None, max_workers: int = 4
) -> list[Path]:
    """
    Process multiple videos concurrently.

    Args:
        video_paths (list[Path]): List of input video file paths
        output_dir (Path): Directory for output files
        config (Optional[TranscodeConfig]): Transcoding configuration
        max_workers (int): Maximum number of concurrent workers

    Returns:
        list[Path]: List of paths to transcoded video files
    """
    import concurrent.futures

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    def process_video(video_path):
        output_path = output_dir / f'{video_path.stem}_transcoded.mp4'
        return transcode_video(video_path, output_path, config)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_video, video_paths))

    return results
