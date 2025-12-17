"""Annotation strategies for ToTask action."""

from typing import Any, Dict

from ..enums import LogCode
from .base import AnnotationStrategy, ToTaskContext


class FileAnnotationStrategy(AnnotationStrategy):
    """Strategy for file-based annotation processing."""

    def process_task(
        self, context: ToTaskContext, task_id: int, task_data: Dict[str, Any], target_specification_name: str, **kwargs
    ) -> Dict[str, Any]:
        """Process a single task for file-based annotation.

        Args:
            context: Shared context for the action execution
            task_id: The task ID to process
            task_data: The task data dictionary
            target_specification_name: The name of the target specification
            **kwargs: Additional parameters

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = context.client
            logger = context.logger

            # Get data unit
            data_unit = task_data.get('data_unit')
            if not data_unit:
                error_msg = 'Task does not have a data unit'
                logger.log_annotate_task_event(LogCode.NO_DATA_UNIT, task_id)
                return {'success': False, 'error': error_msg}

            # Get data unit files
            data_unit_files = data_unit.get('files', {})
            if not data_unit_files:
                error_msg = 'Data unit does not have files'
                logger.log_annotate_task_event(LogCode.NO_DATA_UNIT_FILES, task_id)
                return {'success': False, 'error': error_msg}

            # Extract primary file URL from task data
            primary_file_url, primary_file_original_name = self._extract_primary_file_url(task_data)
            if not primary_file_url:
                error_msg = 'Primary image URL not found in task data'
                logger.log_annotate_task_event(LogCode.PRIMARY_IMAGE_URL_NOT_FOUND, task_id)
                return {'success': False, 'error': error_msg}

            # Get target specification file
            target_file = data_unit_files.get(target_specification_name)
            if not target_file:
                error_msg = 'File specification not found'
                logger.log_annotate_task_event(LogCode.FILE_SPEC_NOT_FOUND, task_id)
                return {'success': False, 'error': error_msg}

            # Get target file details
            target_file_url = target_file.get('url')
            target_file_original_name = target_file.get('file_name_original')

            if not target_file_original_name:
                error_msg = 'File original name not found'
                logger.log_annotate_task_event(LogCode.FILE_ORIGINAL_NAME_NOT_FOUND, task_id)
                return {'success': False, 'error': error_msg}

            if not target_file_url:
                error_msg = 'URL not found'
                logger.log_annotate_task_event(LogCode.URL_NOT_FOUND, task_id)
                return {'success': False, 'error': error_msg}

            # Fetch and process the data using template
            try:
                # Convert data to task object using action's entrypoint
                annotation_to_task = context.entrypoint(logger)
                converted_data = annotation_to_task.convert_data_from_file(
                    primary_file_url, primary_file_original_name, target_file_url, target_file_original_name
                )
            except Exception as e:
                if 'requests' in str(type(e)):
                    error_msg = f'Failed to fetch data from URL: {str(e)}'
                    logger.log_annotate_task_event(LogCode.FETCH_DATA_FAILED, target_file_url, task_id)
                else:
                    error_msg = f'Failed to convert data to task object: {str(e)}'
                    logger.log_annotate_task_event(LogCode.CONVERT_DATA_FAILED, str(e), task_id)
                return {'success': False, 'error': error_msg}

            # Submit annotation data
            try:
                client.annotate_task_data(task_id, data={'action': 'submit', 'data': converted_data})
                return {'success': True}
            except Exception as e:
                error_msg = f'Failed to submit annotation data: {str(e)}'
                logger.log_annotate_task_event(LogCode.ANNOTATION_SUBMISSION_FAILED, task_id, str(e))
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to process file annotation for task {task_id}: {str(e)}'
            context.logger.log_annotate_task_event(LogCode.TASK_PROCESSING_FAILED, task_id, str(e))
            return {'success': False, 'error': error_msg}

    def _extract_primary_file_url(self, task_data: Dict[str, Any]) -> tuple:
        """Extract the primary file URL from task data.

        Args:
            task_data: The task data dictionary

        Returns:
            Tuple of (primary_file_url, primary_file_original_name)
        """
        data_unit = task_data.get('data_unit', {})
        files = data_unit.get('files', {})

        for file_info in files.values():
            if isinstance(file_info, dict) and file_info.get('is_primary') and file_info.get('url'):
                return file_info['url'], file_info.get('file_name_original')

        return None, None


class InferenceAnnotationStrategy(AnnotationStrategy):
    """Strategy for inference-based annotation processing."""

    def process_task(self, context: ToTaskContext, task_id: int, task_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process a single task for inference-based annotation.

        Args:
            context: Shared context for the action execution
            task_id: The task ID to process
            task_data: The task data dictionary
            **kwargs: Additional parameters

        Returns:
            Dict with 'success' boolean and optional 'error' message
        """
        try:
            client = context.client
            logger = context.logger

            # Get pre-processor ID from parameters
            pre_processor_id = context.params.get('pre_processor')
            if not pre_processor_id:
                error_msg = 'Pre-processor ID is required for inference annotation method'
                logger.log_annotate_task_event(LogCode.NO_PREPROCESSOR_ID, task_id)
                return {'success': False, 'error': error_msg}

            # Get pre-processor info using factory-created strategy
            from ..factory import ToTaskStrategyFactory

            factory = ToTaskStrategyFactory()
            preprocessor_strategy = factory.create_preprocessor_strategy()

            pre_processor_info = preprocessor_strategy.get_preprocessor_info(context, pre_processor_id)
            if not pre_processor_info['success']:
                error_msg = pre_processor_info.get('error', 'Failed to get pre-processor info')
                logger.log_annotate_task_event(LogCode.INFERENCE_PREPROCESSOR_FAILED, task_id, error_msg)
                return pre_processor_info

            pre_processor_code = pre_processor_info['code']
            pre_processor_version = pre_processor_info['version']

            # Ensure pre-processor is running
            pre_processor_status = preprocessor_strategy.ensure_preprocessor_running(context, pre_processor_code)
            if not pre_processor_status['success']:
                error_msg = pre_processor_status.get('error', 'Failed to ensure pre-processor running')
                logger.log_annotate_task_event(LogCode.INFERENCE_PREPROCESSOR_FAILED, task_id, error_msg)
                return pre_processor_status

            # Extract primary file URL using factory-created strategy
            extraction_strategy = factory.create_extraction_strategy(context.annotation_method)
            primary_file_url, _ = extraction_strategy.extract_data(context, task_data)
            if not primary_file_url:
                error_msg = 'Primary image URL not found in task data'
                logger.log_annotate_task_event(LogCode.PRIMARY_IMAGE_URL_NOT_FOUND, task_id)
                return {'success': False, 'error': error_msg}

            # Run inference
            inference_result = self._run_inference(
                client,
                pre_processor_code,
                pre_processor_version,
                primary_file_url,
                context.params['agent'],
                context.params['model'],
                pre_processor_params=context.params.get('pre_processor_params', {}),
            )
            if not inference_result['success']:
                error_msg = inference_result.get('error', 'Failed to run inference')
                logger.log_annotate_task_event(LogCode.INFERENCE_PREPROCESSOR_FAILED, task_id, error_msg)
                return inference_result

            # Convert and submit inference data
            try:
                # This would need to be injected or configured based on the action's entrypoint
                # For now, we'll assume the conversion is done externally
                inference_data = inference_result['data']  # Simplified for refactoring

                annotation_to_task = context.entrypoint(logger)
                converted_result = annotation_to_task.convert_data_from_inference(inference_data)

                client.annotate_task_data(task_id, data={'action': 'submit', 'data': converted_result})
                return {'success': True, 'pre_processor_id': pre_processor_id}

            except Exception as e:
                error_msg = f'Failed to convert/submit inference data: {str(e)}'
                logger.log_annotate_task_event(LogCode.INFERENCE_PREPROCESSOR_FAILED, task_id, error_msg)
                return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f'Failed to process inference for task {task_id}: {str(e)}'
            context.logger.log_message_with_code(LogCode.INFERENCE_PROCESSING_FAILED, task_id, str(e))
            return {'success': False, 'error': error_msg}

    def _run_inference(
        self,
        client: Any,
        pre_processor_code: str,
        pre_processor_version: str,
        primary_file_url: str,
        agent: int,
        model: int,
        pre_processor_params: Dict[str, Any] = {},
    ) -> Dict[str, Any]:
        """Run inference using the pre-processor.

        Args:
            client: Backend client instance
            pre_processor_code: Pre-processor code
            pre_processor_version: Pre-processor version
            primary_file_url: URL of the primary file to process
            agent: Agent id for inference
            model: Model id for inference
            pre_processor_params: Additional parameters for the pre-processor

        Returns:
            Dict with inference results or error
        """
        try:
            if not agent or not model:
                return {'success': False, 'error': 'Parameters not available'}

            pre_processor_params['image_path'] = primary_file_url

            inference_payload = {
                'agent': agent,
                'action': 'inference',
                'version': pre_processor_version,
                'params': {
                    'model': model,
                    'method': 'post',
                    'json': pre_processor_params,
                },
            }

            inference_data = client.run_plugin(pre_processor_code, inference_payload)

            # Every inference api should return None if failed to inference.
            if inference_data is None:
                return {'success': False, 'error': 'Inference data is None'}

            return {'success': True, 'data': inference_data}

        except Exception as e:
            return {'success': False, 'error': f'Failed to run inference: {str(e)}'}
