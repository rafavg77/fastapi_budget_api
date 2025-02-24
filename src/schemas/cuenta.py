from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .transaccion import Transaccion

class CuentaBase(BaseModel):
    nombre_banco: str
    nombre_cuenta: str
    tipo_cuenta: str
    cuenta_transaccion: str
    usuario_cuenta: str

class CuentaCreate(CuentaBase):
    pass

class Cuenta(CuentaBase):
    id_cuenta: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True