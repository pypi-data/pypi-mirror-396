"""
Validation logic for Excel data processing.
"""

from typing import Any

from serializable_excel.descriptors import Column, DynamicColumn
from serializable_excel.exceptions import ValidationError


class FieldValidator:
    """Handles validation of field values according to SOLID principles."""

    @staticmethod
    def validate_static_field(
        field_name: str,
        header: str,
        value: Any,
        column: Column,
        row_idx: int,
    ) -> Any:
        """
        Validate a static field value.

        Args:
            field_name: Name of the field in the model
            header: Excel column header name
            value: Raw value from Excel
            column: Column descriptor with validation rules
            row_idx: Current row index for error messages

        Returns:
            Validated and transformed value

        Raises:
            ValidationError: If validation fails
        """
        # Handle missing values
        if value is None:
            if column.required:
                raise ValidationError(
                    f"Row {row_idx}: Required field '{field_name}' (header: '{header}') is missing"
                )
            return column.default

        # Apply validator if present
        if column.validator is not None:
            try:
                return column.validator(value)
            except Exception as e:
                raise ValidationError(
                    f"Row {row_idx}: Validation failed for field '{field_name}': {e}"
                ) from e

        return value

    @staticmethod
    def validate_dynamic_field(
        header: str,
        value: Any,
        dynamic_field: DynamicColumn,
        row_idx: int,
    ) -> Any:
        """
        Validate a dynamic field value.

        Args:
            header: Excel column header name
            value: Raw value from Excel
            dynamic_field: DynamicColumn descriptor with validation rules
            row_idx: Current row index for error messages

        Returns:
            Validated and transformed value

        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            return None

        try:
            return dynamic_field.validate_value(header, value)
        except Exception as e:
            raise ValidationError(
                f"Row {row_idx}: Validation failed for dynamic column '{header}': {e}"
            ) from e
