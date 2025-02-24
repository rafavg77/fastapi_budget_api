from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from .base import Base, TimestampMixin

class TipoCuenta(enum.Enum):
    CREDITO = "credito"
    DEBITO = "debito"
    HIPOTECARIO = "hipotecario"
    AHORRO = "ahorro"
    INVERSION = "inversion"

class Cuenta(Base, TimestampMixin):
    __tablename__ = "cuentas"
    
    id_cuenta = Column(Integer, primary_key=True, index=True)
    nombre_banco = Column(String(100), nullable=False)
    nombre_cuenta = Column(String(100), nullable=False)
    tipo_cuenta = Column(Enum(TipoCuenta), nullable=False)
    cuenta_transaccion = Column(String(50), unique=True, nullable=False)
    usuario_cuenta = Column(String(50), ForeignKey("usuarios.usuario_cuenta"))
    
    transacciones = relationship("Transaccion", back_populates="cuenta")
    usuario = relationship("Usuario", backref="cuentas")