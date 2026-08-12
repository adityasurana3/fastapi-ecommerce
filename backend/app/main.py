from fastapi import FastAPI
from app.accounts.routers import router as account_router

app = FastAPI(title="FastAPI backend")


@app.get("/")
def health() -> dict:
    return {"status": "ok"}


app.include_router(account_router, prefix="/api/account", tags=["Accounts"])
