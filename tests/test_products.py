from decimal import Decimal

from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import categories, products
from tests.helpers import expect_error, database_session


def test_product_crud_filter_and_category_validation() -> None:
    with database_session() as db:
        category = categories.create_category(db, CategoryCreate(name="Coffee"))
        product = products.create_product(db, ProductCreate(name="Iced Latte", price=Decimal("2.50"), category_id=category.id))
        assert products.get_product(db, product.id).price == Decimal("2.50")
        assert len(products.list_products(db, category.id, True, "latte")) == 1
        product = products.update_product(db, product.id, ProductUpdate(name="Hot Latte", price=Decimal("3.00"), category_id=category.id))
        assert product.name == "Hot Latte"
        products.delete_product(db, product.id)
        assert not product.available
        categories.delete_category(db, category.id)
        expect_error(lambda: products.create_product(db, ProductCreate(name="Mocha", price=Decimal("3.00"), category_id=category.id)), 404)
