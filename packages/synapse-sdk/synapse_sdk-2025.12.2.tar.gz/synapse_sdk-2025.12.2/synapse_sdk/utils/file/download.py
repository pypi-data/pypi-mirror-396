import asyncio
import operator
from functools import reduce
from pathlib import Path

import aiohttp
import requests

from synapse_sdk.utils.network import clean_url
from synapse_sdk.utils.string import hash_text

from .io import get_temp_path


def download_file(url, path_download, name=None, coerce=None, use_cached=True):
    """Download a file from a URL to a specified directory.

    This function downloads a file from a URL with support for caching, custom naming,
    and optional path transformation. Downloads are streamed in chunks for memory efficiency.

    Args:
        url (str): The URL to download from. Query parameters and fragments are cleaned
            before generating the cached filename.
        path_download (str | Path): Directory path where the file will be saved.
        name (str, optional): Custom filename for the downloaded file (without extension).
            If provided, caching is disabled. If None, a hash of the URL is used as the name.
        coerce (callable, optional): A function to transform the downloaded file path.
            Called with the Path object after download completes.
            Example: lambda p: str(p) to convert Path to string
        use_cached (bool): If True (default), skip download if file already exists.
            Automatically set to False when a custom name is provided.

    Returns:
        Path | Any: Path object pointing to the downloaded file, or the result of
            coerce(path) if a coerce function was provided.

    Raises:
        requests.HTTPError: If the HTTP request fails (e.g., 404, 500 errors).
        IOError: If file write fails due to permissions or disk space.

    Examples:
        Basic download with caching:
        >>> path = download_file('https://example.com/image.jpg', '/tmp/downloads')
        >>> print(path)  # /tmp/downloads/abc123def456.jpg (hash-based name)

        Custom filename without caching:
        >>> path = download_file(
        ...     'https://example.com/data.json',
        ...     '/tmp/downloads',
        ...     name='my_data'
        ... )
        >>> print(path)  # /tmp/downloads/my_data.json

        With path coercion to string:
        >>> path_str = download_file(
        ...     'https://example.com/file.txt',
        ...     '/tmp',
        ...     coerce=str
        ... )
        >>> print(type(path_str))  # <class 'str'>

    Note:
        - Downloads are streamed in 50MB chunks for memory efficiency
        - URL is cleaned (query params removed) before generating cached filename
        - File extension is preserved from the cleaned URL
        - Existing files are reused when use_cached=True
    """
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()

        with path.open('wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


def files_url_to_path(files, coerce=None, file_field=None):
    """Convert file URLs to local file paths by downloading them.

    This function downloads files from URLs and replaces the URLs with local paths
    in the provided dictionary. Supports both flat dictionaries and nested structures.

    Args:
        files (dict): Dictionary containing file URLs or file objects.
            - If values are strings: treated as URLs and replaced with local paths
            - If values are dicts with 'url' key: 'url' is replaced with 'path'
        coerce (callable, optional): Function to transform downloaded paths.
            Applied to each downloaded file path.
        file_field (str, optional): Specific field name to process. If provided,
            only this field is processed. If None, all fields are processed.

    Returns:
        None: Modifies the files dictionary in-place.

    Examples:
        Simple URL replacement:
        >>> files = {'image': 'https://example.com/img.jpg'}
        >>> files_url_to_path(files)
        >>> print(files['image'])  # Path('/tmp/media/abc123.jpg')

        With nested objects:
        >>> files = {'video': {'url': 'https://example.com/vid.mp4', 'size': 1024}}
        >>> files_url_to_path(files)
        >>> print(files['video'])  # {'path': Path('/tmp/media/def456.mp4'), 'size': 1024}

        Process specific field only:
        >>> files = {'image': 'https://ex.com/a.jpg', 'doc': 'https://ex.com/b.pdf'}
        >>> files_url_to_path(files, file_field='image')
        >>> # Only 'image' is downloaded, 'doc' remains as URL

        With path coercion:
        >>> files = {'data': 'https://example.com/data.csv'}
        >>> files_url_to_path(files, coerce=str)
        >>> print(type(files['data']))  # <class 'str'>

    Note:
        - Downloads to temporary media directory: get_temp_path('media')
        - Creates download directory if it doesn't exist
        - Modifies input dictionary in-place
        - Uses caching by default (via download_file)
    """
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    if file_field:
        files[file_field] = download_file(files[file_field], path_download, coerce=coerce)
    else:
        for file_name in files:
            if isinstance(files[file_name], str):
                files[file_name] = download_file(files[file_name], path_download, coerce=coerce)
            else:
                files[file_name]['path'] = download_file(files[file_name].pop('url'), path_download, coerce=coerce)


def files_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False, is_async=False):
    """Convert file URLs to paths for multiple objects with nested field support.

    This function processes one or more objects, extracting file URLs from specified
    nested fields and replacing them with local file paths. Supports both synchronous
    and asynchronous operation.

    Args:
        objs (dict | list): Single object or list of objects to process.
            If is_list=False, can be a single dict.
            If is_list=True, should be a list of dicts.
        files_fields (list[str]): List of field paths to process.
            Supports dot notation for nested fields (e.g., 'data.files', 'meta.image').
        coerce (callable, optional): Function to transform downloaded paths.
        is_list (bool): If True, objs is treated as a list. If False, objs is wrapped
            in a list for processing. Default False.
        is_async (bool): If True, uses async download (afiles_url_to_path_from_objs).
            If False, uses synchronous download. Default False.

    Returns:
        None: Modifies objects in-place, replacing URLs with local paths.

    Examples:
        Single object with simple field:
        >>> obj = {'files': {'image': 'https://example.com/img.jpg'}}
        >>> files_url_to_path_from_objs(obj, files_fields=['files'])
        >>> print(obj['files']['image'])  # Path('/tmp/media/abc123.jpg')

        Multiple objects with nested fields:
        >>> objs = [
        ...     {'data': {'files': {'img': 'https://ex.com/1.jpg'}}},
        ...     {'data': {'files': {'img': 'https://ex.com/2.jpg'}}}
        ... ]
        >>> files_url_to_path_from_objs(objs, files_fields=['data.files'], is_list=True)
        >>> # Both images are downloaded and URLs replaced with paths

        Async download for better performance:
        >>> objs = [{'files': {'a': 'url1', 'b': 'url2'}} for _ in range(10)]
        >>> files_url_to_path_from_objs(
        ...     objs,
        ...     files_fields=['files'],
        ...     is_list=True,
        ...     is_async=True
        ... )
        >>> # All files downloaded concurrently

        Multiple field paths:
        >>> obj = {
        ...     'images': {'photo': 'https://ex.com/photo.jpg'},
        ...     'videos': {'clip': 'https://ex.com/video.mp4'}
        ... }
        >>> files_url_to_path_from_objs(obj, files_fields=['images', 'videos'])
        >>> # Both images and videos fields are processed

    Note:
        - Silently skips missing fields (KeyError is caught and ignored)
        - Supports dot notation for nested field access
        - Async mode (is_async=True) provides better performance for multiple files
        - Commonly used with API responses containing file URLs
        - Used by BaseClient._list() with url_conversion parameter
    """
    if is_async:
        asyncio.run(afiles_url_to_path_from_objs(objs, files_fields, coerce=coerce, is_list=is_list))
    else:
        if not is_list:
            objs = [objs]

        for obj in objs:
            for files_field in files_fields:
                try:
                    files = reduce(operator.getitem, files_field.split('.'), obj)
                    if isinstance(files, str):
                        files_url_to_path(obj, coerce=coerce, file_field=files_field)
                    else:
                        files_url_to_path(files, coerce=coerce)
                except KeyError:
                    pass


