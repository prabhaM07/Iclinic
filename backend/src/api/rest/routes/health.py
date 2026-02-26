from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def heack_check():
    return { "status" : "healthy", "version" : "1.0.0" }

