"""Pre-processor management strategies for ToTask action."""

import time
from typing import Any, Dict, List

from .base import PreProcessorStrategy, ToTaskContext


class PreProcessorManagementStrategy(PreProcessorStrategy):
    """Strategy for managing pre-processor lifecycle."""

    def _get_preprocessor_config(self, context: ToTaskContext, preprocessor_id: int) -> Dict[str, Any]:
        """Retrieve pre-processor configuration from the backend.

        Args:
            context: Shared context for the action execution
            preprocessor_id: The pre-processor ID

        Returns:
            Dict with 'success', 'config', 'version', and optional 'error'
        """
        try:
            client = context.client
            pre_processor_response = client.get_plugin_release(preprocessor_id)

            if isinstance(pre_processor_response, str):
                return {'success': False, 'error': 'Invalid pre-processor response received'}

            if not isinstance(pre_processor_response, dict):
                return {'success': False, 'error': 'Unexpected pre-processor response format'}

            config = pre_processor_response.get('config', {})
            version = pre_processor_response.get('version')

            return {'success': True, 'config': config, 'version': version}

        except Exception as e:
            return {'success': False, 'error': f'Failed to get pre-processor config: {str(e)}'}

    def get_preprocessor_info(self, context: ToTaskContext, preprocessor_id: int) -> Dict[str, Any]:
        """Get pre-processor information from the backend.

        Args:
            context: Shared context for the action execution
            preprocessor_id: The pre-processor ID

        Returns:
            Dict with pre-processor info or error
        """
        config_result = self._get_preprocessor_config(context, preprocessor_id)
        if not config_result['success']:
            return config_result

        config = config_result['config']
        code = config.get('code')
        version = config_result['version']

        if not code or not version:
            return {'success': False, 'error': 'Invalid pre-processor configuration'}

        return {'success': True, 'code': code, 'version': version}

    def _get_running_serve_apps(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Get list of running serve applications for a preprocessor.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict with 'success', 'running_apps' (list), and optional 'error'
        """
        try:
            client = context.client
            list_serve_applications_params = {
                'plugin_code': preprocessor_code,
                'job__agent': context.params.get('agent') if context.params else None,
            }

            serve_applications_response = client.list_serve_applications(params=list_serve_applications_params)
            if isinstance(serve_applications_response, str):
                return {'success': False, 'running_apps': [], 'error': 'Invalid serve applications response'}

            if not isinstance(serve_applications_response, dict):
                return {'success': False, 'running_apps': [], 'error': 'Unexpected serve applications response format'}

            results = serve_applications_response.get('results', [])
            running_apps: List[Dict[str, Any]] = [
                app for app in results if isinstance(app, dict) and app.get('status') == 'RUNNING'
            ]

            return {'success': True, 'running_apps': running_apps}

        except Exception as e:
            return {'success': False, 'running_apps': [], 'error': f'Failed to get running serve apps: {str(e)}'}

    def ensure_preprocessor_running(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Ensure the pre-processor is running, restart if necessary.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure
        """
        try:
            # Check if pre-processor is already running
            result = self._get_running_serve_apps(context, preprocessor_code)
            if not result['success']:
                return {'success': False, 'error': result.get('error', 'Failed to check running apps')}

            if result['running_apps']:
                return {'success': True}

            # If not running, restart the pre-processor
            restart_result = self._restart_preprocessor(context, preprocessor_code)
            if not restart_result['success']:
                return restart_result

            return {'success': True}

        except Exception as e:
            return {'success': False, 'error': f'Failed to ensure pre-processor running: {str(e)}'}

    def _restart_preprocessor(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Restart the pre-processor and wait for it to be running.

        Starts the pre-processor deployment and polls for up to 3 minutes
        to verify it is running, logging progress messages during the wait.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure
        """
        MAX_WAIT_SECONDS = 180  # 3 minutes
        POLL_INTERVAL_SECONDS = 10

        try:
            # Start deployment
            start_result = self._start_preprocessor_deployment(context, preprocessor_code)
            if not start_result['success']:
                return start_result

            context.logger.log_message('Pre-processor deployment started, waiting for it to be ready...')

            # Poll for running status with logging
            return self._wait_for_preprocessor_ready(
                context, preprocessor_code, MAX_WAIT_SECONDS, POLL_INTERVAL_SECONDS
            )

        except Exception as e:
            return {'success': False, 'error': f'Failed to restart pre-processor: {str(e)}'}

    def _start_preprocessor_deployment(self, context: ToTaskContext, preprocessor_code: str) -> Dict[str, Any]:
        """Start the pre-processor deployment.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code

        Returns:
            Dict indicating success or failure with optional job_id
        """
        try:
            # Retrieve Pre-Processor Configuration
            pre_processor_id = context.params.get('pre_processor')
            if not pre_processor_id:
                return {'success': False, 'error': 'No pre-processor ID provided'}

            config_result = self._get_preprocessor_config(context, pre_processor_id)
            if not config_result['success']:
                return config_result

            config = config_result['config']
            inference_config = config.get('actions', {}).get('inference', {})
            required_resources = inference_config.get('required_resources', {})

            # Build deployment payload
            serve_application_deployment_payload = {
                'agent': context.params.get('agent') if context.params else None,
                'action': 'deployment',
                'params': {
                    'num_cpus': required_resources.get('required_cpu_count', 1),
                    'num_gpus': required_resources.get('required_gpu_count', 0.1),
                },
                'debug': True,
            }

            deployment_result = context.client.run_plugin(
                preprocessor_code,
                serve_application_deployment_payload,
            )

            deployment_job_id = deployment_result.get('job_id')
            if not deployment_job_id:
                return {'success': False, 'error': 'No deployment job ID returned'}

            return {'success': True, 'job_id': deployment_job_id}

        except Exception as e:
            return {'success': False, 'error': f'Failed to start deployment: {str(e)}'}

    def _wait_for_preprocessor_ready(
        self,
        context: ToTaskContext,
        preprocessor_code: str,
        max_wait_seconds: int,
        poll_interval_seconds: int,
    ) -> Dict[str, Any]:
        """Wait for the pre-processor to be running with polling and logging.

        Args:
            context: Shared context for the action execution
            preprocessor_code: The pre-processor code
            max_wait_seconds: Maximum time to wait in seconds
            poll_interval_seconds: Interval between polling attempts in seconds

        Returns:
            Dict indicating success or failure
        """
        max_attempts = max_wait_seconds // poll_interval_seconds

        for attempt in range(max_attempts):
            elapsed_seconds = attempt * poll_interval_seconds
            context.logger.log_message(
                f'Waiting for pre-processor to start... ({elapsed_seconds}s / {max_wait_seconds}s)'
            )

            time.sleep(poll_interval_seconds)

            result = self._get_running_serve_apps(context, preprocessor_code)
            if not result['success']:
                continue  # Keep trying on transient errors

            if result['running_apps']:
                context.logger.log_message('Pre-processor started successfully')
                return {'success': True}

        return {'success': False, 'error': f'Pre-processor failed to start within {max_wait_seconds} seconds'}
