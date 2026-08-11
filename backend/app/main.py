from fastapi import FastAPI

app = FastAPI(title="FastAPI backend")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
