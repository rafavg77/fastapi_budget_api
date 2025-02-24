from sqlalchemy import Column, DateTime
from datetime import datetime
from sqlalchemy.sql import func
from ..core.database import Base

class TimestampMixin:
    fecha_creacion = Column(DateTime, default=func.now(), nullable=False)
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)