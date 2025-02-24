from typing import List
from sqlalchemy.orm import Session
from ..models.transaccion import Transaccion
from ..schemas.transaccion import TransaccionCreate, Transaccion as TransaccionSchema
from .base import CRUDBase

class CRUDTransaccion(CRUDBase[Transaccion, TransaccionCreate, TransaccionSchema]):
    def get_by_cuenta(self, db: Session, *, cuenta_transaccion: str) -> List[Transaccion]:
        return db.query(Transaccion).filter(Transaccion.cuenta_transaccion == cuenta_transaccion).all()

crud_transaccion = CRUDTransaccion(Transaccion)