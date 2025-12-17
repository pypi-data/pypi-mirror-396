import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.file import files_url_to_path_from_objs
from synapse_sdk.utils.file.upload import (
    FileProcessingError,
    FileValidationError,
    close_file_handles,
    process_files_for_upload,
)


class BaseClient:
    name = None
    base_url = None
    page_size = 100

    def __init__(self, base_url, timeout=None):
        self.base_url = base_url.rstrip('/')
        # Set reasonable default timeouts for better UX
        self.timeout = timeout or {
            'connect': 5,  # Connection timeout: 5 seconds
            'read': 15,  # Read timeout: 15 seconds
        }

        # Session is created on first use
        self._session = None

        # Store retry configuration for creating sessions
        self._retry_config = {
            'total': 3,  # Total retries
            'backoff_factor': 1,  # Backoff factor between retries
            'status_forcelist': [502, 503, 504],  # HTTP status codes to retry
            'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
        }

    def _create_session(self):
        """Create a new requests session with retry strategy."""
        session = requests.Session()

        # Configure retry strategy for transient failures
        retry_strategy = Retry(**self._retry_config)

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    @property
    def requests_session(self):
        """Get the requests session.

        Returns a session instance, creating one if it doesn't exist.
        """
        if self._session is None:
            self._session = self._create_session()
        return self._session

    def _get_url(self, path, trailing_slash=False):
        """Construct a full URL from a path.

        Args:
            path (str): URL path or full URL
            trailing_slash (bool): Whether to ensure URL ends with trailing slash

        Returns:
            str: Complete URL
        """
        # Use the path as-is if it's already a full URL, otherwise construct from base_url and path
        url = path if path.startswith(('http://', 'https://')) else f'{self.base_url}/{path.lstrip("/")}'

        # Add trailing slash if requested and not present
        if trailing_slash and not url.endswith('/'):
            url += '/'

        return url

    def _get_headers(self):
        return {}

    def _request(self, method: str, path: str, **kwargs) -> dict | str:
        """Request handler for all HTTP methods.

        Args:
            method (str): HTTP method to use.
            path (str): URL path to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            dict | str: JSON response or text response.
        """
        url = self._get_url(path)
        headers = self._get_headers()
        headers.update(kwargs.pop('headers', {}))

        # Set timeout if not provided in kwargs
        if 'timeout' not in kwargs:
            kwargs['timeout'] = (self.timeout['connect'], self.timeout['read'])

        # List to store opened files to close after request
        opened_files = []

        try:
            if method in ['post', 'put', 'patch']:
                # Process files if present using the utility function
                # TODO: File handling logic using 'files' key is naive. Need to establish and document
                #       a clear convention for including file information in request bodies across Synapse SDK.
                if kwargs.get('files') is not None:
                    kwargs['files'], opened_files = process_files_for_upload(kwargs['files'])

                    # Handle data serialization when files are present
                    if 'data' in kwargs:
                        for name, value in kwargs['data'].items():
                            if isinstance(value, dict):
                                kwargs['data'][name] = json.dumps(value)
                else:
                    # No files - use JSON content type
                    headers['Content-Type'] = 'application/json'
                    if 'data' in kwargs:
                        kwargs['data'] = json.dumps(kwargs['data'])

            # Send request
            response = getattr(self.requests_session, method)(url, headers=headers, **kwargs)
            if not response.ok:
                raise ClientError(
                    response.status_code, response.json() if response.status_code == 400 else response.reason
                )

        except (FileValidationError, FileProcessingError) as e:
            # Catch file validation and processing errors from the utility
            raise ClientError(400, str(e)) from e
        except requests.exceptions.ConnectTimeout:
            raise ClientError(408, f'{self.name} connection timeout (>{self.timeout["connect"]}s)')
        except requests.exceptions.ReadTimeout:
            raise ClientError(408, f'{self.name} read timeout (>{self.timeout["read"]}s)')
        except requests.exceptions.ConnectionError as e:
            # More specific error handling for different connection issues
            if 'Name or service not known' in str(e) or 'nodename nor servname provided' in str(e):
                raise ClientError(503, f'{self.name} host unreachable')
            elif 'Connection refused' in str(e):
                raise ClientError(503, f'{self.name} connection refused')
            else:
                raise ClientError(503, f'{self.name} connection error: {str(e)[:100]}')
        except requests.exceptions.RequestException as e:
            # Catch all other requests exceptions
            raise ClientError(500, f'{self.name} request failed: {str(e)[:100]}')
        finally:
            # Always close opened files, even if an exception occurred
            close_file_handles(opened_files)

        return self._post_response(response)

    def _post_response(self, response):
        try:
            return response.json()
        except ValueError:
            return response.text

    def _get(self, path, url_conversion=None, response_model=None, **kwargs):
        """Perform a GET request and optionally convert response to a pydantic model.

        Args:
            path (str): URL path to request.
            url_conversion (dict, optional): Configuration for URL to path conversion.
            request_model (pydantic.BaseModel, optional): Pydantic model to validate the request.
            response_model (pydantic.BaseModel, optional): Pydantic model to validate the response.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response data, optionally converted to a pydantic model.
        """
        response = self._request('get', path, **kwargs)

        if url_conversion:
            if url_conversion['is_list']:
                files_url_to_path_from_objs(response['results'], **url_conversion, is_async=True)
            else:
                files_url_to_path_from_objs(response, **url_conversion)

        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)

        return response

    def _post(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a POST request and optionally convert response to a pydantic model.

        Args:
            path (str): URL path to request.
            request_model (pydantic.BaseModel, optional): Pydantic model to validate the request.
            response_model (pydantic.BaseModel, optional): Pydantic model to validate the response.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            The response data, optionally converted to a pydantic model.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('post', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _put(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a PUT request to the specified path.

        Args:
            path (str): The URL path for the request.
            request_model (Optional[Type[BaseModel]]): A Pydantic model class to validate the request body against.
            response_model (Optional[Type[BaseModel]]): A Pydantic model class to validate and parse the response.
            **kwargs: Additional arguments to pass to the request method.
                - data: The request body to be sent. If provided along with request_model, it will be validated.

        Returns:
            Union[dict, BaseModel]:
                If response_model is provided, returns an instance of that model populated with the response data.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('put', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _patch(self, path, request_model=None, response_model=None, **kwargs):
        """Perform a PATCH HTTP request to the specified path.

        Args:
            path (str): The API endpoint path to make the request to.
            request_model (Optional[Type[BaseModel]]): A Pydantic model class used to validate the request body.
            response_model (Optional[Type[BaseModel]]): A Pydantic model class used to validate and parse the response.
            **kwargs: Additional keyword arguments to pass to the request method.
                - data: The request body data. If provided along with request_model, it will be validated.

        Returns:
            Union[dict, BaseModel]: If response_model is provided, returns an instance of that model.
                Otherwise, returns the raw response data.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('patch', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _delete(self, path, request_model=None, response_model=None, **kwargs):
        """Performs a DELETE request to the specified path.

        Args:
            path (str): The API endpoint path to send the DELETE request to.
            request_model (Optional[Type[BaseModel]]): Pydantic model to validate the request data against.
            response_model (Optional[Type[BaseModel]]): Pydantic model to validate and convert the response data.
            **kwargs: Additional keyword arguments passed to the request method.
                - data: Request payload to send. Will be validated against request_model if both are provided.

        Returns:
            Union[dict, BaseModel]: If response_model is provided, returns an instance of that model.
                                   Otherwise, returns the raw response data as a dictionary.
        """
        if kwargs.get('data') and request_model:
            kwargs['data'] = self._validate_request_body_with_pydantic_model(kwargs['data'], request_model)
        response = self._request('delete', path, **kwargs)
        if response_model:
            return self._validate_response_with_pydantic_model(response, response_model)
        else:
            return response

    def _list(self, path, url_conversion=None, list_all=False, params=None, **kwargs):
        """List resources from a paginated API endpoint.

        Args:
            path (str): URL path to request.
            url_conversion (dict, optional): Configuration for URL to path conversion.
                Used to convert file URLs to local paths in the response.
                Example: {'files_fields': ['files'], 'is_list': True}
                This will convert file URLs in the 'files' field of each result.
            list_all (bool): If True, returns a generator yielding all results across all pages.
                Default is False, which returns only the first page.
            params (dict, optional): Query parameters to pass to the request.
                Example: {'status': 'active', 'project': 123}
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            If list_all is False: dict response from the API containing:
                - 'results': list of items on the current page
                - 'count': total number of items
                - 'next': URL to the next page (or None)
                - 'previous': URL to the previous page (or None)
            If list_all is True: tuple of (generator, count) where:
                - generator: yields individual items from all pages
                - count: total number of items across all pages

        Examples:
            Get first page only:
            >>> response = client._list('api/tasks/')
            >>> tasks = response['results']  # List of tasks on first page
            >>> total_count = response['count']  # Total number of tasks

            Get all results across all pages:
            >>> generator, count = client._list('api/tasks/', list_all=True)
            >>> all_tasks = list(generator)  # Fetches all pages

            With filters and url_conversion:
            >>> url_conversion = {'files_fields': ['files'], 'is_list': True}
            >>> params = {'status': 'active'}
            >>> generator, count = client._list(
            ...     'api/data_units/',
            ...     url_conversion=url_conversion,
            ...     list_all=True,
            ...     params=params
            ... )
            >>> active_units = list(generator)  # All active units with file URLs converted
        """
        if params is None:
            params = {}

        if list_all:
            response = self._get(path, params=params, **kwargs)
            return self._list_all(path, url_conversion, params=params, **kwargs), response.get('count')
        else:
            response = self._get(path, params=params, **kwargs)
            return response

    def _list_all(self, path, url_conversion=None, params=None, **kwargs):
        """Generator that yields all results from a paginated API endpoint.

        This method handles pagination automatically by following the 'next' URLs
        returned by the API until all pages have been fetched. It uses an iterative
        approach (while loop) instead of recursion to avoid stack overflow with
        deep pagination.

        Args:
            path (str): Initial URL path to request.
            url_conversion (dict, optional): Configuration for URL to path conversion.
                Applied to all pages. Common structure:
                - 'files_fields': List of field names containing file URLs
                - 'is_list': Whether the response is a list (True for paginated results)
                Example: {'files_fields': ['files', 'images'], 'is_list': True}
            params (dict, optional): Query parameters for the first request only.
                Subsequent requests use the 'next' URL which already includes
                all necessary parameters. If 'page_size' is not specified,
                it defaults to self.page_size (100).
                Example: {'status': 'active', 'page_size': 50}
            **kwargs: Additional keyword arguments to pass to requests.
                Example: timeout, headers, etc.

        Yields:
            dict: Individual result items from all pages. Each item is yielded
                as soon as it's fetched, allowing for memory-efficient processing
                of large datasets.

        Examples:
            Basic usage - fetch all tasks:
            >>> for task in client._list_all('api/tasks/'):
            ...     process_task(task)

            With filters:
            >>> params = {'status': 'pending', 'priority': 'high'}
            >>> for task in client._list_all('api/tasks/', params=params):
            ...     print(task['id'])

            With url_conversion for file fields:
            >>> url_conversion = {'files_fields': ['files'], 'is_list': True}
            >>> for data_unit in client._list_all('api/data_units/', url_conversion):
            ...     # File URLs in 'files' field are converted to local paths
            ...     print(data_unit['files'])

            Collecting results into a list:
            >>> all_tasks = list(client._list_all('api/tasks/'))
            >>> print(f"Total tasks: {len(all_tasks)}")

        Note:
            - This is a generator function, so results are fetched lazily as you iterate
            - The first page is fetched with the provided params
            - Subsequent pages use the 'next' URL from the API response
            - No duplicate page_size parameters are added to subsequent requests
            - Memory efficient: processes one item at a time rather than loading all at once
        """
        if params is None:
            params = {}

        # Set page_size only if not already specified by user
        request_params = params.copy()
        if 'page_size' not in request_params:
            request_params['page_size'] = self.page_size

        next_url = path
        is_first_request = True

        while next_url:
            # First request uses params, subsequent requests use next URL directly
            if is_first_request:
                response = self._get(next_url, url_conversion, params=request_params, **kwargs)
                is_first_request = False
            else:
                # next URL already contains all necessary query parameters
                response = self._get(next_url, url_conversion, **kwargs)

            yield from response['results']
            next_url = response.get('next')

    def exists(self, api, *args, **kwargs):
        return getattr(self, api)(*args, **kwargs)['count'] > 0

    def _validate_response_with_pydantic_model(self, response, pydantic_model):
        """Validate a response with a pydantic model."""
        # Check if model is a pydantic model (has the __pydantic_model__ attribute)
        if (
            hasattr(pydantic_model, '__pydantic_model__')
            or hasattr(pydantic_model, 'model_validate')
            or hasattr(pydantic_model, 'parse_obj')
        ):
            pydantic_model.model_validate(response)
            return response
        else:
            # Not a pydantic model
            raise TypeError('The provided model is not a pydantic model')

    def _validate_request_body_with_pydantic_model(self, request_body, pydantic_model):
        """Validate a request body with a pydantic model."""
        # Check if model is a pydantic model (has the __pydantic_model__ attribute)
        if (
            hasattr(pydantic_model, '__pydantic_model__')
            or hasattr(pydantic_model, 'model_validate')
            or hasattr(pydantic_model, 'parse_obj')
        ):
            # Validate the request body and convert to model instance
            model_instance = pydantic_model.model_validate(request_body)
            # Convert model to dict and remove None values
            return {k: v for k, v in model_instance.model_dump().items() if v is not None}
        else:
            # Not a pydantic model
            raise TypeError('The provided model is not a pydantic model')
