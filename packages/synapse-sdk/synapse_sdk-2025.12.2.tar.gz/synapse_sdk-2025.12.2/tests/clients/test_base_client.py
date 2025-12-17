from unittest.mock import patch

import pytest
from pydantic import ValidationError

from synapse_sdk.clients.backend.models import Storage, UpdateJob
from synapse_sdk.clients.base import BaseClient


@pytest.fixture
def base_client():
    return BaseClient('http://fake_url')


@pytest.fixture
def valid_storage_response():
    return {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'file_system',
        'configuration': {},
        'is_default': True,
    }


@pytest.fixture
def invalid_storage_response(valid_storage_response):
    response = valid_storage_response.copy()
    response['provider'] = 'invalid_provider'
    return response


def test_validate_response_with_pydantic_model_success(base_client, valid_storage_response):
    validated_response = base_client._validate_response_with_pydantic_model(valid_storage_response, Storage)
    assert validated_response['id'] == valid_storage_response['id']


def test_validate_response_with_pydantic_model_invalid_data(base_client, invalid_storage_response):
    with pytest.raises(ValidationError) as exc_info:
        base_client._validate_response_with_pydantic_model(invalid_storage_response, Storage)
    assert '1 validation error' in str(exc_info.value)


def test_validate_response_with_pydantic_model_not_pydantic_model(base_client, valid_storage_response):
    with pytest.raises(TypeError) as exc_info:
        base_client._validate_response_with_pydantic_model(valid_storage_response, {})
    assert 'The provided model is not a pydantic model' in str(exc_info.value)


def test_validate_update_job_request_body_with_pydantic_model_success(base_client):
    request_body = {
        'status': 'running',
    }
    validated_request_body = base_client._validate_request_body_with_pydantic_model(
        request_body,
        UpdateJob,
    )
    assert validated_request_body['status'] == request_body['status']


def test_get_url_with_relative_path(base_client):
    """Test _get_url with relative path."""
    url = base_client._get_url('api/jobs')
    assert url == 'http://fake_url/api/jobs'


def test_get_url_with_leading_slash(base_client):
    """Test _get_url with leading slash in path."""
    url = base_client._get_url('/api/jobs')
    assert url == 'http://fake_url/api/jobs'


def test_get_url_with_full_url(base_client):
    """Test _get_url with full URL."""
    full_url = 'https://example.com/api/jobs'
    url = base_client._get_url(full_url)
    assert url == full_url


def test_get_url_with_trailing_slash_enabled(base_client):
    """Test _get_url with trailing_slash=True."""
    url = base_client._get_url('api/jobs', trailing_slash=True)
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_already_present(base_client):
    """Test _get_url with trailing_slash=True when slash already present."""
    url = base_client._get_url('api/jobs/', trailing_slash=True)
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_disabled(base_client):
    """Test _get_url with trailing_slash=False (default)."""
    url = base_client._get_url('api/jobs/')
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_full_url(base_client):
    """Test _get_url with trailing_slash=True and full URL."""
    full_url = 'https://example.com/api/jobs'
    url = base_client._get_url(full_url, trailing_slash=True)
    assert url == 'https://example.com/api/jobs/'


def test_get_url_with_http_protocol(base_client):
    """Test _get_url handles http:// URLs."""
    http_url = 'http://other.com/api'
    url = base_client._get_url(http_url)
    assert url == http_url


def test_get_url_with_https_protocol(base_client):
    """Test _get_url handles https:// URLs."""
    https_url = 'https://secure.com/api'
    url = base_client._get_url(https_url)
    assert url == https_url


