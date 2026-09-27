from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.product.schema import CategoryOut, CategoryCreate, ProductCreate, ProductOut
from app.product.models import Category, Product
from sqlalchemy import select, func
from app.product.utils import generate_slug, save_upload_file
from sqlalchemy.orm import selectinload


async def category_create(
    session: AsyncSession, category: CategoryCreate
) -> CategoryOut:
    category = Category(name=category.name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def fetch_all_categories(session: AsyncSession) -> list[CategoryOut]:
    categories = await session.scalars(select(Category))
    return categories.all()


async def remove_category(session: AsyncSession, category_id: int) -> bool:
    session.get(Category, category_id)
    category = await session.get(Category, category_id)
    if not category:
        return False
    await session.delete(category)
    await session.commit()
    return True


#### Products ####


async def create_product(
    session: AsyncSession, data: ProductCreate, image: UploadFile | None = None
) -> ProductOut:
    if data.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock quantity can not be less then 0",
        )
    image_path = ""
    if image is not None:
        image_path = await save_upload_file(upload_file=image, sub_dir="images")
    if data.category_ids:
        category_stmt = select(Category).where(Category.id.in_(data.category_ids))
        category_result = await session.execute(category_stmt)
        categories = category_result.scalars().all()
    product_dict = data.model_dump(exclude={"category_ids"})
    if not product_dict.get("slug"):
        product_dict["slug"] = generate_slug(product_dict.get("title"))
    new_product = Product(**product_dict, categories=categories, image_url=image_path)
    session.add(new_product)
    await session.commit()
    return new_product


async def fetch_all_products(
    session: AsyncSession,
    category_name: list[str] | None = None,
    limit: int = 5,
    page: int = 1,
) -> dict:
    stmt = select(Product).options(selectinload(Product.categories))
    if category_name:
        stmt.join(Product.categories).where(Category.name.in_(category_name)).distinct()
    count_stmt = stmt.with_only_columns(func.count(Product.id)).order_by(None)
    total = await session.scalar(count_stmt)
    stmt = stmt.limit(limit).offset((page - 1) * limit)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return {"total": total, "page": page, "limit": limit, "items": products}


async def fetch_product_by_slug(session: AsyncSession, slug: str) -> ProductOut | None:
    stmt = (
        select(Product)
        .options(selectinload(Product.categories))
        .where(Product.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar()
