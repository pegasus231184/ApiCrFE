from fastapi import APIRouter
from app.api.v1.endpoints import facturas, utils, documentos

api_router = APIRouter()
api_router.include_router(facturas.router, prefix="/facturas", tags=["facturas"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])
api_router.include_router(utils.router, prefix="/utils", tags=["utilidades"])