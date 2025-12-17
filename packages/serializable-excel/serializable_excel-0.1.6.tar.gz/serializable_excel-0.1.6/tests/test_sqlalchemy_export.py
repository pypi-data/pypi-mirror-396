"""
Tests for exporting SQLAlchemy models to Excel using SerializableExcel.
"""

from decimal import Decimal
from io import BytesIO

import pytest
from faker import Faker
from sqlalchemy.orm import Session

from serializable_excel import Column, ExcelModel
from tests.models import Order, OrderItem, Product, User

fake = Faker()


class UserExportModel(ExcelModel):
    """Excel export model for User SQLAlchemy model."""

    id: int = Column(header="ID")
    name: str = Column(header="Name")
    email: str = Column(header="Email")
    age: int = Column(header="Age")
    created_at: str = Column(header="Created At", getter=lambda u: str(u.created_at))


class ProductExportModel(ExcelModel):
    """Excel export model for Product SQLAlchemy model."""

    id: int = Column(header="ID")
    sku: str = Column(header="SKU")
    name: str = Column(header="Product Name")
    description: str = Column(header="Description", getter=lambda p: p.description or "")
    price: str = Column(header="Price", getter=lambda p: str(p.price))
    stock_quantity: int = Column(header="Stock Quantity")


class OrderExportModel(ExcelModel):
    """Excel export model for Order SQLAlchemy model."""

    id: int = Column(header="ID")
    order_number: str = Column(header="Order Number")
    user_name: str = Column(header="Customer Name", getter=lambda o: o.user.name)
    user_email: str = Column(header="Customer Email", getter=lambda o: o.user.email)
    total_amount: str = Column(header="Total Amount", getter=lambda o: str(o.total_amount))
    status: str = Column(header="Status")
    created_at: str = Column(header="Created At", getter=lambda o: str(o.created_at))


def generate_users(session: Session, count: int = 10) -> list[User]:
    """Generate fake users using Faker."""
    users = []
    for _ in range(count):
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            age=fake.random_int(min=18, max=80),
        )
        session.add(user)
        users.append(user)
    session.commit()
    return users


def generate_products(session: Session, count: int = 20) -> list[Product]:
    """Generate fake products using Faker."""
    products = []
    for _ in range(count):
        product = Product(
            sku=fake.unique.bothify(text="SKU-####-???").upper(),
            name=fake.catch_phrase(),
            description=fake.text(max_nb_chars=200),
            price=Decimal(fake.pyfloat(left_digits=3, right_digits=2, positive=True, min_value=10)),
            stock_quantity=fake.random_int(min=0, max=1000),
        )
        session.add(product)
        products.append(product)
    session.commit()
    return products


def generate_orders(
    session: Session,
    users: list[User],
    products: list[Product],
    count: int = 15,
) -> list[Order]:
    """Generate fake orders using Faker."""
    orders = []
    for _ in range(count):
        user = fake.random_element(elements=users)
        order = Order(
            user_id=user.id,
            order_number=fake.unique.bothify(text="ORD-####-???").upper(),
            total_amount=Decimal(
                fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=100)
            ),
            status=fake.random_element(
                elements=(
                    "pending",
                    "processing",
                    "shipped",
                    "delivered",
                    "cancelled",
                )
            ),
        )
        session.add(order)
        session.flush()  # Flush to get order.id

        # Add order items
        num_items = fake.random_int(min=1, max=5)
        selected_products = fake.random_elements(elements=products, length=num_items, unique=True)
        for product in selected_products:
            quantity = fake.random_int(min=1, max=10)
            unit_price = product.price
            item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=unit_price * quantity,
            )
            session.add(item)

        orders.append(order)
    session.commit()
    return orders


def test_export_users_to_excel_file(db_session: Session, temp_excel_file: str):
    """Test exporting users to Excel file."""
    # Generate test data
    users = generate_users(db_session, count=15)

    # Export to Excel
    UserExportModel.to_excel(users, temp_excel_file)

    # Verify file was created
    import os

    assert os.path.exists(temp_excel_file), "Excel file should be created"

    # Read back and verify
    loaded_users = UserExportModel.from_excel(temp_excel_file)
    assert len(loaded_users) == len(users), "Should load same number of users"

    # Verify first user data
    assert loaded_users[0].id == users[0].id
    assert loaded_users[0].name == users[0].name
    assert loaded_users[0].email == users[0].email


def test_export_users_to_bytes(db_session: Session):
    """Test exporting users to bytes."""
    # Generate test data
    users = generate_users(db_session, count=10)

    # Export to bytes
    excel_bytes = UserExportModel.to_excel(users, return_bytes=True)

    assert excel_bytes is not None, "Should return bytes"
    assert len(excel_bytes) > 0, "Bytes should not be empty"
    assert excel_bytes[:2] == b"PK", "Should be a valid ZIP/Excel file"

    # Read back from bytes
    loaded_users = UserExportModel.from_excel(excel_bytes)
    assert len(loaded_users) == len(users), "Should load same number of users"


def test_export_products_to_excel(db_session: Session, temp_excel_file: str):
    """Test exporting products to Excel."""
    # Generate test data
    products = generate_products(db_session, count=25)

    # Export to Excel
    ProductExportModel.to_excel(products, temp_excel_file)

    # Read back and verify
    loaded_products = ProductExportModel.from_excel(temp_excel_file)
    assert len(loaded_products) == len(products), "Should load same number of products"

    # Verify product data
    assert loaded_products[0].sku == products[0].sku
    assert loaded_products[0].name == products[0].name


def test_export_orders_with_relationships(db_session: Session, temp_excel_file: str):
    """Test exporting orders with user relationships."""
    # Generate test data
    users = generate_users(db_session, count=10)
    products = generate_products(db_session, count=20)
    orders = generate_orders(db_session, users, products, count=20)

    # Export to Excel
    OrderExportModel.to_excel(orders, temp_excel_file)

    # Read back and verify
    loaded_orders = OrderExportModel.from_excel(temp_excel_file)
    assert len(loaded_orders) == len(orders), "Should load same number of orders"

    # Verify relationship data
    assert loaded_orders[0].user_name == orders[0].user.name
    assert loaded_orders[0].user_email == orders[0].user.email


def test_export_large_dataset(db_session: Session, temp_excel_file: str):
    """Test exporting large dataset."""
    # Generate large dataset
    users = generate_users(db_session, count=100)
    products = generate_products(db_session, count=200)
    orders = generate_orders(db_session, users, products, count=150)

    # Export to Excel
    OrderExportModel.to_excel(orders, temp_excel_file)

    # Read back and verify
    loaded_orders = OrderExportModel.from_excel(temp_excel_file)
    assert len(loaded_orders) == len(orders), "Should load all orders"

    # Verify data integrity
    for loaded, original in zip(loaded_orders[:10], orders[:10]):
        assert loaded.order_number == original.order_number
        assert loaded.user_name == original.user.name


def test_export_to_bytesio(db_session: Session):
    """Test exporting to BytesIO stream."""
    # Generate test data
    users = generate_users(db_session, count=10)

    # Export to bytes
    excel_bytes = UserExportModel.to_excel(users, return_bytes=True)

    # Create BytesIO from bytes
    stream = BytesIO(excel_bytes)

    # Read from BytesIO
    loaded_users = UserExportModel.from_excel(stream)
    assert len(loaded_users) == len(users), "Should load from BytesIO correctly"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