async def adownload_file(url, path_download, name=None, coerce=None, use_cached=True):
    """Asynchronously download a file from a URL to a specified directory.

    Async version of download_file() using aiohttp for concurrent downloads.
    All parameters and behavior are identical to download_file().

    Args:
        url (str): The URL to download from.
        path_download (str | Path): Directory path where the file will be saved.
        name (str, optional): Custom filename (without extension).
        coerce (callable, optional): Function to transform the downloaded file path.
        use_cached (bool): If True (default), skip download if file exists.

    Returns:
        Path | Any: Path to downloaded file, or coerce(path) if provided.

    Examples:
        Basic async download:
        >>> path = await adownload_file('https://example.com/large.zip', '/tmp')

        Multiple concurrent downloads:
        >>> urls = ['https://ex.com/1.jpg', 'https://ex.com/2.jpg']
        >>> paths = await asyncio.gather(*[
        ...     adownload_file(url, '/tmp') for url in urls
        ... ])

    Note:
        - Uses aiohttp.ClientSession for async HTTP requests
        - Downloads in 50MB chunks for memory efficiency
        - Recommended for downloading multiple files concurrently
    """
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with path.open('wb') as file:
                    while chunk := await response.content.read(chunk_size):
                        file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


async def afiles_url_to_path(files, coerce=None):
    """Asynchronously convert file URLs to local paths by downloading them.

    Async version of files_url_to_path() for concurrent file downloads.
    Processes all files in the dictionary concurrently for better performance.

    Args:
        files (dict): Dictionary containing file URLs or file objects.
        coerce (callable, optional): Function to transform downloaded paths.

    Returns:
        None: Modifies the files dictionary in-place.

    Examples:
        Download multiple files concurrently:
        >>> files = {
        ...     'image1': 'https://ex.com/1.jpg',
        ...     'image2': 'https://ex.com/2.jpg',
        ...     'image3': 'https://ex.com/3.jpg'
        ... }
        >>> await afiles_url_to_path(files)
        >>> # All 3 files downloaded concurrently

        With nested file objects:
        >>> files = {
        ...     'thumb': {'url': 'https://ex.com/thumb.jpg'},
        ...     'full': {'url': 'https://ex.com/full.jpg'}
        ... }
        >>> await afiles_url_to_path(files)
        >>> print(files['thumb']['path'])  # Path object

    Note:
        - All files are downloaded concurrently using asyncio
        - More efficient than synchronous version for multiple files
        - Does not support file_field parameter (processes all fields)
    """
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    for file_name in files:
        if isinstance(files[file_name], str):
            files[file_name] = await adownload_file(files[file_name], path_download, coerce=coerce)
        else:
            files[file_name]['path'] = await adownload_file(files[file_name].pop('url'), path_download, coerce=coerce)


