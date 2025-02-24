from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class Transaccion(Base, TimestampMixin):
    __tablename__ = "transacciones"
    
    id_transaccion = Column(Integer, primary_key=True, index=True)
    concepto = Column(String(200), nullable=False)
    ingreso = Column(Float, default=0.0)
    egreso = Column(Float, default=0.0)
    cuenta_transaccion = Column(String(50), ForeignKey("cuentas.cuenta_transaccion"))
    
    cuenta = relationship("Cuenta", back_populates="transacciones")