def test_list_all_pagination_no_duplicate_page_size(base_client):
    """Test _list_all doesn't duplicate page_size query parameter in next URL."""
    # Mock the _get method to simulate paginated responses
    page1_response = {
        'results': [{'id': 1}, {'id': 2}],
        'next': 'http://fake_url/api/items/?page=2&page_size=100',
        'count': 4,
    }
    page2_response = {
        'results': [{'id': 3}, {'id': 4}],
        'next': None,
        'count': 4,
    }

    with patch.object(base_client, '_get') as mock_get:
        mock_get.side_effect = [page1_response, page2_response]

        # Call _list_all
        results = list(base_client._list_all('api/items/'))

        # Verify all results are returned
        assert len(results) == 4
        assert results == [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]

        # Verify _get was called twice
        assert mock_get.call_count == 2

        # First call should add page_size to params
        first_call = mock_get.call_args_list[0]
        assert first_call[0][0] == 'api/items/'
        assert first_call[1]['params']['page_size'] == 100

        # Second call should use next URL without additional params
        second_call = mock_get.call_args_list[1]
        assert second_call[0][0] == 'http://fake_url/api/items/?page=2&page_size=100'
        # Should not have params argument or should be empty
        assert 'params' not in second_call[1] or not second_call[1].get('params')


def test_list_all_with_params(base_client):
    """Test _list_all passes user params to first request only."""
    # Mock the _get method to simulate paginated responses
    page1_response = {
        'results': [{'id': 1, 'status': 'active'}],
        'next': 'http://fake_url/api/items/?page=2&status=active&page_size=100',
        'count': 2,
    }
    page2_response = {
        'results': [{'id': 2, 'status': 'active'}],
        'next': None,
        'count': 2,
    }

    with patch.object(base_client, '_get') as mock_get:
        mock_get.side_effect = [page1_response, page2_response]

        # Call _list_all with custom params
        user_params = {'status': 'active'}
        results = list(base_client._list_all('api/items/', params=user_params))

        # Verify all results are returned
        assert len(results) == 2
        assert results == [{'id': 1, 'status': 'active'}, {'id': 2, 'status': 'active'}]

        # Verify _get was called twice
        assert mock_get.call_count == 2

        # First call should have user params + page_size
        first_call = mock_get.call_args_list[0]
        assert first_call[0][0] == 'api/items/'
        assert first_call[1]['params']['status'] == 'active'
        assert first_call[1]['params']['page_size'] == 100

        # Second call should use next URL (which already includes params)
        second_call = mock_get.call_args_list[1]
        assert second_call[0][0] == 'http://fake_url/api/items/?page=2&status=active&page_size=100'


def test_list_all_with_url_conversion(base_client):
    """Test _list_all applies url_conversion to all pages."""
    # Mock the _get method to simulate paginated responses
    page1_response = {
        'results': [{'id': 1}],
        'next': 'http://fake_url/api/items/?page=2&page_size=100',
        'count': 2,
    }
    page2_response = {
        'results': [{'id': 2}],
        'next': None,
        'count': 2,
    }

    with patch.object(base_client, '_get') as mock_get:
        mock_get.side_effect = [page1_response, page2_response]

        # Call _list_all with url_conversion
        url_conversion = {'files_fields': ['files'], 'is_list': True}
        # Consume the generator to trigger all _get calls
        list(base_client._list_all('api/items/', url_conversion=url_conversion))

        # Verify _get was called twice with url_conversion
        assert mock_get.call_count == 2

        # Both calls should have url_conversion argument
        first_call = mock_get.call_args_list[0]
        assert first_call[0][1] == url_conversion  # Second positional arg is url_conversion

        second_call = mock_get.call_args_list[1]
        assert second_call[0][1] == url_conversion  # Second positional arg is url_conversion


def test_list_all_multiple_pages(base_client):
    """Test _list_all handles multiple pages correctly."""
    # Mock the _get method to simulate 3 pages of results
    page1_response = {
        'results': [{'id': 1}, {'id': 2}],
        'next': 'http://fake_url/api/items/?page=2&page_size=2',
        'count': 5,
    }
    page2_response = {
        'results': [{'id': 3}, {'id': 4}],
        'next': 'http://fake_url/api/items/?page=3&page_size=2',
        'count': 5,
    }
    page3_response = {
        'results': [{'id': 5}],
        'next': None,
        'count': 5,
    }

    with patch.object(base_client, '_get') as mock_get:
        mock_get.side_effect = [page1_response, page2_response, page3_response]

        # Call _list_all
        results = list(base_client._list_all('api/items/', params={'page_size': 2}))

        # Verify all results from 3 pages are returned
        assert len(results) == 5
        assert results == [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}, {'id': 5}]

        # Verify _get was called 3 times
        assert mock_get.call_count == 3
