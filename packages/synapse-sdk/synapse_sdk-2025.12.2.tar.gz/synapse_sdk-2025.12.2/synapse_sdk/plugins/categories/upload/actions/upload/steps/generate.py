from ..context import StepResult, UploadContext
from ..enums import LogCode, UploadStatus
from .base import BaseStep


class GenerateDataUnitsStep(BaseStep):
    """Generate data units from uploaded files."""

    @property
    def name(self) -> str:
        return 'generate_data_units'

    @property
    def progress_weight(self) -> float:
        return 0.20

    def execute(self, context: UploadContext) -> StepResult:
        """Execute data unit generation step."""
        data_unit_strategy = context.strategies.get('data_unit')
        if not data_unit_strategy:
            return self.create_error_result('Data unit strategy not found')

        if not context.uploaded_files:
            context.run.log_message_with_code(LogCode.NO_DATA_UNITS_GENERATED)
            return self.create_error_result('No uploaded files to generate data units from')

        try:
            # Setup progress tracking
            upload_result_count = len(context.uploaded_files)
            context.run.set_progress(0, upload_result_count, category='generate_data_units')
            context.run.log_message_with_code(LogCode.GENERATING_DATA_UNITS)

            # Initialize metrics
            initial_metrics = {'stand_by': upload_result_count, 'success': 0, 'failed': 0}
            context.update_metrics('data_units', initial_metrics)
            context.run.set_metrics(initial_metrics, category='data_units')

            # Get batch size from parameters
            batch_size = context.get_param('creating_data_unit_batch_size', 1)

            # Generate data units using strategy
            generated_data_units = data_unit_strategy.generate(context.uploaded_files, batch_size)

            # Update context
            context.add_data_units(generated_data_units)

            # Log data unit results
            for data_unit in generated_data_units:
                context.run.log_data_unit(
                    data_unit.get('id'), UploadStatus.SUCCESS, data_unit_meta=data_unit.get('meta')
                )

            # Update final metrics
            final_metrics = {'stand_by': 0, 'success': len(generated_data_units), 'failed': 0}
            context.update_metrics('data_units', final_metrics)
            context.run.set_metrics(final_metrics, category='data_units')

            # Handle success vs failure cases
            if generated_data_units:
                # Success: Set completion progress with elapsed time
                context.run.set_progress(upload_result_count, upload_result_count, category='generate_data_units')
                return self.create_success_result(
                    data={'generated_data_units': generated_data_units},
                    rollback_data={'data_units_count': len(generated_data_units), 'batch_size': batch_size},
                )
            else:
                # Failure: Mark as failed with elapsed time but no completion
                context.run.set_progress_failed(category='generate_data_units')
                return self.create_error_result('No data units were successfully generated')

        except Exception as e:
            # Exception: Mark as failed with elapsed time
            context.run.set_progress_failed(category='generate_data_units')
            context.run.log_message_with_code(LogCode.DATA_UNIT_BATCH_FAILED, str(e))
            return self.create_error_result(f'Data unit generation failed: {str(e)}')

    def can_skip(self, context: UploadContext) -> bool:
        """Data unit generation cannot be skipped."""
        return False

    def rollback(self, context: UploadContext) -> None:
        """Rollback data unit generation."""
        # In a real implementation, this would delete generated data units
        # For now, just clear the data units list and log
        context.data_units.clear()
        context.run.log_message_with_code(LogCode.ROLLBACK_DATA_UNIT_GENERATION)

    def validate_prerequisites(self, context: UploadContext) -> None:
        """Validate prerequisites for data unit generation."""
        if not context.uploaded_files:
            raise ValueError('No uploaded files available for data unit generation')
