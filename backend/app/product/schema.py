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
    categories: list[CategoryBase]
    model_config = {"from_attributes": True}


class PaginatedProductOut(BaseModel):
    total: int
    page: int
    limit: int
    items: list[ProductOut]


class ProductUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    stock_quantity: int | None = None
    categories_ids: list[int] | None = None
    model_config = {"from_attributes": True}
