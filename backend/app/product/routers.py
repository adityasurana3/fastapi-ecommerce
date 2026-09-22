from typing import Annotated

from fastapi import APIRouter, Depends, Form, status, UploadFile, File

from app.db.config import SessionDep
from app.product.schema import CategoryOut, CategoryCreate, ProductCreate, ProductOut
from app.product.services import (
    category_create,
    create_product,
    fetch_all_categories,
    remove_category,
)
from app.accounts.models import User
from app.accounts.dependencies import require_admin
from fastapi.exceptions import HTTPException

router = APIRouter()


@router.post("/create-category", response_model=CategoryOut)
async def create_category(
    session: SessionDep, category: CategoryCreate, admin: User = Depends(require_admin)
):
    return await category_create(session, category)


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(session: SessionDep) -> list[CategoryOut]:
    return await fetch_all_categories(session)


@router.delete("/delete-category/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    session: SessionDep, category_id: int, user: User = Depends(require_admin)
):
    result = remove_category(session, category_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )


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
