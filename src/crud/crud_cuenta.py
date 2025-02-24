from typing import List
from sqlalchemy.orm import Session
from ..models.cuenta import Cuenta
from ..schemas.cuenta import CuentaCreate, Cuenta as CuentaSchema
from .base import CRUDBase

class CRUDCuenta(CRUDBase[Cuenta, CuentaCreate, CuentaSchema]):
    def get_by_usuario(self, db: Session, *, usuario_cuenta: str) -> List[Cuenta]:
        return db.query(Cuenta).filter(Cuenta.usuario_cuenta == usuario_cuenta).all()