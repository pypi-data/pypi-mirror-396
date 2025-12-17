from unittest.mock import Mock

from synapse_sdk.plugins.categories.upload.actions.upload import LOG_MESSAGES, LogCode, UploadRun
from synapse_sdk.shared.enums import Context


class TestUploadRun:
    """Test UploadRun class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.job_id = 'test-job-123'
        self.context = {
            'plugin_release': Mock(),
            'progress_categories': None,
            'metrics_categories': None,
            'params': {'test': 'param'},
            'envs': {'TEST': 'env'},
            'debug': False,
        }
        self.run = UploadRun(self.job_id, self.context)
        self.run.client._session = Mock()

    def test_upload_run_initialization(self):
        """Test UploadRun initialization."""
        assert self.run.job_id == 'test-job-123'
        assert self.run.context == self.context

    def test_log_message_with_code_valid_code(self):
        """Test logging with valid LogCode."""
        # Mock the log_message method
        self.run.log_message = Mock()

        # Test with a known log code
        self.run.log_message_with_code(LogCode.VALIDATION_FAILED)

        # Verify log_message was called
        self.run.log_message.assert_called_once()
        call_args = self.run.log_message.call_args[0]
        assert len(call_args) >= 1
        assert 'Validation failed' in call_args[0]

    def test_log_message_with_code_with_args(self):
        """Test logging with LogCode and format arguments."""
        # Mock the log_message method
        self.run.log_message = Mock()

        # Use a log code that supports formatting
        self.run.log_message_with_code(LogCode.VALIDATION_FAILED, 'test error')

        # Verify log_message was called
        self.run.log_message.assert_called_once()

    def test_log_message_with_code_with_custom_level(self):
        """Test logging with custom level override."""
        # Mock the log_message method
        self.run.log_message = Mock()

        # Test with custom level
        self.run.log_message_with_code(LogCode.NO_FILES_FOUND, level=Context.WARNING)

        # Verify log_message was called
        self.run.log_message.assert_called_once()

    def test_log_message_with_code_unknown_code(self):
        """Test logging with unknown LogCode."""
        # Mock the log_message method
        self.run.log_message = Mock()

        # Create a fake log code that doesn't exist in LOG_MESSAGES
        fake_code = 'UNKNOWN_CODE'

        # This should handle the unknown code gracefully
        self.run.log_message_with_code(fake_code)

        # Verify log_message was called with unknown code message
        self.run.log_message.assert_called_once()
        call_args = self.run.log_message.call_args[0]
        assert 'Unknown log code' in call_args[0]
        assert fake_code in call_args[0]

    def test_log_upload_event_basic(self):
        """Test log_upload_event method."""
        # Mock both methods
        self.run.log_message_with_code = Mock()

        # Test log_upload_event
        self.run.log_upload_event(LogCode.FILES_DISCOVERED)

        # Verify log_message_with_code was called
        self.run.log_message_with_code.assert_called_once_with(LogCode.FILES_DISCOVERED, level=None)

    def test_log_upload_event_with_args_and_level(self):
        """Test log_upload_event with arguments and level."""
        # Mock the method
        self.run.log_message_with_code = Mock()

        # Test with arguments and level
        self.run.log_upload_event(LogCode.EXCEL_SECURITY_VIOLATION, 'test.xlsx', level=Context.DANGER)

        # Verify log_message_with_code was called with correct arguments
        self.run.log_message_with_code.assert_called_once_with(
            LogCode.EXCEL_SECURITY_VIOLATION, 'test.xlsx', level=Context.DANGER
        )

    def test_log_messages_structure_integration(self):
        """Test integration with LOG_MESSAGES structure."""
        # Verify that LOG_MESSAGES contains expected codes
        assert LogCode.VALIDATION_FAILED in LOG_MESSAGES
        assert LogCode.NO_FILES_FOUND in LOG_MESSAGES

        # Test that message config has proper structure
        config = LOG_MESSAGES[LogCode.VALIDATION_FAILED]
        assert 'message' in config
        assert 'level' in config
        assert isinstance(config['message'], str)
        assert hasattr(config['level'], 'value')  # Context enum
