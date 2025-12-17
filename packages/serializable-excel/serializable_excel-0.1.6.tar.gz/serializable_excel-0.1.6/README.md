# SerializableExcel

[![Documentation](https://readthedocs.org/projects/serializableexcel/badge/?version=latest)](https://of1nn.github.io/serializable-excel)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A user-friendly Python library for seamless bidirectional conversion between Excel spreadsheets and Pydantic models using declarative syntax similar to SQLAlchemy.

## Quick Start

```python
from serializable_excel import ExcelModel, Column

class UserModel(ExcelModel):
    name: str = Column(header="Name")
    age: int = Column(header="Age")
    email: str = Column(header="Email")

# Read from Excel file
users = UserModel.from_excel("users.xlsx")

# Write to Excel file
UserModel.to_excel(users, "output.xlsx")

# Or work with bytes for API usage
excel_bytes = UserModel.to_excel(users, return_bytes=True)
users = UserModel.from_excel(file_bytes)
```

## Installation

```bash
pip install serializable-excel
```

Or install from source:

```bash
git clone https://github.com/of1nn/serializable-excel.git
cd serializable-excel
pip install -r requirements.txt
```

## Features

- **🔄 Bidirectional Conversion**: Seamlessly convert between Excel sheets and Pydantic models
- **📝 Declarative Syntax**: Define models using familiar SQLAlchemy-like syntax
- **🌐 API Ready**: Work with bytes/BytesIO for seamless web API integration (FastAPI, Flask, etc.)
- **🔍 Automatic Type Inference**: Smart type detection from Excel data
- **✅ Built-in Validation**: Automatic validation of data types and constraints
- **🔧 Dynamic Columns**: Support for runtime-detected columns perfect for admin-configurable fields
- **🛡️ Custom Validators**: Define validation functions for data integrity
- **📤 Custom Getters**: Extract values from complex database models when exporting
- **🎨 Cell Styling**: Conditional cell formatting with colors, fonts, and styles
- **📊 Column Ordering**: Control column order in exported Excel files with custom ordering functions

## Documentation

📚 **Full documentation is available at [of1nn.github.io/serializable-excel](https://of1nn.github.io/serializable-excel)**

The documentation includes:
- Installation guide
- Quick start tutorial
- API reference
- Advanced usage examples
- Dynamic columns guide
- Validation and getters documentation

## Requirements

- Python 3.8 or higher
- Pydantic 2.x
- openpyxl (for Excel file handling)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see our [Contributing Guide](https://of1nn.github.io/serializable-excel/contributing.html) for details.
