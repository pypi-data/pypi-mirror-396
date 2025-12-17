from synapse_sdk.plugins.categories.upload.actions.upload import ExcelParsingError, ExcelSecurityError


class TestExcelSecurityError:
    """Test ExcelSecurityError exception class."""

    def test_excel_security_error_creation(self):
        """Test creating ExcelSecurityError instance."""
        error = ExcelSecurityError('Security violation')
        assert str(error) == 'Security violation'

    def test_excel_security_error_default_message(self):
        """Test ExcelSecurityError with no message."""
        error = ExcelSecurityError()
        assert str(error) == ''

    def test_excel_security_error_inheritance(self):
        """Test ExcelSecurityError inherits from Exception."""
        error = ExcelSecurityError('Test')
        assert isinstance(error, Exception)


class TestExcelParsingError:
    """Test ExcelParsingError exception class."""

    def test_excel_parsing_error_creation(self):
        """Test creating ExcelParsingError instance."""
        error = ExcelParsingError('Parsing failed')
        assert str(error) == 'Parsing failed'

    def test_excel_parsing_error_default_message(self):
        """Test ExcelParsingError with no message."""
        error = ExcelParsingError()
        assert str(error) == ''

    def test_excel_parsing_error_inheritance(self):
        """Test ExcelParsingError inherits from Exception."""
        error = ExcelParsingError('Test')
        assert isinstance(error, Exception)
