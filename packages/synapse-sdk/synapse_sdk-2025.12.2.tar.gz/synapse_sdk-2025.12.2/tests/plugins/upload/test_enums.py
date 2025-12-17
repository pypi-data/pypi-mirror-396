from synapse_sdk.plugins.categories.upload.actions.upload import LOG_MESSAGES, LogCode, UploadStatus
from synapse_sdk.shared.enums import Context


class TestUploadStatus:
    """Test UploadStatus enum."""

    def test_upload_status_values(self):
        """Test UploadStatus enum values."""
        assert UploadStatus.SUCCESS == 'success'
        assert UploadStatus.FAILED == 'failed'

    def test_upload_status_string_conversion(self):
        """Test UploadStatus string conversion."""
        assert UploadStatus.SUCCESS.value == 'success'
        assert UploadStatus.FAILED.value == 'failed'


class TestLogCode:
    """Test LogCode enum."""

    def test_log_code_values(self):
        """Test LogCode enum has expected values."""
        assert LogCode.VALIDATION_FAILED == 'VALIDATION_FAILED'
        assert LogCode.NO_FILES_FOUND == 'NO_FILES_FOUND'
        assert LogCode.EXCEL_SECURITY_VIOLATION == 'EXCEL_SECURITY_VIOLATION'

    def test_log_code_string_conversion(self):
        """Test LogCode string conversion."""
        assert LogCode.VALIDATION_FAILED.value == 'VALIDATION_FAILED'
        assert LogCode.NO_FILES_FOUND.value == 'NO_FILES_FOUND'

    def test_log_code_inheritance(self):
        """Test LogCode inherits from str and Enum."""
        assert isinstance(LogCode.VALIDATION_FAILED, str)


class TestLogMessages:
    """Test LOG_MESSAGES dictionary."""

    def test_log_messages_structure(self):
        """Test LOG_MESSAGES has proper structure."""
        assert isinstance(LOG_MESSAGES, dict)
        assert len(LOG_MESSAGES) > 0

    def test_log_messages_has_validation_failed(self):
        """Test LOG_MESSAGES contains VALIDATION_FAILED entry."""
        assert LogCode.VALIDATION_FAILED in LOG_MESSAGES

        message_config = LOG_MESSAGES[LogCode.VALIDATION_FAILED]
        assert 'message' in message_config
        assert 'level' in message_config
        assert message_config['level'] == Context.DANGER

    def test_log_messages_has_no_files_found(self):
        """Test LOG_MESSAGES contains NO_FILES_FOUND entry."""
        assert LogCode.NO_FILES_FOUND in LOG_MESSAGES

        message_config = LOG_MESSAGES[LogCode.NO_FILES_FOUND]
        assert 'message' in message_config
        assert 'level' in message_config

    def test_all_log_codes_have_messages(self):
        """Test all LogCode values have corresponding messages."""
        for log_code in LogCode:
            assert log_code in LOG_MESSAGES, f'LogCode {log_code} missing from LOG_MESSAGES'

    def test_message_config_structure(self):
        """Test each message config has required fields."""
        for log_code, config in LOG_MESSAGES.items():
            assert isinstance(config, dict), f'Config for {log_code} is not a dict'
            assert 'message' in config, f"Config for {log_code} missing 'message'"
            assert 'level' in config, f"Config for {log_code} missing 'level'"
            assert isinstance(config['message'], str), f'Message for {log_code} is not a string'
