import logging
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models.product import Product
from app.models.product_image import ProductImage
from app.repositories import product_images as repo
from app.services.products import get_product


logger = logging.getLogger(__name__)
IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _valid_signature(content_type: str, data: bytes) -> bool:
    if content_type == "image/jpeg":
        return data.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    return data.startswith(b"RIFF") and data[8:12] == b"WEBP"


def upload_product_image(db: Session, product_id: int, file: UploadFile) -> Product:
    product = get_product(db, product_id)
    content_type = file.content_type or ""
    if content_type not in IMAGE_TYPES:
        raise AppError("Unsupported image type", 400)

    limit = get_settings().max_image_size_bytes
    chunks: list[bytes] = []
    size = 0
    while chunk := file.file.read(64 * 1024):
        size += len(chunk)
        if size > limit:
            raise AppError("Image too large", 400)
        chunks.append(chunk)
    image_data = b"".join(chunks)
    if not _valid_signature(content_type, image_data):
        raise AppError("Invalid image file", 400)

    try:
        return repo.save(
            db, product, file_name=f"{uuid4().hex}{IMAGE_TYPES[content_type]}",
            content_type=content_type, image_data=image_data,
        )
    except Exception as exc:
        logger.exception("Product image database update failed")
        raise AppError("Unable to upload product image", 500) from exc


def get_product_image(db: Session, product_id: int) -> ProductImage:
    product = get_product(db, product_id)
    if product.image is None:
        raise AppError("Product image not found", 404)
    return product.image


def delete_product_image(db: Session, product_id: int) -> Product:
    product = get_product(db, product_id)
    try:
        return repo.delete(db, product)
    except Exception as exc:
        logger.exception("Product image database deletion failed")
        raise AppError("Unable to delete product image", 500) from exc
