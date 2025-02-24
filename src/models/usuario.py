from sqlalchemy import Column, Integer, String
from .base import Base, TimestampMixin

class Usuario(Base, TimestampMixin):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    usuario_cuenta = Column(String(50), unique=True, nullable=False)