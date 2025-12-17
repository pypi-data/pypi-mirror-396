"""
Excel file writer with separation of concerns.
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from serializable_excel.color_extractor import ColorExtractor
from serializable_excel.descriptors import Column, DynamicColumn
from serializable_excel.excel_io import write_excel, write_excel_to_bytes
from serializable_excel.excel_types import ExcelType
from serializable_excel.field_extractor import FieldExtractor
from serializable_excel.field_metadata import FieldMetadataExtractor

T = TypeVar('T')


class ExcelWriter:
    """
    Handles writing model instances to Excel files.
    Implements Single Responsibility Principle.
    """

    def __init__(
        self,
        metadata_extractor: FieldMetadataExtractor,
        field_extractor: FieldExtractor,
        color_extractor: Optional[ColorExtractor] = None,
    ):
        """
        Initialize ExcelWriter with dependencies.

        Args:
            metadata_extractor: Extractor for field metadata
            field_extractor: Extractor for field values
            color_extractor: Extractor for cell colors (optional)
        """
        self.metadata_extractor = metadata_extractor
        self.field_extractor = field_extractor
        self.color_extractor = color_extractor or ColorExtractor()

    def write(
        self,
        model_class: type,
        instances: List[Any],
        file_path: Optional[str] = None,
        return_bytes: bool = False,
        column_order: Optional[
            Union[Callable[[str], Optional[int]], Dict[str, int]]
        ] = None,
    ) -> Optional[bytes]:
        """
        Export model instances to an Excel file or return as bytes.

        Args:
            model_class: Model class
            instances: List of model instances to export
            file_path: Path where to save the Excel file (required if return_bytes=False)
            return_bytes: If True, return Excel content as bytes instead of saving to file
            column_order: Optional function or dict to specify order for static columns.
                        If function: takes header name (str) and returns order number (int) or None.
                        If dict: maps header names to order numbers.

        Returns:
            bytes if return_bytes=True, None otherwise

        Raises:
            ValueError: If instances list is empty or invalid
            ValueError: If file_path is not provided when return_bytes=False
        """
        if not instances:
            raise ValueError('Cannot export empty list of instances')

        if not return_bytes and not file_path:
            raise ValueError('file_path is required when return_bytes=False')

        column_fields = self.metadata_extractor.get_column_fields(model_class)
        if not column_fields:
            raise ValueError('No Column fields defined in model')

        dynamic_field = self.metadata_extractor.get_dynamic_column_field(
            model_class
        )

        headers = self._build_headers(
            column_fields,
            dynamic_field,
            instances,
            column_order,
        )
        data_rows = self._build_data_rows(
            instances, column_fields, dynamic_field, headers
        )

        # Build cell colors
        all_dynamic_keys = (
            self._collect_dynamic_keys(instances, dynamic_field)
            if dynamic_field is not None
            else set()
        )
        cell_colors = self.color_extractor.build_cell_colors(
            data_rows=data_rows,
            column_fields=column_fields,
            dynamic_field=dynamic_field,
            all_dynamic_keys=all_dynamic_keys,
            headers=headers,
        )

        # Build column types
        column_types = self._build_column_types(
            column_fields, dynamic_field, all_dynamic_keys
        )

        if return_bytes:
            return write_excel_to_bytes(
                headers,
                data_rows,
                cell_colors=cell_colors,
                column_types=column_types,
            )
        else:
            write_excel(
                headers,
                data_rows,
                file_path,
                cell_colors=cell_colors,
                column_types=column_types,
            )
            return None

    def _build_headers(
        self,
        column_fields: Dict[str, Any],
        dynamic_field: Any,
        instances: List[Any],
        column_order: Optional[
            Union[Callable[[str], Optional[int]], Dict[str, int]]
        ] = None,
    ) -> Dict[str, int]:
        """
        Build headers mapping for Excel export with optional column ordering.

        Args:
            column_fields: Dictionary mapping field names to Column descriptors
            dynamic_field: DynamicColumn descriptor or None
            instances: List of model instances
            column_order: Optional function or dict to specify order for all columns

        Returns:
            Dictionary mapping header names to column indices (1-indexed)
        """
        # Collect static column orders
        static_orders: Dict[str, Optional[int]] = {}
        for field_name, column in column_fields.items():
            header = column.header
            if column_order is not None:
                if callable(column_order):
                    static_orders[header] = column_order(header)
                elif isinstance(column_order, dict):
                    static_orders[header] = column_order.get(header)
                else:
                    static_orders[header] = None
            else:
                static_orders[header] = None

        # Collect dynamic column orders (shared with static)
        dynamic_orders: Dict[str, int] = {}
        all_dynamic_keys: set = set()
        if dynamic_field is not None:
            all_dynamic_keys = self._collect_dynamic_keys(
                instances, dynamic_field
            )
            if column_order is not None:
                if callable(column_order):
                    for key in all_dynamic_keys:
                        order = column_order(key)
                        if order is not None:
                            dynamic_orders[key] = order
                elif isinstance(column_order, dict):
                    for key in all_dynamic_keys:
                        order = column_order.get(key)
                        if order is not None:
                            dynamic_orders[key] = order

        # Normalize all order numbers (remove gaps, make sequential)
        all_orders: Dict[str, int] = {}

        # Add static columns with orders
        for header, order in static_orders.items():
            if order is not None:
                all_orders[header] = order

        # Add dynamic columns with orders
        for header, order in dynamic_orders.items():
            all_orders[header] = order

        # Normalize orders: create mapping old_order -> new_order (sequential 1,2,3...)
        if all_orders:
            # Get unique order values and sort them
            unique_orders = sorted(set(all_orders.values()))
            # Create mapping: old_order -> new_order (sequential)
            order_mapping = {
                old_order: new_order
                for new_order, old_order in enumerate(unique_orders, start=1)
            }

            # Apply normalization
            normalized_orders: Dict[str, int] = {}
            for header, old_order in all_orders.items():
                normalized_orders[header] = order_mapping[old_order]
        else:
            normalized_orders = {}

        # Separate columns with and without orders
        # Columns with order (both static and dynamic) are mixed together
        columns_with_order: List[
            tuple[str, int, bool]
        ] = []  # (header, order, is_static)
        static_without_order: List[str] = []
        dynamic_without_order: List[str] = []

        # Process static columns
        for field_name, column in column_fields.items():
            header = column.header
            if header in normalized_orders:
                columns_with_order.append(
                    (header, normalized_orders[header], True)
                )
            else:
                static_without_order.append(header)

        # Process dynamic columns
        if dynamic_field is not None:
            all_dynamic_keys = self._collect_dynamic_keys(
                instances, dynamic_field
            )
            for key in sorted(all_dynamic_keys):
                if key in normalized_orders:
                    columns_with_order.append(
                        (key, normalized_orders[key], False)
                    )
                else:
                    dynamic_without_order.append(key)

        # Sort all columns with order by their normalized order number
        # If order numbers are equal, sort by column name (header) alphabetically
        # This allows dynamic columns to be before static if they have lower order numbers
        columns_with_order.sort(key=lambda x: (x[1], x[0]))

        # Build final headers dict
        headers: Dict[str, int] = {}
        col_idx = 1

        # Add all columns with order (mixed static and dynamic, sorted by order)
        for header, _, _ in columns_with_order:
            headers[header] = col_idx
            col_idx += 1

        # Add static columns without order (after columns with order)
        for header in static_without_order:
            headers[header] = col_idx
            col_idx += 1

        # Add dynamic columns without order (at the end)
        for header in dynamic_without_order:
            headers[header] = col_idx
            col_idx += 1

        return headers

    def _collect_dynamic_keys(
        self, instances: List[Any], dynamic_field: DynamicColumn
    ) -> set:
        """Collect all dynamic column keys from all instances."""
        all_dynamic_keys = set()
        for instance in instances:
            if dynamic_field.getter is not None:
                try:
                    dynamic_data = dynamic_field.getter(instance)
                except Exception:
                    dynamic_data = {}
            else:
                dynamic_data = getattr(instance, dynamic_field.name, {})
            if isinstance(dynamic_data, dict):
                all_dynamic_keys.update(dynamic_data.keys())
        return all_dynamic_keys

    def _build_data_rows(
        self,
        instances: List[Any],
        column_fields: Dict[str, Any],
        dynamic_field: Any,
        headers: Dict[str, int],
    ) -> List[Dict[str, Any]]:
        """Build data rows for Excel export."""
        data_rows: List[Dict[str, Any]] = []
        all_dynamic_keys = (
            self._collect_dynamic_keys(instances, dynamic_field)
            if dynamic_field is not None
            else set()
        )

        for instance in instances:
            row_data: Dict[str, Any] = {}

            # Process static columns
            for field_name, column in column_fields.items():
                value = self.field_extractor.extract_static_field_value(
                    instance, field_name, column
                )
                row_data[column.header] = value

            # Process dynamic columns
            if dynamic_field is not None:
                dynamic_values = (
                    self.field_extractor.extract_dynamic_field_value(
                        instance, dynamic_field, all_dynamic_keys
                    )
                )
                row_data.update(dynamic_values)

            data_rows.append(row_data)

        return data_rows

    def _build_column_types(
        self,
        column_fields: Dict[str, Column],
        dynamic_field: Optional[DynamicColumn],
        all_dynamic_keys: set,
    ) -> Dict[str, ExcelType]:
        """
        Build column types mapping for Excel export.

        Args:
            column_fields: Dictionary of field names to Column descriptors
            dynamic_field: DynamicColumn descriptor or None
            all_dynamic_keys: Set of all dynamic column keys

        Returns:
            Dictionary mapping header names to ExcelType objects
        """
        column_types: Dict[str, ExcelType] = {}

        # Add types for static columns
        for field_name, column in column_fields.items():
            if column.excel_type is not None:
                column_types[column.header] = column.excel_type
            # If no explicit type, we don't add it (let Excel auto-detect)

        # Add types for dynamic columns
        if dynamic_field is not None:
            for key in all_dynamic_keys:
                excel_type = dynamic_field.get_excel_type(key)
                if excel_type is not None:
                    column_types[key] = excel_type

        return column_types
