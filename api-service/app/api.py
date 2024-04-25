import fastapi

router = fastapi.APIRouter()

@router.get("/health")
async def health():
    return {"message": "Api-service is running"}