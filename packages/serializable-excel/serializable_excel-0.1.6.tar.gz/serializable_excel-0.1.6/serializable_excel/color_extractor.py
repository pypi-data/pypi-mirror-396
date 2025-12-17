"""
Color extraction logic for Excel export.
"""

from typing import Any, Dict, List, Optional, Tuple

from serializable_excel.colors import CellStyle
from serializable_excel.descriptors import Column, DynamicColumn


class ColorExtractor:
    """
    Handles extraction of cell colors for Excel export.
    Implements Single Responsibility Principle.
    """

    @staticmethod
    def extract_cell_color(
        getter_func: Any,
        cell_value: Any,
        row_data: Dict[str, Any],
        column_name: str,
        row_index: int,
    ) -> Optional[CellStyle]:
        """
        Extract cell color using the getter function.

        Args:
            getter_func: Function to determine cell style
            cell_value: Value of the current cell
            row_data: Dictionary with all values in the row {header: value}
            column_name: Header name of the current column
            row_index: Row index (0-based, data rows only)

        Returns:
            CellStyle or None
        """
        if getter_func is None:
            return None

        try:
            return getter_func(cell_value, row_data, column_name, row_index)
        except Exception:
            # If color extraction fails, return None (no styling)
            return None

    @staticmethod
    def build_cell_colors(
        data_rows: List[Dict[str, Any]],
        column_fields: Dict[str, Column],
        dynamic_field: Optional[DynamicColumn],
        all_dynamic_keys: set,
        headers: Dict[str, int],
    ) -> Dict[Tuple[int, int], CellStyle]:
        """
        Build a dictionary of cell colors for all cells.

        Args:
            data_rows: List of row data dictionaries {header: value}
            column_fields: Dictionary of field names to Column descriptors
            dynamic_field: DynamicColumn descriptor or None
            all_dynamic_keys: Set of all dynamic column keys
            headers: Dictionary mapping header names to column indices

        Returns:
            Dictionary mapping (row, col) tuples to CellStyle objects
        """
        cell_colors: Dict[Tuple[int, int], CellStyle] = {}

        for row_index, row_data in enumerate(data_rows):
            excel_row = row_index + 2  # Excel rows start at 1, header is row 1

            # Process static columns
            for field_name, column in column_fields.items():
                if column.getter_cell_color is None:
                    continue

                col_idx = headers.get(column.header)
                if col_idx is None:
                    continue

                cell_value = row_data.get(column.header)
                style = ColorExtractor.extract_cell_color(
                    column.getter_cell_color,
                    cell_value,
                    row_data,
                    column.header,
                    row_index,
                )
                if style is not None:
                    cell_colors[(excel_row, col_idx)] = style

            # Process dynamic columns
            if dynamic_field is not None:
                for key in all_dynamic_keys:
                    color_getter = dynamic_field.get_cell_color_getter(key)
                    if color_getter is None:
                        continue

                    col_idx = headers.get(key)
                    if col_idx is None:
                        continue

                    cell_value = row_data.get(key)
                    style = ColorExtractor.extract_cell_color(
                        color_getter,
                        cell_value,
                        row_data,
                        key,
                        row_index,
                    )
                    if style is not None:
                        cell_colors[(excel_row, col_idx)] = style

        return cell_colors
