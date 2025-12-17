"""
Excel file reader with separation of concerns.
"""

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from serializable_excel.descriptors import Column, DynamicColumn
from serializable_excel.excel_io import (
    load_workbook_from_source,
    read_excel_headers,
    read_excel_rows,
)
from serializable_excel.exceptions import ColumnNotFoundError, ValidationError
from serializable_excel.field_metadata import FieldMetadataExtractor
from serializable_excel.validators import FieldValidator

T = TypeVar("T")


class ExcelReader:
    """
    Handles reading Excel files and converting them to model instances.
    Implements Single Responsibility Principle.
    """

    def __init__(
        self,
        metadata_extractor: FieldMetadataExtractor,
        validator: FieldValidator,
    ):
        """
        Initialize ExcelReader with dependencies.

        Args:
            metadata_extractor: Extractor for field metadata
            validator: Validator for field values
        """
        self.metadata_extractor = metadata_extractor
        self.validator = validator

    def read(
        self,
        model_class: Type[T],
        source: Union[str, bytes, BytesIO],
        dynamic_columns: bool = False,
    ) -> List[T]:
        """
        Read models from an Excel file, bytes, or BytesIO.

        Args:
            model_class: Model class to instantiate
            source: Path to the Excel file, bytes, or BytesIO object
            dynamic_columns: Enable dynamic column detection

        Returns:
            List of model instances

        Raises:
            FileNotFoundError: If file doesn't exist (only for file paths)
            ValidationError: If validation fails
            ColumnNotFoundError: If required column is missing
        """
        # Validate file path exists (only for string paths)
        if isinstance(source, str):
            file_path_obj = Path(source)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"Excel file not found: {source}")

        wb = load_workbook_from_source(source, read_only=True, data_only=True)
        try:
            ws = wb.active
            headers = read_excel_headers(ws, header_row=1)
            if not headers:
                raise ValueError("No headers found in Excel file")

            column_fields = self.metadata_extractor.get_column_fields(model_class)
            dynamic_field = (
                self.metadata_extractor.get_dynamic_column_field(model_class)
                if dynamic_columns
                else None
            )

            self._validate_required_columns(column_fields, headers)
            header_to_field = self.metadata_extractor.build_header_to_field_mapping(column_fields)
            dynamic_headers = self._identify_dynamic_headers(
                headers, column_fields, dynamic_columns, dynamic_field
            )

            data_rows = read_excel_rows(ws, start_row=2)
            return self._process_rows(
                model_class,
                data_rows,
                headers,
                header_to_field,
                column_fields,
                dynamic_headers,
                dynamic_field,
            )
        finally:
            wb.close()

    def _validate_required_columns(
        self, column_fields: Dict[str, Column], headers: Dict[int, str]
    ) -> None:
        """Validate that all required columns are present."""
        header_values = set(headers.values())
        for field_name, column in column_fields.items():
            if column.required and column.header not in header_values:
                raise ColumnNotFoundError(
                    f"Required column '{column.header}' not found in Excel file"
                )

    def _identify_dynamic_headers(
        self,
        headers: Dict[int, str],
        column_fields: Dict[str, Column],
        dynamic_columns: bool,
        dynamic_field: Optional[DynamicColumn],
    ) -> Dict[int, str]:
        """Identify dynamic column headers."""
        dynamic_headers: Dict[int, str] = {}
        if dynamic_columns and dynamic_field is not None:
            static_headers = self.metadata_extractor.get_static_headers(column_fields)
            for col_idx, header in headers.items():
                if header not in static_headers:
                    dynamic_headers[col_idx] = header
        return dynamic_headers

    def _process_rows(
        self,
        model_class: Type[T],
        data_rows: List[Dict[int, Any]],
        headers: Dict[int, str],
        header_to_field: Dict[str, str],
        column_fields: Dict[str, Column],
        dynamic_headers: Dict[int, str],
        dynamic_field: Optional[DynamicColumn],
    ) -> List[T]:
        """Process data rows and create model instances."""
        instances = []
        for row_idx, row_data in enumerate(data_rows, start=2):
            try:
                instance_data = self._build_instance_data(
                    row_idx,
                    row_data,
                    headers,
                    header_to_field,
                    column_fields,
                    dynamic_headers,
                    dynamic_field,
                )
                instance = model_class(**instance_data)
                instances.append(instance)
            except Exception as e:
                if isinstance(e, (ValidationError, ColumnNotFoundError)):
                    raise
                raise ValidationError(f"Row {row_idx}: Error creating model instance: {e}") from e
        return instances

    def _build_instance_data(
        self,
        row_idx: int,
        row_data: Dict[int, Any],
        headers: Dict[int, str],
        header_to_field: Dict[str, str],
        column_fields: Dict[str, Column],
        dynamic_headers: Dict[int, str],
        dynamic_field: Optional[DynamicColumn],
    ) -> Dict[str, Any]:
        """Build data dictionary for model instance creation."""
        instance_data: Dict[str, Any] = {}

        # Process static columns
        for col_idx, header in headers.items():
            if header in header_to_field:
                field_name = header_to_field[header]
                column = column_fields[field_name]
                value = row_data.get(col_idx)
                validated_value = self.validator.validate_static_field(
                    field_name, header, value, column, row_idx
                )
                instance_data[field_name] = validated_value

        # Process dynamic columns
        if dynamic_field is not None:
            dynamic_values: Dict[str, Any] = {}
            for col_idx, header in dynamic_headers.items():
                value = row_data.get(col_idx)
                if value is not None:
                    validated_value = self.validator.validate_dynamic_field(
                        header, value, dynamic_field, row_idx
                    )
                    dynamic_values[header] = validated_value
            instance_data[dynamic_field.name] = dynamic_values

        return instance_data
