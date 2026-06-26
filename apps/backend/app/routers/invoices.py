from fastapi import APIRouter

router = APIRouter(prefix="/api/invoices", tags=["invoices"])

@router.get("/health")
def health_check():
    return {"status": "OK"}
