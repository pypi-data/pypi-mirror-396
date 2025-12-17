import pytest

from synapse_sdk.clients.agent.container import ContainerClientMixin
from synapse_sdk.plugins.models import PluginRelease


class DummyContainerClient(ContainerClientMixin):
    """Concrete client for testing the mixin behaviour."""

    def __init__(self):
        super().__init__('http://agent.local')

    def _get_headers(self):
        return {}


@pytest.fixture
def plugin_release_config():
    return {
        'name': 'Demo Plugin',
        'code': 'demo-plugin',
        'version': '1.0.0',
        'category': 'neural_net',
        'actions': {'gradio': {'entrypoint': 'plugin.gradio_interface.app'}},
    }


@pytest.fixture
def plugin_release(plugin_release_config):
    return PluginRelease(config=plugin_release_config)


def test_create_container_with_plugin_release_object(mocker, plugin_release):
    client = DummyContainerClient()
    mock_post = mocker.patch.object(client, '_post', return_value={'endpoint': 'http://localhost:7860'})

    params = {'foo': 'bar'}
    envs = {'ENV': 'VALUE'}
    labels = ['gradio', 'beta']
    metadata = {'team': 'sdk'}

    response = client.create_container(plugin_release, params=params, envs=envs, labels=labels, metadata=metadata)

    assert response == {'endpoint': 'http://localhost:7860'}
    mock_post.assert_called_once()

    call_path, call_kwargs = mock_post.call_args
    assert call_path[0] == 'containers/'

    payload = call_kwargs['data']
    assert payload['action'] == 'gradio'
    assert payload['entrypoint'] == 'plugin/gradio_interface.py'
    assert payload['plugin_release'] == plugin_release.code
    assert payload['plugin'] == plugin_release.plugin
    assert payload['version'] == plugin_release.version
    assert payload['params'] == params
    assert payload['envs'] == envs
    assert payload['labels'] == labels
    assert payload['metadata'] == metadata
    assert 'files' not in call_kwargs


def test_create_container_with_plugin_file(tmp_path, mocker):
    client = DummyContainerClient()
    mock_post = mocker.patch.object(client, '_post', return_value={'id': 'container-1'})

    archive = tmp_path / 'plugin.zip'
    archive.write_text('plugin archive')

    response = client.create_container('demo-plugin@1.0.0', plugin_file=archive)

    assert response == {'id': 'container-1'}
    mock_post.assert_called_once()
    call_path, call_kwargs = mock_post.call_args
    assert call_path[0] == 'containers/'
    assert call_kwargs['data']['plugin_release'] == 'demo-plugin@1.0.0'
    assert call_kwargs['files']['file'] == archive


def test_create_container_requires_identifier():
    client = DummyContainerClient()
    with pytest.raises(ValueError):
        client.create_container()


def test_create_container_invalid_plugin_release_type(tmp_path):
    client = DummyContainerClient()
    archive = tmp_path / 'plugin.zip'
    archive.write_text('plugin archive')

    with pytest.raises(TypeError):
        client.create_container(123, plugin_file=archive)


def test_create_container_missing_file(tmp_path):
    client = DummyContainerClient()
    missing = tmp_path / 'missing.zip'

    with pytest.raises(FileNotFoundError):
        client.create_container('demo-plugin@1.0.0', plugin_file=missing)


def test_list_containers_uses_list_helper(mocker):
    client = DummyContainerClient()
    mock_list = mocker.patch.object(client, '_list', return_value={'results': []})

    response = client.list_containers(params={'status': 'running'}, list_all=True)

    assert response == {'results': []}
    mock_list.assert_called_once_with('containers/', params={'status': 'running'}, list_all=True)


def test_get_container_calls_get(mocker):
    client = DummyContainerClient()
    mock_get = mocker.patch.object(client, '_get', return_value={'id': 'abc'})

    response = client.get_container('abc')

    assert response == {'id': 'abc'}
    mock_get.assert_called_once_with('containers/abc/')


def test_delete_container_calls_delete(mocker):
    client = DummyContainerClient()
    mock_delete = mocker.patch.object(client, '_delete', return_value={'status': 'removed'})

    response = client.delete_container('abc')

    assert response == {'status': 'removed'}
    mock_delete.assert_called_once_with('containers/abc/')
