from sqlalchemy import Column, String, ForeignKey
from app.database import Base

class Eventos(Base):
    __tablename__ = "evento"

    id = Column(String(36), primary_key=True, nullable=False)
    id_actividad = Column(String(36), ForeignKey("actividad.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
