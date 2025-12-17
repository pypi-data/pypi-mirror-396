from typing import Dict, List

from synapse_sdk.clients.validators.collections import FileSpecificationValidator

from ..base import ValidationResult, ValidationStrategy


class DefaultValidationStrategy(ValidationStrategy):
    """Default validation strategy for upload operations."""

    def validate_params(self, params: Dict) -> ValidationResult:
        """Validate action parameters."""
        errors = []

        # Check required parameters (common to all modes)
        required_params = ['storage', 'data_collection', 'name']
        for param in required_params:
            if param not in params:
                errors.append(f'Missing required parameter: {param}')

        # Check mode-specific requirements
        use_single_path = params.get('use_single_path', True)

        if use_single_path:
            # Single-path mode: 'path' is required
            if 'path' not in params:
                errors.append("Missing required parameter 'path' in single-path mode")
        else:
            # Multi-path mode: 'assets' is required
            if 'assets' not in params:
                errors.append("Missing required parameter 'assets' in multi-path mode")

        # Check parameter types
        if 'storage' in params and not isinstance(params['storage'], int):
            errors.append("Parameter 'storage' must be an integer")

        if 'data_collection' in params and not isinstance(params['data_collection'], int):
            errors.append("Parameter 'data_collection' must be an integer")

        if 'is_recursive' in params and not isinstance(params['is_recursive'], bool):
            errors.append("Parameter 'is_recursive' must be a boolean")

        if 'use_single_path' in params and not isinstance(params['use_single_path'], bool):
            errors.append("Parameter 'use_single_path' must be a boolean")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def validate_files(self, files: List[Dict], specs: Dict) -> ValidationResult:
        """Validate organized files against specifications."""
        try:
            validator = FileSpecificationValidator(specs, files)
            is_valid = validator.validate()

            if is_valid:
                return ValidationResult(valid=True)
            else:
                return ValidationResult(valid=False, errors=['File specification validation failed'])

        except Exception as e:
            return ValidationResult(valid=False, errors=[f'Validation error: {str(e)}'])
