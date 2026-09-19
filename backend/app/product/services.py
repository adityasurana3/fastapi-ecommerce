from sqlalchemy.ext.asyncio import AsyncSession
from app.product.schema import CategoryOut, CategoryCreate
from app.product.models import Category
from sqlalchemy import select


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
