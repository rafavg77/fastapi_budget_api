from pydantic import BaseModel
from datetime import datetime

class TransaccionBase(BaseModel):
    concepto: str
    ingreso: float = 0.0
    egreso: float = 0.0
    cuenta_transaccion: str

class TransaccionCreate(TransaccionBase):
    pass

class Transaccion(TransaccionBase):
    id_transaccion: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True