from fastapi import FastAPI
from app.accounts.routers import router as account_router
from app.product.routers.category import router as category_router
from app.product.routers.product import router as product_router

app = FastAPI(title="FastAPI backend")


@app.get("/")
def health() -> dict:
    return {"status": "ok"}


app.include_router(account_router, prefix="/api/account", tags=["Accounts"])
app.include_router(category_router, prefix="/api/category", tags=["Category"])
app.include_router(product_router, prefix="/api/product", tags=["Product"])
