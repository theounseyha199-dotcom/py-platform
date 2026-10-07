from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services import categories
from tests.helpers import expect_error, database_session


def test_category_crud_and_duplicate() -> None:
    with database_session() as db:
        category = categories.create_category(db, CategoryCreate(name=" Coffee ", description="Drinks"))
        assert category.name == "Coffee"
        assert categories.get_category(db, category.id).description == "Drinks"
        assert len(categories.list_categories(db)) == 1
        expect_error(lambda: categories.create_category(db, CategoryCreate(name="coffee")), 409)
        category = categories.update_category(db, category.id, CategoryUpdate(name="Tea"))
        assert category.name == "Tea"
        categories.delete_category(db, category.id)
        assert categories.list_categories(db) == []
        expect_error(lambda: categories.get_category(db, category.id), 404)
