from sqlalchemy.ext.asyncio import AsyncSession
from app.product.schema import CategoryOut, CategoryCreate
from app.product.models import Category


async def category_create(
    session: AsyncSession, category: CategoryCreate
) -> CategoryOut:
    category = Category(name=category.name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category
