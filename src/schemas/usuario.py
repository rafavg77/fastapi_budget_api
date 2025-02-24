from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class UsuarioBase(BaseModel):
    nombre_usuario: str
    usuario_cuenta: str

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id_usuario: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True