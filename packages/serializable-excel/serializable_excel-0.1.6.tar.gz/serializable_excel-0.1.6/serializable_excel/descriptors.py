"""
Descriptors for defining columns in ExcelModel classes.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from serializable_excel.excel_types import ExcelType


class BaseDescriptor:
    """Base class for column descriptors to reduce code duplication."""

    def __init__(self):
        self.name: Optional[str] = None  # Will be set by the model class

    def __set_name__(self, owner, name: str):
        """Store the field name when the descriptor is assigned to a class."""
        self.name = name

    def __get__(self, instance, owner):
        """Get the value from the instance."""
        if instance is None:
            return self
        return instance.__dict__.get(self.name, self._get_default())

    def __set__(self, instance, value):
        """Set the value on the instance."""
        instance.__dict__[self.name] = value

    def _get_default(self) -> Any:
        """Return default value for the descriptor."""
        return None


class Column(BaseDescriptor):
    """
    Descriptor for defining static columns in ExcelModel classes.

    Args:
        header: Excel column header name (required)
        validator: Function to validate/transform value when reading from Excel.
                   Should accept the value and return the validated/transformed value.
        getter: Function to extract value from model when writing to Excel.
                Should accept the model instance and return the value.
        getter_cell_color: Function to determine cell style when writing to Excel.
                          Signature: (cell_value, row_data, column_name, row_index) -> Optional[CellStyle]
                          - cell_value: Value of the current cell
                          - row_data: Dict[str, Any] with all values in the row {header: value}
                          - column_name: Header name of the current column
                          - row_index: Row index (0-based, data rows only)
                          Returns CellStyle or None (no styling).
        excel_type: ExcelType instance to control cell formatting in Excel.
                   If not specified, type is inferred from Python type annotation.
                   Examples: ExcelDate("%d.%m.%Y"), ExcelNumber(decimal_places=2), ExcelCurrency()
        default: Default value if cell is empty
        required: Raise error if value is missing
    """

    def __init__(
        self,
        header: str,
        validator: Optional[Callable[[Any], Any]] = None,
        getter: Optional[Callable[[Any], Any]] = None,
        getter_cell_color: Optional[Callable[..., Any]] = None,
        excel_type: Optional['ExcelType'] = None,
        default: Any = None,
        required: bool = False,
    ):
        super().__init__()
        self.header = header
        self.validator = validator
        self.getter = getter
        self.getter_cell_color = getter_cell_color
        self.excel_type = excel_type
        self.default = default
        self.required = required

    def _get_default(self) -> Any:
        """Return default value for the column."""
        return self.default


class DynamicColumn(BaseDescriptor):
    """
    Descriptor for defining dynamic columns that are detected at runtime in Excel files.

    Args:
        getter: Function to extract dynamic values when exporting to Excel.
                Should accept the model instance and return a dict[str, Any]
                where keys are column names and values are the corresponding cell values.
        validator: Function to validate all dynamic columns.
                  Receives (column_name: str, value: str) and returns validated value.
        validators: Dictionary mapping column names to validator functions.
                   Each validator receives (column_name: str, value: str) and returns validated value.
        getter_cell_color: Function to determine cell style for all dynamic columns.
                          Signature: (cell_value, row_data, column_name, row_index) -> Optional[CellStyle]
        getters_cell_color: Dictionary mapping column names to style getter functions.
                           Each function has same signature as getter_cell_color.
        type_getter: Function to determine Excel type for dynamic columns.
                    Signature: (column_name: str) -> Optional[ExcelType]
                    Returns ExcelType instance or None (defaults to ExcelText).
    """

    def __init__(
        self,
        getter: Optional[Callable[[Any], Dict[str, Any]]] = None,
        validator: Optional[Callable[[str, Any], Any]] = None,
        validators: Optional[Dict[str, Callable[[str, Any], Any]]] = None,
        getter_cell_color: Optional[Callable[..., Any]] = None,
        getters_cell_color: Optional[Dict[str, Callable[..., Any]]] = None,
        type_getter: Optional[Callable[[str], Optional['ExcelType']]] = None,
    ):
        super().__init__()
        if validator is not None and validators is not None:
            raise ValueError('Cannot specify both validator and validators')
        if getter_cell_color is not None and getters_cell_color is not None:
            raise ValueError(
                'Cannot specify both getter_cell_color and getters_cell_color'
            )
        self.getter = getter
        self.validator = validator
        self.validators = validators or {}
        self.getter_cell_color = getter_cell_color
        self.getters_cell_color = getters_cell_color or {}
        self.type_getter = type_getter

    def _get_default(self) -> Dict[str, Any]:
        """Return default value (empty dict) for dynamic columns."""
        return {}

    def validate_value(self, column_name: str, value: Any) -> Any:
        """
        Validate a dynamic column value using the appropriate validator.

        Args:
            column_name: Name of the dynamic column
            value: Value to validate

        Returns:
            Validated value
        """
        # First check for column-specific validator
        if column_name in self.validators:
            return self.validators[column_name](column_name, value)
        # Then check for general validator
        if self.validator is not None:
            return self.validator(column_name, value)
        # No validator, return as-is
        return value

    def get_cell_color_getter(self, column_name: str) -> Optional[Callable]:
        """
        Get the cell color getter for a specific dynamic column.

        Args:
            column_name: Name of the dynamic column

        Returns:
            Color getter function or None
        """
        # First check for column-specific getter
        if column_name in self.getters_cell_color:
            return self.getters_cell_color[column_name]
        # Then check for general getter
        return self.getter_cell_color

    def get_excel_type(self, column_name: str) -> Optional['ExcelType']:
        """
        Get the Excel type for a specific dynamic column.

        Args:
            column_name: Name of the dynamic column

        Returns:
            ExcelType instance or None (defaults to ExcelText)
        """
        if self.type_getter is not None:
            return self.type_getter(column_name)
        return None
