from fastapi import APIRouter
from .endpoints import usuarios, cuentas, transacciones

api_router = APIRouter()
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(cuentas.router, prefix="/cuentas", tags=["cuentas"])
api_router.include_router(transacciones.router, prefix="/transacciones", tags=["transacciones"])