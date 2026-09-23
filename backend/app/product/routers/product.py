from typing import Annotated

from fastapi import APIRouter, Depends, Form, UploadFile, File

from app.db.config import SessionDep
from app.product.schema import ProductCreate, ProductOut
from app.product.services import create_product, fetch_all_products
from app.accounts.models import User
from app.accounts.dependencies import require_admin

router = APIRouter()


@router.post("/create-product", response_model=ProductOut)
async def product_create(
    session: SessionDep,
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    categories: list[int] = Form(...),
    image: Annotated[UploadFile | None, File()] = None,
    user: User = Depends(require_admin),
) -> ProductOut:
    data = ProductCreate(
        title=title,
        description=description,
        price=price,
        stock=stock,
        category_ids=categories,
    )
    return await create_product(session, data, image=image)


@router.get("", response_model=list[ProductOut])
async def fetch_products(session: SessionDep, current: int = 0, number: int = 10):
    return await fetch_all_products(session, current, number)
