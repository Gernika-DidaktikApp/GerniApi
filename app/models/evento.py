from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from app.database import Base

class Eventos(Base):
    __tablename__ = "evento"

    id = Column(CHAR(36), primary_key=True, nullable=False)
    id_actividad = Column(CHAR(36), ForeignKey("actividad.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
