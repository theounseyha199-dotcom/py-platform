from decimal import Decimal
from io import BytesIO

from fastapi import UploadFile
from pydantic import ValidationError
from starlette.datastructures import Headers

from app.api.v1 import products as product_api
from app.core.security import get_current_user, require_staff
from app.models.product_image import ProductImage
from app.schemas.product import ProductCreate
from app.services import product_images
from tests.helpers import database_session, expect_error, product, user


JPEG = b"\xff\xd8\xffjpeg-data"
PNG = b"\x89PNG\r\n\x1a\npng-data"
WEBP = b"RIFF\x10\x00\x00\x00WEBPwebp-data"


def upload_file(data: bytes, mime: str, filename: str = "../../unsafe") -> UploadFile:
    return UploadFile(file=BytesIO(data), filename=filename, headers=Headers({"content-type": mime}))


def test_upload_supported_images_and_get_bytes() -> None:
    for mime, data, extension in (("image/jpeg", JPEG, ".jpg"), ("image/png", PNG, ".png"), ("image/webp", WEBP, ".webp")):
        with database_session() as db:
            item = product(db)
            result = product_images.upload_product_image(db, item.id, upload_file(data, mime))
            assert result.image_url == f"/api/v1/products/{item.id}/image"
            image = product_images.get_product_image(db, item.id)
            assert image.image_data == data
            assert image.content_type == mime
            assert image.file_size == len(data)
            assert image.file_name.endswith(extension)
            assert "/" not in image.file_name
            response = product_api.get_image(item.id, db)
            assert response.body == data
            assert response.media_type == mime


def test_reject_unsupported_spoofed_and_oversized_images() -> None:
    with database_session() as db:
        item = product(db)
        expect_error(lambda: product_images.upload_product_image(db, item.id, upload_file(b"plain", "text/plain")), 400)
        expect_error(lambda: product_images.upload_product_image(db, item.id, upload_file(b"plain", "image/png")), 400)
        expect_error(lambda: product_images.upload_product_image(db, item.id, upload_file(JPEG + b"x" * 5_000_000, "image/jpeg")), 400)
        assert db.query(ProductImage).count() == 0
        assert item.image_url is None


def test_nonexistent_product_and_missing_image() -> None:
    with database_session() as db:
        item = product(db)
        expect_error(lambda: product_images.upload_product_image(db, 999, upload_file(JPEG, "image/jpeg")), 404)
        expect_error(lambda: product_images.get_product_image(db, 999), 404)
        expect_error(lambda: product_images.get_product_image(db, item.id), 404)


def test_replace_and_delete_image() -> None:
    with database_session() as db:
        item = product(db)
        product_images.upload_product_image(db, item.id, upload_file(JPEG, "image/jpeg"))
        old_id = item.image.id
        product_images.upload_product_image(db, item.id, upload_file(PNG, "image/png"))
        assert item.image.id == old_id
        assert item.image.image_data == PNG
        assert db.query(ProductImage).count() == 1
        product_images.delete_product_image(db, item.id)
        assert item.image_url is None
        assert db.query(ProductImage).count() == 0
        product_images.delete_product_image(db, item.id)
        assert item.image_url is None


def test_authorization_and_product_response() -> None:
    from app.main import app

    route = app.openapi()["paths"]["/api/v1/products/{product_id}/image"]
    assert route["post"]["security"]
    assert route["delete"]["security"]
    assert not route["get"].get("security")
    with database_session() as db:
        customer = user(db)
        expect_error(lambda: require_staff(customer), 403)
        expect_error(lambda: get_current_user("invalid", db), 401)
        staff = user(db, "staff@example.com", role="STAFF")
        assert require_staff(staff).id == staff.id
        item = product(db)
        result = product_api.upload_image(item.id, upload_file(JPEG, "image/jpeg"), db)
        assert result["data"]["image_url"] == f"/api/v1/products/{item.id}/image"
        assert "image_data" not in result["data"]
        assert product_api.get_one(item.id, db)["data"]["image_url"] == result["data"]["image_url"]
        assert product_api.delete_image(item.id, db)["message"] == "Product image deleted successfully"


def test_product_create_does_not_accept_image_url() -> None:
    try:
        ProductCreate(name="Latte", price=Decimal("2.50"), category_id=1, image_url="http://example.com/a.jpg")
    except ValidationError:
        pass
    else:
        raise AssertionError("image_url was accepted in JSON creation")
