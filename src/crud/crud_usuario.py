from typing import Optional
from sqlalchemy.orm import Session
from ..models.usuario import Usuario
from ..schemas.usuario import UsuarioCreate, Usuario as UsuarioSchema
from .base import CRUDBase

class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioSchema]):
    def get_by_cuenta(self, db: Session, *, usuario_cuenta: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.usuario_cuenta == usuario_cuenta).first()

crud_usuario = CRUDUsuario(Usuario)