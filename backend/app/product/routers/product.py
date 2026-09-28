from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    UploadFile,
    File,
    status,
)

from app.db.config import SessionDep
from app.product.schema import PaginatedProductOut, ProductCreate, ProductOut
from app.product.services import (
    create_product,
    fetch_all_products,
    fetch_product_by_slug,
    search_product,
)
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


@router.get("", response_model=PaginatedProductOut)
async def fetch_products(
    session: SessionDep,
    categories: list[str] | None = Query(default=None),
    limit: int = Query(default=5, gt=1, le=100),
    page: int = Query(default=1, ge=1),
):
    return await fetch_all_products(session, categories, limit, page)


@router.get("/search", response_model=PaginatedProductOut)
async def search(
    session: SessionDep,
    categories: list[str] | None = Query(default=None),
    title: str | None = Query(default=None),
    description: Annotated[str, Query()] | None = None,
    min_price: Annotated[float, Query()] | None = None,
    max_price: Annotated[float, Query()] | None = None,
    limit: int | None = Query(default=5, gt=1),
    page: int | None = Query(default=1, gte=1),
) -> PaginatedProductOut:
    return await search_product(
        session, categories, title, description, min_price, max_price, limit, page
    )


@router.get("/{slug}", response_model=ProductOut)
async def get_product(session: SessionDep, slug: str) -> ProductOut:
    product = await fetch_product_by_slug(session, slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product
