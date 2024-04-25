from fastapi import APIRouter, status
from . import schema, controller

router = APIRouter(prefix="/api/query", tags=["query"])

@router.get("/health")
async def health():
    return {"message": "Api-service is running"}

@router.post("/")
async def process(query: schema.Query):
    print(query)
    return status.HTTP_201_CREATED