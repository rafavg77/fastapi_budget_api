from fastapi import FastAPI
from .api.v1.router import api_router
from .core.database import engine
from .models import base, usuario, cuenta, transaccion

# Crear todas las tablas
base.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Budget API")
app.include_router(api_router, prefix="/api/v1")