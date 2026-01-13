from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from app.database import Base

class Actividad(Base):
    __tablename__ = "actividad_estado"

    id = Column(CHAR(36), primary_key=True, nullable=False)
    id_juego = Column(CHAR(36), ForeignKey("juego.id"), nullable=False)
    id_actividad = Column(CHAR(36), ForeignKey("actividad.id"), nullable=False)
    fecha_inicio = Column(DateTime, default=datetime.now, nullable=False)
    duracion = Column(Integer, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(20), default="en_progreso", nullable=False)
