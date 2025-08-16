from fastapi import APIRouter
from app.api.v1.endpoints import facturas, utils, documentos, emails, facturas_v44, referencias

api_router = APIRouter()
api_router.include_router(facturas.router, prefix="/facturas", tags=["facturas"])
api_router.include_router(facturas_v44.router, prefix="/facturas-v44", tags=["facturas-v44"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])
api_router.include_router(utils.router, prefix="/utils", tags=["utilidades"])
api_router.include_router(emails.router, prefix="/emails", tags=["correos"])
api_router.include_router(referencias.router, prefix="/referencias", tags=["referencias"])