async def afiles_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False):
    """Asynchronously convert file URLs to paths for multiple objects.

    Async version of files_url_to_path_from_objs() that downloads all files
    concurrently using asyncio.gather() for maximum performance.

    Args:
        objs (dict | list): Single object or list of objects to process.
        files_fields (list[str]): List of field paths to process (supports dot notation).
        coerce (callable, optional): Function to transform downloaded paths.
        is_list (bool): If True, objs is treated as a list. Default False.

    Returns:
        None: Modifies objects in-place, replacing URLs with local paths.

    Examples:
        Download files from multiple objects concurrently:
        >>> objs = [
        ...     {'files': {'img': 'https://ex.com/1.jpg'}},
        ...     {'files': {'img': 'https://ex.com/2.jpg'}},
        ...     {'files': {'img': 'https://ex.com/3.jpg'}}
        ... ]
        >>> await afiles_url_to_path_from_objs(objs, ['files'], is_list=True)
        >>> # All 3 images downloaded concurrently

        Process large dataset efficiently:
        >>> # 100 objects with multiple files each
        >>> objs = [{'data': {'files': {...}}} for _ in range(100)]
        >>> await afiles_url_to_path_from_objs(
        ...     objs,
        ...     files_fields=['data.files'],
        ...     is_list=True
        ... )
        >>> # All files downloaded in parallel, much faster than sync version

    Note:
        - All file downloads happen concurrently using asyncio.gather()
        - Significantly faster than synchronous version for large datasets
        - Ideal for processing API responses with many file URLs
        - Used internally when is_async=True in files_url_to_path_from_objs()
    """
    if not is_list:
        objs = [objs]

    tasks = []

    for obj in objs:
        for files_field in files_fields:
            try:
                files = reduce(operator.getitem, files_field.split('.'), obj)
                tasks.append(afiles_url_to_path(files, coerce=coerce))
            except KeyError:
                pass

    await asyncio.gather(*tasks)
