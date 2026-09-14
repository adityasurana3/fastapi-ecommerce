from fastapi import APIRouter

from app.db.config import SessionDep
from app.product.schema import CategoryOut, CategoryCreate
from app.product.services import category_create
from app.accounts.models import User
from fastapi import Depends
from app.accounts.dependencies import require_admin

router = APIRouter()


@router.post("/create-category", response_model=CategoryOut)
async def create_category(
    session: SessionDep, category: CategoryCreate, admin: User = Depends(require_admin)
):
    return await category_create(session, category)
