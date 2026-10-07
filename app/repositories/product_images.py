from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.product_image import ProductImage


def save(db: Session, product: Product, *, file_name: str, content_type: str, image_data: bytes) -> Product:
    try:
        image = product.image
        if image is None:
            image = ProductImage(product=product)
        image.file_name = file_name
        image.content_type = content_type
        image.file_size = len(image_data)
        image.image_data = image_data
        db.add(image)
        db.commit()
        return product
    except Exception:
        db.rollback()
        raise


def delete(db: Session, product: Product) -> Product:
    try:
        image = product.image
        if image is not None:
            db.delete(image)
            db.commit()
            db.expire(product, ["image"])
        return product
    except Exception:
        db.rollback()
        raise
