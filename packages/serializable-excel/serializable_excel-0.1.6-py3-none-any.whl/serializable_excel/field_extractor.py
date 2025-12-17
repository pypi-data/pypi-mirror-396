"""
Field extraction logic for Excel export.
"""

from typing import Any, Dict

from serializable_excel.descriptors import Column, DynamicColumn


class FieldExtractor:
    """Handles extraction of field values for Excel export according to SOLID principles."""

    @staticmethod
    def extract_static_field_value(
        instance: Any,
        field_name: str,
        column: Column,
    ) -> Any:
        """
        Extract value from a static field for Excel export.

        Args:
            instance: Model instance
            field_name: Name of the field
            column: Column descriptor with getter function

        Returns:
            Extracted value

        Raises:
            ValueError: If getter fails
        """
        if column.getter is not None:
            try:
                return column.getter(instance)
            except Exception as e:
                raise ValueError(
                    f"Error calling getter for field '{field_name}': {e}"
                ) from e
        return getattr(instance, field_name, column.default)

    @staticmethod
    def extract_dynamic_field_value(
        instance: Any,
        dynamic_field: DynamicColumn,
        all_dynamic_keys: set,
    ) -> Dict[str, Any]:
        """
        Extract dynamic field values for Excel export.

        Args:
            instance: Model instance
            dynamic_field: DynamicColumn descriptor
            all_dynamic_keys: Set of all dynamic keys to include

        Returns:
            Dictionary mapping keys to values
        """
        if dynamic_field.getter is not None:
            try:
                dynamic_data = dynamic_field.getter(instance)
            except Exception as e:
                raise ValueError(
                    f"Error calling getter for dynamic field '{dynamic_field.name}': {e}"
                ) from e
        else:
            dynamic_data = getattr(instance, dynamic_field.name, {})

        if dynamic_data is None:
            dynamic_data = {}
        if not isinstance(dynamic_data, dict):
            return {}

        result = {}
        for key in sorted(all_dynamic_keys):
            result[key] = dynamic_data.get(key)
        return result
