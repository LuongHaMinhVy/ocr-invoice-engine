from fastapi import FastAPI
from app.routers.invoices import router as invoices_router
from app.database import engine, Base

# Create tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OCR Invoice Processing API")

app.include_router(invoices_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=8000, reload=True)
