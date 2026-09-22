from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    name: str
    model_config = {"from_attributes": True}


class ProductBase(BaseModel):
    title: str
    description: str | None = None
    price: float = Field(gt=0)
    stock: int = Field(gt=0)


class ProductCreate(ProductBase):
    category_ids: list[int] | None = None


class ProductOut(BaseModel):
    id: int
    title: str
    model_config = {"from_attributes": True}
