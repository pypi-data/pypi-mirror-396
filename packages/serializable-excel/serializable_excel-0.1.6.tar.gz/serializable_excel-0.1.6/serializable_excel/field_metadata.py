"""
Field metadata extraction and management.
"""

from typing import Dict, Optional

from serializable_excel.descriptors import Column, DynamicColumn


class FieldMetadataExtractor:
    """Extracts field metadata from model classes according to SOLID principles."""

    @staticmethod
    def get_column_fields(cls) -> Dict[str, Column]:
        """
        Get all Column fields from the model class.

        Args:
            cls: Model class

        Returns:
            Dictionary mapping field names to Column descriptors
        """
        columns = {}
        # Pydantic v2 stores descriptors in model_fields.default
        if hasattr(cls, "model_fields"):
            for field_name, field_info in cls.model_fields.items():
                default = getattr(field_info, "default", None)
                if isinstance(default, Column):
                    columns[field_name] = default
        # Fallback: check class __dict__ (for non-Pydantic cases)
        if not columns:
            for name, attr in cls.__dict__.items():
                if isinstance(attr, Column):
                    columns[name] = attr
        return columns

    @staticmethod
    def get_dynamic_column_field(cls) -> Optional[DynamicColumn]:
        """
        Get the DynamicColumn field from the model class, if any.

        Args:
            cls: Model class

        Returns:
            DynamicColumn descriptor or None
        """
        # Pydantic v2 stores descriptors in model_fields.default
        if hasattr(cls, "model_fields"):
            for field_name, field_info in cls.model_fields.items():
                default = getattr(field_info, "default", None)
                if isinstance(default, DynamicColumn):
                    return default
        # Fallback: check class __dict__
        for name, attr in cls.__dict__.items():
            if isinstance(attr, DynamicColumn):
                return attr
        return None

    @staticmethod
    def build_header_to_field_mapping(
        column_fields: Dict[str, Column],
    ) -> Dict[str, str]:
        """
        Build mapping from Excel headers to field names.

        Args:
            column_fields: Dictionary of field names to Column descriptors

        Returns:
            Dictionary mapping header names to field names
        """
        return {column.header: field_name for field_name, column in column_fields.items()}

    @staticmethod
    def get_static_headers(column_fields: Dict[str, Column]) -> set:
        """
        Get set of all static header names.

        Args:
            column_fields: Dictionary of field names to Column descriptors

        Returns:
            Set of header names
        """
        return {col.header for col in column_fields.values()}
