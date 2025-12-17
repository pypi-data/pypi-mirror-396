from datetime import datetime
from unittest.mock import Mock

from synapse_sdk.plugins.categories.upload.actions.upload.context import StepResult, UploadContext


class TestStepResult:
    """Test StepResult class."""

    def test_success_result_creation(self):
        """Test creating a successful step result."""
        result = StepResult(success=True, data={'key': 'value'})

        assert result.success is True
        assert result.data == {'key': 'value'}
        assert result.error is None
        assert isinstance(result.timestamp, datetime)
        assert bool(result) is True

    def test_error_result_creation(self):
        """Test creating an error step result."""
        result = StepResult(success=False, error='Test error')

        assert result.success is False
        assert result.error == 'Test error'
        assert bool(result) is False

    def test_result_with_rollback_data(self):
        """Test step result with rollback data."""
        rollback_data = {'temp_file': '/tmp/test'}
        result = StepResult(success=True, rollback_data=rollback_data)

        assert result.rollback_data == rollback_data


class TestUploadContext:
    """Test UploadContext class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_run = Mock()
        self.mock_client = Mock()
        self.params = {'name': 'Test Upload', 'path': '/test/path', 'storage': 1, 'data_collection': 1}
        self.context = UploadContext(self.params, self.mock_run, self.mock_client)

    def test_context_initialization(self):
        """Test context initialization."""
        assert self.context.params == self.params
        assert self.context.run == self.mock_run
        assert self.context.client == self.mock_client

        # Check initial state
        assert self.context.storage is None
        assert self.context.pathlib_cwd is None
        assert self.context.metadata == {}
        assert self.context.file_specifications == {}
        assert self.context.organized_files == []
        assert self.context.uploaded_files == []
        assert self.context.data_units == []
        assert self.context.metrics == {}
        assert self.context.errors == []

    def test_update_with_success_result(self):
        """Test updating context with successful step result."""
        result = StepResult(
            success=True, data={'organized_files': [{'file': 'test.txt'}]}, rollback_data={'step_name': 'organize'}
        )

        self.context.update(result)

        assert len(self.context.step_results) == 1
        assert self.context.step_results[0] == result
        assert self.context.organized_files == [{'file': 'test.txt'}]
        assert self.context.rollback_data == {'step_name': 'organize'}

    def test_update_with_error_result(self):
        """Test updating context with error step result."""
        result = StepResult(success=False, error='Test error')

        self.context.update(result)

        assert len(self.context.step_results) == 1
        assert len(self.context.errors) == 1
        assert self.context.errors[0] == 'Test error'

    def test_get_result(self):
        """Test getting final result."""
        self.context.uploaded_files = [{'id': '1'}, {'id': '2'}]
        self.context.data_units = [{'id': 'unit1'}]

        result = self.context.get_result()

        assert result['uploaded_files_count'] == 2
        assert result['generated_data_units_count'] == 1
        assert result['success'] is True
        assert result['errors'] == []

    def test_get_result_with_errors(self):
        """Test getting result when context has errors."""
        self.context.errors = ['Error 1', 'Error 2']

        result = self.context.get_result()

        assert result['success'] is False
        assert result['errors'] == ['Error 1', 'Error 2']

    def test_has_errors(self):
        """Test error checking."""
        assert self.context.has_errors() is False

        self.context.errors.append('Test error')
        assert self.context.has_errors() is True

    def test_get_last_step_result(self):
        """Test getting last step result."""
        assert self.context.get_last_step_result() is None

        result1 = StepResult(success=True)
        result2 = StepResult(success=False, error='Error')

        self.context.update(result1)
        self.context.update(result2)

        assert self.context.get_last_step_result() == result2

    def test_get_param(self):
        """Test parameter retrieval."""
        assert self.context.get_param('name') == 'Test Upload'
        assert self.context.get_param('nonexistent', 'default') == 'default'

    def test_add_methods(self):
        """Test add methods for various collections."""
        # Test add_organized_files
        files = [{'file': 'test1.txt'}, {'file': 'test2.txt'}]
        self.context.add_organized_files(files)
        assert self.context.organized_files == files

        # Test add_uploaded_files
        uploaded = [{'id': 'file1'}]
        self.context.add_uploaded_files(uploaded)
        assert self.context.uploaded_files == uploaded

        # Test add_data_units
        units = [{'id': 'unit1'}]
        self.context.add_data_units(units)
        assert self.context.data_units == units

    def test_update_metrics(self):
        """Test metrics updating."""
        self.context.update_metrics('upload', {'success': 5, 'failed': 1})
        self.context.update_metrics('upload', {'total': 6})

        assert self.context.metrics['upload'] == {'success': 5, 'failed': 1, 'total': 6}

    def test_clear_errors(self):
        """Test clearing errors."""
        self.context.errors = ['Error 1', 'Error 2']
        self.context.clear_errors()
        assert self.context.errors == []

    def test_add_error(self):
        """Test adding error."""
        self.context.add_error('New error')
        assert 'New error' in self.context.errors
