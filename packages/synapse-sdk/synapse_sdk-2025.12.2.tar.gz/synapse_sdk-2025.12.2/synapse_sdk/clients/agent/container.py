from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

from synapse_sdk.clients.base import BaseClient


class ContainerClientMixin(BaseClient):
    """Client mixin exposing the agent container management API."""

    def health_check(self):
        """Perform a health check on Docker sock."""
        path = 'health/'
        return self._get(path)

    def list_containers(self, params: Optional[Dict[str, Any]] = None, *, list_all: bool = False):
        """List containers managed by the agent.

        Args:
            params: Optional query parameters (e.g. {'status': 'running'}).
            list_all: When True, returns ``(generator, count)`` covering every page.

        Returns:
            dict | tuple: Standard paginated response or a tuple for ``list_all``.
        """
        path = 'containers/'
        return self._list(path, params=params, list_all=list_all)

    def get_container(self, container_id: Union[int, str]):
        """Retrieve details for a specific container."""
        path = f'containers/{container_id}/'
        return self._get(path)

    def delete_container(self, container_id: Union[int, str]):
        """Stop and remove a container."""
        path = f'containers/{container_id}/'
        return self._delete(path)

    def create_container(
        self,
        plugin_release: Optional[Union[str, Any]] = None,
        *,
        model: Optional[int] = None,
        params: Optional[Dict[str, Any]] = None,
        envs: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        labels: Optional[Iterable[str]] = None,
        plugin_file: Optional[Union[str, Path]] = None,
    ):
        """Create a Docker container running a plugin Gradio interface.

        If a container with the same ``plugin_release`` and ``model`` already exists,
        it will be restarted instead of creating a new one.

        Args:
            plugin_release: Plugin identifier. Accepts either ``synapse_sdk.plugins.models.PluginRelease``
                instances or the ``"<plugin_code>@<version>"`` shorthand string.
            model: Optional model ID to associate with the container. Used together with
                ``plugin_release`` to uniquely identify a container for restart behavior.
            params: Arbitrary parameters forwarded to ``plugin/gradio_interface.py``.
            envs: Extra environment variables injected into the container.
            metadata: Additional metadata stored with the container record.
            labels: Optional container labels/tags for display or filtering.
            plugin_file: Optional path to a packaged plugin release to upload directly.
                The archive must contain ``plugin/gradio_interface.py``.

        Returns:
            dict: Container creation response that includes the exposed Gradio endpoint.
                If an existing container was restarted, the response includes ``restarted: True``.

        Raises:
            FileNotFoundError: If ``plugin_file`` is provided but does not exist.
            ValueError: If neither ``plugin_release`` nor ``plugin_file`` are provided.
        """
        if not plugin_release and not plugin_file:
            raise ValueError('Either "plugin_release" or "plugin_file" must be provided to create a container.')

        data: Dict[str, Any] = {}

        if plugin_release:
            data.update(self._serialize_plugin_release(plugin_release))

        if model is not None:
            data['model'] = model

        optional_payload = {
            'params': params if params is not None else None,
            'envs': envs or None,
            'metadata': metadata or None,
            'labels': list(labels) if labels else None,
        }
        data.update({key: value for key, value in optional_payload.items() if value is not None})

        files = None
        if plugin_file:
            file_path = Path(plugin_file)
            if not file_path.exists():
                raise FileNotFoundError(f'Plugin release file not found: {file_path}')
            files = {'file': file_path}
        post_kwargs = {'data': data}
        if files:
            post_kwargs['files'] = files

        return self._post('containers/', **post_kwargs)

    @staticmethod
    def _serialize_plugin_release(plugin_release: Union[str, Any]) -> Dict[str, Any]:
        """Normalize plugin release data for API payloads."""
        if hasattr(plugin_release, 'code') and hasattr(plugin_release, 'version'):
            payload = {
                'plugin_release': plugin_release.code,
                'plugin': getattr(plugin_release, 'plugin', None),
                'version': plugin_release.version,
            }

            # Extract action and entrypoint from the first action in the config
            if hasattr(plugin_release, 'config') and 'actions' in plugin_release.config:
                actions = plugin_release.config['actions']
                if actions:
                    # Get the first action (typically 'gradio')
                    action_name = next(iter(actions.keys()))
                    action_config = actions[action_name]
                    payload['action'] = action_name

                    # Convert entrypoint from dotted path to file path
                    if 'entrypoint' in action_config:
                        entrypoint = action_config['entrypoint']
                        # Convert 'plugin.gradio_interface.app' to 'plugin/gradio_interface.py'
                        file_path = entrypoint.rsplit('.', 1)[0].replace('.', '/') + '.py'
                        payload['entrypoint'] = file_path

            return payload

        if isinstance(plugin_release, str):
            payload = {'plugin_release': plugin_release}
            if '@' in plugin_release:
                plugin, version = plugin_release.rsplit('@', 1)
                payload.setdefault('plugin', plugin)
                payload.setdefault('version', version)
            return payload

        raise TypeError('plugin_release must be a PluginRelease instance or a formatted string "code@version"')
